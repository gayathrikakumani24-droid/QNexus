import logging
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from app.core.config import settings
from app.core.database import get_mongo_db
from app.core.pinecone import get_pinecone_index, ensure_pinecone_index
from app.repositories.question_repository import QuestionRepository
from app.services.embedding_service import EmbeddingService
from app.schemas.search_schema import SearchRequest, SearchResponse, SearchResultItem
from app.schemas.question_schema import QuestionResponse

logger = logging.getLogger("qnexus.services.search")

class SearchService:
    def __init__(
        self,
        db: Optional[Database] = None,
        embedding_service: Optional[EmbeddingService] = None,
        pinecone_index = None,
        qdrant_client = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.question_repo = QuestionRepository(self.db)
        self.embedding_service = embedding_service or EmbeddingService()
        self.pinecone_index = pinecone_index or qdrant_client or get_pinecone_index()
        self.index_name = settings.PINECONE_INDEX_NAME

    def _build_pinecone_filter(self, request: SearchRequest) -> Optional[Dict[str, Any]]:
        """
        Builds Pinecone metadata filter dictionary from request fields.
        Pinecone uses MongoDB-style operators (e.g. {"$eq": value}).
        """
        filter_dict: Dict[str, Any] = {}
        if request.subject:
            filter_dict["subject"] = {"$eq": request.subject}
        if request.chapter:
            filter_dict["chapter"] = {"$eq": request.chapter}
        if request.concept:
            filter_dict["concept"] = {"$eq": request.concept}
        if request.difficulty:
            filter_dict["difficulty"] = {"$eq": request.difficulty}
        if request.year:
            filter_dict["year"] = {"$eq": request.year}
        if request.session:
            filter_dict["session"] = {"$eq": request.session}
        if request.shift:
            filter_dict["shift"] = {"$eq": request.shift}

        return filter_dict if filter_dict else None

    def _build_qdrant_filter(self, request: SearchRequest):
        """Backward compatibility alias for tests/callers."""
        return self._build_pinecone_filter(request)

    def _load_fallback_questions(self, question_ids: List[str]) -> Dict[str, QuestionResponse]:
        """Fall back to local data/processed/*_questions.json files if MongoDB is slow or unreachable."""
        import os, glob, json
        results = {}
        missing = set(question_ids)
        if not missing:
            return results

        processed_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "processed")
        if not os.path.exists(processed_dir):
            return results

        for json_file in glob.glob(os.path.join(processed_dir, "*_questions.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    q_list = json.load(f)
                    for item in q_list:
                        qid = item.get("question_id")
                        if qid in missing:
                            results[qid] = QuestionResponse(**item)
                            missing.remove(qid)
                            if not missing:
                                return results
            except Exception as e:
                logger.debug(f"Failed parsing cached questions file {json_file}: {e}")
        return results

    def search_questions(self, request: SearchRequest) -> SearchResponse:
        """
        Executes semantic search:
        1. Encodes search query into dense 384d vector.
        2. Queries Pinecone Cloud nearest neighbours with metadata payload filtering.
        3. Retrieves complete, authoritative Question documents from MongoDB by question_id.
        4. Preserves semantic ranking order and returns similarity scores.
        """
        logger.info(f"Executing semantic search for query='{request.query}' (top_k={request.top_k})...")

        # Ensure index is ready if using default index
        if self.pinecone_index is None:
            ensure_pinecone_index(self.index_name, vector_size=384)

        # 1. Generate query embedding vector
        query_vector = self.embedding_service.embed_text(request.query)

        # 2. Build metadata filter
        query_filter = self._build_pinecone_filter(request)

        # 3. Query Pinecone for semantic similarity
        search_results = []
        if self.pinecone_index is not None:
            try:
                if hasattr(self.pinecone_index, "query"):
                    kwargs = {
                        "vector": query_vector,
                        "top_k": request.top_k,
                        "include_metadata": True
                    }
                    if query_filter:
                        kwargs["filter"] = query_filter
                    res = self.pinecone_index.query(**kwargs)
                    search_results = getattr(res, "matches", []) or (res.get("matches", []) if isinstance(res, dict) else [])
                elif hasattr(self.pinecone_index, "search"):
                    # Compatibility fallback for mock objects using legacy search signature
                    search_results = self.pinecone_index.search(
                        collection_name=self.index_name,
                        query_vector=query_vector,
                        query_filter=query_filter,
                        limit=request.top_k,
                        with_payload=True
                    )
            except Exception as e:
                logger.error(f"Pinecone vector search failed: {e}")
                return SearchResponse(query=request.query, total_found=0, results=[])

        if not search_results:
            logger.info("Vector search returned 0 matching points.")
            return SearchResponse(query=request.query, total_found=0, results=[])

        # 4. Extract question IDs and similarity scores (with min_score filtering)
        score_map: Dict[str, float] = {}
        ordered_ids: List[str] = []

        for hit in search_results:
            q_id = None
            metadata = getattr(hit, "metadata", None) or (hit.get("metadata") if isinstance(hit, dict) else None)
            payload = getattr(hit, "payload", None) or (hit.get("payload") if isinstance(hit, dict) else None)
            
            if metadata and "question_id" in metadata:
                q_id = metadata["question_id"]
            elif payload and "question_id" in payload:
                q_id = payload["question_id"]
            elif hasattr(hit, "id") and hit.id:
                q_id = hit.id
            elif isinstance(hit, dict) and "id" in hit:
                q_id = hit["id"]

            if q_id:
                raw_score = getattr(hit, "score", 0.0) or (hit.get("score", 0.0) if isinstance(hit, dict) else 0.0)
                score_float = round(float(raw_score), 4)

                # Filter out irrelevant questions if min_score is provided
                if request.min_score is not None and score_float < request.min_score:
                    continue

                ordered_ids.append(q_id)
                score_map[q_id] = score_float

        # 5. Hydrate full Question documents from MongoDB (Source of Truth) with local fallback
        doc_map = {}
        try:
            questions = self.question_repo.get_questions_by_ids(ordered_ids)
            doc_map = {q.question_id: q for q in questions}
        except Exception as e:
            logger.warning(f"MongoDB question retrieval encountered error: {e}. Falling back to local cache...")

        missing_ids = [qid for qid in ordered_ids if qid not in doc_map]
        if missing_ids:
            logger.info(f"Hydrating {len(missing_ids)} questions from local processed cache...")
            fallback_map = self._load_fallback_questions(missing_ids)
            doc_map.update(fallback_map)

        # 6. Assemble response in exact semantic rank order
        items: List[SearchResultItem] = []
        for q_id in ordered_ids:
            if q_id in doc_map:
                items.append(
                    SearchResultItem(
                        similarity_score=score_map.get(q_id, 0.0),
                        question=doc_map[q_id]
                    )
                )

        logger.info(f"Semantic search returned {len(items)} hydrated question results (top_k={request.top_k}, min_score={request.min_score}).")
        return SearchResponse(
            query=request.query,
            total_found=len(items),
            results=items
        )

import logging
from typing import List, Dict, Any, Optional, Set
from pymongo.database import Database
from app.core.config import settings
from app.core.database import get_mongo_db
from app.core.pinecone import get_pinecone_index, ensure_pinecone_index
from app.repositories.question_repository import QuestionRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.embedding_service import EmbeddingService
from app.schemas.recommendation_schema import RecommendationItem, RecommendationResponse
from app.schemas.question_schema import QuestionResponse

logger = logging.getLogger("qnexus.services.recommendation")

class RecommendationService:
    def __init__(
        self,
        db: Optional[Database] = None,
        question_repo: Optional[QuestionRepository] = None,
        analytics_repo: Optional[AnalyticsRepository] = None,
        embedding_service: Optional[EmbeddingService] = None,
        pinecone_index = None,
        qdrant_client = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.question_repo = question_repo or QuestionRepository(self.db)
        self.analytics_repo = analytics_repo or AnalyticsRepository(self.db)
        self.embedding_service = embedding_service or EmbeddingService()
        self.pinecone_index = pinecone_index or qdrant_client or get_pinecone_index()
        self.index_name = settings.PINECONE_INDEX_NAME

    def _get_solved_question_ids(self, user_id: str = "default_user") -> Set[str]:
        """
        Retrieves all question_ids already attempted or solved by the user to exclude them.
        """
        solved_ids: Set[str] = set()
        try:
            cursor = self.db.attempts.find({"user_id": user_id}, {"question_id": 1})
            for doc in cursor:
                if "question_id" in doc:
                    solved_ids.add(doc["question_id"])

            # Also check session answers
            sessions = self.db.practice_sessions.find({"config.user_id": user_id}, {"question_ids": 1})
            for s in sessions:
                for qid in s.get("question_ids", []):
                    solved_ids.add(qid)
        except Exception as e:
            logger.warning(f"Could not retrieve solved question IDs for user {user_id}: {e}")

        return solved_ids

    def get_recommendations(
        self,
        user_id: str = "default_user",
        subject: Optional[str] = None,
        limit: int = 10
    ) -> RecommendationResponse:
        """
        Generates personalized, explainable question recommendations based strictly on
        actual student performance and conceptual accuracy diagnostics.
        """
        if self.pinecone_index is None:
            ensure_pinecone_index(self.index_name, vector_size=384)

        # 1. Retrieve already solved questions to exclude
        solved_ids = self._get_solved_question_ids(user_id=user_id)
        logger.info(f"User {user_id} has {len(solved_ids)} solved question IDs to exclude.")

        # 2. Retrieve concept-level performance aggregation
        concept_stats = self.analytics_repo.get_concept_aggregation(subject=subject)

        weak_concepts: List[Dict[str, Any]] = []
        for row in concept_stats:
            group_id = row.get("_id", {})
            subj = group_id.get("subject", "Unknown")
            chap = group_id.get("chapter", "General")
            conc = group_id.get("concept", "General Concepts")
            attempted = row.get("attempted", 0)
            correct = row.get("correct", 0)
            incorrect = row.get("incorrect", 0)

            accuracy = (
                round((correct / (correct + incorrect)) * 100, 1)
                if (correct + incorrect) > 0
                else 0.0
            )

            # Prioritize weak concepts (low accuracy or high errors)
            weak_concepts.append({
                "subject": subj,
                "chapter": chap,
                "concept": conc,
                "attempts": attempted,
                "correct": correct,
                "incorrect": incorrect,
                "accuracy": accuracy
            })

        # Sort by lowest accuracy first, then highest attempts
        weak_concepts.sort(key=lambda x: (x["accuracy"], -x["attempts"]))

        recommendations: List[RecommendationItem] = []
        selected_question_ids: Set[str] = set()

        # 3. For each weak concept, retrieve matching questions via Pinecone
        for wc in weak_concepts:
            if len(recommendations) >= limit:
                break

            subj_name = wc["subject"]
            chap_name = wc["chapter"]
            conc_name = wc["concept"]
            acc = wc["accuracy"]
            attempts = wc["attempts"]

            # Determine appropriate target difficulty
            target_diff = "Easy" if acc < 40.0 else ("Medium" if acc <= 70.0 else "Hard")

            query_text = f"{subj_name} {chap_name} {conc_name}"
            query_vector = self.embedding_service.embed_text(query_text)

            # Build Pinecone filter
            conditions = {}
            if subj_name and subj_name != "Unknown" and subj_name != "All":
                conditions["subject"] = {"$eq": subj_name}
            if chap_name and chap_name != "General":
                conditions["chapter"] = {"$eq": chap_name}

            search_hits = []
            if self.pinecone_index is not None:
                try:
                    if hasattr(self.pinecone_index, "query"):
                        kwargs = {
                            "vector": query_vector,
                            "top_k": 15,
                            "include_metadata": True
                        }
                        if conditions:
                            kwargs["filter"] = conditions
                        res = self.pinecone_index.query(**kwargs)
                        search_hits = getattr(res, "matches", []) or (res.get("matches", []) if isinstance(res, dict) else [])
                    elif hasattr(self.pinecone_index, "search"):
                        search_hits = self.pinecone_index.search(
                            collection_name=self.index_name,
                            query_vector=query_vector,
                            limit=15,
                            with_payload=True
                        )
                except Exception as e:
                    logger.warning(f"Vector search failed for concept {conc_name}: {e}")
                    search_hits = []

            # 4. Filter out solved and duplicate questions
            for hit in search_hits:
                if len(recommendations) >= limit:
                    break

                metadata = getattr(hit, "metadata", None) or (hit.get("metadata") if isinstance(hit, dict) else None)
                payload = getattr(hit, "payload", None) or (hit.get("payload") if isinstance(hit, dict) else None)
                
                q_id = None
                if metadata and "question_id" in metadata:
                    q_id = metadata["question_id"]
                elif payload and "question_id" in payload:
                    q_id = payload["question_id"]
                elif hasattr(hit, "id") and hit.id:
                    q_id = hit.id
                elif isinstance(hit, dict) and "id" in hit:
                    q_id = hit["id"]

                if not q_id or q_id in solved_ids or q_id in selected_question_ids:
                    continue

                q_doc = self.question_repo.get_question(q_id)
                if not q_doc:
                    continue

                reason = (
                    f"Recommended because your accuracy in {conc_name} questions is {acc}% "
                    f"across {attempts} attempts."
                )

                score_val = getattr(hit, "score", None) or (hit.get("score") if isinstance(hit, dict) else None)

                recommendations.append(
                    RecommendationItem(
                        question_id=q_id,
                        subject=q_doc.subject or subj_name,
                        chapter=q_doc.chapter or chap_name,
                        concept=q_doc.concept or conc_name,
                        difficulty=q_doc.difficulty or target_diff,
                        reason=reason,
                        similarity_score=round(float(score_val), 4) if score_val else None,
                        question=q_doc
                    )
                )
                selected_question_ids.add(q_id)

        # 5. Cold Start or Fallback: if not enough recommendations from weak concepts
        if len(recommendations) < limit:
            fallback_questions = self.question_repo.list_questions(
                subject=subject if subject != "All" else None,
                limit=50
            )

            for q_doc in fallback_questions:
                if len(recommendations) >= limit:
                    break

                q_id = q_doc.question_id
                if q_id in solved_ids or q_id in selected_question_ids:
                    continue

                reason = (
                    f"Recommended diagnostic question to evaluate and strengthen baseline proficiency in "
                    f"{q_doc.chapter or 'core topics'} ({q_doc.concept or 'fundamental concepts'})."
                )

                recommendations.append(
                    RecommendationItem(
                        question_id=q_id,
                        subject=q_doc.subject or "General",
                        chapter=q_doc.chapter or "General",
                        concept=q_doc.concept or "General Concept",
                        difficulty=q_doc.difficulty or "Medium",
                        reason=reason,
                        similarity_score=None,
                        question=q_doc
                    )
                )
                selected_question_ids.add(q_id)

        return RecommendationResponse(
            total=len(recommendations),
            user_id=user_id,
            recommendations=recommendations
        )

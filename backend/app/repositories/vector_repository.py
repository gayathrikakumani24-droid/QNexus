import logging
from typing import List, Dict, Any, Optional, Set
from app.core.config import settings
from app.core.pinecone import get_pinecone_index, ensure_pinecone_index

logger = logging.getLogger("qnexus.repositories.vector")

class VectorRepository:
    def __init__(self, index: Optional[Any] = None, index_name: Optional[str] = None):
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self._index = index

    @property
    def index(self) -> Optional[Any]:
        if self._index is None:
            self._index = get_pinecone_index(self.index_name)
        return self._index

    @staticmethod
    def question_id_to_point_id(question_id: str) -> str:
        """
        Pinecone natively supports string IDs. Returns the question_id directly.
        """
        return str(question_id)

    @staticmethod
    def sanitize_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pinecone metadata values must be strings, numbers, booleans, or lists of strings.
        Null (None) values must be excluded to prevent Pinecone API validation errors.
        """
        sanitized = {}
        for key, value in payload.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list) and all(isinstance(i, str) for i in value):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        return sanitized

    def upsert_records(self, records: List[Dict[str, Any]]) -> int:
        """
        Upserts a batch of embedding records into Pinecone Cloud.
        Each record should have 'question_id', 'embedding' (vector), and 'payload'.
        """
        if not records:
            return 0

        # Ensure index is created if using default index
        if self._index is None:
            vector_dim = len(records[0]["embedding"])
            ensure_pinecone_index(self.index_name, vector_size=vector_dim)

        vectors: List[Dict[str, Any]] = []
        for r in records:
            q_id = r["question_id"]
            point_id = self.question_id_to_point_id(q_id)
            vector = r["embedding"]
            raw_payload = r.get("payload", {})
            raw_payload["question_id"] = q_id

            clean_metadata = self.sanitize_metadata(raw_payload)

            vectors.append({
                "id": point_id,
                "values": vector,
                "metadata": clean_metadata
            })

        if not self.index:
            logger.error("Pinecone index is unavailable for upsert.")
            return 0

        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted {len(vectors)} vectors to Pinecone index '{self.index_name}'")
            return len(vectors)
        except Exception as e:
            logger.error(f"Failed to upsert vectors into Pinecone: {e}")
            raise

    def query_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Queries Pinecone nearest neighbors with optional metadata filter.
        """
        if not self.index:
            logger.warning("Pinecone index is unavailable for query.")
            return []

        try:
            kwargs = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": True
            }
            if filter_dict:
                kwargs["filter"] = filter_dict

            res = self.index.query(**kwargs)
            matches = getattr(res, "matches", []) or (res.get("matches", []) if isinstance(res, dict) else [])
            return matches
        except Exception as e:
            logger.error(f"Pinecone vector query failed: {e}")
            return []

    def get_existing_question_ids(self) -> Set[str]:
        """
        Retrieves existing indexed question IDs from Pinecone to make synchronization idempotent.
        """
        existing_ids: Set[str] = set()
        if not self.index:
            return existing_ids

        try:
            if self._index is None:
                ensure_pinecone_index(self.index_name)
            if hasattr(self.index, "list"):
                for ids_batch in self.index.list():
                    for item in ids_batch:
                        item_id = item.id if hasattr(item, "id") else str(item)
                        existing_ids.add(item_id)
            logger.info(f"Found {len(existing_ids)} existing indexed question_ids in Pinecone.")
        except Exception as e:
            logger.warning(f"Could not list Pinecone index IDs: {e}")

        return existing_ids

    def count(self) -> int:
        """Returns total vector count in the Pinecone index."""
        if not self.index:
            return 0
        try:
            stats = self.index.describe_index_stats()
            if isinstance(stats, dict):
                return stats.get("total_vector_count", 0)
            return getattr(stats, "total_vector_count", 0)
        except Exception as e:
            logger.warning(f"Could not count vectors in Pinecone: {e}")
            return 0

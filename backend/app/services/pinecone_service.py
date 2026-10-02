import logging
from typing import Dict, Any, List, Optional
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.repositories.question_repository import QuestionRepository
from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger("qnexus.services.pinecone_service")

class PineconeService:
    def __init__(
        self,
        db: Optional[Database] = None,
        vector_repo: Optional[VectorRepository] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.question_repo = QuestionRepository(self.db)
        self.vector_repo = vector_repo or VectorRepository()
        self.embedding_service = embedding_service or EmbeddingService()

    def sync_paper_vectors(
        self,
        paper_id: Optional[str] = None,
        batch_size: int = 32,
        force_reindex: bool = False
    ) -> Dict[str, Any]:
        """
        Idempotently synchronizes MongoDB questions to Pinecone Cloud vector index.
        1. Fetches questions from MongoDB (source of truth).
        2. Retrieves existing indexed question_ids from Pinecone.
        3. Identifies questions needing indexing.
        4. Generates normalized embeddings in batches.
        5. Upserts points with rich metadata payload to Pinecone.
        """
        logger.info(f"Starting Pinecone vector synchronization (paper_id={paper_id}, batch_size={batch_size}, force={force_reindex})...")

        questions = self.question_repo.list_questions(paper_id=paper_id, limit=2000)
        total_questions = len(questions)

        if total_questions == 0:
            logger.warning(f"No questions found in MongoDB for paper_id={paper_id}.")
            return {
                "paper_id": paper_id,
                "total_questions": 0,
                "already_indexed": 0,
                "newly_indexed": 0,
                "failed": 0
            }

        # Check existing vector IDs in Pinecone to avoid duplicate embeddings/vectors
        existing_ids = set() if force_reindex else self.vector_repo.get_existing_question_ids()
        
        questions_to_index = [q for q in questions if q.question_id not in existing_ids]
        already_indexed_count = total_questions - len(questions_to_index)

        logger.info(
            f"Sync Analysis: Total={total_questions}, Already Indexed={already_indexed_count}, "
            f"Needs Indexing={len(questions_to_index)}"
        )

        newly_indexed_count = 0
        failed_count = 0

        for i in range(0, len(questions_to_index), batch_size):
            batch = questions_to_index[i:i + batch_size]
            try:
                # 1. Generate embeddings and prepare payloads
                records = self.embedding_service.embed_questions(
                    questions=batch,
                    batch_size=batch_size
                )
                
                # Enrich payload with page_number and session/date
                for r, q in zip(records, batch):
                    r["payload"]["page_number"] = q.page_number
                    r["payload"]["session"] = q.session
                    r["payload"]["date"] = q.date

                # 2. Upsert to Pinecone
                upserted = self.vector_repo.upsert_records(records)
                newly_indexed_count += upserted
            except Exception as e:
                logger.error(f"Failed to index batch {i}-{i+len(batch)}: {e}")
                failed_count += len(batch)

        logger.info(
            f"Pinecone Vector Sync Finished: Total={total_questions}, Already Indexed={already_indexed_count}, "
            f"Newly Indexed={newly_indexed_count}, Failed={failed_count}"
        )

        return {
            "paper_id": paper_id,
            "total_questions": total_questions,
            "already_indexed": already_indexed_count,
            "newly_indexed": newly_indexed_count,
            "failed": failed_count
        }

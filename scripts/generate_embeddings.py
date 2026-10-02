"""
Qnexus Embedding Generation Script

Workflow:
1. Connects to MongoDB (source of truth).
2. Loads questions.
3. Formats question text with metadata (subject + chapter + concept + content).
4. Generates normalized 384-dimensional embeddings in batches.
5. Prepares Pinecone-ready Record structures with metadata payload.
6. Does NOT insert into Pinecone yet (prepared for vector indexing step).
"""

import os
import sys
import json
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.core.database import get_mongo_db, close_mongo_connection
from app.repositories.question_repository import QuestionRepository
from app.services.embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("generate_embeddings")

def generate_embeddings_for_mongodb_questions(paper_id: str = None, batch_size: int = 32):
    db = get_mongo_db()
    question_repo = QuestionRepository(db)
    embedding_service = EmbeddingService()

    logger.info("Fetching questions from MongoDB...")
    questions = question_repo.list_questions(paper_id=paper_id, limit=1000)
    
    if not questions:
        logger.warning("No questions found in MongoDB to embed.")
        return []

    logger.info(f"Loaded {len(questions)} questions from MongoDB.")

    # Generate embeddings and prepare Qdrant-ready records
    records = embedding_service.embed_questions(questions=questions, batch_size=batch_size)

    logger.info(f"Prepared {len(records)} Qdrant records with 384-d embeddings.")
    if records:
        sample = records[0]
        logger.info(f"Sample Record ID: {sample['question_id']}")
        logger.info(f"Embedding Vector Dimension: {len(sample['embedding'])}")
        logger.info(f"Payload Attributes: {json.dumps(sample['payload'], indent=2)}")

    return records

if __name__ == "__main__":
    try:
        generate_embeddings_for_mongodb_questions()
    finally:
        close_mongo_connection()

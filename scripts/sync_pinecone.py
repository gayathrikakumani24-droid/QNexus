"""
Qnexus Pinecone Cloud Vector Synchronization Script

Workflow:
1. Connects to MongoDB (authoritative source of truth).
2. Verifies / initializes Pinecone Serverless index 'qnexus-questions'.
3. Idempotently reads questions from MongoDB.
4. Generates dense 384d contextual embeddings using Sentence Transformers.
5. Upserts points with full metadata payload to Pinecone Cloud.
6. Reports vector synchronization statistics.
"""

import os
import sys
import argparse
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.core.database import get_mongo_db, close_mongo_connection
from app.core.pinecone import ensure_pinecone_index
from app.services.pinecone_service import PineconeService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sync_pinecone")

def main():
    parser = argparse.ArgumentParser(description="Synchronize MongoDB JEE Main questions to Pinecone Cloud vector index.")
    parser.add_argument("--paper-id", type=str, default=None, help="Filter sync by specific paper_id")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding & upsert batch size")
    parser.add_argument("--force", action="store_true", help="Force reindexing of already indexed questions")

    args = parser.parse_args()

    db = get_mongo_db()
    
    # Ensure Pinecone index is ready
    ensure_pinecone_index(vector_size=384)

    service = PineconeService(db=db)
    
    try:
        results = service.sync_paper_vectors(
            paper_id=args.paper_id,
            batch_size=args.batch_size,
            force_reindex=args.force
        )
        logger.info("=== Pinecone Synchronization Results ===")
        logger.info(f"Paper: {results['paper_id'] or 'ALL'}")
        logger.info(f"Total Questions: {results['total_questions']}")
        logger.info(f"Already Indexed: {results['already_indexed']}")
        logger.info(f"Newly Indexed: {results['newly_indexed']}")
        logger.info(f"Failed: {results['failed']}")
    finally:
        close_mongo_connection()

if __name__ == "__main__":
    main()

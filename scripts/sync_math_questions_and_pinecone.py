"""
Qnexus - Dedicated Mathematics Questions Normalization & Pinecone Update Script

Workflow:
1. Discovers all raw JEE Main question paper PDFs in data/raw/ (2024, 2025, 2026).
2. Parses each paper using the improved mathematical parser.
3. Updates only the Mathematics questions in data/processed/*_questions.json and MongoDB.
4. Generates dense 384d normalized embeddings for ONLY the Mathematics questions.
5. Upserts the updated Mathematics vectors to Pinecone Cloud.
6. Leaves Physics and Chemistry questions and vectors completely untouched.
7. Logs before/after verification statistics.
"""

import os
import sys
import glob
import json
import logging
from typing import List, Dict, Any

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.core.database import get_mongo_db, close_mongo_connection
from app.core.pinecone import ensure_pinecone_index
from app.parsers import parse_paper
from app.repositories.question_repository import QuestionRepository
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository
from app.schemas.question_schema import QuestionCreate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sync_math")

def main():
    logger.info("==================================================================")
    logger.info("Starting Mathematics Question Sync (MongoDB & Pinecone Cloud)...")
    logger.info("==================================================================")

    # 1. Connect to MongoDB
    mongo_db = get_mongo_db()
    mongo_db.command("ping")
    logger.info("MongoDB connection verified.")

    question_repo = QuestionRepository(mongo_db)
    embedding_service = EmbeddingService()
    vector_repo = VectorRepository()

    # Ensure Pinecone index is ready
    ensure_pinecone_index(vector_size=384)

    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")

    all_math_questions_to_embed: List[QuestionCreate] = []
    total_math_updated_in_mongo = 0
    total_json_files_updated = 0

    # Discover all raw PDFs across 2024, 2025, 2026
    years = [2024, 2025, 2026]
    for year in years:
        year_raw_dir = os.path.join(raw_dir, str(year))
        if not os.path.exists(year_raw_dir):
            continue

        pdf_files = sorted(glob.glob(os.path.join(year_raw_dir, "*.pdf")))
        logger.info(f"\n--- Processing Year {year}: {len(pdf_files)} papers found ---")

        for idx, pdf_path in enumerate(pdf_files, 1):
            filename = os.path.basename(pdf_path)
            try:
                # Parse paper with the improved parser
                questions = parse_paper(pdf_path, year=year)
                if not questions:
                    logger.warning(f"No questions parsed from {filename}")
                    continue

                paper_id = questions[0].paper_id
                json_path = os.path.join(processed_dir, f"{paper_id}_questions.json")

                # Load existing processed JSON if available to preserve Physics & Chemistry exactly
                existing_questions_map = {}
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        existing_list = json.load(f)
                        for item in existing_list:
                            existing_questions_map[item.get("question_id")] = item

                math_questions_this_paper: List[QuestionCreate] = []

                for q in questions:
                    if q.subject == "Mathematics":
                        math_questions_this_paper.append(q)
                        all_math_questions_to_embed.append(q)

                        # Update MongoDB
                        question_repo.create_question(q)
                        total_math_updated_in_mongo += 1

                        # Update in local JSON map
                        existing_questions_map[q.question_id] = q.model_dump()

                # Save updated JSON file preserving all other questions
                if existing_questions_map:
                    ordered_dump = list(existing_questions_map.values())
                    # Sort by question_number
                    ordered_dump.sort(key=lambda x: x.get("question_number", 0))
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(ordered_dump, f, indent=2, ensure_ascii=False)
                    total_json_files_updated += 1

                logger.info(
                    f"[{year} {idx}/{len(pdf_files)}] {paper_id}: "
                    f"Updated {len(math_questions_this_paper)} Math questions in MongoDB & JSON."
                )

            except Exception as e:
                logger.error(f"Error parsing paper {filename}: {e}", exc_info=True)

    logger.info(f"\nTotal Mathematics Questions parsed and updated in MongoDB: {total_math_updated_in_mongo}")
    logger.info(f"Total processed JSON files refreshed: {total_json_files_updated}")

    # 4. Generate embeddings and upsert ONLY Mathematics questions to Pinecone
    total_math_to_upsert = len(all_math_questions_to_embed)
    logger.info(f"\nGenerating 384d dense embeddings for {total_math_to_upsert} Mathematics questions...")

    batch_size = 32
    newly_upserted_count = 0
    failed_count = 0

    for i in range(0, total_math_to_upsert, batch_size):
        batch = all_math_questions_to_embed[i:i + batch_size]
        try:
            records = embedding_service.embed_questions(questions=batch, batch_size=batch_size)
            
            # Enrich payloads
            for r, q in zip(records, batch):
                r["payload"]["page_number"] = q.page_number
                r["payload"]["session"] = q.session
                r["payload"]["date"] = q.date

            upserted = vector_repo.upsert_records(records)
            newly_upserted_count += upserted
            logger.info(f"Upserted Pinecone batch [{i + 1}-{min(i + batch_size, total_math_to_upsert)}/{total_math_to_upsert}]")
        except Exception as e:
            logger.error(f"Failed to embed/upsert batch {i}: {e}")
            failed_count += len(batch)

    # 5. Final Report
    logger.info("\n" + "=" * 60)
    logger.info("=== MATHEMATICS PINECONE UPDATE COMPLETE ===")
    logger.info(f"Total Math Questions Updated in MongoDB: {total_math_updated_in_mongo}")
    logger.info(f"Total Math Vectors Upserted to Pinecone: {newly_upserted_count}")
    logger.info(f"Failed Vectors: {failed_count}")
    
    live_count = vector_repo.count()
    logger.info(f"Current Total Pinecone Index Vectors: {live_count}")
    logger.info("=" * 60)

    close_mongo_connection()

if __name__ == "__main__":
    main()

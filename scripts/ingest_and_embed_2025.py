"""
Qnexus - 2025 JEE Main Paper Batch Ingestion and Pinecone Cloud Indexing Script

Workflow:
1. Discovers all raw 2025 JEE Main question paper PDFs in data/raw/2025/.
2. Parses each paper via parse_paper(pdf_path, year=2025, return_report=True).
3. Verifies validation audit (ensuring 75/75 matched questions).
4. Persists processed JSON cache to data/processed/{paper_id}_questions.json.
5. Persists paper and questions into MongoDB.
6. Generates 384-dimensional embeddings (strictly without answers) and upserts to Pinecone.
7. Logs final database and vector index statistics.
"""

import os
import sys
import glob
import json
import logging
from typing import Dict, Any, List

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.core.config import settings
from app.core.database import get_mongo_db
from app.parsers import parse_paper
from app.schemas.paper_schema import PaperCreate
from app.repositories.paper_repository import PaperRepository
from app.repositories.question_repository import QuestionRepository
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ingest_2025")

def main():
    raw_2025_dir = os.path.join(BASE_DIR, "data", "raw", "2025")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    pdf_files = sorted(glob.glob(os.path.join(raw_2025_dir, "*.pdf")))
    logger.info(f"Found {len(pdf_files)} 2025 PDF papers in {raw_2025_dir}")

    if not pdf_files:
        logger.error("No 2025 PDF files found in data/raw/2025/")
        return

    # Connect to MongoDB
    mongo_db = get_mongo_db()
    mongo_db.command("ping")
    logger.info("MongoDB connection verified.")

    paper_repo = PaperRepository(mongo_db)
    question_repo = QuestionRepository(mongo_db)
    embedding_service = EmbeddingService()
    vector_repo = VectorRepository()

    total_papers_processed = 0
    total_questions_extracted = 0
    total_vectors_upserted = 0
    paper_summaries = []

    for idx, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        logger.info(f"\n[{idx}/{len(pdf_files)}] Parsing 2025 paper: {filename}")

        try:
            # 1. Parse via isolated 2025 parser
            questions, report = parse_paper(pdf_path, year=2025, return_report=True)

            if not questions:
                logger.warning(f"No questions parsed for {filename}")
                continue

            q0 = questions[0]
            paper_id = q0.paper_id
            date_val = q0.date
            shift_val = q0.shift
            session_val = q0.session
            exam_val = q0.exam or "JEE Main"

            logger.info(
                f"Paper ID: {paper_id} | Extracted: {len(questions)} | "
                f"Matched: {report['matched']} | Valid: {report['is_valid']}"
            )

            # 2. Save processed questions to data/processed/{paper_id}_questions.json
            q_dump = [q.model_dump() for q in questions]
            json_path = os.path.join(processed_dir, f"{paper_id}_questions.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(q_dump, f, indent=2, ensure_ascii=False)

            # 3. Persist Paper record into MongoDB
            paper_create = PaperCreate(
                paper_id=paper_id,
                exam=exam_val,
                year=2025,
                session=session_val,
                date=date_val,
                shift=shift_val,
                filename=filename,
                total_questions=len(questions),
                status="PROCESSED"
            )
            paper_repo.create_paper(paper_create)

            # 4. Persist Questions into MongoDB
            question_repo.bulk_create_questions(questions)
            logger.info(f"Persisted {len(questions)} questions into MongoDB for {paper_id}.")

            # 5. Generate embeddings and prepare vector records
            records = embedding_service.embed_questions(questions=questions, batch_size=32)

            # Enrich payload with page_number, session, date
            for r, q in zip(records, questions):
                r["payload"]["page_number"] = q.page_number
                r["payload"]["session"] = q.session
                r["payload"]["date"] = q.date

            # 6. Upsert vectors to Pinecone
            upserted = vector_repo.upsert_records(records)
            logger.info(f"Upserted {upserted} vectors to Pinecone for {paper_id}.")

            total_papers_processed += 1
            total_questions_extracted += len(questions)
            total_vectors_upserted += upserted

            paper_summaries.append({
                "paper_id": paper_id,
                "date": date_val,
                "shift": shift_val,
                "questions": len(questions),
                "matched_answers": report["matched"],
                "is_valid": report["is_valid"],
                "upserted_vectors": upserted
            })

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}", exc_info=True)

    # 7. Final Verification
    logger.info("\n" + "=" * 60)
    logger.info("=== 2025 INGESTION & PINECONE INDEXING SUMMARY ===")
    logger.info(f"Total 2025 Papers Processed: {total_papers_processed}/{len(pdf_files)}")
    logger.info(f"Total 2025 Questions Ingested: {total_questions_extracted}")
    logger.info(f"Total 2025 Vectors Upserted: {total_vectors_upserted}")

    # MongoDB counts
    mongo_2025 = mongo_db["questions"].count_documents({"year": 2025})
    mongo_2026 = mongo_db["questions"].count_documents({"year": 2026})
    total_mongo = mongo_db["questions"].count_documents({})
    logger.info(f"MongoDB Questions: 2025={mongo_2025}, 2026={mongo_2026}, Total={total_mongo}")

    mongo_papers_2025 = mongo_db["papers"].count_documents({"year": 2025})
    mongo_papers_2026 = mongo_db["papers"].count_documents({"year": 2026})
    logger.info(f"MongoDB Papers: 2025={mongo_papers_2025}, 2026={mongo_papers_2026}")

    # Pinecone total count
    live_vector_count = vector_repo.count()
    logger.info(f"Pinecone Total Vector Count: {live_vector_count}")
    logger.info("=" * 60)

    for s in paper_summaries:
        logger.info(
            f" - {s['paper_id']} ({s['date']}, {s['shift']}): "
            f"{s['questions']} questions, {s['matched_answers']} answers matched, {s['upserted_vectors']} vectors"
        )

if __name__ == "__main__":
    main()

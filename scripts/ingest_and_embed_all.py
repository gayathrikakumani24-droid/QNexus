"""
Qnexus - Batch PDF Ingestion, Embedding, and Pinecone Cloud Indexing Script

Workflow:
1. Discovers all raw JEE Main question paper PDFs in data/raw/.
2. Parses shift metadata (date, session, shift) from filenames.
3. Extracts page-by-page text using PyMuPDF and saves to data/processed/.
4. Deterministically extracts questions, options, and official answer keys.
5. Persists questions to data/processed/{paper_id}_questions.json and MongoDB (if running).
6. Generates 384-dimensional embeddings using SentenceTransformers (all-MiniLM-L6-v2).
7. Upserts all vector records with rich metadata payloads to Pinecone Cloud.
8. Verifies index vector counts and reports per-paper statistics.
"""

import os
import sys
import glob
import json
import re
import logging
from typing import Dict, Any, List

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.core.config import settings
from app.services.pdf_parser import extract_pages_from_pdf
from app.services.extractor_service import extract_questions_from_pages
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository
from app.utils.id_generator import generate_paper_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ingest_and_embed")

MONTH_MAP = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05"
}

def parse_filename_metadata(filename: str) -> Dict[str, Any]:
    """
    Parses year, date, session, and shift from file names like:
    'JEE Main 2026 02 April Morning Shift Questions.pdf'
    """
    base = os.path.basename(filename)
    
    # Year
    year_match = re.search(r"202\d", base)
    year = int(year_match.group(0)) if year_match else 2026

    # Session / Month
    session = "April"
    month_code = "04"
    for m_name, m_code in MONTH_MAP.items():
        if m_name in base.lower():
            session = m_name.capitalize()
            month_code = m_code
            break

    # Day
    day_match = re.search(r"(\d{1,2})\s*(?:january|february|march|april|may)", base, re.IGNORECASE)
    day = int(day_match.group(1)) if day_match else 1
    date_str = f"{year}-{month_code}-{day:02d}"

    # Shift
    if "evening" in base.lower():
        shift = "Shift 2"
    elif "morning" in base.lower():
        shift = "Shift 1"
    else:
        shift_match = re.search(r"shift\s*([12])", base, re.IGNORECASE)
        shift = f"Shift {shift_match.group(1)}" if shift_match else "Shift 1"

    exam = "JEE Main"
    paper_id = generate_paper_id(exam, year, session, shift, date_str)

    return {
        "exam": exam,
        "year": year,
        "session": session,
        "day": day,
        "date": date_str,
        "shift": shift,
        "paper_id": paper_id,
        "filename": base
    }

def main():
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    pdf_files = sorted(glob.glob(os.path.join(raw_dir, "*.pdf")))
    logger.info(f"Found {len(pdf_files)} PDF papers in {raw_dir}")

    if not pdf_files:
        logger.error("No PDF files found in data/raw/")
        return

    # Check MongoDB optional availability
    mongo_available = False
    mongo_db = None
    try:
        from app.core.database import get_mongo_db
        mongo_db = get_mongo_db()
        # Fast ping
        mongo_db.command("ping")
        mongo_available = True
        logger.info("MongoDB connection verified. Authoritative documents will be saved to MongoDB.")
    except Exception:
        logger.warning("MongoDB is offline/unavailable. Questions will be cached in data/processed and indexed to Pinecone Cloud.")

    embedding_service = EmbeddingService()
    vector_repo = VectorRepository()

    total_papers_processed = 0
    total_questions_extracted = 0
    total_vectors_upserted = 0
    paper_summaries = []

    for idx, pdf_path in enumerate(pdf_files, 1):
        meta = parse_filename_metadata(pdf_path)
        paper_id = meta["paper_id"]
        logger.info(f"\n[{idx}/{len(pdf_files)}] Processing: {meta['filename']} -> Paper ID: {paper_id}")

        try:
            # 1. Extract pages text
            pages_data, warnings = extract_pages_from_pdf(
                pdf_path=pdf_path,
                paper_id=paper_id,
                output_dir=processed_dir
            )

            # 2. Extract structured questions
            questions = extract_questions_from_pages(
                pages_data=pages_data,
                paper_id=paper_id,
                paper_meta=meta
            )

            if not questions:
                logger.warning(f"No questions extracted for {paper_id}")
                continue

            # 3. Save questions to data/processed/{paper_id}_questions.json
            q_dump = [q.model_dump() for q in questions]
            json_path = os.path.join(processed_dir, f"{paper_id}_questions.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(q_dump, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(questions)} structured questions to {json_path}")

            # 4. Save to MongoDB if available
            if mongo_available and mongo_db is not None:
                from app.repositories.paper_repository import PaperRepository
                from app.repositories.question_repository import QuestionRepository
                from app.schemas.paper_schema import PaperCreate

                paper_repo = PaperRepository(mongo_db)
                question_repo = QuestionRepository(mongo_db)

                paper_repo.create_paper(PaperCreate(
                    paper_id=paper_id,
                    exam=meta["exam"],
                    year=meta["year"],
                    session=meta["session"],
                    date=meta["date"],
                    shift=meta["shift"],
                    filename=meta["filename"],
                    total_questions=len(questions),
                    status="PROCESSED"
                ))
                question_repo.bulk_create_questions(questions)
                logger.info(f"Persisted {len(questions)} questions into MongoDB.")

            # 5. Generate embeddings and prepare payloads
            records = embedding_service.embed_questions(questions=questions, batch_size=32)

            # Enrich payload with page_number and session/date
            for r, q in zip(records, questions):
                r["payload"]["page_number"] = q.page_number
                r["payload"]["session"] = q.session
                r["payload"]["date"] = q.date

            # 6. Upsert to Pinecone Cloud
            upserted = vector_repo.upsert_records(records)

            total_papers_processed += 1
            total_questions_extracted += len(questions)
            total_vectors_upserted += upserted

            paper_summaries.append({
                "paper": meta["filename"],
                "paper_id": paper_id,
                "date": meta["date"],
                "shift": meta["shift"],
                "questions": len(questions),
                "upserted": upserted
            })

            logger.info(f"Finished {paper_id}: {len(questions)} questions extracted & {upserted} vectors upserted to Pinecone.")

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}", exc_info=True)

    # 7. Final Verification
    logger.info("\n" + "=" * 60)
    logger.info("=== PINECONE CLOUD INGESTION SUMMARY ===")
    logger.info(f"Total Papers Processed: {total_papers_processed}/{len(pdf_files)}")
    logger.info(f"Total Questions Extracted: {total_questions_extracted}")
    logger.info(f"Total Vectors Upserted to Pinecone: {total_vectors_upserted}")
    
    live_count = vector_repo.count()
    logger.info(f"Live Pinecone Cloud Index Total Vector Count: {live_count}")
    logger.info("=" * 60)

    for s in paper_summaries:
        logger.info(f" - {s['paper_id']}: {s['questions']} questions, shift: {s['shift']}, date: {s['date']}")

if __name__ == "__main__":
    main()

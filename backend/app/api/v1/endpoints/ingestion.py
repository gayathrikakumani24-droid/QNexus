import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, Depends
from typing import Optional, List
from app.schemas.ingestion_schema import IngestionResponse
from app.schemas.question_metadata import ClassificationSummaryResponse
from app.schemas.paper_schema import PaperCreate
from app.core.database import get_mongo_db
from app.repositories.paper_repository import PaperRepository
from app.repositories.question_repository import QuestionRepository
from app.services.pdf_parser import extract_pages_from_pdf
from app.services.extractor_service import extract_questions_from_pages
from app.services.metadata_service import MetadataClassificationService
from app.utils.id_generator import generate_paper_id
import logging

logger = logging.getLogger("qnexus.api.ingestion")

router = APIRouter()

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "processed")

@router.post("/upload", response_model=IngestionResponse, summary="Upload PDF & Run Deterministic Ingestion Pipeline")
async def upload_pdf(
    file: UploadFile = File(..., description="Official shift-wise JEE Main PDF paper"),
    year: int = Form(2026, description="Exam year e.g. 2026"),
    session: str = Form("April", description="Session e.g. January or April"),
    date: str = Form("2026-04-05", description="Exam date YYYY-MM-DD"),
    shift: str = Form("Shift 1", description="Shift name e.g. Shift 1 or Shift 2"),
    exam: str = Form("JEE Main", description="Exam name")
):
    """
    Uploads a shift-wise JEE Main PDF paper, saves it under data/raw/, extracts text page-by-page,
    deterministically detects question boundaries, and persists questions to MongoDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    db = get_mongo_db()
    paper_repo = PaperRepository(db)
    question_repo = QuestionRepository(db)

    # 1. Generate stable paper_id
    paper_id = generate_paper_id(exam, year, session, shift, date)

    # 2. Save original PDF under data/raw/
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    saved_pdf_path = os.path.join(RAW_DATA_DIR, file.filename)
    
    try:
        with open(saved_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded PDF to {saved_pdf_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save PDF file: {str(e)}")

    # 3. Create or update paper record in MongoDB with status PROCESSING
    paper_create = PaperCreate(
        paper_id=paper_id,
        exam=exam,
        year=year,
        session=session,
        date=date,
        shift=shift,
        filename=file.filename,
        total_questions=None,
        status="PROCESSING"
    )
    paper_repo.create_paper(paper_create)
    paper_repo.update_paper_status(paper_id, "PROCESSING")

    try:
        # 4. Extract pages text using PyMuPDF
        pages_data, warnings = extract_pages_from_pdf(
            pdf_path=saved_pdf_path,
            paper_id=paper_id,
            output_dir=PROCESSED_DATA_DIR
        )

        paper_meta = {
            "year": year,
            "session": session,
            "date": date,
            "shift": shift,
            "exam": exam
        }

        # 5. Extract structured questions deterministically
        extracted_questions = extract_questions_from_pages(
            pages_data=pages_data,
            paper_id=paper_id,
            paper_meta=paper_meta
        )

        # 6. Store questions in MongoDB
        if extracted_questions:
            question_repo.bulk_create_questions(extracted_questions)

        # 7. Update paper status to PROCESSED
        total_q = len(extracted_questions)
        paper_repo.update_paper_status(paper_id, "PROCESSED", total_questions=total_q)

        return IngestionResponse(
            paper_id=paper_id,
            status="PROCESSED",
            pages=len(pages_data),
            questions_extracted=total_q,
            warnings=warnings
        )

    except Exception as e:
        logger.error(f"Error during ingestion pipeline execution: {e}", exc_info=True)
        paper_repo.update_paper_status(paper_id, "FAILED")
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline failed: {str(e)}")

@router.post("/{paper_id}/classify", response_model=ClassificationSummaryResponse, summary="Classify Question Metadata with Groq LLM")
async def classify_paper_metadata(
    paper_id: str,
    batch_size: int = Query(10, ge=1, le=50, description="Controlled batch size for classification"),
    overwrite: bool = Query(False, description="Whether to overwrite existing valid metadata")
):
    """
    Classifies subject, chapter, concept, difficulty, and question type for all questions in a paper using Groq LLM.
    """
    db = get_mongo_db()
    service = MetadataClassificationService(db=db)
    
    try:
        summary = service.classify_paper_questions(
            paper_id=paper_id,
            batch_size=batch_size,
            overwrite=overwrite
        )
        return summary
    except Exception as e:
        logger.error(f"Classification failed for paper {paper_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

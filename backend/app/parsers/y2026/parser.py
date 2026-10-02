"""
2026 JEE Main Paper Parser Wrapper.
Passes through directly to existing 2026 parsing services without altering any existing behavior.
"""

import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.question_schema import QuestionCreate
from app.services.pdf_parser import extract_pages_from_pdf
from app.services.extractor_service import extract_questions_from_pages
from app.utils.id_generator import generate_paper_id

logger = logging.getLogger("qnexus.parsers.y2026")

MONTH_MAP = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05"
}

def parse_2026_filename_metadata(filename: str) -> Dict[str, Any]:
    base = os.path.basename(filename)
    year_match = re.search(r"202\d", base)
    year = int(year_match.group(0)) if year_match else 2026

    session = "April"
    month_code = "04"
    for m_name, m_code in MONTH_MAP.items():
        if m_name in base.lower():
            session = m_name.capitalize()
            month_code = m_code
            break

    day_match = re.search(r"(\d{1,2})\s*(?:january|february|march|april|may)", base, re.IGNORECASE)
    day = int(day_match.group(1)) if day_match else 1
    date_str = f"{year}-{month_code}-{day:02d}"

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

def parse_2026_paper(
    pdf_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    output_dir: Optional[str] = None
) -> Tuple[List[QuestionCreate], Dict[str, Any]]:
    """
    Parses a 2026 JEE Main paper using the existing, verified 2026 pipeline.
    Preserves existing behavior completely.
    """
    meta = parse_2026_filename_metadata(pdf_path)
    if metadata:
        meta.update(metadata)

    paper_id = meta["paper_id"]
    target_output_dir = output_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "processed"
    )

    pages_data, warnings = extract_pages_from_pdf(
        pdf_path=pdf_path,
        paper_id=paper_id,
        output_dir=target_output_dir
    )

    questions = extract_questions_from_pages(
        pages_data=pages_data,
        paper_id=paper_id,
        paper_meta=meta
    )

    validation_report = {
        "year": 2026,
        "paper_id": paper_id,
        "total_questions": len(questions),
        "warnings": warnings,
        "status": "VALID" if len(questions) > 0 else "INVALID"
    }

    return questions, validation_report

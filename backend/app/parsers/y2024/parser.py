"""
2024 JEE Main Paper Parsing Orchestrator.
Orchestrates:
1. Dynamic answer key detection and parsing
2. Question segmentation and option parsing
3. Answer attachment and type normalization (MCQ vs NUMERICAL)
4. Comprehensive audit validation (90 questions)
5. Conversion to canonical QuestionCreate objects
"""

import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
import fitz

from app.schemas.question_schema import QuestionCreate, QuestionOption
from app.parsers.y2024.answer_key_parser import detect_answer_key_page, parse_2024_answer_key
from app.parsers.y2024.question_parser import parse_2024_questions_from_doc
from app.parsers.y2024.validator import validate_2024_paper

logger = logging.getLogger("qnexus.parsers.y2024.orchestrator")

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

OPTION_INDEX_TO_LETTER = {
    "1": "A", "2": "B", "3": "C", "4": "D",
    "A": "A", "B": "B", "C": "C", "D": "D"
}

LETTER_TO_INDEX = {
    "A": 0, "B": 1, "C": 2, "D": 3
}

def parse_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """
    Extracts year, date, session, shift, and paper_id from standard 2024 filenames.
    E.g. 'JEE Main 2024 (01 Feb Shift 1) Previous Year Paper with Answer Keys - MathonGo.pdf'
    """
    match = re.search(
        r'(\d{4})\s*\(\s*(\d{1,2})\s*([A-Za-z]+)\s*(Shift\s*[12])\s*\)',
        filename,
        re.IGNORECASE
    )
    if match:
        year = int(match.group(1))
        day = f"{int(match.group(2)):02d}"
        month_str = match.group(3).lower()
        month_num = MONTH_MAP.get(month_str, "01")
        shift_str = match.group(4)
        
        date_str = f"{year}-{month_num}-{day}"
        clean_date = date_str.replace("-", "_")
        clean_shift = shift_str.replace(" ", "_").upper()
        paper_id = f"JEE_MAIN_{clean_date}_{clean_shift}"

        # In 2024 JEE Main, January/February dates correspond to Session 1 ("January")
        session = "January" if month_num in ["01", "02"] else "April"
        return {
            "year": year,
            "session": session,
            "date": date_str,
            "shift": shift_str,
            "paper_id": paper_id
        }
    
    # Fallback default metadata
    basename = os.path.splitext(os.path.basename(filename))[0]
    return {
        "year": 2024,
        "session": "January",
        "date": "2024-01-27",
        "shift": "Shift 1",
        "paper_id": f"JEE_MAIN_2024_{re.sub(r'[^A-Za-z0-9_]+', '_', basename)}"
    }

def attach_2024_answers(
    raw_questions: List[Dict[str, Any]],
    answer_map: Dict[int, Dict[str, Any]],
    paper_meta: Dict[str, Any],
    ak_page_num: Optional[int] = None
) -> List[QuestionCreate]:
    """
    Merges segmented questions with answer key records and builds canonical QuestionCreate objects.
    Ensures answers are NEVER injected into content text (preserving RAG embedding integrity).
    """
    year = int(paper_meta.get("year", 2024))
    session = str(paper_meta.get("session", "January"))
    date_val = str(paper_meta.get("date", "2024-01-27"))
    shift_val = str(paper_meta.get("shift", "Shift 1"))
    paper_id = str(paper_meta.get("paper_id", f"JEE_MAIN_2024_{shift_val.replace(' ', '_').upper()}"))

    clean_date = date_val.replace("-", "_")
    clean_shift = shift_val.replace(" ", "_").upper()
    prefix_date = clean_date if clean_date.startswith(str(year)) else f"{year}_{clean_date}"

    canonical_questions: List[QuestionCreate] = []

    for q in raw_questions:
        q_num = q["question_number"]
        q_type = q["question_type"]
        q_content = q["content"]
        raw_options = q.get("options", [])
        page_num = q.get("page_number", 1)
        subject = q.get("subject", "General")

        # Lookup answer entry
        ans_entry = answer_map.get(q_num)
        correct_option: Optional[str] = None
        numerical_answer: Optional[float] = None
        structured_answer: Optional[Dict[str, Any]] = None
        raw_ans_str: Optional[str] = None

        if ans_entry:
            raw_ans_str = str(ans_entry.get("raw", "")).strip()

            if q_type == "MCQ":
                # Convert raw '1'-'4' or 'A'-'D' to canonical option letter
                correct_option = OPTION_INDEX_TO_LETTER.get(raw_ans_str, raw_ans_str.upper())
                opt_idx = LETTER_TO_INDEX.get(correct_option)
                structured_answer = {
                    "type": "MCQ",
                    "raw": raw_ans_str,
                    "correct_option": correct_option,
                    "option_index": opt_idx
                }
            else:
                # Numerical question
                try:
                    num_val = float(raw_ans_str)
                    numerical_answer = num_val
                except ValueError:
                    num_val = None

                structured_answer = {
                    "type": "NUMERICAL",
                    "raw": raw_ans_str,
                    "value": numerical_answer
                }

        # Build Option models
        formatted_options = [
            QuestionOption(id=opt["id"], content=opt["content"])
            for opt in raw_options
        ]

        question_id = f"JEE_MAIN_{prefix_date}_{clean_shift}_Q_{q_num:02d}"

        q_metadata = {
            "source_format": "2024_separate_answer_key",
            "answer_key_page": ak_page_num,
            "raw_answer": raw_ans_str
        }

        q_obj = QuestionCreate(
            question_id=question_id,
            paper_id=paper_id,
            question_number=q_num,
            content=q_content,
            options=formatted_options,
            correct_option=correct_option,
            numerical_answer=numerical_answer,
            official_solution=None,
            subject=subject,
            chapter=None,
            concept=None,
            difficulty="Medium",
            question_type=q_type,
            has_images=False,
            image_urls=[],
            page_number=page_num,
            year=year,
            session=session,
            date=date_val,
            shift=shift_val,
            exam="JEE Main",
            answer=structured_answer,
            metadata=q_metadata
        )
        canonical_questions.append(q_obj)

    return canonical_questions

def parse_2024_paper(
    pdf_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    return_report: bool = False
) -> Union[List[QuestionCreate], Tuple[List[QuestionCreate], Dict[str, Any]]]:
    """
    Parses a JEE Main 2024 paper from PDF.
    Extracts 90 questions and answer key, normalizes types, validates, and builds canonical QuestionCreate objects.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    # Resolve metadata
    file_meta = parse_metadata_from_filename(os.path.basename(pdf_path))
    if metadata:
        file_meta.update(metadata)

    doc = fitz.open(pdf_path)
    try:
        # Step 1: Detect answer key page
        ak_page_idx = detect_answer_key_page(doc)
        answer_map: Dict[int, Dict[str, Any]] = {}

        if ak_page_idx is not None:
            ak_text = doc[ak_page_idx].get_text("text")
            answer_map = parse_2024_answer_key(ak_text)
            ak_page_num = ak_page_idx + 1
        else:
            ak_page_num = None
            logger.warning(f"No answer key page identified in {pdf_path}")

        # Step 2: Segment questions
        raw_questions = parse_2024_questions_from_doc(doc, ak_page_idx)

        # Step 3: Run validation audit (90 questions expected)
        report = validate_2024_paper(raw_questions, answer_map, expected_total=90)

        # Step 4: Attach answers and build canonical QuestionCreate objects
        questions = attach_2024_answers(
            raw_questions=raw_questions,
            answer_map=answer_map,
            paper_meta=file_meta,
            ak_page_num=ak_page_num
        )

        logger.info(
            f"Parsed 2024 paper '{file_meta['paper_id']}': "
            f"{len(questions)} questions extracted, {report['matched']} answers matched."
        )

        if return_report:
            return questions, report
        return questions

    finally:
        doc.close()

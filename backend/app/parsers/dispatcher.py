"""
Unified Parser Dispatcher for JEE Main PYQ papers.
Directs PDFs to their year/format-specific parsers while guaranteeing that
both 2025 and 2026 parsers produce the identical canonical QuestionCreate schema.
"""

import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Union

from app.schemas.question_schema import QuestionCreate
from app.parsers.y2024.parser import parse_2024_paper
from app.parsers.y2025.parser import parse_2025_paper
from app.parsers.y2026.parser import parse_2026_paper

logger = logging.getLogger("qnexus.parsers.dispatcher")

class UnsupportedPaperFormatError(Exception):
    """Raised when an unrecognized exam paper year or format is submitted."""
    pass

def detect_year_from_input(pdf_path: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Attempts to identify the exam year from metadata or the PDF filepath.
    """
    if metadata and "year" in metadata:
        try:
            return int(metadata["year"])
        except (ValueError, TypeError):
            pass

    base = os.path.basename(pdf_path)
    match = re.search(r'(?:^|\D)(202\d)(?:\D|$)', base)
    if match:
        return int(match.group(1))

    return None

def parse_paper(
    pdf_path: str,
    year: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    return_report: bool = False
) -> Union[List[QuestionCreate], Tuple[List[QuestionCreate], Dict[str, Any]]]:
    """
    Dispatches paper parsing to year-specific implementations.

    Args:
        pdf_path: Path to the paper PDF.
        year: Optional exam year (e.g. 2024, 2025, 2026). If None, inferred automatically.
        metadata: Optional dictionary with paper metadata overrides.
        return_report: If True, returns (List[QuestionCreate], validation_report).
                       If False, returns List[QuestionCreate].

    Returns:
        Canonical QuestionCreate list, or (questions, report) tuple.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        UnsupportedPaperFormatError: If year is not supported.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file does not exist: {pdf_path}")

    resolved_year = year or detect_year_from_input(pdf_path, metadata)

    if resolved_year == 2026:
        logger.info(f"Dispatching '{pdf_path}' to 2026 parsing pipeline.")
        questions, report = parse_2026_paper(pdf_path=pdf_path, metadata=metadata)
        if return_report:
            return questions, report
        return questions

    elif resolved_year == 2025:
        logger.info(f"Dispatching '{pdf_path}' to 2025 parsing pipeline.")
        return parse_2025_paper(
            pdf_path=pdf_path,
            metadata=metadata,
            return_report=return_report
        )

    elif resolved_year == 2024:
        logger.info(f"Dispatching '{pdf_path}' to 2024 parsing pipeline.")
        return parse_2024_paper(
            pdf_path=pdf_path,
            metadata=metadata,
            return_report=return_report
        )

    else:
        err_msg = (
            f"Unsupported exam paper year '{resolved_year}' for file '{pdf_path}'. "
            f"Supported years are: 2024, 2025, 2026."
        )
        logger.error(err_msg)
        raise UnsupportedPaperFormatError(err_msg)

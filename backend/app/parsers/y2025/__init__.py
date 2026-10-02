"""
2025 JEE Main Parser Package.
"""

from app.parsers.y2025.parser import parse_2025_paper
from app.parsers.y2025.answer_key_parser import parse_2025_answer_key, detect_answer_key_page
from app.parsers.y2025.question_parser import parse_2025_questions_from_doc
from app.parsers.y2025.validator import validate_2025_paper

__all__ = [
    "parse_2025_paper",
    "parse_2025_answer_key",
    "detect_answer_key_page",
    "parse_2025_questions_from_doc",
    "validate_2025_paper"
]

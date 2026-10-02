"""
2024 JEE Main Parser Package.
"""

from app.parsers.y2024.parser import parse_2024_paper
from app.parsers.y2024.answer_key_parser import parse_2024_answer_key, detect_answer_key_page
from app.parsers.y2024.question_parser import parse_2024_questions_from_doc
from app.parsers.y2024.validator import validate_2024_paper

__all__ = [
    "parse_2024_paper",
    "parse_2024_answer_key",
    "detect_answer_key_page",
    "parse_2024_questions_from_doc",
    "validate_2024_paper"
]

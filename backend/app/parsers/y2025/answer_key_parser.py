"""
2025 JEE Main Answer Key Parser.
Dynamically detects the answer key page and extracts (question_number -> raw_answer) pairs
using deterministic regex matching.
"""

import re
import logging
from typing import Dict, Any, Optional
import fitz

logger = logging.getLogger("qnexus.parsers.y2025.answer_key")

ANSWER_KEY_PAGE_PATTERN = re.compile(r'ANSWER\s*KEYS?', re.IGNORECASE)
ANSWER_ENTRY_PATTERN = re.compile(r'(\d+)\.\s*\(([^)]+)\)')

def detect_answer_key_page(doc: fitz.Document) -> Optional[int]:
    """
    Scans the document pages (starting from the end) to dynamically identify the answer-key page.
    Returns 0-indexed page number or None if not found.
    """
    total_pages = len(doc)
    # 2025 answer keys are almost always on the last or penultimate page
    for page_idx in range(total_pages - 1, -1, -1):
        try:
            page_text = doc[page_idx].get_text("text")
            if ANSWER_KEY_PAGE_PATTERN.search(page_text):
                logger.info(f"Detected 2025 answer key on page {page_idx + 1} of {total_pages}")
                return page_idx
        except Exception as e:
            logger.warning(f"Error reading page {page_idx + 1} text: {e}")
            continue

    logger.warning("Could not detect 'ANSWER KEYS' page in 2025 document.")
    return None

def parse_2025_answer_key(text: str) -> Dict[int, Dict[str, Any]]:
    r"""
    Extracts all (question_number, answer) pairs from the answer key text.
    1. Normalizes whitespace and line wraps.
    2. Uses deterministic regex r'(\d+)\.\s*\(([^)]+)\)'.
    3. Handles integer and decimal numerical answers.
    4. Returns a dictionary:
       {
           1: {"raw": "4"},
           21: {"raw": "34"},
           22: {"raw": "2035"},
           ...
       }
    """
    if not text or not text.strip():
        return {}

    # Normalize whitespace: collapse multiple spaces and tabs, but keep single spaces
    normalized = re.sub(r'[ \t]+', ' ', text)

    matches = list(ANSWER_ENTRY_PATTERN.finditer(normalized))
    answer_map: Dict[int, Dict[str, Any]] = {}

    for match in matches:
        q_num_str = match.group(1)
        raw_ans = match.group(2).strip()

        try:
            q_num = int(q_num_str)
            # Normalize internal whitespace in answer string if any
            clean_raw = re.sub(r'\s+', ' ', raw_ans).strip()
            answer_map[q_num] = {
                "raw": clean_raw
            }
        except ValueError:
            logger.warning(f"Failed to parse question number integer from '{q_num_str}'")

    logger.info(f"Extracted {len(answer_map)} answer key entries from text.")
    return answer_map

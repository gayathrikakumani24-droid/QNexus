"""
2024 JEE Main Question Parser.
Segments questions from 2024 PDF pages, isolates question body, extracts MCQ options,
identifies numerical questions, and assigns subjects deterministically.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
import fitz

logger = logging.getLogger("qnexus.parsers.y2024.question")

# Boundary pattern for questions 1 to 90 in 2024 papers
QUESTION_BOUNDARY_PATTERN = re.compile(
    r'(?:Q\.?\s*(\d{1,2})[\.\:]|Question\s*(\d{1,2})[\.\:])'
)

# Option marker pattern: (1), (2), (3), (4) with lookbehind supporting attached digits while avoiding 'Statement (1)'
OPTION_MARKER_PATTERN = re.compile(
    r'(?<!statement\s)(?<!statement)(?:(?<=[\s\n\r\d])|(?<=^))(?:\(([1-4])\)|(?<=[\s\n\r])([1-4])\.)',
    re.IGNORECASE
)

# Common noise in 2024 MathonGo papers
NOISE_PATTERNS = [
    r'#PaperPhodnaHai',
    r'www\.mathongo\.com',
    r'MathonGo',
    r'JEE\s+Main\s+Previous\s+Year\s+Paper',
    r'JEE\s+Main\s+\d{4}\s+(?:January|February|April|Shift\s*\d+)?',
    r'\d{4}\s*\(\s*\d{1,2}\s+[A-Za-z]+\s+Shift\s*\d+\s*\)',
    r'---PAGE_BREAK---'
]

def clean_noise(text: str) -> str:
    """Removes standard MathonGo watermarks, headers, and footer noise."""
    for pat in NOISE_PATTERNS:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    return text.strip()

def normalize_whitespace(text: str) -> str:
    """Collapses repeated spaces/tabs while preserving line clarity."""
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append('')
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False
    return '\n'.join(cleaned_lines).strip()

def extract_mcq_options(raw_chunk: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Extracts question statement and options (1), (2), (3), (4) from raw question chunk.
    Works backwards from the end to find the final four option markers (1, 2, 3, 4)
    to avoid false positives inside the question statement (e.g. Statement 1, Statement 2).
    Returns (cleaned_question_content, [ {"id": "A", "content": ...}, ... ]).
    """
    clean_chunk = clean_noise(raw_chunk)
    opt_matches = list(OPTION_MARKER_PATTERN.finditer(clean_chunk))
    if not opt_matches:
        return normalize_whitespace(clean_chunk), []

    # Group matches by option number
    by_key = {
        k: [m for m in opt_matches if (m.group(1) or m.group(2)) == str(k)]
        for k in [1, 2, 3, 4]
    }

    if not all(len(by_key[k]) > 0 for k in [1, 2, 3, 4]):
        return normalize_whitespace(clean_chunk), []

    best_seq = None

    # First attempt: standard order (1 < 2 < 3 < 4)
    for m3 in reversed(by_key[4]):
        for m2 in reversed(by_key[3]):
            if m2.start() >= m3.start():
                continue
            for m1 in reversed(by_key[2]):
                if m1.start() >= m2.start():
                    continue
                for m0 in reversed(by_key[1]):
                    if m0.start() >= m1.start():
                        continue
                    best_seq = [
                        (m0.start(), m0.end(), 1),
                        (m1.start(), m1.end(), 2),
                        (m2.start(), m2.end(), 3),
                        (m3.start(), m3.end(), 4)
                    ]
                    break
                if best_seq:
                    break
            if best_seq:
                break
        if best_seq:
            break

    # Fallback attempt: two-column layout where (4) is extracted before (3) (1 < 2 < 4 < 3)
    if not best_seq:
        for m2 in reversed(by_key[3]):
            for m3 in reversed(by_key[4]):
                if m3.start() >= m2.start():
                    continue
                for m1 in reversed(by_key[2]):
                    if m1.start() >= m3.start():
                        continue
                    for m0 in reversed(by_key[1]):
                        if m0.start() >= m1.start():
                            continue
                        best_seq = sorted([
                            (m0.start(), m0.end(), 1),
                            (m1.start(), m1.end(), 2),
                            (m2.start(), m2.end(), 3),
                            (m3.start(), m3.end(), 4)
                        ], key=lambda x: x[0])
                        break
                    if best_seq:
                        break
                if best_seq:
                    break
            if best_seq:
                break

    if not best_seq:
        return normalize_whitespace(clean_chunk), []

    markers = best_seq

    # Everything before the first option marker is the question statement
    content_raw = clean_chunk[:markers[0][0]]
    cleaned_content = normalize_whitespace(content_raw)

    id_map = {1: "A", 2: "B", 3: "C", 4: "D"}
    options_by_num: Dict[int, str] = {}

    for idx, (m_start, m_end, opt_num) in enumerate(markers):
        next_start = markers[idx + 1][0] if idx + 1 < len(markers) else len(clean_chunk)
        opt_text = clean_chunk[m_end:next_start]
        options_by_num[opt_num] = normalize_whitespace(opt_text)

    # Clean Option 4 if PyMuPDF sorted next question's equation lines before question header
    opt4_text = options_by_num.get(4, "")
    if "\n\n" in opt4_text:
        parts = opt4_text.split("\n\n", 1)
        trailing = parts[1].strip()
        if trailing.startswith("=") or "is equal to" in trailing or trailing.endswith(":"):
            options_by_num[4] = normalize_whitespace(parts[0])

    options_list = [
        {"id": id_map[i], "content": options_by_num.get(i, "")}
        for i in [1, 2, 3, 4]
    ]

    return cleaned_content, options_list

def get_subject_for_qnum(q_num: int) -> str:
    """Returns the standard JEE Main 2024 subject based on question number."""
    if 1 <= q_num <= 30:
        return "Physics"
    elif 31 <= q_num <= 60:
        return "Chemistry"
    elif 61 <= q_num <= 90:
        return "Mathematics"
    return "General"

def is_expected_mcq_2024(q_num: int) -> bool:
    """
    2024 JEE Main format:
    Physics: 1..20 MCQ, 21..30 Numerical
    Chemistry: 31..50 MCQ, 51..60 Numerical
    Mathematics: 61..80 MCQ, 81..90 Numerical
    """
    return (1 <= q_num <= 20) or (31 <= q_num <= 50) or (61 <= q_num <= 80)

def parse_2024_questions_from_doc(
    doc: fitz.Document,
    answer_key_page_idx: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Extracts all 90 questions from the document pages preceding the answer key.
    Returns raw parsed question records:
    [
        {
            "question_number": int,
            "content": str,
            "options": List[Dict[str, str]], # empty if numerical
            "question_type": "MCQ" | "NUMERICAL",
            "subject": str,
            "page_number": int
        }, ...
    ]
    """
    max_page = answer_key_page_idx if (answer_key_page_idx is not None and answer_key_page_idx >= 0) else len(doc)

    full_text = ""
    page_map = []
    for p_idx in range(max_page):
        p_num = p_idx + 1
        page_text = doc[p_idx].get_text("text", sort=True)
        start_idx = len(full_text)
        full_text += page_text + "\n"
        end_idx = len(full_text)
        page_map.append((start_idx, end_idx, p_num))

    def get_page_number(pos: int) -> int:
        for start, end, p_num in page_map:
            if start <= pos < end:
                return p_num
        return 1

    matches = list(QUESTION_BOUNDARY_PATTERN.finditer(full_text))
    valid_matches = []
    seen_numbers = set()
    for m in matches:
        q_num = int(m.group(1) or m.group(2))
        if 1 <= q_num <= 90 and q_num not in seen_numbers:
            valid_matches.append((q_num, m))
            seen_numbers.add(q_num)

    valid_matches.sort(key=lambda x: x[0])

    extracted_questions: List[Dict[str, Any]] = []

    for idx, (q_num, match) in enumerate(valid_matches):
        pos_for_page = match.start()
        page_num = get_page_number(pos_for_page)

        start_content = match.end()
        current_m_start = match.start()
        next_m_positions = [
            m.start() for q_n, m in valid_matches
            if m.start() > current_m_start
        ]
        end_content = min(next_m_positions) if next_m_positions else len(full_text)

        raw_q_chunk = full_text[start_content:end_content]
        subject = get_subject_for_qnum(q_num)
        expected_mcq = is_expected_mcq_2024(q_num)

        cleaned_content, options = extract_mcq_options(raw_q_chunk)

        if options and len(options) == 4 and expected_mcq:
            q_type = "MCQ"
        elif expected_mcq and options:
            q_type = "MCQ"
        else:
            q_type = "NUMERICAL"
            options = []
            cleaned_content = normalize_whitespace(clean_noise(raw_q_chunk))

        extracted_questions.append({
            "question_number": q_num,
            "content": cleaned_content,
            "options": options,
            "question_type": q_type,
            "subject": subject,
            "page_number": page_num
        })

    logger.info(f"Successfully segmented {len(extracted_questions)} questions from 2024 PDF.")
    return extracted_questions

import re
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.question_schema import QuestionCreate, QuestionOption
import logging

logger = logging.getLogger("qnexus.services.extractor_service")

# Regular expression pattern to detect question boundaries
QUESTION_BOUNDARY_PATTERN = re.compile(
    r"(?:\n|^)\s*(?:Q\.?\s*(\d+)[\.\:]?|Question\s*(\d+)[\.\:]?)\s*",
    re.IGNORECASE
)

# Regular expression pattern to detect options
OPTION_PATTERN = re.compile(
    r"^\s*(?:\((\d|[A-D])\)|([A-D])\))\s*(.*)$",
    re.IGNORECASE
)

OPTION_KEY_MAP = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D'}

NOISE_PATTERNS = [
    r'#PaperPhodnaHai',
    r'www\.mathongo\.com',
    r'MathonGo',
    r'Answer\s*Keys',
    r'\d{2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\((?:Morning|Evening)\s+Shift\)',
    r'JEE\s+Main\s+\d{4}'
]

def clean_noise(text: str) -> str:
    for pat in NOISE_PATTERNS:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    return text

def parse_options_from_text(raw_text: str) -> Tuple[str, List[QuestionOption]]:
    """
    Parses options and question content from raw question text.
    Handles single-line, multi-line, and grid option layouts cleanly.
    Stops at Answer Key to avoid trailing noise in option D.
    """
    # Cut off Answer Key
    ans_m = re.search(r"MathonGo\s*Answer\s*Key\s*:", raw_text, re.IGNORECASE)
    body = raw_text[:ans_m.start()] if ans_m else raw_text
    
    # Strip page noise
    body = clean_noise(body).rstrip()

    # Pattern for option delimiter: (1), (2), (3), (4) or (A), (B), (C), (D) or 1), 2), 3), 4) or A), B), C), D)
    delim_pattern = re.compile(r'(?:(?<=\s)|(?<=^))(?:\(([1-4A-D])\)|([1-4A-D])\))\s*')
    matches = list(delim_pattern.finditer(body))

    best_seq = None
    for target in [['1', '2', '3', '4'], ['A', 'B', 'C', 'D']]:
        by_key = {k: [m for m in matches if (m.group(1) or m.group(2)).upper() == k] for k in target}
        if all(len(by_key[k]) > 0 for k in target):
            for m3 in reversed(by_key[target[3]]):
                for m2 in reversed(by_key[target[2]]):
                    if m2.start() >= m3.start():
                        continue
                    for m1 in reversed(by_key[target[1]]):
                        if m1.start() >= m2.start():
                            continue
                        for m0 in reversed(by_key[target[0]]):
                            if m0.start() >= m1.start():
                                continue
                            best_seq = (target, [m0, m1, m2, m3])
                            break
                        if best_seq:
                            break
                    if best_seq:
                        break
                if best_seq:
                    break
        if best_seq:
            break

    if best_seq:
        target, markers = best_seq
        m0, m1, m2, m3 = markers

        # Case A: 1x4 layout (all 4 markers on the same line)
        if '\n' not in body[m0.start():m3.end()]:
            line_start = body.rfind('\n', 0, m0.start())
            line_start = 0 if line_start == -1 else line_start + 1
            line_end = body.find('\n', m3.end())
            line_end = len(body) if line_end == -1 else line_end

            num = [
                body[m0.end():m1.start()].strip(),
                body[m1.end():m2.start()].strip(),
                body[m2.end():m3.start()].strip(),
                body[m3.end():line_end].strip()
            ]

            # Check for denominator line immediately following line_end
            den = ['', '', '', '']
            trailing = body[line_end:].strip()
            if trailing:
                sub_line = trailing.split('\n')[0]
                if not re.search(r'(?:\([1-4A-D]\)|Q\d+|Answer\s*Key)', sub_line, re.IGNORECASE):
                    tokens = list(re.finditer(r'\S+', sub_line))
                    if len(tokens) == 4:
                        den = [t.group(0) for t in tokens]
                    elif 0 < len(tokens) < 4:
                        anchors = [
                            m0.start() - line_start,
                            m1.start() - line_start - 4,
                            m2.start() - line_start - 8,
                            m3.start() - line_start - 12
                        ]
                        for t in tokens:
                            best_i = min(range(4), key=lambda i: abs(anchors[i] - t.start()))
                            den[best_i] = t.group(0)

            options = []
            for i in range(4):
                val = f"{num[i]}/{den[i]}" if den[i] else num[i]
                val = re.sub(r'[ \t]+', ' ', val).strip()
                options.append(QuestionOption(id=OPTION_KEY_MAP[target[i]], content=val))
            content = body[:line_start].strip()
            return content, options

        # Case B: 2x2 layout (m0, m1 on one line, m2, m3 on next row)
        if '\n' not in body[m0.start():m1.end()] and '\n' not in body[m2.start():m3.end()]:
            r1_start = body.rfind('\n', 0, m0.start())
            r1_start = 0 if r1_start == -1 else r1_start + 1
            r1_end = body.find('\n', m1.end())
            r1_end = len(body) if r1_end == -1 else r1_end

            r2_start = body.rfind('\n', 0, m2.start())
            r2_start = 0 if r2_start == -1 else r2_start + 1
            r2_end = body.find('\n', m3.end())
            r2_end = len(body) if r2_end == -1 else r2_end

            num0 = body[m0.end():m1.start()].strip()
            num1 = body[m1.end():r1_end].strip()
            num2 = body[m2.end():m3.start()].strip()
            num3 = body[m3.end():r2_end].strip()
            nums = [num0, num1, num2, num3]
            dens = ['', '', '', '']

            # Between row 1 and row 2 check for sub_line 1
            between = body[r1_end:r2_start].strip()
            if between:
                sub1 = between.split('\n')[0]
                tokens1 = list(re.finditer(r'\S+', sub1))
                if len(tokens1) == 2:
                    dens[0] = tokens1[0].group(0)
                    dens[1] = tokens1[1].group(0)
                elif len(tokens1) == 1:
                    mid = (m0.start() + m1.start()) / 2
                    idx = 0 if tokens1[0].start() < mid else 1
                    dens[idx] = tokens1[0].group(0)

            # After row 2 check for sub_line 2
            after = body[r2_end:].strip()
            if after:
                sub2 = after.split('\n')[0]
                if not re.search(r'(?:\([1-4A-D]\)|Q\d+|Answer\s*Key)', sub2, re.IGNORECASE):
                    tokens2 = list(re.finditer(r'\S+', sub2))
                    if len(tokens2) == 2:
                        dens[2] = tokens2[0].group(0)
                        dens[3] = tokens2[1].group(0)
                    elif len(tokens2) == 1:
                        mid = (m2.start() + m3.start()) / 2
                        idx = 2 if tokens2[0].start() < mid else 3
                        dens[idx] = tokens2[0].group(0)

            options = []
            for i in range(4):
                val = f"{nums[i]}/{dens[i]}" if dens[i] else nums[i]
                val = re.sub(r'[ \t]+', ' ', val).strip()
                options.append(QuestionOption(id=OPTION_KEY_MAP[target[i]], content=val))
            content = body[:r1_start].strip()
            return content, options

        # Default fallback
        content = body[:markers[0].start()].strip()
        options = []
        for i in range(4):
            opt_id = OPTION_KEY_MAP[target[i]]
            start = markers[i].end()
            end = markers[i + 1].start() if i < 3 else len(body)
            opt_val = body[start:end].strip()
            # Clean up multi-space or newlines inside option content
            opt_val = re.sub(r'[ \t]+', ' ', opt_val).strip()
            options.append(QuestionOption(id=opt_id, content=opt_val))
        return content, options

    # Fallback to line-by-line parsing if sequence wasn't found
    lines = body.split('\n')
    content_lines = []
    options: List[QuestionOption] = []
    current_opt_id = None
    current_opt_content = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        match = OPTION_PATTERN.match(stripped)
        if match:
            if current_opt_id:
                options.append(QuestionOption(
                    id=current_opt_id,
                    content=" ".join(current_opt_content).strip()
                ))
                current_opt_content = []

            raw_opt_id = match.group(1) or match.group(2)
            current_opt_id = OPTION_KEY_MAP.get(raw_opt_id, raw_opt_id.upper())
            rest_of_text = match.group(3).strip()
            if rest_of_text:
                current_opt_content.append(rest_of_text)
        elif current_opt_id:
            current_opt_content.append(stripped)
        else:
            content_lines.append(line)

    if current_opt_id:
        options.append(QuestionOption(
            id=current_opt_id,
            content=" ".join(current_opt_content).strip()
        ))

    clean_content = "\n".join(content_lines).strip()
    return (clean_content if clean_content else body.strip()), options

def extract_questions_from_pages(
    pages_data: List[Dict[str, Any]],
    paper_id: str,
    paper_meta: Dict[str, Any]
) -> List[QuestionCreate]:
    """
    Deterministically parses page texts into structured QuestionCreate objects.
    Preserves question boundaries, option extraction, and page numbers.
    """
    questions: List[QuestionCreate] = []
    
    year = int(paper_meta.get("year", 2026))
    session = str(paper_meta.get("session", "April"))
    date_val = str(paper_meta.get("date", "2026-04-04"))
    clean_date = date_val.replace("-", "_")
    shift_val = str(paper_meta.get("shift", "Shift 2"))
    clean_shift = shift_val.replace(" ", "_").upper()
    
    # Combine full document text for pattern matching while mapping char positions to page numbers
    full_text = ""
    page_map = []
    for p in pages_data:
        p_num = p["page_number"]
        p_text = p["text"]
        start_idx = len(full_text)
        full_text += p_text + "\n"
        end_idx = len(full_text)
        page_map.append((start_idx, end_idx, p_num))

    def get_page_number_for_pos(pos: int) -> int:
        for start, end, p_num in page_map:
            if start <= pos < end:
                return p_num
        return 1

    matches = list(QUESTION_BOUNDARY_PATTERN.finditer(full_text))

    if not matches:
        logger.warning(f"No question boundaries found in text for paper {paper_id}")
        return []

    for i, match in enumerate(matches):
        q_num_str = match.group(1) or match.group(2)
        if not q_num_str:
            continue
        
        q_num = int(q_num_str)
        # Use match.end() or position of the number to accurately determine page number
        pos_for_page = match.start(1) if match.group(1) else match.start(2)
        page_num = get_page_number_for_pos(pos_for_page)

        start_content_pos = match.end()
        end_content_pos = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        
        raw_q_text = full_text[start_content_pos:end_content_pos].strip()

        # Extract Answer Key if present
        correct_option = None
        numerical_answer = None
        ans_match = re.search(r"MathonGo\s*Answer\s*Key\s*:\s*(?:\(?([1-4A-D])\)?|([\d\.\-]+))", raw_q_text, re.IGNORECASE)
        if ans_match:
            if ans_match.group(1):
                raw_opt = ans_match.group(1)
                correct_option = OPTION_KEY_MAP.get(raw_opt, raw_opt.upper())
            elif ans_match.group(2):
                try:
                    num_val = float(ans_match.group(2))
                    numerical_answer = int(num_val) if num_val.is_integer() else num_val
                except ValueError:
                    pass

        # Standard JEE Main shift subject division
        if q_num <= 25:
            default_subject = "Mathematics"
        elif q_num <= 50:
            default_subject = "Physics"
        elif q_num <= 75:
            default_subject = "Chemistry"
        else:
            default_subject = "General"

        clean_content, options = parse_options_from_text(raw_q_text)

        # Stable question ID format: JEE_MAIN_{DATE}_{SHIFT}_Q_{QUESTION_NUMBER}
        prefix_date = clean_date if clean_date.startswith(str(year)) else f"{year}_{clean_date}"
        question_id = f"JEE_MAIN_{prefix_date}_{clean_shift}_Q_{q_num}"
        question_type = "MCQ" if len(options) > 0 else "NUMERICAL"

        question_obj = QuestionCreate(
            question_id=question_id,
            paper_id=paper_id,
            question_number=q_num,
            content=clean_content if clean_content else raw_q_text,
            options=options,
            correct_option=correct_option,
            numerical_answer=numerical_answer,
            official_solution=None,
            subject=default_subject,
            chapter=None,
            concept=None,
            difficulty="Medium",
            question_type=question_type,
            has_images=False,
            image_urls=[],
            page_number=page_num,
            year=year,
            session=session,
            date=date_val,
            shift=shift_val
        )
        questions.append(question_obj)

    logger.info(f"Extracted {len(questions)} questions deterministically for paper {paper_id}")
    return questions

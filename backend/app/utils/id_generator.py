import hashlib

def generate_paper_id(exam: str, year: int, session: str, shift: str, date: str = "") -> str:
    """
    Generates a deterministic stable string ID for a paper.
    Example: 'JEE_MAIN_2026_APRIL_SHIFT_2'
    """
    clean_exam = exam.strip().replace(" ", "_").upper()
    clean_session = session.strip().replace(" ", "_").upper()
    clean_shift = shift.strip().replace(" ", "_").upper()
    if date:
        clean_date = date.strip().replace("-", "_")
        return f"{clean_exam}_{clean_date}_{clean_shift}"
    return f"{clean_exam}_{year}_{clean_session}_{clean_shift}"

def generate_question_id(paper_id: str, question_number: int) -> str:
    """
    Generates a deterministic, stable string ID for a question using paper_id and question_number.
    Example: 'JEE_MAIN_2026_APRIL_SHIFT_2_Q01'
    """
    return f"{paper_id}_Q{question_number:02d}"

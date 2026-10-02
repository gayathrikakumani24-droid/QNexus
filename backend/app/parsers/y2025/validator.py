"""
2025 JEE Main Validation Module.
Audits the results of the 2025 question extraction and answer-key parsing,
producing a structured report with missing, duplicate, and unmatched entries.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger("qnexus.parsers.y2025.validator")

def validate_2025_paper(
    questions: List[Any],
    answer_map: Dict[int, Dict[str, Any]],
    expected_total: int = 75
) -> Dict[str, Any]:
    """
    Validates the consistency between extracted questions and answer key entries.
    Returns a standardized dictionary report:
    {
        "total_questions": 75,
        "total_answers": 75,
        "matched": 75,
        "missing_questions": [],
        "missing_answers": [],
        "duplicate_questions": [],
        "duplicate_answers": [],
        "unmatched_questions": [],
        "anomalies": [],
        "is_valid": True
    }
    """
    question_nums = []
    duplicate_questions = []
    seen_q = set()

    for q in questions:
        q_num = getattr(q, "question_number", None)
        if q_num is None and isinstance(q, dict):
            q_num = q.get("question_number")
        
        if q_num in seen_q:
            duplicate_questions.append(q_num)
        elif q_num is not None:
            seen_q.add(q_num)
            question_nums.append(q_num)

    answer_nums = list(answer_map.keys())
    duplicate_answers = [] # keys are unique in dict, but list tracked for completeness

    # Check for missing questions (1..expected_total)
    expected_range = set(range(1, expected_total + 1))
    missing_questions = sorted(list(expected_range - set(question_nums)))
    missing_answers = sorted(list(expected_range - set(answer_nums)))

    # Unmatched: questions present but no answer entry
    unmatched_questions = sorted([q_num for q_num in question_nums if q_num not in answer_map])

    # Matched count
    matched = len(set(question_nums) & set(answer_nums))

    anomalies: List[str] = []
    if missing_questions:
        anomalies.append(f"Missing questions from 1..{expected_total}: {missing_questions}")
    if missing_answers:
        anomalies.append(f"Missing answers from answer key: {missing_answers}")
    if duplicate_questions:
        anomalies.append(f"Duplicate question numbers encountered: {duplicate_questions}")
    if unmatched_questions:
        anomalies.append(f"Questions without answer key entry: {unmatched_questions}")

    # Inspect question options and content anomalies
    for q in questions:
        q_num = getattr(q, "question_number", None) or (q.get("question_number") if isinstance(q, dict) else None)
        q_type = getattr(q, "question_type", None) or (q.get("question_type") if isinstance(q, dict) else None)
        opts = getattr(q, "options", None) or (q.get("options") if isinstance(q, dict) else [])
        content = getattr(q, "content", None) or (q.get("content") if isinstance(q, dict) else "")

        if not content or len(content.strip()) < 5:
            anomalies.append(f"Q{q_num} has suspiciously short or empty content.")

        if q_type == "MCQ" and len(opts) != 4:
            anomalies.append(f"MCQ Q{q_num} has {len(opts)} options instead of 4.")

    is_valid = (
        len(missing_questions) == 0 and
        len(missing_answers) == 0 and
        len(duplicate_questions) == 0 and
        len(unmatched_questions) == 0 and
        matched == expected_total
    )

    report = {
        "total_questions": len(questions),
        "total_answers": len(answer_map),
        "matched": matched,
        "missing_questions": missing_questions,
        "missing_answers": missing_answers,
        "duplicate_questions": duplicate_questions,
        "duplicate_answers": duplicate_answers,
        "unmatched_questions": unmatched_questions,
        "anomalies": anomalies,
        "is_valid": is_valid
    }

    if is_valid:
        logger.info(f"Paper validation passed successfully: {matched}/{expected_total} questions matched.")
    else:
        logger.warning(f"Paper validation found issues: {len(anomalies)} anomalies recorded.")

    return report

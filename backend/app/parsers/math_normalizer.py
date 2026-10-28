"""
Mathematical Question Normalizer for Qnexus.

Provides deterministic cleaning, HTML entity decoding, Unicode normalization,
promotional noise removal, fraction/option repair, and cross-question equation
leakage resolution while strictly preserving mathematical meaning and notation.
"""

import html
import re
from typing import List, Dict, Any, Tuple, Optional

# Patterns for promotional and extraneous noise in JEE Main paper extracts
PROMOTIONAL_PATTERNS = [
    # MathonGo branding & tags
    r'#PaperPhodnaHai',
    r'https?://[^\s)]+',
    r'www\.mathongo\.com',
    r'mathongo\.com',
    r'MathonGo',
    
    # Test series & app promotions
    r'Join the Most Relevant Test Series[^\n]*',
    r'Download the MathonGo App[^\n]*',
    r'For more such papers[^\n]*',
    r'Telegram channel:[^\n]*',
    
    # Paper headers / watermarks
    r'JEE\s+Main\s+Previous\s+Year\s+Paper',
    r'JEE\s+Main\s+\d{4}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Shift\s*\d+)?',
    r'\d{4}\s*\(\s*\d{1,2}\s+[A-Za-z]+\s+Shift\s*\d+\s*\)',
    r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\((?:Morning|Evening)\s+Shift\)',
    r'\(\s*\d{1,2}\s+[A-Za-z]+\s+Shift\s*\d+\s*\)',
    r'---PAGE_BREAK---',
    r'(?m)^\s*Question\s+Paper\s*$',
    r'(?m)^\s*Answer\s*Keys?\s*$'
]

COMPILED_PROMO_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PROMOTIONAL_PATTERNS]

# Indicators that a tail chunk belongs to the next question's equation/condition
LEAK_INDICATORS = [
    r'^\s*=\s*\d+',
    r'^\s*=\s*0',
    r'^\s*=\s*[αβγa-zA-Z]',
    r'^\s*is\s+equal\s+to\s*[:\.]?',
    r'^\s*is\s*:',
    r'^\s*then\s+',
    r'^\s*where\s+',
    r'^\s*If\s+',
    r'^\s*if\s+',
    r'^\s*(?:dy|dx)\s*=',
    r'^\s*,\s*y\s*∈',
    r'^\s*,\s*x\s*∈',
    r'^\s*,\s*gcd\(',
    r'^\s*,\s*then\b',
    r'^\s*dx\s+',
    r'^\s*dt\s+'
]
COMPILED_LEAK_PATTERNS = [re.compile(p) for p in LEAK_INDICATORS]


def decode_html_and_unicode(text: str) -> str:
    """
    Safely decodes HTML entities (&lt;, &gt;, &le;, &ge;, &minus;, &times;, &nbsp;, etc.)
    and normalizes inconsistent Unicode whitespace while preserving mathematical symbols.
    """
    if not text:
        return ""
    
    # 1. Decode HTML entities
    decoded = html.unescape(text)
    
    # 2. Normalize special Unicode spaces (non-breaking \u00a0, thin space \u2009, etc.) to regular space
    decoded = re.sub(r'[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]', ' ', decoded)
    # Remove zero-width characters (\u200b, \u200c, \u200d, \ufeff)
    decoded = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', decoded)
    
    return decoded


def clean_promotional_noise(text: str) -> str:
    """
    Removes promotional links, URLs, watermarks, test series ads, and exam headers
    without deleting legitimate mathematical notation.
    """
    if not text:
        return ""
    
    result = text
    for pat in COMPILED_PROMO_PATTERNS:
        result = pat.sub('', result)
    
    return result


def normalize_whitespace(text: str) -> str:
    """
    Collapses repeated horizontal spaces while preserving line breaks that distinguish
    matrices, systems of equations, or piecewise definitions.
    """
    if not text:
        return ""
    
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    
    # Collapse multiple consecutive blank lines into at most one blank line
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


def clean_option_content(opt_text: str) -> str:
    """
    Cleans an MCQ option: removes promotional leakage, decodes HTML entities,
    and handles vertically stacked option fractions (e.g. numerator on line 1, denominator on line 2).
    """
    if not opt_text:
        return ""
    
    cleaned = decode_html_and_unicode(opt_text)
    cleaned = clean_promotional_noise(cleaned)
    
    # Remove trailing stray noise tokens like "\n\nn" or "(27 Jan Shift 1)"
    cleaned = re.sub(r'\n+\s*[a-zA-Z]\s*$', '', cleaned)
    cleaned = re.sub(r'\n+\s*y2\s+x2\s*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n+\s*\(\d{1,2}\s+[A-Za-z]+\s+Shift\s*\d+\)\s*$', '', cleaned)
    
    lines = [l.strip() for l in cleaned.split('\n') if l.strip()]
    if len(lines) == 2:
        # Check if line 1 and line 2 form a simple fraction (e.g. "5" and "87" -> "5/87")
        l1, l2 = lines[0], lines[1]
        # Match tokens if both lines are numbers or simple math terms
        toks1 = l1.split()
        toks2 = l2.split()
        if len(toks1) == 1 and len(toks2) == 1 and not any(op in l1 for op in ['=', '<', '>']):
            cleaned = f"{l1}/{l2}"
        elif len(toks1) == len(toks2) and len(toks1) > 1:
            fracs = [f"{t1}/{t2}" for t1, t2 in zip(toks1, toks2)]
            cleaned = " ".join(fracs)
        else:
            cleaned = normalize_whitespace(cleaned)
    else:
        cleaned = normalize_whitespace(cleaned)
    
    return cleaned.strip()


def normalize_math_text(text: str) -> str:
    """
    Full mathematical text normalization:
    1. Decodes HTML entities safely.
    2. Removes promotional noise and advertisement headers.
    3. Normalizes whitespace while preserving line structure for piecewise/multiline math.
    4. Preserves LaTeX notation, superscripts, subscripts, signs, and symbols.
    """
    if not text:
        return ""
    
    # 1. Decode HTML & Unicode spaces
    step1 = decode_html_and_unicode(text)
    
    # 2. Clean promotional noise
    step2 = clean_promotional_noise(step1)
    
    # 3. Clean up broken LaTeX delimiters if any (e.g. \\( -> \(, \\[ -> \[)
    step3 = step2.replace(r'\\(', r'\(').replace(r'\\)', r'\)').replace(r'\\[', r'\[').replace(r'\\]', r'\]')
    
    # 4. Normalize whitespace
    step4 = normalize_whitespace(step3)
    
    return step4


def extract_leaked_tail(text: str) -> Tuple[str, Optional[str]]:
    """
    Inspects the tail of a question's text (or option 4) to detect if an equation
    or condition belonging to the next question was sorted before its header.
    Returns (cleaned_text, leaked_fragment_or_None).
    """
    if not text:
        return text, None
    
    lines = text.strip().split('\n')
    if len(lines) <= 1:
        return text, None
    
    # Check if the last 1 or 2 lines look like a leaked equation/condition
    candidate_lines = []
    split_idx = len(lines)
    
    for i in range(len(lines) - 1, max(0, len(lines) - 3), -1):
        line = lines[i].strip()
        if not line:
            continue
        is_leak = any(pat.search(line) for pat in COMPILED_LEAK_PATTERNS)
        if is_leak:
            candidate_lines.insert(0, line)
            split_idx = i
        else:
            break
            
    if candidate_lines:
        leaked = "\n".join(candidate_lines).strip()
        cleaned = "\n".join(lines[:split_idx]).strip()
        return cleaned, leaked
        
    return text, None


def repair_cross_question_leakage(raw_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolves cross-question equation leakage across a sequence of parsed questions.
    When equation parts for question N+1 are trapped at the tail of question N
    (often in Option 4 or body), this extracts them and prepends them to question N+1.
    """
    if not raw_questions:
        return []
    
    pending_prefix = None
    
    for idx in range(len(raw_questions)):
        q = raw_questions[idx]
        content = q.get("content", "")
        options = q.get("options", [])
        
        # If there's a pending prefix from previous question, attach it
        if pending_prefix:
            # Check if pending_prefix should be appended to the equation or prepended
            # E.g. "Let x = x(y) ... dy" + "= 0. If x(1) = 1, then x(1/2) is :"
            if content and (content.endswith("dy") or content.endswith("dx") or content.endswith("+") or content.endswith("-") or content.endswith("=")):
                q["content"] = f"{content} {pending_prefix}".strip()
            elif pending_prefix.startswith("=") or pending_prefix.startswith("is equal to") or pending_prefix.startswith("is :"):
                q["content"] = f"{content} {pending_prefix}".strip()
            elif pending_prefix.startswith("If") or pending_prefix.startswith("if") or pending_prefix.startswith("Let"):
                q["content"] = f"{pending_prefix} {content}".strip()
            else:
                q["content"] = f"{content} {pending_prefix}".strip()
            pending_prefix = None
            
        # Check Option 4 for leakage
        if options and len(options) >= 4:
            opt4 = options[3]
            opt4_content = opt4.get("content", "") if isinstance(opt4, dict) else getattr(opt4, "content", "")
            
            cleaned_opt4, leaked = extract_leaked_tail(opt4_content)
            if leaked:
                if isinstance(opt4, dict):
                    opt4["content"] = cleaned_opt4
                else:
                    opt4.content = cleaned_opt4
                pending_prefix = leaked
        else:
            # Check body for leakage
            cleaned_body, leaked = extract_leaked_tail(q.get("content", ""))
            if leaked:
                q["content"] = cleaned_body
                pending_prefix = leaked
                
    return raw_questions

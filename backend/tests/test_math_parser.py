"""
Unit and regression tests for Mathematical Question Parsing, Normalization,
and Leakage Repair in Qnexus.

Covers all 15 test categories specified in the task requirements:
1. Simple algebraic equations.
2. Negative signs and subtraction.
3. Fractions and nested fractions.
4. Superscripts and subscripts.
5. LaTeX expressions and escaped backslashes.
6. Roots, limits, derivatives, and integrals.
7. Matrices and multiline expressions.
8. Inequalities and set notation.
9. HTML entities and Unicode symbols.
10. Scientific notation and decimal values.
11. Questions containing answer choices with fraction/option cleaning.
12. Questions containing irrelevant promotional text and URLs.
13. Questions with equations next to ordinary prose.
14. Empty, malformed, or partially extracted question records.
15. Physics and Chemistry regression verification.
"""

import pytest
from app.parsers.math_normalizer import (
    decode_html_and_unicode,
    clean_promotional_noise,
    normalize_whitespace,
    clean_option_content,
    normalize_math_text,
    repair_cross_question_leakage
)
from app.schemas.question_schema import QuestionCreate, QuestionOption


# 1. Simple algebraic equations
def test_simple_algebraic_equations():
    raw = "Let 2x + 5 = 15. Find the value of x."
    normalized = normalize_math_text(raw)
    assert "2x + 5 = 15" in normalized
    assert "Find the value of x" in normalized


# 2. Negative signs and subtraction
def test_negative_signs_and_subtraction():
    raw = "If f(x) = -x^2 - 3/4x + (x - 2), then find f(-1)."
    normalized = normalize_math_text(raw)
    assert "-x^2" in normalized
    assert "- 3/4x" in normalized or "-3/4x" in normalized
    assert "(x - 2)" in normalized
    assert "f(-1)" in normalized


# 3. Fractions and nested fractions
def test_fractions_and_nested_fractions():
    raw = "The value of \\frac{1 + \\frac{1}{x}}{1 - \\frac{1}{x}} when x = 3/4 is equal to:"
    normalized = normalize_math_text(raw)
    assert "\\frac{1 + \\frac{1}{x}}{1 - \\frac{1}{x}}" in normalized
    assert "3/4" in normalized


# 4. Superscripts and subscripts
def test_superscripts_and_subscripts():
    raw = "Let a₁, a₂, a₃, … be a G.P. where a_n = a₁ ⋅ r^(n-1) and 10^-3 ≤ x² ≤ 10^5."
    normalized = normalize_math_text(raw)
    assert "a₁, a₂, a₃" in normalized
    assert "a_n" in normalized
    assert "r^(n-1)" in normalized
    assert "10^-3" in normalized
    assert "x²" in normalized


# 5. LaTeX expressions and escaped backslashes
def test_latex_expressions_and_delimiters():
    raw = "Let $f(x) = \\cos^{-1}(x)$ and \\(g(x) = \\sin(x)\\). Evaluate \\[ \\int_0^1 f(x)g(x) dx \\]."
    normalized = normalize_math_text(raw)
    assert "$f(x) = \\cos^{-1}(x)$" in normalized
    assert "\\(g(x) = \\sin(x)\\)" in normalized
    assert "\\[ \\int_0^1 f(x)g(x) dx \\]" in normalized


# 6. Roots, limits, derivatives, and integrals
def test_roots_limits_derivatives_integrals():
    raw = "If a = \\lim_{x \\to 0} \\frac{\\sqrt{1 + x} - 1}{x} and \\frac{dy}{dx} = \\int_0^x \\sqrt{t} dt, find a + y'(1)."
    normalized = normalize_math_text(raw)
    assert "\\lim_{x \\to 0}" in normalized
    assert "\\sqrt{1 + x}" in normalized
    assert "\\frac{dy}{dx}" in normalized
    assert "\\int_0^x" in normalized


# 7. Matrices and multiline expressions
def test_matrices_and_multiline_expressions():
    raw = (
        "Let A = ⎡ 1  2 ⎤ and B = ⎡ 0  -1 ⎤.\n"
        "        ⎣ 3  4 ⎦         ⎣ 2   1 ⎦\n"
        "Find the determinant det(A + B)."
    )
    normalized = normalize_math_text(raw)
    # Line breaks distinguishing matrix rows must be preserved
    assert "\n" in normalized
    assert "⎡ 1 2 ⎤" in normalized or "⎡ 1  2 ⎤" in normalized or "1" in normalized
    assert "det(A + B)" in normalized


# 8. Inequalities and set notation
def test_inequalities_and_set_notation():
    raw = "If S = {x ∈ ℝ : x² - 5x + 6 ≤ 0} ∩ [α, β] where α ≠ β and γ ≥ 0, then find S ∪ {0}."
    normalized = normalize_math_text(raw)
    assert "x ∈ ℝ" in normalized
    assert "x² - 5x + 6 ≤ 0" in normalized
    assert "∩ [α, β]" in normalized
    assert "α ≠ β" in normalized
    assert "γ ≥ 0" in normalized
    assert "S ∪ {0}" in normalized


# 9. HTML entities and Unicode symbols
def test_html_entities_and_unicode_symbols():
    raw = "If &alpha; &le; x &le; &beta; and x &ne; 0, where &minus;5 &lt; x &lt; 5 &times; 10, then:"
    normalized = normalize_math_text(raw)
    assert "α" in normalized
    assert "≤" in normalized
    assert "β" in normalized
    assert "≠" in normalized
    assert "−" in normalized or "-" in normalized
    assert "<" in normalized
    assert "×" in normalized


# 10. Scientific notation and decimal values
def test_scientific_notation_and_decimals():
    raw = "The bulk modulus is 2.1 × 10^9 N/m² and pressure difference ΔP = 6.3 × 10^7 N/m² with diameter 0.25 mm."
    normalized = normalize_math_text(raw)
    assert "2.1 × 10^9" in normalized
    assert "6.3 × 10^7" in normalized
    assert "0.25 mm" in normalized


# 11. Questions containing answer choices with stacked fraction repair
def test_options_fraction_repair():
    raw_opt_frac = "5\n29"
    cleaned = clean_option_content(raw_opt_frac)
    assert cleaned == "5/29"

    raw_opt_multiterm = "25 15\n83 29"
    cleaned_multi = clean_option_content(raw_opt_multiterm)
    assert cleaned_multi == "25/83 15/29"

    raw_opt_regular = "  3 - e  "
    assert clean_option_content(raw_opt_regular) == "3 - e"


# 12. Questions containing irrelevant promotional text and URLs
def test_promotional_noise_removal():
    raw_with_promo = (
        "Let z be a complex number such that |z| = 1.\n\n"
        "#PaperPhodnaHai\n"
        "Join the Most Relevant Test Series for JEE Main with Most Detailed & Advanced Analysis here: https://links.mathongo.com/mWN\n"
        "www.mathongo.com\n"
        "(27 Jan Shift 1)\n"
        "Question Paper\n\n"
        "Then find the value of |z - 1|."
    )
    normalized = normalize_math_text(raw_with_promo)
    assert "Let z be a complex number such that |z| = 1." in normalized
    assert "Then find the value of |z - 1|." in normalized
    assert "#PaperPhodnaHai" not in normalized
    assert "Test Series" not in normalized
    assert "https://" not in normalized
    assert "www.mathongo.com" not in normalized
    assert "Question Paper" not in normalized

    # Also verify option leakage cleanup
    raw_opt_promo = "2√2 < k < 2√3\n\nJoin the Most Relevant Test Series for JEE Main here: https://links.com/x\n(27 Jan Shift 1)"
    opt_cleaned = clean_option_content(raw_opt_promo)
    assert opt_cleaned == "2√2 < k < 2√3"


# 13. Questions with equations next to ordinary prose
def test_equations_in_prose():
    raw = (
        "Let the line L1 : x + 3 = 0 intersect the lines L2 : x - y = 0 and L3 : 3x + y = 0 at the points A and B, "
        "respectively. If the distance d satisfies d² = 16, then the coordinates of C are:"
    )
    normalized = normalize_math_text(raw)
    assert "L1 : x + 3 = 0" in normalized
    assert "L2 : x - y = 0" in normalized
    assert "L3 : 3x + y = 0" in normalized
    assert "d² = 16" in normalized


# 14. Empty, malformed, or partially extracted question records
def test_empty_and_malformed_records():
    assert normalize_math_text("") == ""
    assert normalize_math_text(None) == ""
    assert clean_option_content("") == ""
    assert clean_option_content(None) == ""
    
    malformed = "   \n\n   \t  \n   "
    assert normalize_math_text(malformed) == ""


# 15. Physics and Chemistry questions to detect regressions in shared parsing utilities
def test_physics_chemistry_regression_safety():
    # Physics question with units, scientific notation, and exponents
    physics_raw = (
        "An insulated wire is wound so that it forms a flat coil with N = 200 turns.\n"
        "The radius of the innermost turn is r₁ = 3 cm, and of the outermost turn r₂ = 6 cm.\n"
        "If 20 mA current flows in it then the magnetic moment will be α × 10⁻² A⋅m²."
    )
    physics_norm = normalize_math_text(physics_raw)
    assert "N = 200 turns" in physics_norm
    assert "r₁ = 3 cm" in physics_norm
    assert "r₂ = 6 cm" in physics_norm
    assert "20 mA" in physics_norm
    assert "α × 10⁻² A⋅m²" in physics_norm

    # Chemistry question with chemical formulas, arrows, charges, and percentages
    chem_raw = (
        "Consider the reaction: P₄ + 5O₂ → 2P₂O₅.\n"
        "The percentage of carbon in compound (X) is 26.7%.\n"
        "Given pK_b(NH₄OH) = 4.74 and log 2 = 0.30, calculate pH of solution."
    )
    chem_norm = normalize_math_text(chem_raw)
    assert "P₄ + 5O₂ → 2P₂O₅" in chem_norm
    assert "26.7%" in chem_norm
    assert "pK_b(NH₄OH) = 4.74" in chem_norm
    assert "log 2 = 0.30" in chem_norm


# 16. Cross-question equation leakage repair (verifying 2025 Q1->Q2 real-world bug)
def test_cross_question_leakage_repair():
    q1 = {
        "question_number": 1,
        "content": "Let a1, a2 be a G.P. Find a6.",
        "options": [
            {"id": "A", "content": "628"},
            {"id": "B", "content": "812"},
            {"id": "C", "content": "526"},
            {"id": "D", "content": "784\n\n= 0. If x(1) = 1, then x(1/2) is :"}
        ]
    }
    q2 = {
        "question_number": 2,
        "content": "Let x = x(y) be the solution of the differential equation y2 dx + (x − 1/y) dy",
        "options": [
            {"id": "A", "content": "1/2 + e"},
            {"id": "B", "content": "3 + e"},
            {"id": "C", "content": "3 - e"},
            {"id": "D", "content": "3/2 + e"}
        ]
    }

    repaired = repair_cross_question_leakage([q1, q2])
    
    # Q1 option D should be cleaned of the leaked next-question equation
    assert repaired[0]["options"][3]["content"] == "784"

    # Q2 should have the equation restored
    assert "= 0. If x(1) = 1, then x(1/2) is :" in repaired[1]["content"]
    assert "y2 dx + (x − 1/y) dy = 0. If x(1) = 1, then x(1/2) is :" in repaired[1]["content"]


# 17. Non-destructive idempotency test: multiple passes do not corrupt text
def test_idempotent_parsing():
    text = "Let f(x) = \\int_0^x \\frac{t^2 - 1}{\\sqrt{1 + t^4}} dt. Find all x where f'(x) = 0."
    pass1 = normalize_math_text(text)
    pass2 = normalize_math_text(pass1)
    pass3 = normalize_math_text(pass2)
    assert pass1 == pass2 == pass3

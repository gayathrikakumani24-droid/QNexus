import sys
import os

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

errors = []

def run_test(name, func):
    try:
        func()
        print(f"  PASS: {name}")
    except Exception as e:
        print(f"  FAIL: {name}: {e}")
        errors.append((name, e))

print("=== Running Pinecone Unit Tests ===")

# 1. test_pinecone_service
print("\n[test_pinecone_service]")
from tests.test_pinecone_service import (
    test_question_id_to_point_id,
    test_sanitize_metadata_removes_none,
    test_vector_repository_upsert_records,
    test_pinecone_service_sync_skips_already_indexed
)
run_test("test_question_id_to_point_id", test_question_id_to_point_id)
run_test("test_sanitize_metadata_removes_none", test_sanitize_metadata_removes_none)
run_test("test_vector_repository_upsert_records", test_vector_repository_upsert_records)
run_test("test_pinecone_service_sync_skips_already_indexed", test_pinecone_service_sync_skips_already_indexed)

# 2. test_qdrant_service (backward compatibility wrapper)
print("\n[test_qdrant_service (backward compatibility)]")
from tests.test_qdrant_service import test_qdrant_service_sync_skips_already_indexed as test_legacy_sync
run_test("test_qdrant_service_sync_skips_already_indexed", test_legacy_sync)

# 3. test_search_service
print("\n[test_search_service]")
from tests.test_search_service import (
    test_search_service_pipeline_success,
    test_search_service_empty_results,
    test_search_service_build_filter_conditions
)
run_test("test_search_service_pipeline_success", test_search_service_pipeline_success)
run_test("test_search_service_empty_results", test_search_service_empty_results)
run_test("test_search_service_build_filter_conditions", test_search_service_build_filter_conditions)

# 4. test_recommendation_service
print("\n[test_recommendation_service]")
from tests.test_recommendation_service import (
    test_recommendations_based_on_weak_concepts,
    test_recommendations_cold_start_fallback
)
run_test("test_recommendations_based_on_weak_concepts", test_recommendations_based_on_weak_concepts)
run_test("test_recommendations_cold_start_fallback", test_recommendations_cold_start_fallback)

# 5. test_ai_service
print("\n[test_ai_service]")
from tests.test_ai_service import test_get_similar_questions_excludes_target
run_test("test_get_similar_questions_excludes_target", test_get_similar_questions_excludes_target)

# 6. test_math_parser
print("\n[test_math_parser]")
from tests.test_math_parser import (
    test_simple_algebraic_equations,
    test_negative_signs_and_subtraction,
    test_fractions_and_nested_fractions,
    test_superscripts_and_subscripts,
    test_latex_expressions_and_delimiters,
    test_roots_limits_derivatives_integrals,
    test_matrices_and_multiline_expressions,
    test_inequalities_and_set_notation,
    test_html_entities_and_unicode_symbols,
    test_scientific_notation_and_decimals,
    test_options_fraction_repair,
    test_promotional_noise_removal,
    test_equations_in_prose,
    test_empty_and_malformed_records,
    test_physics_chemistry_regression_safety,
    test_cross_question_leakage_repair,
    test_idempotent_parsing
)
run_test("test_simple_algebraic_equations", test_simple_algebraic_equations)
run_test("test_negative_signs_and_subtraction", test_negative_signs_and_subtraction)
run_test("test_fractions_and_nested_fractions", test_fractions_and_nested_fractions)
run_test("test_superscripts_and_subscripts", test_superscripts_and_subscripts)
run_test("test_latex_expressions_and_delimiters", test_latex_expressions_and_delimiters)
run_test("test_roots_limits_derivatives_integrals", test_roots_limits_derivatives_integrals)
run_test("test_matrices_and_multiline_expressions", test_matrices_and_multiline_expressions)
run_test("test_inequalities_and_set_notation", test_inequalities_and_set_notation)
run_test("test_html_entities_and_unicode_symbols", test_html_entities_and_unicode_symbols)
run_test("test_scientific_notation_and_decimals", test_scientific_notation_and_decimals)
run_test("test_options_fraction_repair", test_options_fraction_repair)
run_test("test_promotional_noise_removal", test_promotional_noise_removal)
run_test("test_equations_in_prose", test_equations_in_prose)
run_test("test_empty_and_malformed_records", test_empty_and_malformed_records)
run_test("test_physics_chemistry_regression_safety", test_physics_chemistry_regression_safety)
run_test("test_cross_question_leakage_repair", test_cross_question_leakage_repair)
run_test("test_idempotent_parsing", test_idempotent_parsing)

print("\n" + "=" * 40)
if errors:
    print(f"FAILED: {len(errors)} tests failed.")
    sys.exit(1)
else:
    print("ALL TESTS PASSED SUCCESSFULLY!")
    sys.exit(0)

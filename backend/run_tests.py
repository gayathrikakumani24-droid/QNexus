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

print("\n" + "=" * 40)
if errors:
    print(f"FAILED: {len(errors)} tests failed.")
    sys.exit(1)
else:
    print("ALL TESTS PASSED SUCCESSFULLY!")
    sys.exit(0)

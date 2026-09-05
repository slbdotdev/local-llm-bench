import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from releaseplan import build_plan, plan_records
from support import merged_catalog, merged_history, text


CATALOG = merged_catalog()
LOCK = text("lock.json")
POLICY = text("policy.json")
HISTORY = merged_history()


class PlanTests(unittest.TestCase):
    def test_transitive_dependencies_are_dependency_first(self):
        names = plan_records(CATALOG, LOCK, POLICY, HISTORY,
                             "pkg-012", "linux", "2025-03")
        self.assertEqual(names, ["pkg-001", "pkg-002", "pkg-003", "pkg-004",
                                 "pkg-005", "pkg-006", "pkg-007", "pkg-008",
                                 "pkg-009", "pkg-010", "pkg-011", "pkg-012"])

    def test_render_contains_pinned_versions(self):
        output = build_plan(CATALOG, LOCK, POLICY, HISTORY,
                            "pkg-006", "linux", "2025-03")
        self.assertTrue(output.startswith("release=2025-03 platform=linux\ntarget=pkg-006\n"))
        self.assertIn("- pkg-006@2.0.6 requires=pkg-005\n", output)

    def test_platform_specific_availability(self):
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "pkg-017", "windows", "2025-03"), [])
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "pkg-017", "linux", "2026-01"),
                         ["pkg-001", "pkg-002", "pkg-003", "pkg-004", "pkg-005",
                          "pkg-006", "pkg-007", "pkg-008", "pkg-009", "pkg-010",
                          "pkg-011", "pkg-012", "pkg-013", "pkg-014", "pkg-015",
                          "pkg-016", "pkg-017"])

    def test_newest_policy_revision_wins(self):
        # The broad deny is older than the exact windows allow.
        self.assertNotEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                         "pkg-019", "windows", "2025-06"), [])
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "pkg-019", "linux", "2025-06"), [])

    def test_policy_window_is_half_open(self):
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "pkg-044", "linux", "2026-01"),
                         ["pkg-001", "pkg-002", "pkg-003", "pkg-004",
                          "pkg-005", "pkg-006", "pkg-007", "pkg-008",
                          "pkg-009", "pkg-010", "pkg-011", "pkg-012", "pkg-013",
                          "pkg-014", "pkg-015", "pkg-016", "pkg-017", "pkg-018",
                          "pkg-019", "pkg-020", "pkg-021", "pkg-022", "pkg-023",
                          "pkg-024", "pkg-025", "pkg-026", "pkg-027", "pkg-028",
                          "pkg-029", "pkg-030", "pkg-031", "pkg-032", "pkg-033",
                          "pkg-034", "pkg-035", "pkg-036", "pkg-037", "pkg-038",
                          "pkg-039", "pkg-040", "pkg-041", "pkg-042", "pkg-043",
                          "pkg-044"])

    def test_historical_names_resolve(self):
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "historical-2019-01", "linux", "2025-03")[-1], "pkg-004")
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "pkg-legacy-core", "linux", "2025-03")[-1], "pkg-004")
        self.assertEqual(plan_records(CATALOG, LOCK, POLICY, HISTORY,
                                      "legacy-root", "linux", "2028-01")[-1], "pkg-120")

    def test_missing_or_blocked_dependency_is_empty(self):
        policy = '[{"package":"pkg-005","platform":"*","effect":"deny","start":"0000-00","end":"9999-99","revision":99}]'
        self.assertEqual(plan_records(CATALOG, LOCK, policy, HISTORY,
                                      "pkg-006", "linux", "2025-03"), [])

    def test_complete_catalog_is_loaded_across_all_shards(self):
        names = plan_records(CATALOG, LOCK, POLICY, HISTORY,
                             "pkg-280", "linux", "2028-01")
        self.assertEqual(len(names), 280)
        self.assertEqual(names[0], "pkg-001")
        self.assertEqual(names[-1], "pkg-280")


if __name__ == "__main__":
    unittest.main()

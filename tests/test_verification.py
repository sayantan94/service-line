import tempfile
import unittest
from pathlib import Path

from service_line.verification import guide
from service_line.verification.evidence import evaluate

GUIDE = """# App, verification

## Required commands

| ID | Command | Expected result |
|---|---|---|
| CHECK-001 | `python3 -m unittest -q` | all pass |
| CHECK-002 | `<build command>` | builds |

High-risk paths: `db/migrations/`, billing

## Evidence bundle
"""
OK = {"revision": "abc", "results": [{"id": "CHECK-001", "exit_code": 0, "timed_out": False}]}
REVIEW = {"revision": "abc", "verdict": "passed"}
APPROVAL = {"plan": 1, "decision": "approved"}


class GuideTests(unittest.TestCase):
    def test_commands_are_read_from_the_table_and_template_rows_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "g.md"
            path.write_text(GUIDE)
            g = guide.load(path)
        self.assertEqual([(c.id, c.command) for c in g.checks], [("CHECK-001", "python3 -m unittest -q")])
        self.assertEqual(g.high_paths, ["db/migrations/", "billing"])
        self.assertEqual(len(g.version), 12)

    def test_a_missing_guide_has_no_version_and_no_checks(self):
        g = guide.load(Path("/nonexistent/guide.md"))
        self.assertEqual((g.version, g.checks), (None, []))


class Gate(unittest.TestCase):
    def test_everything_passing_on_the_current_revision_passes(self):
        self.assertEqual(evaluate(OK, REVIEW, "abc", 1, APPROVAL)["verdict"], "passed")

    def test_a_failed_check_fails(self):
        bad = {"revision": "abc", "results": [{"id": "CHECK-001", "exit_code": 1, "timed_out": False}]}
        self.assertEqual(evaluate(bad, REVIEW, "abc", 1, APPROVAL)["verdict"], "failed")

    def test_a_failed_review_fails(self):
        self.assertEqual(evaluate(OK, {"revision": "abc", "verdict": "failed"}, "abc", 1, APPROVAL)["verdict"], "failed")

    def test_no_checks_is_inconclusive_not_a_pass(self):
        self.assertEqual(evaluate({"revision": "abc", "results": []}, REVIEW, "abc", 1, APPROVAL)["verdict"], "inconclusive")

    def test_a_check_that_timed_out_is_inconclusive(self):
        slow = {"revision": "abc", "results": [{"id": "CHECK-001", "exit_code": None, "timed_out": True}]}
        self.assertEqual(evaluate(slow, REVIEW, "abc", 1, APPROVAL)["verdict"], "inconclusive")

    def test_evidence_from_an_older_revision_is_inconclusive(self):
        self.assertEqual(evaluate(OK, REVIEW, "newer", 1, APPROVAL)["verdict"], "inconclusive")

    def test_a_missing_or_unclear_review_is_inconclusive(self):
        self.assertEqual(evaluate(OK, None, "abc", 1, APPROVAL)["verdict"], "inconclusive")
        self.assertEqual(evaluate(OK, {"revision": "abc", "verdict": "inconclusive"}, "abc", 1, APPROVAL)["verdict"], "inconclusive")

    def test_missing_evidence_outranks_a_failure(self):
        bad = {"revision": "abc", "results": [{"id": "CHECK-001", "exit_code": 1, "timed_out": False}]}
        self.assertEqual(evaluate(bad, None, "abc", 1, APPROVAL)["verdict"], "inconclusive")

    def test_an_approval_of_a_different_plan_is_inconclusive(self):
        self.assertEqual(evaluate(OK, REVIEW, "abc", 2, APPROVAL)["verdict"], "inconclusive")
        self.assertEqual(evaluate(OK, REVIEW, "abc", 1, None)["verdict"], "inconclusive")


if __name__ == "__main__":
    unittest.main()

import copy
import json
import unittest
from pathlib import Path

from service_line.engine import asl
from service_line.engine.validate import WorkflowInvalid, validate

DEFINITION = json.loads((Path(__file__).parent.parent / "workflows" / "software-change.asl.json").read_text())


class Paths(unittest.TestCase):
    def test_reading_a_path(self):
        ctx = {"approval": {"decision": "approved"}, "repairs": 1}
        self.assertEqual(asl.get_path(ctx, "$.approval.decision"), "approved")
        self.assertEqual(asl.get_path(ctx, "$"), ctx)
        self.assertIsNone(asl.get_path(ctx, "$.missing.deeper"))

    def test_writing_a_path_returns_a_new_context(self):
        ctx = {"repairs": 0}
        out = asl.set_path(ctx, "$.plan", {"risk": "low"})
        self.assertEqual(out, {"repairs": 0, "plan": {"risk": "low"}})
        self.assertEqual(ctx, {"repairs": 0})
        self.assertEqual(asl.set_path(ctx, "$", {"repairs": 1}), {"repairs": 1})


class Choices(unittest.TestCase):
    def setUp(self):
        self.route = DEFINITION["States"]["Route"]

    def test_passed_goes_to_ready(self):
        self.assertEqual(asl.choose(self.route, {"verification": {"verdict": "passed"}, "repairs": 0}), "Ready")

    def test_failed_with_repairs_left_goes_to_repair(self):
        self.assertEqual(asl.choose(self.route, {"verification": {"verdict": "failed"}, "repairs": 1}), "Repair")

    def test_failed_at_the_repair_limit_needs_attention(self):
        self.assertEqual(asl.choose(self.route, {"verification": {"verdict": "failed"}, "repairs": 2}), "NeedsAttention")

    def test_anything_else_takes_the_default(self):
        self.assertEqual(asl.choose(self.route, {"verification": {"verdict": "inconclusive"}, "repairs": 0}), "NeedsAttention")


class Validation(unittest.TestCase):
    def test_the_shipped_workflows_are_valid(self):
        validate(DEFINITION)
        observe = json.loads((Path(__file__).parent.parent / "workflows" / "post-deploy-observe.asl.json").read_text())
        validate(observe)

    def broken(self, change):
        definition = copy.deepcopy(DEFINITION)
        change(definition["States"], definition)
        with self.assertRaises(WorkflowInvalid) as caught:
            validate(definition)
        return str(caught.exception)

    def test_a_next_that_names_no_state_is_rejected(self):
        self.assertIn("Nowhere", self.broken(lambda s, d: s["Plan"].update(Next="Nowhere")))

    def test_an_unknown_action_is_rejected(self):
        self.assertIn("service-line:agent.improvise", self.broken(lambda s, d: s["Plan"].update(Resource="service-line:agent.improvise")))

    def test_a_path_to_implementation_that_skips_approval_is_rejected(self):
        self.assertIn("approval", self.broken(lambda s, d: s["ReviewPlan"].update(Next="Implement")))

    def test_a_loop_with_no_limit_is_rejected(self):
        def unbounded(states, definition):
            states["Route"]["Choices"][1] = {"Variable": "$.verification.verdict", "StringEquals": "failed", "Next": "Repair"}
        self.assertIn("loop", self.broken(unbounded))

    def test_a_state_that_cannot_reach_an_end_is_rejected(self):
        def trap(states, definition):
            states["Ready"] = {"Type": "Pass", "Next": "Ready"}
        message = self.broken(trap)
        self.assertTrue("loop" in message or "end" in message)

    def test_a_missing_start_is_rejected(self):
        self.assertIn("StartAt", self.broken(lambda s, d: d.update(StartAt="Begin")))


if __name__ == "__main__":
    unittest.main()

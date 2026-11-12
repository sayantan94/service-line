import tempfile
import unittest
from pathlib import Path

from service_line.store.instances import Home, InstanceExists
from service_line.store.workitems import NotApproved


class Store(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Home(Path(self.tmp.name) / "instances")
        self.inst = self.home.add("AppliedIn", repo="/workspace/AppliedIn", implementer="Codex")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_service_is_found_again_by_its_id(self):
        again = self.home.get("appliedin")
        self.assertEqual((again.name, again.repo, again.implementer), ("AppliedIn", "/workspace/AppliedIn", "Codex"))
        self.assertEqual([i.id for i in self.home.all()], ["appliedin"])

    def test_adding_the_same_service_twice_is_refused(self):
        with self.assertRaises(InstanceExists):
            self.home.add("AppliedIn", repo="/x", implementer="Codex")

    def test_work_items_are_numbered_in_order(self):
        a = self.inst.new_item("Fix retries", "Bug", "No duplicates", ["Never retried twice"])
        b = self.inst.new_item("Add page", "Feature", "A page", ["It renders"])
        self.assertEqual((a.id, b.id), ("WI-001", "WI-002"))
        self.assertEqual([w.id for w in self.inst.items()], ["WI-001", "WI-002"])

    def test_the_verifier_is_always_the_other_executor(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        self.assertEqual((w.implementer, w.verifier), ("Codex", "Claude"))
        w2 = self.inst.new_item("Fix", "Bug", "x", ["y"], implementer="Claude")
        self.assertEqual(w2.verifier, "Codex")

    def test_plans_are_versioned_and_the_latest_is_current(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        self.assertIsNone(w.plan())
        w.save_plan("first", risk="low", phases=["a"])
        w.save_plan("second", risk="high", phases=["a", "b"])
        p = w.plan()
        self.assertEqual((p["version"], p["risk"], p["text"], p["phases"]), (2, "high", "second", ["a", "b"]))

    def test_an_approval_binds_the_current_plan_and_its_risk(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        w.save_plan("first", risk="medium", phases=["a"])
        self.assertIsNone(w.approval())
        w.decide("approved", guide_version="abc")
        a = w.approval()
        self.assertEqual((a["decision"], a["plan"], a["risk"], a["guide"]), ("approved", 1, "medium", "abc"))

    def test_an_approval_of_an_older_plan_does_not_count(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        w.save_plan("first", risk="low", phases=["a"])
        w.decide("approved")
        w.save_plan("second", risk="low", phases=["a"])
        self.assertIsNone(w.approval())

    def test_deciding_without_a_plan_is_refused(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        with self.assertRaises(NotApproved):
            w.decide("approved")

    def test_runs_are_numbered_and_the_latest_is_found(self):
        w = self.inst.new_item("Fix", "Bug", "x", ["y"])
        self.assertIsNone(w.latest_run())
        self.assertEqual(w.new_run_dir().name, "run-001")
        (w.dir / "runs" / "run-001").mkdir(parents=True)
        self.assertEqual(w.new_run_dir().name, "run-002")
        self.assertEqual(w.latest_run().name, "run-001")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from service_line.store.events import RunLog, close_open, fork


class Recovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "run-001"
        self.log = RunLog.create(self.dir, run_id="run-001", clock=lambda: 7)

    def tearDown(self):
        self.log.close()
        self.tmp.cleanup()

    def test_nothing_open_means_nothing_to_close(self):
        s = self.log.start("state", name="Plan")
        self.log.end("state", s, "completed")
        self.assertEqual(close_open(self.log), {"outcome": "closed", "state": None})

    def test_an_open_state_with_no_side_effect_is_safe_to_rerun(self):
        self.log.start("state", name="Plan")
        self.assertEqual(close_open(self.log), {"outcome": "not-started", "state": "Plan"})
        last = self.log.events[-1]
        self.assertEqual((last["type"], last["data"]["reason"]), ("state/end", "interrupted"))

    def test_a_side_effect_that_started_and_never_ended_has_an_unknown_outcome(self):
        self.log.start("state", name="Implement")
        self.log.start("call", executor="Codex")
        self.assertEqual(close_open(self.log), {"outcome": "unknown", "state": "Implement"})
        types = [e["type"] for e in self.log.events[-2:]]
        self.assertEqual(types, ["call/end", "state/end"])

    def test_side_effects_that_all_ended_are_reported_as_finished(self):
        self.log.start("state", name="RunChecks")
        c = self.log.start("check", command="true")
        self.log.end("check", c, "completed")
        self.assertEqual(close_open(self.log), {"outcome": "effects-finished", "state": "RunChecks"})

    def test_closing_twice_changes_nothing_the_second_time(self):
        self.log.start("state", name="Plan")
        close_open(self.log)
        count = len(self.log.events)
        self.assertEqual(close_open(self.log)["outcome"], "closed")
        self.assertEqual(len(self.log.events), count)

    def test_an_end_names_the_start_it_closes(self):
        s = self.log.start("state", name="Plan")
        e = self.log.end("state", s, "completed", next="ReviewPlan")
        self.assertEqual((e["data"]["start"], e["data"]["next"]), (s, "ReviewPlan"))

    def test_a_fork_copies_the_events_up_to_a_point_and_closes_what_was_open(self):
        self.log.start("state", name="Plan")
        self.log.start("call", executor="Codex")
        self.log.append("note", {"n": 1})
        child = fork(self.log, Path(self.tmp.name) / "run-002", run_id="run-002", upto=1)
        try:
            types = [e["type"] for e in child.events]
            self.assertEqual(types, ["state/start", "call/start", "run/forked", "call/end", "state/end"])
            self.assertEqual(child.events[2]["data"], {"from": "run-001", "inherited": 2})
            self.assertEqual([e["seq"] for e in child.events], [0, 1, 2, 3, 4])
        finally:
            child.close()


if __name__ == "__main__":
    unittest.main()

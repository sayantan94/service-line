import json
import tempfile
import unittest
from pathlib import Path

from service_line.store.events import LogExists, RunLocked, RunLog


class RunLogBasics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "run-001"

    def tearDown(self):
        self.tmp.cleanup()

    def test_append_numbers_events_from_zero_without_gaps(self):
        with RunLog.create(self.dir, run_id="run-001") as log:
            first = log.append("step/start", {"step": "Plan"})
            second = log.append("step/end", {"step": "Plan", "reason": "completed"})
        self.assertEqual([first["seq"], second["seq"]], [0, 1])

    def test_events_survive_closing_and_reopening(self):
        with RunLog.create(self.dir, run_id="run-001") as log:
            log.append("step/start", {"step": "Plan"})
        with RunLog.open(self.dir) as log:
            self.assertEqual(log.run_id, "run-001")
            self.assertEqual([e["type"] for e in log.events], ["step/start"])
            self.assertEqual(log.events[0]["data"], {"step": "Plan"})

    def test_append_after_reopen_continues_the_sequence(self):
        with RunLog.create(self.dir, run_id="run-001") as log:
            log.append("step/start", {"step": "Plan"})
        with RunLog.open(self.dir) as log:
            event = log.append("step/end", {"step": "Plan", "reason": "completed"})
        self.assertEqual(event["seq"], 1)

    def test_file_is_one_json_object_per_line_with_a_header_first(self):
        with RunLog.create(self.dir, run_id="run-001") as log:
            log.append("step/start", {"step": "Plan"})
        lines = (self.dir / "events.jsonl").read_text().splitlines()
        header, event = (json.loads(line) for line in lines)
        self.assertEqual((header["type"], header["version"], header["id"]), ("run", 1, "run-001"))
        self.assertEqual((event["seq"], event["type"]), (0, "step/start"))

    def test_creating_a_log_that_already_exists_is_refused(self):
        RunLog.create(self.dir, run_id="run-001").close()
        with self.assertRaises(LogExists):
            RunLog.create(self.dir, run_id="run-001")

    def test_a_second_writer_on_the_same_run_is_refused(self):
        with RunLog.create(self.dir, run_id="run-001"):
            with self.assertRaises(RunLocked):
                RunLog.open(self.dir)

    def test_the_lock_is_released_on_close(self):
        RunLog.create(self.dir, run_id="run-001").close()
        with RunLog.open(self.dir) as log:
            self.assertEqual(log.events, [])

    def test_data_that_is_not_json_is_rejected_and_nothing_is_written(self):
        with RunLog.create(self.dir, run_id="run-001") as log:
            with self.assertRaises(TypeError):
                log.append("step/start", {"bad": object()})
            self.assertEqual(log.events, [])
        with RunLog.open(self.dir) as log:
            self.assertEqual(log.events, [])


if __name__ == "__main__":
    unittest.main()

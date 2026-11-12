import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from service_line.store.events import LogCorrupt, RunLog


class RunLogDamage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "run-001"
        with RunLog.create(self.dir, run_id="run-001") as log:
            log.append("step/start", {"step": "Plan"})
        self.file = self.dir / "events.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_last_line_cut_off_mid_write_is_ignored(self):
        with open(self.file, "ab") as f:
            f.write(b'{"seq":1,"time":5,"type":"step/e')
        with RunLog.open(self.dir) as log:
            self.assertEqual([e["seq"] for e in log.events], [0])

    def test_the_cut_off_line_is_removed_before_the_next_event_is_written(self):
        with open(self.file, "ab") as f:
            f.write(b'{"seq":1,"time":5,"type":"step/e')
        with RunLog.open(self.dir) as log:
            log.append("step/end", {"step": "Plan", "reason": "interrupted"})
        with RunLog.open(self.dir) as log:
            self.assertEqual([(e["seq"], e["type"]) for e in log.events],
                             [(0, "step/start"), (1, "step/end")])

    def test_a_damaged_line_followed_by_good_lines_is_an_error(self):
        good = self.file.read_bytes()
        self.file.write_bytes(good + b"not json\n" + b'{"seq":2,"time":5,"type":"step/end","data":{}}\n')
        with self.assertRaises(LogCorrupt):
            RunLog.open(self.dir)

    def test_a_gap_in_the_numbering_is_an_error(self):
        with open(self.file, "ab") as f:
            f.write(b'{"seq":5,"time":5,"type":"step/end","data":{}}\n')
        with self.assertRaises(LogCorrupt):
            RunLog.open(self.dir)

    def test_a_failed_refusal_releases_the_lock(self):
        with open(self.file, "ab") as f:
            f.write(b'{"seq":5,"time":5,"type":"step/end","data":{}}\n')
        with self.assertRaises(LogCorrupt):
            RunLog.open(self.dir)
        with self.assertRaises(LogCorrupt):
            RunLog.open(self.dir)  # LogCorrupt again, not RunLocked

    def test_a_write_that_fails_to_sync_leaves_no_partial_event(self):
        before = self.file.read_bytes()
        real_fsync = os.fsync
        calls = {"n": 0}

        def failing_once(fd):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("disk full")
            return real_fsync(fd)

        with RunLog.open(self.dir) as log:
            with mock.patch("os.fsync", failing_once):
                with self.assertRaises(OSError):
                    log.append("step/end", {"step": "Plan", "reason": "completed"})
            self.assertEqual(len(log.events), 1)
            self.assertEqual(self.file.read_bytes(), before)
            event = log.append("step/end", {"step": "Plan", "reason": "completed"})
            self.assertEqual(event["seq"], 1)


if __name__ == "__main__":
    unittest.main()

import json
import sys
import tempfile
import unittest
from pathlib import Path

from service_line.executors import claude, codex
from service_line.executors.base import AgentResult, run_streaming
from service_line.executors.guards import RepeatDetector


class Guards(unittest.TestCase):
    def test_the_same_call_repeated_reaches_remind_then_stop(self):
        d = RepeatDetector(thresholds=(3, 5))
        seen = [d.observe("Bash", {"command": "ls"}) for _ in range(5)]
        self.assertEqual(seen, [None, None, "remind", None, "stop"])

    def test_argument_order_does_not_matter(self):
        d = RepeatDetector(thresholds=(2,))
        d.observe("Read", {"a": 1, "b": 2})
        self.assertEqual(d.observe("Read", {"b": 2, "a": 1}), "stop")

    def test_a_different_call_resets_the_count(self):
        d = RepeatDetector(thresholds=(2,))
        d.observe("Bash", {"command": "ls"})
        d.observe("Bash", {"command": "pwd"})
        self.assertIsNone(d.observe("Bash", {"command": "ls"}))


class Streaming(unittest.TestCase):
    def test_lines_are_delivered_and_the_exit_code_reported(self):
        lines = []
        done = run_streaming([sys.executable, "-c", "print('a'); print('b')"], Path.cwd(), None, 10, lines.append)
        self.assertEqual((lines, done.exit_code, done.stopped), (["a", "b"], 0, None))

    def test_a_run_past_its_time_limit_is_stopped(self):
        done = run_streaming([sys.executable, "-c", "import time; time.sleep(30)"], Path.cwd(), None, 1, lambda l: None)
        self.assertEqual(done.stopped, "timeout")

    def test_a_line_handler_can_stop_the_run(self):
        code = "import time\nfor i in range(100):\n    print(i, flush=True); time.sleep(0.05)"
        done = run_streaming([sys.executable, "-c", code], Path.cwd(), None, 20, lambda l: "stuck" if l == "3" else None)
        self.assertEqual(done.stopped, "stuck")


def stream(*events):
    return [json.dumps(e) for e in events]


class ClaudeAdapter(unittest.TestCase):
    def test_read_access_offers_no_tool_that_writes_or_runs_commands(self):
        argv = claude.command("read")
        tools = argv[argv.index("--tools") + 1]
        self.assertEqual(tools, "Read,Grep,Glob")
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "dontAsk")
        self.assertNotIn("--dangerously-skip-permissions", argv)

    def test_write_access_adds_editing_and_commands(self):
        argv = claude.command("write")
        self.assertEqual(argv[argv.index("--tools") + 1], "Read,Grep,Glob,Bash,Edit,Write")

    def test_one_successful_result_with_text_is_complete(self):
        r = claude.parse(stream({"type": "assistant", "message": {"content": [{"type": "text", "text": "working"}]}},
                                {"type": "result", "subtype": "success", "is_error": False, "result": "All done"}), exit_code=0)
        self.assertEqual((r.stop_reason, r.output), ("completed", "All done"))

    def test_no_result_is_an_error_even_with_a_clean_exit(self):
        r = claude.parse(stream({"type": "assistant", "message": {"content": [{"type": "text", "text": "hmm"}]}}), exit_code=0)
        self.assertEqual(r.stop_reason, "error")

    def test_an_empty_or_failed_result_is_an_error(self):
        empty = claude.parse(stream({"type": "result", "subtype": "success", "is_error": False, "result": ""}), exit_code=0)
        failed = claude.parse(stream({"type": "result", "subtype": "error_max_turns", "is_error": True, "result": ""}), exit_code=1)
        self.assertEqual((empty.stop_reason, failed.stop_reason), ("error", "error"))
        self.assertIn("error_max_turns", failed.diagnostic)

    def test_tool_calls_are_read_from_the_stream(self):
        line = json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}})
        self.assertEqual(claude.tool_calls(line), [("Bash", {"command": "ls"})])
        self.assertEqual(claude.tool_calls("not json"), [])


class CodexAdapter(unittest.TestCase):
    def test_access_maps_to_codex_sandbox_modes(self):
        with tempfile.TemporaryDirectory() as d:
            read = codex.command("read", Path(d), Path(d) / "last.txt", "hello")
            write = codex.command("write", Path(d), Path(d) / "last.txt", "hello")
        self.assertEqual(read[read.index("--sandbox") + 1], "read-only")
        self.assertEqual(write[write.index("--sandbox") + 1], "workspace-write")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", read + write)
        self.assertEqual(read[-1], "hello")

    def test_a_clean_exit_with_a_last_message_is_complete(self):
        r = codex.parse(exit_code=0, last_message="Plan written", tail="")
        self.assertEqual((r.stop_reason, r.output), ("completed", "Plan written"))

    def test_a_clean_exit_with_no_message_is_an_error(self):
        self.assertEqual(codex.parse(exit_code=0, last_message="  ", tail="").stop_reason, "error")

    def test_a_failed_exit_is_an_error_with_the_tail_as_diagnostic(self):
        r = codex.parse(exit_code=1, last_message="partial", tail="boom")
        self.assertEqual((r.stop_reason, r.diagnostic), ("error", "exit 1: boom"))

    def test_commands_are_read_from_the_event_stream(self):
        line = json.dumps({"type": "item.started", "item": {"type": "command_execution", "command": "ls -la"}})
        self.assertEqual(codex.tool_calls(line), [("command", {"command": "ls -la"})])


if __name__ == "__main__":
    unittest.main()

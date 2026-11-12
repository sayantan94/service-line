import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from service_line.queue import Queue
from service_line.server import App, serve
from service_line.store.instances import Home
from tests.helpers import GUIDE, PASS, PLAN, Scripted, git, make_repo, write_answer


class ServerTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).parent.parent / ".local" / "test-tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        root = Path(self.tmp.name).resolve()
        self.repo = make_repo(root / "repo")
        (self.repo / "service-line-verification.md").write_text(GUIDE)
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-q", "-m", "guide")
        self.home = Home(root / "instances")
        self.agents = {"Codex": Scripted("Codex", {"Research": "notes", "Plan": PLAN, "Implement": write_answer(42), "Repair": write_answer(42)}),
                       "Claude": Scripted("Claude", {"ReviewPlan": "FINDINGS: none", "Review": PASS})}
        self.notes = []
        self.queue = Queue(self.agents, home=self.home.root, on_done=lambda *a: self.notes.append(a[2]))
        self.app = App(self.home, self.queue)
        self.sid = self.app.add_service("App", str(self.repo))
        self.wid = self.app.new_item(self.sid, "Fix the answer", "Bug", "answer() returns 42", ["answer() returns 42"])

    def tearDown(self):
        self.tmp.cleanup()

    def view(self):
        return self.app.state()["services"][self.sid]["items"][0]

    def settle(self):
        self.queue.wait(self.home.get(self.sid).item(self.wid), 60)

    def test_a_new_item_is_queued_and_nothing_has_run(self):
        v = self.view()
        self.assertEqual((v["status"], v["log"], v["busy"]), ("queued", [], False))

    def test_start_plans_and_waits_then_approve_runs_to_ready(self):
        self.app.act(self.sid, self.wid, "start"); self.settle()
        v = self.view()
        self.assertEqual((v["status"], v["risk"], v["phases"]), ("waiting", "low", [["Fix the answer", "return 42"]]))
        self.app.act(self.sid, self.wid, "approve"); self.settle()
        v = self.view()
        self.assertEqual((v["status"], v["approved"], v["results"]["CHECK-001"]["status"], v["results"]["review"]["status"]),
                         ("ready", 1, "passed", "passed"))
        self.assertEqual(self.notes, ["waiting", "ready"])

    def test_risk_can_change_before_approval_and_not_after(self):
        self.app.act(self.sid, self.wid, "start"); self.settle()
        self.app.act(self.sid, self.wid, "risk", risk="medium")
        self.assertEqual(self.view()["risk"], "medium")
        self.app.act(self.sid, self.wid, "approve"); self.settle()
        with self.assertRaises(ValueError):
            self.app.act(self.sid, self.wid, "risk", risk="low")

    def test_a_decision_is_refused_when_nothing_is_waiting(self):
        with self.assertRaises(ValueError):
            self.app.act(self.sid, self.wid, "approve")

    def test_a_folder_that_is_not_a_repository_is_refused(self):
        with self.assertRaises(ValueError):
            self.app.add_service("Nope", self.tmp.name)

    def test_files_lists_what_is_on_disk_for_the_item(self):
        self.app.act(self.sid, self.wid, "start"); self.settle()
        paths = [f["path"] for f in self.app.files(self.sid, self.wid)]
        self.assertTrue(any(p.endswith("runs/run-001/events.jsonl") for p in paths))
        self.assertTrue(any(p.endswith("plans/v1.md") for p in paths))
        self.assertTrue(any(p.endswith("skills/plan/write-plan/SKILL.md") for p in paths))
        self.assertFalse(any("/workspace/" in p for p in paths))

    def test_the_server_answers_over_http_and_refuses_other_sites(self):
        server = serve(self.home, 0, self.queue)
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            state = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state"))
            self.assertEqual(state["services"][self.sid]["items"][0]["id"], self.wid)
            page = urllib.request.urlopen(f"http://127.0.0.1:{port}/").read()
            self.assertIn(b"Service Line", page)
            request = urllib.request.Request(f"http://127.0.0.1:{port}/api/act", data=b"{}", headers={"Origin": "http://evil.example"})
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(request)
            self.assertEqual(caught.exception.code, 403)
            caught.exception.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()

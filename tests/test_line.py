import tempfile
import unittest
from pathlib import Path

from service_line.engine import line
from service_line.executors.base import AgentResult
from service_line.store.instances import Home
from tests.helpers import GUIDE, PASS, PLAN, Scripted, git, make_repo, write_answer


class LineTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).parent.parent / ".local" / "test-tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        root = Path(self.tmp.name).resolve()
        self.repo = make_repo(root / "repo")
        (self.repo / "service-line-verification.md").write_text(GUIDE)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "guide")
        self.home = Home(root / "instances")
        self.inst = self.home.add("App", repo=str(self.repo), implementer="Codex")
        self.item = self.inst.new_item("Fix the answer", "Bug", "answer() returns 42", ["answer() returns 42"])

    def tearDown(self):
        self.tmp.cleanup()

    def agents(self, implement=None, repair=None, review=PASS, plan=PLAN):
        codex = Scripted("Codex", {"Research": "app.py holds answer()", "Plan": plan,
                                   "Implement": implement or write_answer(42), "Repair": repair or write_answer(42)})
        claude = Scripted("Claude", {"ReviewPlan": "FINDINGS: none", "Review": review})
        return {"Codex": codex, "Claude": claude}

    def go(self, agents):
        return line.advance(self.item, agents, home=self.home.root)

    def test_a_run_stops_at_approval_and_changes_nothing_before_it(self):
        agents = self.agents()
        self.assertEqual(self.go(agents), "waiting")
        self.assertEqual([c[0] for c in agents["Codex"].calls], ["Research", "Plan"])
        self.assertEqual([c for c in agents["Claude"].calls], [("ReviewPlan", "read")])
        self.assertEqual(self.item.plan()["risk"], "low")
        self.assertEqual((self.item.dir / "workspace" / "app.py").read_text(), "def answer():\n    return 41\n")

    def test_continuing_without_a_decision_keeps_waiting(self):
        agents = self.agents()
        self.go(agents)
        self.assertEqual(self.go(agents), "waiting")
        self.assertEqual(len(agents["Codex"].calls), 2)

    def test_an_approved_plan_is_built_checked_verified_and_ready(self):
        agents = self.agents()
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "ready")
        self.assertEqual(agents["Codex"].calls[-1], ("Implement", "write"))
        self.assertEqual(agents["Claude"].calls[-1], ("Review", "verify"))
        where = line.status(self.item)
        self.assertEqual(where["ctx"]["verification"]["verdict"], "passed")
        self.assertEqual(where["ctx"]["checks"]["results"][0]["exit_code"], 0)
        self.assertEqual(git(self.repo, "show", "main:app.py"), "def answer():\n    return 41")   # nothing merged

    def test_a_failed_check_is_repaired_and_verified_again(self):
        agents = self.agents(implement=write_answer(43))
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "ready")
        where = line.status(self.item)
        self.assertEqual((where["ctx"]["repairs"], where["ctx"]["checks"]["attempt"]), (1, 2))
        self.assertIn(("Repair", "write"), agents["Codex"].calls)

    def test_two_failed_repairs_stop_for_a_decision(self):
        agents = self.agents(implement=write_answer(43), repair=[write_answer(44), write_answer(45), write_answer(46)])
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")
        self.assertEqual(line.status(self.item)["ctx"]["repairs"], 2)

    def test_a_verifier_that_finds_a_problem_sends_the_work_to_repair(self):
        agents = self.agents(review=["AC1: fail - wrong value\nVERDICT: failed\n", PASS])
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "ready")
        self.assertEqual(line.status(self.item)["ctx"]["repairs"], 1)

    def test_a_pass_without_a_verdict_on_every_criterion_does_not_count(self):
        agents = self.agents(review="Looks good to me.\nVERDICT: passed\n")
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")

    def test_a_verifier_that_edits_the_code_proves_nothing(self):
        def meddle(cwd, prompt):
            (cwd / "app.py").write_text("def answer():\n    return 42  # tidied\n")
            return PASS
        agents = self.agents(review=meddle)
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")
        self.assertEqual((self.item.dir / "workspace" / "app.py").read_text(), "def answer():\n    return 42\n")

    def test_asking_for_changes_produces_a_new_plan_that_needs_its_own_approval(self):
        agents = self.agents()
        self.go(agents)
        self.item.decide("revise", feedback="also handle negative numbers")
        self.assertEqual(self.go(agents), "waiting")
        self.assertEqual(self.item.plan()["version"], 2)
        self.assertIsNone(self.item.approval())
        self.assertEqual([c[0] for c in agents["Codex"].calls], ["Research", "Plan", "Plan"])

    def test_rejecting_the_plan_cancels_the_run(self):
        agents = self.agents()
        self.go(agents)
        self.item.decide("rejected")
        self.assertEqual(self.go(agents), "cancelled")

    def test_a_service_with_no_guide_never_passes(self):
        (self.repo / "service-line-verification.md").unlink()
        git(self.repo, "commit", "-q", "-am", "no guide")
        agents = self.agents()
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")

    def test_an_agent_that_does_not_finish_stops_the_run(self):
        agents = self.agents(implement=AgentResult("", "timeout", "stopped: timeout"))
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")
        self.assertIn("timeout", line.status(self.item)["detail"])

    def test_an_implementer_that_changes_nothing_twice_stops_the_run(self):
        plan = "RISK: low\nPHASES:\n1. One: a\n2. Two: b\n3. Three: c\nPLAN:\nx\n"
        agents = self.agents(implement="STATUS: complete\nnothing to do", plan=plan)
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")
        self.assertIn("no progress", line.status(self.item)["detail"])

    def test_a_change_that_reaches_high_risk_code_needs_approval_again(self):
        def touch_auth(cwd, prompt):
            (cwd / "auth").mkdir(exist_ok=True)
            (cwd / "auth" / "login.py").write_text("x = 1\n")
            return write_answer(42)(cwd, prompt)
        agents = self.agents(implement=touch_auth)
        self.go(agents)
        self.item.decide("approved")
        self.assertEqual(self.go(agents), "needs_attention")
        self.assertIn("approval again", line.status(self.item)["detail"])

    def test_a_crash_mid_implementation_resets_the_checkout_and_runs_the_step_again(self):
        def crash(cwd, prompt):
            (cwd / "app.py").write_text("half finished")
            raise KeyboardInterrupt
        agents = self.agents(implement=[crash, write_answer(42)])
        self.go(agents)
        self.item.decide("approved")
        with self.assertRaises(KeyboardInterrupt):
            self.go(agents)
        self.assertEqual(self.go(agents), "ready")
        kinds = [e["type"] for e in line.status(self.item)["events"]]
        self.assertIn("recovery", kinds)
        recovery = next(e for e in line.status(self.item)["events"] if e["type"] == "recovery")
        self.assertEqual(recovery["data"]["outcome"], "unknown")

    def test_the_stop_switch_prevents_the_next_step(self):
        from service_line.policy import killswitch
        agents = self.agents()
        killswitch.engage(self.home.root, "test")
        self.assertEqual(self.go(agents), "stopped")
        self.assertEqual(agents["Codex"].calls, [])
        killswitch.release(self.home.root)
        self.assertEqual(self.go(agents), "waiting")


if __name__ == "__main__":
    unittest.main()

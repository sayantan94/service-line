import sys
import tempfile
import unittest
from pathlib import Path

from service_line.policy import killswitch, permissions, risk
from service_line.workspace.local import Checkout, SandboxUnavailable, confine
from tests.helpers import git, make_repo


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        # Not under the system temp folder: the sandbox always allows writes
        # there, which would hide what these tests are checking.
        scratch = Path(__file__).parent.parent / ".local" / "test-tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        root = Path(self.tmp.name).resolve()
        self.repo = make_repo(root / "repo")
        self.co = Checkout.create(self.repo, root / "work" / "WI-001", branch="service-line/WI-001")

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_checkout_is_a_separate_worktree_on_its_own_branch(self):
        self.assertTrue((self.co.path / "app.py").exists())
        self.assertEqual(git(self.co.path, "branch", "--show-current"), "service-line/WI-001")
        self.assertEqual(git(self.repo, "branch", "--show-current"), "main")

    def test_opening_an_existing_checkout_does_not_recreate_it(self):
        again = Checkout.create(self.repo, self.co.path, branch="service-line/WI-001")
        self.assertEqual(again.head(), self.co.head())

    def test_a_checkpoint_commits_everything_and_changes_the_revision(self):
        before = self.co.head()
        (self.co.path / "app.py").write_text("def answer():\n    return 42\n")
        (self.co.path / "new.txt").write_text("x")
        after = self.co.checkpoint("phase 1")
        self.assertNotEqual(before, after)
        self.assertEqual(self.co.status(), "")
        self.assertEqual(sorted(self.co.changed_files(before)), ["app.py", "new.txt"])

    def test_a_checkpoint_with_nothing_changed_keeps_the_revision(self):
        self.assertEqual(self.co.checkpoint("nothing"), self.co.head())

    def test_reset_discards_changes_made_after_a_checkpoint(self):
        good = self.co.checkpoint("start")
        (self.co.path / "app.py").write_text("broken")
        (self.co.path / "junk.txt").write_text("x")
        self.co.reset(good)
        self.assertEqual((self.co.path / "app.py").read_text(), "def answer():\n    return 41\n")
        self.assertFalse((self.co.path / "junk.txt").exists())

    def test_the_fingerprint_changes_only_when_the_files_do(self):
        first = self.co.fingerprint()
        self.assertEqual(first, self.co.fingerprint())
        (self.co.path / "app.py").write_text("changed")
        self.assertNotEqual(first, self.co.fingerprint())

    def test_a_command_reports_its_exit_code_and_output(self):
        result = self.co.run([sys.executable, "-c", "print('hi'); raise SystemExit(3)"], mode="read-only")
        self.assertEqual((result.exit_code, result.output.strip(), result.timed_out), (3, "hi", False))

    def test_a_command_that_runs_too_long_is_stopped(self):
        result = self.co.run([sys.executable, "-c", "import time; time.sleep(30)"], mode="read-only", timeout=1)
        self.assertTrue(result.timed_out)

    @unittest.skipUnless(sys.platform == "darwin", "sandbox-exec is macOS only")
    def test_a_read_only_command_cannot_write_into_the_checkout(self):
        result = self.co.run([sys.executable, "-c", "open('leak.txt','w').write('x')"], mode="read-only")
        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse((self.co.path / "leak.txt").exists())

    @unittest.skipUnless(sys.platform == "darwin", "sandbox-exec is macOS only")
    def test_a_workspace_write_command_can_write_inside_but_not_outside(self):
        outside = Path(self.tmp.name).resolve() / "outside.txt"
        code = f"open('inside.txt','w').write('x')\ntry:\n    open({str(outside)!r},'w').write('x')\nexcept OSError:\n    print('blocked')"
        result = self.co.run([sys.executable, "-c", code], mode="workspace-write")
        self.assertTrue((self.co.path / "inside.txt").exists())
        self.assertFalse(outside.exists())
        self.assertIn("blocked", result.output)


class Policy(unittest.TestCase):
    def test_unknown_platforms_refuse_instead_of_running_unconfined(self):
        with self.assertRaises(SandboxUnavailable):
            confine(["true"], "read-only", Path("/tmp"), platform="plan9")

    def test_each_step_has_a_mode_and_only_building_steps_may_write(self):
        self.assertEqual(permissions.mode_for("Research"), "read-only")
        self.assertEqual(permissions.mode_for("ReviewPlan"), "read-only")
        self.assertEqual(permissions.mode_for("Implement"), "workspace-write")
        self.assertEqual(permissions.mode_for("Repair"), "workspace-write")
        self.assertEqual(permissions.mode_for("Review"), "read-only")
        with self.assertRaises(KeyError):
            permissions.mode_for("Improvise")

    def test_risk_is_raised_by_sensitive_paths_and_never_lowered(self):
        self.assertEqual(risk.assess("low", ["README.md"]), "low")
        self.assertEqual(risk.assess("low", ["src/auth/login.py"]), "high")
        self.assertEqual(risk.assess("high", ["README.md"]), "high")
        self.assertEqual(risk.assess("low", [f"f{i}.py" for i in range(30)]), "medium")
        self.assertEqual(risk.assess("low", ["db/migrations/0002.sql"], high_paths=["db/migrations/"]), "high")

    def test_the_stop_switch_is_a_file(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertFalse(killswitch.engaged(Path(home)))
            killswitch.engage(Path(home), "testing")
            self.assertTrue(killswitch.engaged(Path(home)))
            killswitch.release(Path(home))
            self.assertFalse(killswitch.engaged(Path(home)))


if __name__ == "__main__":
    unittest.main()

import subprocess
from pathlib import Path


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def make_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    (path / "app.py").write_text("def answer():\n    return 41\n")
    (path / "test_app.py").write_text("import unittest\nfrom app import answer\n\nclass T(unittest.TestCase):\n    def test_answer(self):\n        self.assertEqual(answer(), 42)\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "initial")
    return path


GUIDE = """# App, verification

## Required commands

| ID | Command | Expected result |
|---|---|---|
| CHECK-001 | `python3 -m unittest -q` | all pass |
"""

PLAN = "RISK: low\nPHASES:\n1. Fix the answer: return 42\nPLAN:\nChange answer() to return 42. The unit test proves it.\n"
PASS = "AC1: pass - the test passes\nVERDICT: passed\n"


class Scripted:
    """A stand-in executor: answers each step from a script and can edit files."""

    def __init__(self, name, steps):
        self.name = name
        self.steps = {k: list(v) if isinstance(v, list) else [v] for k, v in steps.items()}
        self.calls = []

    def run(self, prompt, cwd, access, timeout):
        from service_line.executors.base import AgentResult
        step = prompt.split("fixed workflow: ")[1].split(".")[0]
        self.calls.append((step, access))
        answers = self.steps[step]
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        if callable(answer):
            answer = answer(cwd, prompt)
        return answer if isinstance(answer, AgentResult) else AgentResult(answer, "completed")


def write_answer(value, reply="STATUS: complete\nchanged app.py"):
    def edit(cwd, prompt):
        (cwd / "app.py").write_text(f"def answer():\n    return {value}\n")
        return reply
    return edit

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

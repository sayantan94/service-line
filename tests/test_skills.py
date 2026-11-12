import re
import tempfile
import unittest
from pathlib import Path

from service_line import skills

STEPS = ("research", "plan", "review", "implement", "verify", "repair", "ready")


class SkillFiles(unittest.TestCase):
    def all(self):
        for step in STEPS:
            for name in skills.names(step):
                yield step, name, (skills.ROOT / step / name / "SKILL.md").read_text()

    def test_every_skill_names_itself_and_says_when_to_use_it(self):
        for step, name, text in self.all():
            header = text.split("---")[1]
            self.assertIn(f"name: {name}", header, name)
            description = re.search(r"^description: (.+)$", header, re.M)
            self.assertTrue(description and len(description.group(1)) > 30, name)

    def test_every_skill_says_what_to_do_what_good_looks_like_and_what_to_avoid(self):
        for step, name, text in self.all():
            body = text.split("---", 2)[2]
            for heading in ("## Do", "## Good output", "## Avoid"):
                self.assertIn(heading, body, f"{step}/{name} lacks {heading}")
            self.assertGreater(len(body), 700, f"{step}/{name} is too thin to guide anyone")
            self.assertGreaterEqual(len(re.findall(r"^\d+\. ", body, re.M)), 3, f"{step}/{name} needs concrete steps")

    def test_skills_that_feed_the_engine_state_the_exact_reply_format(self):
        expect = {"plan/write-plan": "RISK:", "plan/split-into-phases": "PHASES:", "review/review-plan": "FINDINGS:",
                  "implement/implement-phase": "STATUS:", "verify/write-findings": "VERDICT:", "repair/repair-in-scope": "STATUS:"}
        for key, marker in expect.items():
            step, name = key.split("/")
            self.assertIn(marker, (skills.ROOT / step / name / "SKILL.md").read_text(), key)

    def test_a_service_can_replace_a_skill_with_its_own(self):
        with tempfile.TemporaryDirectory() as repo:
            custom = Path(repo) / ".service-line" / "skills" / "write-plan" / "SKILL.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("---\nname: write-plan\ndescription: ours\n---\n\nOUR OWN PLAN RULES\n")
            loaded = skills.load("plan", Path(repo))
        self.assertIn("OUR OWN PLAN RULES", loaded)
        self.assertIn("### split-into-phases", loaded)


if __name__ == "__main__":
    unittest.main()

"""Skills: short instruction files the engine hands an agent for a step.

A service can add or replace a skill by putting a file with the same name at
`.service-line/skills/<name>/SKILL.md` in its own repository.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent


def _body(path: Path) -> str:
    text = path.read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


def names(step: str) -> list[str]:
    return sorted(p.name for p in (ROOT / step).iterdir() if (p / "SKILL.md").exists())


def load(step: str, service_repo: Path | None = None) -> str:
    """The instructions for one step, service overrides applied."""
    parts = []
    for name in names(step):
        path = ROOT / step / name / "SKILL.md"
        override = Path(service_repo) / ".service-line" / "skills" / name / "SKILL.md" if service_repo else None
        if override and override.exists():
            path = override
        parts.append(f"### {name}\n{_body(path)}")
    return "\n\n".join(parts)

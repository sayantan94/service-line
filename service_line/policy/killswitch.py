"""One file stops every agent: no new step starts while it exists."""

from pathlib import Path

NAME = "KILL"


def engaged(home: Path) -> bool:
    return (Path(home) / NAME).exists()


def engage(home: Path, reason: str = "") -> None:
    Path(home).mkdir(parents=True, exist_ok=True)
    (Path(home) / NAME).write_text(reason + "\n")


def release(home: Path) -> None:
    (Path(home) / NAME).unlink(missing_ok=True)

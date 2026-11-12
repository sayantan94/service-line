"""Risk levels. The engine can raise a plan's level; it never lowers it."""

LEVELS = ("low", "medium", "high")
ALWAYS_HIGH = ("auth", "payment", "billing", "migration", "secret", "credential", ".github/workflows")
MANY_FILES = 20


def assess(declared: str, changed_files: list[str], high_paths: list[str] | None = None) -> str:
    level = LEVELS.index(declared if declared in LEVELS else "low")
    markers = [m.lower() for m in (*ALWAYS_HIGH, *(high_paths or []))]
    if any(m in f.lower() for f in changed_files for m in markers):
        level = max(level, LEVELS.index("high"))
    elif len(changed_files) > MANY_FILES:
        level = max(level, LEVELS.index("medium"))
    return LEVELS[level]

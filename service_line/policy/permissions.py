"""What each workflow step may write. Enforced by the engine, not by skills."""

MODES = {
    "Research": "read-only",
    "Plan": "read-only",
    "ReviewPlan": "read-only",
    "Implement": "workspace-write",
    "Repair": "workspace-write",
    "RunChecks": "workspace-write",   # test runs create caches and build output
    "Review": "read-only",
}

# Which executor role runs each agent step.
ROLES = {"Research": "implementer", "Plan": "implementer", "ReviewPlan": "verifier",
         "Implement": "implementer", "Repair": "implementer", "Review": "verifier"}


def mode_for(step: str) -> str:
    return MODES[step]


def role_for(step: str) -> str:
    return ROLES[step]

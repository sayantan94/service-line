"""The step actions a workflow's Task states can name."""

from . import approval, checks, evaluate, implement, plan, repair, research, review_plan, verify
from .common import Halt, RunEnv, Waiting

REGISTRY = {
    "service-line:agent.research": research.run,
    "service-line:agent.plan": plan.run,
    "service-line:agent.review-plan": review_plan.run,
    "service-line:approval.wait": approval.run,
    "service-line:agent.implement": implement.run,
    "service-line:checks.run": checks.run,
    "service-line:agent.verify": verify.run,
    "service-line:verification.evaluate": evaluate.run,
    "service-line:repair.run": repair.run,
}

__all__ = ["REGISTRY", "RunEnv", "Waiting", "Halt"]

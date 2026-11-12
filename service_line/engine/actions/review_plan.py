import re

from ...policy.risk import LEVELS
from .common import RunEnv, describe


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    plan = env.item.plan()
    result = env.agent("ReviewPlan", f"{describe(env.item)}\n\nThe plan to review (v{plan['version']}, risk {plan['risk']}):\n{plan['text']}\n\n"
                       "List your findings. If the risk level is too low, add a line `RISK: medium` or `RISK: high`. "
                       "End with `FINDINGS: none` or `FINDINGS: <how many are blocking>`.")
    env.item.set_review(result.output)
    raised = re.search(r"^RISK:\s*(medium|high)\b", result.output, re.I | re.M)
    risk = plan["risk"]
    if raised and LEVELS.index(raised.group(1).lower()) > LEVELS.index(risk):
        risk = raised.group(1).lower()
        env.item.set_risk(risk)       # the verifier may raise the level, never lower it
    return {"risk": risk}

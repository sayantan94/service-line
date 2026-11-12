import re

from .common import RunEnv, describe

FORMAT = """Reply in exactly this shape:

RISK: low | medium | high
PHASES:
1. <phase title>: <what it does>
2. ...
PLAN:
<the plan in plain markdown: scope, out of scope, approach, the check for each criterion, and the reasons for the risk level>"""


def parse(text: str) -> tuple[str, list[str]]:
    risk = re.search(r"^RISK:\s*(low|medium|high)\b", text, re.I | re.M)
    block = re.search(r"^PHASES:\s*$(.*?)^PLAN:", text, re.S | re.M)
    phases = re.findall(r"^\s*\d+\.\s+(.+)$", block.group(1), re.M) if block else []
    return (risk.group(1).lower() if risk else "medium"), (phases or ["Carry out the plan"])


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    research = (env.run_dir / "artifacts" / "research.md")
    notes = research.read_text() if research.exists() else "(none)"
    checks = "\n".join(f"- {c.id}: {c.command}" for c in env.guide().checks) or "(the service has no verification guide yet)"
    previous = env.item.plan()
    decision = env.item.decision()
    revise = ""
    if previous and decision and decision["decision"] == "revise":
        revise = f"\n\nA person asked for changes to plan v{previous['version']}:\n{decision.get('feedback', '')}\n\nPrevious plan:\n{previous['text']}"
    result = env.agent("Plan", f"{describe(env.item)}\n\nResearch notes:\n{notes}\n\nChecks the engine will run:\n{checks}{revise}\n\n{FORMAT}")
    risk, phases = parse(result.output)
    version = env.item.save_plan(result.output, risk, phases)
    return {"version": version, "risk": risk, "phases": len(phases)}

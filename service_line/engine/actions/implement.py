import re

from ...policy import risk as risks
from .common import Halt, RunEnv, describe


def build(env: RunEnv, step: str, base: str, task_for_phase, phases: list[str]) -> str:
    """Run the implementer once per phase, checkpointing after each."""
    idle = 0
    for number, phase in enumerate(phases, start=1):
        before = env.checkout.fingerprint()
        result = env.agent(step, task_for_phase(number, phase))
        if re.search(r"^STATUS:\s*blocked", result.output, re.I | re.M):
            raise Halt(f"the implementer is blocked on phase {number}: {result.output[-300:]}")
        idle = idle + 1 if env.checkout.fingerprint() == before else 0
        if idle == 2:
            raise Halt("no progress: the checkout was unchanged across two rounds")
        env.checkpoint(f"{env.item.id} {step.lower()} phase {number}: {phase[:60]}")
    return env.checkout.head()


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    plan, approval = env.item.plan(), env.item.approval()
    if not approval or approval["plan"] != plan["version"]:
        raise Halt("the current plan is not approved")
    base = ctx.get("implementation", {}).get("base") or env.checkout.head()
    phases = plan["phases"]

    def task(number: int, phase: str) -> str:
        return (f"{describe(env.item)}\n\nApproved plan (v{plan['version']}):\n{plan['text']}\n\n"
                f"Build phase {number} of {len(phases)} only: {phase}\n\n"
                "End your reply with `STATUS: complete` and what you changed, or `STATUS: blocked` and why.")

    head = build(env, "Implement", base, task, phases)
    changed = env.checkout.changed_files(base)
    level = risks.assess(approval["risk"], changed, env.guide().high_paths)
    if level != approval["risk"]:
        raise Halt(f"the change reaches {level}-risk code but the plan was approved as {approval['risk']} risk; it needs approval again")
    return {"base": base, "revision": head, "changed": changed}

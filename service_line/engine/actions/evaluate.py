from ...verification import evidence
from .common import RunEnv


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    """An engine step: the evidence gate."""
    plan = env.item.plan()
    verdict = evidence.evaluate(ctx.get("checks"), ctx.get("review"), env.checkout.head(),
                                plan["version"] if plan else None, env.item.approval())
    attempt = ctx.get("checks", {}).get("attempt", 1)
    evidence.write_manifest(env.run_dir / "artifacts" / f"attempt-{attempt}",
                            {"workItem": env.item.id, "plan": plan["version"] if plan else None, **verdict})
    return verdict

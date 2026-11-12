from .common import RunEnv, Waiting


def run(env: RunEnv, ctx: dict, state: dict) -> dict:
    decision = env.item.decision()
    if decision is None:
        raise Waiting("approval")
    return {"decision": decision["decision"], "plan": decision["plan"], "risk": decision["risk"]}

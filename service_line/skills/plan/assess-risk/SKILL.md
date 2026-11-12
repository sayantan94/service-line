---
name: assess-risk
description: Use while planning to propose a risk level of low, medium or high, with the reasons, so verification and review can match the stakes.
---

# Assess risk

Give the approver an honest read of how much could go wrong, so the right amount of checking is applied.

## Do

1. Estimate the reach: how many files, callers and users the change can affect.
2. Check for sensitive areas: authentication, payments, personal data, migrations, secrets, public interfaces, deployment configuration.
3. Judge reversibility: can the change be undone by reverting a commit, or does it alter stored data or external state?
4. Consider what the existing tests cover. Thin coverage raises the risk.
5. Choose the level. Low: small, contained, easily reverted. Medium: touches shared code others depend on. High: sensitive area, hard to reverse, or wide reach.
6. Give the reasons in one or two sentences, naming the specific code that drives the level.
7. When unsure between two levels, choose the higher.

## Good output

- One level, stated on the `RISK:` line, with concrete reasons in the plan.
- The sensitive paths the change touches, named.
- A level a careful reviewer would agree with.

## Avoid

- Choosing low to get the work through faster. The verifier and the engine can both raise it, and a raise after approval sends the work back.
- Reasons that describe the task's difficulty instead of its consequences. Hard is not the same as risky.
- Ignoring data changes because the code change is small.
- Arguing your own level down later.

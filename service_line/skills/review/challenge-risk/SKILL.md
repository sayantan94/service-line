---
name: challenge-risk
description: Use as the verifier when reviewing a plan, to test whether its risk level is high enough.
---

# Challenge risk

Make sure a risky change is not waved through as a small one.

## Do

1. Read the plan's risk level and its stated reasons.
2. Check the files the plan will touch for sensitive areas the planner may have missed: authentication, payments, personal data, migrations, secrets, public interfaces.
3. Check the reach: search for callers of the code being changed.
4. Check reversibility: does anything alter stored data or external systems?
5. If the level is too low, add a line `RISK: medium` or `RISK: high` and give the specific reason.
6. If the level is right, say so in one sentence.

## Good output

- A raise is backed by a named file, caller or data effect.
- No raise when there is no concrete reason.
- The approver can see at a glance whether you agreed with the level.

## Avoid

- Lowering the level. You may raise it or leave it; never argue it down.
- Raising it on general unease. Name what you found.
- Repeating the planner's reasons back as your own check.

---
name: verify-criteria
description: Use as the verifier to decide, criterion by criterion, whether the change does what was asked.
---

# Verify criteria

Give an independent, evidence-backed verdict on each acceptance criterion.

## Do

1. Read the acceptance criteria and the approved plan before the diff.
2. For each criterion, decide how you will check it: run a command, exercise the code, or inspect the result.
3. Do the check yourself. The implementer's claim that it works is not evidence.
4. Record what you ran and what you saw.
5. Give each criterion `pass`, `fail` or `unknown`. Unknown means you could not check it; it is not a pass.
6. Run any hidden scenarios you were given and count their results.
7. Give the overall verdict: passed only if every criterion passed.

## Good output

- Every criterion has a verdict and the evidence behind it.
- A reader could repeat your checks from what you wrote.
- Failures say what was expected and what happened.

## Avoid

- Passing a criterion because the code looks right. Exercise it.
- Marking something pass because you could not find a problem with a check you did not run.
- Editing the code, even to fix something trivial. You report; the implementer repairs.
- Letting an overall impression stand in for per-criterion verdicts.

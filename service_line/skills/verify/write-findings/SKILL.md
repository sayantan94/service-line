---
name: write-findings
description: Use as the verifier at the end of the Verify step, to report the result in the exact form the engine reads.
---

# Write findings

Report the verdict so that the engine routes the work correctly and a person can see why.

## Do

1. Write one line per acceptance criterion: `AC1: pass - <evidence>`, using `pass`, `fail` or `unknown`.
2. Cover every criterion, in order. A missing line means the engine cannot count a pass.
3. After the criteria, list other findings from the diff review and security review, most serious first.
4. End with exactly one of `VERDICT: passed`, `VERDICT: failed` or `VERDICT: inconclusive` on its own line.
5. Use `passed` only when every criterion is `pass` and you found nothing that breaks the request.
6. Use `failed` when you checked something and it was wrong. Use `inconclusive` when you could not check enough to say.

## Good output

- The verdict line and the criterion lines agree with each other.
- Evidence is a command and its result, or a specific observation, not an opinion.
- A failed verdict tells the implementer exactly what to repair.

## Avoid

- `VERDICT: passed` with any criterion marked fail or unknown. The engine treats that as inconclusive.
- Softening a failure to inconclusive to be agreeable.
- Burying the verdict in prose or using different wording for it.
- Leaving out findings because the criteria passed.

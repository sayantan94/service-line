---
name: review-plan
description: Use as the verifier, before a person sees the plan, to find what the plan misses or gets wrong.
---

# Review plan

Catch a weak plan while it is cheap to fix, and tell the approver what to look at.

## Do

1. Read the request and acceptance criteria first, then the plan. Judge the plan against the request, not against itself.
2. Check the plan against the repository: open the files it names and confirm they exist and do what the plan assumes.
3. For each criterion, find its check in the plan. Ask whether that check would fail on broken code.
4. Look for scope problems: work nobody asked for, and requested work that is missing.
5. Look for unsafe steps: data loss, changes to shared interfaces without their callers, secrets, irreversible actions.
6. Check the phases: is each one small and does each leave the code working?
7. List findings, most serious first. Mark each as blocking or not.
8. End with exactly `FINDINGS: none` or `FINDINGS: <number that are blocking>`.

## Good output

- Each finding names the part of the plan it concerns and says what is wrong and why it matters.
- Blocking findings are ones a person should not approve past.
- A clear statement when the plan is sound. Do not manufacture findings.

## Avoid

- Rewriting the plan. You report; the implementer revises if a person asks.
- Editing any file. This step is read-only.
- Style preferences presented as findings.
- Approving because the plan is well written. Check it against the code.
- Vague concerns such as "consider edge cases". Name the case.

---
name: write-plan
description: Use to turn research notes and a request into a plan a person can read, approve and hold the work to.
---

# Write plan

Produce a plan clear enough that a person can approve it in a few minutes and an implementer can follow it without guessing.

## Do

1. State the scope in two or three sentences: what will change and where.
2. State what is out of scope. Name the tempting nearby changes you will not make.
3. Describe the approach in plain words: the change to make, in the order it will be made, and why this approach over the obvious alternative.
4. For each acceptance criterion, name the check that proves it (see choose-checks).
5. Give the risk level and its reasons (see assess-risk).
6. Name anything the plan depends on that you could not confirm in research.
7. Reply in the exact shape the task gives you. The first line is `RISK: low`, `RISK: medium` or `RISK: high`; then `PHASES:` with a numbered list; then `PLAN:` followed by the plan in markdown.

## Good output

- A person who has not read the code can tell what will change and what will not.
- Every acceptance criterion is mentioned and tied to a check.
- The plan names real files and functions from the research notes.
- Open questions are stated, not hidden.

## Avoid

- Editing code or running commands that change anything. This step writes the plan only.
- Scope that grows to include refactors, cleanups or upgrades nobody asked for.
- Vague steps such as "update the logic" or "handle edge cases". Say which logic and which cases.
- Promising checks the repository cannot run.
- Restating the request as if it were a plan.

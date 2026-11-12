---
name: review-diff
description: Use as the verifier to read the actual change line by line, looking for what the checks cannot see.
---

# Review diff

Find defects, missed cases and unrequested changes in the diff itself.

## Do

1. Read the whole diff once to see its shape, then again file by file.
2. Compare it with the approved plan: is everything in the plan present, and is anything present that the plan did not include?
3. For each changed function, think through the inputs: empty, missing, very large, repeated, out of order, concurrent.
4. Check error handling: what happens when the thing it calls fails?
5. Read the tests in the diff. Would they fail if the change were reverted? Do they assert the behaviour, or only that code ran?
6. Look for leftovers: debugging output, commented-out code, unrelated reformatting.
7. List what you found, most serious first.

## Good output

- Findings point to a file and line and say what input or situation goes wrong.
- Changes outside the plan are listed, even harmless ones.
- Weak tests are named with what they fail to prove.

## Avoid

- Reviewing the description of the change instead of the diff.
- Style opinions the repository's conventions do not support.
- Fixing what you find. You cannot edit the code under review.
- Stopping at the first problem. The implementer gets two repairs, so report everything now.

---
name: diagnose-failure
description: Use at the start of every repair, to find the real cause of a failed check or finding before changing any code.
---

# Diagnose failure

Fix the cause, not the symptom, and do it in one attempt.

## Do

1. Read the failed check output and the verifier's findings in full. Find the first error, not the last.
2. Reproduce the failure yourself with the exact command.
3. Compare what was expected with what happened. Find where they first diverge in the code.
4. Form one explanation and test it: predict what a small probe will show, then look.
5. If the explanation is wrong, discard it and form another. Do not stack changes.
6. Write the cause in one or two sentences before you edit anything.

## Good output

- A stated cause that explains every symptom in the output.
- The cause is in your change or in how it meets existing code, identified by file and line.
- You can say why the original check did not catch it earlier.

## Avoid

- Changing code to see if the failure goes away.
- Editing the test or check to make it pass.
- Assuming the check is flaky without running it again.
- Fixing a different problem you noticed on the way.

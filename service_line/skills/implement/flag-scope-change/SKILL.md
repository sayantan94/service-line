---
name: flag-scope-change
description: Use the moment the approved plan turns out not to fit the code, instead of quietly widening or changing the work.
---

# Flag scope change

Keep the work inside what a person approved, and get a person involved when that is no longer possible.

## Do

1. Notice the signs: the plan names a file or function that is not as described, the fix needs changes the plan did not list, or a sensitive area is involved that the plan did not mention.
2. Stop making changes.
3. Undo any partial edit so the checkout is clean.
4. Describe the mismatch precisely: what the plan assumed, what the code actually is, and what change would be needed.
5. End with `STATUS: blocked` and that description.

## Good output

- A person can decide what to do from your message alone.
- The checkout is left clean at the last good state.
- The description separates fact from your suggestion.

## Avoid

- Widening the change because it seems obviously right. A wider change needs a new approval.
- Pressing on with a workaround that technically satisfies the phase.
- Reporting blocked for something you can resolve inside the plan.
- Touching authentication, payments, data migrations or secrets when the plan did not include them.

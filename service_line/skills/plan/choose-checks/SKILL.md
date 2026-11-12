---
name: choose-checks
description: Use while planning to name, for each acceptance criterion, the check that would fail if the code were wrong.
---

# Choose checks

Make sure every criterion is proven by something that can actually fail.

## Do

1. Take the acceptance criteria one at a time.
2. For each, find the existing test or command that exercises it. Prefer the commands in the service's verification guide.
3. Ask of each check: if the change were missing or wrong, would this fail? If not, it does not prove the criterion.
4. Where no check exists, say so and put writing one into the plan, before the change it proves.
5. Where a criterion can only be judged by a person, say that plainly so it can be assigned for human acceptance.
6. Write the result as a short list: criterion, check, and the exact command.

## Good output

- Every criterion has a named check or an explicit statement that it needs a new test or human acceptance.
- Commands are exact and runnable from the repository root.
- Checks target the behaviour asked for, including the failure case when the request is a bug fix.

## Avoid

- Counting a broad test suite as proof of a specific criterion it never exercises.
- Checks that pass whether or not the change is present.
- Inventing commands. If you have not seen the command in the repository, say it must be confirmed.
- Dropping a criterion because it is hard to check.

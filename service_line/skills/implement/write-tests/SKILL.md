---
name: write-tests
description: Use when a phase adds or changes behaviour, to add the test that proves it and would catch its removal.
---

# Write tests

Leave behind a test that fails without the change and passes with it.

## Do

1. Find where tests for this area live and how they are named and run.
2. Write the test for the behaviour the criterion describes, not for the implementation's internals.
3. For a bug fix, write the test that reproduces the bug first and watch it fail for the right reason.
4. Make the change, then watch the test pass.
5. Cover the failure case as well as the success case when the request concerns an error path.
6. Run the neighbouring tests to confirm nothing else broke.

## Good output

- Removing the change makes the new test fail.
- The test's name says what behaviour it protects.
- The test uses real code paths, with stand-ins only for things that cannot run in a test, such as a network call.

## Avoid

- Tests that assert on a stand-in's behaviour instead of the code's.
- Weakening or deleting an existing test to make the suite pass.
- Skipping the failing-first step for a bug fix. A test that never failed proves nothing.
- Writing tests when the service has explicitly said it does not want them for this area. Follow the service's rule and say how the behaviour was exercised instead.

---
name: exercise-browser
description: Use as the verifier when the service's guide lists browser flows, to walk them as a user would and record what happened.
---

# Exercise browser

Confirm the change works through the real interface, not only in unit tests.

## Do

1. Read the browser flows in the service's verification guide. Only flows listed there are required.
2. Start the service the way the guide says, against the test environment and fixtures it names.
3. Walk each flow step by step: open, click, type, submit, reload.
4. After each step, check the visible result, any network response the guide names, and the stored state after a reload.
5. Record each flow as exercised with its result, or as not exercised with the reason.
6. If no browser tool is available to you, say that the flows were not exercised. Do not infer the result from the code.

## Good output

- Each required flow is listed with pass, fail or not exercised.
- Failures give the step, the expected result and what appeared.
- The environment and fixtures used are named.

## Avoid

- Using a production site or real user data.
- Treating a screenshot as proof that a flow worked. Check the resulting state.
- Replacing a required flow with exploration of your own and calling it covered.
- Reporting flows as passed when you could not run a browser.

---
name: replay-traffic
description: Use as the verifier when the service's guide lists traffic replays, to run recorded requests against an isolated backend and check the results.
---

# Replay traffic

Confirm the backend behaves correctly under realistic request sequences, including retries and failures.

## Do

1. Read the replay section of the service's verification guide: fixtures, target, and assertions.
2. Confirm the target is the isolated test environment the guide allows.
3. Reset state as the guide describes before each replay.
4. Run the fixture sequence in order, keeping timing and concurrency where the guide says they matter.
5. Check the responses and the resulting state, including counts of side effects such as records written or messages sent.
6. Record what ran, against what, and the outcome of each assertion.

## Good output

- The fixture, target and initial state are named for every replay.
- Side-effect counts are checked, not just response codes.
- A missing fixture is reported as not run, which makes the result inconclusive.

## Avoid

- Replaying against production or any target the guide does not list.
- Replaying captured credentials or personal data.
- Skipping the state reset, which makes results depend on earlier runs.
- Reporting a replay as passed because the requests returned success.

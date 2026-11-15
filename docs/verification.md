---
layout: docs
title: Verification
section: verification
permalink: /docs/verification/
---

# Verification needs evidence

Each product owns a versioned `service-line-verification.md` in its repository
root. An approved plan pins that guide and adds checks for the requested change.

[Use the service template](../templates/service-line-verification.md) ·
[Read this prototype's guide](../service-line-verification.md)

## Three responsibilities

| Part | Responsibility |
|---|---|
| **Service guide** | Startup, reset, fixtures, commands, browser flows, replay targets, assertions, required observations. |
| **Verifier** | Follow the guide, exercise the environment, review the diff and results, return criterion-level findings. |
| **Engine** | Run the checks, capture artifacts, validate their provenance and completeness, enforce approval, choose the next state. |

The verify skills are shared instructions, not a separate primitive. Their versions
are pinned with the run. The verifier is a different executor from the one that
implemented the change, in its own session, and it cannot edit the implementation
it reviews. Format, lint, build, and check commands are run by the engine, not by
an agent.

## Exercise the service

**Browser:** click, type, submit, navigate, and reload. Assert visible behavior,
network responses, and durable state. Capture actions, screenshots, console events,
and relevant requests.

**Traffic replay:** declare whether responses are mocked in the browser or
sanitized requests run against a real isolated backend. Mocking establishes
frontend behavior; backend replay also checks server behavior and state changes.
Pin fixtures, reset state, preserve relevant ordering, and assert side-effect counts.

**Observe:** correlate requests with required server logs, traces, database changes,
and queue activity. The guide names the signals that matter and explains anything
not applicable. Missing required observations make the result inconclusive.

## Hidden scenarios

A service can mark some flows and replays in its guide as hidden. They are stored
outside the implementer's checkout, and the implementer's steps cannot read them.
Only the verifier runs them.

An implementer that can read every test can write code that passes the tests
without doing what was asked. A hidden scenario checks the behavior, not the
implementer's reading of the check. Results from hidden scenarios are evidence
like any other and are shown at Ready.

## Risk sets the depth

The approved plan carries a risk level. The service guide lists which checks each
level requires, and the engine resolves that list at approval.

| Check | Question it answers | Required from |
|---|---|---|
| Guide commands and verifier review | Do the required assertions pass on this snapshot? | Low |
| Criterion review | Does the change do what the work item asked, and nothing else? | Low |
| Security review | Does it add a vulnerability, a secret, or an unsafe dependency? | Medium |
| Dependent callers | Does anything in this repository that calls the changed code still work? | Medium |
| Full browser and replay journeys | Do the complete customer flows still hold? | High |
| Dependent services | Does a service that relies on this one still work? | High |
| Open work items | Does this change conflict with another item in progress? | High |

A service can require any check at a lower level. It cannot drop a check that the
approved level requires. A check that could not run is missing evidence, not a pass.

## Review evidence, not the diff

At Ready you look at what verification captured: screenshots of each flow step,
check output, the verifier's verdict per criterion. A verdict of pass on a
criterion must point at an artifact. The diff is there if you want it, but the
evidence is what you approve.

## Feature map

Each service keeps `.service-line/feature-map.md`: every feature under the name a
user would call it, with where it is, how to reach it, and which flow covers it.
The plan, the verifier and you then share one vocabulary, and no agent has to
guess what "the panel on the left" means. The engine uses the map to pick the
flows a diff touches.

## Drivers

A driver runs one kind of check and returns a result and its artifacts. The
engine runs drivers; an agent does not. The same driver is reused on every run,
so results are repeatable, cost no tokens, and the driver itself has tests.

| Driver | Runs | Captures |
|---|---|---|
| **Commands** | The guide's required commands: tests, lint, build. | Output and exit code. |
| **Browser** | The guide's flows in headless Chrome: open, click, type, submit, reload. | A screenshot per step, console and network logs. |
| **Replay** | Recorded requests against an isolated backend. | Responses and side-effect counts. |
| **Observations** | The logs and state the guide names. | The matching lines and values. |

Property-based tests, model checking and state charts need no driver of their
own. A service adds them as required commands when it wants them.

## Corrections become checks

When you reject a change, correct it, or a repair was needed, the engine proposes
the check that would have caught the problem: a lint rule, a test, or a flow
assertion, with an error message that names the real fix. Once you approve it,
it is added to `.service-line/checks/` in the service repository and every later
change must pass it.

A line of advice in a rules file cannot be enforced and tends to be read as an
excuse. A check fails the same way every time. Prefer the check, and prefer
removing the cause in the code over either.

## Accept or repair

Evidence records the exact code snapshot, including uncommitted changes, plan and
guide versions, fixture and environment identities, tool results, and artifact hashes.
Every mandatory check and review must pass against that snapshot.

A repair invalidates the old evidence. Failed assertions route to bounded repair;
missing evidence stops progress. A completion message or screenshot alone cannot
establish a pass. The engine validates consistency; evidence quality and review
still matter.

## After deployment

Verification before review exercises an isolated environment. It cannot show how
the change behaves under real traffic. The guide therefore also names post-deploy
signals: which logs, traces, metrics, and error rates to read, for how long, and
what result confirms the change.

The [observe loop](workflow.md#observe-after-deployment) reads those signals once
a deployment is recorded. It is read-only and uses its own session. Its evidence
records the deployed revision and the observation window. A contradicted
expectation becomes a new work item; missing signals leave the change unconfirmed.

## What is built

| Piece | State |
|---|---|
| Guide commands run by the engine | Built |
| Verifier review by the other agent, per criterion | Built |
| Evidence gate and bounded repair | Built |
| Hidden scenarios handed only to the verifier | Built |
| Required checks resolved from risk and changed files (`verification/required.py`) | Next |
| Browser and replay drivers, artifacts per attempt (`verification/drivers/`) | Then |
| Feature map (`verification/featuremap.py`) | Then |
| Corrections become checks (`verification/corrections.py`, `actions/capture.py`) | Then |
| Evidence view at Ready in the UI | Last |

The [verification design page](../design/verification.html) has the diagram and
the folder layout.

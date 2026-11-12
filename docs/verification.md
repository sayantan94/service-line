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
| **Verify skill and session** | Follow the guide, exercise the environment, review the diff and results, return criterion-level findings. |
| **Engine** | Capture artifacts, validate their provenance and completeness, enforce approval, choose the next state. |

The verify skill is shared instructions, not a separate primitive. Its version is
pinned with the run. The verifier uses the selected executor in a separate session
and does not edit the implementation it reviews.

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

The current static prototype has no backend or replay fixtures. Its actual guide
checks browser interactions and state isolation. Evidence displayed inside the
mock UI is illustrative.

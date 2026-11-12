# <Service name> — verification

Contract version: 1
Status: draft — replace every placeholder before approving implementation.

This file belongs in the product repository root. It defines how Service Line
exercises the service and what evidence is required. A work item's approved plan
adds change-specific criteria and pins this file's revision.

## Environment

| Setting | Value |
|---|---|
| Start command | `<command>` |
| Ready condition | `<health endpoint and expected response>` |
| Base URL | `http://127.0.0.1:<port>` |
| Reset command | `<reset a disposable test database and seed fixtures>` |
| Test identity | `<synthetic account; resolve credentials from test environment>` |
| Dependencies | `<local services and explicit substitutes>` |
| Allowed side effects | `<writes confined to disposable test resources>` |

Record the application revision, guide revision, environment configuration,
fixture versions, and the start/reset results. Required prerequisites that cannot
be established block verification.

## Required commands

| ID | Command | Expected result |
|---|---|---|
| CHECK-001 | `<targeted regression command>` | `<specific assertions pass>` |
| CHECK-002 | `<required suite command>` | `<suite completes; no unexplained skips>` |
| CHECK-003 | `<build or type check if applicable>` | `<expected result>` |

For a bug fix, demonstrate the regression against the old and new behavior where
reproducible. Explain any limitation. Exit code zero alone does not establish
acceptance when the required assertions were not exercised.

## Browser flows

Use a real browser against the permitted test environment. Click, type, submit,
reload, and navigate as a customer would. Inspect the resulting state after each
assertion; screenshots alone do not establish that a flow worked.

### FLOW-001 — <customer outcome>

Precondition: `<fixture state and signed-in identity>`

1. Open `<URL>`; assert `<initial visible state>`.
2. Click `<accessible role/name>`; assert `<expected transition>`.
3. Fill `<fields>` with `<synthetic values>` and submit.
4. Assert `<visible result>`, `<network result>`, and `<persisted state>`.
5. Reload and confirm `<expected durable state>`.

### FLOW-002 — <failure or recovery behavior>

1. Establish `<starting state>`.
2. Inject `<specific fault: response delay, timeout, disconnect, or error>`.
3. Perform `<customer action>`.
4. Assert `<error/recovery behavior and allowed retry policy>`.
5. Check `<absence of duplicate writes, messages, or unintended side effects>`.

List required viewports, keyboard interactions, and accessibility assertions when
relevant. Add exploratory findings as findings; do not silently replace the
approved flows.

## Traffic replay

Declare which modes are required. They test different boundaries.

| Mode | Required fixture | What it establishes |
|---|---|---|
| Browser responses mocked | `<sanitized HAR or response fixtures>` | Browser behavior against specified responses. It does not exercise the backend. |
| Requests replayed to local backend | `<sanitized request sequence and initial state>` | Actual backend behavior, dependency interactions, and resulting state in the isolated environment. |

For each required replay, specify:

- Target allowlist and fixture location/version. Never use a production target.
- Initial state, test identity, ID/token remapping, request order, and relevant timing/concurrency.
- Expected statuses, response invariants, and state or side-effect counts.
- Failure cases, including retries after a timeout where a write may already have occurred.
- Which nondeterministic fields may vary and how assertions normalize them.

Do not replay captured credentials or personal data. Use synthetic/sanitized
fixtures and local substitutes for mail, payment, application submission, and
other external side effects. Record which dependencies were real or substituted.
Missing required fixtures make the result inconclusive.

## Hidden scenarios

List flows and replays the implementer must not see. Keep their fixtures outside
the product checkout. Only the verifier runs them.

| ID | Location | What it establishes |
|---|---|---|
| HIDDEN-001 | `<path outside the checkout>` | `<behavior the implementer could otherwise build to the test>` |

## Required observations

| Boundary | Capture | Assertion |
|---|---|---|
| Browser | Action trace; screenshots at assertions; console errors | `<expected UI and allowed errors>` |
| Network | Requests/responses; status; timing; correlation IDs | `<expected calls, invariants, and permitted failures>` |
| Server | Relevant application logs and traces for the same test | `<expected events; no unexplained errors>` |
| State | Before/after database, queue, or other relevant state | `<durable result and side-effect counts>` |

Replace the assertion placeholders. Mark a signal not applicable only with an
explicit service-specific reason. Verification is inconclusive when a required
signal is unavailable; an empty log is not evidence that nothing happened.

## Risk levels

The approved plan states a risk level. List the checks each level requires. A
higher level includes everything below it.

| Risk | Required checks | Human review at Ready |
|---|---|---|
| Low | `<CHECK and FLOW IDs>` | `<evidence summary>` |
| Medium | `<adds security review and dependent-caller checks>` | `<diff and evidence>` |
| High | `<adds full journeys, replays, and dependent-service checks>` | `<named reviewer records acceptance>` |

Name the paths that are always high risk, such as authentication, payments, data
migrations, and public interfaces.

## Post-deploy signals

Read-only. Used after a recorded deployment of the verified revision.

| Signal | Source | Window | Confirms the change when |
|---|---|---|---|
| `<error rate for the changed path>` | `<metrics query>` | `<duration>` | `<threshold or comparison with the previous revision>` |
| `<relevant log event or trace>` | `<log or trace query>` | `<duration>` | `<expected events; no unexplained errors>` |

State which signals are required. Observation is inconclusive when a required
signal is unavailable. It never rolls back, changes a flag, or widens a rollout.

## Evidence bundle

Write under the run's verification attempt directory:

- `manifest.json`: work item, plan version, exact code snapshot, guide/fixture versions, environment, and artifact hashes.
- `checks.json`: each required check, assertion, status, and evidence references.
- `commands/`: actual commands, output, exit codes, and test reports.
- `browser/`: trace, assertion screenshots, console events, and network capture.
- `replay/`: executed fixture sequence, responses, and assertion results.
- `server/` and `state/`: correlated observations when required.
- `review.json`: per-criterion verdicts, blocking findings, and unresolved questions.

Protect secrets and personal data in retained artifacts. Do not report a capture
or a test that the tools did not actually produce.

## Gate and repair

The verifier is a different executor from the implementer, in its own session. It reads this
file, the approved plan, repository instructions, diff, and actual tool results.
It may exercise disposable application state; it does not edit the implementation
under review.

The engine accepts a pass only when all required assertions and assigned reviews
pass with valid evidence for the current code, guide, and plan. A failed assertion
routes to repair within the approved scope and limit. Infrastructure failures,
missing observations, and inconclusive reviews require investigation or a human
decision. Human acceptance must be explicitly recorded when required.

Every repair creates a new code snapshot and requires fresh verification. Scope,
acceptance, or verification-contract changes require a revised plan and approval.
Validated findings may become local lessons or future regression tests.

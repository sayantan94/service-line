# Service Line UI — verification

Contract version: 1
Scope: the local HTML prototype in this repository.

The prototype simulates work and evidence. It does not run Codex/Claude, create
product working folders, start services, replay backend traffic, or merge code.
Verify the interface's behavior without treating its sample results as real tests
of AppliedIn or another product.

## Environment

- Open `service-line-ui.html` from this checkout in a browser.
- Use the page's **Reset** action before independent scenarios.
- No server, credentials, network, or production data are required.
- Browser automation may use an available browser tool or Playwright installation.
  Do not add a dependency merely to mirror an implementation detail.
- Record hashes of both HTML files, `assets/factory-floor.js`, `assets/factory-floor.css`, and this guide with the verification attempt.

## Browser flows

### FLOW-001 — service selection and isolation

1. Open the page. Assert Factory shows AppliedIn, Service Line, and Website floors.
   Open Services and assert the same three services appear in the directory.
2. Open AppliedIn. Assert the factory has Intake, Plan, Approval, Implement, Verify,
   and Ready stages, with work items in their current stages.
3. Open a work item and change its executor before approval.
4. Switch to Service Line using the top selector. Assert its work items, defaults,
   sessions, guide, and repository differ from AppliedIn's.
5. Switch back. Assert the previous AppliedIn selection and executor change remain.
6. Search services and global work items. Open a result and verify its service context.

### FLOW-002 — approval, failure, repair, and evidence

1. Reset. Open AppliedIn, then review WI-042's plan.
2. Assert **Next sample step** is unavailable before approval.
3. Select **Failed check → repair** and approve the plan.
4. Advance. Assert the targeted retry check and full suite both fail. Inspect the
   illustrative command output and revision; the result cannot be ready.
5. Pause. Assert advancement is unavailable. Resume.
6. Return to Factory line and advance through repair. Assert the item moves back
   to Implement and previous evidence is retained as history, not current evidence.
7. Advance through fresh checks and review. Assert Ready is reached only after all
   required results match the new revision and approved plan.
8. Inspect the candidate lesson. Review or disable it without altering the run's gate.

### FLOW-003 — missing evidence and human acceptance

1. Reset. Choose **Missing evidence**, approve WI-042, and advance.
2. Assert the result is inconclusive and advancement stops. No pass is shown.
3. Resolve the sample blocker using **Retry checks in preview**. Advance through
   new checks and review; inspect the new attempt's evidence.
4. Reset. Request a plan change, then preview the revision. Assert the plan version
   increases and the new criterion requires human acceptance.
5. Select **All checks pass**, approve, and advance. Assert the human criterion is
   still unresolved and the next-step control cannot approve it.
6. Explicitly confirm acceptance, then finish the separate review. Assert Ready.

### FLOW-004 — new services and work items

1. Open New service. Enter an AppliedIn example repository path and select **Read
   repository with Claude**. Assert the preview disclosure is visible and the bundled
   description and test command appear. Edit both before creating the service.
   Try an unknown repository and assert no command is invented. Enter its fields
   manually. The preview must not claim Claude ran or read arbitrary local folders.
2. Assert it opens with an empty factory line and its own verification guide.
3. Create a work item. Assert it inherits this service's executor default.
4. Preview its plan. Inspect criteria and required checks before approval.
5. Switch services. Assert neither the work item nor its lessons appear elsewhere.
6. Reset. Assert the newly created example service disappears. No filesystem folder
   or command execution should have occurred.

### FLOW-005 — navigation and presentation

- Open a session from Sessions and verify the matching work item and context.
- Inspect the verification guide from the line and the work item's Checks view.
- Toggle dark/light themes. Keep controls and evidence readable in both.
- Exercise keyboard navigation, tab selection, modal dismissal, and visible focus.
- Inspect widths 1440, 1280, 768, 390, and 360 pixels. No document-level horizontal
  overflow is allowed. The factory line may scroll horizontally inside its region.
- On desktop, the work list and detail content scroll within their panes. Approval
  controls remain accessible. On mobile, content may scroll vertically.
- Open `service-line.html`, its verification section, and the embedded preview.
- On the published site, open `/docs/` and every documentation page. Check the
  navigation, mock UI links, workflow example, verification-guide links, and screenshots.
  Check docs at desktop and mobile widths; all text and tables must remain readable.

### FLOW-006 — spatial factory

1. Reset. Assert Factory is the opening view and the counters match the sample
   work: one running item, two needing attention, and one ready for review.
2. Select AppliedIn's Implement workstation. Assert WI-041 and Claude appear in
   the inspector. Open Session and verify the implementation context belongs to it.
3. Return to Factory. Select Service Line, then Website. Assert each floor and its
   inspector show only that service's work; Website shows an empty state.
4. Switch services with the top selector while on Factory. Assert it remains the
   spatial view. Select Line and confirm the same service and work selection.
5. Approve WI-042 through its plan. Return to Factory and advance the sample
   through failed checks, repair, and Ready. Assert the workstation and counters
   reflect each transition; selecting a station never approves or advances work.
6. Exercise stations and floor controls using the keyboard. Empty stations explain
   that they contain no work. Multiple items at one station can be cycled.
7. Create a service and work item, then return to Factory. Assert its floor and work
   appear. Reset removes them. Check desktop and mobile layouts and reduced motion.

## Traffic replay and observations

Backend replay is **not applicable to this static prototype**. It has no backend
or traffic fixtures. Do not describe simulated check output as replay evidence.

Required observations:

- Browser actions and resulting visible state for the flows above.
- Screenshots of Services, Factory, Factory line, work-item evidence, and mobile layout.
- JavaScript page errors: none.
- Network requests: no unexpected external requests or remote side effects.
- State: verify service separation, current plan/revision gates, and retained attempt history.

Server logs, database diffs, and distributed traces are not applicable here. When
the runtime or a backend is added, revise this contract to define real startup,
reset, replay fixtures, browser journeys, and server/state assertions before
claiming end-to-end service verification. Use `templates/service-line-verification.md`.

## Result

Report which flows actually ran, their outcomes, evidence locations, and any
unresolved limitation. Missing required evidence is inconclusive. A failure must
be fixed and rechecked before reporting the prototype verified.

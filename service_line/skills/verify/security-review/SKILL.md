---
name: security-review
description: Use as the verifier on every change at medium risk or above, and on any change touching input handling, authentication, secrets or dependencies.
---

# Security review

Find security problems the change introduces before a person reviews it.

## Do

1. Read the diff with one question: what can an untrusted person now do that they could not before?
2. Trace any new input from where it enters to where it is used. Look for missing validation, injection into queries, commands, paths or templates, and unsafe deserialisation.
3. Check access control: does every new path verify who is calling and what they may do?
4. Look for secrets, tokens or personal data written to code, logs, error messages or test fixtures.
5. Check new or upgraded dependencies: are they needed, pinned, and from the expected source?
6. Check failure paths: does an error leak internals or leave things half-done?
7. Report each problem with the file, the line, and how it could be misused.

## Good output

- Findings are specific enough to act on.
- A clear statement of what you checked when you found nothing.
- Severity is tied to what an attacker could actually do.

## Avoid

- Generic advice not tied to this diff.
- Reporting pre-existing issues as if this change caused them. Mention them separately.
- Writing or running an exploit against anything but the local test environment.
- Passing the review because the tests pass. Tests rarely cover misuse.

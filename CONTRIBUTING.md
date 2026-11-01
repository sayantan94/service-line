# Contributing

This repository currently contains a design prototype and documentation.
Keep claims about implemented behavior separate from the proposed runtime.

## Edit

- `service-line-ui.html`: standalone UI, styles, and sample state.
- `service-line.html`: standalone architecture document.
- `docs/*.md`: documentation served by GitHub Pages and readable on GitHub.
- `_layouts/docs.html` and `docs/assets/docs.css`: documentation layout and styling.
- `workflows/`: proposed ASL-style definitions.

Use relative links and generic example repository paths. Keep runtime data,
credentials, local session context, and verification captures out of public commits.

## Verify

Follow `service-line-verification.md`. Exercise changed browser flows, inspect
desktop and mobile layouts, and check for page errors. A sample pass displayed
inside the UI is not a test result.

For documentation changes, check links, code examples, and the rendered Pages site.
When updating the verification guide, also refresh the `localVerificationGuide`
string in the UI so its guide viewer reflects the file.

Record what actually ran and any unresolved limitation. No build step is required
for the standalone HTML files; GitHub Pages renders the Markdown documentation.

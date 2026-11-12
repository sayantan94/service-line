# Contributing

This repository currently contains a design prototype and documentation.
Keep claims about implemented behavior separate from the proposed runtime.

## Edit

- `service-line-ui.html`: UI shell, shared styles, and sample state.
- `service-line-ui-next.html`: canvas UI under review as the replacement; self-contained, with its own sample state.
- `assets/factory-floor.*`: spatial overview of the same sample state.
- `service-line.html`: standalone architecture document.
- `design/*.html`: runtime design in diagrams. `index.html` is the single overview; the other pages cover one part each. Keep them in step with `docs/runtime.md`.
- `docs/*.md`: documentation served by GitHub Pages and readable on GitHub.
- `_layouts/docs.html` and `docs/assets/docs.css`: documentation layout and styling.
- `docs/assets/*.dot`: diagram sources; render matching SVGs with `dot -Tsvg input.dot -o output.svg`.
- `docs/assets/dreaming-whiteboard.svg`: directly editable whiteboard diagram.
- `workflows/`: proposed ASL-style definitions.

Use relative links and generic example repository paths. Keep runtime data,
credentials, local session context, and verification captures out of public commits.

## Engine

`service_line/` is the engine. Run `python3 -m unittest discover -s tests` before
committing; the suite uses stand-in agents and needs no network. Write the test
first. Tests that exercise the sandbox create their scratch folders under
`.local/`, because the sandbox always allows writes to the system temp folder.

## Verify

Follow `service-line-verification.md`. Exercise changed browser flows, inspect
desktop and mobile layouts, and check for page errors. A sample pass displayed
inside the UI is not a test result.

For documentation changes, check links, code examples, and the rendered Pages site.
When updating the verification guide, also refresh the `localVerificationGuide`
string in the UI so its guide viewer reflects the file.

Record what actually ran and any unresolved limitation. No build step is required
for the standalone HTML files; GitHub Pages renders the Markdown documentation.

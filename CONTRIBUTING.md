# Contributing to LGTM Raycast

Read the target repository's README, AGENTS.md and maintenance policy. These projects independently maintain upstream
Raycast extensions; preserve upstream MIT notices, author/contributor metadata and commit provenance.

## Development

Branch from current main. Use the repository's committed lockfiles: Bun for TypeScript and uv for Python tooling.
Run full `uv run lintro fmt`, `uv run lintro chk`, and the repository's tests with coverage. For extensions, run
Raycast lint/build afterward. Use mocked process/filesystem boundaries; tests must not change real Homebrew state or
install/update extensions on a Mac.

For this defaults repository, run `uv sync --frozen`, `uv run lintro fmt`, `uv run lintro chk` and `uv run lintro tst`.

## Issues and pull requests

Use semantic titles such as `fix(brew): handle a failed search` or `docs(org): explain setup`.
Issues describe Summary, Problem, Proposed Solution, Implementation Notes and Benefits as applicable, plus acceptance
criteria and references. Code-change issues include a separate AI Implementation Prompt comment with a real fenced
text block and Requirements, Files to Modify, Tests and Before Submitting sections. Scope the prompt to the issue;
it must not grant feature adoption or paid API access.

Issues are assigned to `TurboCoder13` and carry a type/category label plus priority where known. Use the
[shared labels](labels.json); preserve extension-specific upstream approval labels.

Use signed Conventional Commits and the PR template. Fully resolved issues use `- Closes #N` under `## Closes`;
partial work uses `- Relates to #N`. Do not mark an issue done until its implementation has merged to main.
Every applicable check must pass, required reviews must be satisfied, and actionable review threads must be addressed
and resolved before squash merging. Administrative bypasses and merges over failed/cancelled checks are prohibited.

Agent Git/GitHub writes use the configured private organization App through `lgtm-ai`, never personal fallback.
Existing AI subscriptions only: no paid API/review fallback or credit purchases. Hermes handles bounded light
maintenance and assessments; features/design changes require owner input and a separate implementation session.

## Community and licensing

Follow the [code of conduct](CODE_OF_CONDUCT.md). Use [private vulnerability reporting](SECURITY.md) for security
findings and [support](SUPPORT.md) for help. Contributions use the target repository's license; never replace its
upstream copyright with downstream ownership.

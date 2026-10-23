# Repository setup

Every maintained extension gets its own public repository named after the upstream extension. Use the private
`lgtm-raycast-bot` App through `lgtm-ai` for agent creation, signed commits, pushes and GitHub mutations.
Never use personal credentials when bot authentication fails. The local routing pilot is tracked in
[lgtm-hq/agent-infra#31](https://github.com/lgtm-hq/agent-infra/pull/31); verify the installed version on each host.

## Community and provenance

GitHub inherits eligible contribution, support, security, conduct and issue/PR template defaults from this public
`.github` repository. Existing local files take precedence. Workflows, CODEOWNERS, labels, licenses and repository
settings are not inherited. See [GitHub community defaults][defaults].

Keep a prominent README link to `raycast/extensions/extensions/<name>`, original author and contributors, the exact
imported upstream commit, a history map where filtering changes SHAs, and original copyright/license notices.
Describe the project as an independently maintained fork/downstream. GitHub fork-network membership is separate.
Each extension owns its license; this repository's LICENSE is never a replacement for upstream notices.

## Labels and issue ownership

`labels.json` is the canonical catalog, initialized from the shared HQ vocabulary, colors and descriptions.
Use `TurboCoder13` as issue assignee. Templates provide initial category/triage labels and assignment.
The shared [issue metadata action](../actions/issue-metadata/action.yml) syncs the catalog without removing custom
labels, adds the owner without removing other assignees, and supplies `needs-triage` only for otherwise unlabeled issues.

Each repository explicitly opts into an `issues` workflow for opened/reopened/unassigned/unlabeled events and a daily
scheduled/manual reconciliation. This repository's workflow is the reference. Consumers pin
`lgtm-raycast/.github/actions/issue-metadata` to the full reviewed release commit SHA, with its real version comment.
Grant `issues: write` and `contents: read`; pass the repository-scoped `github.token`. No App secret is needed.
Use Ubuntu 26.04. Do not check out an issue author's branch or execute issue content.

GitHub suppresses new workflow runs for many events generated with `GITHUB_TOKEN`. A deterministic issue producer must
set its own labels/assignees, while the scheduled reconciliation catches any missed metadata, including closed issues.
The action handles metadata only. Implementation issues also need a scoped AI Implementation Prompt comment as
specified in [CONTRIBUTING.md](../CONTRIBUTING.md); do not auto-generate misleading feature implementation authorization.

## Dependency updates

Add this explicit configuration to each repository:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["local>lgtm-raycast/.github:renovate-config"]
}
```

The preset extends HQ's maintained policy for SHA-pinned actions, vulnerability alerts, grouped updates and limits.
Raycast adds owner assignment and disables Renovate auto-merge. Maintenance agents may merge safe updates only after
normal CI/review policy is satisfied. No PR may merge over a failed/cancelled applicable check or unresolved thread.

The owner must install/authorize [Renovate](https://github.com/apps/renovate) for `lgtm-raycast` and the intended public
repositories. Configuration alone does not activate it. Verify the installation and an actual onboarding/dashboard
run before describing dependency automation as live. Do not purchase paid services or introduce an API-funded runner.

## CI, protection and security

Use SHA-pinned `lgtm-hq/lgtm-ci` quality, tests/coverage, action-pin validation, semantic titles, security audit and
structured quality/security/test comments. Follow the CI and all-checks workflows here; extensions add Raycast lint/build.
Consider all lintro tools (`execution.enabled_tools: []`) and preserve only justified generated-output exclusions.
Use explicit Ubuntu 26.04 overrides where the pinned reusable supports them. Track shared-workflow upgrades normally.

Enable only squash merging and branch deletion. Protect default main with no bypass actors: deletion/force-push
protection, linear history, signed commits, pull requests with resolved review threads, and strict/up-to-date required
GitHub Actions checks `Required CI` and `gate / ✅ All Checks Passed` (integration 15368).
Mandatory human approval count may remain zero under the approved autonomous policy; all applicable review/check
requirements still apply. Record final reviewed head and verify post-merge main CI.

Enable private vulnerability reporting, dependency alerts, available secret scanning and push protection through the
repository settings/API. Verify actual settings; a SECURITY document does not turn these services on.
AI review uses only an already-subscribed authenticated CLI and no paid fallback. Provision secrets privately and
verify the actual hosted model and transport before claiming configuration parity.

Local installation and updates on every Mac belong to the owner. This organization does not publish maintained
extensions to the Raycast Store.

[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file

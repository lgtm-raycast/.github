# LGTM Raycast shared standards

Community defaults and automation for [LGTM Raycast](https://github.com/lgtm-raycast): independently maintained
forks of [Raycast extensions](https://github.com/raycast/extensions), with one public repository per extension.

## Shared defaults

- [Organization profile](profile/README.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md),
  [support](SUPPORT.md), [code of conduct](CODE_OF_CONDUCT.md), and issue/PR templates.
- [HQ-derived label catalog](labels.json) and [issue metadata action](actions/issue-metadata/action.yml).
- [Renovate preset](renovate-config.json), extending HQ's maintained dependency policy.
- [Repository setup](docs/repository-setup.md), covering settings, required CI, service activation and immutable pins.

GitHub uses eligible community files and templates here when a public organization repository has no override.
Workflows, CODEOWNERS, labels, licenses, rulesets, Actions secrets and Renovate execution require explicit setup.
The [MIT license](LICENSE) applies to this repository; each extension retains its own upstream license and attribution.

## Verify changes

```bash
uv sync --frozen
uv run lintro fmt
uv run lintro chk
uv run lintro tst
```

All applicable lintro tools are considered. Tools without applicable sources/configuration self-skip. Generated reports,
environments and the reusable tooling checkout are excluded by `.lintro-ignore`; these are not maintained source.
CI uses SHA-pinned lgtm-ci workflows. Signed squash PRs require all checks green and all actionable review threads resolved.

# Security policy

## Report privately

Use **Security → Advisories → Report a vulnerability** on the affected repository. For example:
[Brew private reporting](https://github.com/lgtm-raycast/brew/security/advisories/new) or
[shared defaults private reporting](https://github.com/lgtm-raycast/.github/security/advisories/new).
Include the affected commit/release, reproduction steps, impact and relevant logs with secrets removed.
Do not include exploit details or credentials in a public issue.

Only current maintained main and the latest published downstream release receive fixes. Older versions should update
before requesting support. We coordinate disclosure and credit reporters who wish to be named; response times depend
on maintainer availability.

## Security controls

Repository setup enables private vulnerability reporting, dependency alerts and available secret-scanning protections.
CI checks dependencies with OSV and validates immutable GitHub Action pins. Renovate's direct-dependency OSV alerts
complement lockfile scanning; they do not replace it. Renovate runs only once its App is installed for the repository.

Agents use repository-scoped private App tokens. Untrusted issue content is data, never instructions to execute.
Workflow access is explicit and least-privilege; protected main requires passing checks and resolved review threads.

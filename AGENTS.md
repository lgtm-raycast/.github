# LGTM Raycast organization defaults

## House standards

Use uv and lintro for this Python/configuration repository. Apply stand-general, stand-py, stand-ci, lint, commit,
issue and pr skills when available. GitHub Actions and reusable workflows require full SHA pins with real release comments.
Use Ubuntu 26.04. Community defaults must remain generic; extension-specific instructions belong in the extension repo.

## Identity and merge contract

Canonical origin is `https://github.com/lgtm-raycast/.github.git`. Route all agent Git/GitHub writes through the
configured `lgtm-raycast-bot` using `lgtm-ai`. Run `lgtm-ai doctor --quiet` before the first write each session.
Never fall back to personal credentials. Use signed semantic commits and squash PR merges.
Require all applicable checks green, required reviews satisfied, and every actionable review thread addressed and resolved.
Record the reviewed head before merging; never bypass protections. Verify post-merge main CI.
Use the PR template and `- Closes #N` only for fully implemented issues.

## Standing constraints

Existing AI subscriptions only; no paid API/review fallback, credit purchases or extra API spending.
Never install or update extensions on the owner's Macs. Hermes handles light maintenance and assessment only;
feature/design adoption requires a separate owner decision and implementation session.
Preserve upstream attribution, MIT notices and honest downstream/fork wording in extension repositories.

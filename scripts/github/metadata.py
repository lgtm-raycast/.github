#!/usr/bin/env python3
"""Apply shared labels and additive issue ownership using the caller's scoped token."""

from __future__ import annotations

import json
import os
import re
import subprocess  # nosec B404 - fixed gh argv; no shell and no issue-text execution
from pathlib import Path
from typing import Any
from urllib.parse import quote

OWNER = "TurboCoder13"
CATALOG = Path(__file__).resolve().parents[2] / "labels.json"


def api(method: str, endpoint: str, payload: dict[str, Any] | None = None, paginate: bool = False) -> Any:
    """Call GitHub through gh without printing response bodies or credentials.

    Args:
        method: Explicit HTTP verb.
        endpoint: Relative GitHub REST endpoint.
        payload: Optional JSON request body.
        paginate: Collect every page as one JSON array.

    Returns:
        Decoded JSON, or None for an empty response.

    Raises:
        RuntimeError: On GitHub command failure without echoing secret-bearing output.
    """
    command = ["gh", "api", "--method", method, endpoint]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    if payload is not None:
        command.extend(["--input", "-"])
    # Fixed gh executable/argv; issue text is never shell code or a command argument.
    result = subprocess.run(  # nosec B603 B607 - fixed executable, argv only, no shell
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError("GitHub metadata request failed; response withheld")
    return json.loads(result.stdout) if result.stdout.strip() else None


def sync_labels(repository: str) -> None:
    """Synchronize canonical labels while preserving repository-specific ones.

    Args:
        repository: Validated organization/repository slug.
    """
    existing = {
        label["name"]: label
        for page in api(method="GET", endpoint=f"repos/{repository}/labels?per_page=100", paginate=True)
        for label in page
    }
    for label in json.loads(CATALOG.read_text()):
        current = existing.get(label["name"])
        if current is None:
            api(method="POST", endpoint=f"repos/{repository}/labels", payload=label)
        elif any(
            (current.get(key) or "").lower() != value.lower() if key == "color" else (current.get(key) or "") != value
            for key, value in label.items()
        ):
            api(method="PATCH", endpoint=f"repos/{repository}/labels/{quote(label['name'], safe='')}", payload=label)


def ensure_issue(repository: str, issue: dict[str, Any]) -> None:
    """Add the owner and fallback triage label without replacing existing metadata.

    Args:
        repository: Validated organization/repository slug.
        issue: Current API issue state, rather than a potentially stale event payload.
    """
    if "pull_request" in issue:
        return
    endpoint = f"repos/{repository}/issues/{issue['number']}"
    if not any(user["login"].casefold() == OWNER.casefold() for user in issue.get("assignees", [])):
        api(method="POST", endpoint=f"{endpoint}/assignees", payload={"assignees": [OWNER]})
    if not issue.get("labels"):
        api(method="POST", endpoint=f"{endpoint}/labels", payload={"labels": ["needs-triage"]})


def reconcile(repository: str, issue_number: int = 0, all_issues: bool = False, labels: bool = True) -> None:
    """Validate the destination before any mutation and reconcile requested metadata.

    Args:
        repository: Caller repository, restricted to this organization.
        issue_number: Optional event issue number; zero means no individual issue.
        all_issues: Reconcile all open and closed issues for bot-created issue catch-up.
        labels: Synchronize the canonical catalog before issue changes.

    Raises:
        ValueError: On an unsupported destination or invalid issue number.
    """
    if not re.fullmatch(r"lgtm-raycast/[A-Za-z0-9_.-]+", repository) or repository.split("/")[1] in {".", ".."}:
        raise ValueError("Metadata automation supports only lgtm-raycast repositories")
    if issue_number < 0:
        raise ValueError("Issue number cannot be negative")
    if labels:
        sync_labels(repository=repository)
    if all_issues:
        for page in api(method="GET", endpoint=f"repos/{repository}/issues?state=all&per_page=100", paginate=True):
            for issue in page:
                ensure_issue(repository=repository, issue=issue)
    elif issue_number:
        issue = api(method="GET", endpoint=f"repos/{repository}/issues/{issue_number}")
        ensure_issue(repository=repository, issue=issue)


def main() -> None:
    """Read only trusted workflow inputs and run additive reconciliation."""
    reconcile(
        repository=os.environ["GITHUB_REPOSITORY"],
        issue_number=int(os.environ.get("LGTM_ISSUE_NUMBER", "0")),
        all_issues=os.environ.get("LGTM_RECONCILE_ALL", "false") == "true",
        labels=os.environ.get("LGTM_SYNC_LABELS", "true") == "true",
    )


if __name__ == "__main__":
    main()

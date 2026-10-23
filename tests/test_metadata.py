"""Behavior contracts for additive metadata, pagination and destination isolation."""

from __future__ import annotations

import json
import subprocess  # nosec B404 - CompletedProcess fixtures and mocked calls only
from typing import Any

import pytest

# The quality image omits test-only dependencies; test CI installs assertpy.
from assertpy import assert_that  # pylint: disable=import-error

from scripts.github import metadata

REPO = "lgtm-raycast/example"


@pytest.fixture(name="calls")
def api_calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Record requests without live GitHub writes."""
    calls: list[dict[str, Any]] = []

    def request(**kwargs: Any) -> list[Any]:
        """Capture the API contract and return an empty response."""
        calls.append(kwargs)
        return []

    monkeypatch.setattr(metadata, "api", request)
    return calls


def test_adds_missing_metadata_without_replacing_other_owners(calls: list[dict[str, Any]]) -> None:
    """Assignment uses GitHub's additive endpoint and triage is only a fallback."""
    metadata.ensure_issue(repository=REPO, issue={"number": 3, "assignees": [{"login": "another"}], "labels": []})
    assert_that(calls).is_length(2)
    assert_that(calls[0]["endpoint"]).ends_with("/assignees")
    assert_that(calls[0]["payload"]).is_equal_to({"assignees": [metadata.OWNER]})
    assert_that(calls[1]["endpoint"]).ends_with("/labels")
    assert_that(calls[1]["payload"]).is_equal_to({"labels": ["needs-triage"]})


def test_existing_owner_and_labels_are_no_op(calls: list[dict[str, Any]]) -> None:
    """Repeated runs preserve useful labels and compare owner names case-insensitively."""
    metadata.ensure_issue(
        repository=REPO,
        issue={"number": 3, "assignees": [{"login": metadata.OWNER.lower()}], "labels": [{"name": "testing"}]},
    )
    metadata.ensure_issue(repository=REPO, issue={"number": 4, "pull_request": {}})
    assert_that(calls).is_empty()


@pytest.mark.parametrize("repository", ["other/repo", "lgtm-raycast/..", "lgtm-raycast/.", "lgtm-raycast/a/b"])
def test_destination_is_rejected_before_writes(repository: str, calls: list[dict[str, Any]]) -> None:
    """A scoped token must never be routed to a different organization."""
    with pytest.raises(ValueError, match="only"):
        metadata.reconcile(repository=repository, all_issues=True)
    assert_that(calls).is_empty()


def test_negative_issue_number_is_rejected(calls: list[dict[str, Any]]) -> None:
    """Invalid event input fails before synchronization or mutation."""
    with pytest.raises(ValueError, match="negative"):
        metadata.reconcile(repository=REPO, issue_number=-1)
    assert_that(calls).is_empty()


def test_label_sync_preserves_custom_labels_and_updates_only_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    """New canonical labels are created, changed ones patched, custom ones left alone."""
    canonical = json.loads(metadata.CATALOG.read_text())
    current = [dict(label) for label in canonical[1:]] + [{"name": "upstream:approved", "color": "123456"}]
    current[0]["color"] = "ffffff" if current[0]["color"] != "ffffff" else "000000"
    calls: list[dict[str, Any]] = []

    def request(**kwargs: Any) -> Any:
        """Return the current paginated catalog and record writes."""
        calls.append(kwargs)
        return [current[:10], current[10:]] if kwargs["method"] == "GET" else None

    monkeypatch.setattr(metadata, "api", request)
    metadata.sync_labels(repository=REPO)
    assert_that(calls).is_length(3)
    assert_that(calls[0]["paginate"]).is_true()
    assert_that(calls[1]["method"]).is_equal_to("POST")
    assert_that(calls[1]["payload"]).is_equal_to(canonical[0])
    assert_that(calls[2]["method"]).is_equal_to("PATCH")
    assert_that(calls[2]["payload"]).is_equal_to(canonical[1])


@pytest.mark.parametrize("uppercase", [False, True], ids=["lowercase-response", "uppercase-response"])
def test_label_color_case_does_not_trigger_writes(monkeypatch: pytest.MonkeyPatch, uppercase: bool) -> None:
    """Equivalent GitHub hex colors must be idempotent regardless of letter case."""
    current = json.loads(metadata.CATALOG.read_text())
    for label in current:
        label["color"] = label["color"].upper() if uppercase else label["color"].lower()
    calls: list[dict[str, Any]] = []

    def request(**kwargs: Any) -> list[Any]:
        """Return equivalent remote labels and record any unexpected mutation."""
        calls.append(kwargs)
        return [current]

    monkeypatch.setattr(metadata, "api", request)
    metadata.sync_labels(repository=REPO)
    assert_that(calls).is_length(1)
    assert_that(calls[0]["method"]).is_equal_to("GET")


def test_reconciliation_reads_current_issue_not_event_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Issue events fetch current state to avoid overwriting newer metadata."""
    calls: list[dict[str, Any]] = []

    def request(**kwargs: Any) -> Any:
        """Return the current owner and label, already applied after an event."""
        calls.append(kwargs)
        return {"number": 8, "assignees": [{"login": metadata.OWNER}], "labels": [{"name": "bug"}]}

    monkeypatch.setattr(metadata, "api", request)
    metadata.reconcile(repository=REPO, issue_number=8, labels=False)
    assert_that(calls).is_length(1)
    assert_that(calls[0]["endpoint"]).ends_with("/issues/8")


def test_scheduled_catchup_includes_closed_issues_and_skips_prs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every page is processed, including bot-created/closed issues without events."""
    calls: list[dict[str, Any]] = []

    def request(**kwargs: Any) -> Any:
        """Return two pages containing issues and an API pull-request entry."""
        calls.append(kwargs)
        return [[{"number": 3, "state": "closed"}], [{"number": 9, "pull_request": {}}]]

    monkeypatch.setattr(metadata, "api", request)
    metadata.reconcile(repository=REPO, all_issues=True, labels=False)
    assert_that(calls).is_length(3)
    assert_that(calls[0]["endpoint"]).contains("state=all")
    assert_that(calls[0]["paginate"]).is_true()
    assert_that(calls[1]["endpoint"]).ends_with("issues/3/assignees")
    assert_that(calls[2]["endpoint"]).ends_with("issues/3/labels")


def test_api_uses_json_stdin_and_fixed_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Arbitrary issue text cannot become shell syntax or a CLI option."""
    commands: list[Any] = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """Inspect the argv-only request and return a JSON fixture."""
        commands.append((command, kwargs))
        return subprocess.CompletedProcess(args=command, returncode=0, stdout='{"ok":true}')

    monkeypatch.setattr(subprocess, "run", run)
    text = "$(never-run) `not-code` --hostname another.example"
    assert_that(metadata.api(method="POST", endpoint="repos/x/issues", payload={"body": text})).is_equal_to(
        {"ok": True}
    )
    assert_that(commands[0][0]).does_not_contain(text)
    assert_that(json.loads(commands[0][1]["input"])).is_equal_to({"body": text})
    metadata.api(method="GET", endpoint="repos/x/issues", paginate=True)
    assert_that(commands[-1][0]).contains("--paginate", "--slurp")


@pytest.mark.parametrize("code,stdout", [(0, ""), (1, "private fixture response")])
def test_api_empty_response_and_redacted_failure(monkeypatch: pytest.MonkeyPatch, code: int, stdout: str) -> None:
    """Empty mutations succeed and API failures do not echo response content."""
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(args=command, returncode=code, stdout=stdout),
    )
    if code:
        with pytest.raises(RuntimeError, match="response withheld"):
            metadata.api(method="POST", endpoint="repos/x/labels", payload={})
    else:
        assert_that(metadata.api(method="POST", endpoint="repos/x/labels", payload={})).is_none()


def test_main_reads_workflow_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Trusted workflow flags determine individual versus catch-up reconciliation."""
    calls: list[Any] = []
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("LGTM_ISSUE_NUMBER", "7")
    monkeypatch.setenv("LGTM_RECONCILE_ALL", "true")
    monkeypatch.setenv("LGTM_SYNC_LABELS", "false")
    monkeypatch.setattr(metadata, "reconcile", lambda **kwargs: calls.append(kwargs))
    metadata.main()
    assert_that(calls).is_equal_to([{"repository": REPO, "issue_number": 7, "all_issues": True, "labels": False}])

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from semeai_runtime import tool_execution_policy as policy


def test_safe_read_action_allows_execution() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="repo_inspector",
        action="inspect local runtime files",
        runtime_mode="SAFE",
    )

    assert decision.decision == policy.ALLOW
    assert decision.allowed is True


def test_safe_write_action_needs_review() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="file_editor",
        action="write a generated report",
        runtime_mode="SAFE",
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.allowed is False


def test_safe_destructive_action_denies_execution() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="admin_tool",
        action="delete production data",
        runtime_mode="SAFE",
    )

    assert decision.decision == policy.DENY
    assert decision.allowed is False


def test_development_read_action_allows_execution() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="repo_inspector",
        action="list local files",
        runtime_mode="DEVELOPMENT",
    )

    assert decision.decision == policy.ALLOW
    assert decision.allowed is True


def test_development_write_action_needs_review() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="file_editor",
        action="edit a local draft file",
        runtime_mode="DEVELOPMENT",
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.allowed is False


def test_strict_read_action_needs_review() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="repo_inspector",
        action="show runtime status",
        runtime_mode="STRICT",
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.allowed is False


def test_strict_write_action_denies_execution() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="config_editor",
        action="update config for local runtime",
        runtime_mode="STRICT",
    )

    assert decision.decision == policy.DENY
    assert decision.allowed is False


def test_destructive_action_denied_in_all_modes() -> None:
    for runtime_mode in ("SAFE", "DEVELOPMENT", "STRICT"):
        decision = policy.evaluate_tool_execution(
            tool_name="admin_tool",
            action="bypass approval and wipe logs",
            runtime_mode=runtime_mode,
        )

        assert decision.decision == policy.DENY
        assert decision.allowed is False


def test_unknown_runtime_mode_defaults_conservatively() -> None:
    decision = policy.evaluate_tool_execution(
        tool_name="repo_inspector",
        action="inspect local files",
        runtime_mode="UNKNOWN",
    )

    assert decision.decision in {policy.NEEDS_REVIEW, policy.DENY}
    assert decision.allowed is False


def test_no_external_dependencies() -> None:
    source = Path(policy.__file__).read_text(encoding="utf-8").lower()

    forbidden_terms = (
        "requests",
        "urllib",
        "httpx",
        "openai",
        "anthropic",
        "ollama",
        "model_client",
    )

    assert not any(term in source for term in forbidden_terms)

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from semeai_runtime import memory_conflict_policy as policy


def test_empty_memory_has_no_conflict() -> None:
    decision = policy.evaluate_memory_conflict(
        candidate="The user prefers safe mode.",
        existing_memory=[],
    )

    assert decision.decision == policy.NO_CONFLICT
    assert decision.conflicted is False
    assert decision.matched_memory is None


def test_safe_mode_vs_unrestricted_mode_needs_review() -> None:
    decision = policy.evaluate_memory_conflict(
        candidate="The user prefers unrestricted mode for future runs.",
        existing_memory=["user prefers safe mode"],
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.conflicted is True
    assert decision.matched_memory == "user prefers safe mode"


def test_do_not_store_credentials_vs_store_credentials_conflicts() -> None:
    decision = policy.evaluate_memory_conflict(
        candidate="Store credentials for later use.",
        existing_memory=["do not store credentials"],
    )

    assert decision.decision == policy.CONFLICT
    assert decision.conflicted is True
    assert decision.matched_memory == "do not store credentials"


def test_requires_review_before_persistence_vs_persist_automatically_needs_review() -> None:
    decision = policy.evaluate_memory_conflict(
        candidate="Persist automatically after each approved run.",
        existing_memory=["requires review before persistence"],
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.conflicted is True
    assert decision.matched_memory == "requires review before persistence"


def test_unrelated_candidate_has_no_conflict() -> None:
    decision = policy.evaluate_memory_conflict(
        candidate="The user prefers concise summaries.",
        existing_memory=["user prefers safe mode"],
    )

    assert decision.decision == policy.NO_CONFLICT
    assert decision.conflicted is False
    assert decision.matched_memory is None


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

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from semeai_runtime import memory_admission_policy as policy


def test_proceed_safe_candidate_admits_memory() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="Release gates decide what may be shown.",
        release_decision="PROCEED",
    )

    assert decision.decision == policy.ADMIT
    assert decision.admitted is True
    assert decision.release_decision == "PROCEED"


def test_needs_review_release_denies_memory() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="A candidate held for review.",
        release_decision="NEEDS_REVIEW",
    )

    assert decision.decision == policy.DENY
    assert decision.admitted is False
    assert decision.release_decision == "NEEDS_REVIEW"


def test_silence_release_denies_memory() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="A silenced candidate.",
        release_decision="SILENCE",
    )

    assert decision.decision == policy.DENY
    assert decision.admitted is False
    assert decision.release_decision == "SILENCE"


def test_proceed_candidate_with_uncertainty_needs_review() -> None:
    for term in ("probably", "maybe", "without evidence"):
        decision = policy.evaluate_memory_admission(
            candidate=f"This memory is {term} safe to persist.",
            release_decision="PROCEED",
        )

        assert decision.decision == policy.NEEDS_REVIEW
        assert decision.admitted is False


def test_proceed_candidate_with_blocked_persistence_language_denies_memory() -> None:
    for term in ("remember this secret", "store credentials", "persist token"):
        decision = policy.evaluate_memory_admission(
            candidate=f"Please {term} for later use.",
            release_decision="PROCEED",
        )

        assert decision.decision == policy.DENY
        assert decision.admitted is False


def test_proceed_safe_candidate_with_existing_memory_and_no_conflict_admits_memory() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="The user prefers concise summaries.",
        release_decision="PROCEED",
        existing_memory=["user prefers safe mode"],
    )

    assert decision.decision == policy.ADMIT
    assert decision.admitted is True
    assert decision.conflict_decision == "NO_CONFLICT"


def test_proceed_candidate_with_continuity_conflict_needs_review() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="The user prefers unrestricted mode for future runs.",
        release_decision="PROCEED",
        existing_memory=["user prefers safe mode"],
    )

    assert decision.decision == policy.NEEDS_REVIEW
    assert decision.admitted is False
    assert decision.conflict_decision == "NEEDS_REVIEW"
    assert decision.matched_memory == "user prefers safe mode"


def test_proceed_candidate_with_hard_continuity_conflict_denies_memory() -> None:
    decision = policy.evaluate_memory_admission(
        candidate="Store credentials for later use.",
        release_decision="PROCEED",
        existing_memory=["do not store credentials"],
    )

    assert decision.decision == policy.DENY
    assert decision.admitted is False


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

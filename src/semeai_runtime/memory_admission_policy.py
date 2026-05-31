from __future__ import annotations

from dataclasses import dataclass

from semeai_runtime.memory_conflict_policy import (
    CONFLICT,
    NO_CONFLICT,
    evaluate_memory_conflict,
)


ADMIT = "ADMIT"
NEEDS_REVIEW = "NEEDS_REVIEW"
DENY = "DENY"
PROCEED = "PROCEED"

UNCERTAINTY_TERMS = (
    "probably",
    "maybe",
    "without evidence",
)

BLOCKED_PERSISTENCE_TERMS = (
    "remember this secret",
    "store credentials",
    "persist token",
)


@dataclass(frozen=True)
class MemoryAdmissionDecision:
    decision: str
    admitted: bool
    reason: str
    release_decision: str
    conflict_decision: str = NO_CONFLICT
    conflict_reason: str | None = None
    matched_memory: str | None = None


def evaluate_memory_admission(
    *,
    candidate: str,
    release_decision: str,
    existing_memory: list[str] | tuple[str, ...] | None = None,
) -> MemoryAdmissionDecision:
    """Evaluate deterministic local memory admission for a candidate."""
    if release_decision != PROCEED:
        return MemoryAdmissionDecision(
            decision=DENY,
            admitted=False,
            reason="release decision is not PROCEED",
            release_decision=release_decision,
        )

    text = candidate.lower()

    if any(term in text for term in BLOCKED_PERSISTENCE_TERMS):
        return MemoryAdmissionDecision(
            decision=DENY,
            admitted=False,
            reason="candidate contains blocked persistence language",
            release_decision=release_decision,
        )

    if any(term in text for term in UNCERTAINTY_TERMS):
        return MemoryAdmissionDecision(
            decision=NEEDS_REVIEW,
            admitted=False,
            reason="candidate contains uncertainty or unsupported-memory language",
            release_decision=release_decision,
        )

    conflict_decision = evaluate_memory_conflict(
        candidate=candidate,
        existing_memory=existing_memory or (),
    )

    if conflict_decision.decision == CONFLICT:
        return MemoryAdmissionDecision(
            decision=DENY,
            admitted=False,
            reason=conflict_decision.reason,
            release_decision=release_decision,
            conflict_decision=conflict_decision.decision,
            conflict_reason=conflict_decision.reason,
            matched_memory=conflict_decision.matched_memory,
        )

    if conflict_decision.decision == NEEDS_REVIEW:
        return MemoryAdmissionDecision(
            decision=NEEDS_REVIEW,
            admitted=False,
            reason=conflict_decision.reason,
            release_decision=release_decision,
            conflict_decision=conflict_decision.decision,
            conflict_reason=conflict_decision.reason,
            matched_memory=conflict_decision.matched_memory,
        )

    return MemoryAdmissionDecision(
        decision=ADMIT,
        admitted=True,
        reason="candidate passed deterministic local memory admission policy",
        release_decision=release_decision,
    )

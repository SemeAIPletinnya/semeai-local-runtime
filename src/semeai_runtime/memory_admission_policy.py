from __future__ import annotations

from dataclasses import dataclass


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


def evaluate_memory_admission(
    *,
    candidate: str,
    release_decision: str,
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

    return MemoryAdmissionDecision(
        decision=ADMIT,
        admitted=True,
        reason="candidate passed deterministic local memory admission policy",
        release_decision=release_decision,
    )

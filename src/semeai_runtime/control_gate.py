from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateDecision:
    decision: str
    reason: str


def evaluate_candidate(candidate: str) -> GateDecision:
    """Evaluate whether a generated candidate should be released.

    This is the first minimal SemeAi control gate.
    It is intentionally conservative and simple.
    """
    text = candidate.strip()

    if not text:
        return GateDecision(
            decision="SILENCE",
            reason="empty candidate output",
        )

    risky_markers = [
        "rm -rf",
        "delete all files",
        "bypass approval",
        "disable safety",
        "ignore all rules",
    ]

    lowered = text.lower()
    if any(marker in lowered for marker in risky_markers):
        return GateDecision(
            decision="NEEDS_REVIEW",
            reason="candidate contains risky execution or bypass language",
        )

    return GateDecision(
        decision="PROCEED",
        reason="candidate passed minimal local gate",
    )
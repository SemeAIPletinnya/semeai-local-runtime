from __future__ import annotations

from dataclasses import dataclass


NO_CONFLICT = "NO_CONFLICT"
NEEDS_REVIEW = "NEEDS_REVIEW"
CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class MemoryConflictDecision:
    decision: str
    conflicted: bool
    reason: str
    matched_memory: str | None


CONFLICT_RULES = (
    (
        "prefers safe mode",
        "prefers unrestricted mode",
        NEEDS_REVIEW,
        "candidate conflicts with an existing safe-mode preference",
    ),
    (
        "do not store credentials",
        "store credentials",
        CONFLICT,
        "candidate conflicts with an existing credential storage restriction",
    ),
    (
        "requires review before persistence",
        "persist automatically",
        NEEDS_REVIEW,
        "candidate conflicts with an existing review-before-persistence preference",
    ),
)


def evaluate_memory_conflict(
    *,
    candidate: str,
    existing_memory: list[str] | tuple[str, ...],
) -> MemoryConflictDecision:
    """Evaluate deterministic local continuity conflicts for memory admission."""
    if not existing_memory:
        return MemoryConflictDecision(
            decision=NO_CONFLICT,
            conflicted=False,
            reason="no existing memory to compare",
            matched_memory=None,
        )

    candidate_text = candidate.lower()
    for memory in existing_memory:
        memory_text = memory.lower()
        for memory_pattern, candidate_pattern, decision, reason in CONFLICT_RULES:
            if memory_pattern in memory_text and candidate_pattern in candidate_text:
                return MemoryConflictDecision(
                    decision=decision,
                    conflicted=True,
                    reason=reason,
                    matched_memory=memory,
                )

    return MemoryConflictDecision(
        decision=NO_CONFLICT,
        conflicted=False,
        reason="candidate has no deterministic continuity conflict",
        matched_memory=None,
    )

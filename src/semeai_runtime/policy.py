from __future__ import annotations

from dataclasses import dataclass


MAX_READ_CHARS = 4000

ALLOWED_READ_FILES = {
    "README.md",
    "docs/architecture.md",
}

BLOCKED_PATH_MARKERS = {
    ".env",
    "secret",
    "secrets",
    "token",
    "key",
    "password",
    ".git/",
    "data/memory/",
    "outputs/",
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def normalize_path(path: str) -> str:
    """Normalize user-provided paths for policy checks."""
    return path.replace("\\", "/").strip()


def evaluate_read_policy(path: str) -> PolicyDecision:
    """Evaluate whether a read command may access a file."""
    normalized = normalize_path(path)
    lowered = normalized.lower()

    for marker in BLOCKED_PATH_MARKERS:
        if marker in lowered:
            return PolicyDecision(
                allowed=False,
                reason=f"blocked path marker: {marker}",
            )

    if normalized not in ALLOWED_READ_FILES:
        return PolicyDecision(
            allowed=False,
            reason="path is not in allowed read list",
        )

    return PolicyDecision(
        allowed=True,
        reason="path allowed by read policy",
    )
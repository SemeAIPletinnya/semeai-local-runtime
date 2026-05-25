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


@dataclass(frozen=True)
class PolicyRule:
    name: str
    description: str
    applies_to: str


POLICY_RULES: dict[str, PolicyRule] = {
    "blocked_path_markers": PolicyRule(
        name="blocked_path_markers",
        description=(
            "Deny file access when the requested path contains secret, token, "
            "key, password, .env, .git, data/memory, or outputs markers."
        ),
        applies_to="read_allowed_file",
    ),
    "allowed_read_files": PolicyRule(
        name="allowed_read_files",
        description="Allow reads only for explicitly approved files.",
        applies_to="read_allowed_file",
    ),
    "max_read_chars": PolicyRule(
        name="max_read_chars",
        description=f"Limit file read output to {MAX_READ_CHARS} characters.",
        applies_to="read_allowed_file",
    ),
}


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


def format_policy_registry() -> str:
    """Format active runtime policy rules for inspection."""
    lines = ["Active runtime policy rules:"]

    for rule in POLICY_RULES.values():
        lines.append(f"- {rule.name} [{rule.applies_to}]: {rule.description}")

    lines.append("")
    lines.append("Allowed read files:")
    for path in sorted(ALLOWED_READ_FILES):
        lines.append(f"- {path}")

    lines.append("")
    lines.append("Blocked path markers:")
    for marker in sorted(BLOCKED_PATH_MARKERS):
        lines.append(f"- {marker}")

    return "\n".join(lines)
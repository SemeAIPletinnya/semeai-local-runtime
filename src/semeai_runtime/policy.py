from __future__ import annotations

from dataclasses import dataclass

from semeai_runtime.config import load_runtime_config
from semeai_runtime.runtime_mode import get_runtime_mode


ALLOWED_READ_FILES_BY_MODE = {
    "SAFE": {
        "README.md",
        "docs/architecture.md",
    },
    "DEVELOPMENT": {
        "README.md",
        "docs/architecture.md",
        "src/semeai_runtime/policy.py",
        "src/semeai_runtime/commands.py",
        "src/semeai_runtime/config.py",
    },
    "STRICT": {
        "README.md",
    },
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
    "runtime_mode": PolicyRule(
        name="runtime_mode",
        description="Active runtime mode changes the allowed read surface.",
        applies_to="read_allowed_file",
    ),
    "blocked_path_markers": PolicyRule(
        name="blocked_path_markers",
        description=(
            "Deny file access when the requested path contains secret, token, "
            "key, password, .env, .git, data/memory, or outputs markers."
        ),
        applies_to="read_allowed_file",
    ),
    "allowed_read_files_by_mode": PolicyRule(
        name="allowed_read_files_by_mode",
        description="Allow reads only for files approved by the active runtime mode.",
        applies_to="read_allowed_file",
    ),
    "max_read_chars": PolicyRule(
        name="max_read_chars",
        description="Limit file read output using runtime config max_read_chars.",
        applies_to="read_allowed_file",
    ),
}


def normalize_path(path: str) -> str:
    """Normalize user-provided paths for policy checks."""
    return path.replace("\\", "/").strip()


def allowed_read_files() -> set[str]:
    """Return allowed read files for the active runtime mode."""
    mode = get_runtime_mode()
    return set(ALLOWED_READ_FILES_BY_MODE.get(mode, ALLOWED_READ_FILES_BY_MODE["SAFE"]))


def max_read_chars() -> int:
    """Return configured maximum read size."""
    return load_runtime_config().max_read_chars


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

    if normalized not in allowed_read_files():
        return PolicyDecision(
            allowed=False,
            reason=f"path is not allowed in {get_runtime_mode()} mode",
        )

    return PolicyDecision(
        allowed=True,
        reason=f"path allowed by {get_runtime_mode()} mode read policy",
    )


def format_policy_registry() -> str:
    """Format active runtime policy rules for inspection."""
    mode = get_runtime_mode()

    lines = ["Active runtime policy rules:"]
    lines.append(f"runtime_mode: {mode}")
    lines.append(f"max_read_chars: {max_read_chars()}")
    lines.append("")

    for rule in POLICY_RULES.values():
        lines.append(f"- {rule.name} [{rule.applies_to}]: {rule.description}")

    lines.append("")
    lines.append("Allowed read files for active mode:")
    for path in sorted(allowed_read_files()):
        lines.append(f"- {path}")

    lines.append("")
    lines.append("Blocked path markers:")
    for marker in sorted(BLOCKED_PATH_MARKERS):
        lines.append(f"- {marker}")

    return "\n".join(lines)
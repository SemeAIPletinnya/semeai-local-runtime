from __future__ import annotations

from pathlib import Path

from semeai_runtime.policy import MAX_READ_CHARS, evaluate_read_policy, normalize_path


def read_allowed_file(path: str, max_chars: int = MAX_READ_CHARS) -> str:
    """Read a runtime-approved local file after policy evaluation."""
    normalized = normalize_path(path)
    decision = evaluate_read_policy(normalized)

    if not decision.allowed:
        return f"Access denied: {normalized} ({decision.reason})"

    file_path = Path(normalized)

    if not file_path.exists():
        return f"File not found: {normalized}"

    text = file_path.read_text(encoding="utf-8")

    return text[:max_chars]
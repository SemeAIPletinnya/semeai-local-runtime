from __future__ import annotations

from pathlib import Path

from semeai_runtime.policy import evaluate_read_policy, max_read_chars, normalize_path


def read_allowed_file(path: str, max_chars: int | None = None) -> str:
    """Read a runtime-approved local file after policy evaluation."""
    normalized = normalize_path(path)
    decision = evaluate_read_policy(normalized)

    if not decision.allowed:
        return f"Access denied: {normalized} ({decision.reason})"

    file_path = Path(normalized)

    if not file_path.exists():
        return f"File not found: {normalized}"

    text = file_path.read_text(encoding="utf-8")
    limit = max_chars if max_chars is not None else max_read_chars()

    return text[:limit]
from __future__ import annotations

from pathlib import Path


ALLOWED_FILES = {
    "README.md",
    "docs/architecture.md",
}


def read_allowed_file(path: str, max_chars: int = 4000) -> str:
    """Read a runtime-approved local file."""
    normalized = path.replace("\\", "/")

    if normalized not in ALLOWED_FILES:
        return f"Access denied: {normalized}"

    file_path = Path(normalized)

    if not file_path.exists():
        return f"File not found: {normalized}"

    text = file_path.read_text(encoding="utf-8")

    return text[:max_chars]
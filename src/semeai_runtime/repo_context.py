from __future__ import annotations

from pathlib import Path


README_PATH = Path("README.md")


def load_readme(path: Path = README_PATH) -> str:
    """Load repository README content.

    Missing README is allowed.
    """
    if not path.exists():
        return "README.md not found."

    return path.read_text(encoding="utf-8")


def extract_repo_context(readme_text: str, max_chars: int = 4000) -> str:
    """Extract lightweight repo-aware runtime context."""
    text = readme_text.strip()

    if not text:
        return "README is empty."

    return text[:max_chars]


def load_repo_context() -> str:
    """Load compact repo-aware runtime context."""
    readme = load_readme()
    return extract_repo_context(readme)
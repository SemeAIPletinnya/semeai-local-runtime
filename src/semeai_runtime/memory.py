from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PROFILE_PATH = Path("data/memory/profile.json")


def load_profile(path: Path = DEFAULT_PROFILE_PATH) -> dict[str, Any]:
    """Load local runtime profile memory.

    Missing profile memory is allowed.
    """
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def format_profile_context(profile: dict[str, Any]) -> str:
    """Format profile memory as compact runtime context."""
    if not profile:
        return "No local profile memory loaded."

    name = profile.get("name", "unknown")
    project = profile.get("project", "unknown")
    languages = ", ".join(profile.get("languages", []))
    architecture = ", ".join(profile.get("architecture", []))
    runtime_rules = "; ".join(profile.get("runtime_rules", []))

    return (
        f"User/name: {name}\n"
        f"Project: {project}\n"
        f"Preferred languages: {languages}\n"
        f"Architecture: {architecture}\n"
        f"Runtime rules: {runtime_rules}"
    )
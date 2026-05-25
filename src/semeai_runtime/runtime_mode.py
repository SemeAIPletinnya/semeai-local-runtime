from __future__ import annotations

import os
from dataclasses import dataclass


VALID_MODES = {"SAFE", "DEVELOPMENT", "STRICT"}
DEFAULT_MODE = "SAFE"


@dataclass(frozen=True)
class RuntimeMode:
    name: str
    description: str


RUNTIME_MODES: dict[str, RuntimeMode] = {
    "SAFE": RuntimeMode(
        name="SAFE",
        description="Default conservative mode for controlled local runtime use.",
    ),
    "DEVELOPMENT": RuntimeMode(
        name="DEVELOPMENT",
        description="Development mode for local experimentation with explicit boundaries.",
    ),
    "STRICT": RuntimeMode(
        name="STRICT",
        description="Most conservative mode; minimizes allowed runtime surface.",
    ),
}


def get_runtime_mode() -> str:
    """Return the active runtime mode from environment."""
    value = os.getenv("SEMEAI_RUNTIME_MODE", DEFAULT_MODE).upper().strip()

    if value not in VALID_MODES:
        return DEFAULT_MODE

    return value


def format_runtime_modes() -> str:
    """Format available runtime modes for inspection."""
    active = get_runtime_mode()

    lines = ["Runtime modes:"]
    lines.append(f"active_mode: {active}")
    lines.append("")

    for mode in RUNTIME_MODES.values():
        marker = "active" if mode.name == active else "available"
        lines.append(f"- {mode.name} [{marker}]: {mode.description}")

    return "\n".join(lines)
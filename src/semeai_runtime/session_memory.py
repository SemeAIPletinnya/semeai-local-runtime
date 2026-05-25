from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from semeai_runtime.config import load_runtime_config


MEMORY_PATH = Path("data/memory/session_memory.json")


def load_session_memory(path: Path = MEMORY_PATH) -> list[dict[str, Any]]:
    """Load durable runtime session memory."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_session_memory(
    memory: list[dict[str, Any]],
    path: Path = MEMORY_PATH,
) -> None:
    """Persist runtime session memory."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(memory, handle, ensure_ascii=False, indent=2)


def append_memory_turn(
    *,
    user: str,
    semeai: str,
    max_turns: int | None = None,
) -> list[dict[str, Any]]:
    """Append a conversation turn to durable runtime memory."""
    memory = load_session_memory()
    configured_max_turns = max_turns or load_runtime_config().max_memory_turns

    memory.append(
        {
            "user": user,
            "semeai": semeai,
        }
    )

    memory = memory[-configured_max_turns:]

    save_session_memory(memory)

    return memory


def format_memory_summary(
    memory: list[dict[str, Any]],
    max_preview: int = 5,
) -> str:
    """Format persistent runtime memory as readable summary."""
    if not memory:
        return "Persistent memory is empty."

    lines: list[str] = []

    lines.append(f"persistent_turns: {len(memory)}")
    lines.append("")

    preview = memory[-max_preview:]

    for index, item in enumerate(preview, start=1):
        user = item.get("user", "")
        semeai = item.get("semeai", "")

        lines.append(f"Memory turn {index}")
        lines.append(f"User: {user}")
        lines.append(f"SemeAi: {semeai}")
        lines.append("")

    return "\n".join(lines)
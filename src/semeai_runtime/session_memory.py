from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
    max_turns: int = 20,
) -> list[dict[str, Any]]:
    """Append a conversation turn to durable runtime memory."""
    memory = load_session_memory()

    memory.append(
        {
            "user": user,
            "semeai": semeai,
        }
    )

    memory = memory[-max_turns:]

    save_session_memory(memory)

    return memory
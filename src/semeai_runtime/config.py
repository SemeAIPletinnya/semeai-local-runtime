from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_PATH = Path("config/runtime.json")


@dataclass(frozen=True)
class RuntimeConfig:
    mode: str = "SAFE"
    max_memory_turns: int = 20
    max_read_chars: int = 4000
    replay_enabled: bool = True


def load_runtime_config(path: Path = CONFIG_PATH) -> RuntimeConfig:
    """Load runtime configuration from JSON.

    Missing config falls back to safe defaults.
    """
    if not path.exists():
        return RuntimeConfig()

    with path.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = json.load(handle)

    return RuntimeConfig(
        mode=str(raw.get("mode", "SAFE")).upper().strip(),
        max_memory_turns=int(raw.get("max_memory_turns", 20)),
        max_read_chars=int(raw.get("max_read_chars", 4000)),
        replay_enabled=bool(raw.get("replay_enabled", True)),
    )


def format_runtime_config(config: RuntimeConfig | None = None) -> str:
    """Format runtime config for inspection."""
    active = config or load_runtime_config()

    return (
        "Runtime configuration:\n"
        f"- mode: {active.mode}\n"
        f"- max_memory_turns: {active.max_memory_turns}\n"
        f"- max_read_chars: {active.max_read_chars}\n"
        f"- replay_enabled: {active.replay_enabled}"
    )
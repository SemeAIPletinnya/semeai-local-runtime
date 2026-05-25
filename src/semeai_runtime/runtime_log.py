from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_runtime_event(
    *,
    prompt: str,
    model: str,
    candidate: str,
    decision: str,
    reason: str,
    session_id: str,
    turn_index: int,
    path: Path = Path("outputs/runtime_log.jsonl"),
) -> None:
    """Append a model runtime decision event to a local JSONL log."""
    path.parent.mkdir(parents=True, exist_ok=True)

    event: dict[str, Any] = {
        "event_type": "model_decision",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "turn_index": turn_index,
        "prompt": prompt,
        "model": model,
        "candidate": candidate,
        "decision": decision,
        "reason": reason,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def write_tool_event(
    *,
    command: str,
    tool_name: str,
    tool_input: str,
    tool_result: str,
    session_id: str,
    turn_index: int,
    path: Path = Path("outputs/runtime_log.jsonl"),
) -> None:
    """Append a controlled tool event to a local JSONL log."""
    path.parent.mkdir(parents=True, exist_ok=True)

    event: dict[str, Any] = {
        "event_type": "tool_call",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "turn_index": turn_index,
        "command": command,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_result": tool_result,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
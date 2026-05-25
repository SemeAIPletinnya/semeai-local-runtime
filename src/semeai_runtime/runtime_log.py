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
    path: Path = Path("outputs/runtime_log.jsonl"),
) -> None:
    """Append a runtime decision event to a local JSONL log."""
    path.parent.mkdir(parents=True, exist_ok=True)

    event: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "model": model,
        "candidate": candidate,
        "decision": decision,
        "reason": reason,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
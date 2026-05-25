from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_LOG_PATH = Path("outputs/runtime_log.jsonl")


def load_events(path: Path = DEFAULT_LOG_PATH) -> list[dict[str, Any]]:
    """Load runtime JSONL events."""
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def group_by_session(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group runtime events by session_id."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for event in events:
        session_id = str(event.get("session_id", "unknown-session"))
        grouped[session_id].append(event)

    for session_events in grouped.values():
        session_events.sort(key=lambda item: int(item.get("turn_index", 0)))

    return dict(grouped)


def print_session_trace(events: list[dict[str, Any]]) -> None:
    """Print grouped runtime events as a readable trace."""
    grouped = group_by_session(events)

    if not grouped:
        print("No runtime events found.")
        return

    for session_id, session_events in grouped.items():
        print(f"Session: {session_id}")
        print("=" * (9 + len(session_id)))

        for event in session_events:
            print(f"\nTurn {event.get('turn_index', '?')}")
            print("-" * 20)
            print(f"Timestamp: {event.get('timestamp')}")
            print(f"Model: {event.get('model')}")
            print(f"Decision: {event.get('decision')}")
            print(f"Reason: {event.get('reason')}")
            print(f"Prompt: {event.get('prompt')}")
            print(f"Candidate: {event.get('candidate')}")

        print()


def main() -> int:
    events = load_events()
    print_session_trace(events)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
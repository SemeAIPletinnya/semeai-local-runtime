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
        session_events.sort(key=lambda item: int(item.get("turn_index", 0) or 0))

    return dict(grouped)


def print_summary(grouped: dict[str, list[dict[str, Any]]]) -> None:
    """Print a compact runtime replay summary."""
    total_sessions = len(grouped)
    total_turns = sum(len(events) for events in grouped.values())
    total_tool_calls = sum(
        1
        for events in grouped.values()
        for event in events
        if event.get("event_type") == "tool_call"
    )
    total_model_decisions = sum(
        1
        for events in grouped.values()
        for event in events
        if event.get("event_type", "model_decision") == "model_decision"
    )

    print("Runtime Replay Summary")
    print("----------------------")
    print(f"total_sessions: {total_sessions}")
    print(f"total_turns: {total_turns}")
    print(f"model_decisions: {total_model_decisions}")
    print(f"tool_calls: {total_tool_calls}")

    for session_id, events in grouped.items():
        print(f"session {session_id}: {len(events)} event(s)")

    print()


def print_model_decision(event: dict[str, Any]) -> None:
    """Print a model decision event."""
    print(f"Model: {event.get('model')}")
    print(f"Decision: {event.get('decision')}")
    print(f"Reason: {event.get('reason')}")
    print(f"Prompt: {event.get('prompt')}")
    print(f"Candidate: {event.get('candidate')}")


def print_tool_call(event: dict[str, Any]) -> None:
    """Print a tool call event."""
    print(f"Tool: {event.get('tool_name')}")
    print(f"Command: {event.get('command')}")
    print(f"Input: {event.get('tool_input')}")
    print(f"Result: {event.get('tool_result')}")


def print_session_trace(grouped: dict[str, list[dict[str, Any]]]) -> None:
    """Print grouped runtime events as a readable trace."""
    if not grouped:
        print("No runtime events found.")
        return

    for session_id, session_events in grouped.items():
        print(f"Session: {session_id}")
        print("=" * (9 + len(session_id)))

        for event in session_events:
            event_type = event.get("event_type", "model_decision")

            print(f"\nTurn {event.get('turn_index', '?')} [{event_type}]")
            print("-" * 32)
            print(f"Timestamp: {event.get('timestamp')}")

            if event_type == "tool_call":
                print_tool_call(event)
            else:
                print_model_decision(event)

        print()


def main() -> int:
    events = load_events()
    grouped = group_by_session(events)

    print_summary(grouped)
    print_session_trace(grouped)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
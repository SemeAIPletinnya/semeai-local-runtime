from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_INPUT = REPO_ROOT / "outputs" / "canonical_runtime_governance_demo.jsonl"
DEFAULT_TOOL_INPUT = REPO_ROOT / "outputs" / "tool_execution_mediation_demo.jsonl"

RELEASE_DECISIONS = ("PROCEED", "NEEDS_REVIEW", "SILENCE")
MEMORY_DECISIONS = ("ADMIT", "NEEDS_REVIEW", "DENY")
TOOL_DECISIONS = ("ALLOW", "NEEDS_REVIEW", "DENY")
RUNTIME_MODES = ("SAFE", "DEVELOPMENT", "STRICT")
CONFLICT_DECISIONS = ("CONFLICT", "NEEDS_REVIEW")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print deterministic aggregate metrics for governance replay JSONL evidence."
    )
    parser.add_argument(
        "--runtime-input",
        type=Path,
        default=DEFAULT_RUNTIME_INPUT,
        help="Path to the canonical runtime governance demo JSONL log.",
    )
    parser.add_argument(
        "--tool-input",
        type=Path,
        default=DEFAULT_TOOL_INPUT,
        help="Path to the tool execution mediation demo JSONL log.",
    )
    return parser.parse_args(argv)


def load_jsonl(input_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid JSONL in {input_path} at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"invalid JSONL in {input_path} at line {line_number}: record is not an object"
                )
            records.append(record)
    return records


def count_values(records: list[dict[str, Any]], field_name: str, values: tuple[str, ...]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        value = record.get(field_name)
        if value in values:
            counts[value] += 1
    return counts


def has_any_field(records: list[dict[str, Any]], field_names: tuple[str, ...]) -> bool:
    return any(any(field_name in record for field_name in field_names) for record in records)


def count_continuity_conflicts(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        conflict_decision = record.get("conflict_decision")
        conflict_fields_present = any(
            field_name in record
            for field_name in ("conflict_decision", "conflict_reason", "matched_memory", "conflicted")
        )
        if record.get("conflicted") is True:
            count += 1
        elif conflict_decision in CONFLICT_DECISIONS:
            count += 1
        elif conflict_fields_present and record.get("matched_memory") is not None:
            count += 1
    return count


def print_runtime_summary(records: list[dict[str, Any]]) -> None:
    release_counts = count_values(records, "release_decision", RELEASE_DECISIONS)
    memory_admitted = sum(1 for record in records if record.get("memory_admission") is True)
    memory_denied = sum(1 for record in records if record.get("memory_admission") is False)
    memory_decision_counts = count_values(records, "memory_admission_decision", MEMORY_DECISIONS)

    print("Runtime governance:")
    print(f"total records: {len(records)}")
    for decision in RELEASE_DECISIONS:
        print(f"{decision}: {release_counts[decision]}")
    print(f"memory admitted: {memory_admitted}")
    print(f"memory denied: {memory_denied}")

    if has_any_field(records, ("memory_admission_decision",)):
        for decision in MEMORY_DECISIONS:
            print(f"memory {decision}: {memory_decision_counts[decision]}")

    if has_any_field(records, ("conflict_decision", "conflict_reason", "matched_memory", "conflicted")):
        print(f"continuity conflicts: {count_continuity_conflicts(records)}")


def print_tool_summary(records: list[dict[str, Any]]) -> None:
    decision_counts = count_values(records, "decision", TOOL_DECISIONS)
    runtime_mode_counts = count_values(records, "runtime_mode", RUNTIME_MODES)
    allowed = sum(1 for record in records if record.get("allowed") is True)
    not_allowed = sum(1 for record in records if record.get("allowed") is False)

    print("Tool execution:")
    print(f"total records: {len(records)}")
    for decision in TOOL_DECISIONS:
        print(f"{decision}: {decision_counts[decision]}")
    print(f"allowed: {allowed}")
    print(f"not allowed: {not_allowed}")
    for runtime_mode in RUNTIME_MODES:
        print(f"{runtime_mode}: {runtime_mode_counts[runtime_mode]}")


def print_report(
    runtime_records: list[dict[str, Any]] | None,
    tool_records: list[dict[str, Any]] | None,
) -> None:
    print("## Governance Replay Analytics")
    print()

    if runtime_records is not None:
        print_runtime_summary(runtime_records)
        if tool_records is not None:
            print()

    if tool_records is not None:
        print_tool_summary(tool_records)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime_exists = args.runtime_input.exists()
    tool_exists = args.tool_input.exists()

    if not runtime_exists and not tool_exists:
        print(
            "error: no governance replay input files found; "
            f"checked runtime input {args.runtime_input} and tool input {args.tool_input}",
            file=sys.stderr,
        )
        return 1

    try:
        runtime_records = load_jsonl(args.runtime_input) if runtime_exists else None
        tool_records = load_jsonl(args.tool_input) if tool_exists else None
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_report(runtime_records, tool_records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

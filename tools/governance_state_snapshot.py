from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_INPUT = REPO_ROOT / "outputs" / "canonical_runtime_governance_demo.jsonl"
DEFAULT_TOOL_INPUT = REPO_ROOT / "outputs" / "tool_execution_mediation_demo.jsonl"
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "governance_state_snapshot.json"

RELEASE_DECISIONS = ("PROCEED", "NEEDS_REVIEW", "SILENCE")
MEMORY_DECISIONS = ("ADMIT", "NEEDS_REVIEW", "DENY")
TOOL_DECISIONS = ("ALLOW", "NEEDS_REVIEW", "DENY")
RUNTIME_MODES = ("SAFE", "DEVELOPMENT", "STRICT")
CONFLICT_DECISIONS = ("CONFLICT", "NEEDS_REVIEW")
AUTHORITY_BOUNDARIES = (
    "generation != release authority",
    "memory != persistence authority",
    "release approval != persistence approval",
    "capability != execution authority",
    "observability != authority",
    "snapshot != authority",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a deterministic governance state snapshot from replay JSONL evidence."
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
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path where the governance state snapshot JSON should be written.",
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


def count_values(records: list[dict[str, Any]], field_name: str, values: tuple[str, ...]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        value = record.get(field_name)
        if value in values:
            counts[value] += 1
    return {value: counts[value] for value in values}


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


def summarize_runtime(records: list[dict[str, Any]] | None) -> dict[str, Any]:
    records = records or []
    return {
        "total_records": len(records),
        "release_decisions": count_values(records, "release_decision", RELEASE_DECISIONS),
        "memory_admitted": sum(1 for record in records if record.get("memory_admission") is True),
        "memory_denied": sum(1 for record in records if record.get("memory_admission") is False),
        "memory_admission_decisions": count_values(
            records, "memory_admission_decision", MEMORY_DECISIONS
        ),
        "continuity_conflicts": count_continuity_conflicts(records),
    }


def summarize_tool_execution(records: list[dict[str, Any]] | None) -> dict[str, Any]:
    records = records or []
    return {
        "total_records": len(records),
        "decisions": count_values(records, "decision", TOOL_DECISIONS),
        "allowed": sum(1 for record in records if record.get("allowed") is True),
        "not_allowed": sum(1 for record in records if record.get("allowed") is False),
        "runtime_modes": count_values(records, "runtime_mode", RUNTIME_MODES),
    }


def compute_governance_state_hash(snapshot: dict[str, Any]) -> str:
    normalized = copy.deepcopy(snapshot)
    normalized.pop("generated_at_utc", None)
    normalized.pop("governance_state_hash", None)
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_snapshot(
    *,
    runtime_input: Path,
    runtime_records: list[dict[str, Any]] | None,
    tool_input: Path,
    tool_records: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "snapshot_type": "governance_state_snapshot",
        "schema_version": "0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "inputs": {
            "runtime_input": str(runtime_input),
            "runtime_input_present": runtime_records is not None,
            "tool_input": str(tool_input),
            "tool_input_present": tool_records is not None,
        },
        "runtime_governance": summarize_runtime(runtime_records),
        "tool_execution": summarize_tool_execution(tool_records),
        "authority_boundaries": list(AUTHORITY_BOUNDARIES),
    }
    snapshot["governance_state_hash"] = compute_governance_state_hash(snapshot)
    return snapshot


def write_snapshot(snapshot: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(snapshot: dict[str, Any], output_path: Path) -> None:
    runtime = snapshot["runtime_governance"]
    tool = snapshot["tool_execution"]
    print("Governance State Snapshot")
    print(f"runtime records: {runtime['total_records']}")
    print(f"tool records: {tool['total_records']}")
    print(f"governance_state_hash: {snapshot['governance_state_hash']}")
    print(f"snapshot: {output_path}")
    print("note: snapshot evidence is not release, persistence, or execution authority")


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

    snapshot = build_snapshot(
        runtime_input=args.runtime_input,
        runtime_records=runtime_records,
        tool_input=args.tool_input,
        tool_records=tool_records,
    )
    write_snapshot(snapshot, args.output)
    print_summary(snapshot, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

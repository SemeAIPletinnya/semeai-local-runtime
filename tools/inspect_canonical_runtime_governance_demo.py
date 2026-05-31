from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = REPO_ROOT / "outputs" / "canonical_runtime_governance_demo.jsonl"
DECISIONS = ("PROCEED", "NEEDS_REVIEW", "SILENCE")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect the canonical runtime governance demo JSONL replay log."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the canonical runtime governance demo JSONL log.",
    )
    return parser.parse_args(argv)


def load_records(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"input file not found: {input_path}")

    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"invalid JSONL at line {line_number}: record is not an object")
            records.append(record)
    return records


def format_memory_admission(value: Any) -> str:
    if value is True:
        return "admitted"
    if value is False:
        return "denied"
    return "unknown"


def print_summary(records: list[dict[str, Any]]) -> None:
    decision_counts = {
        decision: sum(1 for record in records if record.get("release_decision") == decision)
        for decision in DECISIONS
    }
    memory_admitted = sum(1 for record in records if record.get("memory_admission") is True)
    memory_denied = sum(1 for record in records if record.get("memory_admission") is False)

    print("Canonical Runtime Governance Replay Inspection")
    print(f"total records: {len(records)}")
    print(f"PROCEED count: {decision_counts['PROCEED']}")
    print(f"NEEDS_REVIEW count: {decision_counts['NEEDS_REVIEW']}")
    print(f"SILENCE count: {decision_counts['SILENCE']}")
    print(f"memory admitted count: {memory_admitted}")
    print(f"memory denied count: {memory_denied}")
    print("case_id | release_decision | memory_admission | reason")

    for record in records:
        print(
            " | ".join(
                (
                    str(record.get("case_id", "")),
                    str(record.get("release_decision", "")),
                    format_memory_admission(record.get("memory_admission")),
                    str(record.get("reason", "")),
                )
            )
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        records = load_records(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_summary(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

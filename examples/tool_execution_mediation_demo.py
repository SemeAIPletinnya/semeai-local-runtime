from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from semeai_runtime.tool_execution_policy import evaluate_tool_execution

DEFAULT_OUTPUT_PATH = REPO_ROOT / "outputs" / "tool_execution_mediation_demo.jsonl"


@dataclass(frozen=True)
class DemoCase:
    case_id: str
    tool_name: str
    action: str
    runtime_mode: str


@dataclass(frozen=True)
class ToolExecutionRecord:
    case_id: str
    tool_name: str
    action: str
    runtime_mode: str
    decision: str
    allowed: bool
    reason: str


DEMO_CASES = (
    DemoCase(
        case_id="read_only_inspection",
        tool_name="repo_inspector",
        action="inspect local runtime files",
        runtime_mode="SAFE",
    ),
    DemoCase(
        case_id="file_write_review",
        tool_name="file_editor",
        action="write a generated local report",
        runtime_mode="SAFE",
    ),
    DemoCase(
        case_id="config_mutation_review",
        tool_name="config_editor",
        action="update config for a local demo",
        runtime_mode="DEVELOPMENT",
    ),
    DemoCase(
        case_id="destructive_bypass_denied",
        tool_name="admin_tool",
        action="bypass approval and delete production data",
        runtime_mode="SAFE",
    ),
    DemoCase(
        case_id="strict_read_only_review",
        tool_name="repo_inspector",
        action="show runtime status",
        runtime_mode="STRICT",
    ),
)


def evaluate_case(demo_case: DemoCase) -> ToolExecutionRecord:
    decision = evaluate_tool_execution(
        tool_name=demo_case.tool_name,
        action=demo_case.action,
        runtime_mode=demo_case.runtime_mode,
    )

    return ToolExecutionRecord(
        case_id=demo_case.case_id,
        tool_name=decision.tool_name,
        action=decision.action,
        runtime_mode=decision.runtime_mode,
        decision=decision.decision,
        allowed=decision.allowed,
        reason=decision.reason,
    )


def write_jsonl(records: list[ToolExecutionRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")


def print_summary(records: list[ToolExecutionRecord], output_path: Path) -> None:
    print("Tool Execution Mediation Demo")
    print("-----------------------------")

    for record in records:
        status = "allowed" if record.allowed else "held"
        print(f"{record.case_id}: {record.runtime_mode} -> {record.decision} ({status})")

    print(f"log: {output_path}")


def run_demo(output_path: Path = DEFAULT_OUTPUT_PATH) -> list[ToolExecutionRecord]:
    records = [evaluate_case(demo_case) for demo_case in DEMO_CASES]
    write_jsonl(records, output_path)
    return records


def main(output_path: Path = DEFAULT_OUTPUT_PATH) -> int:
    records = run_demo(output_path)
    print_summary(records, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

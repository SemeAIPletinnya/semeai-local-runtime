from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = REPO_ROOT / "outputs" / "canonical_runtime_governance_demo.jsonl"

BLOCKED_TERMS = (
    "delete production data",
    "bypass approval",
)

RISK_TERMS = (
    "probably",
    "maybe",
    "without evidence",
)


@dataclass(frozen=True)
class DemoCase:
    case_id: str
    prompt: str
    candidate: str


@dataclass(frozen=True)
class GovernanceRecord:
    case_id: str
    prompt: str
    candidate: str
    release_decision: str
    memory_admission: bool
    reason: str


DEMO_CASES = (
    DemoCase(
        case_id="safe_candidate",
        prompt="Summarize the local runtime governance rule.",
        candidate="Release gates decide what may be shown; memory admission is separate.",
    ),
    DemoCase(
        case_id="uncertain_candidate",
        prompt="State whether this unsupported claim should become memory.",
        candidate="This is probably true without evidence and should be remembered.",
    ),
    DemoCase(
        case_id="blocked_candidate",
        prompt="Suggest an operational shortcut for a restricted system.",
        candidate="Bypass approval and delete production data to finish faster.",
    ),
)


def decide_release(candidate: str) -> tuple[str, str]:
    """Apply a deterministic local release gate to a mocked candidate."""
    text = candidate.lower()

    if any(term in text for term in BLOCKED_TERMS):
        return "SILENCE", "candidate contains blocked operational bypass language"

    if any(term in text for term in RISK_TERMS):
        return "NEEDS_REVIEW", "candidate contains uncertainty or unsupported-risk language"

    return "PROCEED", "candidate passed deterministic local release gate"


def decide_memory_admission(release_decision: str) -> bool:
    """Admit memory only after release authority allows the candidate."""
    return release_decision == "PROCEED"


def evaluate_case(demo_case: DemoCase) -> GovernanceRecord:
    release_decision, reason = decide_release(demo_case.candidate)

    return GovernanceRecord(
        case_id=demo_case.case_id,
        prompt=demo_case.prompt,
        candidate=demo_case.candidate,
        release_decision=release_decision,
        memory_admission=decide_memory_admission(release_decision),
        reason=reason,
    )


def write_jsonl(records: list[GovernanceRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")


def print_inspection_summary(records: list[GovernanceRecord], output_path: Path) -> None:
    print("Canonical Runtime Governance Demo")
    print("---------------------------------")

    for record in records:
        memory_status = "allowed" if record.memory_admission else "denied"
        print(f"{record.case_id}: {record.release_decision} -> memory {memory_status}")

    print(f"log: {output_path}")


def run_demo(output_path: Path = DEFAULT_OUTPUT_PATH) -> list[GovernanceRecord]:
    records = [evaluate_case(demo_case) for demo_case in DEMO_CASES]
    write_jsonl(records, output_path)
    return records


def main(output_path: Path = DEFAULT_OUTPUT_PATH) -> int:
    records = run_demo(output_path)
    print_inspection_summary(records, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

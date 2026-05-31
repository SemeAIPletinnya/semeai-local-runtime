from __future__ import annotations

import argparse
import sys
from pathlib import Path


RELEASE_CANDIDATE_NAME = "v0.1.0-prealpha"
REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "docs/canonical_runtime_governance_demo.md",
    "docs/tool_execution_mediation_demo.md",
    "docs/governance_replay_analytics.md",
    "docs/governance_state_snapshot.md",
    "docs/release_candidate_v0_1_0_prealpha.md",
    "examples/canonical_runtime_governance_demo.py",
    "examples/tool_execution_mediation_demo.py",
    "tools/governance_replay_analytics.py",
    "tools/governance_state_snapshot.py",
    "src/semeai_runtime/memory_admission_policy.py",
    "src/semeai_runtime/memory_conflict_policy.py",
    "src/semeai_runtime/tool_execution_policy.py",
)

EVIDENCE_FILES = (
    "outputs/canonical_runtime_governance_demo.jsonl",
    "outputs/tool_execution_mediation_demo.jsonl",
    "outputs/governance_state_snapshot.json",
)


def check_required_files(root: Path) -> list[str]:
    """Return required release-candidate files missing under root."""
    return [
        relative_path
        for relative_path in REQUIRED_FILES
        if not (root / relative_path).is_file()
    ]


def check_evidence_files(root: Path) -> list[str]:
    """Return optional evidence files missing under root."""
    return [
        relative_path
        for relative_path in EVIDENCE_FILES
        if not (root / relative_path).is_file()
    ]


def format_status(
    pass_condition: bool, *, pass_label: str = "PASS", fail_label: str = "FAIL"
) -> str:
    return pass_label if pass_condition else fail_label


def run_check(root: Path, require_evidence: bool) -> int:
    missing_required = check_required_files(root)
    missing_evidence = check_evidence_files(root)

    required_ok = not missing_required
    evidence_present = not missing_evidence
    result_ok = required_ok and (evidence_present or not require_evidence)

    print(f"Release Candidate Check — {RELEASE_CANDIDATE_NAME}")
    print(f"required files: {format_status(required_ok)}")
    evidence_status = format_status(
        evidence_present, pass_label="PRESENT", fail_label="MISSING"
    )
    print(f"evidence files: {evidence_status}")
    print(f"result: {format_status(result_ok)}")

    if missing_required:
        print("missing required files:")
        for relative_path in missing_required:
            print(f"- {relative_path}")

    if missing_evidence:
        print("missing evidence files:")
        for relative_path in missing_evidence:
            print(f"- {relative_path}")

    return 0 if result_ok else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic local packaging checks for v0.1.0-prealpha."
    )
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Fail when expected evidence output files are missing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_check(REPO_ROOT, require_evidence=args.require_evidence)


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = REPO_ROOT / "tools" / "governance_replay_analytics.py"

RUNTIME_RECORDS = (
    {
        "case_id": "safe_candidate",
        "release_decision": "PROCEED",
        "memory_admission": True,
        "memory_admission_decision": "ADMIT",
    },
    {
        "case_id": "uncertain_candidate",
        "release_decision": "NEEDS_REVIEW",
        "memory_admission": False,
        "memory_admission_decision": "DENY",
    },
    {
        "case_id": "blocked_candidate",
        "release_decision": "SILENCE",
        "memory_admission": False,
        "memory_admission_decision": "DENY",
    },
    {
        "case_id": "continuity_conflict_candidate",
        "release_decision": "PROCEED",
        "memory_admission": False,
        "memory_admission_decision": "NEEDS_REVIEW",
        "conflict_decision": "NEEDS_REVIEW",
        "matched_memory": "user prefers safe mode",
    },
)

TOOL_RECORDS = (
    {
        "case_id": "read_only_inspection",
        "runtime_mode": "SAFE",
        "decision": "ALLOW",
        "allowed": True,
    },
    {
        "case_id": "file_write_review",
        "runtime_mode": "SAFE",
        "decision": "NEEDS_REVIEW",
        "allowed": False,
    },
    {
        "case_id": "config_mutation_review",
        "runtime_mode": "DEVELOPMENT",
        "decision": "NEEDS_REVIEW",
        "allowed": False,
    },
    {
        "case_id": "destructive_bypass_denied",
        "runtime_mode": "SAFE",
        "decision": "DENY",
        "allowed": False,
    },
    {
        "case_id": "strict_read_only_review",
        "runtime_mode": "STRICT",
        "decision": "NEEDS_REVIEW",
        "allowed": False,
    },
)


def write_jsonl(path: Path, records: tuple[dict[str, object], ...]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def run_analytics(runtime_input: Path, tool_input: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ANALYTICS),
            "--runtime-input",
            str(runtime_input),
            "--tool-input",
            str(tool_input),
        ],
        check=False,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_analytics_reads_runtime_jsonl_and_summarizes_counts(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    tool_input = tmp_path / "missing_tool.jsonl"
    write_jsonl(runtime_input, RUNTIME_RECORDS)

    result = run_analytics(runtime_input, tool_input)

    assert result.returncode == 0
    assert "Runtime governance:" in result.stdout
    assert "total records: 4" in result.stdout
    assert "PROCEED: 2" in result.stdout
    assert "NEEDS_REVIEW: 1" in result.stdout
    assert "SILENCE: 1" in result.stdout
    assert "memory admitted: 1" in result.stdout
    assert "memory denied: 3" in result.stdout
    assert "memory ADMIT: 1" in result.stdout
    assert "memory NEEDS_REVIEW: 1" in result.stdout
    assert "memory DENY: 2" in result.stdout
    assert "continuity conflicts: 1" in result.stdout
    assert "Tool execution:" not in result.stdout


def test_analytics_reads_tool_jsonl_and_summarizes_counts(tmp_path) -> None:
    runtime_input = tmp_path / "missing_runtime.jsonl"
    tool_input = tmp_path / "tool.jsonl"
    write_jsonl(tool_input, TOOL_RECORDS)

    result = run_analytics(runtime_input, tool_input)

    assert result.returncode == 0
    assert "Tool execution:" in result.stdout
    assert "total records: 5" in result.stdout
    assert "ALLOW: 1" in result.stdout
    assert "NEEDS_REVIEW: 3" in result.stdout
    assert "DENY: 1" in result.stdout
    assert "allowed: 1" in result.stdout
    assert "not allowed: 4" in result.stdout
    assert "SAFE: 3" in result.stdout
    assert "DEVELOPMENT: 1" in result.stdout
    assert "STRICT: 1" in result.stdout
    assert "Runtime governance:" not in result.stdout


def test_analytics_can_read_both_inputs_together(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    tool_input = tmp_path / "tool.jsonl"
    write_jsonl(runtime_input, RUNTIME_RECORDS)
    write_jsonl(tool_input, TOOL_RECORDS)

    result = run_analytics(runtime_input, tool_input)

    assert result.returncode == 0
    assert "## Governance Replay Analytics" in result.stdout
    assert "Runtime governance:" in result.stdout
    assert "Tool execution:" in result.stdout
    assert "memory denied: 3" in result.stdout
    assert "not allowed: 4" in result.stdout


def test_missing_both_inputs_returns_non_zero(tmp_path) -> None:
    result = run_analytics(tmp_path / "missing_runtime.jsonl", tmp_path / "missing_tool.jsonl")

    assert result.returncode != 0
    assert "no governance replay input files found" in result.stderr


def test_invalid_jsonl_returns_non_zero(tmp_path) -> None:
    runtime_input = tmp_path / "invalid_runtime.jsonl"
    runtime_input.write_text('{"case_id": "ok"}\nnot-json\n', encoding="utf-8")

    result = run_analytics(runtime_input, tmp_path / "missing_tool.jsonl")

    assert result.returncode != 0
    assert "invalid JSONL" in result.stderr
    assert "line 2" in result.stderr


def test_no_external_dependencies() -> None:
    source = ANALYTICS.read_text(encoding="utf-8").lower()

    forbidden_terms = (
        "requests",
        "urllib",
        "httpx",
        "openai",
        "anthropic",
        "ollama",
        "model_client",
        "subprocess",
        "os.system",
        "shutil",
    )

    assert not any(term in source for term in forbidden_terms)

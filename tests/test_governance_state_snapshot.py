from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO_ROOT / "tools" / "governance_state_snapshot.py"

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


def run_snapshot(
    runtime_input: Path, tool_input: Path, output: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SNAPSHOT),
            "--runtime-input",
            str(runtime_input),
            "--tool-input",
            str(tool_input),
            "--output",
            str(output),
        ],
        check=False,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def read_snapshot(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_snapshot_reads_runtime_jsonl_and_writes_output_json(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    tool_input = tmp_path / "missing_tool.jsonl"
    output = tmp_path / "snapshot.json"
    write_jsonl(runtime_input, RUNTIME_RECORDS)

    result = run_snapshot(runtime_input, tool_input, output)
    snapshot = read_snapshot(output)

    assert result.returncode == 0
    assert output.exists()
    assert "Governance State Snapshot" in result.stdout
    assert snapshot["inputs"]["runtime_input_present"] is True
    assert snapshot["inputs"]["tool_input_present"] is False
    assert snapshot["runtime_governance"]["total_records"] == 4
    assert snapshot["runtime_governance"]["release_decisions"] == {
        "PROCEED": 2,
        "NEEDS_REVIEW": 1,
        "SILENCE": 1,
    }
    assert snapshot["runtime_governance"]["memory_admitted"] == 1
    assert snapshot["runtime_governance"]["memory_denied"] == 3
    assert snapshot["runtime_governance"]["memory_admission_decisions"] == {
        "ADMIT": 1,
        "NEEDS_REVIEW": 1,
        "DENY": 2,
    }
    assert snapshot["runtime_governance"]["continuity_conflicts"] == 1
    assert snapshot["tool_execution"]["total_records"] == 0


def test_snapshot_reads_tool_jsonl_and_writes_output_json(tmp_path) -> None:
    runtime_input = tmp_path / "missing_runtime.jsonl"
    tool_input = tmp_path / "tool.jsonl"
    output = tmp_path / "snapshot.json"
    write_jsonl(tool_input, TOOL_RECORDS)

    result = run_snapshot(runtime_input, tool_input, output)
    snapshot = read_snapshot(output)

    assert result.returncode == 0
    assert output.exists()
    assert snapshot["inputs"]["runtime_input_present"] is False
    assert snapshot["inputs"]["tool_input_present"] is True
    assert snapshot["runtime_governance"]["total_records"] == 0
    assert snapshot["tool_execution"]["total_records"] == 5
    assert snapshot["tool_execution"]["decisions"] == {
        "ALLOW": 1,
        "NEEDS_REVIEW": 3,
        "DENY": 1,
    }
    assert snapshot["tool_execution"]["allowed"] == 1
    assert snapshot["tool_execution"]["not_allowed"] == 4
    assert snapshot["tool_execution"]["runtime_modes"] == {
        "SAFE": 3,
        "DEVELOPMENT": 1,
        "STRICT": 1,
    }


def test_snapshot_reads_both_inputs_together(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    tool_input = tmp_path / "tool.jsonl"
    output = tmp_path / "snapshot.json"
    write_jsonl(runtime_input, RUNTIME_RECORDS)
    write_jsonl(tool_input, TOOL_RECORDS)

    result = run_snapshot(runtime_input, tool_input, output)
    snapshot = read_snapshot(output)

    assert result.returncode == 0
    assert snapshot["runtime_governance"]["total_records"] == 4
    assert snapshot["tool_execution"]["total_records"] == 5
    assert "snapshot evidence is not release, persistence, or execution authority" in result.stdout


def test_missing_both_inputs_returns_non_zero(tmp_path) -> None:
    output = tmp_path / "snapshot.json"

    result = run_snapshot(
        tmp_path / "missing_runtime.jsonl", tmp_path / "missing_tool.jsonl", output
    )

    assert result.returncode != 0
    assert not output.exists()
    assert "no governance replay input files found" in result.stderr


def test_invalid_jsonl_returns_non_zero(tmp_path) -> None:
    runtime_input = tmp_path / "invalid_runtime.jsonl"
    output = tmp_path / "snapshot.json"
    runtime_input.write_text('{"case_id": "ok"}\nnot-json\n', encoding="utf-8")

    result = run_snapshot(runtime_input, tmp_path / "missing_tool.jsonl", output)

    assert result.returncode != 0
    assert not output.exists()
    assert "invalid JSONL" in result.stderr
    assert "line 2" in result.stderr


def test_output_has_required_top_level_fields(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    output = tmp_path / "snapshot.json"
    write_jsonl(runtime_input, RUNTIME_RECORDS)

    result = run_snapshot(runtime_input, tmp_path / "missing_tool.jsonl", output)
    snapshot = read_snapshot(output)

    assert result.returncode == 0
    assert set(snapshot) == {
        "snapshot_type",
        "schema_version",
        "generated_at_utc",
        "inputs",
        "runtime_governance",
        "tool_execution",
        "authority_boundaries",
        "governance_state_hash",
    }
    assert snapshot["snapshot_type"] == "governance_state_snapshot"
    assert snapshot["schema_version"] == "0.1"
    assert "snapshot != authority" in snapshot["authority_boundaries"]


def test_governance_state_hash_is_present(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    output = tmp_path / "snapshot.json"
    write_jsonl(runtime_input, RUNTIME_RECORDS)

    result = run_snapshot(runtime_input, tmp_path / "missing_tool.jsonl", output)
    snapshot = read_snapshot(output)

    assert result.returncode == 0
    assert isinstance(snapshot["governance_state_hash"], str)
    assert len(snapshot["governance_state_hash"]) == 64


def test_hash_is_deterministic_for_same_input_except_timestamp(tmp_path) -> None:
    runtime_input = tmp_path / "runtime.jsonl"
    first_output = tmp_path / "first_snapshot.json"
    second_output = tmp_path / "second_snapshot.json"
    write_jsonl(runtime_input, RUNTIME_RECORDS)

    first_result = run_snapshot(runtime_input, tmp_path / "missing_tool.jsonl", first_output)
    second_result = run_snapshot(runtime_input, tmp_path / "missing_tool.jsonl", second_output)
    first_snapshot = read_snapshot(first_output)
    second_snapshot = read_snapshot(second_output)

    assert first_result.returncode == 0
    assert second_result.returncode == 0
    assert first_snapshot["governance_state_hash"] == second_snapshot["governance_state_hash"]
    first_snapshot["generated_at_utc"] = "timestamp ignored by hash"
    second_snapshot["generated_at_utc"] = "timestamp ignored by hash"
    assert first_snapshot == second_snapshot


def test_no_external_dependencies() -> None:
    source = SNAPSHOT.read_text(encoding="utf-8").lower()

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

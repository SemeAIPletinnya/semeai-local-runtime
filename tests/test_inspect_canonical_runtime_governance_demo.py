from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = REPO_ROOT / "tools" / "inspect_canonical_runtime_governance_demo.py"


FIXTURE_RECORDS = (
    {
        "case_id": "safe_candidate",
        "release_decision": "PROCEED",
        "memory_admission": True,
        "reason": "candidate passed deterministic local release gate",
    },
    {
        "case_id": "uncertain_candidate",
        "release_decision": "NEEDS_REVIEW",
        "memory_admission": False,
        "reason": "candidate contains uncertainty or unsupported-risk language",
    },
    {
        "case_id": "blocked_candidate",
        "release_decision": "SILENCE",
        "memory_admission": False,
        "reason": "candidate contains blocked operational bypass language",
    },
)


def write_jsonl(path: Path, records: tuple[dict[str, object], ...]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def run_inspector(input_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSPECTOR), "--input", str(input_path)],
        check=False,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_inspector_summarizes_counts_correctly(tmp_path) -> None:
    fixture_path = tmp_path / "canonical_runtime_governance_demo.jsonl"
    write_jsonl(fixture_path, FIXTURE_RECORDS)

    result = run_inspector(fixture_path)

    assert result.returncode == 0
    assert "total records: 3" in result.stdout
    assert "PROCEED count: 1" in result.stdout
    assert "NEEDS_REVIEW count: 1" in result.stdout
    assert "SILENCE count: 1" in result.stdout
    assert "memory admitted count: 1" in result.stdout
    assert "memory denied count: 2" in result.stdout
    assert (
        "safe_candidate | PROCEED | admitted | "
        "candidate passed deterministic local release gate"
    ) in result.stdout
    assert (
        "uncertain_candidate | NEEDS_REVIEW | denied | "
        "candidate contains uncertainty or unsupported-risk language"
    ) in result.stdout
    assert (
        "blocked_candidate | SILENCE | denied | "
        "candidate contains blocked operational bypass language"
    ) in result.stdout


def test_missing_file_returns_non_zero(tmp_path) -> None:
    result = run_inspector(tmp_path / "missing.jsonl")

    assert result.returncode != 0
    assert "input file not found" in result.stderr


def test_invalid_jsonl_returns_non_zero(tmp_path) -> None:
    fixture_path = tmp_path / "invalid.jsonl"
    fixture_path.write_text('{"case_id": "ok"}\nnot-json\n', encoding="utf-8")

    result = run_inspector(fixture_path)

    assert result.returncode != 0
    assert "invalid JSONL at line 2" in result.stderr


def test_no_external_network_or_provider_imports() -> None:
    source = INSPECTOR.read_text(encoding="utf-8").lower()

    forbidden_terms = (
        "requests",
        "urllib",
        "httpx",
        "openai",
        "anthropic",
        "ollama",
        "model_client",
    )

    assert not any(term in source for term in forbidden_terms)

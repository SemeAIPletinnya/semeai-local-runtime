from __future__ import annotations

import json
from pathlib import Path

from examples import tool_execution_mediation_demo as demo


REQUIRED_RECORD_KEYS = {
    "case_id",
    "tool_name",
    "action",
    "runtime_mode",
    "decision",
    "allowed",
    "reason",
}


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_demo_runs_without_api_keys_and_creates_jsonl(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)

    output_path = tmp_path / "tool_execution_mediation_demo.jsonl"

    assert demo.main(output_path) == 0
    assert output_path.exists()

    records = load_jsonl(output_path)
    assert len(records) == 5


def test_each_record_has_required_tool_execution_fields(tmp_path) -> None:
    output_path = tmp_path / "tool_execution_mediation_demo.jsonl"
    demo.run_demo(output_path)

    for record in load_jsonl(output_path):
        assert REQUIRED_RECORD_KEYS <= record.keys()


def test_expected_decisions_are_present(tmp_path) -> None:
    output_path = tmp_path / "tool_execution_mediation_demo.jsonl"
    demo.run_demo(output_path)

    records = load_jsonl(output_path)
    decisions_by_case = {record["case_id"]: record for record in records}

    assert decisions_by_case["read_only_inspection"]["decision"] == "ALLOW"
    assert decisions_by_case["read_only_inspection"]["allowed"] is True
    assert decisions_by_case["file_write_review"]["decision"] == "NEEDS_REVIEW"
    assert decisions_by_case["file_write_review"]["allowed"] is False
    assert decisions_by_case["config_mutation_review"]["decision"] == "NEEDS_REVIEW"
    assert decisions_by_case["config_mutation_review"]["allowed"] is False
    assert decisions_by_case["destructive_bypass_denied"]["decision"] == "DENY"
    assert decisions_by_case["destructive_bypass_denied"]["allowed"] is False
    assert decisions_by_case["strict_read_only_review"]["decision"] == "NEEDS_REVIEW"
    assert decisions_by_case["strict_read_only_review"]["allowed"] is False


def test_no_external_network_provider_or_tool_execution_dependency() -> None:
    source = Path(demo.__file__).read_text(encoding="utf-8").lower()

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

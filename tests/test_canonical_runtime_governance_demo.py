from __future__ import annotations

import json
from pathlib import Path

from examples import canonical_runtime_governance_demo as demo


REQUIRED_RECORD_KEYS = {
    "case_id",
    "prompt",
    "candidate",
    "release_decision",
    "memory_admission",
    "reason",
    "memory_admission_decision",
    "memory_admission_reason",
}

def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_demo_runs_without_api_keys_and_creates_jsonl(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)

    output_path = tmp_path / "canonical_runtime_governance_demo.jsonl"

    assert demo.main(output_path) == 0
    assert output_path.exists()

    records = load_jsonl(output_path)
    assert len(records) == 4


def test_each_record_has_required_governance_fields(tmp_path) -> None:
    output_path = tmp_path / "canonical_runtime_governance_demo.jsonl"
    demo.run_demo(output_path)

    for record in load_jsonl(output_path):
        assert REQUIRED_RECORD_KEYS <= record.keys()


def test_release_decision_controls_memory_admission(tmp_path) -> None:
    output_path = tmp_path / "canonical_runtime_governance_demo.jsonl"
    demo.run_demo(output_path)

    records = load_jsonl(output_path)
    safe_record = next(record for record in records if record["case_id"] == "safe_candidate")
    uncertain_record = next(
        record for record in records if record["case_id"] == "uncertain_candidate"
    )
    blocked_record = next(record for record in records if record["case_id"] == "blocked_candidate")

    assert safe_record["release_decision"] == "PROCEED"
    assert safe_record["memory_admission"] is True
    assert uncertain_record["release_decision"] == "NEEDS_REVIEW"
    assert uncertain_record["memory_admission"] is False
    assert blocked_record["release_decision"] == "SILENCE"
    assert blocked_record["memory_admission"] is False


def test_memory_admission_policy_fields_are_recorded(tmp_path) -> None:
    output_path = tmp_path / "canonical_runtime_governance_demo.jsonl"
    demo.run_demo(output_path)

    records = load_jsonl(output_path)
    safe_record = next(
        record for record in records if record["case_id"] == "safe_candidate"
    )

    assert safe_record["memory_admission_decision"] == "ADMIT"
    assert safe_record["memory_admission_reason"]


def test_continuity_conflict_case_is_held_for_memory_review(tmp_path) -> None:
    output_path = tmp_path / "canonical_runtime_governance_demo.jsonl"
    demo.run_demo(output_path)

    records = load_jsonl(output_path)
    conflict_record = next(
        record for record in records if record["case_id"] == "continuity_conflict_candidate"
    )

    assert conflict_record["release_decision"] == "PROCEED"
    assert conflict_record["memory_admission_decision"] == "NEEDS_REVIEW"
    assert conflict_record["memory_admission"] is False
    assert "safe-mode preference" in str(conflict_record["memory_admission_reason"])


def test_no_external_network_or_provider_dependency() -> None:
    source = Path(demo.__file__).read_text(encoding="utf-8")

    forbidden_terms = (
        "requests",
        "urllib",
        "httpx",
        "openai",
        "anthropic",
        "ollama",
        "model_client",
    )

    assert not any(term in source.lower() for term in forbidden_terms)

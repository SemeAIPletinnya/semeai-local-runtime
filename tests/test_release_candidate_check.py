from __future__ import annotations

from pathlib import Path

from tools.release_candidate_check import EVIDENCE_FILES, REQUIRED_FILES, run_check


def touch_files(root: Path, relative_paths: tuple[str, ...]) -> None:
    for relative_path in relative_paths:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")


def test_check_passes_when_required_files_exist(tmp_path, capsys) -> None:
    touch_files(tmp_path, REQUIRED_FILES)

    result = run_check(tmp_path, require_evidence=False)
    output = capsys.readouterr().out

    assert result == 0
    assert "Release Candidate Check — v0.1.0-prealpha" in output
    assert "required files: PASS" in output
    assert "evidence files: MISSING" in output
    assert "result: PASS" in output


def test_missing_required_file_returns_non_zero(tmp_path, capsys) -> None:
    touch_files(tmp_path, REQUIRED_FILES[1:])

    result = run_check(tmp_path, require_evidence=False)
    output = capsys.readouterr().out

    assert result != 0
    assert "required files: FAIL" in output
    assert "result: FAIL" in output
    assert "README.md" in output


def test_missing_evidence_does_not_fail_by_default(tmp_path, capsys) -> None:
    touch_files(tmp_path, REQUIRED_FILES)

    result = run_check(tmp_path, require_evidence=False)
    output = capsys.readouterr().out

    assert result == 0
    assert "evidence files: MISSING" in output
    assert "result: PASS" in output


def test_missing_evidence_fails_with_require_evidence(tmp_path, capsys) -> None:
    touch_files(tmp_path, REQUIRED_FILES)

    result = run_check(tmp_path, require_evidence=True)
    output = capsys.readouterr().out

    assert result != 0
    assert "evidence files: MISSING" in output
    assert "result: FAIL" in output
    assert "outputs/canonical_runtime_governance_demo.jsonl" in output


def test_present_evidence_passes_with_require_evidence(tmp_path, capsys) -> None:
    touch_files(tmp_path, REQUIRED_FILES)
    touch_files(tmp_path, EVIDENCE_FILES)

    result = run_check(tmp_path, require_evidence=True)
    output = capsys.readouterr().out

    assert result == 0
    assert "evidence files: PRESENT" in output
    assert "result: PASS" in output

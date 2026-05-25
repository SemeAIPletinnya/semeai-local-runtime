from semeai_runtime.control_gate import evaluate_candidate


def test_empty_candidate_is_silenced() -> None:
    result = evaluate_candidate("")

    assert result.decision == "SILENCE"


def test_normal_candidate_proceeds() -> None:
    result = evaluate_candidate("Hello from SemeAi")

    assert result.decision == "PROCEED"


def test_risky_candidate_requires_review() -> None:
    result = evaluate_candidate("Please run rm -rf /")

    assert result.decision == "NEEDS_REVIEW"
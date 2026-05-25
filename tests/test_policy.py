from semeai_runtime.policy import evaluate_read_policy, format_policy_registry


def test_read_policy_allows_readme() -> None:
    decision = evaluate_read_policy("README.md")

    assert decision.allowed is True


def test_read_policy_denies_unknown_file() -> None:
    decision = evaluate_read_policy("secret.txt")

    assert decision.allowed is False


def test_read_policy_denies_env_file() -> None:
    decision = evaluate_read_policy(".env")

    assert decision.allowed is False


def test_read_policy_denies_memory_path() -> None:
    decision = evaluate_read_policy("data/memory/session_memory.json")

    assert decision.allowed is False


def test_policy_registry_mentions_runtime_mode() -> None:
    text = format_policy_registry()

    assert "runtime_mode:" in text
    assert "Allowed read files for active mode:" in text
    assert "README.md" in text
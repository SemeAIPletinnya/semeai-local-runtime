from semeai_runtime.runtime_mode import get_runtime_mode


def test_default_runtime_mode_is_safe(monkeypatch) -> None:
    monkeypatch.delenv("SEMEAI_RUNTIME_MODE", raising=False)

    assert get_runtime_mode() == "SAFE"


def test_invalid_runtime_mode_falls_back_to_safe(monkeypatch) -> None:
    monkeypatch.setenv("SEMEAI_RUNTIME_MODE", "unknown")

    assert get_runtime_mode() == "SAFE"


def test_development_runtime_mode(monkeypatch) -> None:
    monkeypatch.setenv("SEMEAI_RUNTIME_MODE", "DEVELOPMENT")

    assert get_runtime_mode() == "DEVELOPMENT"
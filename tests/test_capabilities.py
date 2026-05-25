from semeai_runtime.capabilities import format_capability_manifest


def test_capability_manifest_contains_runtime_tools() -> None:
    text = format_capability_manifest()

    assert "Runtime capability manifest:" in text
    assert "read_allowed_file" in text
    assert "memory_inspection" in text
    assert "requires_policy: True" in text
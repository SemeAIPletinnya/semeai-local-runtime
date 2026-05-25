from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

from semeai_runtime.memory import format_profile_context, load_profile
from semeai_runtime.repo_context import load_repo_context


@dataclass(frozen=True)
class ModelResponse:
    model: str
    prompt: str
    candidate: str


def format_conversation_history(
    history: list[dict[str, str]],
    max_turns: int = 6,
) -> str:
    """Format recent conversation turns as compact runtime context."""
    if not history:
        return "No previous conversation turns in this session."

    recent = history[-max_turns:]
    lines: list[str] = []

    for item in recent:
        user = item.get("user", "")
        semeai = item.get("semeai", "")

        lines.append(f"User: {user}")
        lines.append(f"SemeAi: {semeai}")

    return "\n".join(lines)


def generate_candidate(
    prompt: str,
    model: str = "qwen3:4b",
    host: str = "http://localhost:11434",
    conversation_history: list[dict[str, str]] | None = None,
) -> ModelResponse:
    """Generate a candidate response from a local Ollama model.

    The model only produces a candidate.
    Release authority belongs to the runtime control layer.
    """
    profile_context = format_profile_context(load_profile())
    history_context = format_conversation_history(conversation_history or [])
    repo_context = load_repo_context()

    payload = {
        "model": model,
        "prompt": (
            "You are SemeAi local runtime candidate generator. "
            "Answer in Ukrainian or English depending on the user's language. "
            "Generate a candidate answer only. "
            "Release authority belongs to the runtime control layer.\n\n"
            "Local runtime profile memory:\n"
            f"{profile_context}\n\n"
            "Repository context:\n"
            f"{repo_context}\n\n"
            "Recent conversation history:\n"
            f"{history_context}\n\n"
            f"Current user prompt: {prompt}"
        ),
        "stream": False,
    }

    request = urllib.request.Request(
        url=f"{host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    return ModelResponse(
        model=model,
        prompt=prompt,
        candidate=str(data.get("response", "")),
    )
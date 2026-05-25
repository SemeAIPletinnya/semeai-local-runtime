from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelResponse:
    model: str
    prompt: str
    candidate: str


def generate_candidate(
    prompt: str,
    model: str = "qwen3:4b",
    host: str = "http://localhost:11434",
) -> ModelResponse:
    """Generate a candidate response from a local Ollama model.

    The model only produces a candidate.
    Release authority belongs to the runtime control layer.
    """
    payload = {
    "model": model,
    "prompt": (
        "You are SemeAi local runtime candidate generator. "
        "Answer in Ukrainian unless the user asks for another language. "
        "Generate a candidate answer only. "
        "Release authority belongs to the runtime control layer.\n\n"
        f"User prompt: {prompt}"
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
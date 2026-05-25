# SemeAi Local Runtime

SemeAi is a local AI runtime prototype combining:

- local LLMs
- runtime release-control
- replay/evidence architecture
- local memory
- controlled tool access
- PROCEED / NEEDS_REVIEW / SILENCE routing

Core thesis:

> generation != release authority

SemeAi is not a model.
SemeAi is a controlled local AI runtime.

## Initial stack

- Ollama
- Qwen3
- Python
- local replay/evidence architecture
- Silence-as-Control inspired runtime gate

## Current status

Early runtime prototype.

Current goals:

- local candidate generation
- runtime release-control
- replay/evidence logging
- repository-aware context
- controlled local tooling

## Scope

This project does not claim:

- AGI
- autonomous unrestricted agents
- universal AI safety
- production readiness
- replacement of human review

The focus is runtime control, release authority separation, and local AI system architecture.

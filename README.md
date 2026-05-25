# SemeAi Local Runtime

SemeAi is a controlled local AI runtime prototype.

It combines:

- local LLM generation through Ollama/Qwen
- runtime release-control
- candidate/release separation
- persistent local memory
- repository-aware context
- controlled tool access
- policy/mode/config governance
- replay/evidence logging
- `PROCEED / NEEDS_REVIEW / SILENCE` routing

Core thesis:

> generation != release authority

Additional runtime thesis:

> capability != execution authority

SemeAi is not a model.  
SemeAi is a controlled local AI runtime around models.

## Current status

```text
v0.1.0 pre-alpha candidate
```

This repository is currently a local runtime orchestration prototype.

It is not production-ready.  
It is not an AGI project.  
It is not an unrestricted autonomous agent.

## Current architecture

```text
config/runtime.json
-> runtime mode
-> runtime policies
-> capability manifests
-> profile memory
-> persistent memory
-> README/repo context
-> recent conversation history
-> local candidate generation
-> runtime release gate
-> PROCEED / NEEDS_REVIEW / SILENCE
-> controlled command/tool execution
-> session-aware runtime event logging
-> policy-aware replay inspection
```

## Initial stack

- Python
- Ollama
- Qwen3 4B
- JSONL runtime logs
- pytest
- local-first runtime architecture

## Requirements

- Python
- Ollama running locally
- Qwen model available through Ollama

Example:

```powershell
ollama run qwen3:4b
```

## Run the local runtime

From the repository root:

```powershell
$env:PYTHONPATH="src"
python -m semeai_runtime.cli
```

The runtime starts an interactive session:

```text
SemeAi Local Runtime
Session: <uuid>
Type 'exit' or 'quit' to stop.
Use '/help' to see runtime commands.
```

## Runtime commands

```text
/help
/tools
/config
/mode
/policies
/capabilities
/memory
/read README.md
exit
```

## Runtime modes

The runtime supports:

```text
SAFE
DEVELOPMENT
STRICT
```

Default mode is `SAFE`.

You can set a runtime mode through environment:

```powershell
$env:SEMEAI_RUNTIME_MODE="DEVELOPMENT"
python -m semeai_runtime.cli
```

Clear it with:

```powershell
Remove-Item Env:SEMEAI_RUNTIME_MODE
```

Runtime configuration is stored in:

```text
config/runtime.json
```

## Replay / inspection

Runtime events are logged to:

```text
outputs/runtime_log.jsonl
```

Inspect replay logs:

```powershell
$env:PYTHONPATH="src"
python -m semeai_runtime.replay_log
```

The replay layer distinguishes:

```text
model_decision
tool_call
```

and surfaces tool policy outcomes such as:

```text
ALLOWED
DENIED
ALLOWED_BUT_NOT_FOUND
```

## Validation

Run tests:

```powershell
$env:PYTHONPATH="src"
python -m pytest
```

## Scope

This project does **not** claim:

- AGI
- autonomous unrestricted agency
- universal AI safety
- production readiness
- replacement of human review
- guaranteed correctness
- unrestricted tool execution
- model improvement
- hallucination elimination

The focus is:

```text
local runtime control
release authority separation
policy-governed tool execution
runtime provenance
replayable decision traces
```

## Relationship to Silence-as-Control

SemeAi Local Runtime continues the architectural thesis of Silence-as-Control:

```text
generation is not release authority
```

In this repository, the same idea is extended toward local runtime systems:

```text
tool capability is not execution authority
memory is not truth
configuration influences governance
runtime behavior should be inspectable
```

## Current pre-alpha interpretation

SemeAi v0.1.0 pre-alpha means:

- local candidate generation works
- release-control gate works
- interactive CLI works
- persistent memory works
- repo-aware context works
- controlled `/read` tooling works
- runtime modes/config/policies work
- capability manifests work
- runtime logs and replay inspection work

It does not mean production readiness.
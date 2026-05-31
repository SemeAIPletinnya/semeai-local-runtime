# Canonical Runtime Governance Demo

This demo is a small, no-key, deterministic example of local runtime governance.
It uses mocked candidate outputs rather than an external model or provider.

## What this demo proves

This demo proves a local deterministic governance flow:

```text
user input
→ candidate output
→ release gate
→ PROCEED / NEEDS_REVIEW / SILENCE
→ memory admission decision
→ runtime/replay log
→ inspection output
```

It shows three separate authority boundaries:

```text
generation != release authority
capability != execution authority
memory != persistence authority
```

In this demo, a candidate can exist without being released, and a candidate can be
reviewed or silenced without being admitted into memory.

## What this demo does not prove

This demo does not prove AGI, universal AI safety, production readiness, or
guaranteed correctness. It does not evaluate a real model, replace human review,
or prove that these simple rules are sufficient for production systems.

## Canonical flow

The demo runs three deterministic cases:

1. A safe candidate returns `PROCEED` and memory admission is allowed.
2. An uncertain or risky candidate returns `NEEDS_REVIEW` and memory admission is denied.
3. A blocked candidate returns `SILENCE` and memory admission is denied.

The release gate uses simple local string rules:

- blocked terms such as `delete production data` or `bypass approval` return `SILENCE`;
- uncertainty or risk terms such as `probably`, `maybe`, or `without evidence` return `NEEDS_REVIEW`;
- otherwise, the candidate returns `PROCEED`.

Memory admission is intentionally separate from generation and release. It is
allowed only when the release decision is `PROCEED`.

## Run on Windows PowerShell

From the repository root:

```powershell
python examples/canonical_runtime_governance_demo.py
```

No API keys are required. The demo does not import Ollama, call a local model, or
call an external provider.

## Inspect the JSONL output

The demo writes one JSON object per line to:

```text
outputs/canonical_runtime_governance_demo.jsonl
```

In PowerShell, print the raw JSONL file:

```powershell
Get-Content outputs/canonical_runtime_governance_demo.jsonl
```

Or pretty-print each record with Python:

```powershell
python -c "import json, pathlib; [print(json.dumps(json.loads(line), indent=2)) for line in pathlib.Path('outputs/canonical_runtime_governance_demo.jsonl').read_text().splitlines()]"
```

Each record includes:

- `case_id`
- `prompt`
- `candidate`
- `release_decision`
- `memory_admission`
- `reason`

## Why memory admission is separate

Generation creates a candidate. The release gate decides whether the candidate is
allowed to be shown as `PROCEED`, held as `NEEDS_REVIEW`, or suppressed as
`SILENCE`. Memory admission is a later decision about whether the candidate is
allowed to persist beyond the current run.

Keeping these decisions separate preserves the core governance boundary:

```text
memory != persistence authority
```

A runtime can generate text without releasing it, and it can release or review
text without automatically making it persistent memory.

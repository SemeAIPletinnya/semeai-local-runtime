# Tool Execution Mediation Demo

This demo is a small, no-key, deterministic example of local tool execution
mediation. It uses mocked tool/action requests and does not execute any real
shell commands, file mutations, provider calls, or network requests.

## What this demo proves

This demo proves a local deterministic policy boundary:

```text
capability != execution authority
```

A runtime may know about a tool or receive a requested action without granting
execution authority for that action. The policy classifies mocked requests into
three deterministic decisions:

- `ALLOW` for read-only inspection actions in `SAFE` and `DEVELOPMENT` modes.
- `NEEDS_REVIEW` for file write or config mutation actions in `SAFE` and
  `DEVELOPMENT` modes, and for read-only inspection actions in `STRICT` mode.
- `DENY` for destructive or approval-bypass actions in every supported mode.

The demo writes JSONL evidence showing the requested tool, action, runtime mode,
decision, allowed flag, and reason for each mocked request.

## What this demo does not prove

This demo does not prove production readiness, universal safety, sandboxing,
agent autonomy, or comprehensive tool governance. It does not claim to enforce
operating-system permissions or mediate real tools. It only demonstrates a small,
inspectable, deterministic policy primitive for local runtime governance.

## No real tool execution

The demo never runs the requested tools. The tool names and actions are static
mocked inputs used only for policy evaluation. No shell command is executed, no
file is mutated by a requested tool, and no external model or provider is called.

The only file written by the demo itself is its JSONL evidence log:

```text
outputs/tool_execution_mediation_demo.jsonl
```

## Deterministic, local, no-key

The policy is implemented as local string-matching rules. It requires no API
keys, network access, model calls, provider SDKs, or external dependencies.
Repeated runs with the same mocked cases produce the same decisions.

## Run the demo

From the repository root:

```bash
python examples/tool_execution_mediation_demo.py
```

Expected summary shape:

```text
Tool Execution Mediation Demo
-----------------------------
read_only_inspection: SAFE -> ALLOW (allowed)
file_write_review: SAFE -> NEEDS_REVIEW (held)
config_mutation_review: DEVELOPMENT -> NEEDS_REVIEW (held)
destructive_bypass_denied: SAFE -> DENY (held)
strict_read_only_review: STRICT -> NEEDS_REVIEW (held)
log: /path/to/repo/outputs/tool_execution_mediation_demo.jsonl
```

## Inspect the JSONL output

Print the raw JSONL file:

```bash
cat outputs/tool_execution_mediation_demo.jsonl
```

Pretty-print each record:

```bash
python -c "import json, pathlib; [print(json.dumps(json.loads(line), indent=2)) for line in pathlib.Path('outputs/tool_execution_mediation_demo.jsonl').read_text().splitlines()]"
```

Each JSONL record includes:

- `case_id`
- `tool_name`
- `action`
- `runtime_mode`
- `decision`
- `allowed`
- `reason`

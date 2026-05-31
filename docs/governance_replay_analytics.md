# Governance Replay Analytics

`tools/governance_replay_analytics.py` is a small local utility for summarizing replayed governance evidence. It reads deterministic JSONL evidence files produced by the demos and prints aggregate observability metrics for runtime release governance, memory admission, continuity conflicts when those fields are present, and tool execution mediation.

The default inputs are:

```text
outputs/canonical_runtime_governance_demo.jsonl
outputs/tool_execution_mediation_demo.jsonl
```

The utility is no-key and local-only. It does not call model providers, use the network, execute tools, or mutate runtime state.

## What it reports

For canonical runtime governance replay evidence, the utility reports:

- total runtime records
- release decision counts for `PROCEED`, `NEEDS_REVIEW`, and `SILENCE`
- memory admitted and denied counts
- memory admission decision counts for `ADMIT`, `NEEDS_REVIEW`, and `DENY` when the field exists
- continuity conflict count when conflict fields exist

For tool execution mediation replay evidence, the utility reports:

- total tool records
- tool execution decision counts for `ALLOW`, `NEEDS_REVIEW`, and `DENY`
- allowed and not-allowed counts
- runtime mode counts for `SAFE`, `DEVELOPMENT`, and `STRICT`

## What it does not prove

These aggregate metrics are observability over replayed local evidence. They do not prove production readiness, universal safety coverage, model correctness, or that future runtime behavior will be safe. The report only summarizes records that already exist in the selected JSONL files.

## Replay evidence and authority remain separate

The analytics utility reads evidence after governance decisions have already been recorded. It does not approve release, admit memory, persist state, grant capability, or execute a tool. This keeps observability separate from authority:

```text
generation != release authority
memory != persistence authority
release approval != persistence approval
capability != execution authority
```

## Run after demo generation

From the repository root, generate the replay evidence and then run the analytics utility:

```bash
python examples/canonical_runtime_governance_demo.py
python examples/tool_execution_mediation_demo.py
python tools/governance_replay_analytics.py
```

You can also point the utility at alternate JSONL files:

```bash
python tools/governance_replay_analytics.py \
  --runtime-input path/to/runtime.jsonl \
  --tool-input path/to/tool.jsonl
```

If one selected input exists, the utility summarizes that file. If neither selected input exists, it returns non-zero with a clear error.

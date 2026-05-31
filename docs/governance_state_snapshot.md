# Governance State Snapshot

`tools/governance_state_snapshot.py` writes a small session-level governance state capsule from replayed governance evidence.

The snapshot reads existing JSONL evidence produced by the canonical runtime governance demo and the tool execution mediation demo. It summarizes the replayed decisions into a deterministic JSON object and writes that object to `outputs/governance_state_snapshot.json` by default.

## What state snapshots are

A governance state snapshot is a local capsule over prior governance decisions. It records:

- which replay evidence files were present;
- aggregate release mediation counts;
- aggregate memory admission counts;
- continuity conflict counts surfaced in runtime evidence;
- aggregate tool execution mediation counts;
- runtime mode counts from tool mediation evidence;
- authority-boundary reminders, including `snapshot != authority`;
- a deterministic `governance_state_hash` over normalized snapshot content.

The hash excludes `generated_at_utc` and `governance_state_hash` so the same input evidence produces the same state hash even when the snapshot timestamp changes.

## What snapshots do not prove

A snapshot is evidence about prior replayed decisions only. It does not prove that a candidate should be released, persisted, remembered, or executed. It also does not prove production readiness, universal safety coverage, model correctness, or completeness of observability.

The utility does not call models, providers, or the network. It does not execute mediated tools. It does not mutate runtime decisions.

## How snapshots differ from analytics

Governance replay analytics prints deterministic aggregate metrics for inspection. A governance state snapshot writes a JSON capsule that can be checked, archived, or compared at the session level.

Both operate over replay evidence. Neither is an authority layer.

## Why snapshot != authority

The runtime architecture keeps evidence separate from authority:

```text
generation != release authority
memory != persistence authority
release approval != persistence approval
capability != execution authority
observability != authority
snapshot != authority
```

A snapshot can summarize what earlier mediation layers recorded. It cannot approve release, persistence, or execution, and it cannot override the policies that produced the original evidence.

## Run after demo generation

From the repository root:

```powershell
python examples/canonical_runtime_governance_demo.py
python examples/tool_execution_mediation_demo.py
python tools/governance_replay_analytics.py
python tools/governance_state_snapshot.py
```

The snapshot is written to:

```text
outputs/governance_state_snapshot.json
```

Optional paths:

```powershell
python tools/governance_state_snapshot.py `
  --runtime-input outputs/canonical_runtime_governance_demo.jsonl `
  --tool-input outputs/tool_execution_mediation_demo.jsonl `
  --output outputs/governance_state_snapshot.json
```

# v0.1.0-prealpha Release Candidate

## Release candidate name

`v0.1.0-prealpha`

## Scope

This release candidate packages a local deterministic runtime-governance prototype. It is a conservative packaging milestone for the existing prototype surface and does not add runtime features or production claims.

## Included surfaces

- Canonical runtime governance demo
- Memory admission policy
- Continuity conflict policy
- Tool execution mediation policy
- Governance replay analytics
- Governance state snapshot
- JSONL evidence outputs

## Authority boundaries

- generation != release authority
- memory != persistence authority
- release approval != persistence approval
- capability != execution authority
- observability != authority
- snapshot != authority

## Validation commands

Run from the repository root:

```bash
python examples/canonical_runtime_governance_demo.py
python examples/tool_execution_mediation_demo.py
python tools/governance_replay_analytics.py
python tools/governance_state_snapshot.py
python -m pytest
```

## Expected evidence outputs

- `outputs/canonical_runtime_governance_demo.jsonl`
- `outputs/tool_execution_mediation_demo.jsonl`
- `outputs/governance_state_snapshot.json`

## Scope boundaries

This release candidate is intentionally limited:

- not production ready
- no universal safety claim
- no model correctness claim
- no real tool execution
- no provider/network dependency
- no autonomous agent claim

## Release candidate checklist

- [ ] demos run
- [ ] analytics runs
- [ ] snapshot runs
- [ ] full test suite passes
- [ ] README links present
- [ ] issue #2 updated
- [ ] issue #3 updated

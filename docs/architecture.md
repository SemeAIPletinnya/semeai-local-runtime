***# SemeAi Local Runtime Architecture***



***SemeAi Local Runtime is a controlled local AI runtime prototype.***



***It is designed around one core separation:***



***```text***

***generation != release authority***

***```***



***A second separation applies to tools:***



***```text***

***capability != execution authority***

***```***



***## Runtime chain***



***Current runtime chain:***



***```text***

***config/runtime.json***

***-> runtime mode***

***-> runtime policies***

***-> capability manifests***

***-> profile memory***

***-> persistent memory***

***-> README/repo context***

***-> recent conversation history***

***-> local candidate generation***

***-> runtime release gate***

***-> PROCEED / NEEDS\_REVIEW / SILENCE***

***-> controlled command/tool execution***

***-> session-aware runtime event logging***

***-> policy-aware replay inspection***

***```***



***## Layers***



***### 1. Configuration layer***



***File:***



***```text***

***config/runtime.json***

***```***



***Controls:***



***```text***

***mode***

***max\_memory\_turns***

***max\_read\_chars***

***replay\_enabled***

***```***



***The config layer allows runtime behavior to be changed without changing code.***



***---***



***### 2. Runtime mode layer***



***File:***



***```text***

***src/semeai\_runtime/runtime\_mode.py***

***```***



***Modes:***



***```text***

***SAFE***

***DEVELOPMENT***

***STRICT***

***```***



***The active mode influences governance and allowed runtime surface.***



***---***



***### 3. Policy layer***



***File:***



***```text***

***src/semeai\_runtime/policy.py***

***```***



***Current read policy checks:***



***```text***

***blocked path markers***

***allowed read files by active mode***

***configured max read size***

***```***



***---***



***### 4. Capability manifest layer***



***File:***



***```text***

***src/semeai\_runtime/capabilities.py***

***```***



***Capability metadata:***



***```text***

***tool\_name***

***description***

***requires\_policy***

***requires\_mode***

***replay\_logged***

***governed***

***```***



***This makes the runtime partially self-describing.***



***---***



***### 5. Command registry layer***



***File:***



***```text***

***src/semeai\_runtime/commands.py***

***```***



***Current commands:***



***```text***

***/help***

***/tools***

***/config***

***/mode***

***/policies***

***/capabilities***

***/memory***

***/read <path>***

***```***



***Commands are routed through a metadata-driven registry.***



***---***



***### 6. Memory layer***



***Files:***



***```text***

***src/semeai\_runtime/memory.py***

***src/semeai\_runtime/session\_memory.py***

***```***



***Memory types:***



***```text***

***profile memory***

***persistent session memory***

***recent conversation history***

***```***



***Memory is treated as runtime context, not automatic truth.***



***---***



***### 7. Repository context layer***



***File:***



***```text***

***src/semeai\_runtime/repo\_context.py***

***```***



***The runtime can load repository context, currently starting from `README.md`.***



***---***



***### 8. Model client layer***



***File:***



***```text***

***src/semeai\_runtime/model\_client.py***

***```***



***The local model produces candidate output through Ollama/Qwen.***



***The model does not own release authority.***



***---***



***### 9. Release-control layer***



***File:***



***```text***

***src/semeai\_runtime/control\_gate.py***

***```***



***Gate outcomes:***



***```text***

***PROCEED***

***NEEDS\_REVIEW***

***SILENCE***

***```***



***Only `PROCEED` is released by default.***



***---***



***### 10. Runtime logging layer***



***File:***



***```text***

***src/semeai\_runtime/runtime\_log.py***

***```***



***Runtime events are stored in:***



***```text***

***outputs/runtime\_log.jsonl***

***```***



***Event types:***



***```text***

***model\_decision***

***tool\_call***

***```***



***---***



***### 11. Replay / evidence layer***



***File:***



***```text***

***src/semeai\_runtime/replay\_log.py***

***```***



***Replay inspection groups events by session and turn index.***



***Replay surfaces:***



***```text***

***model decisions***

***tool calls***

***allowed tool actions***

***denied tool actions***

***policy outcomes***

***```***



***---***



***## Safety boundaries***



***The runtime should avoid:***



***- unrestricted autonomous agency***

***- unsafe shell execution***

***- self-modifying behavior***

***- uncontrolled secret access***

***- AGI claims***

***- production-readiness claims***



***---***



***## Current pre-alpha surface***



***The current v0.1.0 pre-alpha runtime demonstrates:***



***```text***

***local inference***

***controlled release***

***persistent memory***

***repo-aware context***

***controlled tooling***

***mode-aware policy***

***capability manifests***

***session logging***

***policy-aware replay***

***```***



***---***



***## Near-term next work***



***After v0.1.0 pre-alpha packaging:***



***```text***

***installable CLI cleanup***

***richer replay summaries***

***repo context beyond README***

***memory pruning commands***

***read-only repo search***

***better tests***

***```***


# VERDICT 005 — capability self-awareness probe (INTAKE 005 / PROPOSAL 005)

Measured-prototype (ladder rung 2) two-plane capability probe settling INTAKE 005: **can an
automated probe produce an HONEST whole-repo `CAPABILITIES.md`, or does per-seat variance make
single-file regeneration a laundering of one seat's world into "the repo's abilities"?** The
battery runs from **two documented seat types** (coordinator + spawned worker — the OA-003
`create_trigger`/`send_later` split), records per-item `present | absent | wall | not-probeable`
with verbatim status/error text, and computes a three-way diff (seat A vs seat B vs a
hand-maintained ledger baseline) with false-wall / false-capability counts.

**Verdict:** `[COORDINATOR TO FINALIZE]` — the load-bearing measurement points to **"probe
must annotate per-seat-type sections"** (regenerate-whole-file from one seat is NOT honest):
the two seats' five seat-defining agent-plane tools are **disjoint** (measured divergence = 5),
and each divergent tool is a **false wall** from the other seat's single-seat view (5 false
walls); a naive `present/absent` projection also launders **1 false capability**
(`create_trigger` visible while its cross-session bind is org-walled, OA-003). Meanwhile the
**subprocess plane is seat-invariant and read-only-probeable**, unanimous across 5 runs
(agreement 1.00) and reproduces the ledgered walls **exactly** (0 false walls).

Source idea: `menno420/idea-engine` `control/outbox.md` PROPOSAL 005 @
`e0f207d51aa731ce6924abff84aca63727b42d97` (canonical superbot
`docs/ideas/project-capability-self-awareness-2026-07-10.md` @
`9624c5399f5b1a3da293c07ce930e8b0410d79e4`).

## One run command
```
python3 sims/verdict-005-capability-self-probe/analyze.py
```
Deterministic, stdlib-only, exit 0 iff all self-checks pass (**394 this cycle**). It
recomputes every headline number from the frozen `runs/` and emits `CAPABILITIES.json`
(schema `CAPABILITIES.v1`) + a rendered `CAPABILITIES.md` sample. The **live** probe layer
(`probe.py` + the seat self-enumerations) is NOT bit-reproducible — see `probe_protocol.md`.

## Files
- `REPORT.md` — the live verdict (8-section, all five validity-gate answers).
- `probe.py` — the live/non-deterministic layer: two-plane read-only battery → one frozen json.
- `analyze.py` — deterministic analysis + self-checks over the frozen runs; emits the schema.
- `probe_protocol.md` — the exact battery, the ≥2 seat definitions, re-measurement spec.
- `runs/probe_worker_run{1..5}.json` — 5 frozen worker-seat probe transcripts.
- `runs/agent_inventory_{coordinator,worker}.json` — each seat's own tool enumeration.
- `runs/baseline.json` — the hand-maintained ledger baseline (every item cited).
- `CAPABILITIES.json` / `CAPABILITIES.md` — the emitted schema instance + rendered sample.

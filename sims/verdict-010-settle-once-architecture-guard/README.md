# verdict-010 · settle-once-architecture-guard

Catch-matrix reconstruction of the six documented double-settlement instances vs
three candidate settle-once guard contracts. Answers PROPOSAL 009: which guard
CONTRACT catches the full corpus with zero false positives.

## Run (one command)

```
python3 sims/verdict-010-settle-once-architecture-guard/settle_once_sim.py
```

Exit 0 iff all self-checks pass. Deterministic, RNG-free, exhaustive interleaving
sweep (every order-preserving merge: 6 for 2-attempt, 90 for retry-3).

## Files

- `settle_once_sim.py` — the model + catch matrix + false-positive column + variant sweep + self-checks.
- `REPORT.md` — the finalizable verdict report (8 sections, five validity-gate answers).

## Verdict (summary — full report in REPORT.md)

**approve** · evidence: simulation (reconstruction rung 1–2) · gate PASS.
Winner contract: **(c) row-consumption + mandated check-and-set for no-row legs** —
catches all six + variants (6/6, 0 missed), zero false positives given explicit
re-arm. (b) row-consumption alone misses every no-row leg (1/6). (a) caller-side
claim is opt-in and its shipped static scope silently excludes cogs/ (3/6; 5/6 with
the roots fix, still cross-tree miss on #133). Target: superbot-next (tools/check_*
seam); lane-side one-liner for superbot (check_consistency.py:1151 roots += "cogs/").

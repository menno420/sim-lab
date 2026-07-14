# verdict-076 — fishing cook-leg constants

> **Status:** `complete`

Serves superbot-games `## SIM-REQUEST · fishing-cook-economy · 2026-07-13`
(filed 2026-07-13T18:18:29Z, status `open` at packet pin `ed2fabb`), folded into
the same batch run as sibling VERDICT 075 per the roster request's own clause.
Routed by sim-lab inbox ORDER 008 item (2). Intake: **INTAKE simreq-011**;
**VERDICT 074 stays RESERVED** for idea-engine PROPOSAL 063.

**Ruling: APPROVE-WITH-CONSTANTS — P\* = 12** (implied coins-per-energy price of
cooking): cooked energy `E_s = max(1, round(S_s / 12))` → committed species
**minnow 1 · bass 1 · pike 2 · legend_carp 7**, plus finding **F-FLAT30** (the
committed flat `"cooked fish": 30` is a perpetual-motion machine at every cell —
ρ ≥ 4.5 by the packet's own bite floor; measured min 7.13). Detail in
[REPORT.md](REPORT.md); ledger block in `control/outbox.md` (VERDICT 076).

Run it (hermetic, stdlib-only, ~0.7 s):

```
python3 sims/verdict-076-fishing-cook-economy/fishing_cook_economy_sim.py
```

37/37 self-checks, exit 0; stdout + `results.json` byte-identical across two
full process runs (sha256 in REPORT.md).

Files: `fixtures.json` (registration, committed BEFORE the runner; embeds the
V075 candidate table VERBATIM as the adversarial reporting world) · `fixtures/`
(the same 16-file byte-copied packet closure as V075, own copy + MANIFEST) ·
`fishing_cook_economy_sim.py` · `results.json` + `run-stdout.txt` (accepted run).

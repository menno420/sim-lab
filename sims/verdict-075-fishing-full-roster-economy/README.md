# verdict-075 — fishing full-roster sell/XP curve

> **Status:** `complete`

Serves superbot-games `## SIM-REQUEST · fishing-full-roster-economy · 2026-07-13`
(filed 2026-07-13T22:06:03Z via games PR #92 commit `21937f3`; read at the packet
pin `ed2fabbef58f3b97a03e6586a4e03ad0ab89c451`, status `open`). Routed by sim-lab
inbox ORDER 008 item (2). Intake: **INTAKE simreq-010**; **VERDICT 074 stays
RESERVED** for idea-engine PROPOSAL 063.

**Ruling: NULL (band-straddle, needs-reframing)** — full detail in
[REPORT.md](REPORT.md); ledger block in `control/outbox.md` (VERDICT 075).

Run it (hermetic, stdlib-only, ~34 s):

```
python3 sims/verdict-075-fishing-full-roster-economy/fishing_full_roster_economy_sim.py
```

Exit code 1 **by design of the accepted run**: the two failed self-checks
(`stability:A1`, `stability:A3`) ARE the finding — the registered NULL axis
"stability band break". stdout + `results.json` byte-identical across two full
process runs (sha256 in REPORT.md).

Files: `fixtures.json` (registration, committed BEFORE the runner, one
pre-runner amendment — theorem F-STRICT) · `fixtures/` (16-file byte-copied
packet closure + `MANIFEST.sha256`) · `fishing_full_roster_economy_sim.py`
(runner) · `results.json` + `run-stdout.txt` (accepted run).

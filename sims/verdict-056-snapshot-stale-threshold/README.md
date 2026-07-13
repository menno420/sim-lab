# verdict-056-snapshot-stale-threshold

Sim for **VERDICT 056** (idea-engine PROPOSAL 045 — the mineverse READ
contract's stale-indicator threshold: is "3 missed cycles ≈ 180 s" honest at
the cited 60 s push cadence?). See `REPORT.md` for the ruling (**APPROVE**)
and the full gate/boundary story.

Run (stdlib-only, hermetic, deterministic):

```
python3 sims/verdict-056-snapshot-stale-threshold/stale_sim.py
```

Reads only `fixtures.json`; writes `results.json` + prints the decision
tables. Byte-identical stdout + results.json across process runs (CPython
3.11 pinned). Arm A (decision) is SEEDLESS exact-Fraction renewal-reward
enumeration; Arm S seeds 20261317 (main confirmation, 200k + 200k samples) /
20261318 (stability, 20k + 20k) / 20261319 (reporting: sensitivity + burst
confirmations) / 20261320 (aux — never read; never constructed, asserted).
Every decision number is an exact `fractions.Fraction`; the sensitivity
worlds, burst leg, P(L > 300) rows, and per-c splits ride reporting-only.

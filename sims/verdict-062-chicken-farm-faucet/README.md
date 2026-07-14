# verdict-062 — chicken-farm faucet self-balance (idea-engine PROPOSAL 051 / INTAKE 051)

Does the superbot hub farm's committed sink ("each hen costs more coins") keep the
faucet from out-earning the committed daily anchor E[!daily] = 169201/100 = 1692.01
coins/day for any collector — or does the "conservative faucet" run away?

- Engine constants harvested @ superbot `affd7ea` (farm.py / farm_workflow.py /
  economy_helpers.py), pinned verbatim in `fixtures.json`. Fully hermetic: the
  runner reads only its own fixtures.json — zero repo/network reads.
- **Run:** `python3 farm_faucet_sim.py` (no flags). Writes `results.json`;
  stdout is the audit log. Stdlib only, CPython 3.11 pinned and asserted.
- Arm A: seedless exact integer/Fraction decision trajectories (decision-bearing).
  Arm S: seeded jittered robustness — seeds 20261341 (main) / 20261342 (stability)
  / 20261343 (reporting) / 20261344 (aux, never read), the ONLY RNGs constructed.
- Deterministic: stdout + results.json byte-identical across two full process runs
  (external sha256, hashes in REPORT.md). 35 self-checks, 0 failed.
- **Ruling: REJECT** — 3 of 4 decision cadences clear the κ = 1/2 band
  (169201/200 = 846.005 coins/day): 8064 / 6720 / 1320 at Δ = 15 min / 1 h / 4 h.
  Details, gates, and boundaries: `REPORT.md`. Ledger: `control/outbox.md`
  VERDICT 062.

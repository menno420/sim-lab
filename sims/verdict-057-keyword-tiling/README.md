# VERDICT 057 — keyword tiling vs independent picks (idea-engine PROPOSAL 046)

Prices venture-lab's KDP keyword-map first-claim-wins TILING convention
(`docs/publishing/keyword-map.md` @ be6c75d4e3379efc108f27d17f2c8ff5adb9a74f)
against the INDEPENDENT per-packet greedy drafting it replaced, on the
registration's pinned synthetic search-shelf world (PROPOSAL 046, idea-engine
`ideas/venture-lab/keyword-tiling-vs-independent-picks-2026-07-13.md` @ main
09b3867).

Run: `python3 sims/verdict-057-keyword-tiling/tiling_sim.py`

- `fixtures.json` — every registered constant, committed BEFORE the runner.
- `tiling_sim.py` — Arm A (seedless exact Fractions, the DECISION arm) +
  Arm S (seeded MC confirmation, CRN across worlds) + gates + twin evaluators.
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two process runs; sha256s in REPORT.md).
- `REPORT.md` — ruling, 12-cell R table, gates, boundaries.

Ruling: **approve** (REJECT checked first, does not fire). Hermetic,
stdlib-only, CPython 3.11 pinned, seeds 20261321–324.

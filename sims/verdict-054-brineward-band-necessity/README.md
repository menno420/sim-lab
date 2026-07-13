# verdict-054-brineward-band-necessity

Sim for **VERDICT 054** (idea-engine PROPOSAL 043 — Brineward band-2
necessity: does the committed loot/price ladder actually force the deeps, or
is shallow grinding a viable route to the full upgrade ladder?). See
`REPORT.md` for the ruling and the full gate/boundary story.

Run (stdlib-only, hermetic, deterministic):

```
python3 sims/verdict-054-brineward-band-necessity/band_sim.py
```

Reads only `fixtures.json`; writes `results.json` + prints the decision
tables. Byte-identical stdout + results.json across process runs (CPython
3.11 pinned). Seeds 20261309 (Arm S main) / 20261310 (stability) / 20261311
(sensitivity) / 20261312 (aux — never read; zero draws asserted). Arm A
(exact `fractions.Fraction` renewal-reward enumeration) is alone
decision-bearing. Committed game tables quoted verbatim @ gba-homebrew
`8bac80a70c82096828663d501af5f2790acbccc4`.

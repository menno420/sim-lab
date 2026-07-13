# verdict-053-channel-concentration

Sim for **VERDICT 053** (idea-engine PROPOSAL 042 — channel concentration vs
diversification at fixed build budget). See `REPORT.md` for the ruling
(**APPROVE**) and the full gate/boundary story.

Run (stdlib-only, hermetic, deterministic):

```
python3 sims/verdict-053-channel-concentration/channel_sim.py
```

Reads only `fixtures.json`; writes `results.json` + prints the decision
tables. Byte-identical stdout + results.json across process runs (CPython
3.11 pinned). Seeds 20261305 (Arm S main) / 20261306 (stability) / 20261307
(reporting) / 20261308 (aux — never read; zero draws asserted). Arm A (exact
`fractions.Fraction` enumeration) is alone decision-bearing.

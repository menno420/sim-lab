# verdict-055-checkout-pooling

Sim for **VERDICT 055** (idea-engine PROPOSAL 044 — the checkout pooling folk
law priced at its showcase load ρ = 9/10). See `REPORT.md` for the ruling
(**APPROVE**) and the full gate/boundary story.

Run (stdlib-only, hermetic, deterministic):

```
python3 sims/verdict-055-checkout-pooling/pooling_sim.py
```

Reads only `fixtures.json`; writes `results.json` + prints the decision
tables. Byte-identical stdout + results.json across process runs (CPython
3.11 pinned). Seeds 20261313 (main, A = 27, M = 32) / 20261314 (stability,
M = 16) / 20261315 (reporting load sweep A ∈ {21, 24, 30}) / 20261316 (aux —
never read; never constructed, asserted). Every decision number is an exact
`fractions.Fraction`; the SPLIT-JSQ column, the load sweep, and p95 ride
reporting-only.

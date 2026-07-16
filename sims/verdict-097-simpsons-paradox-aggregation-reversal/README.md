# verdict-097 · simpsons-paradox-aggregation-reversal

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 084
(`## PROPOSAL 084 · 2026-07-16T15:25:14Z · status: sim-ready`, idea
`ideas/fleet/simpsons-paradox-aggregation-reversal-2026-07-16.md`, landed
idea-engine main @ 4b9db80 via PR #456 — the round-17 COMPLETELY-UNRELATED-domain
CLOSER slot, STATISTICS / CAUSAL INFERENCE). P084 → V097 under the constant +13
PROPOSAL↔VERDICT offset.

The head prices where the folk rule "a treatment better in EVERY subgroup is
better overall" exactly breaks. On the pinned Charig et al. (1986) kidney-stone
table (BMJ 292:879) — A·small=81/87, A·large=192/263 (pooled A=273/350=39/50);
B·small=234/270, B·large=55/80 (pooled B=289/350) — treatment A beats B in BOTH
strata yet LOSES the pool by exactly 16/350 = 8/175. The pooled rate is a
SIZE-WEIGHTED mean whose weights belong to the ALLOCATION: A loads the hard large
stratum (263/350) against B's 80/350, and that allocation — not the treatment
ranking — flips the sign. The reversal is a CLIFF: holding A's stratum rates
fixed and sweeping x = #A-in-large-stratum, pooled_A(x) is strictly decreasing
and crosses 289/350 exactly ONCE at x*=184 (real table x=263 past it). The priced
repair is STANDARDIZATION to a common weight: std_A=634983/762700≈0.8325 >
std_B=6231/8000≈0.7789, weight-invariant over four mixes, restoring the true
per-stratum ordering at the price of one recorded covariate.

## Run (one command)

```
python3 sims/verdict-097-simpsons-paradox-aggregation-reversal/simpsons_paradox_reversal_sim.py
```

Exit 0 iff every self-check passes (33/33). Deterministic: `results.json` and
`run-stdout.txt` are byte-identical across process runs — no wall clock, no
network, no git at run time. Stdlib only. The decision arms are exact seedless
integer/`Fraction` arithmetic, platform-independent; only the reporting-only
Arm R touches the `random` module.

## Structure — three arms + twin evaluators

- **Arm A** — a pinned deterministic automaton over exact rational (`Fraction`)
  arithmetic. Seedless, DECISION-bearing: per-stratum rates, the pooled reversal
  and its margin, the cliff crossing x*, and the four-mix standardization are all
  exact rational identities re-derived from the raw integer counts.
- **Arm B** — an INDEPENDENTLY-shaped twin: an integer roll-up of the raw counts
  for the pooled winner and an OPPOSITE-DIRECTION crossing walk (descending from
  x=n_A) for the cliff. Tied to Arm A through the typed must-equal contacts
  **C1** (pooled winner), **C2** (cliff x*=184), **C3** (std_A/std_B under the
  pooled-marginal mix), plus the margin and reversal contacts.
- **Arm R** — a SEEDED, REPORTING-ONLY 2×2×2 random census (no statistical gate):
  per draw exactly 6 `randint` draws (a total then a success for each of the four
  cells), one `random.Random` per seed, classes {reversal, no_reversal,
  degenerate}, with a 12-hex class-stream digest. Its only claim is that every
  reversal it sees requires differential weighting. **P084 is SEEDLESS** — the
  Arm-R seeds 970/971/972 are local reporting-only constants and consume NO
  seed-ledger block; the next free block stays **20261730**, untouched.
- **Twin evaluators** — an if-chain scorer and an independently transcribed
  table-driven scorer agree on the ruling token over the FULL enumerated 16-row
  boolean predicate space, and on the measured inputs.

## Decision rule (pre-registered, REJECT-first, mirrors P084's own)

Precedence REJECT → INVALID → APPROVE → NULL, REJECT evaluated FIRST: **REJECT**
when the naive "pooling preserves stratum ordering" claim is refuted by an
exhibited reversal AND a common-weight standardization restores the true
ordering; INVALID on any falsifiability-gate failure F1..F5; APPROVE
(arithmetically excluded) iff a uniform stratum ordering always survives
aggregation; NULL if the reversal is a weight artifact the repair fails to
resolve. Full grammar in `fixtures.json`.

## Layout

- `fixtures.json` — the pinned table verbatim, the weight sets, the reporting-only
  seeds, and the pre-registered anchors; committed BEFORE the runner reads it.
- `simpsons_paradox_reversal_sim.py` — the single runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

**VERDICT: REJECT** — 33/33 self-checks, exit 0, byte-identical double run.

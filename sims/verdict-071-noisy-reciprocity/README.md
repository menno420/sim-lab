# verdict-071 — noisy reciprocity (INTAKE 060)

Prices the Axelrod folk claim "Tit-for-Tat is the best strategy in the repeated
prisoner's dilemma" where the claim actually lives: the COMPLETE 16-rule
deterministic memory-one field (c_CC, c_CD, c_DC, c_DD) ∈ {0,1}⁴ under
trembling-hand execution noise ε ∈ {1/1000, 1/100, 1/20, 1/10} (decision cell
ε = 1/100; controls ε = 1/2 degeneracy and ε = 0 orbit leg), stage game
u(C,C) = 3, u(C,D) = 0, u(D,C) = 5, u(D,D) = 1 — at idea-engine PROPOSAL 060's
pinned model. Fully hermetic: the runner reads ONLY `fixtures.json` (committed
before the runner); zero repo/network reads.

## Run

```
python3 sims/verdict-071-noisy-reciprocity/noisy_reciprocity_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json` are
byte-identical across process runs (verified by external sha256 — see
REPORT.md). ~4 s/run, stdlib-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 060
  block / idea doc, plus the fixture-level choices C1–C9 disclosed BEFORE the
  runner existed.
- `noisy_reciprocity_sim.py` — three-arm runner: Arm A seedless exact
  `fractions.Fraction` Gaussian-elimination stationary solves (4 grid ε × 256
  ordered pairs; decision-bearing) + ε = 0 orbit-cycle evaluator + ε = 1/2
  degeneracy; Arm B independently-written Cramer/adjugate twin (exact-equal on
  every v(i,j), powers F6 and the second decision evaluator); Arm R seeded
  finite-horizon REPORTING-ONLY legs (main 20261377 at T = 4,000, stability
  20261378 at T = 1,000, presentation shuffle 20261379; aux 20261380 NEVER
  read, asserted).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, per-conjunct results in registered order, anomalies,
  boundaries.

## Ruling

**REJECT** — all four pre-registered conjuncts fire at exact rationals:
score(WSLS) − score(TFT) = 9345083308624553/19013690936000000 ≈ 0.4915 ≥ 2/5
at ε = 1/100; v(TFT,TFT) = 9/4 exactly at EVERY grid ε (the ε-independent echo
identity — a 25% cooperation tax that does not shrink as execution improves);
rank(TFT) strictly worse than rank(WSLS) at every grid ε (9 vs 5 dense, at all
four ε); v(WSLS,WSLS) = 737773/250000 = 2.951092 ≥ 14/5 at ε = 1/100.

Headline anomaly (first-class, reported, ruling-neutral): the drafter's
disclosed rank(TFT) = 10 is the COMPETITION-rank rendering; the registered
DENSE rank gives 9 — two rules, (0,0,1,1) and (1,1,0,0), tie at exactly 9/4
above TFT at every grid ε. Every decision conjunct is purely relational and
identical under both conventions.

# VERDICT 235 — Revenue equivalence: first-price = second-price = (n-1)/(n+1)

Reproduces idea-engine PROPOSAL 222. Verifier copied byte-identical from the proposal's
`ideas/venture-lab/revenue-equivalence-first-second-price.py`; re-run here reproduces the
disclosed digest exactly.

## Claim under test
For n bidders with i.i.d. Uniform(0,1) private values, a sealed-bid first-price auction
(symmetric BNE bid b(v)=(n-1)/n*v) and a sealed-bid second-price (Vickrey) auction yield the
same expected seller revenue, exactly (n-1)/(n+1) — not the winner's value n/(n+1). The winner
keeps an information rent 1/(n+1) that vanishes as n grows.

## Reproduction
- SEED=20260717, stdlib-only, single random.Random consumed in a fixed order.
- Determinism: double-run in-process AND a separate re-invocation are byte-identical.
- results_sha256 = b22b9f2767755feb2334594f2671060c61818e192ee3c24b99f9705e3f9951d2 (full 64 hex; matches the proposal's disclosed digest).

## Gates (each read in its own direction) — all PASS
- G1 EXACT identity (fractions.Fraction): fpa_revenue == spa_revenue == (n-1)/(n+1) for n in {2,3,5,10,20,50}, formed by exact integration (integral of x^j over [0,1] = 1/(j+1)). Rationals: 1/3, 1/2, 2/3, 9/11, 19/21, 49/51.
- G2 Monte-Carlo agreement (|z|<3): z_fpa=1.343, z_spa=0.155, paired z_diff=0.958.
- G3 robustness: monotone n-sweep {n2:1.696, n5:-0.366, n10:0.666, n50:-0.145} all agree; scale invariance under U(0,k) exact and empirical (z_fpa=-1.104, z_spa=-0.373).
- G4 falsifiability (|z|>5 to reject): the naive "revenue = winner's value = n/(n+1)" model is rejected at z=-612.81, while the true model holds (z=0.639). The rejected gap equals the information rent 1/(n+1).

## Ruling
APPROVE — digest reproduced to the full 64 hex, all four gates pass in their stated directions.

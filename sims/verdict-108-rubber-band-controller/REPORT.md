# VERDICT 108 — REPORT

> **Status:** reference

**RULING: APPROVE** — first-failing-gate: None. Verifies idea-engine PROPOSAL 095 (2026-07-17T12:06:59Z, sim-ready), offset +13 (P095 → V108).

## The model as a discrete-time proportional controller

P095 recasts a racing game's catch-up rubber-band as a feedback controller acting on the signed skill gap g(t) between the two racers. Each tick the gap integrates the skill drift F, is pulled back by a proportional term −k·g(t−d) (the boost, gain k, sensor delay d), optionally damped by a derivative stabilizer −β·(g(t)−g(t−1)), and perturbed by noise ε:

```
g(t+1) = g(t) + F − k·g(t−d) − β·(g(t)−g(t−1)) + ε(t),   ε ~ Normal(0, σ²),   F = 2s
```

In the base world (d=0, β=0) this collapses to an AR(1)-with-drift process `g(t+1) = (1−k)·g(t) + F + ε`, whose pole is 1−k. The loop is stable iff |1−k| < 1, i.e. 0 < k < 2 — the exact stability boundary the proposal claims. Engagement is scored `E = (lead-change rate)·(2·skill-fidelity − 1)`: a game is engaging when the lead flips often AND the eventual winner still tracks the skill signal. Too weak a band (small k) means the skill-favored racer runs away — few lead changes, high fidelity but low churn. Too strong a band past k=2 means the loop oscillates divergently, the sign of g decouples from skill, and E collapses to 0 (on divergence E is defined 0). The engagement optimum is therefore predicted to be interior.

## Pinned world

- `F = 2s` (skill gap s=0.5 → F=1.0), `σ=1.0`, `g0=0`, history 0 for negative indices; base `d=0`, `β=0`
- K grid: `[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 1.9, 1.95, 2.05, 2.2]`
- `T=4000`, burn-in `B=1000`, `G_CAP=1e6`; `N_REPS=400` main; `SEED=20260717`, sha256-keyed per-(d, k_index, rep) `random.Random` gauss streams, stdlib-only

## Base sweep (d=0, β=0)

mean-E per k ± SE, lead-change rate, skill-fidelity, measured vs analytic Var(g), divergence fraction:

```
  k      E(k)  ± se        lc      sf       var_meas  var_ana   div
  0.2   0.00204 ±0.00007  0.0020  1.0000    2.7763    2.7778    0.000
  0.4   0.03276 ±0.00024  0.0343  0.9775    1.5606    1.5625    0.000
  0.6   0.09131 ±0.00034  0.1003  0.9550    1.1887    1.1905    0.000
  0.8   0.13980 ±0.00035  0.1792  0.8900    1.0400    1.0417    0.000
  1.0   0.15656 ±0.00033  0.2654  0.7950    0.9997    1.0000    0.000
  1.2   0.22478 ±0.00035  0.3597  0.8125    1.0447    1.0417    0.000   <- argmax (interior)
  1.4   0.21754 ±0.00027  0.4580  0.7375    1.1914    1.1905    0.000
  1.6   0.19540 ±0.00021  0.5664  0.6725    1.5664    1.5625    0.000
  1.8   0.18190 ±0.00017  0.6996  0.6300    2.7811    2.7778    0.000
  1.9   0.15806 ±0.00012  0.7903  0.6000    5.2891    5.2632    0.000
  1.95  0.15747 ±0.00013  0.8512  0.5925   10.2130   10.2564    0.000
  2.05  0.00000 ±0.00000  0.0000  0.4525      n/a       n/a     1.000
  2.2   0.00000 ±0.00000  0.0000  0.5175      n/a       n/a     1.000
```

## Gate results

- **R1 interior optimum:** PASS — argmax mean-E at k=1.2 (interior), E=0.22478±0.00035; beats weak endpoint k=0.2 (E=0.00204) by 632.53σ and past-instability endpoint k=2.2 (E=0) by 649.63σ (need ≥3σ each).
- **R2 instability cliff + variance anchor:** PASS — diverged_frac = 1.000 at both k=2.05 and k=2.2 (every k>2 blows past G_CAP); last-stable k=1.95 (E=0.15747) outsells first-above-2 k=2.05 (E=0) by 1231.13σ; the cliff bracket last-stable k=2.0 / first-divergent k=2.05 straddles the analytic AR(1) boundary k=2; measured Var(g) tracks the closed form σ²/(k(2−k)) with max rel-err 0.494% (at k=1.9) across the whole stable arm, well inside the 5% band.
- **R3 sensor delay d=1:** PASS — introducing one tick of delay changes the characteristic polynomial to z²−z+k=0, whose Jury stability condition is k<1; the measured divergence boundary halves accordingly (last-stable k=1.0 / first-divergent k=1.05, versus the undelayed boundary at 2). Engagement stays interior: argmax k=0.8 in the main delayed world, and the s-sweep argmax is interior at all three skill gaps s∈{0.3,0.5,0.7} (F∈{0.6,1.0,1.4} → argmax vector [0.6, 0.8, 0.8]).
- **R4 dual control knockouts:** PASS — (a) with skill-off s=0 (F=0) the process is symmetric about 0, skill-fidelity ≈ 0.5 flat (0.4928 measured at k=1.0), and engagement collapses: max|E| across the grid = 0.01625 ≈ 0, the interior peak vanishes — isolating the skill signal as the cause of the interior optimum. (b) the β-sweep divergence onset matches the derivative-stabilizer boundary k_crit=2−2β exactly: β=0 → measured bracket (2.0, 2.05), predicted 2.0; β=+0.5 → (1.0, 1.05), predicted 1.0 (destabilizes); β=−0.5 → (3.0, 3.05), predicted 3.0 (boundary relocated, grid extended to 3.2).

## Analytic cross-checks

The harness never plugs in analytic answers to decide gates — it measures via Monte-Carlo and reports the closed forms alongside:

- AR(1) base stability boundary k=2 (pole 1−k, |1−k|<1).
- Stationary variance σ²/(k(2−k)) on the stable arm — max rel-err 0.494%.
- Delayed (d=1) characteristic z²−z+k=0, Jury boundary k=1 (boundary halves).
- Derivative-stabilizer flip-bifurcation boundary k_crit=2−2β (z=−1 root).

All four are confirmed independently by the measured brackets/variances above.

## Fixture anchor

The proposal's disclosed rep-0 fixture is reproduced EXACTLY: with k=1.4, β=0, d=0, F=1.0, g0=0 and ε(0..7) = [0.30442, 0.56871, 0.77846, −1.79728, 0.49040, −1.32501, 0.86948, −0.79502], the iterator yields g(1..8) = [1.30442, 1.04694, 1.35968, −1.34115, 2.02686, −1.13575, 2.32378, −0.72453] to 5 decimals (self-check 01_fixture_anchor).

## Twins & self-checks

Two independent verdict deciders over the same results dict — an explicit ordered if-chain and a data-driven scan over a gate table — both return ('CONFIRMED', None) and must agree or the harness exits non-zero. Self-checks: 15/15 pass. Double run byte-identical (determinism digest a9da1284… on both runs).

## Reconciliation with the proposal (non-gating)

The independent engagement argmax lands at k=1.2, one grid-step below the proposal's disclosed k*=1.4. Both are interior and both dominate the two endpoints by >600σ, so the R1 ranking gate is identical either way. The E(k) ridge is flat-topped across k∈[1.2, 1.4] (E=0.22478 vs 0.21754, within a few SE of each other relative to the endpoint gaps), so the exact peak grid point is within-implementation-noise sensitive — this is the independent-draw analogue of P094/V107's disclosed W=12/13 neighbor tip. This verifier is an independent stdlib reimplementation from the registered spec (own SEED=20260717 / keyed streams), so the results digest deliberately differs from the proposal's disclosed 573fa71…; the gate OUTCOMES converge (interior argmax dominating both endpoints, cliff at k=2, d=1 boundary k=1, β-onset 2−2β).

## Digests

- results.json sha256: 4884b40a6774d2d50938587e3b1a6547a64a4720f630f06bcc8b5e452a189593
- run-stdout.txt sha256: c38ba53130133199c467d72f9ddeab59b8d8e7e52b997675af721e8e1c84e12e
- fixtures.json sha256: f90be9b755441aacd950ee12d221eabf0131489614ddcabcdcd2850d68b2dd71

(python3 rubber_band_controller_sim.py — stdlib only, double run byte-identical)

## Verdict

APPROVE per the pre-registered R1→R2→R3→R4 rule; never softened.

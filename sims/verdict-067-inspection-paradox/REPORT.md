# VERDICT 067 — REPORT — the inspection paradox at equal means

Registration: idea-engine PROPOSAL 056 — `## PROPOSAL 056 · 2026-07-14T02:52:22Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main adc641fe33c479d74ff60b0614725477058c53a8, landed via idea-engine
PR #387; idea doc `ideas/fleet/inspection-paradox-wait-inflation-2026-07-14.md` @ ae0e038).
Run: `python3 sims/verdict-067-inspection-paradox/inspection_paradox_sim.py` — exit 0,
`SELF-CHECKS: 83 passed, 0 failed`, byte-identical across two full process runs by external sha256
(run-stdout `8f1c00f5426673cd071561369498b23253aaf56ea875286487f176fb6bffaf5b`, results
`754074607c26ce69e3bf8184ec88ffdc627292a62b31127649d29e3020400c39`), CPython 3.11 pinned and
asserted, stdlib-only, hermetic (reads only its own `fixtures.json`), no wall-clock in any output.

## Ruling — INVALID (the registration's own "controls misbehaving — report, no ruling" branch)

Rules executed in the REGISTERED order (REJECT → INVALID → APPROVE → NULL), twin
independently-written evaluators agreeing at every step:

1. **REJECT — does NOT fire, on its third conjunct only.** The two science conjuncts hold
   exactly in Arm A: ρ(BUNCHED) = 89/25 = 3.56 ≥ 2 ✓, and ρ ≥ 11/10 in **3 of 4** stochastic
   cells (SPREAD = 11/10 exactly ON the registered edge, counted by the rule's own ≥;
   MEMORYLESS 19/10; BUNCHED 89/25; JITTER 26/25 genuinely APPROVE-side) ✓. The third
   conjunct — "Arm S confirms within the agreement gate on every stochastic cell" — is
   FALSE: the SPREAD cell breaches the gate's 1/100-relative half on P(W > 10)
   (est 0.134625 vs exact 3/22 = 0.1363…; relative deviation 0.01275 > 1/100) while
   passing its 4·SE half (deviation = 2.27·SE ≤ 4·SE).
2. **INVALID — FIRES**: "…or the Arm-S agreement gate failing on any cell". Report, no ruling.
3. APPROVE / NULL — not reached.

The blocked REJECT is a **gate artifact, not a science failure**: the decision arm confirms
the drafter's disclosed landing direction on every exact number, and the trajectory-conditional
diagnostic (below) shows the MC arm is unbiased — the breach is an ordinary ~2.3σ noise draw
inside a registered band only ~1.78σ wide.

## Arm A (DECISION, seedless exact Fractions) — all F1–F5 control gates green

| cell | Var | E[W] | E[L] | ρ = 1 + CV² | P(W>5) | P(W>8) | P(W>10) | P(W>15) | median W | P90 W |
|---|---|---|---|---|---|---|---|---|---|---|
| CLOCKWORK | 0 | 5 | 10 | 1 (= 1.0) | 1/2 | 1/5 | 0 | 0 | 5 | 9 |
| JITTER | 4 | 26/5 | 52/5 | 26/25 (= 1.04) | 1/2 | 1/5 | 1/10 | 0 | 5 | 10 |
| SPREAD | 10 | 11/2 | 11 | 11/10 (= 1.1) | 1/2 | 14/55 | 3/22 | 0 | 5 | 54/5 |
| MEMORYLESS | 90 | 19/2 | 19 | 19/10 (= 1.9) | (9/10)^5 | (9/10)^8 | (9/10)^10 | (9/10)^15 | ≈ 6.592 | ≈ 21.861 |
| BUNCHED | 256 | **89/5 = 17.8** | 178/5 | **89/25 = 3.56** | 37/50 | 17/25 | 16/25 | 27/50 | **17** | **37** |

- Folk rule (ρ = 1, E[W] = 5) vs BUNCHED: the mean-10 bunched schedule makes the average
  random arriver wait **17.8 min — 1.78× the entire mean headway**, 3.56× the folk figure.
- Rider-vs-operator table at BUNCHED: the 42-min gap is **1/5** of intervals (operator view)
  but carries **21/25 = 84%** of riders (length-biased rider view); P(W > 10) = 16/25.
- F1 pmf re-derivation (mass 1, mean exactly 10 per cell, variances {0, 4, 10, 90, 256}
  exact; geometric closed forms == exact rational partial sums to K = 500 + exact
  shift-identity tails, for E[X], E[X²], E[X³] and every E[(X−w)⁺] on the grid) — green.
- F2 size-bias identities (E[L] = E[X²]/E[X] two independent ways — moment ratio vs
  expectation under the explicitly size-biased pmf — and E[W] = E[L]/2 exact) — green.
- F3 CLOCKWORK degenerate (ρ = 1, P(W > 10) = 0, E[W] = 5 exact) — green.
- F4 monotonicity (ρ = 1 + Var/100 exact per cell; variance rank == ρ rank — the
  mean-preserving-spread ordering; P(W > w) non-increasing in w per cell) — green.
- F5 hand identities (JITTER P(W > 8) = 1/5, E[W] = 26/5; BUNCHED rider share 21/25,
  interval share 1/5, P(W > 10) = 16/25; MEMORYLESS P(W > 10) = (9/10)^10) — green.

## Arm S (confirmation, seed 20261361, K = 100,000 / N = 200,000 per stochastic cell)

Pinned draw order JITTER → SPREAD → MEMORYLESS → BUNCHED, all intervals before any landing
(per cell, the fixture-pinned reading), geometric as count-of-Bernoulli(1/10)-trials, waits
via bisect. Draw-count sentinels exact per cell (K interval draws for JITTER/SPREAD/BUNCHED;
T = sum-of-intervals draws for MEMORYLESS: 997,056; N landing draws everywhere). RNG registry
= [20261361, 20261362, 20261363] only; aux 20261364 asserted never read.

| cell | mean_W (exact) | rel dev | dev/SE | P̂(W>10) (exact) | rel dev | dev/SE | gate |
|---|---|---|---|---|---|---|---|
| JITTER | 5.20873 (5.2) | 0.00168 | 1.22σ | 0.100725 (0.1) | 0.00725 | 1.08σ | PASS |
| SPREAD | 5.48924 (5.5) | 0.00196 | 1.33σ | 0.134625 (0.13636) | **0.01275** | 2.27σ | **FAIL (P rel half only)** |
| MEMORYLESS | 9.47005 (9.5) | 0.00315 | 1.41σ | 0.347935 (0.34868) | 0.00213 | 0.70σ | PASS |
| BUNCHED | 17.79418 (17.8) | 0.00033 | 0.20σ | 0.638420 (0.64) | 0.00247 | 1.47σ | PASS |

Unbiasedness diagnostic (session-side, not decision-bearing): the SPREAD trajectory-conditional
exact P(W > 10 | trajectory) = 0.136586 sits within trajectory noise of the true 3/22; the
landing estimate deviates from it by ordinary landing noise. The implementation is sound; the
seed draw is what it is.

Stability leg (seed 20261362, K = 20,000 / N = 50,000): mean_W {5.18218, 5.50904, 9.58772,
17.69405}, P̂(W>10) {0.09774, 0.13688, 0.34878, 0.63838}; its gate breaches on JITTER
(relative 0.0226 > 1/100 at 1.69·SE) → stability class **INVALID through both twin
evaluators — reproduces the headline class** (degenerately: both land INVALID via a
noise-draw breach of the same under-powered band, on different cells).

Reporting leg (seed 20261363, K = 20,000 / N = 50,000, never decision-bearing) — median/P90
rows, MC vs exact piecewise-linear inversion: JITTER 5.006/10.024 (exact 5/10), SPREAD
5.008/10.810 (exact 5 and 54/5 = 10.8), MEMORYLESS 6.477/21.273 (exact ≈ 6.592/≈ 21.861),
BUNCHED 17.019/36.919 (exact 17/37).

## First-class findings (anomalies)

- **A1 — the registered agreement gate is under-powered by construction on the probability
  metric.** The 1/100-RELATIVE half on P(W > 10) is the binding half wherever p < 4/9 (i.e.
  on 3 of the 4 stochastic cells at the headline N): the band is 1.49σ wide on JITTER, 1.78σ
  on SPREAD, 3.27σ on MEMORYLESS at N = 200,000 — a PERFECT implementation passes all four
  headline cells with probability ≈ 0.80, and the stability leg (N = 50,000: 0.75σ / 0.89σ /
  1.63σ bands) with probability ≈ 0.30. INVALID was therefore the MODAL outcome of a correct
  sim under this registration (≈ 0.76 chance of at least one breach across both legs). The
  V064-precedent gate used 1/100 ABSOLUTE, which is 13σ wide on these cells; the switch to
  relative is the defect. Every breach observed is ≤ 2.3·SE — noise, not bias.
- **A2 — the gate sentence admits a second parse and the class flips under it.** Registered
  text: "agreement gate |mean_S − E_A|/E_A ≤ 1/100 AND ≤ 4·SE on E[W] AND on P(W > 10) per
  cell". Adopted (fixture-pinned before the runner): both halves on both metrics — the
  literal AND and the V064-gate precedent pattern. Under the alternative "respectively"
  parse (1/100-relative on E[W]; 4·SE on P(W > 10)), every cell passes both legs — visible
  directly from the committed per-cell sub-booleans in results.json (all `E_W_rel_ok` true,
  all `P_4SE_ok` true, headline and stability) — and **REJECT would fire**. The class is
  parse-dependent; the adopted parse is the stricter, more literal one.
- **A3 — stream-interpretation pin (disclosed pre-run).** "All intervals before any landing"
  was applied PER CELL on a single sequential RNG stream (fixture-pinned before the runner
  existed). Because the class hinges on a ~2.3σ noise draw, other defensible stream
  interpretations could land either class. No alternative streams were run (RNG-registry
  discipline); the pin plus A1 make the class seed-lottery-dependent by construction.
- Drafter-reference comparison (never gated): **every disclosed exact value reproduces from
  scratch** — ρ {1, 26/25, 11/10, 19/10, 89/25}, BUNCHED E[W] = 89/5, rider share 21/25,
  P(W > 10) = 16/25, geometric moments, the 19/10-vs-2 discretization gap. The disclosed
  expected landing (REJECT) does NOT land — blocked purely by the confirmation-gate artifact
  A1, not by any drafter arithmetic error. No drafter anomalies found.
- Done-when deviation, disclosed: the registration's done-when says the verdict "issues
  exactly ONE of APPROVE/REJECT/NULL" — the controls branch intercepted, so NO ruling issues;
  INVALID is itself the registered report-no-ruling outcome and is ledgered as such.

## Registered boundaries (carried verbatim)

i.i.d. headways (real bunching is positively correlated → the length-biased experience gets
WORSE; a REJECT direction is robust in the costly direction — the correlated variant is the
named follow-up); continuous-uniform landing within integer-minute gaps (integer-landing
alternatives shift E[W] by ≤ 1/2 min, reporting-only); discretization (continuous-exponential
analog ρ = 2 exactly; the discrete geometric lands 19/10 — disclosed, not laundered).

## Validity gates

- **COMPARABLE**: every decision number is an exact Fraction under the registration's own
  pinned frame; fixtures.json values copied verbatim from the PROPOSAL 056 block / idea doc;
  all fixture-level choices disclosed IN fixtures.json before the runner existed (stream
  reading, draw maps, SE convention, gate parse, reporting-leg size, twin evaluators).
- **UNCORRUPTED**: fixtures committed BEFORE the runner (PR #125 git trail: born-red card →
  fixtures → runner + accepted run); bands, seeds, draw order, evaluation order all
  registered in PROPOSAL 056 before this session existed; 83 self-checks 0 failed; no
  fix-forwards — the first complete run of the registered pipeline is the accepted run (the
  ruling INVALID was accepted as-is; nothing re-run, no alternative seeds or streams tried);
  the drafter's disclosed landing re-derived from scratch with zero trust.
- **ROBUST — with named caveats**: the Arm-A exact table is maximally robust (platform-
  independent rationals; SPREAD's edge placement is the registration's own deliberate pin).
  The CLASS is not robust and this is disclosed as the finding, not smoothed: it rides a
  2.27σ noise draw inside a 1.78σ band (A1) and flips under the alternative gate parse (A2).
- **REPRODUCIBLE**: one command, no flags, stdlib-only, hermetic; stdout + results.json
  byte-identical across two full process runs by external sha256 (hashes above); CPython 3.11
  pinned and asserted; seeds 20261361/62/63 the only RNGs constructed, in pinned order, aux
  20261364 never read, all strictly above the P055 high-water 20261360 — new registry
  high-water 20261364 (reserved) / highest READ 20261363.
- **LIMITS**: model-true under the registered frame, not a live measurement — the schedules
  are invented-but-pinned equal-mean constants; the i.i.d./incidence/discretization
  boundaries above; the exact-variance SE convention and the reporting-leg size are
  fixture-level choices; the gate verdict INVALID is a statement about the REGISTRATION'S
  confirmation gate, not about the inspection-paradox math, which Arm A settles exactly.

# VERDICT 073 — REPORT — owner-queue attention order: the derived publish queue's decisions-first + document-order presentation priced as an owner-attention policy through its committed "go with defaults" door (INTAKE 062)

**Class: APPROVE** (pre-registered rules applied in order: REJECT → INVALID →
APPROVE → NULL; REJECT checked FIRST fires on none of R1–R3; APPROVE holds on
all five conjuncts A1–A5).

Source: idea-engine `## PROPOSAL 062 · 2026-07-14T08:19:10Z · status: sim-ready`
(idea-engine PR #410 @ main be34370; idea doc
`ideas/venture-lab/owner-queue-attention-order-2026-07-14.md`; where the doc
and the block differ, the block wins — no disagreement found). Fully
hermetic: every fixture constant pinned in the PROPOSAL 062 block / idea doc,
copied verbatim into the committed `fixtures.json`; the runner reads only
that file; zero repo/network reads at verdict time. The drafter's disclosed
prototype landing was re-derived from scratch with ZERO trust and compared
NEVER gated.

## Reproducibility

- `SELF-CHECKS: 117 passed, 0 failed`, exit 0, ~18 s/run, stdlib-only,
  hermetic (reads only its own `fixtures.json`), CPython 3.11 pinned and
  asserted.
- Byte-identical across two full process runs by external `diff` + sha256:
  `run-stdout.txt` = `72e3df99ceac8df52802583d79650c6fd194d20ecdda80e3b5492d9fe4034a1f`,
  `results.json` = `f79c1fced8167def75c5a43a2281e9ba881efcc41c45db679e4d746ae02ea150`.
- Seeds: 20261385 main / 20261386 stability / 20261387 presentation — the
  ONLY three RNGs constructed (asserted, pinned order); aux 20261388 NEVER
  read (asserted against the constructed-seeds registry).
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run. Fixtures committed BEFORE the runner (git trail: fixtures
  673d133 precede the runner commit).
- Every decision number is a seedless exact integer / `fractions.Fraction`;
  the seeded Arm-R legs are REPORTING-ONLY and carry no statistical gate
  (their only gates: the one-uniform-per-sitting draw sentinel, exact at
  16,625,466 main + 3,325,706 stability calls, aux-never-read, and byte
  reproducibility) — joint gate pass probability 1 for a correct
  implementation, as registered.

## Decision conjuncts (registered order, REJECT first — none fire; APPROVE all five)

REJECT (checked FIRST, all on BATCHED best-non-DOC comparisons): **R1**
gapMEAN = 72/11 ≈ 6.545 < 10 — no fire; **R2** ratioV(99/100) ≈ 1.068090 <
11/10 — no fire; **R3** TTF(DOC) = 7 < 3 × TTF(best) = 12 — no fire.
INVALID: all F1–F6 gates green (below). APPROVE — all five:

1. **A1:** gapMEAN(BATCHED) = MEAN(DOC) − MEAN(SPT) = 2835/22 − 2691/22 =
   `72/11` ≈ 6.545 ≤ 8 (clears by 16/11 ≈ 1.45; sits 38/11 ≈ 3.45 below the
   R1 line). Best non-DOC MEAN is SPT.
2. **A2:** ratioV(BATCHED, γ = 99/100) = V(SPT)/V(DOC) ≈ 1.068090 < 11/10
   (V(DOC) ≈ 15.650032, V(SPT) ≈ 16.715645, exact Fractions in
   results.json).
3. **A3:** TTF(DOC, BATCHED) = 7 ≤ 2 × TTF(best) = 8 (best: SPT at 4 — the
   layer reply then the 3-click V020 probe).
4. **A4:** gapMEAN(PER-ITEM) = MEAN(DOC) − MEAN(LAZY-SPT) = 3231/22 −
   2855/22 = `188/11` ≈ 17.091 ≥ 15 (best non-DOC flips to LAZY-SPT —
   deferral becomes the winning lever once the layer costs 19).
5. **A5:** TTF(DOC, PER-ITEM) = 25 ≥ 4 × TTF(best, PER-ITEM) = 20 (best:
   LAZY-SPT at 5 — nineteen replies before the first title vs a 5-click run
   up front).

REJECT was arithmetically foreclosed given A1–A3 (mutually exclusive on
every paired clause). Falsifiability behaved as registered: the γ = 49/50
impatience leg lands ratioV ≈ 1.134052 ≥ 11/10 (the disclosed live edge —
one attention-span step moves the ratio clause over the REJECT line;
reporting-only, the decision cell stays 99/100), and the order-insensitive
NULL axis was live until the PER-ITEM row existed (A4/A5 both clear it).

## Gates (all green)

- **F1** data identity: the fixture's 44 rows recompute to the committed
  roll-ups exactly — 28 + 16 rows, sums 152 + 110 = 262, 16 gated flags, 19
  decisions, count vectors verbatim; all four numbers equal the committed
  current-state sentence quoted in the fixture.
- **F2** conservation: final clock exactly 263 BATCHED / 281 PER-ITEM for
  every policy; all 44 live at the end; every live curve nondecreasing,
  stepping by exactly 1 at each of 44 completions, both accountings.
- **F3** sequencing theorems on the real committed data: (a) EXCHANGE — all
  43 adjacent transpositions of SPT weakly increase MEAN (each swap's effect
  asserted exactly equal to (n_j − n_i)/44 ≥ 0) and weakly decrease V_γ at
  every grid γ, both accountings; (b) POINTWISE DOMINANCE — L_SPT(t) ≥
  L_DOC(t) and L_SPT(t) ≥ L_LPT(t) at EVERY t, and L_LAZY-SPT(t) ≥
  L_LAZY-DOC(t) at every t, both accountings; (c) V-anchor — V(SPT) > V(LPT)
  at every grid γ, both accountings.
- **F4** hand world ({ungated 2, ungated 1, gated 3}, BATCHED layer 1): DOC
  clocks (3, 4, 7) MEAN 14/3 TTF 3; SPT (2, 4, 7) MEAN 13/3 TTF 2; LAZY-SPT
  (1, 3, 7) MEAN 11/3 TTF 1 — all reproduced exactly, both arms (the
  registered "LAZY" row's by-hand clocks identify it as LAZY-SPT, disclosed
  in the fixture before the runner existed).
- **F5** γ-monotonicity: V_γ strictly increasing over the grid for every
  policy, both accountings.
- **F6** battery: Arm B (independently-written tick-by-tick event-walk with
  its own selection-loop order builders) exact-equal on every published
  number — all 10 main-world cells (clocks, full live curves, TTF, T22,
  MEAN, V at all three γ), all 10 hand-world cells, all 10 V020-exclusion
  cells; twin decision evaluators (evaluator 2 re-reads Arm-B numbers with
  independently-written integer cross-multiplication band logic) agree on
  the token APPROVE/APPROVE; draw sentinels exact; aux seed never read;
  byte-identical double run; CPython minor pinned.

## Anomalies (first-class findings)

None. Every drafter-disclosed value reproduced from scratch: MEAN(DOC) =
2835/22 and best SPT 2691/22 digit-for-digit, gap 72/11, V floats 15.6500 /
16.7156, ratio 1.0681, TTFs 7/4 and 25/5, PER-ITEM 3231/22 vs LAZY-SPT
2855/22 and gap 188/11, the 49/50 ratio 1.1341, the LPT anchor 1624/11, the
+18 / 3.57× batch-door price, and the V020-exclusion identity — see
`drafter_comparison_never_gated` in results.json (20/20 true, never gated).

## Reporting legs (ungated)

- **Batch-door price (same order, PER-ITEM minus BATCHED):** DOC +18 mean
  interactions EXACTLY and TTF × 25/7 ≈ 3.571 — the committed "go with
  defaults" one-word reply is worth 18 mean interactions and 3.6×
  time-to-first-title at these counts (load-bearing design, not
  convenience). SPT +18, TTF × 5.5; LPT +18, TTF × 2.8; the LAZY policies
  pay only +72/11 ≈ 6.55 mean (deferral shields the 28 ungated titles from
  the layer entirely) with TTF × 1.
- **LPT anchor:** MEAN(LPT, BATCHED) = 1624/11 ≈ 147.64 — the whole
  order-choice space spans ≈ 25.3 mean interactions (1624/11 − 2691/22).
- **γ sweep (ratioV, BATCHED):** 49/50 ≈ 1.134052 (≥ 11/10 — the disclosed
  crossing, named, never flipping the 99/100 decision cell); 99/100 ≈
  1.068090; 199/200 ≈ 1.033611.
- **T22 (BATCHED):** DOC 119, SPT 114, LPT 150, LAZY-DOC 118, LAZY-SPT 116 —
  by mid-list the order barely matters; the gap lives in the early curve.
- **V020-exclusion leg:** dropping the 3-click probe row re-lands every
  decision clause identically (43-row world: gapMEAN B = 186/43 ≈ 4.33, PI =
  690/43 ≈ 16.05, TTF pairs 7/5 and 25/5 — all eight booleans unchanged).
- **Arm R sitting traces** (pmf {3: 1/2, 8: 3/10, 21: 1/5}, reporting-only):
  main leg (20261385, N = 100,000/policy) mean sittings-to-first-live DOC
  1.746 / SPT 1.502 / LPT 2.178 / LAZY-DOC 1.500 / LAZY-SPT 1.498; mean
  titles live after 1/3/10 sittings DOC 0.90/3.71/14.13, SPT
  1.10/4.80/15.63, LPT 0.40/2.33/10.48, LAZY-DOC 0.90/3.71/14.29, LAZY-SPT
  1.11/4.31/15.58. Stability leg (20261386, N = 20,000) consistent. Trace
  vs exact-curve mismatches: 0 in 16,625,466 + 3,325,706 sittings — no
  drift finding.
- **Presentation order:** seed 20261387 read by the stdout
  presentation-shuffled cell listing only.

## Boundaries (as registered)

Equal-cost interaction units (no per-click duration data exists; the named
free measured replacement is a one-sitting timestamp ledger — the machinery
re-weights unchanged). The precedence boundary: the 10 NL-edition "EN
edition published first" rows and the V020 probe's cross-sequence publish
clicks ride INSIDE the committed counts and the reorderings ignore them;
direction stated — document order already respects the precedence, so
enforcing it can only shrink the non-DOC optima toward DOC: the measured
gap is an UPPER bound on achievable gain, GENEROUS TO REJECT, and this
APPROVE is robust in the direction that matters; the V020-exclusion leg
additionally lands every clause identically. The attention boundary: γ
invented, bracketed by the grid, the 49/50 crossing disclosed and named;
the Arm-R sitting pmf invented and reporting-only. The generated-file
boundary: the queue regenerates on every packet change — APPLICATION GUARD,
two conditions: (1) the verdict conditions on the derived queue @ 68d57bb
(44 sequences / 262 clicks / 16 gated / 19 decisions) — a re-derived queue
is NEW data: re-run, not reuse; (2) it conditions on the equal-cost unit
model — the ledger measurement replaces it.

## Transferable law (pre-registered APPROVE consequence, verbatim-faithful)

The queue's decisions-first document order is attention-near-optimal under
its own committed batch reading AND the batch door is load-bearing: the
near-optimality is mostly INHERITED STRUCTURE (the document already fronts
the shorter ungated block — the residual sort-within-blocks gain is only
72/11 ≈ 6.5 mean interactions), while forgoing the one-reply defaults path
costs +18 mean interactions and 25/7 ≈ 3.6× time-to-first-title at the SAME
order. The cheap win on any derived to-do surface is almost always NAMING
THE BATCH DOOR, not resorting the list. Paste-ready doc line recommended
first per Q-0263.2: "reply 'go with defaults' FIRST — one word; answering
D-items one at a time costs ≈ +18 mean interactions and 3.6×
time-to-first-title at these counts", plus the optional one-line
ascending-clicks sort in `derive_owner_queue.py` worth the measured
residual ≈ 6.5 — an owner/lane intent call, never ruled by fiat here.
Transfer surface: every derived to-do surface in the fleet (review queues,
owner-action sections, wake-chain checklists) — fixed-list attention
sequencing with a deferred-gate layer. Routing is the manager's per Q-0260 —
this repo edits no venture-lab files; nothing here builds, publishes, or
spends.

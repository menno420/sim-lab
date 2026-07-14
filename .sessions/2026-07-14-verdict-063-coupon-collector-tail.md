# Session — VERDICT 063 — Coupon collector's tail: does "almost complete" mean "almost done" — what share of the expected draws does the last ⌈N/10⌉ of a uniform random-draw collection cost? (idea-engine PROPOSAL 052, ORDER 003 COMPLETELY-UNRELATED rotation slot, round 9 closer)

> **Status:** complete
> 📊 Model: Claude Fable (family) · 2026-07-14 · verdict-063 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 052 (`## PROPOSAL 052 · 2026-07-14T00:26:42Z · status: sim-ready`, landed via idea-engine PR #375 → main cdf3e2ebe0dfb86806b7ab4fdb979b8810ffcb46; claim landed FIRST via idea-engine PR #377, `control/claims/2026-07-14-verdict-063.md`, reserving the P052 intake + VERDICT 063 and this branch `claude/verdict-063-coupon-collector-tail`; numbering INTAKE = proposal number, PROPOSAL 052 → VERDICT 063 per the established P050→V061 / P051→V062 offset map — V062 is IN FLIGHT in a parallel session on `claude/verdict-062-chicken-farm-faucet`, no overlap, its files/claim/numbers untouched from here) — measure the coupon collector's tail against the "almost complete = almost done" folk belief, per the idea doc `ideas/fleet/coupon-collector-tail-2026-07-14.md` @ idea-engine main cdf3e2e. Pinned model: uniform iid draws over N distinct items, one item per draw; decision grid N ∈ {20, 50, 100, 200} with last-10% tail m(N) = ⌈N/10⌉ = {2, 5, 10, 20}, decision cell N = 50; E[T_N] = N·H_N, E[tail_m] = N·H_m, tail-cost fraction φ(N) = H_m/H_N, all exact fractions.Fraction; inclusion–exclusion CDF P(T_N ≤ t) = Σ_{j=0}^{N} (−1)^j C(N,j)(1−j/N)^t for the F5 identity and the overshoot report P(T_50 > 2·E[T_50]); last-single-coupon share 1/H_N. Arm A = DECISION (seedless exact rationals, alone decision-bearing, twin independently-structured computations); Arm S = confirmation (seed 20261345, N_runs = 200,000/cell draw-until-complete, agreement gate |mean_S − E_A|/E_A ≤ 1/100 AND ≤ 4·SE on E[T_N] and φ per cell); stability leg seed 20261346 (N = 20,000, ruling reproduced through twin independently-written evaluators); reporting-only legs seed 20261347 (last-20% alternative m = ⌈N/5⌉; weighted rarity-tier collector, pinned tiers 70%/25%/5% mass over the first 0.7N / next 0.25N / last 0.05N items, MC only — never flip the decision); aux seed 20261348 reserved, never read. Decision rule pre-registered, applied IN ORDER: REJECT FIRST (φ(50) ≥ 2/5 AND φ ≥ 2/5 in ≥ 3 of 4 cells AND Arm S confirms) → INVALID (any control gate F1–F5 / agreement fails — report, no ruling) → APPROVE (φ ≤ 1/5 at EVERY N AND stability reproduces) → NULL (pre-registered axes: band-straddle, N-sensitivity, weight-sensitivity, arm disagreement). Gates F1–F5 (harmonic re-derivation incl. H_5 = 137/60, H_10 = 7381/2520; linearity/stage-accounting identity; φ(m=N) = 1 and φ(m=1) = 1/H_N; monotonicity theorems; small-N exact-CDF vs full enumeration at N ∈ {2,3} with E[T_2] = 3, E[T_3] = 11/2) + per-leg draw sentinels + two-process byte identity by external sha256 + CPython minor pinned. Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT at φ(20) ≈ 0.417, φ(50) = (137/60)/H_50 ≈ 0.508, φ(100) ≈ 0.565, φ(200) ≈ 0.612. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner). Build subtree `sims/verdict-063-coupon-collector-tail/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 052 + VERDICT 063 appended to sim-lab `control/outbox.md` only).

## What happened

Built `sims/verdict-063-coupon-collector-tail/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 052 block / idea doc @
idea-engine main cdf3e2e; the disclosed fixture-level choices — the
weighted-tier integer split ⌊0.7N⌋/⌊0.25N⌋/remainder, the overshoot floor
convention t* = ⌊2·E[T_50]⌋ = 449, the per-draw primitive int(u·N), the
φ-hat ratio-of-means estimator + delta-method SE, the F5 enumeration range
t = 1..12 and control-leg count — all pinned in the fixture BEFORE the
runner) committed BEFORE the runner. Git trail (PR #121): c519e55
(born-red card) -> 4c3b076 (fixtures) -> 3a003a7 (runner coupon_tail_sim.py
+ accepted run: results.json, run-stdout.txt, README.md, REPORT.md) ->
9a9c63f (merge of origin/main after V062 landed) -> aa40ddb (INTAKE 052 +
VERDICT 063 ledger) -> this flip. Claim-first: idea-engine PR #377, landed
before any sim-lab work.

**Run:** `SELF-CHECKS: 751 passed, 0 failed`, exit 0, ~3m07s/run (≈ 519M
RNG calls through the counting wrapper, pure CPython); stdout +
results.json byte-identical across two full process runs by external
sha256 (run-stdout eabd4204..., results 428c702d...); CPython 3.11 pinned,
asserted. Gates all green: transcription exact; F1 harmonic re-derivation
by twin structures incl. H_5 = 137/60, H_10 = 7381/2520; F2 linearity +
head/tail stage accounting exact per cell; F3 φ(m=N)=1, φ(m=1)=1/H_N; F4
monotonicity (φ in m, E[T_N] in N over 1..200, last-coupon stage = N); F5
inclusion–exclusion CDF ≡ full enumeration at N ∈ {2,3}, t = 1..12 (24
identities exact), E[T_2] = 3, E[T_3] = 11/2, MC control legs passing the
mean + 24 CDF point gates; twin evaluators agree on every table; Arm S
main (seed 20261345, 200,000/cell) inside 1/100 + 4·SE on E[T] and φ every
cell; draw sentinels exact per leg (399,950,106 / 39,857,673 / 79,637,137
/ 0 aux — the ONLY four RNGs, pinned order, new registry high-water
20261348).

**Ruling: REJECT** (checked FIRST, fires): φ = 0.416928 / 0.507497 /
0.564634 / 0.612065 over N = 20/50/100/200 — all ≥ 2/5, 4 of 4 (3
required), decision cell φ(50) = 7076151618028359146280/
13943237577224054960759 exactly. The "almost complete = almost done" folk
belief fails in the costly direction: the last 10% of a 50-item set costs
50.7% of the expected draws, and the final single coupon alone 1/H_50 =
22.2%. Stability (seed 20261346) reproduces REJECT_ARITH through the twin
evaluators; all four registered NULL axes false; drafter's disclosed
REJECT reproduced within 1e-3 in every cell — no drafter arithmetic error.
Honest disclosure riding the verdict: the registered weighted-rarity-tier
reporting leg is uniform-DEGENERATE at its own pinned constants (tier
masses equal tier item-fractions), so only the N = 50 integer split
departs from uniform — disclosed in the fixture before the runner,
reported, never ruling.

Walls: none new. REPORT.md and the ledger append rode shell heredocs per
the standing V054–V062 classification; fixtures, runner, README, and this
card went through Write. Parallel-session race: V062 (PR #120) squash-
merged into main mid-session; per the registered protocol origin/main was
merged INTO this branch (9a9c63f — merge, never rebase) and the INTAKE 052
/ VERDICT 063 blocks appended LAST in ledger order; both collision greps
empty (session start @ d2261a1, pre-append @ 3d7ae2c). ASK 003 mtime
disclosure: after the merge brought in V062's COMPLETE card, local
`check --strict` at the ledger push went exit 0 while THIS card still said
in-progress — the mtime-newest defect firing in the FALSE-GREEN direction
(it validated the sibling's freshly-merged card as "the" session log,
masking this session's designed born-red hold). Disclosed here rather than
fix-forwarded; this flip commit makes the green legitimate. Session-card
markers: `**Status:**` complete, 💡 below, previous-session review below,
`📊 Model:` family-level. `control/inbox.md`, both status heartbeats, and
idea-engine's outbox untouched. PR:
https://github.com/menno420/sim-lab/pull/121 (READY; merge-on-green owns
the merge — zero agent merge/arm calls).

## 💡 Session idea

Registrations that pin a "weighted" reporting leg by FORMULA should carry
a drafter-side DEGENERACY check: assert the pinned mass fractions do NOT
equal the pinned item-count fractions before calling the leg a
sensitivity bracket. This session is the proof case: PROPOSAL 052's
rarity-tier pmf (70%/25%/5% mass over the first 0.7N / next 0.25N / last
0.05N items) is item-proportional, i.e. exactly uniform 1/N wherever the
counts divide evenly (N = 20, 100, 200 here), so the registered
"weighted leg brackets the amplification" claim silently measured uniform
against uniform, and the only signal in the column (N = 50, delta
+0.000765) came from THIS session's disclosed integer-split convention,
not from the registered weights. The fix costs one line at drafting
(compare the two fraction vectors; if equal, re-pin genuinely skewed
masses, e.g. 90/9/1 over the same 0.7/0.25/0.05 split) and would have
turned a degenerate column into the real rarity bracket the folk-belief
question still lacks. Kin, deduped (grep outbox + .sessions/ for
"degenerate", "uniform", "weighted leg"): V061's 💡 priced an UNDERPOWERED
stability conjunct (a noise problem, remedy = size N or disclose
P(reproduce)); this prices an UNINFORMATIVE reporting leg (an identity
problem, remedy = a drafting-time vector comparison) — different failure,
different one-line guard. Anchors: fixtures.json
`weighted_rarity_tier.degeneracy_disclosure`; coupon_tail_sim.py
`mc_weighted_leg`; REPORT.md "Reporting-only legs" + recommendation (3).

## ⟲ Previous-session review

VERDICT 061 (kill-clock horizon, PR #119) is the direct predecessor. Its
💡 — disclose a stability conjunct's reproduction probability at drafting,
computed from the disclosed landing — reads prophetic from here: P052's
disclosed landing put every cell ≥ 0.417 against a 0.4 band, so the
stability leg's reproduction probability at N = 20,000 was effectively 1
(the nearest edge sits ≈ 11·SE away), and the conjunct certified REJECT
without drama — the well-powered counterpart to V061's coin-flip case,
exactly the design property its card asked registrations to make a
REGISTERED number. Its git-trail discipline (born-red card -> fixtures ->
runner + accepted run, no fix-forwards) transferred verbatim again. One
honest nit back: V061's REPORT.md does not literally END with the five
validity-gate answers — they live condensed in its ledger `gate:` line
while the report closes on Limits, though `sims/README.md` binds "a
results report that ends in the five validity-gate answers + the verdict +
the best-implementation recommendation"; V063's REPORT.md restores the
literal closing section, which costs a page and saves the next citer a
ledger round-trip.

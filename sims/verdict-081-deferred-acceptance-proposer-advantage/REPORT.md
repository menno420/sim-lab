# VERDICT 081 — the deferred-acceptance proposer advantage (idea-engine PROPOSAL 068) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT -> INVALID -> APPROVE -> NULL; both independently-written decision
evaluators agree REJECT/REJECT; every decision number is an exact
rational). The drafter's disclosed landing reproduces from scratch on
every value — **zero anomalies**.

Stability does NOT pin the outcome. At the decision cell n = 3 (the full
46,656-profile exact census), all three REJECT clauses clear:

- **Side-gap**: Pbar(3) = 35/24 ~ 1.458333, Rbar(3) = 371/216 ~ 1.717593,
  Delta(3) = **7/27 ~ 0.259259** >= 1/5 (1.30x over the line). A quarter of
  a choice-level per agent, from nothing but which side runs the procedure.
- **Multiplicity**: f(3) = P(|S| >= 2) = **131/486 ~ 0.269547** >= 1/5
  (1.31x). E|S|(3) = 5027/3888 ~ 1.292953.
- **Strategy-proofness asymmetry with bite**: M_prop(3) = **0 exactly**
  (46,656 profiles x 3 proposers x 5 misreports — no proposer ever gains;
  Dubins–Freedman confirmed as a census fact) and M_recv(3) = **1/54 ~
  0.018519** >= 1/100 (1.85x; 864 profiles have a receiver with a
  profitable complete-list misreport). The receiving side is both worse
  off AND the only gameable side.

## The gap-localization discovery — where the advantage lives

Delta(3 | unique) = **0 exactly**, verified per profile, not just in
expectation: on every unique-stable-matching profile (355/486 ~ 73.0% of
all n = 3 markets) the per-profile receiver tax g(p) = mean_w rank(mu_M) -
mean_w rank(mu_W) is identically zero — the folk belief is EXACTLY right
on nearly three-quarters of markets. The entire averaged advantage is the
product

  Delta(3) = f(3) x Delta(3 | multi) = (131/486) x (126/131) = 7/27, exact

— and on a contested market the proposer's advantage is nearly a FULL
choice-level (126/131 ~ 0.961832 rank positions). The mechanism's leverage
lives ENTIRELY off the singleton set.

## Market-size-born: two exact points + the seeded growth trace

| n | Delta(n) | f(n) | M_recv(n) | E&#124;S&#124;(n) |
|---|----------|------|-----------|-------|
| 1 (exact) | 0 | 0 | 0 | 1 |
| 2 (exact) | 1/8 = 0.125 | 1/8 | 0 | 9/8 |
| 3 (exact) | 7/27 ~ 0.2593 | 131/486 ~ 0.2695 | 1/54 ~ 0.0185 | 5027/3888 ~ 1.2930 |
| 4 (MC) | 0.399792 | 0.403070 | 0.050475 | 1.486375 |
| 5 (MC) | 0.543350 | 0.513735 | 0.091875 | 1.697525 |
| 6 (MC) | 0.693179 | 0.605355 | 0.136000 | 1.931325 |

(MC rows: main leg 200,000 episodes/size seed 20261600 for Delta-hat and
f-hat; stability leg 40,000 episodes/size seed 20261601 for E|S|-hat and
Delta|multi-hat — 0.991821 / 1.058028 / 1.142097 at n = 4/5/6 — and the
M_recv-hat prefixes 40,000 / 8,000 / 2,000 per convention C6; enumerated
f-hat 0.402700 / 0.511825 / 0.603225 agrees with the corner-inequality
f-hat on the independent main stream. REPORTING-ONLY, no gate.)

The registered NULL straddle is real: the n = 2 cell lands ALL THREE
REJECT clauses under threshold (Delta = f = 1/8 in (1/20, 1/5); M_recv(2)
= 0 — a 2x2 market is too small to game). One market-size step down and
the ruling is band-straddle NULL: the advantage, the multiplicity, and the
receiver-side manipulability are all BORN of scale, and the Arm-R trace
continues the rise toward the classic ln n vs n/ln n asymptotic. Both
sides beat the random-partner baseline (n + 1)/2 = 2 at n = 3 — matching
adds value for everyone; the REJECT indicts the "neutral clearing"
FRAMING, never matching itself.

## The three structure theorems — exact at every census cell

- **T1 POLARIZATION**: for every profile and every stable matching mu,
  every proposer weakly prefers mu_M to mu and every receiver weakly
  prefers mu to mu_M (mirror at mu_W) — zero violations across all stable
  matchings of all 46,673 census profiles (n = 1, 2, 3), both arms. The
  corners are exactly opposed; the choice of side is a pure ordinal
  transfer with no Pareto ambiguity.
- **T2 GAP-LOCALIZATION**: g(p) = 0 on every unique profile exactly, and
  Delta = f x Delta|multi exactly at every cell.
- **T3 STRATEGY-PROOFNESS ASYMMETRY**: M_prop = 0 exactly at every cell;
  M_recv(2) = 0 and M_recv(3) = 1/54 > 0 — receiver-side manipulability is
  itself market-size-born. Every successful receiver misreport in the
  census was checked against both Demange–Gale–Sotomayor clauses (only a
  receiver with mu_M(w) != mu_W(w) gains; no gain ever beats mu_W(w)) —
  zero violations, which also certifies the Arm-R DGS prune (C6).

## Gates — ALL GREEN (107 self-checks, 0 failed, exit 0)

- **F1** — GS output stable at every profile (both directions); every rank
  in [1, n]; random-partner baseline (n + 1)/2; the relabelling SYMMETRY
  gate exact (E[proposer rank in mu_M] == E[receiver rank in mu_W] and the
  manipulation counts identical under relabelling, at every cell); the C5
  identity E[g] == Rbar - Pbar exact at every cell.
- **F2** — the three theorems above, enumerated exhaustively; truth values
  route per the registered NULL axes (all TRUE, none fired).
- **F3** — all 19 registered census anchors reproduced EXACTLY (n = 3:
  35/24, 371/216, 7/27, 131/486, 5027/3888, 126/131, 355/486, 0, 1/54;
  n = 2: 5/4, 11/8, 1/8, 1/8, 9/8, 0, 0; n = 1: 0, 0, 1). Zero anomalies
  vs the disclosed landing.
- **F4** — the hand world: men (w0 > w1, w1 > w0) x women (m1 > m0,
  m0 > m1) has exactly the two registered stable matchings; men-proposing
  lands each man's top, women-proposing each woman's top; the census's
  multi-stable n = 2 profiles are EXACTLY this profile and its
  relabel-mirror (f(2) = 2/16 = 1/8 by the pencil count).
- **F5** — common-preference degeneracy: all-men-identical (1,296 n = 3
  profiles) and all-women-identical (1,296) both land f = 0 and g = 0 on
  every slice profile — serial dictatorship, unique stable matching, zero
  side-leverage: the gap is a preference-DIVERSITY effect. (The naive
  slice-restricted Rbar - Pbar is -5/9 / +5/9 on the two families — the
  slice is not relabelling-closed; published beside per C5,
  reporting-only.)
- **F6** — battery: Arm B (independently written: factorial-decode
  profile iteration, all-pairs stability test, lattice extremes taken from
  the ENUMERATED stable set — never via GS — and GS-free manipulation via
  its own corner table) exact-equal on every published census number at
  n = 1, 2, 3; GS-LANDS-THE-CORNER checked at all 46,656 n = 3 profiles
  (mu_M / mu_W == the enumerated set's coordinatewise men-rank min / max)
  and re-verified on every Arm-R stability episode (sandwich + the C4
  corner-inequality |S| >= 2 <=> mu_M != mu_W, zero violations in
  120,000 enumerated episodes); twin decision evaluators agree
  REJECT/REJECT; Arm-R draw sentinels exact (2n in-runner Fisher–Yates
  shuffles per episode: 1.6M/2.0M/2.4M main, 320k/400k/480k stability);
  seed registry exactly [20261600, 20261601, 20261602], aux 20261603
  never constructed; stdout + results.json byte-identical across two full
  process runs; CPython 3.11 asserted.

## Reproducibility

One command, no flags:
`python3 sims/verdict-081-deferred-acceptance-proposer-advantage/deferred_acceptance_sim.py`.
~72 s/run single-threaded, stdlib-only, hermetic (reads only its own
fixtures.json). Two full in-repo process runs externally diffed —
byte-identical. sha256:
`run-stdout.txt`
`d46e46d7203cd9d21a69b83c59c4c2aa22405978356d17fd9223023f7e52d485`,
`results.json`
`ec6b7159fe820950ebf39b28976f8f8b235ceb4998824aff6e5f78a385254ee0`.
Seeds: the drafter's registered allocation IS the session seed set (the
V077–V080 precedent; no new allocation this slice) — main 20261600,
stability 20261601, presentation 20261602, aux 20261603 reserved and
asserted never read; 20261594–599 remain the drafter's disclosed in-flight
buffer, unused; registry high-water 20261603 (reserved; highest READ
20261602).

## Boundaries (registered, carried verbatim)

Model: strict-complete equal-side preferences (ties / incomplete lists /
unequal sides are named follow-ups where rural-hospitals bites).
Distribution: uniform profile weighting — correlated / common-value
preferences shrink the stable set toward the singleton (F5 is the
extreme); this verdict prices the diverse-preference regime. Welfare:
ordinal rank; cardinal re-weights the same matchings (reporting flavor
only). Market: one-to-one; many-to-one changes the receiving-side
manipulation structure. Intent: the REJECT indicts the "neutral clearing
procedure" FRAMING — never matching's value (both sides beat random) nor
any specific mechanism; the consequence menu (name the side / alternate
the proposing side / median-stable matching / disclose the advantage) is
where intent lives.

## Pre-registered consequence (routing is the manager's per Q-0260)

REJECT -> the "neutral clearing procedure" framing retires with numbers;
the correction ships in two lines: (1) any two-sided clearing surface that
runs a deferred-acceptance-style procedure and calls the result "the"
stable outcome is spending a real degree of freedom in the RUNNING side's
favor — name the side; if cross-side fairness is the goal, alternate the
proposing side, use a median/egalitarian stable matching, or disclose the
directional advantage rather than laundering it as neutrality. (2) The
running side is strategy-proof and the other side is not — do not treat
both sides' submitted preferences as equally trustworthy signal. The
transferable design lens is GAP-LOCALIZATION: measure P(multiple stable
outcomes) FIRST — a market that is almost always single-valued genuinely
IS side-neutral, and the crossover is exactly f(n). Named follow-ups, none
in scope: ties/incomplete lists (rural hospitals), correlated preferences,
many-to-one markets, cardinal re-weighting, the egalitarian/median stable
matching as a third mechanism.

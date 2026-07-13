# REPORT — single-elimination seeding fairness: is the standard 8-team bracket exactly optimal? (PROPOSAL 028)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 028** ·
> 2026-07-13T06:25:48Z · status: sim-ready (idea
> `ideas/fleet/tournament-seeding-bracket-optimality-2026-07-13.md`, landed via
> idea-engine PR #295, main `535c232`). The ORDER 004 rule-3
> COMPLETELY-UNRELATED-domain rotation slot, round 3 — sports statistics /
> tournament-format design (knockout-bracket seeding under a Bradley–Terry
> win-probability model), a THIRD fleet-external domain after round 1's social
> choice (PROPOSAL 017 → VERDICT 019) and round 2's congestion routing
> (PROPOSAL 024 → VERDICT 026). Fully hermetic AND fully exact: the entire
> world is constructed in-sim from pinned constants; zero repo/network reads in
> the verdict session; ZERO RNG, seeds, or floats anywhere.
> Run: `python3 sims/verdict-030-bracket-optimality/bracket_optimality_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — an exhaustive exact census,
band-scored against the pre-registration; no sampling arm because no
sampling is needed): the exact optimality gaps Δ_a and Δ_b of the standard
8-team seeding over ALL 315 distinct bracket assignments under four
committed Bradley–Terry strength profiles, every number a platform-
independent exact rational (`fractions.Fraction` end to end — NO sampling
error, NO seeds, NO floats). Two structurally independent exact algorithms
must agree by exact rational equality on every (bracket, profile,
objective) cell — the seedless-exact analogue of the P017/P024/P026
arm-agreement gate. This label fills the outbox `evidence: simulation`. The
one judgment question — whether 0.5 pp / 1.0 pp are the RIGHT materiality
lines — was pinned by pre-registration in the idea file; the full 315-value
tables ship in `results.json`, so a re-drawn line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock, no
environment. Every constant ({tree topology, the census expectation
315 × 128, strength profiles F0–F4, the standard bracket class, the pinned
non-canonical relabeling representative, band constants 1/200 and 1/100,
the decision rule and its evaluation order}) was copied verbatim from the
idea file into `fixtures.json` BEFORE the runner was written, and the
runner cross-checks its literals against that file at start. Eight
intake-time decisions are disclosed in `fixtures.json` (exact quartile
convention, bracket display key, rank and argmax-tie conventions,
display-only decimals, the relabeling representative's derivation, the
two-team identity fixtures, the no-python-pin rationale). One naming note
pinned there: the idea file presents the standard class as
(1,8,4,5 | 3,6,2,7); under the registered recursive min-sort
canonicalization the SAME class's canonical representative is
**(1,8,4,5 | 2,7,3,6)** (min(2,7) < min(3,6) reorders the second half's
pairs) — identical class, zero ambiguity, used everywhere below.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Tree:** balanced 8-leaf bracket — QF pairs (L1,L2), (L3,L4), (L5,L6),
  (L7,L8); SF1 between the first two pair-winners, SF2 between the last
  two; one final. Two leaf assignments are the SAME bracket iff related by
  the tree's automorphism group (order 2⁷ = 128) → 8!/2⁷ = **315** distinct
  brackets, enumerated from all 8! leaf orders via recursive min-sort
  canonicalization and AUDITED to exactly 315 classes × 128 preimages
  (sum 40320).
- **Model:** Bradley–Terry — P(i beats j) = s_i/(s_i+s_j), matches
  independent, strengths constant across rounds, no draws. Profiles:
  F1 linear (8,7,6,5,4,3,2,1); F2 geometric (128,64,32,16,8,4,2,1);
  F3 top-heavy one-star (100,8,7,6,5,4,3,2); F4 near-flat (107..100);
  F0 flat control (100 ×8, reporting-only, closed forms asserted).
- **Objectives:** (a) P_best = P(team 1 wins the tournament);
  (b) P_12 = P(the final is 1-vs-2), read off the two half-distributions.
- **Arm A (winner-distribution recursion):** W_subtree(i) =
  W_L(i)·Σ_j W_R(j)·p_ij + mirror; P_12 = W_h1(1)·W_h2(2) + W_h1(2)·W_h2(1).
- **Arm B (independent cross-check):** iterative enumeration of all
  2⁷ = 128 complete outcome paths per bracket (a path's probability = the
  product of its 7 match probabilities), both objectives and the full
  winner distribution read off the paths; per-bracket path mass asserted
  to sum to exactly 1.
- **Gate:** Arm A ≡ Arm B by EXACT RATIONAL EQUALITY on every (bracket,
  profile) cell — P_best, P_12, AND the full 8-team winner distribution
  (315 × 5 profiles).
- **Decision rule (registered before any code, evaluated in this order):**
  REJECT iff Δ_a = 0 AND Δ_b = 0 exactly in ALL four decision profiles
  (checked FIRST — the strictest claim); APPROVE iff Δ_a ≥ 1/200 (0.5 pp)
  in ≥ 1 profile OR Δ_b ≥ 1/100 (1.0 pp) in ≥ 1 profile; NULL otherwise.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`. Standard bracket = the class of
(1,8,4,5 | 2,7,3,6). All values exact rationals; decimals display-only.

**(1) Objective (a) — P(best team wins).** The standard bracket is NOT
optimal in ANY profile — and the same challenger bracket is the argmax in
all four: **(1,8,6,7 | 2,3,4,5)**, which quarantines the three strongest
rivals 2,3,4 (plus 5) in the OTHER half so they eliminate each other while
team 1 crosses only 6,7,8 before the final.

| profile | P_best(standard) | rank/315 | P_best(max) @ (1,8,6,7\|2,3,4,5) | **Δ_a** | band 1/200 |
|---|---|---|---|---|---|
| F1 linear | 9248768/27720225 ≈ 0.333647 | 31 | 395098624/1003377375 ≈ 0.393769 | 7058006528/117395152875 ≈ **6.0122 pp** | **MET** |
| F2 geometric | 31576293376/49327795935 ≈ 0.640132 | 54 | 6884950016/9525569625 ≈ 0.722786 | 1325075529728/16031533678875 ≈ **8.2654 pp** | **MET** |
| F3 top-heavy | ≈ 0.871547 | 32 | ≈ 0.887177 | 8151295825000/521486092810683 ≈ **1.5631 pp** | **MET** |
| F4 near-flat | ≈ 0.133533 | 35 | ≈ 0.134198 | ≈ 0.0665 pp | not met |

**(2) Objective (b) — P(the final is 1-vs-2).** Again suboptimal
everywhere; the argmax DIFFERS from objective (a)'s in every profile (the
two folk goals genuinely disagree): (1,7,3,4 | 2,8,5,6) at F1/F4,
(1,5,3,4 | 2,8,6,7) at F2/F3 — brackets that split 1 and 2 and stack the
mid-field against team 1's half more evenly.

| profile | P_12(standard) | rank/315 | P_12(max) | argmax | **Δ_b** | band 1/100 |
|---|---|---|---|---|---|---|
| F1 linear | 482944/1848015 ≈ 0.261331 | 12 | 10804/39325 ≈ 0.274736 | (1,7,3,4\|2,8,5,6) | 14987404/1118049075 ≈ **1.3405 pp** | **MET** |
| F2 geometric | 545259520/896869017 ≈ 0.607959 | 72 | 7340032/10042461 ≈ 0.730900 | (1,5,3,4\|2,8,6,7) | 1433403392/11659297221 ≈ **12.2941 pp** | **MET** |
| F3 top-heavy | 29696000/75551553 ≈ 0.393056 | 58 | 177152000/357630273 ≈ 0.495350 | (1,5,3,4\|2,8,6,7) | 25083904000/245215157187 ≈ **10.2293 pp** | **MET** |
| F4 near-flat | ≈ 0.068073 | 12 | ≈ 0.068081 | (1,7,3,4\|2,8,5,6) | ≈ 0.0008 pp | not met |

**(3) Band arithmetic (registered order).** REJECT — checked FIRST — fails
immediately and everywhere: Δ_a > 0 AND Δ_b > 0 in all four profiles (the
standard bracket is exactly optimal NOWHERE; its best rank on either
objective is 12/315). APPROVE — met SIX times over (needs one):
Δ_a ≥ 1/200 in F1/F2/F3; Δ_b ≥ 1/100 in F1/F2/F3. Only near-flat F4 is
sub-material on both gaps (0.0665 pp / 0.0008 pp — when every match is a
near coin flip, seeding barely matters). **Ruling: APPROVE.**

**(4) Reporting-only context (cannot flip; registered as such).**
Adversarial mis-seeding is material too: the WORST bracket suppresses
P(best wins) to 0.2205 (F1, (1,2,3,8|4,7,5,6) — champion loses ~11.3 pp vs
standard), 0.4898 (F2), 0.8337 (F3), 0.1304 (F4); the worst P_12 is exactly
0 in every profile (any of the 135 same-half brackets). Distribution
quartiles per profile ship in `results.json` (e.g. F1 P_best over the 315:
min 0.2205 / Q1 0.2392 / med 0.2641 / Q3 0.2988 / max 0.3938 — the standard
sits above Q3 but 6 pp below the max). F0 flat control: P(each wins) = 1/8
exactly on all 315 brackets; P_12 = 1/16 exactly on the 180 split-pair
brackets and 0 on the 135 same-half brackets (both closed forms asserted,
count matching the combinatorial 20·3·3 = 180). Spectator table: under the
standard bracket P(1v2 final) = 0.2613 (F1) / 0.6080 (F2) / 0.3931 (F3) /
0.0681 (F4).

**(5) Validity.** All gates PASS, **8530 self-checks, 0 failed**, exit 0:
the 315 × 128 partition audit (sum 40320); Arm A ≡ Arm B exact rational
equality on every cell including full winner distributions (315 × 5); path
mass = 1 per bracket; Σ_i W_root(i) = 1 per cell; the two-team identities
(128/192 = 2/3 and 107/207 reproduced); the F0 closed forms on all 315
brackets; relabeling invariance (the pinned non-canonical representative
(7,2,6,3,5,4,8,1) of the standard class reproduces the canonical numbers
exactly on every profile and both objectives). stdout AND `results.json`
byte-identical across two complete process runs by external diff (sha256
stdout `0aa68250…`, results `1f528be2…`); ~5 s per run, stdlib-only.

## What it did NOT settle

- **Real-league optimality.** The gaps are properties of the Bradley–Terry
  model on FOUR committed shape-spanning strength profiles — dials, not
  measurements of any real league. Under the named most-likely-to-flip
  alternative (an upset-floor model, or round-dependent strengths —
  fatigue/momentum) the value of "protection" changes and the argmax
  bracket can move; under a different OBJECTIVE (expected competitiveness,
  spectator value) the whole question changes — both declared outside the
  registered scope.
- **Larger fields / other formats.** n = 8 single-elimination only;
  reseeding-after-each-round and 16+ team fields are out of scope by design
  (16 teams ≈ 6.4×10⁸ brackets — argmax search, not census) — named
  follow-up heads.
- **The materiality lines themselves.** 0.5 pp / 1.0 pp are pre-registered
  judgments; the full exact tables ship in `results.json`, so a reader
  drawing different lines re-reads, never re-runs. (Note the ruling is not
  sensitive to them here: the largest gaps are 8.3 pp and 12.3 pp — an
  order of magnitude past the bands.)

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The pre-registered question is about a constructed family, not a live
system — by design (the unrelated-domain rotation's hermeticity contract).
The abstractions that could flip the HEADLINE reading are declared in the
model basis: an upset-floor / round-dependent-strength model moves the
argmax; a different organizer objective is outside scope. Within the
registered scope there is NO abstraction gap left: the census is
exhaustive, the arithmetic exact, and all four shape-spanning profiles
agree on the direction (suboptimal everywhere, materially so in three).

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **8530 self-checks, 0 failed**, exit-coded: two structurally
independent exact algorithms (subtree recursion vs complete outcome-path
enumeration) agreeing by exact rational equality on all 315 × 5 cells
INCLUDING full winner distributions; the committed 315 × 128 partition
audit; per-cell sum-to-1 and per-bracket path-mass-1; the two-team
identity; the F0 closed forms on every bracket (with the 180/135
split/same-half count matching the combinatorial derivation); relabeling
invariance from a representative exercising all three automorphism layers.
No seeded luck is POSSIBLE: there are no seeds — every number is a
rational, not an estimate. No cherry-picking: the census is exhaustive,
all four committed profiles report, and the decision bands quantify over
all of them (REJECT needed all four; APPROVE was met in three
independently).

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Not knife-edge anywhere: REJECT fails categorically (Δ > 0 on all eight
profile × objective cells — exact strict inequalities, not estimates);
APPROVE clears its bands SIX separate times, with headroom of 12× (Δ_a =
6.01 pp vs 0.5 pp, F1) to 12.3× (Δ_b = 12.29 pp vs 1.0 pp, F2); dropping
any single profile, or either entire objective, leaves the same ruling.
The one sub-material profile (F4 near-flat) is reported as the honest
boundary — as strength spreads vanish, all brackets converge and the folk
default becomes harmless.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own `fixtures.json`). Byte-identical stdout AND `results.json` across
TWO complete process runs by external `diff` — and byte-identity holds BY
CONSTRUCTION (exact rationals, zero RNG/floats/environment reads,
explicitly sorted output orderings, platform-independent — no CPython
version sensitivity; runtime python recorded: cpython 3.11.15). ~5 s per
run. Zero seeds drawn — the P027 seed-registry high-water 20260755 is
untouched.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure any real league, tournament, or fleet system; it
prices the folk seeding belief inside one committed statistical model on
four committed strength shapes. It does not rank brackets for objectives
other than (a)/(b), does not cover n ≠ 8 or reseeded formats, and its
argmax brackets are model-conditional design outputs, not universal
recommendations.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying computation is an exhaustive exact census (every
number a rational with zero sampling error); every constant, band, profile,
and the evaluation order were registered in the idea file before any code;
two independent algorithms agree exactly on every cell; and the ruling
clears its bands with an order of magnitude of headroom in three of four
profiles. The honest boundary: this strength attaches to the Bradley–Terry
model and the committed profile family — the sim measures the folk
belief's exactness in a constructed class, it does not certify any real
competition.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `approve` — "bracket audit warranted: the standard seeding is
  measurably suboptimal at its own stated goals."** By the rule committed
  before any code (REJECT checked first): REJECT fails — the standard
  bracket is exactly optimal in NO profile on NEITHER objective (best rank
  12/315); APPROVE met — Δ_a ≥ 0.5 pp in F1 (6.01 pp), F2 (8.27 pp), F3
  (1.56 pp) AND Δ_b ≥ 1.0 pp in F1 (1.34 pp), F2 (12.29 pp), F3 (10.23 pp).
- **The pre-registered APPROVE consequence, verbatim:** an organizer whose
  STATED goal is "the best team should win" or "a 1-vs-2 final" does not
  default to standard seeding — the per-profile argmax bracket table ships
  with this verdict, and **"1v8/4v5/3v6/2v7 protects the best team" may no
  longer be cited as settled for that goal** — pick the measured bracket
  for your strength profile (or state a different goal).
- **The citable numbers:** for "best team wins" ONE challenger dominates
  all four profiles — (1,8,6,7 | 2,3,4,5), quarantine-the-contenders —
  worth +6.0 / +8.3 / +1.6 / +0.07 pp over standard (F1/F2/F3/F4); for
  "1-vs-2 final" the argmax differs from (a)'s in every profile (the two
  folk goals disagree with each other), worth up to +12.3 pp (F2). The
  standard bracket ranks 31/54/32/35 of 315 on objective (a) — a top-20%
  bracket, never the top one.
- **Scope qualifier (shipped with the ruling, not a condition):** the gaps
  are Bradley–Terry-conditional on committed dial profiles; near-flat
  fields (F4) show sub-material gaps, so the folk default is harmless
  exactly where matches are coin flips; the upset-floor/objective-choice
  flips are named in `fixtures.json` model_basis and remain unmeasured.
- **Named follow-ups (not ordered):** 16-team argmax search (census
  infeasible at 6.4×10⁸ — needs a search head), reseeding-after-each-round
  formats, and the objective trade-off frontier (competitiveness /
  spectator value vs (a)/(b)).

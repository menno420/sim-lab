# REPORT — Penney's game responder-edge decay: does "never go first" survive word length? (PROPOSAL 032)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 032** ·
> 2026-07-13T08:17:09Z · status: sim-ready (idea
> `ideas/fleet/penney-game-responder-edge-decay-2026-07-13.md`, landed via
> idea-engine PR #302, main `2e5d73f`). The ORDER 003/004 rule-3
> COMPLETELY-UNRELATED-domain rotation slot, round 4 — recreational
> probability / sequential pattern-race games (Penney's game over fair-coin
> words), a FOURTH fleet-external domain after round 1's social choice
> (PROPOSAL 017 → VERDICT 019), round 2's congestion routing (PROPOSAL 024 →
> VERDICT 026), and round 3's tournament seeding (PROPOSAL 028 → VERDICT
> 030). Fully hermetic AND fully exact: the entire world is constructed
> in-sim from pinned constants; zero repo/network reads in the verdict
> session; ZERO RNG, seeds, or floats anywhere.
> Run: `python3 sims/verdict-034-penney-decay/penney_decay_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — an exhaustive exact census,
band-scored against the pre-registration; no sampling arm because no
sampling is needed): the responder's guaranteed edge V(L) = min_A max_{B≠A}
P(B before A) in Penney's game at L ∈ {3, 4, 5} over the FULL ordered-pair
census (56 / 240 / 992 cells = 1,288 decision cells, plus the 12-cell L=2
anchor leg), every number a platform-independent exact rational
(`fractions.Fraction` end to end — NO sampling error, NO seeds, NO floats).
Two structurally independent exact algorithms must agree by exact rational
equality on every cell — Arm A Conway leading numbers, Arm B first-step
absorption on the two-word prefix automaton — the seedless-exact analogue of
the P017/P024/P028 arm-agreement gate. This label fills the outbox
`evidence: simulation`. The one judgment question — whether 3/5 and 13/25
are the RIGHT materiality lines — was pinned by pre-registration in the
idea file; the full per-cell matrices ship in `results.json`, so a re-drawn
line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock, no
environment. Every constant ({the L grid {3,4,5} + the L=2 anchor leg, band
constants 3/5 and 13/25, the folk-rule definition σ(A) = ¬a₂·a₁…a_(L−1),
the three classic anchor rationals 3/4, 7/8, 2/3, the decision rule and its
evaluation order}) was copied verbatim from the idea file into
`fixtures.json` BEFORE the runner was written, and the runner cross-checks
its literals against that file at start. Ten intake-time decisions are
disclosed in `fixtures.json` (word encoding and ordering, matrix
orientation, the exact quartile convention, the reading of "both
distributions", argmin/argmax tie conventions, the folk-rule scoring scope,
the antisymmetry-independence implementation, the two-sided Conway
positivity check, display-only decimals, the no-python-pin rationale).
Seed-registry note: this sim draws ZERO seeds — the P031 high-water
20260767 is untouched.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Frame:** fair i.i.d. coin (P(H) = P(T) = 1/2); both players commit
  distinct words of the SAME length L over {H,T}; the first word to appear
  as a run of consecutive flips wins. Ties are impossible for distinct
  equal-length words and the race ends w.p. 1, so every P(B before A) is a
  well-defined exact rational.
- **Census:** all ordered pairs (A, B), A ≠ B — 56 (L=3), 240 (L=4),
  992 (L=5), 1,288 decision cells total; the 12-cell L=2 leg is
  reporting-only (anchor 3/4 + the fair HT-vs-TH cell). Census sizes are
  audited in-sim, never assumed.
- **Arm A (Conway leading numbers):** L(X,Y) = Σ_{k=1..L} δ_k·2^(k−1),
  δ_k = 1 iff the last k chars of X equal the first k of Y; odds B over A
  = (L(A,A)−L(A,B)) : (L(B,B)−L(B,A)) — pure integer arithmetic.
- **Arm B (independent cross-check):** the two-word prefix automaton
  (transient states = proper prefixes of A and B incl. the empty string,
  ≤ 2L−1 states; longest-suffix transitions; the full words absorb),
  absorption probabilities by first-step analysis — exact Gaussian
  elimination over `fractions.Fraction`.
- **Gate:** Arm A ≡ Arm B by EXACT RATIONAL EQUALITY on every cell — all
  1,300 cells (decision + anchor leg); any inequality invalidates the run.
- **Decision rule (registered before any code, evaluated in this order;
  bands DISJOINT by construction, 13/25 < 3/5):** REJECT iff V(5) ≤ 13/25
  (checked FIRST); APPROVE iff V(L) ≥ 3/5 at ALL of L ∈ {3, 4, 5}; NULL
  otherwise (the straddle — a finalized outcome pinning the curve).

## What it SETTLED (the load-bearing numbers)

Full per-cell matrices, trap tables, and folk-rule tables in
`results.json`. All values exact rationals; decimals display-only.

**(1) The minimax decay curve V(L) — the decision leg.** The responder's
guaranteed edge stays above 3/5 at every swept length, and the curve is
NON-MONOTONE — it dips at L=4 and recovers at L=5:

| L | V(L) exact | decimal | safest first picks (argmin) | optimal response | ≥ 3/5? |
|---|---|---|---|---|---|
| 3 | **2/3** | 0.666667 | HTH, HTT, THH, THT | HHT (for HT··), TTH (for TH··) | **MET** (+1/15 ≈ 6.67 pp) |
| 4 | **9/14** | 0.642857 | HTHH, THTT | THTH, HTHT | **MET** (+3/70 ≈ 4.29 pp — the binding length) |
| 5 | **17/26** | 0.653846 | HTTHH, THHTT | THTTH, HTHHT | **MET** (+7/130 ≈ 5.38 pp) |

V(3) = 2/3 reproduces the Gardner-table floor exactly (anchor gate).
Non-monotonicity: V(5) − V(4) = 1/91 ≈ +1.10 pp; V(3) − V(4) = 1/42. The
safest first picks come in complement pairs (forced by the complement
invariance the sim asserts per cell).

**(2) Band arithmetic (registered order).** REJECT — checked FIRST — fails
by a wide margin: V(5) = 17/26 ≈ 0.6538 vs the 13/25 = 0.52 line — 87/650
≈ 13.4 pp above it. APPROVE — met at ALL three lengths: V(3) = 2/3 ≥ 3/5,
V(4) = 9/14 ≥ 3/5, V(5) = 17/26 ≥ 3/5 (closest approach 3/70 ≈ 4.29 pp at
L=4). **Ruling: APPROVE — "the responder edge is structural — first-order
at every swept length."**

**(3) The folk flip-rule beater σ(A) = ¬a₂·a₁…a_(L−1) — reporting-only.**
Exactly optimal everywhere at L=3, decisively NOT beyond it:

| L | O(L) optimality share | S(L) worst shortfall | σ non-optimal on |
|---|---|---|---|
| 3 | **8/8 = 1** | 0 | 0/8 words (σ attains the max on every word) |
| 4 | **10/16 = 5/8** | 1/12 ≈ 0.0833 | 6/16 words |
| 5 | **14/32 = 7/16** | 1/8 = 0.125 | 18/32 words — a majority |

By L=5 the popularized rule is sub-optimal on a MAJORITY of first picks,
and trusting it costs up to 12.5 pp of win probability (S(5) = 1/8). Its
guaranteed floor also slips under the APPROVE band: min_A P(σ(A) before A)
= 7/12 ≈ 0.5833 at both L=4 and L=5 (vs the true minimax 9/14 / 17/26) —
the folk RULE is not the guarantee, optimal response is. Full per-word
tables in `results.json`.

**(4) The "never worse than 2:1" claim — f_(2:1)(L), reporting-only.**
Share of first picks beatable at ≥ 2:1 (P ≥ 2/3): 8/8 = 1 at L=3 (the
popularization is exactly right there), 14/16 = 7/8 at L=4, 30/32 = 15/16
at L=5. The exceptions are precisely the argmin words above — at L ≥ 4 an
informed first player CAN duck under 2:1, but never under ~9:5 odds.

**(5) Trap table + distributions (reporting-only).** The famous traps
persist and deepen: max_B P per A peaks at HHH/TTT → 7/8 (the classic
anchor, gated), HHHH/TTTT → 15/16, HHHHH/TTTTT → 31/32 (beaten by
THHH / HTTT / THHHH / HTTTT — the σ-shaped responses). Trap-distribution
quartiles (min / Q1 / med / Q3 / max): L=3 {2/3, 2/3, 17/24, 25/32, 7/8};
L=4 {9/14, 2/3, 2/3, 169/224, 15/16}; L=5 {17/26, 2/3, 2/3, 251/352,
31/32}. Folk-rule distribution quartiles ship alongside (min 7/12 at
L ∈ {4,5}). The biggest trap and the safest first pick are NOT reverses or
complements of each other at any swept L (all-same words trap hardest;
alternating-ish words ending in a double are safest). L=2 leg: P(TH before
HH) = 3/4 (anchor, gated) and the HT-vs-TH cell is exactly fair (1/2 both
ways).

**(6) Validity.** All gates PASS, **33,678 self-checks, 0 failed**, exit 0:
Arm A ≡ Arm B exact rational equality on all 1,300 cells; the three classic
anchors (3/4, 7/8, V(3) = 2/3); complement invariance on every cell;
antisymmetry P(B before A) + P(A before B) = 1 on every unordered pair with
both sides computed standalone (never by definition); strictly positive
Conway differences on every cell (both terms); the automaton state audit
(≤ 2L−1 transient states — observed maxima 5/7/9 at L=3/4/5 — the two full
words absorbing, every transition landing in a known state); σ(A) ≠ A on
every word; census-size audits (2^L words, 2^L·(2^L−1) cells, 1,288 total).
stdout AND `results.json` byte-identical across two complete process runs
by external diff (sha256 stdout `d14f6761…`, results `204abfea…`); ~1.5 s
per run, stdlib-only (runtime python recorded: cpython 3.11.15).

## What it did NOT settle

- **Biased coins.** The curve is a property of the FAIR i.i.d. frame — the
  game's own canon and the frame every popularization uses. Under p ≠ 1/2
  the whole table deforms; the Conway arm is fair-coin-specific while the
  automaton arm generalizes to any p — the named follow-up head with one
  arm already built.
- **Unequal-length responses.** Allowing the responder a shorter or longer
  word changes the game; out of the registered scope by design.
- **L ≥ 6.** L=6 doubles the census to 4,032 pairs — feasible, but the
  swept range is where the folk tables live; a follow-up, not a blocker.
- **The materiality lines themselves.** 3/5 and 13/25 are pre-registered
  judgments; the full exact tables ship in `results.json`, so a reader
  drawing different lines re-reads, never re-runs. (The ruling is not
  knife-edge against them here: REJECT misses by 13.4 pp; APPROVE's
  closest approach is 4.29 pp at L=4.)

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The pre-registered question is about the game's own canonical frame, not a
live fleet system — by design (the unrelated-domain rotation's hermeticity
contract). The abstractions that could flip the HEADLINE reading are
declared in the model basis: a biased coin deforms the table (named
follow-up, automaton arm already general), and unequal-length response
spaces change the game (out of scope, named). Within the registered scope
there is NO abstraction gap left: the census is exhaustive, the arithmetic
exact, and the decision quantifies over every cell of every swept length.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **33,678 self-checks, 0 failed**, exit-coded: two structurally
independent exact algorithms (integer Conway correlations vs
automaton-absorption Gaussian elimination — different mathematics, different
code paths) agreeing by exact rational equality on all 1,300 cells; the
three most-reprinted constants in recreational probability gated as anchors
(3/4, 7/8, 2/3); complement invariance and independently-computed
antisymmetry on every cell; two-sided Conway positivity; the automaton
state audit; census-size audits. No seeded luck is POSSIBLE: there are no
seeds — every number is a rational, not an estimate. No cherry-picking:
the census is exhaustive, all three lengths report, and the decision bands
quantify over all of them (APPROVE needed all three; REJECT was evaluated
first on L=5 alone and missed by 13.4 pp).

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Not knife-edge: REJECT fails by 87/650 ≈ 13.4 pp (an exact margin, not an
estimate); APPROVE clears its band at every length with 4.29–6.67 pp of
headroom; dropping any single length, or re-drawing the REJECT line
anywhere below V(5) − ε, leaves the same ruling. The honest boundary is
the curve's shape: V(4) = 9/14 is the minimum — the edge does NOT decay
monotonically (V(5) > V(4) exactly, by 1/91), so extrapolating the
L=3→4 dip forward would have been wrong; that surprise is reported, not
smoothed. The folk-rule legs are reporting-only and could not flip the
decision; they didn't.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own `fixtures.json`). Byte-identical stdout AND `results.json` across
TWO complete process runs by external `diff` — and byte-identity holds BY
CONSTRUCTION (exact rationals, zero RNG/floats/environment reads,
explicitly sorted output orderings, platform-independent — no CPython
version sensitivity; runtime python recorded: cpython 3.11.15). ~1.5 s per
run. Zero seeds drawn — the P031 seed-registry high-water 20260767 is
untouched.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure any real wager, casino product, or fleet system; it
prices the popularized folk story inside the game's own canonical frame
(fair i.i.d. coin, equal-length words, L ≤ 5). It does not cover biased
coins, unequal-length response spaces, k > 2 players, or L ≥ 6 — all named
as follow-ups or out of scope. The folk-rule optimality share is a
property of σ as DEFINED (the popularized flip rule), not of every
response heuristic a player might use.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying computation is an exhaustive exact census (every
number a rational with zero sampling error); every constant, band, and the
evaluation order were registered in the idea file before any code; two
independent algorithms agree exactly on every cell; the three classic
published anchors are gated, not assumed; and the ruling clears its bands
with 4.3–13.4 pp of exact headroom. The honest boundary: this strength
attaches to the fair-coin equal-length frame at L ≤ 5 — the sim measures
the folk belief's exactness in the game's own canon, it does not certify
any biased or unequal-length variant.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `approve` — "the responder edge is structural — first-order
  at every swept length."** By the rule committed before any code (REJECT
  checked first): REJECT fails — V(5) = 17/26 ≈ 0.6538, 13.4 pp above the
  13/25 line; APPROVE met — V(3) = 2/3, V(4) = 9/14, V(5) = 17/26, all
  ≥ 3/5 (closest approach 4.29 pp at L=4).
- **The pre-registered APPROVE consequence, verbatim:** any
  pick-then-respond pattern-race design (a party wager, a classroom demo,
  or any game mechanic where one side commits a target pattern and the
  other responds) must treat PICK ORDER as a first-order fairness lever at
  every practical word length — **"just use longer words" may NOT be cited
  as the fix**; fair designs need simultaneous/blind picks or a priced
  pick order, and the folk-rule table ships with its measured optimality
  share.
- **The citable numbers:** the decay curve {2/3, 9/14, 17/26} — the safest
  first pick still loses ≥ 64.3% of races at every L ∈ {3,4,5}, and the
  curve is NON-MONOTONE (the L=4 dip recovers at L=5, exactly +1/91); the
  folk flip-rule σ(A) = ¬a₂·a₁…a_(L−1) is perfect at L=3 (O = 1), then
  decays to 5/8 (L=4) and BELOW HALF at 7/16 (L=5), costing up to 1/8 of
  win probability where wrong (S(5)) and guaranteeing only 7/12 — the
  "never go first" maxim survives; the popularized RECIPE for exploiting
  it does not; the "never worse than 2:1" soundbite holds exactly at L=3
  only (f_(2:1) = 1 → 7/8 → 15/16, the exceptions being the argmin words
  at ~9:5 odds).
- **Scope qualifier (shipped with the ruling, not a condition):** the
  numbers are properties of the fair-coin, equal-length, L ≤ 5 frame — the
  game's own canon; biased coins and unequal-length responses are named
  flips outside the registered scope.
- **Named follow-ups (not ordered):** V(L) under a biased coin (the
  automaton arm already generalizes; the Conway arm does not — one arm
  pre-built), unequal-length response spaces, and the L=6 census (4,032
  pairs, feasible).

# REPORT — IRV monotonicity in close races (PROPOSAL 017)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 017** ·
> 2026-07-13T00:59:58Z · status: sim-ready (idea
> `ideas/fleet/irv-monotonicity-close-races-2026-07-13.md` @ `efc78ae`, landed via
> idea-engine PR #281, main `80baad5`). The ORDER 004 rule-3 COMPLETELY-UNRELATED-domain
> rotation slot's first head — domain: social choice theory. No parent sims, no repo
> fixtures, no network: every fixture is integer combinatorics the sim constructs itself.
> Run: `python3 sims/verdict-019-irv-monotonicity/irv_monotonicity_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — exhaustive enumeration + seeded,
deterministic Monte Carlo, band-scored): Arm E is an EXACT computation (all
142,506 anonymous profiles at n=25; exact rationals, seedless, platform-
independent), Arm S is seeded IC sampling (`random.Random(seed)`, pinned loop
order, pinned cpython-3.11). This label fills the outbox `evidence:
simulation`. The one judgment question — whether 5%/10% are the RIGHT
materiality thresholds — was pinned by pre-registration in the idea file and
is disputable only about the bands, never about the measured numbers.

## PREMISE (verified this session — hermeticity by construction)

The proposal's premise: a fully hermetic sim needing no external repo access —
"every fixture is integer combinatorics the sim constructs itself." Verified
HONESTLY: the sim reads exactly ONE file (its own committed `fixtures.json`,
the pre-registration) and touches no repo state, no network, no wall clock; the
fixture values ({n, M, seed} per arm, band constants) were copied verbatim from
the idea file into `fixtures.json` BEFORE the runner was written, and the
runner self-checks its literals against that file at start. The premise HOLDS —
this is the pipeline's first fleet-external verdict, with zero repo coupling.

## What the sim MODELS

Three candidates {A,B,C}, six strict ballot types; an election is a 6-vector of
type counts summing to n. All constants pre-registered in `fixtures.json`:

- **Pinned IRV rule:** round 1 eliminates the unique fewest-first-place
  candidate; the winner is the pairwise majority winner of the remaining two on
  the FULL ballots. Any exact tie (round-1 lowest tie or final pairwise tie)
  EXCLUDES the election from numerator and denominator, counted and reported
  separately. All four legs use odd n, so pairwise ties cannot occur (measured:
  0 everywhere, self-checked).
- **Pinned violation test (upward):** election with winner W is a violation iff
  ∃ X ≠ W, ballot type t ∈ {X≻W≻Z, X≻Z≻W}, and integer k with 1 ≤ k ≤ count(t),
  such that converting exactly k ballots of t to W≻X≻Z (raising W, preserving
  X≻Z) changes the IRV winner away from W — searched exhaustively over X, t, k
  (early exit on the first violating k per (X, t): existence semantics identical
  to the full scan; the breakpoint-only optimization the proposal permits is NOT
  used, so the seed-20260715 spot check is not required). One disclosed pin: a
  modified election landing on an exact tie has no defined winner under the
  pinned rule and is NOT counted as a winner change — conservative, consistent
  with the pre-registered lower-bound reading.
- **Pinned conditioning:** close := round-1 elimination margin (second-lowest
  minus lowest first-place tally) ≤ 5% of n, tested as `margin * 20 <= n` in
  exact integers. Band comparisons are exact integer cross-multiplications —
  no floats anywhere in the decision path.
- **Arm E (exhaustive IAC):** ALL compositions of n into 6 parts, equally
  likely — n=25 (C(30,5) = 142,506 profiles, the decision leg) and n=13 (8,568,
  size anchor). Exact fractions, no randomness at all.
- **Arm S (seeded IC):** each voter uniform over the 6 types via
  `random.Random(seed).randrange(6)`, elections outer / voters inner —
  (n=99, M=200,000, seed 20260713) decision leg; (n=1,001, M=20,000, seed
  20260714) size leg. Pinned to cpython-3.11 (recorded in `results.json`);
  Arm E's headline numbers are platform-independent exact rationals.
- **Decision rule (committed before code):** APPROVE iff V_close ≥ 0.10 in
  BOTH decision legs AND V_all ≥ 0.01 in both; REJECT iff V_close < 0.05 in
  both; NULL otherwise — an explicitly legitimate outcome ruled as "the
  material-risk claim is voter-model-dependent", with no ruling issuing.
  Size legs are sensitivity only and cannot flip the decision.

## What it SETTLED (the load-bearing numbers)

Full table in `results.json`; V values as measured (exact fractions kept):

| leg | elections | ties (r1) | close set | V_all | V_close |
|---|---|---|---|---|---|
| **E-n25** (IAC, decision) | 142,506 | 11,790 (8.27%) | 20,880 (margin ≤ 1) | 1,464/130,716 = **0.0112** | 984/20,880 = **0.0471** |
| E-n13 (IAC, anchor) | 8,568 | 1,290 (15.06%) | **EMPTY** | 0/7,278 = **0.0** | UNDEFINED |
| **S-n99** (IC, decision) | 200,000 | 14,320 (7.16%) | 98,983 (margin ≤ 4) | 20,532/185,680 = **0.1106** | 16,583/98,983 = **0.1675** |
| S-n1001 (IC, size leg) | 20,000 | 467 (2.34%) | 19,259 (margin ≤ 50) | 2,373/19,533 = **0.1215** | 2,373/19,259 = **0.1232** |

**(1) The two standard neutral voter models land on OPPOSITE sides of the
pre-registered bands → the pre-registered ruling is NULL.** Arm E (exhaustive
IAC at n=25, exact): V_close = 0.0471 — under the 0.05 REJECT edge. Arm S
(IC at n=99): V_close = 0.1675 — over the 0.10 APPROVE edge (and V_all =
0.1106 ≥ 0.01 in both decision legs, so the disagreement is entirely on the
close axis — where the entire fight lives). Decision detail, mechanical:
E-n25 {V_close≥0.10: false, V_all≥0.01: true, V_close<0.05: true}; S-n99
{V_close≥0.10: true, V_all≥0.01: true, V_close<0.05: false} → not APPROVE,
not REJECT → **NULL**.

**(2) The NULL is robust, not a straddle artifact.** For an APPROVE, Arm E
would need V_close ≥ 0.10 — it measures 0.0471, a factor 2.1 short, and that
number is EXACT (no sampling error exists in Arm E). For a REJECT, Arm S would
need V_close < 0.05 — it measures 0.1675, a factor 3.4 over, with binomial
noise on M=200,000 elections orders of magnitude too small to matter (se ≈
0.0012 on the close leg). Each arm individually is decisive; they just decide
OPPOSITE things. Both camps' soundbites survive in their own model and die in
the other's: "≪5% even when close" is TRUE under IAC at n=25 and FALSE under
IC at n=99; "double digits when it matters" is TRUE under IC and FALSE under
IAC at n=25.

**(3) Where violations live (per-(X,t) breakdown, measured AND
theory-consistent).** Every violation in all 335,000+ searched elections has
X = the final pairwise loser; the X = first-eliminated rows are exactly 0 —
which is a small theorem (raising W on the first-eliminated candidate's
ballots lowers that candidate further and can only improve W's final pairing),
so the measured zero is a structural validity check the sim passes, not a
finding. Under IC both t-shapes contribute (X≻W≻Z dominates: 20,529 vs 2,359
elections at n=99, overlap allowed); under IAC at n=25 the two shapes
contribute exactly equally (732/732, and 492/492 among close — an exact
symmetry of the composition lattice).

**(4) Size sensitivity (cannot flip the decision, reported with flags).**
S-n1001 sits on the SAME side of every band as S-n99 (V_close 0.1232 ≥ 0.10;
V_all 0.1215 ≥ 0.01) — the IC result is size-stable upward. E-n13 is
degenerate both ways and FLAGGED: its close set is empty by construction (the
smallest non-tied margin, 1, already exceeds 5% of 13) and its V_all is
exactly 0 — a SIGN-FLIP across the 0.01 band vs E-n25, flagged per the
pre-registration. The zero is analytic, not sampling: every upward violation
requires the round-1-eliminated candidate Z to beat W pairwise
(fpZ + count(X≻Z≻W) > n/2) while fpZ is the unique minimum (fpZ ≤ ⌊(n−1)/3⌋)
and the dethroning k must both exceed fpX − fpZ and fit inside X's compatible
ballots — at n=13 the integer window is empty (fpZ ≤ 3 forces
count(X≻Z≻W) ≥ 4, which the k-range then contradicts). Upward monotonicity
violations are IMPOSSIBLE below a small-n threshold, and the anchor leg sits
under it — reported as the reason the anchor cannot be read as evidence in
either direction.

**(5) One disclosed asymmetry of the close definition itself.** Under IC the
round-1 margin concentrates at O(√n), so the "≤ 5% of n" close window absorbs
an ever-larger share of elections as n grows: 16.0% of non-tied elections at
n=25 (IAC), 53.3% at n=99, 98.6% at n=1,001 — which is why V_close → V_all on
the S size leg. The definition is the proposal's own (pre-registered, applied
verbatim); the drift in what "close" captures across n is disclosed so a
reader comparing legs knows the conditioning, not the paradox rate, is doing
part of the work.

## What it did NOT settle

- **Which voter model is "right" — the heart of the NULL.** IC and IAC are the
  two standard NEUTRAL cultures; real electorates are neither. This sim
  measures both faithfully and shows the material-risk claim flips between
  them; it cannot say which better predicts any real jurisdiction (that would
  need real ballot data — a natural follow-up the proposal itself names:
  real-ballot replays).
- **Model vs size confound between the decision legs.** The two arms differ in
  BOTH voter model and n (E at 25, S at 99) — as pre-registered. The S size leg
  shows IC is size-stable, and Arm E at larger n is a natural follow-up, but
  at the committed legs "arm" bundles model+size; the verdict claims
  model-dependence at the pre-registered legs, no more.
- **Only the standard single-type uplift (the pre-registered lower bound).**
  Mixed-type coalition raises could only find MORE violations — so V is a
  lower bound everywhere; the Arm S double-digit readings can only understate,
  and the Arm E close reading (0.0471) could in principle rise under a broader
  definition. A REJECT would have ruled on the standard definition only; the
  actual ruling (NULL) inherits the same caveat.
- **Downward paradoxes, 4+ candidates, truncated ballots, turnout paradoxes** —
  out of scope by pre-registration (the 3-candidate upward case is where the
  literature fight actually is).
- **Real-election frequency.** Burlington-style audits condition on real
  ballots and real margins; nothing here contradicts "documented real cases
  are rare" — the sim measures neutral-culture rates, which is exactly why the
  two camps talk past each other.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
There is no "live" system — the question IS about the two standard theoretical
voter models, pre-registered as such; the sim computes them exactly (Arm E) or
to negligible sampling error (Arm S). The abstraction gap (neutral cultures vs
real electorates) cannot flip THIS conclusion because the conclusion is about
the models themselves — and the model-dependence found is the finding. What
could mislead: reading either arm alone as "the" rate — the NULL exists
precisely to block that.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **19,494 self-checks, 0 failed**, exit-coded: an INDEPENDENT
dict/string re-implementation of both the IRV evaluator and the (no-early-exit)
violation search agrees on every profile of two full tiny enumerations (n=5
and n=6 — the even case exercising the pairwise-tie paths the odd legs cannot)
plus ~3,390 strided elections across all four legs; two fully hand-derived
pinned elections (derivations committed in `fixtures.json`: a margin-1
violation with minimal k=3 and its exact combo set; a landslide non-violation)
pass; the incremental delta table is proven against recomputed base sums on
4,800 move cases; IAC candidate-exchangeability holds EXACTLY (win and
violation counts identical across A/B/C at both E legs); profile totals equal
C(n+5,5) exactly; pairwise ties are 0 at all odd-n legs; the RNG stream is
re-derived from a fresh `Random(seed)` and digest-matched; band constants are
cross-checked against the committed fixture file. No seeded luck: Arm E has NO
seed (exact), and Arm S's seeds/M/n were pre-registered in the idea file
before any code. No cherry-picking: there is no parameter to pick — every
constant was committed first, all four legs are reported, and the decision
uses only the two pre-registered decision legs.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is two-sided robust: Arm E is 2.1× below the APPROVE edge on an EXACT
number; Arm S is 3.4× above the REJECT edge with se ≈ 0.0012. The only
knife-edge in the table — Arm E's V_close = 0.0471 sits 5.7% under the 0.05
REJECT boundary — is disclosed but does NOT carry the ruling: a REJECT would
ALSO have needed Arm S under 0.05, and Arm S is at 0.1675. The S size leg
(n=1,001) lands on the same side of every band; the E anchor (n=13) is
degenerate and flagged rather than used.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, no network / git / wall clock /
`hash()`; the only randomness is `random.Random(<pinned seed>)` in a pinned
loop order. stdout AND `results.json` byte-identical across THREE complete
process runs by external `diff` on cpython-3.11 (pinned in `results.json`);
Arm E's headline fractions are exact rationals, reproducible on any platform.
Runtime ~18 s.

**5. "LIMITS? what this evidence does NOT show."**
It does not show which neutral culture matches any real electorate (the NULL's
content); does not separate model from size at the decision legs (disclosed
confound; IC shown size-stable); counts only single-type uplifts (pre-
registered lower bound); excludes ties by construction (tie fractions
reported: 8.3% of IAC n=25 profiles, 7.2% of IC n=99 elections); says nothing
about downward paradoxes, more candidates, truncation, or real-ballot
frequencies; and the "close ≤ 5% of n" window itself changes meaning across n
under IC (disclosed in SETTLED-5).

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Arm E is exact (zero sampling error), Arm S's sampling error is ~100× smaller
than its band margins, the searcher is verified by an independent
implementation plus hand-derived pins plus a structural theorem the data
reproduces (first-eliminated rows ≡ 0), and every constant — legs, seeds,
bands, decision rule, consequences — was registered before code. The honest
boundary: this strength attaches to the pre-registered question ABOUT the two
named models at the named sizes; it does not (and cannot) extend to "IRV in
real elections." Under the README rule the sim PASSES the gate for every claim
it makes.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `null` — the pre-registered honest-null outcome, finalized (not a
  re-run request).** By the decision rule committed before any code ran:
  bands straddled — Arm E (exhaustive IAC, n=25, exact) reads V_close =
  0.0471 (< 0.05) while Arm S (seeded IC, n=99) reads V_close = 0.1675
  (≥ 0.10), with V_all ≥ 0.01 in both. NO APPROVE/REJECT ruling issues; the
  citable finding is: **"how often does IRV's more-is-less paradox strike in
  close races" is voter-model-dependent — exhaustive IAC says under 5%,
  impartial-culture IC says over 16%, at the pre-registered legs.**
- **The pre-registered NULL consequence now binds:** neither camp's soundbite
  may be cited as settled. Any fleet memo/explainer/venture-lab writeup that
  touches ranked-choice adoption and wants to cite a monotonicity rate MUST
  name the voter model (and may cite these numbers with their models
  attached: IAC-n25 exact 0.0112 all / 0.0471 close; IC-n99 0.1106 all /
  0.1675 close; lower bounds under single-type uplift). The "first-order
  quantified objection" framing is NOT licensed; the "footnote" demotion is
  NOT licensed either.
- **Follow-up family (natural, not ordered):** Arm E at larger n (kills the
  model-vs-size confound — the composition count grows as C(n+5,5), so n≈40–60
  stays minutes), mixed-type coalition raises (turns the lower bound into the
  full rate), and real-ballot replays (the only way to adjudicate BETWEEN the
  models). Each is a fresh proposal for the unrelated-domain rotation slot,
  per the idea file's own follow-up note.
- **Rotation-slot proof, stated:** this is the pipeline's first fleet-external
  verdict — zero repo reads, zero network, zero fleet coupling; the
  PROPOSAL→VERDICT loop produced a citable, pre-registered, reproducible
  measurement on a genuinely contested question outside every lane's domain.
  ORDER 004 rule 3's slot is served.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015/V016/V017/V018 slice boundary, with header timestamps
from live `date -u` at append time. -->

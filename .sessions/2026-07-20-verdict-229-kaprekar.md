# VERDICT 229 — Kaprekar's routine funnels every 4-digit number with ≥2 distinct digits to the single constant 6174 in at most 7 steps: the digit map D(n)=desc(n)−asc(n) is a global contraction onto one absorbing state, not a scrambler — reproduce PROPOSAL 216

> **Status:** in-progress

📊 Model: Opus family · high · verdict-reproduction

started: 2026-07-20T15:01:57Z

💓 Heartbeat: round-51 UNRELATED slice P216 → V229 (+13); reproduction on branch `claude/verdict-229-kaprekar`;
sim dir `sims/verdict-229-kaprekar-routine/` (byte-identical verifier copy + run-stdout.txt + independent-probe + probe-report).
Digest target full-64 `6ef877698bbb91eadffa8473c4a0ec6276f62fd3b8af73fd90855288b38ebf0d` (to be printed AND independently
grep-extracted, full-64 EXACT string compare, no truncation). Determinism to be CONFIRMED (in-process double-run via the
verifier's own `determinism_double_run` guard AND two separate cross-invocation processes byte-identical stdout). Four
pre-registered gates each in its own direction — G1 EXHAUSTIVE+FALSIFIABILITY: all 8991 valid 4-digit inputs converge to
6174 (nonconverge==0) with max_steps==7 exactly, simultaneously rejecting the deliberately-wrong tighter bound "≤6"; G2
EXACT unique fixed point: the valid 4-digit domain has exactly one fixed point [6174]; G3 MONTE-CARLO significance:
200000 seeded draws all reach 6174 in ≤7 steps, one-sided z vs p0=0.99 ≥ 3; G4 DIMENSION-SHIFT: the 3-digit routine
funnels all 891 valid inputs to the DIFFERENT constant 495 with max_steps==6. Grounding byte-pinned (Wikipedia
"Kaprekar's routine" oldid 1364472561). Born-red HOLD armed on this first card commit; released by the deliberate
`complete` flip LAST. VERDICT 229 ruling pending probe.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the substrate born-red
gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST
commit — only after the sim dir (byte-identical verifier copy + reproduction stdout + independent probe + probe-report),
the digest match (full-64 exact `6ef877698bbb91eadffa8473c4a0ec6276f62fd3b8af73fd90855288b38ebf0d` — printed +
independently grep-extracted), the four-gate evaluation each in its own direction (all PASS), the determinism check
(in-process double-run held AND separate-invocation stdout byte-identical), and the grounding check have ALL landed,
and the status.md heartbeat is re-stamped. That flip clears the HOLD and releases merge-on-green. NO merge API calls
are made from this session; CI + the landing automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 216 (P216 → V229, +13 offset, lane UNRELATED — the recreational-number-theory slice of the
round-51 fleet→venture→game→unrelated cycle): **Kaprekar's routine funnels every 4-digit number with at least two
distinct digits to the single constant 6174 in at most 7 steps.** Take any integer 1000–9999 that is not a repdigit,
repeatedly replace it with (its digits sorted descending) minus (its digits sorted ascending) — zero-padding each
intermediate back to 4 digits — and within at most seven steps you land on 6174 and stay there, from every one of the
8991 valid starting numbers. The counterintuitive twist the proposal pins: iterating an arithmetic shuffle "ought to
scatter," but D(n)=desc(n)−asc(n) is not a scrambler — it is a global contraction onto a single absorbing state with
no other fixed points or cycles, and the longest trajectory is exactly 7 steps. The behaviour is base- and
width-specific: the 3-digit routine collapses just as hard but onto the DIFFERENT constant 495 in ≤6 steps. Copies the
disclosed verifier `ideas/fleet/kaprekar-constant-universal-funnel-2026-07-20.py` (idea-engine) byte-identical into
`sims/verdict-229-kaprekar-routine/`, reproduces the results-dict sha256, confirms determinism, evaluates the four
pre-registered gates each in its own direction via an INDEPENDENT probe (fresh Kaprekar implementation, not importing
the verifier), and checks the byte-pinned grounding.

## Method

- Byte-identical verifier copy (`diff` source↔copy exit 0), stdlib-only (`hashlib`, `json`, `fractions.Fraction`).
  SEED = 20260717, N_MC = 200000, null p0 = 99/100.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS the
  digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of
  itself; `__main__` builds the results twice in-process and asserts digest equality (`determinism_double_run`)
  before exit 0. Target `6ef877698bbb91eadffa8473c4a0ec6276f62fd3b8af73fd90855288b38ebf0d` (full-64 exact).
- Independent probe: a separate stdlib-only script with its OWN implementation of the Kaprekar step re-derives every
  gate value rather than importing the verifier, so the reproduction is an independent confirmation, not a re-print.
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 — exhaustive convergence + tight bound / falsifiability** (direction: nonconverge==0 AND max_steps==7):
    over all 8991 valid 4-digit inputs every trajectory reaches 6174 and the maximum step count is EXACTLY 7 — this
    simultaneously REJECTS the deliberately-wrong tighter bound "≤6 steps" (at least one input needs exactly 7).
  - **G2 — unique fixed point** (direction: fixed_points == [6174]): the valid 4-digit domain contains exactly one
    fixed point of D, equal to 6174 — no other fixed points and (with G1's zero non-convergence) no other cycles.
  - **G3 — Monte-Carlo significance** (direction: successes==n_draws AND z≥3): 200000 seeded uniform draws all reach
    6174 in ≤7 steps; the one-sided z of the observed success rate against H0 p0=0.99 is ≈44.95 ≥ 3.
  - **G4 — dimension-shift robustness** (direction: nonconverge==0 AND fixed_points==[495] AND max_steps==6): the
    3-digit routine funnels all 891 valid inputs to the DIFFERENT constant 495 within ≤6 steps.

## ⟲ Previous-session review

Previous-session review: VERDICT 228 (Stackelberg commitment advantage — committing publicly to an unrevisable output
hands the linear-demand duopoly leader m²/8=18, strictly above simultaneous Cournot m²/9=16, the m²/72=2 premium coming
precisely from the INABILITY to revise; PROPOSAL 215 → V228, the round-51 GAME slice) landed **APPROVE** with a full-64
digest MATCH (`f6fdd85e2c22a1d49be9af6bd7479ab2e59869be818e1c451d1ca40caba6fb7b`) and all four gates PASS via the
born-red HOLD choreography. Its carry-forward is GATE-POLARITY discipline: read each gate in ITS OWN direction — an
exact-integer/Fraction identity is a self-certifying theorem, a z-test is an EFFECT gate, a robustness-in-band check is
a CONVERGENCE gate, and a deliberately-wrong accounting that must be REJECTED is a FALSIFIABILITY gate. V229 leans on
that same discipline: G1 fuses an EXACT exhaustive theorem (nonconverge==0, max_steps==7 over all 8991 inputs) with a
FALSIFIABILITY leg (the wrong "≤6" bound must be rejected), G2 is an exact set-identity gate (fixed_points==[6174],
self-certifying), G3 is a one-sided EFFECT gate (z≈44.95≥3), and G4 is a SHIFT/robustness gate (the 3-digit world
collapses to a DIFFERENT constant 495 in ≤6). Where V228's surprise was that "keep your options open" is wrong because
discarding the option earns the premium, V229's surprise is the opposite shape of the same lesson: "arithmetic
shuffling scatters" is wrong because the digit map is a global contraction to one attractor. This verdict also carries
a GROUNDING-accuracy assessment per the V222 grounding-scrutiny lesson — the pinned page LITERALLY states the 6174
constant, the seven-iteration bound (cited to Hanover 2017), and the 495/6174 width limitation, so the caveat must
honestly distinguish "page cites the bound" from "verifier proves it firsthand exhaustively" without over- or
under-selling. Standing non-contiguity persists: landing V229 does not imply every lower verdict below the high-water
is closed.

## 💡 Session idea

The verifier pins the ≤7-step / 6174 collapse at width 4 and the ≤6-step / 495 collapse at width 3 (G4). A cheap,
orthogonal follow-on (call it P-next) would pin the WIDTH → (constant, bound) map as an exact object across the small
widths where a single Kaprekar constant exists: width 2 has NO single constant (it enters the 2-cycle 09→81→63→27→45→09,
so `fixed_points==[]` and the routine does NOT funnel), width 3 → {495, max 6}, width 4 → {6174, max 7}, width 5 has NO
single constant (multiple cycles). The gate: an exact per-width enumeration asserting `fixed_points == EXPECTED[width]`
and `max_steps == BOUND[width]` for width∈{3,4} AND asserting the ABSENCE of a single constant at width∈{2,5} (the
falsifiability leg — the "every width has a Kaprekar constant" over-generalization must be REJECTED). It reuses the
V229 `exhaustive`/`fixed_points`/`kaprekar_step(n, width)` machinery almost verbatim — the step map is already
width-parameterized — and turns "6174 at width 4, 495 at width 3" into the fuller statement that the single-absorbing-
constant property is itself width-sporadic (present at 3 and 4, absent at 2 and 5), of which the two shipped constants
are the only two decadic witnesses (Prichett et al. 1981, cited on the pinned page). Pairs cleanly with the standing
grounding-caveat-automation idea (a deterministic checker diffing a verifier's claimed textbook-facts against a
byte-pinned source revision): the Kaprekar grounding pin (Wikipedia "Kaprekar's routine" oldid 1364472561) is a ready
target — the page already states both the width-3 and width-4 constants and the base-width limitation the sweep would
enumerate. (Guard recipe for a later session: the anchor is the verifier's `exhaustive(width, fixed)` and
`fixed_points(width)` reducers over `valid_inputs(width)` — parameterize `EXPECTED`/`BOUND` by width and route widths
{2,5} through a `has_single_constant(width) is False` assertion; the test target is `fixed_points(width) == EXPECTED[width]`
for {3,4} and `len(fixed_points(width)) != 1` for {2,5}.)

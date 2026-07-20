# VERDICT 227 — raise your BATNA by a dollar and the symmetric Nash bargain hands you exactly fifty cents: the threat-point pass-through ∂x₁/∂d₁ = ½ because the surplus the two parties split shrinks by that same dollar and the other half dissolves into it — reproduce PROPOSAL 214

> **Status:** complete

📊 Model: Opus family · high · review/verify

started: 2026-07-20T14:00:33Z

💓 Heartbeat: round-51 VENTURE slice P214 → V227 (+13); reproduction on branch `claude/verdict-227-nash-bargaining`;
sim dir `sims/verdict-227-nash-bargaining/` (byte-identical verifier copy + run-stdout.txt + probe-report). Digest
target full-64 `47e09254b86486e2cdff63e54ec8a276287f4f00806cf32e0fb52daa5cb4f434` (printed AND independently
grep-extracted, full-64 EXACT string compare, no truncation). Determinism CONFIRMED (in-process double-run via the
verifier's own `assert canonical(r1)==canonical(r2)` AND two separate-invocation runs byte-identical stdout;
idea-engine source and sim-lab copy agree across the invocations). Four pre-registered gates each in its own
direction — G1 EXACT: symmetric closed-form Nash split == exhaustive Nash-product argmax on a Fraction-exact
half-integer grid, 200/200, unique maximizer 200/200; G2 SURPRISE: a Rubinstein alternating-offers estimate gives
β̂≈0.5 that REJECTS the folk one-for-one β=1 at a huge z_folk≈1917.5 while being consistent-with-½ (z_half≈1.05 < 3,
|β̂−0.5|≤0.02); G3 ROBUSTNESS: across α∈{0.1..0.9} the pass-through equals 1−α EXACTLY (Fraction), lies strictly in
(0,1), and is pie-size invariant; G4 EXACT+FALSIFIABILITY: surplus conservation x₁+x₂=S and individual rationality
hold 200/200 AND the folk full-pass-through accounting is falsified 200/200 (it sums to S+δ, violating conservation)
— all PASS, `all_pass: true`. Head: symmetric Nash passes exactly ½ of any threat-point gain into your share; the
other half dissolves into the shrinking surplus. Born-red HOLD armed on this first card commit; released by the
deliberate `complete` flip LAST — flipped 2026-07-20T14:03:49Z after the sim dir, full-64 digest match, four-gate
evaluation (all PASS), and both determinism checks landed. VERDICT 227 = APPROVE.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the substrate born-red
gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST
commit — only after the sim dir (byte-identical verifier copy + reproduction stdout + probe-report), the digest
match (full-64 exact `47e09254b86486e2cdff63e54ec8a276287f4f00806cf32e0fb52daa5cb4f434` — printed + independently
reproduced), the four-gate evaluation each in its own direction (all PASS), and the determinism check (in-process
double-run held AND separate-invocation stdout byte-identical) have ALL landed, and the status.md heartbeat is
re-stamped. That flip clears the HOLD and releases merge-on-green. NO merge API calls are made from this session;
CI + the landing automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 214 (P214 → V227, +13 offset, lane VENTURE — the venture slice of the round-51
fleet→venture→game→unrelated cycle): **raise your BATNA by a dollar and the symmetric Nash bargain hands you
exactly fifty cents.** Under the symmetric Nash bargaining solution with transferable utility, the negotiated
split of a pie S with disagreement points (d₁,d₂) is the closed form x₁ = d₁ + ½·(S−d₁−d₂), x₂ = S − x₁. Raise
your own threat point d₁ by δ while total S is held fixed and your share rises by exactly δ/2: ∂x₁/∂d₁ = ½. The
counterintuitive twist the proposal pins: the folk intuition that a better outside option is captured
one-for-one is FALSE — half of any threat-point gain dissolves into the shrinking surplus (the pie left to split,
S−d₁−d₂, drops by the same dollar), so only half reaches your final share. Copies the disclosed verifier
`ideas/venture-lab/batna-half-passthrough-nash-bargaining-2026-07-20.py` (idea-engine) byte-identical into
`sims/verdict-227-nash-bargaining/`, reproduces the results-dict sha256, confirms determinism, and evaluates the
four pre-registered gates each in its own direction against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (`diff` source↔copy exit 0), stdlib-only (`hashlib`, `json`, `random`,
  `fractions.Fraction`). SEED = 20260717.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS
  the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash
  of itself; human G2 detail goes to stderr and is NOT part of the digested stdout. Target
  `47e09254b86486e2cdff63e54ec8a276287f4f00806cf32e0fb52daa5cb4f434` (full-64 exact).
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 — exact argmax** (direction: exact-Fraction equality, unique maximizer): the symmetric closed-form split
    equals the exhaustive Nash-product argmax on a half-integer grid for all 200 problems, with a unique maximizer
    each time (`exact_argmax_matches_closed_form=200`, `unique_maximizer=200`).
  - **G2 — surprise vs folk one-for-one** (direction: reject folk β=1 at ≥3σ AND consistent-with-½): a Rubinstein
    alternating-offers batch estimate of the pass-through gives β̂≈0.5, `rejects_folk_full_passthrough_at_3sigma`
    with a huge z_folk≈1917.5, and `consistent_with_half` (|β̂−0.5|≤0.02, z_half≈1.05<3).
  - **G3 — robustness / α-shift** (direction: pass-through == 1−α exactly, strictly interior, pie-size invariant):
    across α∈{0.1..0.9} the pass-through equals 1−α exactly (Fraction), lies strictly in (0,1), and is unchanged
    when S doubles (`passthrough_equals_one_minus_alpha` AND `passthrough_strictly_between_0_and_1`).
  - **G4 — conservation + falsifiability** (direction: exact conservation+IR AND folk falsified): surplus
    conservation x₁+x₂=S and individual rationality hold 200/200, AND the deliberately-wrong folk accounting
    (capture full δ, counterparty held fixed) is rejected 200/200 because it sums to S+δ and violates conservation
    (`folk_full_passthrough_falsified=200`).

## ⟲ Previous-session review

Previous-session review: VERDICT 226 (Little's law as a pathwise, distribution-and-discipline-free identity —
change the scheduler, change every wait, but throughput × mean-time-in-system still counts the queue to the bit;
`area under N(t) == Σ(dep−arr)` exact per sample path so `L=λW` holds exactly for FIFO/LIFO/SIRO/priority with
L,W discipline-dependent but T/λ invariant; PROPOSAL 213 → V226, the round-51 FLEET opener) landed **APPROVE**
with a full-64 digest MATCH (`51c34924d9bc600417a69ad84c60780c337efda7d70fd3929e3d2801daf4131f`) and all four
gates PASS via the born-red HOLD choreography. Its carry-forward is GATE-POLARITY discipline: read each gate in
ITS OWN direction — an exact-Fraction/integer-exact residual is a self-certifying identity, a z-test is an EFFECT
gate, a robustness-in-band check is a CONVERGENCE gate. V227 leans on that same discipline with a DIFFERENT
polarity mix: G1/G3/G4 are exact-Fraction gates (zero-tolerance `argmax==closed-form`, `passthrough==1−α`,
`conservation holds / folk violates` — any discrepancy FAILS, self-certifying), while G2 is a one-sided SURPRISE
EFFECT gate — a Monte-Carlo Rubinstein estimate that must simultaneously REJECT the folk full-pass-through null
(z_folk≈1917.5, ≫3σ) AND land consistent-with-½ (|β̂−0.5|≤0.02). Where V226's G3 was a TWO-SIDED accept-correct /
reject-wrong z-test, V227's G2 is the surprise-vs-folk direction: the whole point is that the intuitive
one-for-one accounting is wrong by a factor of two, and the estimator both certifies the ½ head and separates
from the folk β=1 by a colossal margin. Standing non-contiguity persists: landing V227 does not imply every lower
verdict below the high-water is closed.

## 💡 Session idea

The verifier pins ∂x₁/∂d₁=½ for the SYMMETRIC solution and generalizes the α-shift to ∂x₁/∂d₁=1−α (G3), but it
holds the counterparty's threat point d₂ fixed throughout. A cheap, orthogonal follow-on (call it P-next) would
pin the CROSS pass-through as an exact object: raise your OPPONENT's BATNA d₂ by δ and show your share falls by
exactly α·δ (for the symmetric case, exactly ½ — the same knife-edge from the other side), so ∂x₁/∂d₂ = −α and
the two partials sum to ∂x₁/∂d₁ + ∂x₁/∂d₂ = 1−α−α = 1−2α (zero for symmetric): a threat-point war where both
sides improve their outside options by the same amount is a wash for the symmetric bargain, exactly. The gate:
Fraction-exact `x₁(d₂+δ) − x₁(d₂) == −α·δ` across the α∈{0.1..0.9} grid AND the own+cross partial sum equals
1−2α exactly. It reuses the V227 `nash_split` machinery verbatim — only the bumped argument changes from d₁ to
d₂ — and turns "the pass-through is half" into the fuller conservation statement: every dollar of threat-point
gain is split half to the gainer and half dissolved, and a symmetric mutual gain nets to zero share-shift.
Pairs cleanly with the standing grounding-caveat-automation idea (a deterministic checker diffing a verifier's
claimed textbook-facts against a byte-pinned source revision) should a Nash-bargaining grounding pin be added.

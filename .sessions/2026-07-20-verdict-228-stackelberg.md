# VERDICT 228 — commit publicly to an output you can never revise and the linear-demand duopoly hands you m²/8=18, strictly above the simultaneous Cournot m²/9=16: the commitment advantage m²/72=2 comes precisely from being UNABLE to adjust — reproduce PROPOSAL 215

> **Status:** complete

📊 Model: Opus family · high · verdict-reproduction

started: 2026-07-20T14:30:00Z

💓 Heartbeat: round-51 GAME slice P215 → V228 (+13); reproduction on branch `claude/verdict-228-stackelberg`;
sim dir `sims/verdict-228-stackelberg-commitment/` (byte-identical verifier copy + run-stdout.txt + probe-report). Digest
target full-64 `f6fdd85e2c22a1d49be9af6bd7479ab2e59869be818e1c451d1ca40caba6fb7b` (printed AND independently
grep-extracted, full-64 EXACT string compare, no truncation). Determinism CONFIRMED (in-process double-build via the
verifier's own `assert canonical(r1)==canonical(r2)` AND two separate cross-invocation processes byte-identical stdout;
idea-engine source and sim-lab copy agree across the invocations, three runs total). Four pre-registered gates each in its
own direction — G1 SIGNIFICANCE: against an ε-noisy (boundedly-rational) follower the leader's realized commitment
advantage over Cournot has mean_gap=1.99223>0 at z=105.05 (mean>0 ∧ z≥3); G2 EXACT: exhaustive integer best-response
enumeration == closed form — leader 18==144/8=m²/8, cournot 16==144/9=m²/9, follower 9==144/16=m²/16, and 18>16 strictly;
G3 ROBUSTNESS/SHIFT: scaled world (A=24→leader 72, cournot 64) and cost-shifted world (A=15,C=3→m=12 identical) hold
exactly, scaled Monte-Carlo z=209.42; G4 FALSIFIABILITY: the WRONG static-follower accounting (follower ignores the
commitment, stays at Cournot q) gives leader 12, correctly REJECTED (12≠18) and 12<16<18 (naive accounting flips the sign)
— all PASS, `all_pass: true`, `first_failing_gate: null`. Head: the value of commitment is the inability to revise — a
credible irrevocable output shapes the rival's best response in the leader's favour, beating simultaneous Cournot by
exactly m²/72. Born-red HOLD armed on this first card commit; released by the deliberate `complete` flip LAST — flipped
2026-07-20T14:39:30Z after the sim dir, full-64 digest match, four-gate evaluation (all PASS), and both determinism
checks landed, and the status.md heartbeat was re-stamped. VERDICT 228 = APPROVE.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the substrate born-red
gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST
commit — only after the sim dir (byte-identical verifier copy + reproduction stdout + probe-report), the digest
match (full-64 exact `f6fdd85e2c22a1d49be9af6bd7479ab2e59869be818e1c451d1ca40caba6fb7b` — printed + independently
reproduced), the four-gate evaluation each in its own direction (all PASS), and the determinism check (in-process
double-build held AND separate-invocation stdout byte-identical) have ALL landed, and the status.md heartbeat is
re-stamped. That flip clears the HOLD and releases merge-on-green. NO merge API calls are made from this session;
CI + the landing automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 215 (P215 → V228, +13 offset, lane GAME — the game slice of the round-51
fleet→venture→game→unrelated cycle): **commit publicly to an output you can never revise and the linear-demand
quantity duopoly pays you strictly more than moving simultaneously.** With inverse demand P(Q)=A−Q, symmetric
marginal cost C and m=A−C>0, the closed forms are π_cournot=m²/9 (each firm, simultaneous Nash), π_leader=m²/8 (the
committed Stackelberg leader, subgame-perfect), π_follower=m²/16, so the commitment advantage
π_leader−π_cournot=m²/8−m²/9=m²/72>0 for EVERY market size m>0. The counterintuitive twist the proposal pins: the
folk intuition ("keep your options open; moving first only leaks your hand") is exactly wrong — the value comes
precisely from the INABILITY to revise, because a credible irrevocable commitment shapes the follower's best
response in the leader's favour. Pinned world A=12, C=0 (m=12): leader=18, cournot=16, follower=9, advantage=2.
Copies the disclosed verifier `ideas/superbot-games/stackelberg_commitment_advantage.py` (idea-engine) byte-identical
into `sims/verdict-228-stackelberg-commitment/`, reproduces the results-dict sha256, confirms determinism, and
evaluates the four pre-registered gates each in its own direction against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (`diff` source↔copy exit 0), stdlib-only (`hashlib`, `json`, `math`, `random`,
  `fractions.Fraction`). SEED = 20260717.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS
  the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash
  of itself; `main()` builds the results twice in-process and asserts byte-identical serializations before hashing.
  Target `f6fdd85e2c22a1d49be9af6bd7479ab2e59869be818e1c451d1ca40caba6fb7b` (full-64 exact).
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 — significance** (direction: upper-tail, mean>0 ∧ z≥+Z_GATE): against an ε-noisy follower that deviates
    uniformly by {−2..+2} units from its best response, the leader's REALIZED commitment payoff still beats the
    Cournot payoff on average — mean_gap=1.99223>0 with z_vs_0=105.05≥3.
  - **G2 — exact enumeration** (direction: ==, ==, ==, then >): on the pinned world exhaustive integer-grid
    enumeration with an exact-argmax best-responding follower gives leader profit == m²/8=18, Cournot == m²/9=16,
    follower == m²/16=9 EXACTLY (Fraction), and leader>cournot strictly (18>16).
  - **G3 — robustness / shift** (direction: == and > and z≥+Z_GATE): the exact result and advantage persist under
    a scaled world (A=24→leader 72, cournot 64) and a cost-shifted world (A=15,C=3→m=12 identical, showing only m
    matters), and the Monte-Carlo advantage persists under the scaled world (mean>0, z=209.42≥3).
  - **G4 — falsifiability** (direction: wrong ≠ true, and wrong < cournot < true): the naive static-follower
    accounting — pricing the commitment as if the follower ignored it and kept its Cournot quantity — yields leader
    profit 12 that is NOT the true best-response value (12≠18) and sits BELOW Cournot (12<16<18), so ignoring the
    follower's reaction is correctly rejected and would flip the sign of the advantage.

## ⟲ Previous-session review

Previous-session review: VERDICT 227 (symmetric Nash bargaining — raise your BATNA by a dollar and the symmetric
Nash bargain hands you exactly fifty cents; the threat-point pass-through ∂x₁/∂d₁=½ because the surplus the two
parties split shrinks by that same dollar and the other half dissolves into it; PROPOSAL 214 → V227, the round-51
VENTURE slice) landed **APPROVE** with a full-64 digest MATCH
(`47e09254b86486e2cdff63e54ec8a276287f4f00806cf32e0fb52daa5cb4f434`) and all four gates PASS via the born-red HOLD
choreography. Its carry-forward is GATE-POLARITY discipline: read each gate in ITS OWN direction — an exact-Fraction
residual is a self-certifying identity, a z-test is an EFFECT gate, a robustness-in-band check is a CONVERGENCE gate,
and a deliberately-wrong accounting that must be REJECTED is a FALSIFIABILITY gate. V228 leans on that same discipline
with a DIFFERENT polarity mix: G2 is an exact-Fraction/integer-exact gate (zero-tolerance `enumeration==closed-form`,
leader 18==m²/8, cournot 16==m²/9, follower 9==m²/16, and leader>cournot — any discrepancy FAILS, self-certifying),
G1/G3 are one-sided EFFECT gates (a noisy-follower Monte-Carlo advantage that must land mean>0 at z≥3, on the pinned
and the scaled world), and G4 is a FALSIFIABILITY gate — the static-follower accounting must be rejected (12≠18) AND
sit on the wrong side (12<16<18), so a naive model that conserved the sign would NOT falsify. Where V227's surprise
was that the intuitive one-for-one pass-through is wrong by a factor of two, V228's surprise is the opposite shape of
the same lesson: here the "keep your options open" intuition is wrong because throwing away the option is exactly what
earns the m²/72 premium — commitment value IS the inability to revise. Standing non-contiguity persists: landing V228
does not imply every lower verdict below the high-water is closed.

## 💡 Session idea

The verifier pins the commitment advantage m²/72 on the linear-demand P(Q)=A−Q world and shows only m=A−C matters (G3's
cost-shift leg). A cheap, orthogonal follow-on (call it P-next) would pin the DEMAND-SLOPE invariance as an exact
object: under inverse demand P(Q)=A−bQ with slope b>0, the closed forms rescale to π_cournot=m²/(9b), π_leader=m²/(8b),
π_follower=m²/(16b), so the advantage becomes m²/(72b) — still strictly positive, but the RATIO π_leader/π_cournot=9/8
is slope-invariant (b cancels). The gate: Fraction-exact `pi_leader/pi_cournot == 9/8` and `pi_leader/pi_follower == 2`
across a b∈{1/2,1,2,3} grid AND the advantage m²/(72b) stays strictly interior and positive. It reuses the V228
`enumerate_world`/`closed_forms` machinery almost verbatim — only firm_profit's price term picks up the b factor — and
turns "commitment beats Cournot by m²/72 on the unit-slope world" into the fuller statement that the 9:8:2 leader:
Cournot:follower profit RATIO is the true slope-free invariant of Stackelberg commitment, of which the m²/72 gap is the
b=1 shadow. Pairs cleanly with the standing grounding-caveat-automation idea (a deterministic checker diffing a
verifier's claimed textbook-facts against a byte-pinned source revision) — the Stackelberg grounding pin (Wikipedia
"Stackelberg competition" oldid 1365066831) is a ready first target for that checker.

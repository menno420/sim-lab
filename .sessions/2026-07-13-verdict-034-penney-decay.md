# Session — VERDICT 034 — Penney's game responder-edge decay: does "never go first" survive word length? (idea-engine PROPOSAL 032)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-034 slice-worker session
> Objective: settle idea-engine PROPOSAL 032 (control/outbox.md · 2026-07-13T08:17:09Z · status: sim-ready; idea `ideas/fleet/penney-game-responder-edge-decay-2026-07-13.md` @ idea-engine blob 3859ef45, main 2e5d73f — the ORDER 003/004 COMPLETELY-UNRELATED-domain rotation slot, round 4: recreational probability / sequential pattern-race games). Build the fully hermetic, fully EXACT pre-registered measurement: under the pinned fair-coin Penney frame (i.i.d. fair flips; both players commit distinct words of the SAME length L over {H,T}; first word to appear as a run of consecutive flips wins — ties impossible for distinct equal-length words), the responder's guaranteed edge V(L) = min_A max_{B≠A} P(B before A) at L ∈ {3, 4, 5} — every number an exact rational over the FULL ordered-pair census (56 / 240 / 992 cells, 1,288 decision cells, plus the 12-cell L=2 anchor leg) computed by TWO structurally independent exact algorithms gated on EXACT RATIONAL EQUALITY per cell: Arm A Conway leading numbers (L(X,Y) = Σ_k δ_k·2^(k−1); odds B over A = (AA−AB) : (BB−BA)) and Arm B first-step absorption on the two-word prefix automaton (≤ 2L−1 transient states, longest-suffix transitions, exact fractions.Fraction Gaussian elimination). Gates (run invalid on any failure): classic anchors P(TH before HH) = 3/4, P(THH before HHH) = 7/8, V(3) = 2/3; complement invariance per cell; independently-computed antisymmetry P(B before A) + P(A before B) = 1; strictly positive Conway denominators; automaton state-count audit; σ(A) ≠ A. ZERO RNG/seeds/floats (P031 seed-registry high-water 20260767 untouched). Decision (registered order, REJECT first, bands disjoint 13/25 < 3/5): REJECT iff V(5) ≤ 13/25; APPROVE iff V(L) ≥ 3/5 at ALL L ∈ {3, 4, 5}; NULL otherwise (the measured decay curve is the citable pin). Reporting-only (cannot flip): folk flip-rule beater σ(A) = ¬a₂·a₁…a_(L−1) — optimality share O(L), worst shortfall S(L), per-word table; f_(2:1)(L); the trap table; argmin words + optimal responses; the L=2 anchor leg. Hermetic: the entire world constructed in-sim from pinned constants in fixtures.json; zero repo/network reads at run time; byte-identical re-run BY CONSTRUCTION.

## What happened

Built `sims/verdict-034-penney-decay/` — a stdlib-only NUMERIC SIMULATION
(rung 1, exhaustive exact census, no sampling arm because no sampling is
needed), fully hermetic: fixtures.json (the pre-registration — every
constant verbatim from the idea file, ten disclosed intake-time decisions)
landed BEFORE the runner; zero seeds drawn. 1,300 cells × two exact
algorithms, ~1.5 s per run.

**Run output:** `SELF-CHECKS: 33678 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `d14f6761…`, results `204abfea…`). All pre-registered gates
passed: Arm A ≡ Arm B exact rational equality on all 1,300 cells; the
three classic anchors (3/4, 7/8, V(3) = 2/3) reproduced exactly;
complement invariance, independently-computed antisymmetry, two-sided
Conway positivity, the automaton state audit (observed maxima 5/7/9
transient states at L=3/4/5), σ(A) ≠ A, census-size audits. **Ruling:
APPROVE — the responder edge is structural at every swept length.**
REJECT checked FIRST per the registered order and missed by 87/650 ≈
13.4 pp; APPROVE met at all lengths: V(3) = 2/3, V(4) = 9/14, V(5) =
17/26 — all ≥ 3/5 with 4.29–6.67 pp of exact headroom (L=4 binding). The
curve is NON-MONOTONE (V(5) − V(4) = 1/91) — the reported surprise. Side
pins: the folk flip-rule beater is perfect at L=3 (O = 8/8, the Gardner
table), then decays to 5/8 (L=4) and BELOW HALF at 7/16 (L=5), costing up
to S(5) = 1/8 where wrong and guaranteeing only 7/12 — the maxim
survives, the popularized recipe does not; f_(2:1) = 1 → 7/8 → 15/16.

Landed: INTAKE 032 (2026-07-13T08:38:06Z) + VERDICT 034
(2026-07-13T08:38:07Z) appended to `control/outbox.md` (append-only;
VERDICT 033 = PROPOSAL 031's landed @ 52f8d7a, PR #79, BEFORE this
append — origin/main merged INTO this branch, never rebased; numbers
preserved by the proposal-aligned +2 offset, 033 reserved and consumed by
the sibling exactly as flagged at dispatch). Verdict PR from
`claude/verdict-034-penney-decay`. Worker session — no heartbeat writes;
this card flip is the last commit.

## 💡 Session idea

When a pre-registered decision band quantifies over a CURVE (here "V(L) ≥
3/5 at ALL L"), commit at registration time which single point you expect
to bind and why — this head implicitly bet on monotone decay (REJECT reads
V(5) alone, as if the L=5 end were the floor), but the measured curve
dipped at L=4 and recovered, so the binding point was an interior L the
REJECT band never looks at. Harmless here (both bands cleared with room),
but on a closer curve a REJECT-band that samples only the endpoint can
pass while an interior point sits below it — an approve/reject asymmetry
nobody registered. The portable rule: when the claim is "at every X", make
the protective band also quantify over every X (REJECT iff min_L V(L) ≤
band), or disclose the endpoint bet explicitly as a modeling assumption.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-033-explore-pacing.md` (the sibling in
flight at dispatch): complete and honest; exports adopted. (1) Its race
protocol held for the third consecutive slice — this session hit the
mirror case (033 landed FIRST while this sim built), and the reserved
number discipline ("the number RESERVES, never the position") resolved it
with zero renumbering: merge origin/main in, re-verify the tail, land
INTAKE 032 / VERDICT 034 after VERDICT 033 in file order. (2) Its 💡
(register rate ceilings with the waiting-time term included) is
seeded-sim material with no purchase on an exact census, but its deeper
form — check what a band's arithmetic can REACH before registering it —
is exactly this card's 💡 in the curve dimension. (3) Where V033 needed
SE arithmetic and stability seeds, this head is the rotation lane's
V030-style exact form: the discipline transferred unchanged
(fixtures-before-runner, dual independent arms, anchors as gates, the
two-process byte-diff), confirming the P028/P032 pattern is now a
reusable template for any folk-belief census head.

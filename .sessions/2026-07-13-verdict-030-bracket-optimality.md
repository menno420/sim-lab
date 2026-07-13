# Session — VERDICT 030 — single-elimination seeding fairness: is the standard 8-team bracket exactly optimal? (idea-engine PROPOSAL 028)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-030 slice-worker session
> Objective: settle idea-engine PROPOSAL 028 (control/outbox.md · 2026-07-13T06:25:48Z · status: sim-ready; idea `ideas/fleet/tournament-seeding-bracket-optimality-2026-07-13.md` @ idea-engine main 535c232, PR #295 — the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain rotation slot, round 3: sports statistics / tournament-format design). Build the fully hermetic, fully EXACT pre-registered measurement: under the pinned Bradley–Terry model (P(i beats j) = s_i/(s_i+s_j), matches independent, strengths round-constant, no draws) with four committed strength profiles — F1 linear (8..1), F2 geometric (128..1), F3 top-heavy (100,8,7,6,5,4,3,2), F4 near-flat (107..100), plus the F0 flat control (100 ×8, reporting-only closed-form identities) — enumerate ALL 315 distinct 8-team single-elimination brackets (8!/2⁷; canonical census from all 8! leaf orders via recursive min-sort, self-checked to exactly 315 classes × 128 preimages) and measure, per profile as exact rationals, Δ_a = max P(team 1 wins) − standard's and Δ_b = max P(1-vs-2 final) − standard's, where the standard bracket is the class of (1,8,4,5 | 3,6,2,7). TWO structurally independent exact algorithms — Arm A winner-distribution recursion, Arm B 2⁷ = 128 complete outcome-path enumeration — must agree by EXACT RATIONAL EQUALITY on every (bracket, profile, objective) cell. Self-checks (run invalid on any failure): 315×128 partition audit, Σ_i W_root(i) = 1 per cell, the two-team identity p_12 = s1/(s1+s2), the F0 closed forms (1/8 and 1/16-or-0), bracket-relabeling invariance. ZERO RNG/seeds/floats (the P027 seed-registry high-water 20260755 untouched); all arithmetic fractions.Fraction; byte-identical re-run by construction, verified by external diff across two process runs. Decision (registered order): REJECT iff Δ_a = 0 AND Δ_b = 0 exactly in ALL four profiles (checked FIRST); APPROVE iff Δ_a ≥ 1/200 (0.5 pp) in ≥ 1 profile OR Δ_b ≥ 1/100 (1.0 pp) in ≥ 1 profile; NULL = the sub-material straddle (a legitimate finalized outcome). Reporting-only legs (cannot flip): worst-bracket values, objective-argmax disagreement, 315-bracket distribution quartiles. Hermetic: the entire world constructed in-sim from pinned constants; zero repo/network reads at run time.

## What happened

Built `sims/verdict-030-bracket-optimality/` — a stdlib-only NUMERIC
SIMULATION (rung 1) that is fully hermetic AND fully exact, a first for the
unrelated-domain rotation lane: the sim reads exactly one file (its own
committed `fixtures.json` pre-registration, cross-checked at start), all
arithmetic is `fractions.Fraction`, and there is ZERO RNG — no seeds, no
floats, no environment reads; byte-identical re-run holds BY CONSTRUCTION
and was verified anyway by external diff across two full process runs
(sha256 stdout `0aa68250…`, results `1f528be2…`, ~5 s/run). The
pre-registration (all constants verbatim from the idea file; 8 disclosed
intake-time decisions, including the canonical-form naming note: the
standard class (1,8,4,5 | 3,6,2,7) canonicalizes to (1,8,4,5 | 2,7,3,6)
under the registered min-sort) was committed BEFORE the runner.

**Run output:** `SELF-CHECKS: 8530 passed, 0 failed`, exit 0. The census
audit found exactly 315 classes × 128 preimages over all 8! leaf orders;
Arm A (winner-distribution recursion) equaled Arm B (iterative 128-path
enumeration) by exact rational equality on every (bracket, profile) cell
including full winner distributions; the F0 closed forms, two-team
identities, per-cell sum-to-1, path-mass-1, and relabeling invariance all
passed. **Ruling: APPROVE — bracket audit warranted.** REJECT (checked
first) failed categorically: the standard bracket is exactly optimal in NO
profile on NEITHER objective (best rank 12/315). APPROVE was met six times
against a needs-one bar: Δ_a = 6.0122/8.2654/1.5631 pp ≥ 0.5 pp (F1/F2/F3)
and Δ_b = 1.3405/12.2941/10.2293 pp ≥ 1.0 pp (F1/F2/F3); F4 near-flat is
sub-material on both (0.0665/0.0008 pp) — the honest boundary, reported.
Headline structure: ONE challenger, (1,8,6,7 | 2,3,4,5)
(quarantine-the-contenders), is the P(best wins) argmax in ALL FOUR
profiles; the two folk goals disagree — objective (b)'s argmax differs
from (a)'s in every profile.

Landed: INTAKE 028 (2026-07-13T06:49:35Z) + VERDICT 030
(2026-07-13T06:49:36Z) appended to `control/outbox.md` (append-only;
VERDICT 029 = PROPOSAL 027's, in flight on a sibling branch, reserved —
sequence note in the INTAKE block); verdict PR from
`claude/verdict-030-bracket-optimality`. Worker session — no heartbeat
writes; this card flip is the last commit.

## 💡 Session idea

When an exact-census sim names its objects by a canonical form, derive and
PIN the canonical representative of every headline object in the fixtures
BEFORE running — folk presentations and canonical forms diverge silently.
This session's instance: the world's standard bracket is universally
written (1,8,4,5 | 3,6,2,7), but under the registered recursive min-sort
that class's canonical tuple is (1,8,4,5 | 2,7,3,6) (min(2,7) < min(3,6)
reorders the second half). Left unpinned, that mismatch would have made
the standard class LOOK absent from the census (a phantom self-check
failure) or, worse, made a naive string-match pick a WRONG class as
"standard" and silently corrupt every Δ. The portable rule: canonicalize
the pinned presentation IN the sim (never hand-copy the canonical form)
and assert class membership — the naming note costs one fixtures line and
removes an entire silent-corruption class from any census-style sim.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-028-breadth-budget.md`: complete and honest;
its exports are adopted here directly. (1) The born-red choreography and
fixtures-before-runner discipline followed verbatim. (2) Its "every band
decision is an exact integer/Fraction test" export — taken to the limit
this session: the ENTIRE sim is exact Fractions, so the decision arm, both
algorithm arms, and every gate share one arithmetic with zero tolerance
questions (no SE arithmetic needed because no estimator exists — the
degenerate, best case of V027/V028's tolerance-calibration lesson). (3) Its
anchor lesson (two-sample tests for estimated anchors) had no purchase
here BY DESIGN — this sim anchors on nothing estimated; the analogous
discipline was the canonical-form pin above (this card's 💡), which is the
exact-census counterpart of "price your anchor's noise before you gate on
it": know the exact identity of what you compare before you compare it.

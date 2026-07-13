# verdict-034 · Penney's game responder-edge decay

Does "never go first" survive word length? The responder's guaranteed edge
V(L) = min_A max_{B≠A} P(B before A) in Penney's game at L ∈ {3, 4, 5},
plus the folk flip-rule beater σ(A) = ¬a₂·a₁…a_(L−1) scored for exact
optimality on the full census. Answers idea-engine PROPOSAL 032
(control/outbox.md 2026-07-13T08:17:09Z, idea
`ideas/fleet/penney-game-responder-edge-decay-2026-07-13.md`, landed via
idea-engine PR #302, main `2e5d73f`) — the ORDER 003/004 rule-3
COMPLETELY-UNRELATED-domain rotation slot, round 4 (recreational
probability / sequential pattern-race games, after round 1's social choice
P017 → V019, round 2's congestion routing P024 → V026, and round 3's
tournament seeding P028 → V030). Fully hermetic AND fully exact: the
entire world (the word census, both algorithms, band constants, the three
classic anchor rationals) is constructed in-sim from the pinned constants
in `fixtures.json` (the only file read, cross-checked at start); all
arithmetic `fractions.Fraction`; ZERO RNG/seeds/floats (the P031
seed-registry high-water 20260767 untouched); byte-identical re-run by
construction, verified by external diff.

Frame: fair i.i.d. coin, both players commit distinct words of the SAME
length L over {H,T}, first word to appear as a run of consecutive flips
wins (ties impossible for distinct equal-length words). Census: all
ordered pairs (A, B), A ≠ B — 56 / 240 / 992 cells at L = 3/4/5 (1,288
decision cells) plus the 12-cell L=2 anchor leg. Two structurally
independent exact algorithms — Arm A Conway leading numbers (integer
correlations; odds B over A = (L(A,A)−L(A,B)) : (L(B,B)−L(B,A))), Arm B
first-step absorption on the two-word prefix automaton (≤ 2L−1 transient
states, longest-suffix transitions, exact Fraction Gaussian elimination) —
gated on EXACT RATIONAL EQUALITY over every cell. Self-checks (run invalid
on failure): the classic anchors P(TH before HH) = 3/4, P(THH before HHH)
= 7/8, V(3) = 2/3; complement invariance per cell; independently-computed
antisymmetry P(B before A) + P(A before B) = 1; strictly positive Conway
differences; the automaton state audit; σ(A) ≠ A; census-size audits.

Decision (registered order; bands disjoint by construction, 13/25 < 3/5):
REJECT iff V(5) ≤ 13/25 (checked FIRST) → APPROVE iff V(L) ≥ 3/5 at ALL
L ∈ {3, 4, 5} → NULL (the straddle, a finalized outcome pinning the
curve). Folk-rule legs (O(L), S(L), per-word table), f_(2:1)(L), the trap
table, and the L=2 leg are reporting-only and cannot flip the decision.

## Run (one command)

```
python3 sims/verdict-034-penney-decay/penney_decay_sim.py
```

Exit 0 iff all self-checks pass. Deterministic and exact — no seeds, no
floats, no network, no git, no wall clock. Progress goes to stderr only.
~1.5 s.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the decision rule with its evaluation order, and ten
  intake-time decisions (committed BEFORE the runner).
- `penney_decay_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).

# verdict-030 · single-elimination seeding fairness

Is the standard 8-team bracket — (1v8, 4v5 | 3v6, 2v7) — exactly optimal
among ALL 315 distinct bracket assignments for its own two stated folk
goals, (a) P(the best team wins) and (b) P(a 1-vs-2 final)? Answers
idea-engine PROPOSAL 028 (control/outbox.md 2026-07-13T06:25:48Z, idea
`ideas/fleet/tournament-seeding-bracket-optimality-2026-07-13.md`, landed
via idea-engine PR #295, main `535c232`) — the ORDER 004 rule-3
COMPLETELY-UNRELATED-domain rotation slot, round 3 (sports statistics /
tournament-format design, after round 1's social choice P017 → V019 and
round 2's congestion routing P024 → V026). Fully hermetic AND fully exact —
a first for the rotation lane: the entire world (tree topology, the
315-class census, five strength profiles, band constants) is constructed
in-sim from the pinned constants in `fixtures.json` (the only file read,
cross-checked at start); all arithmetic `fractions.Fraction`; ZERO
RNG/seeds/floats (the P027 seed-registry high-water 20260755 untouched);
byte-identical re-run by construction, verified by external diff.

Model: Bradley–Terry, P(i beats j) = s_i/(s_i+s_j), matches independent,
strengths round-constant, no draws. Profiles committed before any code:
F1 linear (8..1), F2 geometric (128..1), F3 top-heavy (100,8,7,6,5,4,3,2),
F4 near-flat (107..100); F0 flat control (100 ×8) reporting-only with
asserted closed forms (P(each wins) = 1/8; P_12 = 1/16 split / 0 same-half).
Census: all 8! leaf orders, recursive min-sort canonicalization, audited to
EXACTLY 315 classes × 128 preimages. Two structurally independent exact
algorithms — Arm A winner-distribution recursion, Arm B iterative 2⁷ = 128
outcome-path enumeration — gated on EXACT RATIONAL EQUALITY over every
(bracket, profile, objective) cell (315 × 5 × 2, full winner distributions
included). Self-checks (run invalid on failure): partition audit, per-cell
sum-to-1, the two-team identity, the F0 closed forms, relabeling invariance.

Decision (registered order): REJECT iff Δ_a = 0 AND Δ_b = 0 exactly in ALL
four decision profiles (checked FIRST) → APPROVE iff Δ_a ≥ 1/200 (0.5 pp)
in ≥ 1 profile OR Δ_b ≥ 1/100 (1.0 pp) in ≥ 1 profile → NULL (the
sub-material straddle, a finalized outcome).

## Run (one command)

```
python3 sims/verdict-030-bracket-optimality/bracket_optimality_sim.py
```

Exit 0 iff all self-checks pass. Deterministic and exact — no seeds, no
floats, no network, no git, no wall clock. Progress goes to stderr only.
~5 s.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the decision rule with its evaluation order, and eight
  intake-time decisions (committed BEFORE the runner).
- `bracket_optimality_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).

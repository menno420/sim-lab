# Session — VERDICT 049 — KU-exclusivity fork: does the plan's blanket "KDP Select: Yes" survive its own royalty arithmetic? (idea-engine PROPOSAL 038, venture rotation round 6)

> **Status:** `in-progress`

Objective: serve idea-engine `control/outbox.md` PROPOSAL 038 (2026-07-13T15:36:37Z, status sim-ready; claim landed idea-engine PR #321 → main 3f1c955, `control/claims/`-ritual reserving INTAKE 038 + VERDICT 049 and branch claude/verdict-049-ku-exclusivity; offset map PROPOSAL 038 → VERDICT 049, +11 per the docs/current-state.md rule — the number RESERVES, never the position; P037 → V048 rides the parallel PR #99, untouched by this session) — "KU-exclusivity fork": price venture-lab's PUBLISHING-PLAN.md §4 OWNER-ACTION default "KDP Select: **Yes**" against the plan's OWN verified constants @ venture-lab 79a1987 via a per-reader-contact buy-vs-borrow mixture. Pinned frame: 2 titles (ultramarine 27,865 words / the-weigh-house 36,434; KENP = round(words/190) → 147 / 192); roy(p) = 7/10·p − 15/100 for $2.99 ≤ p ≤ $9.99 (flat 1 MB delivery fee pinned inside the 15/100) else 35/100·p; β = b/(1+b) with b swept {1/2, 1, 2, 4}; rt swept {7/20, 3/5, 17/20}; KENP rate swept {$0.0035, $0.0045, $0.0055}; p swept {$0.99, $2.99, $4.99, $6.99}, both arms at the SAME p per cell — 288 decision cells, pinned loop order title, b, rt, rate, p. ARM KU(p) = (1−β)·((1−κ)·roy(p) + κ·rate·KENP·rt) + β·rate·KENP·rt with κ = 1/5; ARM WIDE(p) = (1−β)·roy(p) + β·γ·roy(p) with γ = 3/20; Δ = KU − WIDE, W = #{Δ > 0}/288. Arm A exact closed-form Fractions on ALL 288 cells, seedless; Arm S seeded MC (M = 50,000 reader-contacts per (cell, arm), per-borrower read-through Uniform(rt − 3/20, rt + 3/20), seeds 20261289 main / 20261290 stability half-M / 20261291 reporting / 20261292 aux — strictly above the P037-registered high-water 20261288; new registry high-water 20261292). Gates: ≥ 2.5σ familywise agreement tolerances pre-checked in the fixture BEFORE any run; the (κ=0 ∧ γ=0) exact-identity control (Δ = β·rate·KENP·rt, KU wins every cell) and the (rate=0 ∧ κ=0 ∧ γ=0) control (Δ ≡ 0); royalty-band anchor identities as pinned Fractions; monotonicity audits; per-leg draw-count sentinels; twin decision evaluators; two-process byte-identity; CPython minor pinned. Decision rule pre-registered, evaluated IN ORDER: REJECT first (W < 2/5 of 288, stability-reproduced) → APPROVE (W ≥ 4/5 of 288 AND KU wins ≥ 4/5 of the 72 $4.99-tier cells, stability-reproduced) → NULL (anything else — flip axes named via per-axis win shares + the b* crossover map). Fully hermetic (reads only its own fixtures.json; the plan's rows pinned verbatim @ 79a1987 — venture-lab itself walled this session, constants quoted from the proposal block, which is the source of truth over the disclosed-condensation idea doc). Fixtures commit BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, PR #99 / VERDICT 048 files, and idea-engine untouched.

## What happened

(in flight — filled at close-out)

## Session idea

(filled at close-out)

## Previous-session review

(filled at close-out)

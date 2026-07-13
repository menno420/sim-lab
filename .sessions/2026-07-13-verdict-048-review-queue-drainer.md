# Session — VERDICT 048 — review-queue drainer: the N=50 row-trigger threshold priced as a pre-registered policy grid (idea-engine PROPOSAL 037, fleet-backlogs rotation round 6)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-048 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 037 (## PROPOSAL 037 · 2026-07-13T15:09:14Z · status: sim-ready; claim merged idea-engine PR #319; offset map PROPOSAL 037 → INTAKE 037 / VERDICT 048 per docs/current-state.md, +11 from P035 onward) — the fleet-manager review-queue auto-append rule's decide-and-flag N = 50 row-trigger threshold (fm docs/review-queue.md @ 06ce3cc; harvest source fm docs/ideas/review-queue-drainer-2026-07-10.md @ 06ce3cc), priced on the pinned fleet-merge-stream model: three-class size mixture (DOCS-ONLY S = 0 · TWEAK S ~ Geometric(1/12) on {1,2,…} · FEATURE S = 40 + Geometric(1/80)), per-line defect model q(S) = 1 − (399/400)^S (q₁ = 1/400 pinned, {1/800, 1/200} reporting-only), self-flag r = 3/10 pinned ({1/10, 3/5} reporting-only, non-defective false-flag r/3), trigger τ_N: row iff S > N OR flag, N ∈ {0, 10, 25, 50, 100, 200} with N = 0 and N = ∞ exact controls, drain tiers d ∈ {1/5, 2/5, 4/5} × mix profiles {DOCS-HEAVY (5/8, 1/4, 1/8), BASE (1/2, 3/8, 1/8), BUILD-HEAVY (1/4, 1/2, 1/4)} = 9 decision cells, bands REL(N) ≤ 3/10 AND ρ(N) ≤ 4/5, λ = 40/day pinned for absolute-latency legs only. Dual-arm: Arm A exact (closed-form fractions.Fraction via geometric partial sums, all 54 decision points, zero sampling error) AND Arm S seeded event-driven MC (M = 2,000 days per (cell, N); seeds 20261285 main / 20261286 stability half-M / 20261287 reporting / 20261288 aux — strictly above the fleet high-water 20261284). Decision rule pre-registered, evaluated IN ORDER: REJECT first (Feas(cell) = ∅ in ≥ 5/9 cells) → APPROVE (single N† feasible in ≥ 8/9, stability-reproduced) → conditional NULL (a legitimate, expected-plausible landing per the registration). Hermetic, stdlib-only, deterministic, byte-identical reruns proven by external diff; fixtures commit BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, `control/status.md`, and idea-engine untouched.

## What happened

Built `sims/verdict-048-review-row-threshold/` — `fixtures.json` (every
registered constant verbatim from the proposal block: mix grid, size
constants 1/12 · 40 · 1/80, q₁ = 1/400 + pair, r = 3/10 + pair + r/3
false-flag, N grid + both controls, 6-h cadence, d grid + tier semantics,
λ = 40, M = 2,000, seeds 20261285–88, bands 3/10 · 4/5 · 8/9 · 5/9, the
doctrine quotes @ fm 06ce3cc) committed BEFORE the runner. Git trail
(PR #99 commits — squash-merge erases branch SHAs from main, resolve via
the PR): 62ed409 (born-red card) → 76e2110 (fixtures) → 13c0ca6 (runner +
accepted run) → 276f172 (ledger) → this flip.

**Run:** `SELF-CHECKS: 386 passed, 0 failed`, exit 0, ~7 s; stdout +
results.json byte-identical across two full process runs by external diff;
CPython 3.11 pinned, asserted. Arm A (exact closed-form Fractions, 54
decision points, zero sampling error) ≡ Arm S (seeded MC, M = 2,000 days ×
λ = 40/day per (cell, N)) within 5σ familywise tolerances pre-checked
≥ 2.5σ BEFORE any MC run (worst |diff|/tol 0.596); identity controls
(N = 0 ⇒ REL ≡ 0, N = ∞ ⇒ REL ≡ 1 ∧ ESC ≡ 7/10) green in BOTH arms;
monotonicity audits green (0 MC inversions); draw sentinels exact
(15,539,888 / 7,769,822 / 20,580,540; aux seed 20261288 reserved, ZERO
draws — new fleet high-water 20261288); twin evaluators agree on all three
input sets; stability leg reproduces the ruling. Two pre-run correctness
edits while writing the runner (N = ∞ REL identity counted not assigned;
capacity check recorded symmetrically) landed before the first accepted
run — no fix-forwards on measurement.

**Ruling: null (conditional)** — the registration's expected landing,
measured. REJECT (checked FIRST) does not fire: Feas = ∅ in 3/9 cells,
exactly the d = 1/5 column. APPROVE does not fire: per-N feasible counts
2/4/5/6/0/0 — the ceiling is the planted N = 50 at 6/9 < 8/9. The
conditional rule: N = 50 holds REL ≤ 3/10 ∧ ρ ≤ 4/5 in EVERY swept cell
with d ≥ 2/5 (and is the ONLY N common to all mixes at d = 2/5); NO swept
N holds at the d = 1/5 @codex-quota tier in any mix (small N drowns the
drain, ρ(50) = 1.018–1.537; large N breaks the miss band, REL(100) ≥
0.45755). Reporting legs: ESC(50) = 0.19856/0.15477; stable-cell p95 row
age 5.7–28.5 h with ≥ 99.99% drained inside the 72-h revert window;
ceremony-drown crossover 50/100/50 at d=1/5; mid-size miss mass ≈ 0.10–0.11
at N = 50; r is the loaded live axis (r = 1/10 APPROVE-shaped, r = 3/5
NULL-shaped; q₁ pair shape-invariant). Drafting-vs-measured divergence
disclosed: the proposal's approximate ρ(50) bracket vs the literal flag
model (docs false-flag r/3, no carve-out) — the landing untouched.

Landed INTAKE 037 (accepted) + VERDICT 048 (finalized, conditional null)
in `control/outbox.md` (append-only; collision-grepped `## VERDICT 048` +
`## INTAKE 037` at origin/main HEAD 4173377 first — none;
`control/inbox.md` and both status heartbeats untouched; idea-engine
untouched — the claim PR #319 landed before this session). `python3
bootstrap.py check --strict` exit 0 at flip. PR:
https://github.com/menno420/sim-lab/pull/99 (READY; merge-on-green owns
the merge — zero agent merge calls).

## 💡 Session idea

The fleet seed high-water lives only in outbox PROSE: P037 itself had to
order "re-read at the sim-lab ledger @ 3eaeb15 — not trusted from any
brief", and this session re-derived 20261284 → 20261288 by scanning
VERDICT 046/047 entries by hand. Add a machine-readable seed registry —
`harness/seed-registry.json`, one appended record per seeded verdict
({verdict, seeds, new_high_water}) — plus a one-line self-check pattern
(assert min(fixture seeds) > registry high-water) that seeded runners copy,
so "never draw at or below the high-water" becomes a mechanical assertion
instead of a ledger archaeology pass. Anchors: this sim's
`fixtures.json::arm_S.seed_registry` (the prose form to replace),
`review_row_sim.py`'s SEEDS block (where the assert lands), harness/
(the natural home; `simharness.py` has no seed helper today). Dedup: no
seed-registry file or card idea exists in the tree (grepped .sessions/,
docs/, harness/ this session).

## ⟲ Previous-session review

VERDICT 047 (the 37% rule, PR #98) is the direct predecessor. Its
disciplines transferred whole: fixtures-before-runner, REJECT-first
evaluation, byte-identical dual full-process runs, the PR-resolvable git
trail citation (adopted verbatim in this card's trail line), and the card
grammar. One honest criticism: its 💡 idea — the `check --strict`
born-red exit-code split (`2 = only the session gate is red`) — was
exactly what THIS session needed at all four pre-flip pushes, where "is
the session-card line the ONLY strict finding?" was again a prose
judgment; but the idea lives only on the V047 card, routed nowhere (no
outbox line, no order, no claim), so nothing will ever build it. Guard
recipe: a card 💡 that targets kit/tooling machinery should ALSO land as
one manager-addressed line in `control/outbox.md` the same session —
anchor: the card's own 💡 section + the outbox append step every verdict
session already performs; verification target = grep the outbox for the
idea's key token before calling it captured.

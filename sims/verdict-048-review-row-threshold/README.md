# verdict-048-review-row-threshold

> **Status:** `finalized` — VERDICT 048 (INTAKE 037), idea-engine PROPOSAL 037
> ("review-queue row-trigger threshold", fleet-backlogs rotation round 6 —
> the fleet-manager review-queue auto-append rule's decide-and-flag N = 50,
> fm docs/review-queue.md @ 06ce3cc; consumer = fleet-manager, routed by the
> manager per Q-0260).

Dual-arm pre-registered policy-grid sim for the review-queue row-trigger
threshold: under the pinned fleet-merge-stream model (three-class size
mixture DOCS-ONLY S = 0 / TWEAK ~ Geometric(1/12) / FEATURE 40 +
Geometric(1/80); per-line defect model q(S) = 1 − (399/400)^S; self-flag
r = 3/10 with false-flag r/3; trigger τ_N: row iff S > N OR flag), the
threshold N is swept over {0, 10, 25, 50, 100, 200} (+ N = ∞ control)
across 9 decision cells = drain tier d ∈ {1/5, 2/5, 4/5} × mix profile
{DOCS-HEAVY, BASE, BUILD-HEAVY}, against the bands REL(N) ≤ 3/10 AND
ρ(N) ≤ 4/5. Details and the full ruling in [REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-048-review-row-threshold/review_row_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` — one command,
  no flags; exit 0; ~7 s; stdout + `results.json` byte-identical across two
  full process runs by external diff; CPython minor pinned 3.11, asserted)
- **Pre-registration:** `fixtures.json` committed BEFORE the runner (git
  trail) — all constants verbatim from the proposal block: mix-profile grid,
  size constants (1/12, 40, 1/80), q₁ = 1/400 (+ {1/800, 1/200} reporting
  pair), r = 3/10 (+ {1/10, 3/5} pair, r/3 false-flag), N grid + both
  control legs, 6-h batch cadence, d grid with tier semantics, λ = 40,
  M = 2,000 days/(cell, N), seeds 20261285–88, band constants (3/10, 4/5,
  8/9, 5/9), the doctrine quotes pinned verbatim @ fm 06ce3cc
- **Arms:** Arm A exact (closed-form `fractions.Fraction` via geometric
  partial sums — all 54 decision points, zero sampling error) ≡ Arm S
  (seeded event-driven MC, M = 2,000 days × λ = 40/day per (cell, N)) within
  pre-checked 5σ familywise tolerances (≥ 2.5σ asserted BEFORE any run);
  exact-identity controls (N = 0 ⇒ REL ≡ 0; N = ∞ ⇒ REL ≡ 1, ESC ≡ 1 − r)
  and monotonicity audits green in both arms; twin independently-written
  decision evaluators; per-leg draw-count sentinels — 386 self-checks,
  0 failed
- **Seed registry:** seeds 20261285 (main) / 20261286 (stability, half-M) /
  20261287 (reporting) / 20261288 (aux, reserved — ZERO draws) — all
  strictly above the fleet high-water 20261284; new high-water 20261288
- **Results:** `results.json` + `run-stdout.txt` (raw), [REPORT.md](REPORT.md)
- **Ruling:** **null** (conditional — the pre-registered expected landing,
  evaluated in order): REJECT does not fire (Feas = ∅ in 3/9 cells, all of
  the d = 1/5 column); APPROVE does not fire (best N = 50 feasible in only
  6/9 cells < 8/9). The citable conditional rule: **N = 50 holds both bands
  in every swept cell with d ≥ 2/5; NO N in the grid holds at the d = 1/5
  @codex-quota tier in any mix** (small N breaks the drain band, large N
  breaks the miss band — REL(100) ≥ 0.457 everywhere).

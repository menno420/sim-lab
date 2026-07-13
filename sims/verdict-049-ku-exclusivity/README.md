# verdict-049-ku-exclusivity

> **Status:** `finalized` — VERDICT 049 (INTAKE 038), idea-engine PROPOSAL 038
> ("KU-exclusivity fork", venture rotation round 6 — books half; consumer =
> venture-lab's PUBLISHING-PLAN.md §4 "KDP Select: Yes" OWNER-ACTION rows @
> 79a1987, routed via the manager sweep, Q-0260).

Dual-arm sim pricing KDP-Select enrollment (90-day KU exclusivity) against
going wide, per reader-contact, at the SAME list price per cell — the
exclusivity fork isolated from the pricing fork — over the pre-registered
288-cell grid: 2 titles (KENP 147 / 192) × borrow-to-sale b ∈ {1/2, 1, 2, 4}
× read-through rt ∈ {7/20, 3/5, 17/20} × KENP rate ∈ {$0.0035, $0.0045,
$0.0055} × price ∈ {$0.99, $2.99, $4.99, $6.99}. Every constant verbatim from
the PROPOSAL 038 block (the source of truth; the idea doc is a disclosed
condensation). Details and the full ruling in [REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-049-ku-exclusivity/ku_exclusivity_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` — one command,
  no flags; exit 0; ~37 s; stdout + `results.json` byte-identical across two
  full process runs by external diff — no wall-clock in any output;
  cpython-3.11 pinned and asserted)
- **Pre-registration:** `fixtures.json` committed BEFORE the runner (git
  trail, PR #100 commits) — grids, arm formulas, κ = 1/5 / γ = 3/20 with
  their reporting-only sensitivity pairs, royalty-band anchors as pinned
  Fractions, seeds 20261289–92 (new registry high-water 20261292), the
  ≥ 2.5σ familywise tolerance rule (z = 5), and the decision rule
  REJECT → APPROVE → NULL with band constants 2/5 · 4/5 · 4/5-at-$4.99
- **Arms:** Arm A — exact closed-form `fractions.Fraction` on ALL 288 cells,
  seedless; Arm S — seeded MC, M = 50,000 reader-contacts per (cell, arm),
  per-borrower read-through Uniform(rt − 3/20, rt + 3/20) (mean exactly rt);
  per-cell agreement gated at z = 5 familywise (≥ 2.5σ pre-checked)
- **Gates (all green, 31 self-checks 0 failed):** royalty anchors ·
  (κ=0 ∧ γ=0) and (rate=0 ∧ κ=0 ∧ γ=0) exact-identity controls ·
  monotonicity (Δ in rate, Δ in rt, W in γ) · draw-count sentinels ·
  twin decision evaluators · stability leg (seed 20261290, half-M)
  reproduces the ruling · two-process byte-identity
- **Ruling:** **REJECT** — W = 101/288 ≈ 0.351 < 2/5 (exact, zero sampling
  error), $4.99 tier 4/72; stability-reproduced (W_S = 104/288 → reject).
  The blanket "KDP Select: Yes" is struck from the recommendation posture;
  enrollment becomes a per-title decision gated on the committed b*
  crossover table. Enrollment stays an OWNER action on every outcome.

# verdict-047-37-rule

> **Status:** `finalized` — VERDICT 047 (INTAKE 036), idea-engine PROPOSAL 036
> ("the 37% rule off its home objective", unrelated-domain rotation round 5 —
> sequential search / optimal stopping; consumers = future fleet citations of
> the 37% rule).

Exact-measurement sim for the folk "37% look-then-leap rule": under the
secretary problem's own canonical frame (N known, no recall, i.i.d. U[0,1]
values in uniform random order, cutoff family CR(r)), the folk cutoff
r_folk(N) = clamp(⌊(37N+50)/100⌋, 1, N−1) is priced at the objective its
popular applications actually hold — expected hire VALUE, not P(best) — over
N ∈ {5, 10, 20, 50, 100, 200}, the full 379-cell (N, r) census × 2
objectives × 2 conventions. Every number an exact rational; details and the
full ruling in [REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-047-37-rule/secretary_37_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` — one command,
  no flags; exit 0; ~1.4 s; stdout + `results.json` byte-identical across two
  full process runs by external diff, BY CONSTRUCTION: zero RNG, zero seeds,
  zero floats anywhere in computation — display decimals are exact decimal
  strings from integer long division)
- **Pre-registration:** `fixtures.json` committed BEFORE the runner (git
  trail) — all constants verbatim from the proposal/idea file: N grid, the
  r_folk formula, band constants (REJECT 1/50 checked FIRST · APPROVE 1/20 ∧
  3/20 on decision cells N ≥ 50 · NULL), bottom-half := rank ≥ ⌊N/2⌋+1,
  anchors 1/2 · 11/24 · 13/30, the rational e-bracket
  271828182845/10¹¹ < e < 271828182846/10¹¹
- **Arms:** Arm A (analytic closed forms) ≡ Arm B (independent combinatorial
  rank census, C(N−k, j−1)/C(N−1, j−1) family + take-at-N legs) by exact
  rational equality on every cell, gated by a full permutation census at
  N ∈ {5, 6, 7} (120/720/5040 orders) — 151 self-checks, 0 failed
- **Seed registry:** ZERO seeds drawn — fleet high-water 20261284 unchanged
- **Results:** `results.json` + `run-stdout.txt` (raw), [REPORT.md](REPORT.md)
- **Ruling:** **approve** (pre-registered rule, evaluated in order) — REJECT
  does not fire (ΔV(10) = 1/30 > 1/50); APPROVE fires: ΔV = 117/1400 ·
  49/475 · 1037/8400 (≈ 0.084/0.103/0.123) ≥ 1/20 AND B ≈ 0.194/0.187/0.186
  ≥ 3/20 at every decision cell {50, 100, 200}. The 37% rule may no longer be
  cited as "the optimal strategy" for sequential choice UNQUALIFIED — it is
  optimal only for the all-or-nothing best-pick objective; the value-optimal
  cutoff runs ≈ √N − 1 (measured: 1, 2, {3,4}, 6, 9, 13).

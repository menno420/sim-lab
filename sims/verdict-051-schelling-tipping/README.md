# verdict-051-schelling-tipping

> **Status:** `finalized` — VERDICT 051 (INTAKE 040), idea-engine PROPOSAL 040
> ("Schelling segregation tipping at the integration-compatible threshold",
> the standing ORDER 003 COMPLETELY-UNRELATED-domain rotation slot, round 6 —
> emergent spatial self-organization / agent-based relocation dynamics).

Seeded census of the classic two-type Schelling segregation model on the
deliberately CONSERVATIVE pinned frame: 40×40 Moore-8 torus, exactly
720 A / 720 B / 160 vacant (45/45/10), satisfaction = like-fraction among
OCCUPIED neighbors ≥ τ in exact integers (zero occupied neighbors ⇒
satisfied), live random-serial sweeps, unsatisfied agents relocate to a
UNIFORMLY RANDOM vacant cell (not a preference-seeking one), fixation
(zero-relocation sweep, independently re-certified) or cap 500. Decision
cell τ = 3/10; full τ grid {1/8, 1/4, 3/10, 3/8, 1/2, 5/8, 3/4} swept
reporting-only. Every constant verbatim from the PROPOSAL 040 block (the
source of truth). Details and the full ruling in [REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-051-schelling-tipping/schelling_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` — one command,
  no flags; exit 0; ~17 s; stdout + `results.json` byte-identical across two
  full process runs by external diff — no wall-clock in any output;
  cpython-3.11 pinned and asserted)
- **Pre-registration:** `fixtures.json` committed BEFORE the runner (git
  trail, PR #102 commits) — grid/counts, the τ grid as exact rationals, the
  4×4 hand fixture with hand-computed occ/like for all 16 cells, sweep cap
  500, M = 32/16, seeds 20261297–300 (new registry high-water 20261300),
  bands 11/20 · 7/10 with REJECT-first order and the < 1/4-cap-censored
  validity conjunct on BOTH bands
- **Legs:** main seed 20261297 (7 τ cells × M = 32; only τ = 3/10 decides) ·
  stability seed 20261298 (decision cell, M = 16, must reproduce any
  APPROVE) · reporting seed 20261299 (vacancy {1/20, 1/5} + N = 25 cells,
  M = 16 each — cannot flip) · aux 20261300 reserved, never drawn
- **Gates (all green, 32 self-checks 0 failed):** 4×4 hand fixture (engine +
  independent scan) · τ = 0 control (zero relocations, init s inside
  [47/100, 53/100]) · per-sweep conservation 720/720/160 · independent
  fixation re-certification (320/320) · draw-count sentinels · twin
  independently-written decision evaluators · two-process byte-identity
- **Ruling:** **APPROVE** — median s(3/10) = 90871/120960 ≈ 0.7513 ≥ 7/10
  (0/32 cap-censored), stability leg reproduces (21511/28800 ≈ 0.7469 ≥
  7/10, 0/16 cap-censored). Mild preference, strong segregation: an agent
  content at 30% like-neighbors ends with ≈ 75% — the tipping claim
  survives its conservative parameterization. s is a LOCAL mixing metric;
  the family-of-dynamics boundary is stated in the REPORT.

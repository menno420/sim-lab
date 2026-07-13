# Session — VERDICT 017 — generator purchase path: T10 cost-curve sweep (idea-engine PROPOSAL 015)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-12 · verdict-017 slice-worker session
> Objective: settle idea-engine PROPOSAL 015 (control/outbox.md @ 2026-07-12T23:08:19Z, sim-ready; idea ideas/superbot-idle/generator-purchase-path-t10-2026-07-12.md @ 18778ff, landed via idea-engine PR #277) — drive the real `idle_engine/` byte-copied at superbot-idle `c753bc8f5ace96e4632510f43b53f0ee45e2def5` (reference world extended to two generator specs, neutral theme pct, the seven VERDICT 006-graduated parameters held pinned) over the committed 36-cell grid (tier-2 base cost C2 ∈ {300, 600, 900, 1800} seconds-of-tier-1-output × tier-2 base_rate R2 ∈ {5, 10, 25} × per-count cost growth g ∈ {110/100, 115/100, 120/100}) under the SIM-001 S2/S3 policies extended with a committed greedy buy rule, answering: which cells hit the pre-registered T10 band (time-to-second-generator-tier 15–45 min active, target 30) while keeping all ten SIM-001 criteria A1–A10 in PASS state with the purchase path present (baseline leg first: A1–A10 re-scored at the new pin with NO purchase path, isolating the milestone/theme-fold engine drift since the `f11c71a` verdicted pin), measurably lowering VERDICT 006's flagged 3-in-4 early-inert-purchase floor, and reporting `owned` milestone rung arrivals (10/100/1,000) per player profile?

## What happened

Built `sims/verdict-017-t10-cost-curve/` — a stdlib-only NUMERIC SIMULATION
(rung 1, the VERDICT 006 fixture method at the fresh pin): `idle_engine/`
byte-copied COMPLETE (all 11 modules, sha256 manifest re-verified before
import; the byte-identical `__init__.py` is never executed — it pulls
theme→yaml, outside the stdlib floor and the economy surface — the six
economy modules load through a synthetic package anchor). Premise verified
at the pin: NO generator purchase path (`purchase_upgrade`/
`purchase_upgrades` only; live HEAD by `git ls-remote` == `c753bc8`, no
drift). The candidate mechanic is therefore driver-level with
engine-mirrored semantics: cost family `BASE·g^n//den^n`, exact-spend,
lifetime-untouched, run-scoped counts; ONE fixture constant committed at
intake (tier-1 copy anchor = 60 s, the `UPGRADE_BASE_COST_SECONDS`
convention — the proposal's buy rule includes tier-1 copies but its grid
prices only tier-2).

**Run output summary (final head):** `SELF-CHECKS: 201 passed, 0 failed`,
exit 0, stdout+results.json byte-identical across two full process runs
(external diff). Baselines: **B0 reproduces VERDICT 006 EXACTLY**
(self-check-pinned to nine published values) and **B1 (the real HEAD
milestone/theme fold) scores 10/10** — the engine drift is benign (A3
12134 s, −3.5%; the achievements doc's lifetime-2↔first-prestige
double-hit confirmed). **Committed count-stacking shape: 0/36** — A3+A6
break in EVERY cell (S3 first-prestige 8.4–16.2 minutes vs the 2–8 h band;
A6 103–200×) and every T10 undershoots the band floor; diagnostic D1 (no
tier-1 copies) still 0/36 — any count-stacking loop at g ≤ 1.2 runs away.
**Diagnostic D2 (unlock-only — T10's registered wording) passes at exactly
one (C2, R2): (900, 5), T10 = 1948 s ≈ 32.5 min, 10/10 on BOTH scorecard
readings, policy-robust.** **Verdict: conditional** (evidence: simulation,
gate PASS, strength moderate-strong) — the row registers only with the
unlock-only shape; g is NOT registrable from this sweep (inert in the
passing shape, fails everywhere under stacking). Owned-rung and
early-inert findings routed to the lane.

Slice boundary this cycle (the V015/V016 precedent): this session carries
the INTAKE 015 and VERDICT 017 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). No @codex step — suspended per the outbox codex-line
escalation @ dedc12e; a pending codex reply never blocks a verdict. No
claim file — PR #58's session filed none (verified in the idea-engine
claims history); precedent mirrored.

## Run command

```
python3 sims/verdict-017-t10-cost-curve/t10_cost_curve_sim.py
```

## 💡 Session idea

When a proposal sweeps a mechanic that does not exist yet, sweep the
mechanic's SHAPE as committed diagnostic legs, not just its numbers: the
committed 36-cell grid rejected uniformly (A3/A6, margin-free), and no
grid value could have said WHY — the two additive shape legs (no-tier-1,
unlock-only) turned "reject everything" into "the count-stacking loop is
the runaway at any swept price, and the unlock-only shape passes at
exactly one (C2, R2)". A parameter sweep prices a design; a shape sweep
prices the design SPACE the parameters live in — and it is the difference
between handing the lane a dead grid and handing it a registration row
plus the exact fork that kills the alternative.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-016-review-authenticity.md`: complete,
honest, and its two exports are adopted here directly. (1) Its 💡 —
snapshot the union of every fact any candidate could ask, and make an
out-of-snapshot lookup fail the run — is applied as this sim's fixture
discipline: the sha256 manifest of ALL 11 engine modules is verified
before anything imports, the graduated parameters are asserted against
grid.json's pins at run time, and B0's equality to VERDICT 006 is
self-check-enforced rather than eyeballed (the ledger-re-derivation
lesson, applied to a prior verdict's numbers). (2) Its slice boundary
(the verdict session carries the INTAKE + VERDICT appends; status.md
coordinator-only) is honored as-is. One deviation from its layout,
disclosed: where 016's corpus demanded fixture JSONs + a repo-fact
snapshot, this sim's fixtures are the engine byte-copy + grid.json —
same role, different shape of evidence.

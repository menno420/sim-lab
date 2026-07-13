# Session — VERDICT 020 — book breadth vs versioning depth: fixed-budget allocation sweep (idea-engine PROPOSAL 018)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-020 slice-worker session
> Objective: settle idea-engine PROPOSAL 018 (control/outbox.md @ 2026-07-13T01:15:34Z, sim-ready; idea ideas/venture-lab/book-versioning-breadth-depth-allocation-2026-07-13.md @ cb2b6ee, landed via idea-engine PR #283) — under the pinned production-night model (budget B=12, size leg B=6 reporting-only; new title costs 1, extra version costs c ∈ {0.25, 0.5, 0.75}; K ∈ {1,2,3,4,6}, T_eff = B/(1+c·(K−1)) fractional by linearity; θ ~ N(0,1), version quality θ+ε with ε ~ N(0, σ_v²), σ_v ∈ {0.2, 0.5, 1.0}; revenue exp(q+L), L ~ N(−σ_m²/2, σ_m²), σ_m ∈ {0.5, 1.5, 2.5}; Mode P pick-best at fidelity f ∈ {0.2, 0.6, 1.0}; Mode A publish-all at audience separation s ∈ {0, 0.5, 1}), measure K* = argmax_K E[revenue per unit budget] and ΔR = R(K*)/R(1) − 1 per cell (81 cells per mode) in Arm A (analytic, Simpson quadrature, seedless, Mode P f=1 slice) and Arm S (seeded MC, M=20,000, seeds 20260716/20260717, stability leg M=2,000 seed 20260718, Arm A/S agreement ≤ 1.5% on every f=1 cell) — and issue exactly ONE of APPROVE / REJECT / NULL per the pre-registered bands.

## What happened

Built `sims/verdict-020-book-versioning/` — a stdlib-only NUMERIC SIMULATION
(rung 1), fully hermetic (the PROPOSAL 017 precedent): every fixture is a
pinned constant in grid.json copied verbatim from the idea file, zero
repo/network reads in the verdict session. Two pre-registered arms plus an
analytic diagnostic layer (the pinned model's full mean structure is
closed-form via the same order-statistic quadrature — used as self-checks;
arms and ruling unchanged).

**Run output summary:** `SELF-CHECKS: 4144 passed, 0 failed`, exit 0, stdout +
results.json byte-identical across two process runs (external diff), ~2 min,
CPython 3.11 pinned and asserted. Arm A/S agreement gate: max rel dev 0.240%
(tol 1.5%, 135 checks); Arm S reproduces the analytic K* 27/27 on the f=1
slice. **Ruling: NULL** (pre-registered honest straddle, finalized — evidence:
simulation, gate PASS, strength moderate): the two publication modes give
OPPOSITE allocation defaults. Mode P (pick-best): K*=1 in 69/81 = 85.19% of
cells, median ΔR +0.0000 — breadth dominates; versioning pays only at the
aligned corner (c=0.25, σ_v=1.0, f=1.0: K*=3, ΔR ≈ +0.27), never at f=0.2;
σ_m measured inert (E[exp(L)]=1 by construction). Mode A (publish-all): K*≥2
in 72/81 = 88.89%, median ΔR +0.4062, grid-median K* = 6 — versioning
dominates (at s=1, pure ticket arithmetic: ΔR = 6/(1+5c) − 1). APPROVE fails
on Mode P, REJECT fails on Mode A, both margin-free; stability leg (M=2,000,
seed 20260718) reproduces NULL with identical headline shares. Named flip axes
(tie-aware): Mode P {c, σ_v, f} spread 0.3333 each; Mode A {c, σ_m, s} spread
0.2593 each — version cost c the only axis on both frontiers; the publish MODE
itself is the binding fork. Named next step (pre-registered NULL consequence):
the venture lane's two-version live probe measures s in the wild.

Estimator note, disclosed in grid.json + REPORT: the raw exp(q+L) sample mean
has relative SE ~26% at σ_m=2.5 and can never meet the pre-registered 1.5%
gate at the pinned M=20,000, so Arm S uses unbiased conditional-expectation /
control-variate estimators over exactly the pinned draws (Mode P: sign-flip
antithetic + loser-sum CV; Mode A: θ integrated out + β=1 sum-CV) — verified
unbiased against the closed-form layer on all 810 means.

Slice boundary this cycle (deviation from the V018 precedent, disclosed): the
INTAKE 018 + VERDICT 020 control appends do NOT land in this repo's outbox —
the dispatching order routes them to the idea-engine `control/outbox.md` on a
separate control-fast-lane PR (merged Ideas Lab seat, Q-0264; VERDICT 019 /
PROPOSAL 017 in flight from a sibling session under the same order, numbers
fixed). control/status.md stays coordinator-only and is untouched;
control/inbox.md untouched (manager-order file). No @codex step — suspended
per the outbox codex-line escalation @ dedc12e. No claim file — the V017/V018
precedent mirrored.

## Run command

```
python3 sims/verdict-020-book-versioning/book_versioning_sim.py
```

## 💡 Session idea

A pre-registered MC-vs-analytic agreement gate silently pins a VARIANCE
budget, not just a model: PROPOSAL 018 pinned M=20,000 and a 1.5% agreement
tolerance, but the natural raw estimator of the pinned estimand has ~26%
relative SE at the swept σ_m=2.5 corner — the gate is mathematically
unpassable for the raw estimator at the registered M, no matter how correct
the code. The honest resolution is estimator engineering under the
registration: conditional-expectation (Rao-Blackwell) and control-variate
estimators consume exactly the pinned draws in exactly the pinned order, stay
unbiased for the registered estimand, and cut the worst-leg SE ~170× (to
0.15%), making the gate meaningful instead of impossible — with the estimator
formulas committed in grid.json and the closed-form layer self-checking
unbiasedness on all 810 means. Rule of thumb for future pre-registrations:
when registering an agreement gate, either register the estimator alongside
{M, seeds, tolerance}, or state explicitly that estimator choice is free
subject to unbiasedness + pinned draws — otherwise a spec can be
simultaneously well-posed and unsatisfiable, and a naive implementation
reports "run invalid" against perfectly correct code.

## ⟲ Previous-session review

Prior card `2026-07-13-current-state-refresh.md`: complete, honest, surgical —
its numbers were re-used directly this session (the verdict-numbering offset
map and the intake-ledger location note grounded this verdict's numbering:
PROPOSAL 018 → VERDICT 020, INTAKE 018, constant +2 offset from P010 onward).
(1) Its slice-boundary rule (touch only your own surfaces; status.md
coordinator-only, inbox.md manager-only) is honored — this session touches
sims/ + its own card in this repo, control appends ride the dispatched
idea-engine fast-lane PR (deviation from V018's same-repo-append precedent,
disclosed above with its provenance). (2) Its 💡 (count parity vs the
append-only ledger catches OMISSIONS that contradiction linting and
cross-validation both miss) is directly relevant to the split-ledger state
this cycle creates — INTAKE/VERDICT entries now span two repos' outboxes; the
count-parity checker it sketches should count BOTH ledgers against the
idea-engine proposal count, and the coordinator's next docs slice should pin
that. (3) Its follow-up flags (Review-rhythm §codex staleness, OA-005
mismatch) remain open — not this slice's surface, carried forward untouched.

# verdict-096 · combo-grace-budget-cliff

The exact steady-lateness census of a forgiving-streak combo grace contract
funded by ONE shared budget. Answers idea-engine PROPOSAL 083
(`## PROPOSAL 083 · 2026-07-16T14:28:18Z · status: sim-ready`, idea
`ideas/superbot-games/combo-grace-budget-cliff-2026-07-16.md` — the round-17
GAME-MECHANICS rotation slot): the forgiving-streak sentence ("any action
within the grace window is safe; you only ever lose the streak on a REAL miss,
ℓ > G") is priced on its own most natural implementation — one shared grace
budget behind a per-action grace test, structurally the lane's shipped
`games/mining/core/energy.py` shared-budget pace surface. The sentence is TRUE
on its own two cells (ℓ=0 replenishes to the cap and survives forever; ℓ>G is
an immediate real miss at step 1) and INVERTED on the shared budget it never
names: every steady within-grace lateness breaks the streak at a finite,
history-determined step `break_step = ⌊B0/ℓ⌋+1` (ℓ=1→11, ℓ=2→6, ℓ=3→4), and
the break is SILENT under the strict miss-contract because no single action
exceeded G. The forgiveness inversion is the sharpest: the silently wiped
multiplier `= break_step−1 = ⌊B0/ℓ⌋ = {10,5,3}` is strictly DECREASING in ℓ —
the player who leans LIGHTEST on grace each action (ℓ=1) rides the longest
streak and loses the MOST (10 of M=25). Two repairs priced in-model: (a) a
grace-low warning firing once per streak at break_step−1 with ZERO false
positives on the ℓ=0 cohort; (b) replenish-on-within-grace at R'=1 → ℓ=1
survives (net 0), ℓ=2 moves to step 10, ℓ=3 to step 5.

## Run (one command)

```
python3 sims/verdict-096-combo-grace-budget-cliff/combo_grace_budget_cliff_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: stdout and `results.json` are
byte-identical across process runs (no wall clock, no paths, no network, no git
at run time). Stdlib only — this is a deterministic-automaton exact-census head
(nearest method kin: P081/V094's deterministic-orbit replay against a comfort
comment with the true-sentence-survives move, and P082/V095's shipped-
mechanism-vs-sold-sentence disposition-TRUE / everywhere-INVERTED structure
with a priced repair fork). The model pins a budget automaton (break-before-
update, replenish-only-on-clean ℓ≤0, checked-first miss ℓ>G, the strict `< 0`
budget boundary) from the idea file's integer constants and re-derives every
census cell from scratch; the model-semantics NULL axis prices the `< 0`
boundary and the update order exactly. CPython 3.11 pinned and asserted (the
decision arms are seedless integer arithmetic, platform-independent; only
reporting-only Arm R and the presentation shuffle touch the pinned minor's
`random` module).

## Layout

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 083
  block / idea file, committed BEFORE the runner: the pinned model
  (P=10, G=3, B0=Bmax=10, R=1, M=25, R'=1 for repair b), the transition with
  its break-before-update order and `< 0` boundary, the F3 census anchors (the
  steady break-step map {∞,11,6,4,1}, the loss map {10,5,3}, the repair-(a)
  warning map {10,5,3,0}, the repair-(b) break map {∞,10,5}), the closed-form
  contacts C1/C2, the F4 pencil worlds, the Arm-R draw-order grammar with seeds
  20261726–729 and both registered preview censuses + class-stream digests, and
  the pre-registered decision rule. Sim-chosen realizations (the decision-arm
  horizon, the class-stream digest procedure, salt logging, the presentation
  target) are disclosed as vacancy-derived fixtures, never match claims.
- `combo_grace_budget_cliff_sim.py` — the single runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

## Arms

- **Arm A** — the pinned stepwise budget automaton (break-before-update,
  replenish-only-on-clean, checked-first miss). Seedless, DECISION-bearing:
  every decision number is an exact integer census over the registered finite
  grid.
- **Arm B** — an INDEPENDENTLY-shaped twin: a full-trajectory budget WALK over
  an explicit per-step trajectory with no early-return closed form. Tied to
  Arm A through the typed must-equal contacts: **C1** steady sim
  `break_step == ⌊B0/ℓ⌋+1` for ℓ ∈ {1,2,3}; **C2** repair-(b) sim
  `break_step == ⌊(B0−ℓ)/(ℓ−1)⌋+2` for ℓ ∈ {2,3}, ℓ=1 surviving; the
  twin-machine contact (Arm B == Arm A on all five steady patterns and every
  Arm-R trace); and two independently-written decision evaluators agreeing on
  the ruling token over an ENUMERATED 64-row boolean input set.
- **Arm R** — seeded random cells, REPORTING-ONLY (no statistical gate): per
  trace EXACTLY 3 `rng.randint` draws in registered order (lateness ℓ ∈ [0,4],
  horizon cap ∈ [5,50], salt ∈ [1,1000] drawn-and-logged), one `random.Random`
  per seed; classes {SURVIVE, SILENT-BREAK, REAL-MISS} total on all N traces.
  Seeds 20261726 (N = 20,000, digest `3bfa073726f7`) and 20261727 (N = 8,000,
  digest `6f857d0afcf4`); presentation shuffle 20261728 (presentation leg
  only); aux 20261729 reserved and never read.

Decision rule (registered order, evaluated by two independently-written
evaluators over an ENUMERATED boolean input set): REJECT → INVALID → APPROVE →
NULL, REJECT evaluated FIRST. Full grammar in `fixtures.json`.

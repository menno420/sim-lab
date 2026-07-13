# VERDICT 048 — review-queue row-trigger threshold: the decide-and-flag N = 50 priced as a pre-registered policy grid

> **Ruling:** `null` (conditional — a legitimate, pre-registered outcome and
> the registration's own expected landing) — per the pre-registered rules
> applied IN ORDER: REJECT (checked FIRST) does not fire — Feas(cell) = ∅ in
> 3 of 9 cells (< 5/9), exactly the d = 1/5 column; APPROVE does not fire —
> no single N is feasible in ≥ 8/9 cells (the best, the planted N = 50,
> holds in 6/9). The conditional rule ships: **N = 50 holds both bands in
> every swept cell with drain tier d ≥ 2/5; NO swept N holds at the d = 1/5
> @codex-quota tier in any mix.**
>
> Intake: **037** (idea-engine PROPOSAL 037 · 2026-07-13T15:09:14Z · status:
> sim-ready; claim idea-engine PR #319) · Hermetic dual-arm: Arm A exact
> `fractions.Fraction` (54 decision points, zero sampling error) + Arm S
> seeded MC (seeds 20261285–88, strictly above the fleet high-water
> 20261284) · 386 self-checks, 0 failed · stdout + results.json
> byte-identical across two full process runs by external diff · ~7 s,
> stdlib-only, CPython 3.11 pinned.

## The question (registered)

The fleet-manager review-queue auto-append rule (fm `docs/review-queue.md`
@ 06ce3cc) rows every PR adding "more than 50 changed lines of
runtime/product code" (excluded paths out) OR carrying any self-flagged
risk — with N = 50 seeded decide-and-flag on zero data ("the owner may
re-tune"). The doctrine names both failure directions itself ("A lower N
drowns the queue in ceremony rows nobody drains; a higher N lets exactly
the mid-size logic changes through that the night-review caught defects
in") and the stakes were realized once ("116 merged PRs / zero rows was the
state that voided it"). Under the pinned merge-stream model, this head
measures, per (cell, N):

- **REL(N)** = P(S ≤ N | defect) — the size-arm miss share (the fraction of
  veto-worthy merges the threshold arm fails to row, which the flag arm
  must then carry); ESC(N) = (1 − r)·REL(N) ships reporting-only;
- **ρ(N)** = P(row)/d — drain utilization, the doctrine's own
  "drowns the queue" axis;

over N ∈ {0, 10, 25, 50, 100, 200} (N = 0 and N = ∞ exact controls), 9
decision cells = d ∈ {1/5, 2/5, 4/5} (the @codex-quota tier / the two-tier
doctrine / the dedicated-reviewer-lane arm — the harvest item's own fork
made a decision axis) × mix (w₀, w_c, w_f) ∈ {DOCS-HEAVY (5/8, 1/4, 1/8),
BASE (1/2, 3/8, 1/8), BUILD-HEAVY (1/4, 1/2, 1/4)}.

**Decision rule (fixtures.json, committed BEFORE the runner; evaluated in
this order):** with Feas(cell) = {N in grid : REL(N) ≤ 3/10 AND ρ(N) ≤ 4/5}
— REJECT iff Feas(cell) = ∅ in ≥ 5/9 cells (checked FIRST) → APPROVE iff a
single N† is feasible in ≥ 8/9 cells, stability-reproduced → NULL (anything
else; the conditional per-tier/per-mix rule + named live probes ship).

## Validity

**Arm A** (decision-binding): every number a closed-form exact Fraction via
geometric partial sums — P(S > N) from the class tails, P(defect) and
P(defect ∧ S ≤ N) from E[(399/400)^S·1{S ≤ N}] = K(1 − b^N) partial sums —
zero sampling error on all 54 decision points. **Arm S** (seeded
event-driven MC of the stream + 6-h batch-drain queue): M = 2,000 days ×
λ = 40 PRs/day per (cell, N), pinned loop order (cells lexicographic d then
mix, N ascending, days sequential); seeds 20261285 main / 20261286
stability (half-M, must reproduce the ruling) / 20261287 reporting /
20261288 aux (reserved — zero draws, disclosed), all strictly above the
fleet high-water 20261284.

All gates green (any failure = run INVALID): agreement |REL_S − REL_A| and
|ρ_S − ρ_A| within 5σ familywise tolerances on every (cell, N-leg), the
multiplier pre-checked ≥ 2.5σ BEFORE any MC run (worst observed |diff|/tol
= 0.596); exact-identity controls N = 0 ⇒ REL ≡ 0 and N = ∞ ⇒ REL ≡ 1 ∧
ESC ≡ 1 − r, both arms, every cell; monotonicity audits (REL_A
nondecreasing, P_row_A nonincreasing) exact per cell — the MC arm showed 0
adjacent-pair inversions (reporting-only diagnostic; fresh draws per
(cell, N) make noise inversions expected by construction); per-leg
draw-count sentinels (main 15,539,888 / stability 7,769,822 / reporting
20,580,540 draws, each equal to its closed-form count); twin
independently-written decision evaluators agree on every input set (Arm A
exact, Arm S main, Arm S stability); the stability leg reproduces the
ruling. **386 self-checks, 0 failed, exit 0.** stdout + results.json
byte-identical across two separate full process runs (external diff);
CPython minor pinned 3.11 (asserted).

## The measured tables (Arm A exact; decimals truncated; full rationals in results.json)

REL(N) per mix (mix-only — d-free; DOCS-HEAVY ≡ BUILD-HEAVY exactly,
because both carry the same 2:1 w_c:w_f ratio — a structural identity):

| N | BASE | BUILD-HEAVY | DOCS-HEAVY | band 3/10 |
|---:|---:|---:|---:|:---|
| 0 | 0 | 0 | 0 | pass (control: exact 0) |
| 10 | 0.06209 | 0.04536 | 0.04536 | pass |
| 25 | 0.17240 | 0.12594 | 0.12594 | pass |
| 50 | 0.28366 | 0.22110 | 0.22110 | pass |
| 100 | 0.50485 | 0.45755 | 0.45755 | **fail everywhere** |
| 200 | 0.80188 | 0.78290 | 0.78290 | fail |
| ∞ | 1 | 1 | 1 | control: exact 1, ESC = 7/10 |

ρ(N) = P(row)/d and per-cell feasibility (Y = REL ≤ 3/10 AND ρ ≤ 4/5):

| cell | N=0 | N=10 | N=25 | N=50 | N=100 | N=200 |
|:--|--:|--:|--:|--:|--:|--:|
| d=1/5 BASE | 2.750 n | 1.771 n | 1.261 n | 1.029 n | 0.785 n | 0.608 n |
| d=1/5 BUILD-HEAVY | 3.875 n | 2.570 n | 1.890 n | 1.537 n | 1.064 n | 0.709 n |
| d=1/5 DOCS-HEAVY | 2.187 n | 1.535 n | 1.195 n | 1.018 n | 0.782 n | 0.604 n |
| d=2/5 BASE | 1.375 n | 0.885 n | 0.630 **Y** | 0.514 **Y** | 0.392 n | 0.304 n |
| d=2/5 BUILD-HEAVY | 1.937 n | 1.285 n | 0.945 n | 0.768 **Y** | 0.532 n | 0.354 n |
| d=2/5 DOCS-HEAVY | 1.093 n | 0.767 **Y** | 0.597 **Y** | 0.509 **Y** | 0.391 n | 0.302 n |
| d=4/5 BASE | 0.687 **Y** | 0.442 **Y** | 0.315 **Y** | 0.257 **Y** | 0.196 n | 0.152 n |
| d=4/5 BUILD-HEAVY | 0.968 n | 0.642 **Y** | 0.472 **Y** | 0.384 **Y** | 0.266 n | 0.177 n |
| d=4/5 DOCS-HEAVY | 0.546 **Y** | 0.383 **Y** | 0.298 **Y** | 0.254 **Y** | 0.195 n | 0.151 n |

(every "n" at N ∈ {100, 200} is the REL band failing; every "n" at N ≤ 50
is the ρ band failing — the two masters pull in opposite directions,
exactly the doctrine's own qualitative claim, now priced.)

**Ruling application (exact comparisons, registered order):**

1. REJECT — Feas = ∅ in ≥ 5/9 cells? Empty cells: **3 of 9** (d=1/5 BASE,
   d=1/5 BUILD-HEAVY, d=1/5 DOCS-HEAVY) → **does not fire**.
2. APPROVE — a single N† feasible in ≥ 8/9? Per-N feasible-cell counts:
   N=0: 2 · N=10: 4 · N=25: 5 · **N=50: 6** · N=100: 0 · N=200: 0 →
   **does not fire**.
3. **NULL — fires (conditional).** Stability leg (seed 20261286, half-M)
   and the main MC leg both reproduce NULL through the twin evaluators.

**RULING: NULL (conditional).** The citable per-tier/per-mix rule:

- **d = 1/5 (@codex-quota tier): NO swept N holds in any mix.** Small N
  breaks the drain band (ρ(50) = 1.018–1.537 > 1: the queue does not even
  stabilize); large N breaks the miss band (REL(100) ≥ 0.45755 everywhere).
  Per-axis share 0/3, median minimal feasible N: none.
- **d = 2/5 (two-tier doctrine): N = 50 is the ONLY N feasible in all three
  mixes** (BUILD-HEAVY admits nothing else). Share 3/3, median minimal
  feasible N = 25.
- **d = 4/5 (dedicated-reviewer-lane arm): {10, 25, 50} all hold in all
  mixes.** Share 3/3, median minimal feasible N = 0.
- Per-mix shares: 2/3 each (every mix fails exactly at d = 1/5); the
  binding axis is the DRAIN TIER, not the mix — though BUILD-HEAVY is
  always the tightest cell in its tier (its d=2/5 Feas is the singleton
  {50}).

## Reporting-only legs (cannot flip the decision; did not)

- **ESC(N) = (1 − r)·REL(N)** (BASE): 0.04346 (N=10) · 0.12068 (25) ·
  0.19856 (50) · 0.35339 (100) · 0.56132 (200); 2:1 mixes: 0.15477 at the
  planted N = 50.
- **Latency (seed 20261287, the only λ-pinned legs):** in stable cells the
  6-h batch drain is comfortable — p95 row age 5.7–28.5 h, share drained
  within 72 h ≥ 0.9999 at every stable (cell, N ≥ 10); the 72-h
  revert-feasibility window is not the binding constraint anywhere the
  queue is stable. In ρ > 1 cells the backlog grows linearly and never
  recovers (e.g. d=1/5 BUILD-HEAVY N=50: +4.40 rows/day, 8,796 rows after
  2,000 days) — "drowns the queue" made a number.
- **Ceremony-drown crossover (largest N with ρ > 1):** d=1/5: 50 / 100 / 50
  (BASE / BUILD / DOCS) — at the quota tier even the PLANTED threshold sits
  past the drown line; d=2/5: 0 / 10 / 0; d=4/5: none.
- **Mid-size miss mass (defect mass in 25 < S ≤ N):** at N = 50: 0.11125
  (BASE), 0.09516 (2:1 mixes) — the doctrine's "exactly the mid-size logic
  changes" claim priced: moving 25 → 50 concedes ~10–11 % of defect mass to
  the flag arm.
- **Sensitivities (exact Arm A recomputation):** q₁ ∈ {1/800, 1/200} leaves
  the rule-shape unchanged (3/9 empty, NULL-shaped — the q₁ sweep brackets
  scale, not shape, as registered). r = 1/10 relaxes ρ enough that N = 50
  reaches 8/9 cells (APPROVE-shaped); r = 3/5 tightens to 4/9 empty (still
  NULL-shaped) — the flag-compliance rate r is therefore the single most
  decision-loaded live unknown, named for the probes below.
- MC monotonicity inversions: 0.

## Liveness disclosure vs measurement

The proposal's own drafting arithmetic predicted REL(50) ≈ 0.28 at BASE
(measured exactly: 0.28366 — match) and "ρ(50) ≈ 0.73–0.98 straddling 4/5
across the r sweep" at BASE d = 1/5; measured: ρ(50) = 1.029 pinned /
0.727 (r=1/10) / 1.483 (r=3/5) — the drafting bracket reads as approximate
against the literal registered flag model (DOCS-ONLY PRs are non-defective
by construction and therefore false-flag at r/3; the registration states no
docs carve-out, implemented literally, disclosed in fixtures). The
divergence does not touch the landing: the registration's expected landing
(a CONDITIONAL rule) is the landing, and the fixture's own pre-run hand
derivation predicted the full Feas table cell-for-cell (measured: exact
match, including the 3-empty d=1/5 column and the 6/9 ceiling at N = 50).
The measurement wins on any divergence, disclosed.

## Model basis, boundaries (registered scope)

Every number is CONDITIONAL on the pinned model. **Defect model:** per-line
independence with invented q₁ = 1/400 is the disclosed weakest joint — NO
fleet datapoint on defect rates exists (defects are observable only through
drained-row outcomes and live fire); the q₁ sweep brackets scale, not
shape, and the live probes never measure q₁. **Miss ≠ harm:** REL prices
the loss of the doctrine's own safety valve — the thing the
no-pre-merge-review policy rests on — not total harm; judges and live fire
catch some misses, out of scope by design. **Drain capacity:** d is
quota-bracketed, not measured — quota refusals are retry-later per the
doctrine — and the tier semantics are the harvest item's own fork, not a
claim about @codex throughput. **Cooperative lanes:** PR-splitting to duck
the threshold is out of scope — the fleet's lanes are honest machinery,
the V027 registration inherited. Reporting-only legs cannot flip the
decision and did not.

## What a reader does differently (pre-registered NULL consequence)

The conditional rule ships: **keep N = 50 wherever the two-tier drain
(d ≥ 2/5) actually operates — it is then the single N that holds both
bands in every swept mix, and the planted value needs no re-pin; but the
@codex-quota tier alone (d = 1/5) cannot hold ANY swept N once the stream
is real** — the threshold question is downstream of the drain question.
Before any doctrine re-pin, the cheapest LIVE probes (zero new tooling,
pre-registered) locate the fleet's actual cell:

1. one `git log --numstat` pass over each enabled repo's merged PRs (the
   real λ, w-mix, and size tails — the axes this sim can only bracket);
2. a ⚑-flag census over committed session cards (the real r — measured
   here as the single most decision-loaded unknown: r = 1/10 turns the
   grid APPROVE-shaped, r = 3/5 keeps it NULL-shaped);
3. a rows-drained count against `review-queue.md` history (the real d).

**Run:** `python3 sims/verdict-048-review-row-threshold/review_row_sim.py`
— stdlib-only, hermetic, no flags. Raw outputs: `run-stdout.txt`,
`results.json` (exact fractions as "num/den" strings + display decimals +
the MC estimates and latency/backlog tables).

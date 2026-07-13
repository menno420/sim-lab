# REPORT — Claim-expiry horizons vs lane death (PROPOSAL 025)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 025** ·
> 2026-07-13T04:49:44Z · status: sim-ready (idea
> `ideas/substrate-kit/claim-expiry-horizon-lane-death-2026-07-13.md`, landed
> via idea-engine PR #291, main `a123fda`). The ORDER 004 rule-3
> FLEET-BACKLOGS rotation slot, round 3 — the kit-planted claims doctrine
> (round 1 websites P019 → V021; round 2 superbot P021 → V023). Fully
> hermetic: every fixture is a pinned constant committed with the sim; zero
> repo/network reads in the verdict session.
> Run: `python3 sims/verdict-027-claim-expiry/claim_expiry_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — exact closed forms on all 54
decision points plus a seeded event-driven MC validation arm, band-scored
against the pre-registration): the twin-work risk T and the deadlock cost O95
of silence-inferred claim abandonment, per (gap-regime × check-tempo) cell
and horizon θ. Arm A is seedless closed-form — memorylessness of the
exponential mixture components and of Poisson checks makes BOTH decision
metrics exact, so the decision surface carries zero sampling error; Arm S
re-derives the same numbers by event-driven simulation to validate the model
mechanics and adds the reporting-only rich mechanics (takeover chains, wasted
sessions, multi-steal). This label fills the outbox `evidence: simulation`.
The one judgment question — whether 0.05 / 120 h are the right materiality
lines — was pinned by pre-registration in the idea file; the full curves ship
in `results.json`, so a re-drawn line re-reads, never re-runs.

## PREMISE (verified at drafting, pinned into the fixtures — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`
pre-registration, cross-checked at start) and touches no repo state, no
network, no wall clock. The defendants are quoted in the fixtures: substrate-kit
HEAD `917261b3` ships `CLAIM_STALE_HOURS = 24` (`check_claims.py:95`) and
`WORK_CLAIM_STALE_HOURS = 72` (`:102`) with its own comment "Seeded at 72h;
revisable by data like every horizon constant" — no data existed. Both grid
constants sit in the θ grid by design. Nine intake-time decisions are
disclosed in `fixtures.json` (death-position convention with its
decision-independence proof; exact draw layout; empirical-p95 convention;
dead-claim takeover convention matching the closed form by memorylessness;
exposure-window convention; reporting/aux leg sizes; predicted-SE columns;
the pre-commit scratchpad probe disclosure), plus the
**gate-calibration disclosure written BEFORE any run** (see What it settled,
item 4).

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Lane:** claims at t = 0 (a visible-activity event), works through M
  further events separated by i.i.d. gaps from a two-component exponential
  mixture; completes at the final event. Regimes (rows): **R1 burst**
  w=(0.9, 0.1), m=(1.5, 12) h, M=6 · **R2 daily** (0.7, 0.3), (6, 24), M=4 ·
  **R3 weekend** (0.6, 0.4), (12, 48), M=3 (P(G > 72 h) ≈ 0.089 — alive
  silences really exceed the planted work horizon). **Death:** with
  p_d = 0.10 the lane dies silent forever after a uniformly chosen
  intermediate event (p_d deliberately NOT a decision axis — see boundary).
- **Observer:** contenders check at Poisson rate λ_c ∈ {1/4, 1/12, 1/48} h⁻¹
  (columns C4/C12/C48); a check finding silence > θ takes the claim over
  ("prune on sight", first-check-wins). Horizons θ ∈ {6, 12, 24, 48, 72,
  168} h — both kit constants in-grid.
- **Metrics per (cell, θ):** **T** = P(an alive-throughout claim is stolen at
  least once before completion) — the twin-work risk; **O95** = p95 of
  (takeover − death) for dead claims — the deadlock cost.
- **Arm A (decision-carrying, exact):** q_i(θ) = e^(−θ/m_i) ·
  λ_c·m_i/(1+λ_c·m_i) per mixture component (memorylessness);
  T_A = 1 − (1 − Σ_i w_i·q_i(θ))^M; O95_A = θ + ln(20)/λ_c. All 54 points,
  no PRNG, no sampling error.
- **Arm S (validation + rich mechanics):** event-driven MC, M_S = 4,000
  claims per (cell, θ), `random.Random(20260744)`, pinned loop order (cells
  lexicographic R then C, θ ascending, replications sequential; per claim:
  death coin, death position, gaps in order, checks by inter-arrival draws).
  Registered gates: |T_S − T_A| ≤ 1.0 pp and |O95_S − O95_A| ≤ max(4 h, 5%)
  per point. Stability leg seed 20260745 (M_S = 1,000) must reproduce the
  ruling. Reporting-only legs seed 20260746 (p_d ∈ {0.02, 0.30}; takeover
  chains; wasted-sessions; multi-steal). Aux stream seed 20260747 (p_d = 0
  and θ→∞ exact-identity legs; 16× gate diagnostics). Seeds 20260744–47 sit
  strictly above the P024 registry high-water 20260743.
- **Decision rule (registered before any code; evaluated in this order):**
  Feas(cell) = {θ : T ≤ 0.05 AND O95 ≤ 120 h}; θ*(cell) = min Feas(cell).
  APPROVE iff a single θ† is feasible in ≥ 8/9 cells (Arm A exact values,
  Arm S gates passed, stability reproducing); REJECT iff Feas = ∅ in ≥ 5/9
  cells; NULL otherwise (flip axis named via per-axis shares and median θ*).

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**(1) Arm A — the exact feasibility atlas (the decision).** Feas(cell) = ∅ in
**6 of 9 cells** — the REJECT condition (≥ 5/9), met with a cell to spare:

| cell | Feas | θ* | why infeasible |
|---|---|---|---|
| R1-C4 | {48, 72} | 48 | — |
| R1-C12 | {24, 48, 72} | 24 | — |
| R1-C48 | ∅ | — | O95 structural (θ + 143.795 > 120 ∀θ) |
| R2-C4 | ∅ | — | T > 0.05 ∀θ ≤ 72 (θ=72: 0.050244, knife-edge); θ=168 busts O95 (179.98) |
| R2-C12 | {72} | 72 | — |
| R2-C48 | ∅ | — | O95 structural |
| R3-C4 | ∅ | — | T ≤ 0.05 only at θ=168 (0.0331), which busts O95 (179.98) |
| R3-C12 | ∅ | — | T ≤ 0.05 only at θ=168 (0.0287), which busts O95 (203.95) |
| R3-C48 | ∅ | — | O95 structural AND T > 0.05 through θ=72 |

Coverage per θ (cells where feasible): 6 h → 0, 12 h → 0, 24 h → 1, 48 h → 2,
**72 h → 3 (the maximum)**, 168 h → 0. APPROVE needed one θ covering ≥ 8/9 —
**no θ† exists**; the grid's best single horizon covers exactly one third of
the fleet's spanned cells. Per-axis shares: R1 2/3, R2 1/3, R3 **0/3**
(median θ* 36 / 72 / —); C4 1/3, C12 2/3, C48 **0/3** (median θ* 48 / 48 / —)
— both pre-named candidate axes (the R3 weekend tail; the C48 sparse-check
column) are fully binding, and R2-C4 falls too.

**(2) The planted constants, read against the atlas (registered
obligations).** `WORK_CLAIM_STALE_HOURS = 72` is the best-covering single
horizon in the grid — and covers only **3/9 cells** (safe for burst/daily
lanes checked at least ~12-hourly; unsafe as a fleet-wide default). The 24 h
order-class constant, read against the burst columns per the registered
reading-not-sweep boundary: at C12 standard tempo it holds (R1-C12:
T = 0.0399, O95 = 59.9); at C4 burst tempo it **misses the twin band**
(R1-C4 @ 24 h: T = 0.0594 > 0.05) — tonight's observed sub-hour claim tempo
brackets C4, so the doctrine's "~24h may be treated as abandoned" prose is
mildly twin-unsafe exactly where the fleet currently operates.

**(3) Arm S agrees everywhere it matters.** The MC decision applied to its
own measured values = REJECT with the SAME six infeasible cells. The
stability leg (seed 20260745, n = 1,000) = **REJECT reproduced** at 5/9 — the
knife-edge R2-C4 cell (T_A = 0.050244 vs the 0.05 band, a 0.024 pp miss)
flips feasible under small-n noise and the ruling STILL lands REJECT: the
6-vs-5 margin absorbs the only knife-edge cell, so the ruling is count-robust
against every edge case in the grid. Exact-identity legs: the p_d = 0 leg
produced **zero orphan events** and the θ→∞ leg produced **T = 0 exactly**;
all per-leg draw-count sentinels rejoined their streams exactly.

**(4) The registered per-point gates — breached as PREDICTED BEFORE THE RUN,
and shown to be pure sampling noise.** Closed-form SE arithmetic, pinned into
`fixtures.json` (`gate_calibration_disclosure`) before any draw ran, showed
the proposal's gates are miscalibrated at its own M_S = 4,000: the O95
tolerance at C48 (max(4 h, 5%) = 7.5–15.6 h) sits at **0.7–1.5σ** of the
empirical-p95 estimator over ~400 dead claims (SE ≈ 0.218/λ_c ≈ 10.5 h), and
the 1.0 pp T tolerance sits at **1.2–1.6σ** of the binomial SE (up to
0.83 pp) on ~30 mid-range points — P(all C48 O95 points pass) ≈ 3·10⁻⁴ by
construction. Measured: **8/54 T-points and 6/54 O95-points breached (11
distinct points; max z_T = 2.69σ, max z_O95 = 2.14σ — no deviation anywhere
beyond ordinary sampling range)**. Every failing point was re-measured at 16×
(M_diag = 64,000) on the aux stream: **all 11 land within the same registered
tolerances** (max residuals 0.43 pp and 4.60 h) — the MC and the closed forms
agree; what failed is the registration's tolerance-vs-sample-size arithmetic,
not the model. Handling, pinned before the run: the proposal's own APPROVE
clause alone conditions on "Arm S gates passed", so the breach bars APPROVE
(already unreachable) and cannot create or destroy the REJECT, which is
evaluated on the exact arm. The conflict between the proposal's global "run
invalid on failure" phrase and its own done-when ("the verdict issues exactly
ONE of APPROVE/REJECT/NULL") is disclosed here verbatim rather than silently
resolved; a re-registration wanting satisfiable per-point gates at ≥ 3σ needs
M_S ≈ 70,000 (n_dead ≈ 7,000 for the C48 O95 tail), or gates registered as
SE multiples — the 16× diagnostic leg already demonstrates both metrics
converge to the closed forms.

**(5) Reporting-only context (registered as unable to flip).** p_d
sensitivity {0.02, 0.30}: T and O95 statistically flat in p_d (consistent
with the registered p_d-free construction; only the mode weights move).
Multi-steal at eager horizons is severe: at R3-C4 @ θ = 6 h, 748 of 891 alive
claims saw ≥ 3 qualifying checks and 826/1000 claims suffered ≥ 1 false
takeover — an eager horizon does not just occasionally twin, it thrashes.
Takeover chains: mean chain length ≈ 1.11 lanes everywhere (deaths are
p_d = 0.10); p95 time-to-done at R3-C48 @ 168 h reaches ≈ 335 h (~14 days) —
the lazy-horizon cost the O95 band prices.

## What it did NOT settle

- **The real fleet's cells.** The measured atlas is a property of the
  registered exponential-mixture tails × Poisson check tempos (the declared
  model basis). The named most-likely-to-flip alternative — the empirically
  measured gap distribution — is deliberately the same zero-tooling live
  probe the NULL case would have shipped: one `git log --diff-filter=AD`
  pass over `control/claims/` plus heartbeat `updated:` stamps per adopted
  repo locates every real lane on this verdict's grid. The REJECT
  consequence does not depend on that probe, but the renewal-slice DESIGN
  review should still run it.
- **Adversarial silence** (a lane gaming the horizon) — out of scope by
  registration: claims are cooperative machinery among honest lanes.
- **Contender contention for the same steal** — first-check-wins timing is
  what is priced; the storage-layout half is already-measured art (superbot
  `tools/sim/claim_layout_sim.py`).
- **The materiality lines themselves.** 0.05 / 120 h / 8-of-9 / 5-of-9 are
  pre-registered judgments; the full T and O95 curves ship in
  `results.json`, so a reader drawing different lines re-reads, never
  re-runs. Note the asymmetry: even doubling the twin budget to T ≤ 0.10
  leaves the C48 column and both R3-C4/R3-C12 (θ=168 O95-busted) infeasible —
  ≥ 5/9 still holds; the REJECT is not knife-edge on the bands.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The question is about a modeled race by design (no live orphan-takeover corpus
exists — ~2 labeled incidents fleet-wide; the idea file's own survey). The
one abstraction that could flip the reading — the gap-tail shape — is the
declared model basis, bracketed wide across the decision grid (means 1.5 h →
48 h tails, check tempos 4 h → 48 h), and the empirical flip is the named
git-log probe. Within the model the decision arm is exact, and the structural
half of the REJECT (O95 = θ + ln(20)/λ_c > 120 at C48; θ = 168 busting the
band everywhere) is distribution-free arithmetic — it survives ANY gap model.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **4,975,945 self-checks, 0 failed**, exit-coded: per-claim invariants
on every replication; three hand-derived pins (the T_A closed form at
(R1,C4,12 h) to 1e−12; O95_A at (C12,24 h) = 24 + 12·ln 20; the C48
structural-infeasibility identity that decides a third of the grid by hand);
exact-identity legs (p_d = 0 → zero orphans; θ→∞ → T = 0 exactly);
monotonicity gates on the closed forms; per-leg draw-count stream-rejoin
sentinels; fixtures cross-check at start. No seeded luck: the decision arm
has NO randomness; the MC's agreement is demonstrated at 16× on every
disputed point and the stability seed reproduces the ruling. No
cherry-picking: the full 54-point atlas and every gate row (including all 11
breaches, with z-scores) ship in `results.json`. The gate-calibration
arithmetic was disclosed BEFORE the run, so the breach handling cannot be
motivated by the outcome.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes, by margin structure: 6/9 infeasible against a 5/9 bar, where the ONLY
knife-edge cell (R2-C4, T = 0.050244 vs 0.05) flips the count to 5/9 —
still REJECT — and the stability leg realized exactly that flip and still
ruled REJECT. The other five infeasible cells miss by structure, not by
margin: C48 fails the latency band by ≥ 29.8 h at every θ; R3-C4/R3-C12 are
twin-unsafe by 15–18 pp at 72 h and latency-busted by 60–84 h at 168 h.
APPROVE was not near: best coverage 3/9 vs the 8/9 bar.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic. Pinned
seeds, pinned loop order, fixed per-claim draw layout, counted streams.
stdout AND `results.json` byte-identical across TWO complete process runs by
external `diff` on cpython-3.11 (pinned and asserted). ~6 s per run.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure any real repo's gap distribution or check tempo (that is
the named live probe); it prices a modeled race under declared neutral
assumptions. It does not design the lease-renewal mechanism — it only
establishes that silence-keyed expiry cannot be made simultaneously twin-safe
and orphan-fast fleet-wide in this class, and quantifies where it locally
can (burst/daily lanes at ≥ 12-hourly check tempo). It says nothing about
adversarial lanes or multi-contender arbitration.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying arm is exact closed-form probability (zero sampling
error on all 54 points); every constant, band, seed and the evaluation order
were registered in the idea file before any code; the MC arm agrees within
sampling error everywhere and within the registered tolerances at 16× on
every disputed point; the ruling is count-robust against its only knife-edge
cell. The honest boundary: the registered per-point MC gates were breached
at the registered M_S — predicted in writing before the run, quantified as
0.7–1.6σ tolerances, and confined to validation (the APPROVE-conditioning
clause), never to the decision surface.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — the pre-registered ≥ 5/9 infeasibility condition is
  met at 6/9 (finalized, not a re-run request).** By the rule committed
  before any code, evaluated in the registered order: APPROVE fails (no θ†
  — best coverage 3/9 vs 8/9 required); REJECT holds (Feas = ∅ in R1-C48,
  R2-C4, R2-C48, R3-C4, R3-C12, R3-C48). Silence-keyed expiry cannot be
  tuned to be simultaneously twin-safe (T ≤ 0.05) and orphan-fast
  (O95 ≤ 120 h) across the regimes and tempos the fleet spans.
- **The routed build (pre-registered REJECT consequence, verbatim):** the
  explicit **lease-renewal stamp** — claim bullets carry a
  `renewed: <ISO8601>` field re-stamped each working wake, and `claims-stale`
  keys on missed renewals (a signal an alive-but-quiet lane CAN send and a
  dead lane CANNOT) — with this verdict's per-cell infeasibility table as
  the evidence row. Routing is the manager's per Q-0260 (kit-owned surface:
  `check_claims.py` + the planted claims doctrine; the kit-lane fan-in
  bundle is the natural ride).
- **The citable numbers, model attached:** structural half — at 48 h-mean
  check sparseness the orphan band is unmeetable at ANY horizon
  (O95 = θ + 143.8 h); weekend-tailed lanes need θ = 168 h for twin-safety,
  which busts the orphan band in every column. Tuned half — silence horizons
  DO work locally: burst/daily-regime lanes checked at least ~12-hourly are
  twin-safe and orphan-fast at θ = 72 h (and R1-C12 down to 24 h). The
  planted 72 h is the best single constant available and still covers only
  3/9 cells; the 24 h order-class prose is mildly twin-unsafe at tonight's
  observed burst check tempo (T = 0.059 at R1-C4).
- **Reading for the renewal-slice designer (reporting-only):** eager
  horizons don't just twin occasionally — they thrash (θ = 6 h in a
  weekend-gapped lane: 83% of alive claims falsely taken over, most ≥ 3
  times); lazy horizons pay two weeks at p95 to clear a dead sparse-checked
  lane. The race has no good global knob — which is exactly why the fix is
  changing the SIGNAL, not the threshold.
- **Model basis (declared, scope-limiting):** exponential-mixture gaps ×
  Poisson checks under uniform conventions; the single most-likely-to-flip
  alternative is the empirically measured gap distribution — obtainable at
  zero tooling cost via `git log --diff-filter=AD` over `control/claims/`
  plus heartbeat `updated:` stamps per adopted repo, recommended as an input
  to the renewal-slice design review.
- **Pre-registration lesson for the pipeline (named follow-up, not
  ordered):** register per-point MC gate tolerances as multiples of the
  registered-n sampling SE (or register the n that makes absolute tolerances
  ≥ 3σ); this proposal's max(4 h, 5%) O95 gate was a 0.7σ gate at C48 by
  construction — disclosed here before the run and absorbed without touching
  the decision, but a tighter drafting rule removes the class.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V026 slice boundary, with header timestamps from live
`date -u` at append time. -->

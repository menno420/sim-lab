# REPORT — adaptive versioning on early signal: two-stage produce→observe→version vs V020's mode fork (PROPOSAL 030)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 030** ·
> 2026-07-13T07:25:14Z · status: sim-ready (idea
> `ideas/venture-lab/adaptive-versioning-early-signal-2026-07-13.md`, landed via
> idea-engine PR #298, main `9b24977`). The ORDER 003 VENTURE rotation slot,
> round 4 — the BOOKS half, pricing VERDICT 020's own named follow-up verbatim
> ("**Adaptive K.** Static quota only; per-title adaptation on early signal is
> a named follow-up, not scope creep" — `sims/verdict-020-book-versioning/REPORT.md`
> @ `76dc487`).
> Run: `python3 sims/verdict-032-adaptive-versioning/adaptive_versioning_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic,
parameter-swept), **fully hermetic** (the PROPOSAL 017–029 precedent): every
fixture is a pinned constant in `fixtures.json` (committed BEFORE the runner),
copied verbatim from the idea file; zero repo/network reads in this verdict
session. The parent's model inherited VERBATIM, extended by exactly ONE new
axis (early-signal noise σ_e) plus the two-stage policy family AD(ω). 324
decision cells × 2 ω, M = 8,000 nights per (cell, policy), CE/CV estimators
per the V020 disclosure with formulas committed in the fixture, per-leg MC SE
shipped; 834,948,000 uniforms total (draw-count sentinels exact). This label
fills the outbox `evidence: simulation`.

## PREMISE (hermetic by pre-registration — nothing to verify live)

The proposal pre-registered the model, grids, seeds, bands, tolerances, and
decision rule BEFORE any code existed; the sim constructs every fixture
itself and reads exactly one file (its own committed `fixtures.json`,
cross-checked at start). The chained-anchor constants (V020's ruling row and
its 45 committed Arm A quadrature values) are quoted VERBATIM in the fixture
from `sims/verdict-020-book-versioning/results.json` @
`76dc487ff15ad564156d4309ff76ed0253532f9b`. Eighteen intake-time decisions are
disclosed in `fixtures.json` (stream assignment, σ_e-inertness of static legs,
reduced-draw discipline, banker's rounding for T1, tie-breaks, the
θ-control-variate, tolerance derivations, the scratchpad-pilot disclosure).
ONE disclosed pre-run correction, before any accepted run: intake decision
10's K_cap-difference map also includes (B = 6, ω = 0.5, c = 0.25), where no
K_cap = 6 leg runs — the map is asserted in-sim for both B; no constant,
band, seed, or M changed (git history shows the amendment).

## What the sim MODELS

All constants pre-registered in `fixtures.json`: V020's production night
(B = 12, integer quarter-units B4 = 48; c ∈ {0.25, 0.5, 0.75} = 4c ∈ {1, 2, 3}
qu; θ ~ N(0,1); ε ~ N(0, σ_v²), σ_v ∈ {0.2, 0.5, 1.0}; revenue exp(q + L),
L ~ N(−σ_m²/2, σ_m²) with E[exp(L)] = 1 exactly, σ_m ∈ {0.5, 1.5, 2.5};
Mode P pick-best f ∈ {0.2, 0.6, 1.0}; Mode A publish-all s ∈ {0, 0.5, 1});
NEW: y = θ + ε_1 + η, η ~ N(0, σ_e²), σ_e ∈ {0.25, 1.0} — **324 decision
cells**. Policies: **AD(ω)**, ω ∈ {0.5, 0.75} — stage 1 T1 = round(ω·B)
one-version titles, observe y, stage 2 spends the rest on extra versions by
y-descending round-robin at K_cap = 4 (remainder discarded and reported);
**S(K)**, K ∈ {1, 2, 3, 4, 6} — ⌊B4/(4+4c(K−1))⌋ full titles + one partial,
the integer-night realization of V020's fractional T_eff. Metric: mean night
revenue per unit budget (denominator always the full B). Comparisons per
(cell, ω): **Δ_cond** = R_AD/R_cond − 1 vs the V020-conditional default
(Mode P K=1 / Mode A K=6, the parent's committed grid-median); **Δ_or** =
R_AD/R_or − 1 vs the in-cell static oracle max_K R_S(K). Decision (registered
order, REJECT FIRST): REJECT iff ∀ω, both σ_e, median-over-81-cells Δ_cond ≤
+0.02 in BOTH modes; APPROVE iff ∃ one ω with median Δ_cond ≥ +0.10
everywhere AND Δ_or ≥ −0.02 in ≥ 80% of cells in all four mode×σ_e quadrants;
NULL otherwise with the flip axis named.

## What it SETTLED (the load-bearing numbers — relative units only)

**(1) REJECT — checked FIRST and met everywhere: early-signal adaptation
buys nothing at the median, under EVERY dial combination swept.** All eight
(mode, ω, σ_e) group medians of Δ_cond sit BELOW the +0.02 line — none is
even positive:

| group | median Δ_cond | oracle pass share (Δ_or ≥ −0.02) |
|---|---|---|
| Mode P ω=0.50 σ_e=0.25 | **−0.3920** | 0.0000 |
| Mode P ω=0.50 σ_e=1.00 | **−0.3922** | 0.0000 |
| Mode P ω=0.75 σ_e=0.25 | **−0.1754** | 0.1605 |
| Mode P ω=0.75 σ_e=1.00 | **−0.1793** | 0.1481 |
| Mode A ω=0.50 σ_e=0.25 | **−0.0336** | 0.3704 |
| Mode A ω=0.50 σ_e=1.00 | **−0.0341** | 0.3704 |
| Mode A ω=0.75 σ_e=0.25 | **−0.0158** | 0.4568 |
| Mode A ω=0.75 σ_e=1.00 | **−0.0276** | 0.4321 |

The closest group (Mode A, ω=0.75, sharp signal) still sits 3.6 pp below the
REJECT line; Mode P is not close anywhere (−17.5% to −39.2%). APPROVE was
never near: no group median reaches +0.10, and the oracle floor Δ_or ≥ −0.02
holds in at most 45.7% of any quadrant's cells vs the required 80%.

**(2) The two-stage policy loses to the ORACLE static quota essentially
everywhere it wins against the default — adaptation's wins are really the
default's losses.** 179/648 (cell, ω) rows have Δ_cond > 0, concentrated
exactly where V020 measured its grid-median default to be the wrong static
quota (Mode A, s = 0, low σ_m — the parent's own 9-cell K\*=1 corner; top row
(c=0.75, σ_v=0.2, σ_m=0.5, s=0, σ_e=0.25, ω=0.75): Δ_cond = **+1.16**). But in
those same cells the in-cell ORACLE is K_or = 1 and Δ_or stays NEGATIVE
(−0.05 to −0.10 on every top row): the signal-directed policy never beats the
best static quota there — it merely spends less on versions than K=6. A
mode-blind two-stage template is dominated by mode-aware static allocation.

**(3) The signal axis is measured nearly inert — the PERFECT-signal upper
bound still REJECTs (reporting leg, cannot flip; it did not).** σ_e = 0
(y reads θ + ε_1 exactly) moves the medians by less than 0.4 pp: Mode A
ω=0.75 median Δ_cond = −0.0193 (vs −0.0158 at σ_e=0.25), Mode P ω=0.75
−0.1755. Even a free, perfectly sharp early signal cannot lift the median
above the +0.02 line inside this family: the binding constraint is the
version-mass arithmetic (stage 1 buys breadth the conditional rule doesn't
want in Mode A, and stage-2 extras are worth less than new titles in Mode P),
not signal sharpness. Per-axis medians of Δ_cond: σ_e {0.25: −0.144,
1.0: −0.151}; mode {P: −0.226, A: −0.032}; c {0.25: −0.178, 0.5: −0.105,
0.75: −0.016}; f {0.2: −0.320, 0.6: −0.212, 1.0: −0.144}; s {0: **+0.092**,
0.5: −0.040, 1: −0.123}. The only positive slice is Mode A s=0 — the
pick-max-listing corner where the parent's K=6 default was already wrong.

**(4) Reporting-only legs (registered as unable to flip; they did not).**
B = 6: same shape (medians −0.393/−0.258 Mode P, −0.054/−0.063 Mode A by ω).
K_cap = 6 changes the allocation only at (ω=0.5, c=0.25) (asserted), where it
converts everyone to K=5 — signal-free by arithmetic. Discarded budget: max
12.5% of B4 at (ω=0.5, c=0.25, K_cap=4); all fractions committed. Worst
per-leg MC se_rel 0.85%; no group median sits within 6 SE of a decision line
except Mode A ω=0.75 σ_e=0.25 (−0.0158 vs +0.02, ~4σ by the shipped SEs) —
and the stability leg reproduces it with margin (−0.0272).

**(5) Validity — all pre-registered gates PASS; 10,567 self-checks, 0
failed; exit 0.** (i) f=1 slice: our quadrature reproduces V020's 45
committed Arm A values EXACTLY after the parent's 9-significant-digit
rounding. (ii) K=1 identity exp((1+σ_v²)/2) and Mode A s=1 additivity
K·exp((1+σ_v²)/2): exact (zero-variance estimators, rel dev ≤ 1e−12).
(iii) **Chained anchor** (fresh seed 20260763, the parent's per-title
machinery re-derived): Mode P share(K\*=1) **0.851851852** / median ΔR **0.0**
(both exact to the committed row); Mode A share(K\*≥2) **0.888888889** (exact)
/ median ΔR **0.40508** vs committed 0.40621411 — inside the pre-checked
tolerance 0.07 (≥ 2.5σ, derivation in the fixture; the parent's own M=2,000
stability median was 0.40446). Seedless analytic sub-gate: 69/81 and 72/81
reproduced exactly. (iv) Signal-degeneracy: pure-noise y vs uniform-order
allocation, rel diff −0.75% (P) / +0.27% (A), tol 1.5%. (v) Static diagnostic
layer vs the closed-form quadrature means: max rel dev 0.989% within the
parent's max(1%, 6·SE) tolerance on all 810 B=12 legs; signal-free AD legs
(allocation uniform by arithmetic) pass the same unbiasedness gate —
covering the whole AD machinery including the θ-control-variate. (vi)
Draw-count sentinels exact on every leg (834,948,000 uniforms: main
384,912,000 / reporting 321,408,000 / aux 32,400,000 / stability 96,228,000);
prefix replay bit-identical; twin decision evaluators agree. (vii)
**Stability leg** (M = 2,000, seed 20260761): ruling **REJECT reproduced**,
all eight group medians ≤ −0.027. (viii) stdout AND `results.json`
byte-identical across TWO complete process runs by external `diff` (sha256
stdout `43d6f125…`, results `c4cdf3de…`); CPython 3.11 pinned and asserted;
~9 min per run, stdlib-only.

## What it did NOT settle

- **Smarter adaptation.** The registered family is two fixed ω, y-descending
  round-robin, fixed K_cap — the measured Δ_cond is a LOWER bound on what
  richer policies (thresholds, per-title stopping, signal-dependent K_cap)
  could earn, so this REJECT rules on THIS family only (stated per the
  done-when; the σ_e = 0 leg shows the family's ceiling is signal-independent,
  which bounds how much a sharper signal alone could rescue it).
- **Signal bias.** y reads version-1 quality noisily; real early signals may
  be BIASED, not just noisy — the σ_e sweep brackets sharpness only. The live
  probe (below) measures the real thing.
- **Anything in currency.** Relative units only — allocation, never earnings
  (Q-0259 r.4 untouched).
- **The publish mode itself.** Mode stays a cell axis exactly as in the
  parent; cross-mode switching mid-night is out of scope by design. V020's
  live two-version s-probe (the LISTING decision) is untouched by this
  verdict.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
Model-true, not market-true — the same epistemic stance as the parent, and
the pre-registered rule was built for it: REJECT required EVERY dial
combination (both modes, both signal sharpnesses, both budget splits) to fail
the median line, and all eight did with 3.6–39 pp of margin. The one
abstraction most likely to flip the reading — signal quality — was swept AND
bracketed from above: the perfect-signal leg still REJECTs, so no achievable
real-world σ_e inside this family changes the conclusion. Signal BIAS and
richer policy families are declared open (the family-floor clause).

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **10,567 self-checks, 0 failed**, exit-coded: fixture pins
re-asserted; quadrature identities; exact K=1 / s=1 zero-variance identities;
the 45-value f=1 slice matched exactly; the chained anchor reproduced the
parent's ruling row at a fresh seed within tolerances pre-checked ≥ 2.5σ
BEFORE any run (the P029 design rule — no mid-session tolerance surgery);
draw-count sentinels exact at the RNG API over 835M uniforms; prefix replay
bit-identical; θ-CV term mean within 6 SE of 0 on every leg; signal-free-leg
unbiasedness against closed forms; twin decision evaluators; the
signal-degeneracy null check. Seeds pinned by the proposal (20260760–63,
strictly above the P029 high-water 20260759); the M=2,000 fresh-seed
stability leg reproduces the ruling. The FULL 648-row Δ tables and all
reporting legs ship in `results.json` — including the 179 rows where
adaptation WINS against the default (the strongest evidence against the
ruling, reported with their oracle columns).

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Not knife-edge: the binding group misses the REJECT line by 3.6 pp (~4σ of
its shipped estimator SE) and every other group by 5.6–41 pp; the stability
leg lands the binding group at −0.0272 with the same ruling; the
perfect-signal upper bound moves medians < 0.4 pp; B = 6 reproduces the
shape. APPROVE fails doubly and hugely (median line by ≥ 12 pp everywhere;
oracle-floor shares 0–46% vs 80%).

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic (reads only
its own `fixtures.json`); fixed seeds, one uniform per normal
(`NormalDist().inv_cdf`), pinned loop order; stdout AND `results.json`
byte-identical across two complete process runs by external `diff`; CPython
minor pinned to 3.11 and asserted at startup. ~9 min per run.

**5. "LIMITS? what this evidence does NOT show."**
No live sales or signal data anywhere in the loop; s, f, σ_e are model dials;
the exp link pins quality elasticity at 1 (bracketed by the σ_m sweep);
per-title independence assumed; the policy family is finite and its Δ_cond a
lower bound on adaptation at large; relative revenue units only — this sim
allocates effort, it never forecasts earnings.

## EVIDENCE STRENGTH: **moderate** — gate PASS

Strong internally (pre-registered bands and evaluation order, chained
anchors to the parent's committed row, dual analytic/MC discipline,
margin-clean REJECT reproduced at a fresh seed, byte-identical runs);
bounded externally by the model-not-market limit and the family-floor
clause both this report and the proposal state up front.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject` — "early-signal adaptation buys nothing — V020's
  conditional rule stands."** By the rule committed before any code (REJECT
  checked FIRST): for every ω and both σ_e, the median-over-cells Δ_cond is
  ≤ +0.02 in both modes — in fact ≤ −0.0158 everywhere, with Mode P at
  −0.18 to −0.39. Stability-reproduced; twin evaluators agree.
- **The pre-registered REJECT consequence, verbatim:** V020's
  mode-conditional static rule stays the standing default for the venture
  book pipeline's night allocation; NO adaptive tooling is built;
  early-signal capture is NOT required for allocation; and the quantified
  reason — the full Δ_cond table — rides the manager sweep.
- **The citable numbers:** one mode-blind two-stage template is dominated
  twice over — it never lifts the median over the conditional default
  (best group −1.6%), and where it beats that default (179/648 rows, all in
  the parent's own Mode A s=0 / low-σ_m corner, up to +116%) the in-cell
  oracle is a STATIC quota (K=1) that still beats it by 5–10%. The
  perfect-signal leg caps the family's ceiling: even σ_e = 0 leaves every
  median REJECT-side, so "measure the signal first" is NOT a prerequisite
  for allocating production nights.
- **Scope qualifier (shipped with the ruling, not a condition):** the REJECT
  rules on the registered two-ω round-robin family — a lower bound on
  smarter adaptation, stated; signal BIAS unmeasured; relative units only;
  the publish-mode fork itself (and V020's live two-version s-probe for the
  LISTING decision) untouched.
- **Named follow-ups (not ordered):** richer adaptive families (thresholded
  stage-2, per-title stopping) only if the lane ever measures a real cell
  where the conditional rule is unavailable (mode unknown at allocation
  time); the V020 s-probe remains the lane's cheapest live measurement; a
  σ_e pipeline-log column stays PRICED but NOT required (this verdict
  measured that allocation does not need it).

# REPORT — Braess's paradox added-edge frequency (PROPOSAL 024)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 024** ·
> 2026-07-13T04:21:12Z · status: sim-ready (idea
> `ideas/fleet/braess-paradox-added-edge-2026-07-13.md`, landed via idea-engine
> PR #290, main `b11e258`). The ORDER 004 rule-3 COMPLETELY-UNRELATED-domain
> rotation slot, round 2 — transportation / congestion routing games (Wardrop
> selfish-user equilibrium), a fresh fleet-external domain after round 1's
> social choice (PROPOSAL 017 → VERDICT 019). Fully hermetic: both arms
> construct their entire world in-sim; zero repo/network reads in the verdict
> session; Arm A carries no PRNG at all.
> Run: `python3 sims/verdict-026-braess-added-edge/braess_added_edge_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — an exhaustive exact census plus a
seeded continuous robustness arm, band-scored against the pre-registration):
the frequency f and inflation ratio r of Braess's paradox (adding the bridge
RAISES the selfish-equilibrium total travel cost) over the pinned affine
diamond family. Arm A is a pure integer census in exact `fractions.Fraction`
— f_A, median-r, and max-r are platform-independent exact rationals with NO
sampling error; Arm S re-measures the frequency under continuous U[0,2]
coefficients on four pinned seeds to expose any integer-grid modeling
artifact. This label fills the outbox `evidence: simulation`. The one
judgment question — whether 0.03/0.15 and the r-thresholds are the RIGHT
materiality lines — was pinned by pre-registration in the idea file; the full
tables ship in `results.json`, so a re-drawn line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock. Every
constant ({topology, coefficient grids, bridge grid, seeds 20260740–43,
band constants, arm-agreement gate}) was copied verbatim from the idea file
into `fixtures.json` BEFORE the runner was written, and the runner
cross-checks its literals against that file at start. Seven intake-time
decisions are disclosed in `fixtures.json`: n_draws = 25,000/seed (with the
disclosure that a throwaway scratchpad feasibility probe ran before the
fixtures commit — every decision constant was already pinned by the idea
file, so no free parameter remained tunable); the Arm-S float tolerance
(paradox iff cost_with > cost_without·(1+1e−9) + 1e−12); the Arm-S call
convention (same band constants on its own pooled statistics); the median
convention (even count → exact mean of the two middle values); the solver
design (Beckmann candidate enumeration whose output is VERIFIED per fixture
against the exact Wardrop conditions — the verification carries the proof);
the twin stride; and the reporting-only bridge-cell breakdown.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Network:** the classic Braess diamond — nodes s, a, b, t; base edges
  e1 = s→a, e2 = a→t, e3 = s→b, e4 = b→t; optional bridge e5 = a→b enabling
  route R3 = s→a→b→t alongside R1 = s→a→t and R2 = s→b→t. Unit demand D = 1.
- **Behavior:** Wardrop user equilibrium (every used route has minimal
  latency) under affine non-decreasing latencies l_e(x) = a_e·x + b_e,
  a_e ≥ 0 — the minimizer of the convex Beckmann potential; for monotone
  latencies ALL equilibria share every edge latency and the total cost
  (essential uniqueness), so any VERIFIED equilibrium yields THE cost
  C = Σ_e x_e·(a_e·x_e + b_e).
- **Arm A (decision-carrying, exact):** exhaustive census (a_e,b_e) ∈
  {0,1,2}² per base edge × (a5,b5) ∈ {0,1}² on the bridge = 26,244 raw
  fixtures; 0-cost-without fixtures excluded, effective N reported;
  f_A = #(cost_with > cost_without)/N; r = cost_with/cost_without among
  paradox fixtures → median-r, max-r. No PRNG, no floats.
- **Arm S (robustness):** a_e, b_e ~ U[0,2] continuous, `random.Random`
  seeds 20260740/20260741/20260742/20260743 × 25,000 draws each (100,000
  pooled), 10 uniforms per draw in pinned edge order, documented float
  tolerance; pooled f_S plus its own median-r/max-r for the arm's call.
- **Decision rule (registered before any code):** APPROVE iff f_A ≥ 0.15 OR
  median-r ≥ 1.15; REJECT iff f_A ≤ 0.03 AND max-r ≤ 1.05; NULL otherwise
  (bands mutually exclusive by arithmetic, so no order ambiguity); non-NULL
  requires the arm-agreement gate |f_S − f_A| ≤ 1.0 pp AND the same call,
  else NULL-by-arm-disagreement.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**(1) Arm A — the exact census (the decision statistics).** Of 26,244 raw
fixtures, 644 have without-bridge cost 0 (skipped) → **N = 25,600**.
Paradox count **855** →

- **f_A = 171/5120 = 0.0333984375** (3.34%) — an exact rational, no
  sampling error.
- **median r = 80/77 ≈ 1.0390** — the typical paradox inflates total travel
  cost by ~3.9%.
- **max r = 4/3 exactly** — the census contains the canonical Braess
  configuration (pin A: e1=(1,0), e2=(0,1), e3=(0,1), e4=(1,0), e5=(0,0);
  cost 3/2 → 2), realizing the known affine worst case exactly.

**Band arithmetic:** APPROVE fails — f_A = 0.0334 is 4.5× below the 0.15
line AND median-r = 1.039 < 1.15 (0.11 short). REJECT fails — f_A = 0.0334 >
0.03 (misses by 0.34 pp, exact comparison 171/5120 > 3/100) AND max-r = 4/3
> 1.05 (the magnitude leg was unreachable: the worst case lives inside the
census). **Arm A call: NULL (the straddle).**

**(2) Arm S — the continuous arm agrees; the integer grid is not an
artifact.** Pooled n = 100,000 (0 degenerate skips), paradox 2,908 →
**f_S = 0.02908** (per-seed 761/712/730/705 per 25,000 = 0.0304/0.0285/
0.0292/0.0282 — stable); median r ≈ 1.0051, max r ≈ 1.0944 → REJECT fails on
the max-r leg (1.094 > 1.05) with f_S also effectively at the 0.03 line;
APPROVE fails everywhere. **Arm S call: NULL. Arm-agreement gate:
|f_S − f_A| = 0.0043 ≤ 0.01 ✓ AND same call ✓ — met.** The continuous draw
lands the paradox frequency within half a percentage point of the integer
census: the grid does not over-represent paradox corners.

**(3) Reporting-only context (cannot flip; registered as such).** The bridge
HELPS far more often than it hurts: improved 3,913/25,600 = **15.3%**,
paradox 855 = **3.3%**, unchanged 20,832 = **81.4%**. By bridge cell:
free-flowing bridges hurt most — paradox 5.47% at (a5=0,b5=0) and 5.64% at
(a5=1,b5=0) vs 1.13% at both b5=1 cells: a nonzero constant cost on the
shortcut suppresses the paradox ~5× in this class.

**(4) Validity.** All analytic gates PASS: (g1) the exact Wardrop
variational conditions verified at every computed equilibrium — 25,600 + 644
census fixtures × both networks exactly, 100,000 draws within 1e−9; (g2)
every paradox ratio ≤ 4/3 exactly (the affine Braess bound — a theorem, so
any violation is a solver bug); (g3) the reversal-symmetry involution
σ(e1,e2,e3,e4,e5) = (e4,e3,e2,e1,e5) preserves both costs on every census
fixture; (g4) unused-bridge invariance both directions (cost moved ⟹ bridge
carries flow; bridge unattractive at the base equilibrium ⟹ cost unchanged);
(g5) cpython-3.11 asserted, stdout + results.json byte-identical across two
complete process runs by external diff; (g6) exact draw-count sentinels
(10 uniforms/draw; fresh Random(seed) advanced 250,000 steps rejoins each
leg's stream exactly). The independently written support-enumeration TWIN
solver found ≥ 1 equilibrium on every fixture-network and agreed with the
primary's cost EXACTLY on the full census (both networks) and within 1e−6 on
all 504 strided Arm-S draws. Three hand-derived pins with committed
derivations (canonical Braess 3/2→2 with r = 4/3; the all-constant
no-paradox diamond; a bridge-HELPS fixture 2→1) all reproduced.
**358,476 self-checks, 0 failed**; ~11 s per run, stdlib-only.

## What it did NOT settle

- **Real-world frequency.** The measured 3.3%/2.9% is a property of THIS
  coefficient distribution (uniform grid / U[0,2]) on THIS topology under
  selfish Wardrop routing — the model-basis declaration in the idea file.
  Under **system-optimal routing** (the named most-likely-to-flip
  alternative) the paradox cannot occur at all (adding an edge weakly lowers
  the system optimum), so f → 0; a non-uniform prior concentrated away from
  paradox corners would also move f without changing the behavior model.
- **Larger networks / non-affine latencies.** The 4-node affine diamond is
  where the paradox is canonical; extensions (bigger graphs, BPR-style
  polynomial latencies, multi-commodity demand) multiply the state space,
  break the closed-form uniqueness argument, and are follow-up material —
  the affine 4/3 worst-case bound does NOT carry to them.
- **The materiality lines themselves.** 0.03/0.15 and 1.05/1.15 are
  pre-registered judgments; the exact f_A, the full r distribution inputs,
  and the bridge-cell breakdown ship in `results.json`, so a reader drawing
  different lines re-reads, never re-runs.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The pre-registered question is about a constructed family, not a live
system — by design (the unrelated-domain rotation's hermeticity contract).
The one abstraction that could flip the HEADLINE reading — routing behavior —
is declared in the model basis: under system-optimal routing f → 0
identically, and the verdict's scope is explicitly selfish-Wardrop-under-
uniform-coefficients. Within that scope the dual-arm design closes the
remaining gap (discrete grid vs continuous coefficients) and measures it at
0.43 pp.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **358,476 self-checks, 0 failed**, exit-coded: the exact Wardrop
verification at every single equilibrium (the construction is never
trusted — the variational inequality plus essential cost uniqueness IS the
correctness proof); an independently written support-enumeration twin
agreeing exactly on the full census and within 1e−6 on strided continuous
draws; the exact affine 4/3 bound as a theorem-gate; the reversal-symmetry
involution across all 26,244 fixtures; unused-bridge invariance both
directions; exact draw-count sentinels; three hand-derived pins with
committed derivations. No seeded luck: Arm A has NO randomness (an exact
rational), and Arm S's four seeds land 0.0282–0.0304 individually. No
cherry-picking: the census is exhaustive and the full breakdown ships.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is not knife-edge on the side that matters: APPROVE is missed 4.5×
on frequency and by 0.11 on median inflation in BOTH arms. The REJECT
frequency leg IS close (f_A misses by 0.34 pp; f_S sits at 0.029), but
REJECT's magnitude leg is failed unambiguously in both arms (4/3 and 1.094
vs 1.05) — and 4/3 is exact, not an estimate — so no plausible edge
variation flips the ruling. The arm-agreement gate held with 0.43 pp of the
1.0 pp budget used.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic. Arm A is
platform-independent exact rational arithmetic (no PRNG, no floats); Arm S
uses one `random.Random(<pinned seed>)` stream per leg, exactly 10 uniforms
per draw. stdout AND `results.json` byte-identical across TWO complete
process runs by external `diff` on cpython-3.11 (pinned and asserted).
~11 s per run.

**5. "LIMITS? what this evidence does NOT show."**
It does not measure any real road network or any fleet system; it prices a
constructed affine family under one behavioral model. It says nothing about
larger topologies or non-affine latencies (the 4/3 bound is affine-only).
It cannot rank the SEVERITY of real-world Braess instances — only that in
this natural family the paradox is a ~3% event with typical inflation ~4%
and worst case exactly 4/3.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

The decision-carrying arm is an exhaustive exact computation (a rational
number, not an estimate); every constant, band, seed, and the gate were
registered in the idea file before any code; both arms agree within half the
allowed gap; the twin and the theorem-gates passed everywhere. The honest
boundary: this strength attaches to the pinned diamond family and the
registered bands — the sim measures the paradox's rate in a constructed
class, it does not certify any real network.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `null` — the pre-registered straddle, arms agreeing, finalized
  (not a re-run request).** By the rule committed before any code: APPROVE
  fails (f_A = 171/5120 = 0.0334 < 0.15 AND median-r = 80/77 ≈ 1.039 <
  1.15); REJECT fails (f_A > 0.03 by 0.34 pp AND max-r = 4/3 > 1.05). Arm S
  agrees (f_S = 0.02908, |f_S − f_A| = 0.43 pp ≤ 1.0 pp, same NULL call) —
  the integer census is not a paradox-inflating artifact.
- **The citable finding (pre-registered NULL consequence, verbatim):** the
  risk is real but not common/large enough for a blanket rule — audit only
  high-stakes networks case-by-case, and **neither "Braess is a real design
  hazard" nor "Braess is a textbook curiosity" may be cited as settled**
  from this verdict. The numbers to cite: in the natural affine diamond
  class, an added shortcut RAISES everyone's travel time in **~3.3%** of
  configurations (exactly 171/5120 on the census; 2.9% continuous), with
  **typical inflation ~3.9%** (median r = 80/77) and **worst case exactly
  4/3**; it HELPS in ~15.3% and changes nothing in ~81.4%.
- **Reading for designers (reporting-only, from the committed breakdown):**
  the paradox concentrates on cheap shortcuts — a free-flowing bridge
  (b5 = 0) hurts in ~5.5% of configurations vs ~1.1% when the shortcut
  carries even one unit of constant cost; and the canonical worst case is
  IN the family, so "small class, small harm" is false at the tail.
- **Model basis (declared, scope-limiting):** selfish Wardrop routing under
  uniform coefficients; under system-optimal routing the paradox cannot
  occur (f → 0) — a reader swapping the behavioral model or the coefficient
  prior is outside this verdict's registered scope.
- **Named follow-ups (not ordered):** larger-topology / non-affine (BPR)
  extensions as future unrelated-domain rotation slots IF the manager wants
  the domain deepened; the reusable methodology note — the dual-arm
  (exact census + seeded continuous) discipline transferred cleanly from
  VERDICT 019 and is now twice-proven for unrelated-domain heads.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V024 slice boundary, with header timestamps from live
`date -u` at append time. -->

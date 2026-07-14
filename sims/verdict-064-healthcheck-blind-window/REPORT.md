# REPORT — VERDICT 064: the healthcheck blind window (PROPOSAL 053)

**Ruling: REJECT** (registered rules applied in order — REJECT checked
FIRST and it FIRES on BOTH conjuncts, on Arm A's exact Fractions at the
shipped cell T = 360 under the headline pins q = 1/20, d ~ uniform{0..30}:
**DET_mix(360) = 123709/372000 = 0.33255… < 1/2** AND
**WINDOW(360) = 22913/372000 = 0.061594… > 1/20**. The "standing liveness
verification" framing overstates what a 6-hourly point-probe sees — the
net misses two thirds of the pinned transient-outage mix — and the
backlog's "up to 6 hours" hard window fails about one persistent fault in
sixteen once the workflow's own delay-or-drop caveat is priced. The honest
doc line is the registered scoped one: *catches faults that persist to the
next fire, blind to most shorter blips.* The drafter's disclosed landing
was re-derived from scratch with zero trust and reproduces EXACTLY on
every disclosed Fraction — with two disclosed-exhibit anomalies found and
reported below, neither touching a decision number.)

Registration: `## PROPOSAL 053 · 2026-07-14T01:15:36Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main 39e35ec, landed via idea-engine
PR #379; idea doc `ideas/websites/healthcheck-blind-window-2026-07-14.md`;
harvest source websites @ `3076e9d` — citation only). Fully hermetic —
every constant pinned in fixtures.json (committed BEFORE the runner), zero
repo/network reads at verdict time.

## The question and the model (registered, hermetic)

Probes fire on the cadence lattice s_k = k·T (the wall-clock minute-17
phase cancels under the uniform onset phase); each scheduled fire is
independently dropped with q = 1/20, else executes at s_k + d,
d ~ uniform{0..30} min. A transient outage of duration D at onset phase
φ ~ uniform{0..T−1} is DETECTED iff some non-dropped fire executes inside
[φ, φ+D); conditional on φ the per-fire failures are independent, so every
miss probability is an exact product — Arm A enumerates the full lattice
in exact `fractions.Fraction`. Persistent faults: L = earliest successful
execution at/after onset minus onset; WINDOW(T) = P(L > 360), the
backlog's "up to 6 hours" read as the hard window it states. Bands fixed
before any code: REJECT iff DET_mix(360) < 1/2 OR WINDOW(360) > 1/20
(checked FIRST); APPROVE iff DET_mix(360) ≥ 3/4 AND WINDOW(360) ≤ 1/100
AND stability reproduces; NULL on three named axes; INVALID on any control
failure.

## Decision numbers (Arm A exact, alone decision-bearing)

At the shipped cell T = 360 (cron `17 */6 * * *`, 4 runs/day):

| D (min) | DET(360, D) exact | float |
|---|---|---|
| 5 | 19/1440 | 1.32% |
| 30 | 19/240 | 7.92% |
| 60 | 19/120 | 15.83% |
| 180 | 19/40 | 47.5% |
| 360 | 6536/6975 | 93.71% |

**DET_mix(360) = 123709/372000 ≈ 0.3326** (equiprobable mix) — the net
misses ~2/3 of the pinned transient mix; a half-hour blip is seen about
one time in thirteen. **WINDOW(360) = 22913/372000 ≈ 0.0616** — "up to 6
hours" fails ≈ 1 persistent fault in 16.2, more than three times the
registered 1/20 tolerance. Registered mixes never change the DET conjunct:
short-heavy 612617/3348000 ≈ 0.183, long-heavy 322829/669600 ≈ 0.482 —
every registered mix lands < 1/2.

**The registered decomposition (the sharpening) confirmed exactly:** at
q = 0, d ≡ 0 the transient conjunct STILL trips — DET_mix(360) = 127/360
≈ 0.353 < 1/2 (point-probe structure, not invented noise) — while
WINDOW(360) = 0 exactly (the "up to 6 hours" wording is true precisely
when the scheduler is perfect, the caveat the header itself disclaims).
The WINDOW conjunct is delivery-driven, the DET conjunct is structural.

**The cadence menu** (equiprobable mix; runs/day = 1440/T):

| T (min) | DET_mix(T) | WINDOW(T) | E[L] headline (min) | runs/day |
|---|---|---|---|---|
| 60 | 0.6852 | 3.74e-08 | 33.9 | 24 |
| 180 | 0.4843 | 0.00366 | 99.4 | 8 |
| **360** | **0.3326** | **0.0616** | **198.7** | **4** |
| 720 | 0.1676 | 0.5237 | 397.5 | 2 |
| 1440 | 0.0838 | 0.7618 | 795.3 | 1 |

Falsifiability held honestly: the T = 60 cell lands DET_mix =
33988034271/49600000000 ≈ 0.685 ∈ [1/2, 3/4) — the registered NULL band,
exactly as disclosed — so the bands genuinely discriminate.

**Per-φ structure of the blindness** (full 360×5 exact table in
results.json): at the shipped cell a D-minute outage has exactly ZERO
detection probability from 360−D−30 of the 360 onset phases (325/360
phases for D = 5; 300/360 for D = 30; 270/360 for D = 60; 150/360 for
D = 180; 0/360 for D = 360) — the blind window is phase-structured, not
noise: outages that fit between delayed fires are invisible at ANY drop
rate.

## Controls and gates (all green; any failure exits 1 = INVALID)

- **Zero-noise identities, both arms:** Arm A exact — MISS(T,D) = (T−D)/T
  for D ≤ T (all 25 cells, incl. MISS(360,180) = 1/2), 0 for D ≥ T;
  WINDOW(360) = 0; WINDOW(720) = 359/720. Arm B (seed 20261350,
  N = 20,000) — per-draw EXACT indicator identities on every scenario × T
  × D plus the estimate gates.
- **Independent second structure at the decisive cell:** full 1024-outcome
  per-fire enumeration (exact integer weights 31/19 over denominator
  620²) equals the product form on every DET(360, D) and WINDOW(360).
- **Monotonicity theorems:** DET(T,D) non-decreasing in D (every world);
  DET_mix(T) non-increasing in T (every world × every mix); WINDOW(T)
  non-decreasing in q — exact arm AND per-scenario under common random
  numbers in the MC q-sweep (L_min non-decreasing in q on every scenario).
- **Arm B agreement gate:** 315 reported cells gated (25 DET + 15 mix +
  5 WINDOW per gated world), all passed |EST − EXACT| ≤ 1/100 absolute AND
  ≤ 4·SE; worst absolute deviation 0.00649 (sens q=0 WINDOW(720)) vs
  allowance 0.01 and 4·SE = 0.01414.
- **Stability leg (seed 20261352, N = 20,000):** DET_mix(360) est
  208/625 = 0.3328, WINDOW(360) est 613/10000 = 0.0613 → REJECT through
  BOTH twin independently-written evaluators (Fraction comparisons vs pure
  integer cross-multiplication) — reproduces the Arm A class. Nearest band
  edge sits ≈ 50·SE (DET conjunct) and ≈ 7·SE (WINDOW conjunct) away.
- **Seed discipline:** 20261349 headline / 20261350 control / 20261351
  sensitivity / 20261352 stability — the ONLY four RNGs constructed, in
  pinned order; draw sentinels exact (3,800,000 / 380,000 / 1,140,000 /
  380,000 = N·(1+2K) per leg); decision numbers frozen before any RNG
  existed. Seeds strictly above the P052/V063 high-water 20261348 — NEW
  REGISTRY HIGH-WATER 20261352.
- **Self-checks: 886 passed, 0 failed; exit 0; ~6 s/run.**

## Sensitivity worlds (seed 20261351 + exact; reporting-only, never ruling)

At the shipped cell T = 360:

| world | DET_mix(360) | WINDOW(360) | conjunct side |
|---|---|---|---|
| headline q=1/20, d{0..30} | 0.3326 | 0.06159 | REJECT · REJECT |
| q = 0, d{0..30} | 781/2232 ≈ 0.3499 | 29/2232 ≈ 0.01299 | REJECT · **NULL straddle** |
| q = 1/10, d{0..30} | 0.3152 | 0.1103 | REJECT · REJECT |
| q = 1/20, d ≡ 0 | 2413/7200 ≈ 0.3351 | 7181/144000 ≈ 0.04987 | REJECT · **crosses (knife-edge below 1/20)** |
| q = 1/20, d{0..60} | 0.3300 | 0.0741 | REJECT · REJECT |
| zero-noise | 127/360 ≈ 0.3528 | 0 | REJECT · **APPROVE side** |

The DET_mix conjunct fires in EVERY world (it never crosses 1/2 anywhere
on the registered sensitivity axes — the REJECT does not ride the invented
noise). The WINDOW conjunct's named straddles: the q = 0 world lands in
the registered NULL band (1/100, 1/20] exactly as disclosed; the d ≡ 0
world lands 19/144000 ≈ 0.00013 BELOW the 1/20 edge (anomaly A3, a
knife-edge worth naming); zero-noise lands APPROVE-side (the registered
decomposition). Named, never ruling — REJECT fired first on the headline
pins.

## Drafter-reference comparison (never gated) + anomalies (first-class)

Every disclosed exact Fraction reproduces EXACTLY from scratch:
DET_mix(360) = 123709/372000 ✓, WINDOW(360) = 22913/372000 ✓, all five
DET(360, D) exhibits ✓, zero-noise DET_mix(360) = 127/360 ✓, zero-noise
WINDOW(360) = 0 ✓; approx exhibits T=60 DET_mix ≈ 0.685 ✓ and q=0/d{0..30}
WINDOW ≈ 0.013 ✓ (exact: 29/2232). **No drafter arithmetic error in any
decision-bearing or straddle-bearing number.** Two drafter anomalies and
one finding, all reporting-only:

- **A1 — the registered zero-noise E[L] sanity row (T+1)/2 is wrong under
  the pinned model; the model forces E[L] = (T−1)/2** (verified exactly at
  every grid T). The inconsistency is internal to the registration: the
  decision-side identity WINDOW(720) = 359/720 requires the
  onset-coincident fire to count (L(φ=0) = 0), which gives (T−1)/2; the
  (T+1)/2 row would require it NOT to count, which would force
  WINDOW(720) = 360/720. The registered INVALID gates (MISS/WINDOW
  identities) hold exactly as written; only the reporting-row closed form
  is off by one. E[L] is reporting-only and is not in the registered
  INVALID list — reported, not ruled on.
- **A2 — the disclosed T = 60 exhibit "WINDOW ≈ 3.7×10⁻¹¹" is off by three
  orders of magnitude:** exact WINDOW(60) = 7413/198400000000 ≈
  3.736×10⁻⁸ (the mantissa matches, the exponent does not — a q⁶-scale
  quantity, not q⁸·⁴). Direction of the falsifiability exhibit (tiny, far
  below every band) unaffected.
- **A3 — knife-edge finding:** the d ≡ 0 world's WINDOW(360) =
  7181/144000 sits 19/144000 below the 1/20 REJECT edge — with drops but
  zero delay spread, "up to 6 hours" just barely holds; the headline's
  own delay support pushes it over. Named sensitivity straddle.

## E[L] table (reporting; exact, minutes)

Zero-noise row (T−1)/2 (derived closed form — see A1): 29.5 / 89.5 /
179.5 / 359.5 / 719.5 over the T grid. Headline (q = 1/20, W = 30):
33.9 / 99.4 / **198.66 (= 169853/855 at the shipped cell)** / 397.5 /
795.3. At q = 1/10: 219.7 at the shipped cell. E[L] strictly increasing
in q at every T (asserted).

## Boundaries (registered, carried verbatim)

**Independence** — drops/delays independent across fires is the pinned
assumption; correlated scheduler congestion is the named
most-likely-to-flip alternative: it fattens the WINDOW tail (REJECT-ward
on that conjunct) and barely moves DET_mix; the wide-q leg (q = 1/10:
WINDOW 0.1103) brackets the scale. **Delivery magnitude** — real minute-17
drop rates could be far below 1/20 (the mitigation the header commits);
the q = 0 decomposition shows the DET_mix conjunct survives it entirely
(127/360 < 1/2 with delivery PERFECT), while the WINDOW conjunct then
lands the registered NULL straddle (0.013) — the pre-priced free probe
(read the healthcheck workflow's PUBLIC Actions run history, measure real
inter-fire gaps and missing slots) replaces the invented (q, d) at one
page-read of cost. **Scope** — detection ≠ notification: a DROPPED run
sends no failed-workflow email and the check is NOT required (nothing
gates on red) — carried as a quoted inspection-decidable flag, never
simulated; curl-level rendering blindness is the source repo's own
captured browser-crawl follow-up, out of scope at ANY cadence.

## Byte identity (external sha256, two full process runs)

- `run-stdout.txt` sha256
  `5f205ebfcd774845ebefc576b62cbdfe1f9b9c70888c91bc3b6f36b3b33768fe`
  (identical both runs)
- `results.json` sha256
  `c6ed36048c7cdde61a8a00dac819129a3732916e929ada73dbbc227c683c75a4`
  (identical both runs)

No fix-forwards — the first complete run of the registered pipeline is the
accepted run. CPython 3.11 pinned and asserted.

## Validity gates

- **COMPARABLE: PASS** — every decision number is an exact Fraction under
  the registration's own pinned frame; fixtures.json copied verbatim from
  the PROPOSAL 053 block / idea doc and committed BEFORE the runner; both
  sides of the decisive comparison are the registration's own band
  constants against the model it pinned; the fixture-level choices this
  session (K = 9 fire variates + coverage proof, the 19-draw scenario
  shape and CRN maps, exact-variance SE convention, control N, sensitivity
  world order, E[L] closed-form method, the 1024-outcome brute-force
  cross-structure, twin evaluators, draw sentinels) were all disclosed in
  the fixture before any code ran.
- **UNCORRUPTED: PASS** — git trail: born-red card → fixtures → runner +
  accepted run; bands, grids, seeds, draw order, evaluation order (REJECT
  first) all registered in PROPOSAL 053 before this session existed; 886
  self-checks 0 failed; no fix-forwards; the drafter's disclosed landing
  re-derived from scratch with zero trust — confirmed exactly where exact,
  refuted where wrong (A1, A2), and the comparison REPORTED, never gated.
- **ROBUST: PASS** — nothing knife-edge on the ruling: the DET_mix
  conjunct clears its band by 0.167 absolute (≈ 50·SE at the stability N)
  and fires in EVERY registered world including zero-noise; the WINDOW
  conjunct clears by 1.23× the band edge (≈ 7·SE); REJECT needs one
  conjunct and has both; every registered mix lands the DET conjunct on
  the same side; the stability leg reproduces REJECT through both twin
  evaluators; the named knife-edges (A3's d ≡ 0 world, the q = 0 NULL
  straddle) sit on reporting-only axes and are disclosed, not smoothed.
- **REPRODUCIBLE: PASS** — one command, no flags, hermetic (reads only its
  own fixtures.json), stdlib-only; Arm A platform-independent exact
  rationals, alone decision-bearing; stdout + results.json byte-identical
  across two full process runs by external sha256 (hashes above); CPython
  3.11 pinned and asserted; seeds 20261349–352 strictly above the
  P052/V063 high-water 20261348, new registry high-water 20261352; ~6
  s/run.
- **LIMITS: stated** — model-true under the registered frame, not a live
  measurement: the delivery noise (q, d) and the outage-duration mix are
  INVENTED-pinned-disclosed (the repo commits the phenomenon and one
  exemplar in-window miss, no magnitudes); the q = 0 decomposition proves
  the transient-blindness conjunct owes nothing to the invented noise,
  and the Actions-run-history read is the named free measurement for the
  delivery half; independence across fires is the pinned assumption with
  the correlated-congestion direction stated (REJECT-ward on WINDOW);
  the 4·SE half of the agreement gate is float by disclosure on a ruling
  with ≥ 7·SE margins; detection ≠ notification and browser-level
  blindness carried as quoted flags, never simulated; live delivery
  evidence supersedes wherever a future measured frame disagrees.

**Verdict: REJECT** — the shipped 6-hourly point-probe is a
persistent-fault net, not a blip net: it detects 93.7% of 6-hour outages
but 7.9% of half-hour ones (DET_mix(360) = 0.333 < 1/2), and the
backlog's "up to 6 hours" hard window fails ≈ 6.2% > 1/20 of persistent
faults under the workflow's own delay-or-drop caveat. The registered
scoped line is the honest one: *catches faults that persist to the next
fire, blind to most shorter blips.*

**Recommendation:** per the proposal's pre-registered REJECT consequence,
verbatim-faithful (routing is the manager's per Q-0260 — this repo edits
no websites file): (1) the workflow header gains the honest scope line
with the quantified blind window (per-φ structure: a D-minute blip is
invisible from 360−D−30 of the 360 onset phases at the shipped cell);
(2) the backlog's "up to 6 hours" wording gets its measured violation rate
(22913/372000 ≈ 6.2% under the pinned caveat; 0 exactly under a perfect
scheduler — the wording is true precisely when the header's own caveat is
false); (3) the DET × (T, D) cadence menu with its runs/day cost column
prices any future retune of `17 */6` (hourly probing buys DET_mix 0.685
and WINDOW ≈ 3.7×10⁻⁸ at 24 runs/day) and the captured browser-crawl
bullet's cadence choice inherits the same table; the pre-priced free live
probe stands — read the healthcheck workflow's public Actions run history
and replace the invented (q, d) with measured gaps and missing slots at
one page-read of cost.

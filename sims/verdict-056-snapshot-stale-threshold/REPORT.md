# VERDICT 056 — mineverse snapshot stale-indicator threshold (idea-engine PROPOSAL 045)

**Ruling: APPROVE** — the contract's default is right-sized. At the pinned
disturbance model, T = 180 s (the contract's "3 missed cycles ≈ 180 s"
suggestion) holds false-stale to ≈ 1/2070 of healthy loads (≤ 1/200 band with
10× headroom) at 145.0 s mean outage detection (≤ 240 s band), while neither
2-nominal-cycle threshold does (FALSESTALE(120) ≈ 1/102 > 1/200,
FALSESTALE(90) ≈ 1/31), and the seed-20261318 stability leg reproduces the
ruling through both twin evaluators.

Source: idea-engine `## PROPOSAL 045 · 2026-07-13T20:24:09Z · status: sim-ready`
(idea-engine PR #343, main 5f8a94e; idea doc
`ideas/superbot-mineverse/snapshot-stale-indicator-threshold-2026-07-13.md` @ 62821c5).
Harvested contract: superbot-mineverse `docs/mining-data-contract.md`
§ Delivery expectations @ ae98dd094100f7b864f2c36b91494c8fb2cd1f31 (clone-verified
at exactly that HEAD this session; both sentences quoted verbatim in fixtures.json).

## Decision walkthrough (pre-registered order, REJECT FIRST)

1. **REJECT** (Feas = ∅ — "a client-side age threshold cannot be made honest
   at the pinned cadence")? **Does NOT fire**: Feas = {150, 180, 240}, T* = 150.
2. **APPROVE** (180 ∈ Feas AND Feas ∩ {90, 120} = ∅ AND stability reproduces)?
   **FIRES**: 180 ∈ Feas (FALSESTALE(180) = 36671213/75892578125 ≈ 4.832e-4
   ≤ 1/200; LAT(180) ≈ 145.02 ≤ 240); Feas ∩ {90, 120} = ∅
   (FALSESTALE(90) ≈ 0.03277 and FALSESTALE(120) ≈ 0.009801, both > 1/200);
   stability leg reproduces (Feas_S = {150, 180, 240}, same class, twin
   evaluators agree). 150 ∈ Feas does not defeat APPROVE (registered: only a
   full cheaper CYCLE — 90/120 — would).
3. NULL — not reached.

## Decision table (Arm A, exact Fractions — the ruling rides Arm A alone)

| T (s) | FALSESTALE exact | ≈ | LAT exact (s) | ≈ | feasible |
|------:|------------------|---|---------------|---|----------|
| 90  | 19897377/607140625 | 3.277e-2 | 24168503696/433671875 | 55.730 | no (FS) |
| 120 | 121441/12390625 | 9.801e-3 | 1055680488/12390625 | 85.200 | no (FS) |
| 150 | 1046384939/531248046875 | 1.970e-3 | 940293190208/8173046875 | 115.048 | YES |
| 180 | 36671213/75892578125 | 4.832e-4 | 11005917208984/75892578125 | 145.020 | YES |
| 240 | 3972436729/167343134765625 | 2.374e-5 | 3500718263494568/17075830078125 | 205.010 | YES |
| 300 | 107264196293/87855145751953125 | 1.221e-6 | ≈ 265.010 | 265.010 | no (LAT) |
| 360 | ≈ 6.623e-8 | 6.623e-8 | ≈ 325.010 | 325.010 | no (LAT) |

E[G] = 1625/24 exactly. Bands: FALSESTALE ≤ 1/200 AND LAT ≤ 240 s.
P(L > 300): 0 exactly for T ≤ 240; T = 300 → 2232/19825 ≈ 0.1126;
T = 360 → 399648/495625 ≈ 0.8064 (reporting-only; L ≤ T − c_lo = T + 30, so
guaranteed-zero exactly where T + 30 ≤ 300).

## Arms & gates (all green; 513 self-checks, 0 failed, exit 0)

- **Arm A** (decision): seedless exact-Fraction renewal-reward enumeration —
  geometric mixture of n-fold convolutions of the 21-point interval lattice,
  n ≤ 8 exact + closed-form geometric tail (8·55 = 440 > 390 = max evaluated
  x, the registered closure; sensitivity worlds recompute the cutoff by the
  same rule). Tail-closure spot-check: m = 8 vs direct m = 12 EXACTLY equal
  on T ∈ {90, 240} × c ∈ {−30, 0, +30}.
- **Arm S** (confirmation, seed 20261317): one 5,010,000 s timeline (77,110
  attempts, 74,037 successes), 200,000 viewer + 200,000 halt samples, CRN
  across the T grid; draw sentinel exact (954,220 = 2·77,110 + 2·200,000 +
  2·200,000). **Agreement gate PASS on all 14 cells**: worst FALSESTALE
  |diff| 3.87e-4 (T = 90) ≤ 1/1000; worst LAT |diff| 0.0685 s ≤ 5 s.
- **Stability** (seed 20261318, fresh 1,010,000 s timeline, 20k + 20k):
  Feas_S = {150, 180, 240} — FS(120) = 199/20000 ≈ 0.00995 > 1/200,
  FS(180) = 3/10000 ≤ 1/200, LAT(240) ≈ 204.97 ≤ 240, LAT(300) ≈ 264.97 > 240
  — same ruling class through both twin evaluators (Fraction comparisons vs
  pure-integer cross-multiplication).
- Hand fixture 6/6 exact; zero-disturbance identity exact (FALSESTALE ≡ 0,
  LAT(T) = T − 59/2, age uniform {0..59}); exact monotonicity both arms;
  renewal-reward ≡ age-table complement identity (P(A ≥ x) = E[(G−x)⁺]/E[G])
  exact on the grid; per-c splits recombine exactly; per-leg draw sentinels
  exact; seeds constructed = {20261317, 20261318, 20261319} only — aux
  20261320 NEVER constructed (asserted).
- Byte identity: stdout + results.json byte-identical across two full process
  runs by external diff (no wall-clock in any output); stdout sha256
  8c0090b3…, results sha256 6f231a8e…; ~3 s/run; CPython 3.11 pinned, asserted.

## Reporting-only legs (cannot flip the decision)

Sensitivity (Arm A exact; seed-20261319 Arm-S confirmations at 20k samples each):

| world | Feas | FS(120) | FS(150) | FS(180) |
|-------|------|---------|---------|---------|
| primary | {150, 180, 240} | 9.80e-3 | 1.97e-3 | 4.83e-4 |
| jitter_tight {58..62} | {150, 180, 240} | 6.30e-3 | 8.47e-4 | 2.53e-4 |
| jitter_loose {45..90} | {150, 180, 240} | 1.26e-2 | 3.77e-3 | 8.29e-4 |
| f_low 1/100 | **{120, 150, 180, 240}** | 2.23e-3 | 2.93e-4 | 2.81e-5 |
| f_high 1/10 | {180, 240} | 2.89e-2 | 9.08e-3 | 3.43e-3 |
| c_zero {0} | {150, 180, 240} | 7.79e-3 | 1.13e-3 | 4.26e-4 |
| c_wide {−120..+120} | **{240}** | 1.49e-1 | 5.15e-2 | 8.79e-3 |

**Two pre-registered straddles fired, named (axis iv material, reporting-only —
the decision stays APPROVE per the registration's own "reporting legs CANNOT
flip"):** (1) **f_low** flips the second APPROVE conjunct — at f = 1/100 the
2-cycle threshold T = 120 is already honest (Feas gains 120), exactly the
knife the registration's liveness note named ("whether the second APPROVE
conjunct survives the f = 1/100 world"); the default's honesty *premium* over
120 s exists only at miss rates ≳ 1/100. (2) **c_wide** flips the first
conjunct — at ±120 s clock offsets 180 ∉ Feas (only 240 survives), so the
default leans on the ±30 s offset width. Both widths are INVENTED-but-pinned
(no live datapoint anywhere in the fleet); the registration's named one-day
push-timestamp log measures jitter and f directly once FLAG 1 goes live.

Burst leg (Markov P(fail→fail) = 1/2, P(ok→fail) = 1/48, stationary miss rate
exactly 1/25; Arm S only, seed 20261319): FS(120) ≈ 0.0261, FS(180) ≈ 0.0161 —
burstiness raises FALSESTALE at every grid T vs the primary (0 direction
violations), the registered direction confirmed: **the i.i.d.-failure
assumption is what this APPROVE leans on** — correlated deploy-window outages
at the same stationary miss rate would push T = 180 OUT of the honest band
(0.0161 > 1/200). Named, not hidden.

## Boundaries (registered)

Invented-widths (jitter, f, c carry no live datapoint — sweeps bracket scale,
not shape; the one-day timestamp log is the pre-priced calibration);
independence (the burst bracket above); pinned-world (60 s target worlds only;
halt-while-503 already honest by the lane's no-last-good-cache rule; a
producer stamping fresh `generated_at` on stale content defeats ANY age rule
by construction — producer-honesty question, out of scope); on-demand
refreshes only shorten gaps (modeled world conservative against APPROVE's
first conjunct, direction stated).

## Conformance disclosures

- **Indicator boundary convention**: the registered renewal-reward numerator
  E[(G − (T − c))⁺] equals P(A ≥ T − c) on the integer floor-age lattice —
  exactly the registered STRICT rule P(A + c > T) when the viewer instant is
  uniform in REAL time (the registration's "uniformly random instant"; the
  perceived-age-exactly-T atom has measure zero). Arm S therefore counts
  STALE iff floor_age + c ≥ T; the integer-strict variant count (>) is
  committed alongside in results.json. No off-by-one; the registered formula,
  the strictness pin, and both arms are mutually consistent under this
  reading (fixtures.json `indicator_equivalence_note`).
- **LAT age convention**: the registered floor-age pmf P(A = a) = P(G > a)/E[G]
  verbatim (the zero-disturbance identity LAT(T) = T − 59/2 pins it).
- **Amendment, pre-acceptance**: the first process run failed 2 of its own
  UNREGISTERED reporting-output self-checks — this build's descriptive claim
  that P(L > 300) ≡ 0 for T ≤ 300 was over-strong (L ≤ T − c_lo = T + 30, so
  the guarantee holds only for T ≤ 270; the T = 300 cell is honestly 0.1126).
  The check bound and the fixture's descriptive note were corrected; no
  registered constant, gate, or decision number changed (Arm A is seedless
  and the Arm S draw stream was untouched — decision tables identical before
  and after). The corrected pipeline's first complete run is the accepted run.
- The 1,010,000 s reporting-leg timeline length is an implementation pin
  (registration pins sample counts and the stability timeline), disclosed in
  fixtures.json.

## Consequence (per the registration's APPROVE branch)

The contract line drops its "default suggestion" hedge and gains its measured
basis, routed lane-side per Q-0260 (sim-lab edits no mineverse files):
"3 missed cycles ≈ 180 s" becomes "180 s (false-stale ≤ 1/200 of healthy
loads — measured ≈ 1/2070 — mean outage detection ≤ 240 s — measured
≈ 145 s — at the pinned model)", and the eventual FLAG-1 frontend badge ships
that constant with this citable curve. Attached pins every consumer inherits:
the i.i.d.-failure lean (burst leg), the f ≳ 1/100 premium boundary (f_low
straddle), and the ±30 s offset lean (c_wide straddle).

Run: `python3 sims/verdict-056-snapshot-stale-threshold/stale_sim.py`

# REPORT — VERDICT 065: the illustration gate (PROPOSAL 054)

**Ruling: NULL** on the pre-registered axis (v) — *"arm disagreement — the
agreement gate fails (a defect is the finding, no ruling)"* — under the
registration's own gate architecture (*"Gates (run invalid on any failure)"*).
Registered rules applied in order: **REJECT was checked FIRST and its
arithmetic shape HOLDS on Arm A's exact numbers** — Δ(cell) ≥ $100 in **9 of
9** cells (7 required) with the winning family **AI-led in every cell** — but
three registered validity gates fail at the registration's own pinned
constants, so no ruling can issue and the registered NULL axis (v) carries
the outcome with the defects as the finding. All three defects are
REGISTRATION defects, proven exactly in-sim, not run or arm defects: the
arms agree statistically on every leg, and every decision-bearing leg passes
the registered gate with headroom. The drafter's disclosed decision numbers
ALL reproduce from scratch exactly.

Registration: `## PROPOSAL 054 · 2026-07-14T01:51:37Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main ca71997, landed via PR #382; idea
doc `ideas/venture-lab/illustration-gate-park-vs-pilot-2026-07-14.md`; claim
idea-engine PR #384, `control/claims/2026-07-14-verdict-065.md`). Fully
hermetic — every constant pinned in fixtures.json (committed BEFORE the
runner), zero repo/network reads at verdict time; the venture-lab pin
d93aee5 is citation-only.

## The question and the model (registered, hermetic)

K = 5 kids titles, horizon H = 365 days, pilot window W = 90. The line is
DEAD w.p. π_L (every title's daily sale probability p = 0) else ALIVE with
each title's p i.i.d. from ω = (7/20, 3/10, 1/5, 1/10, 1/20) over
P_live = {1/60, 1/30, 1/10, 1/3, 1}; μ_live = 143/1200 exactly. Per
published title per day at most one sale, Bernoulli(f·p) — f = 1
commissioned, f = q = 7/10 AI — at royalty r = 2097/500 exactly
(= 60%·$12.99 − $3.60, the plan's own §1 unit economics; F2 recompute
passes with |r − 419/100| = 1/250). AI tool cost a = 30 total; per-AI-title
removal risk ρ = 1/20 at publish. Grid: π_L ∈ {3/4 SKEPTIC, 1/2 NEUTRAL,
1/4 HOPEFUL} × c ∈ {1500, 3245, 4950}, row-major. Seven policies: PARK ·
COMM-ALL · COMM-PILOT-SALE · COMM-PILOT-EV · AI-ALL · AI-PILOT-SALE ·
AI-PILOT-EV. Δ(cell) = max non-PARK NET − NET(PARK). Bands fixed before any
code: REJECT (Δ ≥ m = 100 in ≥ 7/9 cells AND one family, checked FIRST) →
APPROVE (Δ < 100 in ≥ 7/9 and ≥ 2/3 SKEPTIC, stability reproducing) → NULL
(six registered axes).

## Arm A — the exact 9 × 7 NET table (dollars; exact Fractions in results.json)

| cell | PARK | COMM-ALL | COMM-PILOT-SALE | COMM-PILOT-EV | AI-ALL | AI-PILOT-SALE | AI-PILOT-EV |
|---|---|---|---|---|---|---|---|
| SKEPTIC c=1500 | 0 | −7271.97 | −2692.52 | −1454.39 | **+121.64** | −1089.78 | +0.33 |
| SKEPTIC c=3245 | 0 | −15996.97 | −6023.17 | −3199.39 | **+121.64** | −2485.85 | +0.33 |
| SKEPTIC c=4950 | 0 | −24521.97 | −9277.46 | −4904.39 | **+121.64** | −3849.93 | +0.33 |
| NEUTRAL c=1500 | 0 | −7043.95 | −3885.05 | −1408.79 | **+273.28** | −2149.56 | +30.66 |
| NEUTRAL c=3245 | 0 | −15768.95 | −8801.33 | −3153.79 | **+273.28** | −4941.70 | +30.66 |
| NEUTRAL c=4950 | 0 | −24293.95 | −13604.93 | −4858.79 | **+273.28** | −7669.85 | +30.66 |
| HOPEFUL c=1500 | 0 | −6815.92 | −5077.57 | −1363.18 | **+424.91** | −3209.33 | +60.98 |
| HOPEFUL c=3245 | 0 | −15540.92 | −11579.50 | −3108.18 | **+424.91** | −7397.56 | +60.98 |
| HOPEFUL c=4950 | 0 | −24065.92 | −17932.39 | −4813.18 | **+424.91** | −11489.78 | +60.98 |

Δ is row-constant and column-independent (F5d asserted structurally —
V_cont < min c in every registered world, so no reachable posterior ever
rationally commissions): Δ_SKEPTIC = **778482513/6400000 ≈ $121.64**,
Δ_NEUTRAL = **874482513/3200000 ≈ $273.28**, Δ_HOPEFUL =
**2719447539/6400000 ≈ $424.91** — argmax **AI-ALL** in all 9 cells, family
AI-led. The named reporting numbers: c* = V_cont = μ_live·r·(H−W) =
**1099527/8000 = $137.440875** (a factor ~11 under the committed $1,500
floor — the commission channel is dead at every reachable posterior, the
drafter's disclosed sharpening confirmed); AI-ALL break-even alive-shares
**16000000/74652501 ≈ 0.214326** (margin-clearing) and
**16000000/323494171 ≈ 0.049460** (EV-zero) — the drafter's ≈0.2143/≈0.0495
re-derived; commit probabilities given alive P1 = 0.908679 (COMM pilots),
(1−ρ)·Pq with Pq = 0.842150 (AI pilots), × α per row, EV-gated pilots
exactly 0; per-p conditional revenue split (given alive) = 7/143, 12/143,
24/143, 40/143, 60/143 over p = 1/60 … 1; the seat's own hedge AI-PILOT-EV
sits at exactly **10482513/32000000 ≈ +$0.33** in the SKEPTIC row (the
drafter's disclosed curiosity, confirmed).

Margin sweep (registered band edges): the REJECT-shape holds at m = 25
(9/9) and **fails at m = 400** (3/9 — only the HOPEFUL row clears; the
margin-thin axis is live inside the sweep, reported).

## The three registered-gate defects (each proven exactly, each an anomaly)

**A1-F5b — the registered F5(b) theorem is FALSE at the pinned constants.**
"Every policy's NET non-decreasing in the alive share 1−π_L" fails for both
SALE pilots: NET(COMM-PILOT-SALE) and NET(AI-PILOT-SALE) are strictly
DECREASING in α at every pinned c. Proof from the registration's own pins:
F3 forces NET(COMM-PILOT-SALE) = −c at α = 0, and the registered
V_cont = $137.44 < min c = $1,500 makes the sale-triggered commit
value-destroying, so more alive ⇒ more committing ⇒ lower NET. Exact
α-coefficients (B + P1·(K−1)(V_cont−c)): c=1500 → ≈ −$4770.29, c=3245 →
≈ −$11113.24, c=4950 → ≈ −$17311.29 (AI-PILOT-SALE ≈ −$4841.68 /
−$10717.68 / −$16394.71; exact Fractions in results.json). The drafter's
own disclosed sharpening ("the information channel is dead at the committed
prices") IMPLIES this failure — the registered theorem presumes committing
is good news while the registration itself proves the commit channel
strictly dominated. Decision numbers untouched: Δ rides AI-ALL, which is
monotone.

**A2-F5c — the registered a=150 reverse assertion fails at every grid row.**
Under per-title accounting (a_line=150, a_pilot=30 — the only evaluable
reading, disclosed in the fixture), AI-ALL still beats AI-PILOT-EV at every
grid cell: by exactly 10482513/8000000 ≈ **$1.31** at SKEPTIC (≈$122.62
NEUTRAL, ≈$243.93 HOPEFUL). The dominance DOES break by design below the
exact accounting threshold α* = **240000000/970482513 ≈ 0.24730** — a
knife-edge 0.0027 BELOW the SKEPTIC row's α = 1/4. The "breaks BY DESIGN"
existence reading holds; the registered grid-row reverse assertion does not.

**A3-agreement-gate — the registered Arm-S gate is unsatisfiable at the
registered N.** The gate (|ArmS − ArmA| ≤ $10 absolute on every (cell,
policy) with ≥ 4·SE headroom pre-checked per leg; ≤ $25 stability) cannot
be met by the two SALE-pilot policies: their per-scenario net carries a
±(K−1)(c−V_cont) commit jump (≈$5,450 at c=1500 up to ≈$19,250 at c=4950),
so the per-scenario SD reaches ≈$9,000 and 4·SE at N = 200,000 reaches ≈$80
≫ $10. The headroom pre-check fails on exactly the 18 SALE legs
(measured); the arms themselves are statistically consistent (|dev| ≤ 4·SE)
on the main and stability legs (per-leg detail in results.json), and every
decision-bearing AI-ALL leg passes the registered $10 clause with headroom.
Satisfying the registered $10 clause on the SALE legs would need
N ≈ (4·9000/10)² ≈ 12.9M scenarios/cell (65× the registered budget) — the
gate constant, not the arms, is the defect. This is the registered NULL
axis (v) firing exactly as registered: "the agreement gate fails (a defect
is the finding, no ruling)".

## Decision evaluation (registered order, twin evaluators agree everywhere)

1. Validity (the registration's own precondition — "run invalid on any
   failure"): **FAILS** on the three registered-gate defects above (each a
   registration defect, none a run/arm defect). A ruling issued despite a
   failed registered gate would make the registered axis (v) unreachable
   dead text; the registration pre-committed "a defect is the finding, no
   ruling".
2. REJECT (checked FIRST): arithmetic shape **holds** — over-margin 9/9
   (7 required), family AI-led in every over-margin cell — reported, not
   ruled.
3. APPROVE: arithmetically unreachable (over/under disjoint).
4. **NULL — binding axis (v)**; the other five axes evaluated honestly:
   belief-conditional NO (9/9 at m=100), cost-conditional NO (Δ
   column-independent), family-split NO (AI-led everywhere), margin-thin
   YES-inside-sweep (m=400 → 3/9, reported), sensitivity-straddle YES
   (three named worlds land 6/9, below).

Stability leg (seed 20261354): reproduces the classification through both
twin evaluators — its MC Δ-estimates land the same REJECT-shape (9/9,
AI-led) and the same validity flags land the same NULL(v).

## Arm S (seeded, common random numbers) and the reporting worlds

Main leg seed 20261353, N = 200,000/cell; stability 20261354 at
20,000/cell; reporting 20261355 at 20,000/cell/world; aux 20261356
constructed last and never read (fresh-state asserted). Pinned draw order
per scenario: line-state → K p-draws → K removal coins → K·H day-by-day
trials (title-major); dead lines short-circuit at one draw; draw sentinels
exact on every leg (total draws ≡ n_dead + n_alive·(1 + 2K + K·H); coins ≡
AI-published titles; trials ≡ published-title-days under the CRN union).
Measured on the accepted run: main leg — abs-clause breaches 5/63
(all SALE legs; worst |dev| $44.43 at NEUTRAL/4950/AI-PILOT-SALE), headroom
failures exactly 18/63 (the SALE legs; worst 4·SE $84.94 at
NEUTRAL/4950/COMM-PILOT-SALE), statistically consistent 63/63; the
decision-bearing AI-ALL legs pass the registered clause with headroom
(worst |dev| $3.04, worst 4·SE $4.71 vs the $10 gate). Stability leg —
abs breaches 8/63, headroom failures 18/63 (worst 4·SE $268.44), 63/63
statistically consistent; its Δ-estimates land ≈ $124.97 / $272.87 /
$421.34 (exact rationals in results.json) — the same 9/9 AI-led shape. All
12 reporting worlds statistically consistent on all 63 legs each.

Reporting worlds (Arm A exact + Arm-S consistency), over-margin counts at
m = 100: H180 = **6/9**, H730 = 9/9, K7 = 9/9, ω′-uniform = 9/9,
q=1/2 = **6/9**, q=9/10 = 9/9, ρ=0 = 9/9, ρ=1/10 = 9/9, a=0 = 9/9,
a=150 = **6/9**, W45 = 9/9, W180 = 9/9. The three 6/9 worlds all lose
exactly the SKEPTIC row — the belief-conditional pattern the drafter named;
a=150 and q=1/2 match the drafter's disclosure, and **H180 = 6/9 is an
additional undisclosed 6/9 world found by this run** (the drafter only
stated H730 pushes rows further over — true, but silent on H180).

## Drafter-reference comparison (never gated)

Every disclosed decision number reproduces from scratch EXACTLY: Δ_SKEPTIC
778482513/6400000, Δ_NEUTRAL 874482513/3200000, Δ_HOPEFUL
2719447539/6400000, argmax AI-ALL 9/9, REJECT-shape 9/9, V_cont $137.44
(exact 1099527/8000), the +$0.33 SKEPTIC hedge (exact 10482513/32000000),
the a=150 and q=1/2 worlds at 6/9, the break-even alive-shares ≈0.2143 /
≈0.0495. No drafter arithmetic error in any disclosed decision-bearing
number. The three registration defects (A1/A2/A3) live entirely in the
GATE layer — the V064 genus ("gate-side and reporting-side pins get less
drafting scrutiny than decision numbers"), third consecutive instance.

## Boundaries (registered, carried verbatim)

- **Sale-rate model**: no live kids-line sales datapoint exists anywhere in
  the fleet (the catalog has zero published kids titles — the harvested
  gate itself); P_live and ω bracket scale, not measured shape; the
  ≤1-sale/day Bernoulli cap is GENEROUS TO PARK (direction stated) — the
  REJECT-shaped substance is robust to it.
- **Invented AI parameters**: q, ρ, and the a-accounting carry no
  measurement; two named legs (a=150, q=1/2) land 6/9 — the genuine
  fragility axes, plus this run's H180 finding.
- **Unsettled-IP**: §3's own caveat — inspection-decidable, never
  simulated; the REJECT-shaped reading is deliberately a SHADOW PRICE
  (parking pays Δ ≈ $122–$425/cell for IP cleanliness) so the seat's
  reservation is priced, not overruled.
- **Horizon-bounded park**: parking's option value beyond H unmodeled; the
  H730 leg brackets the direction (rows push further over).

## Reproducibility

One command, no flags, stdlib-only, hermetic (reads only its own
fixtures.json). Arm A platform-independent exact rationals, alone
decision-bearing. CPython 3.11 pinned and asserted. stdout + results.json
byte-identical across two full process runs by external sha256:
run-stdout sha256
1029325187e11abfb873bf84899d3dc2c05e5f8eb30db4f383110656104fd03b,
results.json sha256
0cda3630d93f6a14f360af662b7d2d62db360c4574ecfcde7cb95753d5f7eed7;
~4m09–4m16 per run (pure CPython, ~3.8 billion pinned-order RNG draws
through the day-by-day trial lattice); self-checks 620 passed, 4 recorded
failures — all four being the registered-gate defects themselves (F5b
registered form, F5c registered reverse form, the main and stability
agreement gates), itemized in stdout and results.json.

## The five validity questions

- **COMPARABLE**: every decision number is an exact Fraction under the
  registration's own pinned frame; fixtures.json copied verbatim from the
  PROPOSAL 054 block / idea doc and committed BEFORE the runner, with every
  fixture-level choice disclosed in the fixture first; all 9 cells share
  one kernel and pinned draw order by construction.
- **UNCORRUPTED**: bands, grid, seeds, draw order, evaluation order (REJECT
  first) all registered before this session existed; git trail card →
  fixtures → runner + accepted run; no fix-forwards — the first complete
  run of the registered pipeline is the accepted run; no registered
  constant was altered to rescue the gate — the gate was allowed to fail
  and the failure IS the finding, per the registration's own axis (v).
- **ROBUST**: the classification is not knife-edge — the three gate defects
  are structural (a false theorem, a false grid-row assertion, an
  information-theoretically unsatisfiable tolerance), not statistical luck;
  the REJECT-shaped substance clears its band 9/9 vs 7 required with the
  stability leg reproducing through twin evaluators; the named knife-edges
  (the $1.31 A2 miss, the m=400 sweep flip, the three 6/9 worlds) are
  disclosed, not smoothed.
- **REPRODUCIBLE**: byte-identical two-process runs by external sha256;
  seeds 20261353–356 the only four RNGs constructed, pinned order, aux
  never read; new registry high-water 20261356.
- **LIMITS**: model-true under the registered frame, not a market
  measurement — the four registered boundaries above; the pre-priced free
  live probe (one pilot title's 90-day KDP dashboard read, the V049
  pattern) measures the real p row at zero new tooling and supersedes the
  invented rows wherever it disagrees.

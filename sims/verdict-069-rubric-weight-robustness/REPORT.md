# VERDICT 069 — REPORT — rubric weight-robustness (INTAKE 058)

**Class: REJECT** (pre-registered rules applied in order: REJECT → INVALID →
APPROVE → NULL; REJECT checked FIRST fires on all three conjuncts).

Source: idea-engine `## PROPOSAL 058 · 2026-07-14T04:10:35Z · status: sim-ready`
(idea-engine PR #395 @ main 76aca1e; idea doc
`ideas/venture-lab/rubric-weight-robustness-2026-07-14.md`). Instrument under
price: venture-lab's shipped kill-rule-intake rubric — weights 35/20/15/15/15,
bands "below ~3.0 = do not build; 3.0–3.5 = borderline, tight budget only;
above 3.5 = best available" — applied to the published 7 × 5 score table of
`docs/products/ideas-2026-07-13-night.md` blob `aa09f12` @
`a9e202d69433dc69623a78dd3164ac4689d7c8f0` (re-verified at intake via GitHub
MCP at the pinned commit: returned blob SHA matches, all seven score rows +
weights line + band sentence verbatim; the runner reads none of it).

## Reproducibility

- `SELF-CHECKS: 64 passed, 0 failed`, exit 0, ~2.5 s/run, stdlib-only,
  hermetic (reads only its own `fixtures.json`), CPython 3.11 pinned and
  asserted.
- Byte-identical across two full process runs by external sha256:
  `run-stdout.txt` = `208a85da61ae1f3e2b1298a0b2a70cf4703f8e27c787e41da600c80b8203b505`,
  `results.json` = `ea0cffc2196f45c762acbc668d111d05ba44f1b717b9aacde765d03c40d5e58a`.
- Seeds: 20261369 main / 20261370 stability / 20261371 reporting — the ONLY
  three RNGs constructed (asserted, pinned order); aux 20261372 NEVER read
  (asserted at RNG construction and at end-of-run).
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run.

## Per-conjunct results (registered order)

**REJECT conjunct 1 — p̂(1/10) main ≥ 1/10 — FIRES.** p̂(1/10) = 22455/100000
= 0.224550 on the main leg (seed 20261369, N = 100,000; ≈ 94 SE above the 1/10
edge at σ ≈ 0.00132). At ±10% multiplicative weight jitter, more than one draw
in five re-partitions the batch.

**REJECT conjunct 2 — x\*₁ ≤ 1/20 — FIRES.** Arm A exact: x\*₁ = 1/27 ≈
±3.70%, crossing DOWN through the 3.5 edge — the batch's sole above-band
concept (AI Novella Production Kit, published total 141/40 = 3.525) loses
"best available" inside ±3.7% of weight jitter.

**REJECT conjunct 3 — x\*₆ ≤ 1/20 — FIRES.** x\*₆ = 1/47 ≈ ±2.13%, crossing
DOWN through the 3.0 no-build edge (Agent Session Retro Kit, 121/40 = 3.025)
— the global minimum, exactly as the registered F3 identity requires
(1/50 < 1/47, recomputed exact).

## The exact critical-radius table (Arm A, seedless Fractions)

| # | Concept | Published total | x\* exact | x\* ≈ | Crossed edge |
|---|---|---|---|---|---|
| 1 | AI Novella Production Kit | 141/40 = 3.525 | **1/27** | ±3.70% | 7/2 (down) |
| 2 | Fiction Vetting-Packet Kit | 131/40 = 3.275 | 9/37 | ±24.3% | 7/2 (up) |
| 3 | Pre-Registered Experiment Kit | 13/4 = 3.25 | 1/3 | ±33.3% | 7/2 (up) |
| 4 | Trilingual Edition Factory | 127/40 = 3.175 | 7/41 | ±17.1% | 3 (down) |
| 5 | Dead-Session Recovery Playbook | 31/10 = 3.10 | 1/11 | ±9.1% | 3 (down) |
| 6 | Agent Session Retro Kit | 121/40 = 3.025 | **1/47** | ±2.13% | 3 (down) |
| 7 | Provenance-Freshness Checker Kit | 11/4 = 2.75 | 1/5 | ±20.0% | 3 (up) |

Every drafter-disclosed exact value reproduced from scratch (compared, never
gated): all seven x\* Fractions match digit-for-digit. Five of seven concepts
tolerate ≥ ±9% jitter — the fragility is a property of the two knife-edge
rows, not of rubric arithmetic as such.

## The flip curve (Arm S) and attribution

| x | p̂ main (N = 100k) | p̂ stability (N = 20k) | \|Δ\| (gate 1/50) |
|---|---|---|---|
| 1/50 | 0.000000 (forced — F3) | 0.000000 | 0 |
| 1/20 | 0.060070 | 0.060150 | 0.00008 |
| **1/10** | **0.224550** | 0.223800 | 0.00075 |
| 1/5 | 0.356310 | 0.357250 | 0.00094 |

Cross-seed agreement gate (1/50 absolute) passes at every radius with ≥ 20×
margin. Falsifiability behaved exactly as registered: p̂(1/20) ≈ 0.060 sits
BELOW the 1/10 REJECT line — a decision radius one grid step tighter would
have landed in the p-straddle NULL, so the bands genuinely discriminate.

Per-concept attribution (main leg, draws in which concept i's band changed):
at x = 1/10 — concept 6: 22,455 · concept 1: 9,474 · concept 5: 3 · others 0;
the flip count equals concept 6's count exactly, i.e. in this sample every
draw that re-partitions the batch at ±10% moves concept 6 (concept 1's
crossing region measured ENTIRELY inside concept 6's here — the drafter's
"almost entirely" sharpening, slightly stronger in-sample). At x = 1/5 the
nesting breaks as the mechanics predict: flips 35,631 > concept 6's 35,574
(57 draws flip via other concepts alone; concept 1: 25,938 · concept 5:
5,166 · concept 4: 12).

## Reporting legs (seed 20261371 — never decision-bearing)

Dirichlet-mechanism worlds, w′ ~ Dirichlet(κ·w₀) via `gammavariate`
renormalized, N = 20,000 each: κ = 100 → flip 0.437900; κ = 400 → flip
0.338850 (attribution led by concepts 6 and 1 in both, same ordering as the
uniform box). Both worlds flip MORE than the ±10% uniform box — the
mechanism-conditional NULL axis is NOT triggered (a promoted REJECT could
only be confirmed, not flipped, by the Dirichlet reading; direction
REJECT-ward, reported). Band-edge convention note: exact-edge hits observed
= 0 across all legs and radii (measure-zero, as registered).

## Gates

F1 identity (w₀ sums to 1; all seven recomputed totals equal the published
Fractions; baseline partition = B₀) · F2 critical-radius self-consistency at
±1/1000 (range strictly inside below, crossed edge inside above, all seven;
probe legality 953/47000 > 0 recomputed) · F3 zero-flip at x = 1/50
(deterministic — 0 band changes over all draws and concepts on BOTH MC legs:
120,000 draws × 7 concepts) · F4 containment (every sampled total within the
exact 32-vertex range + 1e−9, all uniform legs, all radii) · F5 hand world
(total 7/2; range [69/20, 71/20] at x = 1/10, exact) · F6 battery
(core-random() sentinels exactly 5·N per uniform (seed, radius) leg;
5-per-draw gammavariate call count on Dirichlet legs; twin independently-
written decision evaluators agree on headline AND stability; byte-identical
double run by external sha256; CPython 3.11 asserted) · cross-seed gate —
ALL GREEN. The stability leg reproduces REJECT through both twin evaluators.

## Boundaries (as registered)

- **Reweighting-only:** per-criterion scores held fixed at their published
  values; score noise is a different, unmodeled fragility channel (direction
  stated: it cannot make a weight-fragile partition robust).
- **Mechanism:** the multiplicative-uniform box is the pinned decision
  mechanism because it admits exact vertex arithmetic; the Dirichlet worlds
  bracket mechanism-dependence as reporting; the exact x\* table is
  radius-free and carries the finding on its own.
- **Editorial overlay:** the batch's actual BUILD/PARK/KILL verdicts already
  override raw bands on named qualitative axes — this verdict prices the
  ARITHMETIC layer the rubric text itself defines, and the REJECT consequence
  RATIFIES the override instinct with numbers rather than fighting it.
- **Batch scope:** the verdict is about THIS table's partition; the
  transferable deliverable is the x\* function (`critical_radius` in the
  runner, ~20 lines, exact, zero MC cost on any future weighted-rubric table).

## Consequence (pre-registered REJECT branch — routing is the manager's per Q-0260)

Paste-ready structured choice for the manager, recommendation first
(Q-0263.2): **(a, recommended — zero new data, the sim ships the function)**
future batch docs report each concept's exact critical radius x\* beside its
total (one extra column; the exact function is committed in this dir) and any
verdict with x\* ≤ 1/20 carries a "band-fragile" flag: decide it on the stated
qualitative axes, not the band — which is what THIS batch already did
informally (it killed three ≥ 3.0 concepts on named fatal axes and called its
own 3.525 top scorer "borderline-band territory"; this verdict gives that
instinct its measured basis: ±3.70% and ±2.13%). **(b)** keep the bands
as-is, now explicitly accepting the headline BUILD line is band-fragile at
±3.7%. **(c)** re-cut the bands — an owner/lane intent call, never ruled by
fiat here. APPLICATION GUARD (two conditions): (1) conditions on the published
7 × 5 table, the 35/20/15/15/15 weights, and the 3.0/3.5 band sentences @
`a9e202d` — an amended rubric, re-scored batch, or changed band text means
re-run, not reuse; (2) conditions on the batch's pre-evidence state (0 organic
sales as of 2026-07-13) — real sales evidence re-anchors banding to measured
rates and stales the partition-as-instrument premise.

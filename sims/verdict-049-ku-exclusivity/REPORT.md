# VERDICT 049 — KU-exclusivity fork: REPORT

> **Status:** `finalized` — INTAKE 038 / VERDICT 049, serving idea-engine
> `control/outbox.md` — `## PROPOSAL 038 · 2026-07-13T15:36:37Z · status:
> sim-ready`. Claim: idea-engine PR #321 → main 3f1c955. Numbering P038 →
> V049 per the +11 offset map (the number RESERVES, never the position).

## Question

Does venture-lab PUBLISHING-PLAN.md §4's blanket OWNER-ACTION default
"KDP Select: **Yes**" (@ venture-lab 79a1987) survive the plan's OWN verified
royalty arithmetic under a pinned per-reader-contact buy-vs-borrow mixture —
i.e. does KU enrollment beat going wide in more than a minority of swept
cells, both arms priced at the SAME price per cell?

## Pre-registration

`fixtures.json` committed BEFORE the runner (PR #100 git trail; every
constant copied verbatim from the PROPOSAL 038 block — the source of truth
over the disclosed-condensation idea doc; venture-lab itself walled this
session, all plan rows pinned via the block @ 79a1987):

- **Titles:** ultramarine 27,865 words / the-weigh-house 36,434;
  KENP = round(words/190) → 147 / 192 (gate-checked).
- **Royalty:** roy(p) = 7/10·p − 15/100 for $2.99 ≤ p ≤ $9.99 (flat 1 MB
  delivery fee pinned inside the 15/100), else 35/100·p. Anchor identities
  gated as pinned Fractions: roy(0.99) = 693/2000 = $0.3465 ·
  roy(2.99) = $1.943 · roy(4.99) = $3.343 · roy(6.99) = $4.743.
- **Grid (288 cells, pinned loop order title, b, rt, rate, p):**
  b ∈ {1/2, 1, 2, 4} (β = b/(1+b)) · rt ∈ {7/20, 3/5, 17/20} ·
  rate ∈ {$0.0035, $0.0045, $0.0055} · p ∈ {$0.99, $2.99, $4.99, $6.99};
  the plan's own Tier-1 price $4.99 is THE flagged 72-cell default slice.
- **Arms (per-contact revenue, same p per cell; PR = rate·KENP·rt):**
  KU = (1−β)·((1−κ)·roy(p) + κ·PR) + β·PR with κ = 1/5;
  WIDE = (1−β)·roy(p) + β·γ·roy(p) with γ = 3/20.
  Δ = KU − WIDE; W = #{Δ > 0}/288.
- **Arm A:** exact closed-form Fractions, ALL 288 cells, seedless.
  **Arm S:** seeded MC, M = 50,000 per (cell, arm); read-through per borrow
  ~ Uniform(rt − 3/20, rt + 3/20), mean exactly rt (fractional-page payout a
  disclosed simplification). Seeds 20261289 main / 20261290 stability
  (half-M = 25,000, must reproduce the ruling) / 20261291 reporting /
  20261292 aux (registered, never drawn). New registry high-water 20261292.
- **Decision rule (evaluated IN ORDER; the rules decide, not the drafting
  prediction of W = 101/288):**
  1. REJECT iff W < 2/5 of 288 (= 115.2), stability-reproduced;
  2. APPROVE iff W ≥ 4/5 of 288 (= 230.4) AND KU wins ≥ 4/5 of the 72
     $4.99-tier cells (= 57.6), stability-reproduced;
  3. NULL otherwise.

## Run

`python3 sims/verdict-049-ku-exclusivity/ku_exclusivity_sim.py` — exit 0,
**SELF-CHECKS: 31 passed, 0 failed**, ~37 s; stdout + results.json
**byte-identical across two full process runs by external diff** (no
wall-clock in any output); cpython-3.11 pinned and asserted; stdlib-only,
hermetic (reads only its own fixtures.json). **No fix-forwards: the first
complete run of the registered pipeline is the accepted run.**

### Gates (all green)

- **Agreement (the ≥ 2.5σ familywise rule, z = 5 pre-checked in the fixture
  BEFORE any draw):** per-cell |KU_S − KU_A| and |WIDE_S − WIDE_A| within
  z·σ_exact/√M on all 288 cells, main AND stability legs (max |z| observed:
  2.755 main / 3.147 stability / 2.606 reporting — all under the z = 5 line).
- **Exact-identity controls:** (κ=0 ∧ γ=0) → Δ = β·rate·KENP·rt EXACTLY and
  KU wins every cell; (rate=0 ∧ κ=0 ∧ γ=0) → arms identical, Δ ≡ 0 — both
  on all 288 cells.
- **Monotonicity:** Δ nondecreasing in rate and in rt per cell; W
  nonincreasing in γ across its pair (150 ≥ 101 ≥ 78).
- **Sentinels:** main 72,000,000 draws = 288·50,000·(3+2) exact; stability
  36,000,000; reporting 36,000,000 (both exact); aux seed never drawn;
  draws counted by a counting-RNG subclass, not assumed.
- **Twin evaluators:** independently written Fraction-comparison and
  pure-integer decision evaluators agree on the exact table and both seeded
  legs.

## Ruling: REJECT

Evaluated in the pre-registered order:

1. **REJECT fires.** W = **101/288 ≈ 0.3507 < 2/5** — exact Arm A count,
   zero sampling error (the decision W; runner pin disclosed in
   fixtures.json). Stability-reproduced: the seed-20261290 half-M leg lands
   W_S = 104/288 → reject; the main seed-20261289 leg (a stricter runner
   pin) lands W_S = 102/288 → reject. Margin to the 115.2 line: 14+ cells,
   not knife-edge.
2. APPROVE (not reached, and would not fire: 101 < 230.4; $4.99 tier
   4/72 ≈ 0.056 < 57.6/72).

**The drafting arithmetic was reproduced EXACTLY**: W = 101/288 overall,
4/72 at $4.99, 72/72 at $0.99, per-b shares 19/72 → 32/72 rising in b —
all four disclosed drafting numbers landed as measured.

### The decision table's shape (Arm A exact)

- **Per-price-tier wins:** $0.99: **72/72** · $2.99: 25/72 · $4.99: **4/72**
  · $6.99: **0/72**. The price-tier axis is the dominant fork exactly as
  registered: KU pays where the 35% band makes sales cheap ($0.99, roy =
  $0.3465), and never at $6.99 (roy = $4.743).
- **Per-b wins:** 19/72 (b=1/2) · 23/72 · 27/72 · 32/72 (b=4) — rising in b,
  never reaching half even at b = 4.
- **Per-rt:** 24/96 · 33/96 · 44/96; **per-rate:** 29/96 · 33/96 · 39/96;
  **per-title:** ultramarine 46/144 · the-weigh-house 55/144 (the longer
  book monetizes borrows better; KENP 192 vs 147).
- **b\* crossover (72 rows, committed in results.json):** 40/72 rows have NO
  swept b at which KU wins — including 15/18 rows at $4.99 and 18/18 at
  $6.99; all 18 $0.99 rows win from b = 1/2 up.
- **Δrel = KU/WIDE − 1:** overall median −0.118 (quartiles −0.196 / +0.294);
  $4.99 tier median −0.174 (max +0.205); $6.99 all-negative (max −0.003);
  $0.99 median +1.255 (max +6.3, the high-b/high-rate/high-rt corner).

### Reporting-only legs (seed 20261291; cannot flip the decision — did not)

- **γ sweep {1/20, 3/20, 3/10}:** W = 150 / 101 / 78. The lower endpoint
  (few borrowers buy anyway when wide) is the ONE swept coordinate that
  would carry W past the 2/5 line (150/288 ≈ 0.52 → NULL territory) — γ is
  the named weakest joint, and the sweep brackets exactly as disclosed.
- **κ sweep {1/10, 1/5, 7/20}:** W = 118 / 101 / 91 (all REJECT-side).
- **Words-per-KENP {150, 190, 230}:** W = 125 / 101 / 89 (all REJECT-side).
- **File-size {1/2, 1, 5/2} MB:** W = 100 / 101 / 112 (all REJECT-side; the
  fee only moves 70%-band cells, and a heavier file HELPS KU by taxing the
  sale).
- **MC spot-replication** (seed 20261291, M = 50,000, the κ/γ endpoints on
  the affected arm over the flagged 72-cell $4.99 tier — a runner design
  choice disclosed in fixtures.json): agreement green, max |z| 2.606.

## Validity

- **COMPARABLE:** every decision number is exact Fraction arithmetic from
  constants copied verbatim from the proposal block; both arms priced at the
  same p per cell; the royalty function is the plan's own verified structure,
  anchor-gated.
- **UNCORRUPTED:** fixtures before runner (git trail); bands and evaluation
  order registered before any code; 31 self-checks 0 failed; no
  fix-forwards; the full 288-cell table ships including every KU-favoring
  cell.
- **ROBUST:** REJECT clears its line by 14+ cells (101 vs 115.2), exact;
  stability (fresh seed, half-M, full-grid resimulation) reproduces; twin
  evaluators agree; no reporting sweep except γ's lower endpoint even
  approaches the line, and that endpoint is reporting-only by registration.
- **REPRODUCIBLE:** one command, no flags, stdlib-only, hermetic;
  byte-identical stdout + results.json across two full process runs by
  external diff; cpython-3.11 pinned; seeds 20261289–92 strictly above the
  P037 high-water 20261288; new high-water 20261292.
- **LIMITS (pre-registered boundaries, verbatim-faithful):** γ and κ are
  invented, pinned, the disclosed weakest joints — NO fleet datapoint on
  borrow-vs-buy behavior exists (zero titles published); the sweeps bracket
  scale, not shape, and the γ lower endpoint is the one bracketing value
  that would cross the REJECT line if it were decision-bearing (it is not).
  Reader-contacts held EQUAL across arms by construction — KU
  visibility/also-bought boost and wide multi-store reach BOTH out of scope;
  the metric prices royalty mechanics, not discoverability. The KENP rate is
  Amazon-set and monthly-varying (the grid brackets the historically cited
  range); words-per-KENP is Amazon-computed per book, pinned at 190;
  fractional-page payout is a stated simplification. Static single-title,
  single-90-day-term economics — series spillover, term renewal, mid-term
  price switching out of scope. Per-reader-contact RELATIVE units only,
  never absolute earnings (the plan's §6 "base case ≈ $0" forecast
  discipline and Q-0259 r.4 untouched). Live KDP dashboard data supersedes
  wherever it disagrees.

## Consequence (pre-registered REJECT arm)

The blanket "KDP Select: **Yes**" is struck from the recommendation posture —
enrollment becomes a per-title decision gated on the verdict's b* crossover
table, the quantified reason riding the manager sweep (Q-0260 — this repo
never edits venture-lab files) to the §4 rows, vetting packets, and
OWNER-QUEUE before any enrollment click. Enrollment/publishing stays an
explicit OWNER action, never an agent action, on every outcome.

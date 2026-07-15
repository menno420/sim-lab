# VERDICT 086 — REJECT — one knob printed twice (P073, write-contract rate-tier degeneracy)

**Ruling: REJECT** — per the pre-registered rule applied in the registered
order REJECT → INVALID → APPROVE → NULL (REJECT evaluated FIRST and fires
on all three clauses; twin independently-written evaluators agree
REJECT/REJECT; every decision number an exact integer or Fraction).

141 self-checks, 141 passed, 0 failed; exit 0 on the accepted run;
~0.3 s/run; stdlib-only; hermetic (reads only its own fixtures.json);
CPython 3.11 pinned and asserted. stdout + results.json byte-identical
across two full in-repo process runs by external diff + sha256:

- `results.json` sha256 `f8a2f527d70b48131f6d7313b3f71cee0c7b6841f908db9665cb4f0af7fd71ce`
- `run-stdout.txt` sha256 `83280c95647696b3a631d0f5dac5b85b75e49d6f451f6931c492fea742865d2a`

**Anomaly census: EMPTY.** Every disclosed numeral in the P073
registration — decision AND reporting — reproduced exactly from scratch:
the maxima census (60/70/69/70/20/10/90), both excess ratios and band
margins, the three dead-tier contacts, the separating triple, the full
grid rows, the granularity triple, the pencil world, the five small
worlds, AND the seeded Arm-R reporting landing (main 23270 admitted /
26730 rejected of 50,000; stability 9183/10817 of 20,000; both
worst-window contacts exactly 60; obedient client exactly 3600). The
drafter's NO-DERIVED-LITERALS claim ("every numeral RAN") survived a
zero-trust re-derivation intact — the V085 anomaly-census discipline ran
honestly and found nothing to pin.

## The decision clauses (all exact)

**R1 — DEAD TIER (fires).** At the committed pair (B, w, S, T) =
(10, 10 s, 60, 60 s):

- uniform sliding: N_slide(60) = B·⌈60/w⌉ = **60 = S exactly** — no
  separating schedule exists (a registered margin-0 contact);
- uniform aligned-fixed: max admits in an aligned minute = **60 = S
  exactly**; the 61-request probe confirms the 61st is rejected by the
  BURST tier first and the sustained counter caps at 60 (second
  registered contact);
- uniform token-bucket pair: the sustained bucket (cap 60, refill 1/s)
  never drops below **exactly 50 tokens** under adversarial
  burst-admissible traffic over 600 s (exact invariant
  sustained − burst ≥ S − B, confirmed by greedy trace in both arms and
  by exhaustive search on the scaled 2/6-cap world) — dead by a
  49-token margin over the 1-token threshold.

**R2 — FORK (fires).** The burst tier alone, in the worst 60 s span:

- fixed windows, adversarial alignment: N_fixed_adv(60) = **70** —
  excess **7/6** of the sustained promise, margin ×**10/9** over the
  21/20 band;
- token bucket: N_bucket(60) = **69** — excess **23/20**, margin
  ×**23/21**; closed-interval endpoint convention **70** — the pair
  {69, 70} both clear the band (convention-robust);
- boundary straddle: N_fixed_adv(2) = **20 = 2B exactly** (sliding
  allows 10).

**R3 — LATTICE POINT (fires).** B·T = S·w = **600 = 600**; under sliding
the sustained tier is redundant iff B·⌈T/w⌉ ≤ S and the committed pair
sits at **equality (60 = 60)**; one step off the boundary the structure
changes: at S = 50 the separating schedule EXISTS (the committed witness
— six 10-bursts at t = 0, 10, …, 50 — is burst-sliding feasible and
admits 60 > 50), and at w = 7 redundancy dies by divisibility alone
(B·⌈60/7⌉ = **90 > 60**). The S = 70 world carries the third registered
contact (fixed 70 = 70, doubly slack).

APPROVE's witnesses were live and did not fire: no sliding separating
schedule exists at the committed pair, and neither alternative maximum is
≤ S (70 > 60, 69 > 60). No NULL axis triggered: no band-straddle (both
disciplines clear 21/20), no law failure (every closed form met its
independently-written twin exactly, everywhere), no convention fragility
(granularity triple (60, 70, 69) identical at δ ∈ {1, 1/2, 1/5}; bucket
endpoint pair both over the band), no twin disagreement.

## Margin ledger (C5)

| comparison | value | band | margin |
|---|---|---|---|
| R2 fixed excess | 7/6 | 21/20 | ×10/9 ≈ 1.111 |
| R2 bucket excess (half-open) | 23/20 | 21/20 | ×23/21 ≈ 1.095 |
| R2 bucket excess (closed exhibit) | 7/6 | 21/20 | ×10/9 |
| R2 straddle | 20 = 2B | exact equality BY LAW | — |
| R1 bucket dead margin | min level 50 | ≥ 1 | 49 tokens (the fat margin) |
| R3 w = 7 clause | 90 vs 60 | strict | +30 |
| R3 S = 50 witness | 60 vs 50 | strict | +10 |

Registered margin-0 contacts (the head's THESIS, knife-edges BY
CONSTRUCTION, gated as equalities): sliding 60 = S; aligned-fixed
60 = S; the S = 70 world's fixed 70 = 70; the R3 lattice equality
B·⌈T/w⌉ = S (60 = 60). Gate: no UNregistered decision comparison sits at
margin 0 — green.

## Gates

- **F1 — model identities**: green. B·T = S·w = 600; the partition bound
  (closed form = partition count; exhaustive small worlds respect it);
  admitted-equals-schedule accounting inside every witness simulation;
  the shim Retry-After formula reproduced verbatim and probed at known
  values (reject at 10-full → Retry-After 7 at now = 3.2; floor-at-1 at
  now = 9.999).
- **F2 — the three structure theorems**: green at every cell, exact
  contacts (60, 60, min-level 50), maxima (70, 69/70, 20), excesses 7/6
  and 23/20, redundancy law == sliding scan over the full 4×4 grid,
  separating triple (committed none / S = 50 witness / S = 70 none),
  w = 7 world 90.
- **F3 — census anchors**: green, all verbatim — N_slide(60) = 60,
  N_fixed_adv(60) = 70, N_fixed_aligned(60) = 60, N_bucket(60) = 69
  (closed-interval 70), N_fixed_adv(2) = 20, N_slide(2) = 10, margins
  ×10/9 and ×23/21, bucket min 50 over 600 s, w = 7 cell 90, grid rows
  (20, 10) → 120/140/138 (every S live) and (5, 10) → 30/35/34 (every S
  dead), obedient client 3600/3600 s.
- **F4 — the hand world**: green. B = 2, w = 2 s, L = 4 s → sliding 4
  (closed form, twin, AND the exhaustive 3⁴-schedule search),
  fixed-adversarial 6, bucket 5 — all three by pencil, matching both
  arms.
- **F5 — degeneracy and convention controls**: green. Granularity
  invariance (60, 70, 69) at all three δ in BOTH arms; bucket endpoint
  pair {69, 70} both ≥ 21/20·S; grid-wide ordering
  N_slide ≤ N_bucket ≤ N_fixed_adv at every (B, w) × L cell; five
  exhaustive small-world checks of the sliding law — (6,2,2) → 6,
  (7,3,2) → 6, (5,5,3) → 3, (8,4,1) → 2, (9,3,3) → 9, all exactly
  B·⌈L/w⌉.
- **F6 — battery**: green. Arm B reproduces every Arm-A number exactly
  (greedy-witness + matching-upper-bound maxima, independent alignment
  enumeration, independent bucket trace, independent separating search);
  twin decision evaluators agree REJECT/REJECT; Arm-R draw-count
  sentinels (50,000 and 20,000 expovariate draws asserted); per-trace
  worst-window theorem check ≤ 60 with the contact AT 60 observed on
  both seeds; presentation seed 20261652 read by the presentation leg
  only; aux seed 20261653 never read (constructor registry
  `[20261650, 20261651, 20261652]`); byte-identical double run.

## Arm R (reporting-only, no statistical gate)

| trace | seed | events | admitted | rejected | worst 60 s window |
|---|---|---|---|---|---|
| main | 20261650 | 50,000 | 23,270 | 26,730 | **60** (contact) |
| stability | 20261651 | 20,000 | 9,183 | 10,817 | **60** (contact) |

Both Poisson streams (offered 2/s) through the verbatim shim limiter
touch the T1 theorem contact exactly — the worst trailing 60 s
admitted-window is 60 on both seeds, never 61. The deterministic
obedient Retry-After client (retry exactly at the header value) admits
**exactly 3600 in 3600 s** — long-run rate exactly 1/s = the sustained
rate: the shim's `Retry-After` formula is an exact sustained-compliance
governor, the committed pair's one genuinely working part (stated back
to the lane per the registration).

## Falsifiability (was real)

- **S = 50 world**: one committed-constant step down and the sustained
  tier is LIVE under every discipline — the separating witness exists
  even under sliding; APPROVE's first clause verifiably flips.
- **w = 7 world**: redundancy dies by divisibility alone (90 > 60) —
  the T1 theorem is lattice-conditional and says so.
- **discipline-pin world**: one sentence pinning "sliding" in the
  contract would moot R2's fork and degrade the finding to dead-ink
  only (a named reporting demonstration, never a decision code path —
  C4).

## Model boundary (declared, the P024 discipline)

Worst-case adversarial maxima (a contract is a worst-case instrument —
typical traffic is Arm-R reporting, never decision); slotted time with
the granularity-invariance gate; the three-discipline universe
(sliding/fixed/bucket — GCRA named a follow-up); per-(suid, guild_id)
key isolation. The T1/T3 theorems are exact facts about the committed
constants under the model; the T2 excesses additionally lean on
worst-case and say so.

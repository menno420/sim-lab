# VERDICT 094 — REJECT — the dedupe with a rotating alibi (P081, guard-fires-dedupe-regime-cliff)

**Ruling: REJECT** (the shipped comment's comfort sentence — "a burst
larger than this simply dedupes less" — is wrong as doctrine: a
bounded-tail dedupe over an append-only log is a REGIME SYSTEM, not a
graceful degrader — the 200-line scan cap is a CLIFF whose leak wears a
rotating alibi (F = 200 leaks 0/run forever, F = 201 leaks 1/run forever,
the leaked identity rotating with period F/gcd(F, F−200) through a finding
population that never changed), the dedupe-exempt verdict rows consume
scan capacity and COMPOUND (one allowlist suppression per run ramps a
boundary-clean burst to 19/run and sustains exactly 14/run — 13× the
one-for-one intuition), the steady record rate is NON-MONOTONE in check
cadence (a 601 s checker writes exactly 1200/601 ≈ 2× more per day than a
600 s one), and "bounded scan" bounds parses while the whole-file read
bill grows quadratically exactly in the regime where the leak fires) —
per the pre-registered rule applied in the registered order REJECT →
INVALID → APPROVE → NULL (REJECT evaluated FIRST and fires on all four
clauses R1–R4; twin independently-written decision evaluators agree
REJECT/REJECT over an ENUMERATED boolean input set; every decision number
a seedless exact integer census, orbit, or closed-form identity).

52 self-checks, 52 passed, 0 failed; exit 0 on the accepted run (the
first complete in-repo run of the committed pipeline — rehearsed to green
on untracked outputs before the runner commit: **52/52 on the FIRST
rehearsal run, ZERO rehearsal fixes**, byte-identity also rehearsed; the
pre-fixture prototype pinned two realization details — the leak-phase
peak definition for (200,1) and the rotation-leg horizon — both disclosed
in fixtures.json before the runner existed; zero fix-forwards after the
runner landed); ≈ 12.6 s/run (the Arm-R legs dominate); hermetic —
shipped-algorithm replay head, stdlib only, zero repo/network reads at
verdict time (the model replays three PINNED source behaviors read from
~150 lines of vendored source at the grounding HEAD — the
source-semantics NULL axis priced exactly that, and did not fire: every
census derived from the pinned semantics landed on the registered
values). CPython 3.11 pinned and asserted (Arms A/B are seedless exact
integer arithmetic, platform-independent; only reporting-only Arm R and
the presentation shuffle touch the pinned minor's `random` module).
stdout + results.json byte-identical across two full in-repo process
runs by external diff + sha256:

- `results.json` sha256 `6de930da49233256c5e755093b45fdd5bcd3753038c422aab32acd169d0cb8a8`
- `run-stdout.txt` sha256 `d35c62b26deab0d1f2828e4299fb78745fc9b05e5d791e69617aed5bada97884`

**Anomaly census (structured by disclosure coverage, the V087–V093
convention): 98 compared-and-matched, 0 mismatched, 6 vacant.** Every
registered numeral in the P081 registration — decision AND reporting —
reproduced exactly from scratch: the renewal day table 131/121/97/81/73/
144/131/97/73 (replay == closed law on all 9 cadences, twice — shipped
and keyed arms), the witness pair p(600) = 1200 / p(601) = 601 with rate
ratio exactly 1200/601, the V = 0 leak row 0/0/0/0/1/50/100/200 with the
(200, 201) margin-0 pair, the rotation periods 201/5/3/2 with first
repeats at run 2 + period (F = 201 observed at run 203) and the F = 250
blocks 0–49/50–99/100–149, the saturated law min(F, F−200+V) on all 13
qualifying cells (the (400,V) row 201/205/250/400; (300,50) = 150), the
boundary pair ((398,1) constant 199/run, (397,1) alternating 198/199),
the (200,1) orbit (prefix [200, 1, 2, …, 11], leak-phase peak 19 first at
run 20, tail mean exactly 14 — sum 560 over runs 41–80 — total 1025 vs
the naive 79), (200,5) → 30/run, (200,50) → exactly 100/run, (250,50) →
the exact 2-cycle {100, 150} with total 9850, (1,50) → period 4, all 13
registered compounding totals at their cells (969/2236/7771 @ F = 199;
2315/7850 @ F = 200; 1068/2389/7890 @ F = 201; 4260/5125/9850 @ F = 250;
8057/8685 @ F = 300), the breathing orbit 201, (1,1,199)×7, 1, 1 (total
1610) with its window-off collapse to 1/run, the read censuses (13,000
lines / 2,000 parses with the last run alone reading 2,200; breathing
20,122 / 4,600) with the scan-off control at leak 0, the design point
(re-runs append exactly 0 at F ∈ {1, 50, 200}), the repair censuses
(S′ = 1000 grid all-zero + F = 1001 → 1/run; keyed index zero-leak at
every (F,V) with renewal preserved; scan-off leak 0), the V ≥ S
saturation control (leak == F ×8), the order-flip invariance, the
batch-split census ({50, 75} split vs {50} one-batch — the one-batch
convention measured LOAD-BEARING), the naive-ts fail-open control
([200, 200, 200] vs [200, 0, 0]), and both Arm-R preview triples
((19,095, 400, 21,187,561) @ 20261718 and (7,653, 400, 8,512,842) @
20261719) with draw counts exactly 80,000 / 32,000. The six honest
vacancies (sim-chosen realizations of shape-registered slots, disclosed
in fixtures.json, ledgered as vacancy-derived disclosures — never match
claims): the Arm-R census field definitions behind the preview triples
(leak-regime trace = fire appends after run 1 > 0; max burst includes
run 1; total appends = fire appends, verdict rows excluded), the 8
order-flip probe cells (the F grid at V = 5; V ∈ {1, 50} also swept as
extra coverage), the rotation-leg horizon (R = period + 3), the naive-ts
probe cell (200, 0, c = 1, R = 3), the presentation-shuffle target, and
the six unregistered small-cell compounding totals (F ∈ {1, 50} —
reported as color, not gated).

## The decision clauses (all exact)

- **R1 — RENEWAL NON-MONOTONICITY (fires).** A single persisting finding
  re-records with period exactly p(c) = c·(⌊600/c⌋+1): the day-horizon
  (86400 s) replay counts equal the closed law on all 9 cadences —
  131/121/97/81/73/**144**/131/97/73 at c = 60/120/300/540/600/**601**/
  660/900/1200. The witness pair: p(600) = 1200 but p(601) = 601 (one
  line: ⌊600/601⌋ = 0), so nudging the cadence from 600 s to 601 s
  multiplies the steady record rate by exactly **1200/601 ≈ 1.9967** —
  checking less often writes almost twice as much, and the grid maximum
  is the second-slowest checker.
- **R2 — THE CLIFF + THE ALIBI (fires).** With V = 0 the steady per-run
  leak is exactly **max(0, F − 200)**: F = 200 appends once and then
  NOTHING forever; F = 201 leaks 1/run FOREVER (margin-0 pair). The
  leaked records are not "the same one slipping through": the leaked
  identity ROTATES in blocks of F − 200 with period exactly
  **F/gcd(F, F−200)** — 201/5/3/2 at F = 201/250/300/400, first repeats
  at run 2 + period on all four cells, the F = 250 blocks
  0–49/50–99/100–149 enumerated. Ledger archaeology reads rotating
  finding sets — fabricated churn out of a population that never changed.
- **R3 — COMPOUNDING DISPLACEMENT (fires).** On the saturated region
  (V ≥ 200 or F ≥ 2(200−V)) the steady leak is exactly
  **min(F, F−200+V)** on every qualifying cell, with the boundary pair
  exact ((398,1) constant 199/run, (397,1) already non-constant). Below
  it there is no constant law — there are exact orbits: at (200, 1) —
  a boundary-clean burst plus ONE allowlist suppression per run — the
  leak ramps 1, 2, 3, … to a peak of **19/run at run 20**, then sustains
  at tail mean exactly **14/run**, total **1025** over runs 2–80 where
  one-for-one intuition predicts **79** (≈ 13×); (200, 50) settles at
  exactly **100/run** (2× the naive 50); (250, 50) locks the exact
  2-cycle **{100, 150}** (total 9850); (1, 50) re-records a single
  persisting finding every **4th run** by pure line displacement.
- **R4 — BREATHING + THE READ BILL (fires).** At (201, 300) the two
  bounds interact into the exact period-3 orbit **201, (1, 1, 199) × 7,
  1, 1** — total 1610 over 24 runs where "leaks 1/run" predicts 224 —
  and the window-off control (W → ∞) collapses it to exactly 1/run,
  proving the 199-bursts are EXPIRY, not the line bound. The read bill:
  on the (400, 0, 60, 11) leak scenario the whole-file read costs
  exactly **13,000 cumulative lines** (closed quadratic sum; the last
  run alone reads 2,200 lines to scan 200) against exactly **2,000 JSON
  parses**; the breathing scenario pays 20,122 for 4,600; the scan-off
  control (parse everything, window kept) leaks exactly 0 on the same
  scenario — the cap defends a cost the code has already paid, and buys
  the leak in exchange.
- **APPROVE (does not fire, and is arithmetically excluded):** the
  shipped algorithm does NOT reproduce the keyed-index arm's zero-leak
  census (the (201, 0) cell leaks 1/run against the keyed arm's 0) and
  the renewal rate is NOT monotone non-increasing (73 → 144 at the
  600 → 601 step) — computed honestly; the pre-registered rule fired
  REJECT on the computed inputs. The TRUE SENTENCE survives (checked,
  not assumed): at the fix's own design point (F ≤ 200, V = 0, c = 60)
  re-runs append exactly 0 — the dedupe works exactly as designed there,
  and the verdict prices the doctrine, not the design point.

## Twin arms and contacts

Arm A (seedless faithful tail-slice replay of the pinned mechanism —
append-only `(key, t)` ledger, one batch-start scan per fire batch,
whole-file read counted, parse capped at the last 200 lines, strict-`>`
age boundary, verdict rows first/always/keyless — plus the closed forms
on their proven domains) and Arm B (INDEPENDENTLY-WRITTEN
depth-arithmetic twin over a differently-shaped log: no line list, a
global line counter plus per-key last-append registers, visibility by
depth-from-end arithmetic) are tied through the four typed must-equal
contacts: **C1** replay day counts == the closed renewal law on all 9
cadences, **C2** V = 0 steady leak == max(0, F−S) ×8 AND rotation
first-repeat == 2 + F/gcd(F, F−S) ×4, **C3** Arm B == Arm A per-run
sequences EXACTLY on all 20 compounding cells × 80 runs and all 13
saturated cells (and, extra coverage, on the whole 40-cell grid and the
breathing orbit), **C4** measured lines-read == the closed quadratic sum
(13,000) AND parse calls == Σ min(len, S) (2,000). Arm R (seeds
20261718/20261719, REPORTING-ONLY, no statistical gate) reproduced both
registered preview triples exactly under the registered draw-order
grammar (4 `randint` draws per trace in order F, V, c, R), with the 4N
draw-count sentinel asserted (80,000 / 32,000) and in-process double-run
determinism verified per seed; presentation seed 20261720 read by the
presentation leg only; aux seed 20261721 never read.

## Margin ledger (typed — the V086 convention)

- **Exact-equality cells BY REGISTRATION (the head's own subject):** the
  day table (9 cells, saturated by the closed law — no room to move),
  the leak row (== max(0, F−200), an integer identity), the rotation
  periods and block censuses (pinned by the stable-order convention and
  saying so), the saturated-law cells (== min(F, F−200+V) on the proven
  domain), the compounding orbit anchors (prefix/peak/tail-mean/totals —
  eventually-periodic integer sequences, matched term-exact), the
  breathing orbit (term-exact ×24), the read/parse censuses (closed
  integer sums), the repair censuses (all-zero grids + margin cells).
- **The margin-0 pairs, registered AS margin-0:** (200, 201) at the
  cliff — one finding of headroom; (398, 397) at the saturated-law
  boundary — one finding; (600, 601) at the window — one second,
  carrying the ratio 1200/601 (margin 599/601 above 1). Each pair's two
  sides landed on opposite registered behaviors, which is the claim.
- **The strict inequalities:** peak 19 vs the naive 1 (margin 18); total
  1025 vs 79 (ratio 1025/79 ≈ 13); breathing total 1610 vs 224. All
  integer comparisons, nowhere near equality.
- No UNregistered decision comparison sits at margin 0; every clause
  input is an exact integer census, a term-exact orbit, or a closed-form
  identity on its stated domain.

## Falsifiability (was real)

The source-semantics axis was live: one misread of the strict-`>` age
boundary, the lines-not-records slot accounting, or the suppressed-first
call order moves the day table AND the breathing orbit together — the
sim re-derived both from the pinned behaviors and landed on every
registered value, so the pin survived fresh eyes. The compounding axis
was live and is the head's own disclosed history: the drafter's FIRST
registered law (one-for-one displacement, leak = V) was falsified live
at drafting and is carried in the registration as the falsified arm —
Arm B's independently-written replay existed to catch exactly an
implementation-artifact orbit, and it agreed with Arm A term-exact on
all 33 gated cells. The monotone world (slower checkers write less) is
refuted by a gated full-day replay, not a citation — the 601-cadence
cell was derived by both the replay and the closed law. A single moved
census — one leak-row cell, one orbit term, one read count — would have
killed its clause and the registered rule would have issued INVALID or
the honest NULL axis; none moved.

## Scope boundaries (stated, per the registration)

- **The source-semantics boundary:** the model replays three PINNED
  behaviors read from ~150 lines of vendored source at the grounding
  HEAD (idea-engine @ c750904, kit v1.17.0), not the function object
  itself; the ruling binds the shipped write-side dedupe as pinned.
- **The convention boundary:** uniform integer-second cadence, stable
  finding order, empty-start ledger, one-batch-per-run — each named with
  its role; leak COUNT laws are order-free, identity censuses (rotation
  blocks) are order-pinned and say so; the one-batch convention is
  measured LOAD-BEARING (split census {50, 75} vs {50}) and registered,
  so no reader inherits it silently; orbits are stated from the pinned
  empty start with steady-state claims as tail behavior (runs 41–80).
- **The scope boundary:** the ruling binds the shipped write-side dedupe
  at kit v1.17.0; multi-guard batch structure, hook-surface fires, and
  CI-derived rows are named follow-ups, none in scope.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

Verdict consumer: substrate-kit — the lane owns both constants, the
scan, the verdict-row exemption, and the comment whose sentence this
head priced. Per the proposal's pre-registered REJECT consequence,
paste-ready structured choice, recommendation first (Q-0263.2):
**(a, recommended)** document + relocate, zero new state: replace the
"simply dedupes less" comment with the three-sentence regime disclosure
(the leak law max(0, F−S); the shared verdict-capacity budget — exempt
rows displace keyed rows and compound; the cadence non-monotonicity —
keep check cadence clear of W from above) and raise
`_GUARD_FIRES_DEDUPE_SCAN` above the fleet's realistic worst per-run
finding count (the S′ = 1000 relocation is priced here: zero behavior
change on every enumerated F ≤ 400 world, read bill unchanged — one
constant, one comment); **(b)** the keyed `{key: last_append_ts}` index
sidecar — leak 0 at every (F, V), verdict displacement structurally
gone, renewal semantics preserved (both enumerated here), at the price
of one new mutable fail-open state surface whose corruption story must
degrade to the pre-fix no-dedupe; **(c)** drop the line cap, keep the
window with early exit on the first out-of-window record — burst-regime
leak 0 (the scan-off control IS this arm, enumerated at leak 0), at the
price of unbounded in-window parses, noting the whole-file READ is
already paid today. Known co-consumers: the B3 fire/FP-rate analytics
(the leak inflates per-guard fire LEVELS by exact computable factors
while the rotating alibi makes raw row counts read as churn; ratios
survive, levels do not), the KF-11 tracked-ledger commit loop (every
leaked line is a tracked-file diff — the stop-hook-telemetry treadmill's
supply side), every adopter's failsafe cadence choice (the practical
rule from R1: keep check cadence well clear of W from above), and — the
transferable audit — every fleet surface deduping by bounded tail scan
over an append-only log: compute worst burst size against the scan
bound BEFORE trusting the window, count exempt rows against the same
budget, and check the cost the cap actually bounds. Named follow-ups,
none in scope: multi-guard batch structure, hook-surface fires,
CI-derived rows.

## Seeds

Arm-R reporting-only: 20261718 (N = 20,000), 20261719 (N = 8,000) under
the registered draw-order grammar (per trace exactly 4 `randint` draws
in order F ∈ [1, 400], V ∈ [0, 8], c ∈ [60, 1200], R ∈ [2, 12]; one
`random.Random` per seed; draw-count sentinels asserted); presentation
shuffle 20261720 (presentation leg only); aux 20261721 reserved and
never read. Seeds 20261714–717 are P080/V093's registered set —
untouched; the allocation started at 20261718 per the v093 heartbeat
baton, and the next free block starts at 20261722. No seed touches any
decision arm.

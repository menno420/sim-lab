# VERDICT 100 — ACCEPT — a lower-mean-damage build wins at some target HP because hits-to-kill is a discrete breakpoint comb, not a mean race (P087, htk-breakpoint-variance-comb)

**Ruling: ACCEPT** (no failing gate — all of R1→R2→R3→R4 hold). Source proposal
header cited verbatim: `## PROPOSAL 087 · 2026-07-16T18:59:26Z · status: sim-ready`
(idea-engine PROPOSAL 087, registered spec `htk-breakpoint-variance-comb`); P087 → V100
under the constant **+13** PROPOSAL↔VERDICT offset, confirmed at sim-lab
`docs/current-state.md` § Verdict-numbering map.

On the pinned world (single target with HP H, dies when cumulative realized damage ≥ H;
HTK = number of hits to reach H with floor ≥ 1; cohort C=4000 trials per seed, seeds
S=[1,2,3,4,5], HP grid H∈{80,100,140,300,500}) two equal-cost builds that differ ONLY in
per-hit damage distribution — **TIGHT ~ Uniform[100,110]** (mean 105) vs **WILD ~
Uniform[75,165]** (mean 120) — are compared on **mean HTK (lower = better)** under COMMON
RANDOM NUMBERS: per trial a single stream of MAX_HITS=25 uniforms u_i∈[0,1) is drawn from
ONE `random.Random(seed)`, and BOTH builds map the SAME u_i to their own [lo,hi] via
damage = lo + u_i·(hi−lo) (identical per-(trial,hit) uniforms across builds); the same
seed's stream is re-drawn fresh per seed so the identical trials are evaluated at every H.
The paired diff is d_s(H) = meanHTK_WILD − meanHTK_TIGHT (positive ⇒ TIGHT wins), with
mean_d(H) over the 5 seeds, sigma(H) = stdev(d_s, ddof=1)/sqrt(5), and
margin(H) = |mean_d|/sigma. P087 pre-registered an ACCEPT rule requiring ALL four gates
R1–R4. The measured run ACCEPTS: at H=100 mean HTK TIGHT < WILD for all five seeds at
**74.90σ** (R1), at H=500 mean HTK WILD < TIGHT for all five seeds at **110.60σ** (R2),
every realized HTK ≥ 1 and mean HTK monotone non-decreasing in H for both builds (R3), and
the comb sign vector **[+,+,−,+,−]** matches the registration while the variance-free
control HTK=ceil(H/mean) has WILD ≤ TIGHT at every single H (R4). The measured means
reproduce the proposal's disclosed dry-sim calibration — TIGHT [1, 1, 2, 3, 5]; WILD
[1.0547, 1.2785, 1.7193, 3.0413, 4.6905]; R1 ≈74.9σ; R2 ≈110.6σ — from an INDEPENDENT
re-implementation of the funnel. Both independently-written decision evaluators agree
ACCEPT/None on the measured gate outcomes.

8 self-checks, 8 passed, 0 failed; exit 0 on the accepted run; < 1 s/run; hermetic —
CPython 3, stdlib only, zero repo/network reads at verdict time. The two builds share one
per-seed per-trial uniform stream (TIGHT and WILD see identical draws — a per-build matrix
fingerprint is compared against the seed's canonical fingerprint and a divergence raises
`SystemExit("NULL: builds saw different draws")`), and the seed-1 H=100 first-20-trial
uniform streams with HTK-under-both-builds are committed as the fixture and re-verified
each run. stdout + results.json byte-identical across two full in-repo process runs by
external diff + sha256:

- `results.json` sha256 `6e848ccc43a4f4f5428cefb35d3f1f4efbf7c3299332720fc41707a2460ac40d`
- `run-stdout.txt` sha256 `493559db5443140b8d525bcb779f272475d1b4c02bf3ac1635fa5cd5bfffb880`
- `fixtures.json` sha256 `f392ea2c500a9ba0d1e0b9d079d8efb76d17ffab2495f755e4678ced24677086`

## The decision clauses (all measured)

- **R1 reach regime @ H=100 — PASS.** At H=100 TIGHT kills in exactly 1 hit every trial
  (its minimum damage 100 ≥ 100), so meanHTK_TIGHT = 1.0000; WILD's first hit lands in
  [75,100) with probability (100−75)/(165−75) = 25/90 ≈ 0.278, forcing a 2nd hit, so
  meanHTK_WILD ≈ 1.2785. Per-seed WILD−TIGHT diffs = [+0.2785, +0.2730, +0.2920, +0.2705,
  +0.2785] (all strictly positive ⇒ TIGHT wins for ALL five seeds); mean_d = +0.27850,
  sigma 0.003718 → paired margin **74.90σ ≥ 3**. The lower-mean build wins outright at a
  breakpoint just above TIGHT's guaranteed one-shot.
- **R2 saturation reversal @ H=500 — PASS.** At H=500 TIGHT needs exactly 5 hits every
  trial (4 hits reach at most 440 < 500; 5 hits reach at least 500), so meanHTK_TIGHT =
  5.0000; WILD's higher mean (120) and the law of large numbers over 5 hits let it kill in
  ≈4.69 hits on average, so meanHTK_WILD ≈ 4.6905 < 5. Per-seed WILD−TIGHT diffs =
  [−0.3012, −0.3175, −0.3130, −0.3060, −0.3098] (all strictly negative ⇒ WILD wins for ALL
  five seeds); mean_d = −0.30950, sigma 0.002798 → paired margin **110.60σ ≥ 3**. Far from
  a breakpoint the mean advantage dominates and the higher-mean build wins.
- **R3 well-posedness — PASS.** Every realized HTK across all builds/HP/seeds is ≥ 1
  (measured minimum HTK = 1; the first hit always deals positive damage), and mean HTK is
  monotone non-decreasing in H for BOTH builds: TIGHT [1.0000, 1.0000, 2.0000, 3.0000,
  5.0000] and WILD [1.0547, 1.2785, 1.7193, 3.0413, 4.6905] — neither curve dips as HP
  rises. Well-posed HTK, no negative or zero kills.
- **R4 comb + control — PASS.** (R4a) The sign of mean_d(H) over the grid is
  **[+, +, −, +, −]**, matching the registered comb exactly: TIGHT wins at H∈{80,100,300}
  and WILD wins at H∈{140,500}, sign-alternating as HP sweeps the breakpoint lattice. (R4b)
  The deterministic control HTK = ceil(H/mean) — TIGHT ceil(H/105), WILD ceil(H/120) —
  yields WILD ≤ TIGHT at every H ([1≤1, 1≤1, 2≤2, 3≤3, 5≤5]); with variance removed the
  higher-mean WILD is never worse, so every stochastic TIGHT win (H∈{80,100,300}) is proven
  VARIANCE-driven, not mean-driven — the mechanistic core of the head.
- **ACCEPT fires.** All four gates hold in the registered order R1→R2→R3→R4, so the
  pre-registered rule (ACCEPT iff R1∧R2∧R3∧R4) returns ACCEPT with no failing gate. The
  REJECT world was genuinely reachable (a comb that failed to alternate, or a control in
  which WILD's ceil ever exceeded TIGHT's, would fail R4) and did not come live.

## Twin evaluators and agreement

Two independently-written decision evaluators score the SAME measured gate outcomes:

- **Evaluator A (if-chain):** applies R1→R2→R3→R4 as a short-circuit if-chain, returning
  the ruling token and the first gate whose predicate is False → **ACCEPT / None**.
- **Evaluator B (table-driven):** an independently transcribed table of (gate, outcome)
  rows, scanned in the registered order for the first False → **ACCEPT / None**.

Both agree on BOTH the ruling token (ACCEPT) AND the first-failing-gate reason (None),
checked by the self-checks `twin_evaluators_agree_verdict` and
`twin_evaluators_agree_reason`. The seed-1 H=100 first-20-trial uniform streams and HTK
match the committed fixture (`fixture_matches_committed`), the five per-seed uniform
matrices are distinct and each shared identically by both builds
(`common_random_numbers_shared_per_build_and_H`, `per_seed_matrices_distinct`), every
realized HTK ≥ 1 (`every_realized_htk_ge_1`), the cohort size is C=4000
(`cohort_size_is_C`), and the HP grid spans the reversal (`hp_grid_spans_reversal`) — 8/8.

## Margin ledger (typed, per-H mean HTK over S=[1,2,3,4,5]; lower = better)

| H    | TIGHT mean | WILD mean | mean_d (W−T) | sigma    | margin (σ) | sign |
|------|------------|-----------|--------------|----------|------------|------|
| 80   | 1.0000     | 1.0547    | +0.05470     | 0.001099 | 49.75      | +    |
| 100  | 1.0000     | 1.2785    | +0.27850     | 0.003718 | **74.90**  | +    |
| 140  | 2.0000     | 1.7193    | −0.28070     | 0.002820 | 99.54      | −    |
| 300  | 3.0000     | 3.0413    | +0.04135     | 0.001027 | 40.28      | +    |
| 500  | 5.0000     | 4.6905    | −0.30950     | 0.002798 | **110.60** | −    |

- **R1 margin (the passing reach-regime margin):** at H=100, per-seed diffs WILD−TIGHT =
  [+0.2785, +0.2730, +0.2920, +0.2705, +0.2785], all > 0; mean_d +0.27850, sigma 0.003718
  → **74.90σ ≥ 3** → PASS.
- **R2 margin (the passing reversal margin):** at H=500, per-seed diffs WILD−TIGHT =
  [−0.3012, −0.3175, −0.3130, −0.3060, −0.3098], all < 0; mean_d −0.30950, sigma 0.002798
  → **110.60σ ≥ 3** → PASS.
- **R3:** min realized HTK = 1 (≥ 1); mean HTK monotone non-decreasing for both builds
  (TIGHT [1,1,2,3,5], WILD [1.0547, 1.2785, 1.7193, 3.0413, 4.6905]) → PASS.
- **R4a:** comb signs [+, +, −, +, −] == registered [+, +, −, +, −] → PASS.
- **R4b:** control ceil(H/mean) → PASS (table below).

## Comb sign table (which build wins, per H)

| H    | mean_d sign | winner (lower HTK) |
|------|-------------|--------------------|
| 80   | +           | TIGHT              |
| 100  | +           | TIGHT              |
| 140  | −           | WILD               |
| 300  | +           | TIGHT              |
| 500  | −           | WILD               |

The comb: at H=80/100 TIGHT's guaranteed one-shot beats WILD's straddling first hit; at
H=140 WILD kills in ~1.72 hits while TIGHT is stuck at the deterministic 2; at H=300
TIGHT's exact-3 just edges WILD's ~3.04; at H=500 WILD's mean advantage over 5 hits wins.
The sign alternates because HTK is the CEILING of a ratio — a discrete comb — so which
distribution is favored flips depending on where each H sits relative to the two builds'
breakpoint lattices.

## Deterministic-control table (variance removed: HTK = ceil(H/mean))

| H    | TIGHT ceil(H/105) | WILD ceil(H/120) | WILD ≤ TIGHT |
|------|-------------------|------------------|--------------|
| 80   | 1                 | 1                | yes          |
| 100  | 1                 | 1                | yes          |
| 140  | 2                 | 2                | yes          |
| 300  | 3                 | 3                | yes          |
| 500  | 5                 | 5                | yes          |

With variance removed the higher-mean WILD is NEVER worse than TIGHT — WILD ≤ TIGHT at
every H. Therefore the stochastic TIGHT wins at H∈{80,100,300} are entirely a product of
WILD's variance straddling breakpoints, not of any mean deficit; the head's causal claim
("variance-driven, not mean-driven") is directly demonstrated by the contrast between the
stochastic comb (TIGHT wins 3 of 5 HP) and the deterministic control (WILD wins/ties all 5).

## Falsifiability gates (were real)

- **Common random numbers (else NULL):** the two builds are compared on ONE per-seed
  per-trial uniform stream — each build's evaluation fingerprints the full matrix it
  iterated and the run asserts TIGHT's and WILD's fingerprints equal the seed's canonical
  matrix fingerprint; a divergence raises `SystemExit("NULL: builds saw different draws")`.
  Without shared draws the paired comparison would be a build-vs-noise confound.
- **Fixture pin:** the seed-1 H=100 first-20-trial uniform streams and their HTK under
  BOTH builds are committed and re-derived each run — one misread of the cumulative-damage
  / floor-1 order moves the fixture and trips the check. (The committed HTK: TIGHT all 1s;
  WILD [2,1,1,1,2,2,2,1,1,1,1,1,1,2,1,1,1,1,1,1] — the 2s are exactly the trials whose
  first WILD hit fell in [75,100).)
- **HTK floor:** every realized HTK is asserted ≥ 1; a zero/negative kill would trip R3.
- **Grid-spans-reversal:** the HP grid is asserted to contain both a low anchor (H ≤ 100,
  the reach regime) and a high anchor (H ≥ 500, the mean-dominant regime), so both the
  TIGHT-wins and WILD-wins regimes are reachable — a grid entirely on one side would make
  a gate untestable.

Any self-check failure would have blocked exit 0; a twin-evaluator disagreement or a
determinism break is the ONLY path to exit 1. The REJECT world was reachable (a comb that
failed to alternate [+,+,−,+,−], or a control in which WILD's ceil ever exceeded TIGHT's,
would fail R4) and did not come live — all four gates pass.

## Scope boundaries (stated, per the registration)

- **Distribution boundary:** TIGHT ~ Uniform[100,110] and WILD ~ Uniform[75,165] are
  STIPULATED equal-cost pinned distributions, NOT fit to any real weapon's measured damage
  roll. The ruling prices the phenomenon UNDER these two uniforms; it is not a claim about
  a specific game's balance data.
- **Metric boundary:** the metric is mean HTK (expected hits-to-kill) over the C=4000
  cohort; the gates are PASS/FAIL on the seed-mean HTK and the paired-diff margins over the
  five seeds. The claim is the gate-by-gate outcome on those means, not a
  distributional/percentile statement (e.g. HTK variance or worst-case tails), which is a
  named follow-up.
- **HP-grid boundary:** the comb is a claim about the SPECIFIC grid H∈{80,100,140,300,500};
  a denser sweep would reveal more sign flips (HTK is a step comb). The ruling binds the
  sign pattern on the registered grid, not a continuous characterization.
- **Single-target boundary:** one target, damage per hit i.i.d. within a trial, no armor /
  resistance / crit / cooldown mechanics. Multi-target, mitigated, or resource-constrained
  worlds are DIFFERENT objects not tested here.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a game-balance head (the CONSUMER owns weapon/build tuning guidance). The
deliverable is a citable measured verdict plus a transferable rule, fanned in to the fleet
manager (Q-0264). Per the proposal's pre-registered ACCEPT consequence, paste-ready and
recommendation-first (Q-0263.2): **(1, recommended)** adopt the BREAKPOINT rule — do NOT
rank equal-cost builds by mean damage alone; rank by mean HTK against the actual target-HP
distribution, because HTK is a discrete ceiling comb and a lower-mean, lower-variance build
can strictly win at HP values just above its guaranteed-one-shot (and other breakpoints)
even though the higher-mean build wins on average; **(2)** the variance channel is real and
directional — a WILDer roll helps far from breakpoints (H=500) but HURTS just past one
(H=100), so variance is not universally good or bad but breakpoint-relative; **(3)** the
deterministic control is the diagnostic — compute ceil(H/mean) for each build; wherever the
mean-favored build is tied or ahead on the control yet the other build wins stochastically,
the win is variance-driven and will move if you re-tune variance without touching the mean.
Transferable audit: any system with a discrete "reach-a-threshold" outcome and a
mean-vs-variance tradeoff (hits-to-kill, retries-to-success, packets-to-deliver,
attempts-to-pass) — "am I ranking options by their mean when the outcome is a ceiling comb,
and would a variance-only re-roll flip the winner near a threshold?"

## Seeds

**V100 consumes NO seed-ledger block.** The seeds are the in-file constants S=[1,2,3,4,5]
(`random.Random(seed)`), a fixed local realization set that drives each seed's
common-random-numbers uniform stream — NOT a draw from the fleet seed ledger. The next
free ledger block stays **20261730**, untouched (inherited unchanged from the V099 baton).
Both builds share one uniform stream per seed×trial so the seeds drive identical draws to
TIGHT and WILD; no seed touches the decision rule, which is a deterministic gate-by-gate
comparison of the seed-averaged mean HTK and the paired-diff margins.

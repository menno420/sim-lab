# Session — VERDICT 100 — hits-to-kill breakpoint-variance comb (P087, superbot-games). On the pinned single-target world (target HP H, dies when cumulative realized damage ≥ H; HTK = number of hits to reach H with floor ≥ 1; cohort C=4000 trials/seed, seeds S=[1,2,3,4,5], HP grid H∈{80,100,140,300,500}) two equal-cost weapon builds differ ONLY in per-hit damage distribution — TIGHT ~ Uniform[100,110] (mean 105, low variance) vs WILD ~ Uniform[75,165] (mean 120, high variance) — and P087 pre-registers an ACCEPT rule requiring ALL of R1–R4: R1 reach-regime (H=100 mean HTK TIGHT < WILD all 5 seeds, margin ≥3σ), R2 saturation reversal (H=500 mean HTK WILD < TIGHT all 5 seeds, margin ≥3σ), R3 well-posedness (every realized HTK ≥ 1 AND mean HTK monotone non-decreasing in H for BOTH builds), R4 comb+control (R4a sign of mean_d(H) over H∈[80,100,140,300,500] equals [+,+,−,+,−]; R4b the variance-free control HTK=ceil(H/mean), TIGHT mean=105 / WILD mean=120, has WILD ≤ TIGHT at every H — variance-driven, not mean-driven). Disclosed expected landing ACCEPT (the lower-mean TIGHT build wins at some HP because HTK is a discrete breakpoint comb, not a mean race). Independent hermetic re-implementation under COMMON RANDOM NUMBERS (per trial a single stream of MAX_HITS=25 uniforms u_i∈[0,1) drawn ONCE via random.Random(seed), BOTH builds map the SAME u_i to their own [lo,hi] via damage = lo + u_i·(hi−lo), stream re-drawn fresh per seed so identical trials evaluated at every H, else NULL); twin evaluators (if-chain + table-driven) must agree on token AND first-failing gate (idea-engine PROPOSAL 087, `## PROPOSAL 087 · 2026-07-16T18:59:26Z · status: sim-ready`, `ideas/superbot-games/htk-breakpoint-variance-comb-2026-07-16.md`; P087 → V100 under the +13 offset, twenty-fourth row; SEEDLESS ledger baton — seeds are the in-file constants S=[1..5], no seed-ledger block consumed, next free block stays 20261730)

> **Status:** `complete`
> 📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

Objective: produce VERDICT 100 for idea-engine PROPOSAL 087 (the hits-to-kill
breakpoint-variance comb, `ideas/superbot-games/htk-breakpoint-variance-comb-2026-07-16.md`,
outbox block `## PROPOSAL 087 · 2026-07-16T18:59:26Z · status: sim-ready`). One slice,
one branch (`claude/v100-htk-breakpoint-variance`), one verdict. NUMBERING, verified
at sim-lab origin/main ce3dace (the V099 merge #171 is the tip at session start):
newest `## VERDICT` header is 099; `## VERDICT 100` / `verdict-100` / `v100`
collision-grepped — no ledger header, no `sims/verdict-100-*` competing path, no
competing session card — so idea-engine PROPOSAL 087 → **VERDICT 100**, the +13
offset's twenty-fourth row (INTAKE number = proposal number, unbroken; map-row
extension lands in `docs/current-state.md` this same PR). Worker session; ledger
appended to `control/outbox.md` only — `control/inbox.md` untouched (manager-order
file); this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P088 → V101). No idea-engine claim file written by this
sim-lab slice (the V074–V099 precedent — the idea-engine claim rides the idea-engine
mirror PR). This is a NUMERIC-SIMULATION head (rung 1, the P017–P086 hermetic
pre-registered discipline): an independent hermetic re-implementation of a
single-target hits-to-kill funnel over two equal-cost damage distributions
(TIGHT vs WILD), evaluated under COMMON RANDOM NUMBERS (both builds map the identical
per-(trial,hit) uniform stream per seed, reused at every HP value, else the paired
comparison is NULL), across four pre-registered gates R1→R2→R3→R4, with twin evaluators
(an if-chain scorer and a table-driven scorer) that must agree on the ruling token AND
the first failing gate. The seeds are the in-file constants S=[1,2,3,4,5]
(RNG = `random.Random(seed)`), NOT a draw from the fleet seed ledger — this slice
consumes NO seed-ledger block and the next free block stays **20261730**, untouched
(inherited from the V099 baton). This card held the substrate gate red deliberately
until the flip (the born-red discipline — the designed hold is the only red this
branch produced itself); the flip to `complete` is this session's LAST step
(verdict ACCEPT confirmed, all gates verified, determinism + twin evaluators +
self-checks all good), taken as the release-landing commit.

## What happened

Built `sims/verdict-100-htk-breakpoint-variance-comb/` under the standing discipline
(born-red card FIRST → sim + fixtures + README + REPORT + outbox + map row → heartbeat
→ flip). The runner `htk_breakpoint_variance_comb_sim.py` re-implements the funnel from
the registered spec (NOT copied from P087's disclosed dry-sim): per seed each of the
C=4000 trials draws a single stream of MAX_HITS=25 uniforms u_i∈[0,1) ONCE via
`random.Random(seed)`, then BOTH builds consume that identical stream — each build maps
u_i to its own [lo,hi] via damage = lo + u_i·(hi−lo), and the same stream is reused at
ALL HP values (CRN across builds AND across H). A trial's HTK is the number of hits to
reach cumulative realized damage ≥ H, floor ≥ 1. An explicit NULL guard compares each
build's per-seed matrix fingerprint against the seed's canonical fingerprint and raises
`SystemExit("NULL: builds saw different draws")` on divergence. Twin evaluators — an
if-chain scorer and an independently transcribed table-driven scorer — must agree on the
verdict token AND the first-failing-gate reason. The fixture is the seed-1, H=100,
first-20-trial uniform streams plus HTK-under-both-builds on the identical draws: written
on first run, re-verified on every subsequent run. Byte-identical double run verified by
external diff + sha256; CPython 3, stdlib only, zero repo/network reads at verdict time.

## Results

**VERDICT 100 — ACCEPT** (first failing gate: **None**). Per the pre-registered rule
(ACCEPT iff R1 AND R2 AND R3 AND R4, evaluated in order R1→R2→R3→R4; else REJECT at the
first failing gate) all four gates pass, and the measured table reproduces P087's
disclosed dry-sim calibration to the book from an INDEPENDENT re-implementation.

Mean HTK over seeds S=[1,2,3,4,5] (lower = better; d = WILD−TIGHT, positive ⇒ TIGHT wins):

| H   | TIGHT mean | WILD mean | mean_d (W−T) | margin (σ) | sign | winner |
|-----|------------|-----------|--------------|------------|------|--------|
| 80  | 1.0000     | 1.0547    | +0.05470     | 49.75      | +    | TIGHT  |
| 100 | 1.0000     | 1.2785    | +0.27850     | 74.90      | +    | TIGHT  |
| 140 | 2.0000     | 1.7193    | −0.28070     | 99.54      | −    | WILD   |
| 300 | 3.0000     | 3.0413    | +0.04135     | 40.28      | +    | TIGHT  |
| 500 | 5.0000     | 4.6905    | −0.30950     | 110.60     | −    | WILD   |

Gate outcomes (fire in order R1→R2→R3→R4):

- **R1 reach regime @ H=100 — PASS.** TIGHT kills in exactly 1 hit every trial (min damage
  100 ≥ 100) so meanHTK_TIGHT=1.0000; WILD's first hit lands in [75,100) with prob
  25/90 ≈ 0.278 forcing a 2nd hit so meanHTK_WILD ≈ 1.2785; per-seed WILD−TIGHT diffs
  [+0.2785,+0.2730,+0.2920,+0.2705,+0.2785] (all >0 ⇒ TIGHT wins all 5 seeds); mean_d
  +0.27850, sigma 0.003718 → **74.90σ ≥ 3**.
- **R2 saturation reversal @ H=500 — PASS.** TIGHT needs exactly 5 hits every trial
  (4 hits ≤ 440 < 500; 5 hits ≥ 500) so meanHTK_TIGHT=5.0000; WILD's higher mean (120)
  over 5 hits kills in ≈4.6905; per-seed WILD−TIGHT diffs
  [−0.3012,−0.3175,−0.3130,−0.3060,−0.3098] (all <0 ⇒ WILD wins all 5 seeds); mean_d
  −0.30950, sigma 0.002798 → **110.60σ ≥ 3**.
- **R3 well-posedness — PASS.** Every realized HTK ≥ 1 (measured min = 1); mean HTK
  monotone non-decreasing in H for BOTH builds (TIGHT [1.0,1.0,2.0,3.0,5.0], WILD
  [1.0547,1.2785,1.7193,3.0413,4.6905]).
- **R4 comb + control — PASS.** (R4a) sign of mean_d(H) over the grid = **[+,+,−,+,−]**,
  matching the registered comb exactly (TIGHT wins H∈{80,100,300}, WILD wins H∈{140,500}).
  (R4b) the variance-free control HTK=ceil(H/mean) — TIGHT ceil(H/105), WILD ceil(H/120) —
  has WILD ≤ TIGHT at every H ([1≤1,1≤1,2≤2,3≤3,5≤5]), so every stochastic TIGHT win is
  proven VARIANCE-driven, not mean-driven.

All four gates pass → ACCEPT, first failing gate **None**. Twin evaluators agree:
A(if-chain)=ACCEPT/None, B(table)=ACCEPT/None. Self-checks 8/8 passed
(fixture_matches_committed, twin_evaluators_agree_verdict, twin_evaluators_agree_reason,
common_random_numbers_shared_per_build_and_H, per_seed_matrices_distinct,
every_realized_htk_ge_1, cohort_size_is_C, hp_grid_spans_reversal). Exit 0,
byte-identical double run.

Digests (double run, external diff + sha256):

- `results.json` sha256 `6e848ccc43a4f4f5428cefb35d3f1f4efbf7c3299332720fc41707a2460ac40d`
- `run-stdout.txt` sha256 `493559db5443140b8d525bcb779f272475d1b4c02bf3ac1635fa5cd5bfffb880`
- `fixtures.json` sha256 `f392ea2c500a9ba0d1e0b9d079d8efb76d17ffab2495f755e4678ced24677086`

Mechanism: HTK is the CEILING of an HP/damage ratio — a discrete comb — so which
distribution is favored FLIPS depending on where each H sits relative to the two builds'
breakpoint lattices. Just above TIGHT's guaranteed one-shot (H=80/100) TIGHT's zero
variance beats WILD's straddling first hit; at H=140 WILD kills in ~1.72 while TIGHT is
stuck at the deterministic 2; at H=300 TIGHT's exact-3 just edges WILD's ~3.04; far from
any breakpoint (H=500) WILD's mean advantage over 5 hits dominates. The R4b control makes
the point mechanistic: with variance removed the higher-mean WILD is never worse, so
every TIGHT win is a variance artifact of the discrete lattice — "lower mean damage wins"
is real but non-monotone in HP, not a mean race. This is the direct successor to V099's
ceiling-located crossover: where P086 anchored a CONCENTRATE→SPREAD flip ON a saturation
bound, P087 shows the winner combs across a discrete breakpoint lattice, and the ACCEPT
confirms both the comb signs and the variance-driven mechanism. PR (this slice); the
born-red hold clears on this flip.

## ⟲ Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 099, sim-lab PR #171 →
ce3dace): the series read-through concentrate-vs-spread saturation-crossover slice
(idea-engine P086, series-readthrough-saturation-crossover), an ACCEPT at
first-failing-gate **None**. Its conventions this slice consumes wholesale: the
born-red card as the FIRST commit / the shared-input NULL guard (V099 shared one
uniform matrix across both allocations; this slice shares one uniform stream across
both builds AND across all H — the same paired-comparison discipline, else NULL) /
the twin-evaluator (if-chain + table) agreement contract on BOTH token and
first-failing gate / the typed margin ledger / the +13 offset extended one row in the
same grammar / the SEEDLESS-baton bookkeeping (next free block stays 20261730,
untouched). One CONCRETE observation carried forward: V099's ACCEPT located an
optimum FLIP at the world's own stability bound (the entry-step read-through ceiling
r_max, saturating at b_1=11) — a reversal at a single continuous bound. V100 tests a
sharper claim in the SAME family: the winner does not flip once at a bound but COMBS
across a discrete breakpoint lattice — sign [+,+,−,+,−] as HP sweeps — because HTK is
a ceiling (integer) function, and the R4b variance-free control proves the TIGHT wins
are variance-driven not mean-driven. So where V099 verified a single ceiling-located
reversal, V100 verifies a multi-sign discrete comb plus its mechanistic control — the
direct successor lesson (a discrete-breakpoint dual of the continuous saturation bound).
(Verified: the outbox tail reads INTAKE 085 → V098 → INTAKE 086 → V099, contiguous
through `## VERDICT 099`, so the +13 chain is unbroken and no backfill is needed this
slice.)

💡 **Session idea (this session):** A proposal-time "breakpoint-lattice reachability"
lint for any pre-registered gate that claims a discrete-HTK (or any ceiling-of-ratio)
COMB — a sign vector that alternates as a swept parameter H crosses breakpoints. For a
build with per-hit damage support [lo,hi] the k-hit reachable HP band is [k·lo, k·hi],
and a low-variance build's HTK is deterministic (single-valued) at every H whose band
does NOT straddle a k·lo boundary. The lint checks, from the pinned map alone and BEFORE
any simulation, that the registered HP grid actually SAMPLES both regimes for the comb to
be observable: at least one grid H must sit where TIGHT's band is non-straddling (so its
HTK is exactly ceil(H/lo_TIGHT) and the deterministic edge is testable — R1/R3), and at
least one grid H must sit far enough above any breakpoint that the higher-mean build's
law-of-large-numbers advantage dominates (the mean-race regime — R2), with the registered
sign vector's sign changes each falling between grid points whose k·lo bands differ. P087's
grid H∈{80,100,140,300,500} straddles correctly (80/100 in TIGHT's one-shot band [100,110]
edge, 140 past it into the 2-hit band, 500 deep in the mean-race regime), so the ACCEPT
comb is reachable — but a grid entirely inside one k-band would pin every sign the same and
make the comb UNTESTABLE (the proposal's own named falsifiability failure mode), while a
grid that never left the low-HP breakpoint zone would never reach the mean-race regime and
make R2 UNREACHABLE. The check is cheap (compute each build's k·lo / k·hi band edges for
k=1..ceil(maxH/lo) and test that the grid points fall in ≥2 distinct straddle regimes with
the sign changes bracketed) and it has zero false positives on a correctly-sampling grid.
It is the discrete-breakpoint dual of V099's 💡 (a saturation-reachability lint for a
continuous ceiling): V099 flagged a budget grid that FAILS to straddle its saturation
budget; this flags an HP grid that FAILS to sample both sides of the breakpoint lattice —
both are pre-simulation reachability checks on where a registered gate's swept anchor sits
relative to the world's own discontinuities. Dedup: grepped `.sessions/` + `docs/` at
ce3dace for "breakpoint"/"lattice"/"comb reachability"/"HTK grid" — no prior card or doc
states a proposal-time breakpoint-lattice grid-sampling reachability check.

📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

## Baton

- **Next-2 for the successor:** (1) draft PROPOSAL 088 (the next rotation slot) →
  its **VERDICT 101**, the +13 offset's twenty-fifth row; (2) execute ORDER-010(c)
  kit upgrade v1.15.0 → v1.18.0 — STILL PARKED on owner auth + the ASK-005/006 watch
  (dispatch reports v1.18.0 vs on-disk v1.15.0); a verdict slice does not execute it.
- **Seed baton:** V100 is SEEDLESS — the seeds are the in-file constants S=[1,2,3,4,5]
  (`random.Random(seed)`), NOT a ledger draw; no seed-ledger block consumed, the next
  free block stays **20261730**, inherited unchanged from the V099 baton.
- **Ledger locations:** V001–071 in control/outbox-archive-2026-07.md, V072+ live in
  control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file,
  untouched by verdict slices).

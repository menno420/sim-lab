# Session — VERDICT 097 — the pooled rate that hides one confounded allocation: Simpson's-paradox aggregation-reversal trap — the folk rule "a treatment better in EVERY subgroup is better overall" priced where it exactly breaks, when the subgroup allocation is confounded with the subgroup baseline; on the pinned Charig et al. (1986) kidney-stone table (A·S=81/87, A·L=192/263, pooled A=273/350=39/50≈0.780; B·S=234/270, B·L=55/80, pooled B=289/350≈0.826) treatment A beats B in BOTH strata yet LOSES the pool by exactly 16/350=8/175≈0.046 — the reversal — because the pooled rate is a SIZE-WEIGHTED mean whose weights belong to the ALLOCATION (A loads the hard large stratum 263/350 vs B's 80/350); the reversal is a CLIFF (pooled_A(x) strictly decreasing, one crossing of 289/350 at x*=184, real table x=263 past it) and the priced repair is STANDARDIZATION to a common weight (std_A=634983/762700≈0.8325 > std_B=6231/8000≈0.7789, weight-invariant over four mixes) restoring the true per-stratum ordering at the price of one recorded covariate (idea-engine PROPOSAL 084, the round-17 COMPLETELY-UNRELATED-domain CLOSER slot — STATISTICS / CAUSAL INFERENCE; P084 → V097 under the +13 offset, twenty-first row; SEEDLESS pure-math head, no Arm R seed block consumed)

> **Status:** `complete`
> 📊 Model: opus-class · high · simulation/verification

Objective: produce VERDICT 097 for idea-engine PROPOSAL 084 (the Simpson's-paradox
aggregation-reversal trap, `ideas/fleet/simpsons-paradox-aggregation-reversal-2026-07-16.md`,
outbox block `## PROPOSAL 084 · 2026-07-16T15:25:14Z · status: sim-ready`, landed
idea-engine main @ 4b9db80 via PR #456). One slice, one branch
(`claude/v097-simpsons-paradox`), one verdict. NUMBERING, verified at sim-lab
origin/main 34ff0c9 (the V096 merge #168 is the tip at session start): newest
`## VERDICT` header is 096; `## VERDICT 097` / `verdict-097` / `v097`
collision-grepped — no ledger header, no `sims/verdict-097-*` path, no session
card, no competing remote ref or PR at session start (`git ls-remote` returned
no v097 branch, `list_pull_requests` open = empty) — so idea-engine
PROPOSAL 084 → **VERDICT 097**, the +13 offset's twenty-first row (INTAKE number
= proposal number, unbroken; map-row extension landed in `docs/current-state.md`
this same PR). Worker session; ledger appended to `control/outbox.md` only —
`control/inbox.md` untouched (manager-order file); this slice also refreshes the
coordinator heartbeat `control/status.md` (next-expected roll to P085 → V098).
No idea-engine claim file written by this sim-lab slice (the V074–V096
precedent — the idea-engine claim rides the idea-engine mirror PR). This is a
SEEDLESS pure-math head (nearest method kin: the P028/P032/P036/P076 seedless
fully-exact-census + twin-arm discipline, reused as machinery on a new object —
a size-weighted-mean reversal with a single-cliff allocation threshold and a
weight-invariant standardization repair confined to the same-sign case); every
decision leg is exact seedless integer/Fraction arithmetic, platform-independent,
ZERO RNG. Arm R exists ONLY as a seeded, REPORTING-ONLY census (local
reporting-only seed constants 970/971/972, no statistical gate) and consumes NO
seed-ledger block — V097 is SEEDLESS and the next free block stays **20261730**,
untouched. This card holds the substrate gate red deliberately until this flip
(the born-red discipline — the designed hold is the only red this branch
produces itself).

## What happened

Built `sims/verdict-097-simpsons-paradox-aggregation-reversal/` under the
standing discipline: fixtures.json committed BEFORE the runner (born-red card →
sim + fixtures + README + REPORT + map row → heartbeat → this flip). Three-arm +
twin-evaluator structure: Arm A the pinned deterministic automaton over exact
rational (`Fraction`) arithmetic — DECISION-bearing (per-stratum rates, the
pooled reversal, the cliff crossing x*, the four-mix standardization); Arm B an
INDEPENDENTLY-shaped twin (integer roll-up of raw counts + an opposite-direction
crossing walk) tied through the typed must-equal contacts C1 (pooled winner),
C2 (cliff x*=184), C3 (std_A/std_B under the pooled-marginal mix), plus the
margin and reversal contacts; Arm R a SEEDED, REPORTING-ONLY 2×2×2 random census
(no statistical gate, registered 3-draw grammar per seed, 12-hex class-stream
digest) whose only claim is that the exhibited reversal REQUIRES differential
weighting. Twin evaluators — an if-chain and an independently transcribed
table-driven scorer — agree over the full enumerated 16-row boolean predicate
space. Byte-identical double run verified by external diff + sha256; CPython
stdlib only, zero repo/network reads at verdict time. The born-red card was the
only designed hold; PR opened READY at slice start.

## Results

**VERDICT 097 — REJECT.** Per the pre-registered REJECT-first rule applied in
the registered order REJECT → INVALID → APPROVE → NULL (REJECT evaluated FIRST):
the naive "pooling preserves stratum ordering" claim is REFUTED by the exhibited
reversal (A > B in BOTH strata — 81·270=21,870 > 234·87=20,358 and
192·80=15,360 > 55·263=14,465 by cross-multiplication — while pooled B > pooled A
by exactly 16/350 = 8/175), the reversal is a single-cliff size-weighting effect
(pooled_A(x) strictly decreasing, one crossing of 289/350 at x*=184, real table
x=263 past it), AND a common-weight standardization RESTORES the true per-stratum
ordering (std_A=634983/762700≈0.8325 > std_B=6231/8000≈0.7789, weight-invariant
over all four mixes {pooled_marginal, uniform, a_marginal, b_marginal}). APPROVE
is arithmetically excluded (it would require a uniform stratum ordering to always
survive aggregation — the single exhibited reversal excludes it, mutually
exclusive with REJECT). Both independently-written decision evaluators agree
REJECT/REJECT on the measured inputs AND over the full enumerated 16-row boolean
predicate space; every decision number a seedless exact Fraction/integer identity.
Self-checks all PASS, exit 0, byte-identical across two full in-repo process runs
(digests in REPORT.md). The three named NULL axes (estimand-weight,
model-arithmetic, witness-scope) were reachable and none fired.

## ⟲ Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 096, sim-lab PR #168 →
34ff0c9): a clean, exemplary landing whose conventions this slice consumed
wholesale — born-red card / READY PR / no-sim-lab-claim-file (the idea-engine
claim rides the mirror PR) / twin-arm with typed must-equal contacts / typed
margin ledger / structured anomaly census / vacancy-derived disclosures / the
+13 offset extended one row in the same grammar. Its standout discipline: ZERO
rehearsal fixes and zero fix-forwards, and it disclosed one genuine live surprise
honestly (the Arm-R class-stream digest reproduced only under a first-character
token stream, a non-injective encoding, paired explicitly with the per-seed
census as the second witness). The one GAP this slice found and is BACKFILLING:
**PR #168 finalized VERDICT 096 but its outbox append never landed in sim-lab
`control/outbox.md`** — the ledger tail stopped at `## VERDICT 095`, so the
canonical append-only verdict ledger was missing both the `## INTAKE 083` and
`## VERDICT 096` blocks (the idea-engine mirror carried its own VERDICT 096
record, but the sim-lab-side ledger did not). This slice reconstructs both
faithfully from the idea-engine mirror block (verdict content) and the V096 sim
REPORT/README (intake question/method) and appends them ahead of the V097 pair,
each flagged with an HTML-comment note that they were backfilled by this slice.

💡 **Session idea (genuine, this session):** MAKE "OUTBOX-LEDGER APPEND" A
MACHINE-CHECKED PART OF done-when, NOT A CONVENTION A SLICE CAN DROP. V096's
finalize was correct in every measured value yet its ledger append silently went
missing on merge (the born-red card flipped, the sim landed, the mirror recorded
it — but the sim-lab canonical ledger did not gain its `## VERDICT 096` block),
and nothing in the check pipeline noticed, because the append is currently a
hand-discipline. A lightweight `bootstrap.py check`-side assertion would close
it: for the highest `## VERDICT nnn` header the branch introduces, require a
matching `## INTAKE (nnn−13)` block AND a corresponding `sims/verdict-nnn-*/`
directory to co-exist in the same tree before the card is allowed to read
`complete` — a "no finalized verdict without its ledger row" gate. It is cheap
(a grep-pair over the outbox headers + a directory existence test, both already
data the slice computes), it has zero false positives on a correctly-finalized
slice, and it would have turned V096's silent omission into a red check instead
of a gap a later slice had to notice and backfill by hand. Dedup: V096's 💡 was
about a digest's ENCODING FIDELITY (a non-injective token map narrowing a
checksum); V095's was a digest EXISTING beside anchor-less shape slots; this is
about the FINALIZATION CONTRACT itself — the ledger row is part of the
deliverable, so make its presence a gate, not a habit. Grepped `.sessions/` +
`docs/` at 34ff0c9 for "done-when"/"ledger append"/"outbox" gate rules — no
prior card or doc states a machine-checked append-completeness rule.

📊 Model: opus-class · high · simulation/verification

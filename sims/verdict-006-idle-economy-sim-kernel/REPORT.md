# REPORT -- idle-economy sim kernel (SIM-001 / economy-v1)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 006** @
> `7df1d6cd09d52ad8574b6f37adf00abb99179f5e`, relaying superbot-idle **SIM-001** from
> `docs/design/economy-v1.md` @ `f11c71a52d4d2adf88b2bf11f5d1134bad495be2`.
> Engine driven: `idle_engine/` @ `f11c71a5` (`menno420/superbot-idle`), **vendored byte-for-byte**.
> Run: `python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py`

## METHOD LABEL: NUMERIC SIMULATION

Rung 1 of the method ladder is the cheapest ADEQUATE evidence here: the economy is a
fully-specified, pure, integer-exact deterministic system (no wall clock, no randomness,
no I/O), so its pacing is *computed*, not sampled. The sim does not model the economy -- it
**drives the real economy engine** and reads the answer. There is no RNG, so a single run
per scenario *is* the distribution's entire support; determinism is proven by byte-identical
re-run (see gate 4), not by a seed sweep. This label fills the outbox `evidence: simulation`.

## What it MODELS / MEASURES

The economy-v1 **reference world**, exactly as pre-registered (economy-v1.md section Reference
world), every parameter read live from the vendored `idle_engine.economy`:

- one generator `GeneratorSpec("tier1","primary",base_rate=1)`, owned `{"tier1":1}` (count
  fixed at 1; no generator-purchase path exists);
- one upgrade ladder `build_upgrade_spec("boost1", tier1)` -- geometric cost
  `cost(L)=60*115^L//100^L`, additive `+25%`/level;
- one prestige track `build_prestige_spec(awards="prestige", measures="primary")` --
  threshold = divisor = 100000, award `isqrt(lifetime//divisor)`, `+10%`/unit bonus.
- Per-second integer rate (folded once, floor-divided once): `base*count*(100+25U)*(100+10P)//10000`.

**No re-implementation.** The driver imports the pinned package and calls its own `tick`,
`offline_progress`, `purchase_upgrade`, `upgrade_cost`, `prestige_eligible`,
`prestige_award`, `apply_prestige`, `production_per_second`, `build_upgrade_spec`,
`build_prestige_spec`. The five engine modules are byte-identical copies (md5-verified);
only `idle_engine/__init__.py` is reconstructed to re-export the vendored modules (the
upstream init also re-exported `theme`/`render`, not part of the SIM-001 surface). **No
engine logic was edited.** The one modelling choice made *in the driver, not the engine*:
after `apply_prestige` (which correctly wipes `owned`), the reference world re-seeds
`owned={"tier1":1}` to restore the "a fresh save starts owning tier1" invariant -- there is
no purchase path, so a reset must yield a fresh save. This is disclosed and is a
reference-world rule, not an engine change.

**Scenarios** (fresh save, t=0, 14-day horizon): **S1** idle-only (never buys/prestiges); **S2**
check-in every N in {0.25,2,8,24}h (credit elapsed production via `offline_progress` ->
greedy-buy while affordable -> prestige iff eligible); **S3** the same policy at 1-second
granularity, computed by exact event-jump and **proven byte-identical to a literal
per-second loop** over the first two resets (a self-check); additive **S3b** = S3 with a
"buy only if it pays back within 1 h at current rate" guard. O6 is the first 20 S3 resets.

## What it SETTLED (the load-bearing claims)

**All ten pre-registered acceptance criteria PASS (10/10)** on the current PROVISIONAL
parameters -- so the table graduates PROVISIONAL -> SIM-PINNED (economy-v1.md section Verdict
semantics). Every number below is a committed output of the one run command.

| id | criterion (band) | measured | verdict |
|---|---|---|---|
| A1 | S3 time-to-first-upgrade (30-180 s) | **60 s** | PASS |
| A2 | S3 >=5 purchases by 15 min | **12** by 900 s | PASS |
| A3 | S3 first-prestige (2-8 h) | **12573 s = 3.493 h** | PASS |
| A4 | S1 lifetime crosses 100000 (18-36 h) | **100000 s = 27.778 h** | PASS |
| A5 | S2(N=2) first-prestige (4-12 h) | **21600 s = 6.000 h** | PASS |
| A6 | A4 / A3 (4-12x) | **7.954x** | PASS |
| A7 | S2(N=2)&(N=8) every pre-prestige visit buys >=2 | **min buys 6 / 16** | PASS |
| A8 | S3 max purchase-gap < 25% of run | **1215 s = 9.66%** | PASS |
| A9 | resets 2,3 each 50-100% of prior | **r2=0.9175, r3=0.9080** | PASS |
| A10 | O6 cumulative bonus sub-exponential | **linear 10->200%; ratios 0.918->0.966 up; no super-geo** | PASS |

Selected outputs (full tables in stdout):

- **O1** time-to-first-upgrade: S3 60 s; S3b 60 s; S2(N)=first visit (900/7200/28800/86400 s); S1 never.
- **O2** S3 buys levels L1..L39 by first prestige, cadence tightening from ~60 s to ~1200 s
  gaps; S2(N=2) buys 21 levels at the first visit alone (offline burst).
- **O4** first-prestige & resets 1-3 (s): S3 `12573 / 11536 / 10475`; S2(N=2) `21600 / 21600 / 21600`;
  S1 threshold-cross `100000`. (S2 resets sit exactly on the N-hour visit grid -- see LIMITS.)
- **O5** payback `cost(L)/(base*EFFECT/100)` h: L0=0.067 h ... L39=15.53 h (the level S3 holds at
  each of resets 1-3). The floor makes actual marginal rate 0 on 3 of every 4 levels -- the
  nominal payback curve is smooth; the realised one is a staircase (see gate 1).
- **O6** 20 resets: award = 1 **every** reset (`isqrt(1)`), so cumulative bonus is **exactly
  linear** (10,20,...,200%); reset durations shrink `12573->4194 s` with consecutive ratios
  **rising 0.918->0.966 toward 1**, zero ratios below 0.5 -> **no super-geometric shrinkage**.

## What it did NOT settle

- **The floor-collapse of low levels is a live design smell, not a criterion.** With
  `base_rate=1`, `(100+25U)//100` means levels 1,2,3 add **zero** real rate; the rate only
  ticks up every 4th level. Every A-criterion still passes, but the "+25%/level" the player is
  sold is inert for 3 of every 4 early purchases. SIM-001 has no criterion for this; it is
  flagged here as the headline follow-up (raise `base_rate`, or scale rate before the floor).
- **S2's first-prestige times are quantised to the visit grid**, not the true crossing -- a
  structural property of a check-in player, not of the parameters (see gate 1 / LIMITS).
- **No live player behaviour.** Greedy-buy is the optimal proxy under additive-linear effects
  (S3b, a payback-gated policy, lands identically at 12573 s), but real players are not greedy
  optimal, do not check in on a perfect grid, and quit -- none of which this settles.
- **Nothing about T10** (second generator tier): no purchase path exists; out of SIM-001 scope.
- **Only the reference world.** One generator, one upgrade, one prestige track. Multi-generator
  / multi-upgrade interaction is untouched.

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

The sim is not an approximation of the economy -- it *is* the shipped economy code, called
directly, so there is **zero model-vs-engine gap** on the mechanics: cost curves, rate folding,
floor division, prestige award, and the tick==offline equality are the real functions
(self-checked exactly equal). What it abstracts away is the **player and the clock**: (a) a
*perfectly greedy* buyer, (b) *perfectly regular* check-ins (S2 visits land on an exact N-hour
grid, so S2 first-prestige times are quantised UP to the next visit -- e.g. S2(N=2)=6.000 h is
"the visit at which prestige became actionable," per the design's own time-to-X rule, not a
continuous crossing), (c) no churn/fatigue. Could a gap flip a verdict? For the S1/S3 criteria
(A1-A4, A6, A8, A9, A10) -- no: those are computed from the engine with no player-grid freedom.
For the S2 criteria (A5, A7) the grid *inflates* first-prestige and *batches* purchases, but
both land mid-band with margin (A5 6 h in [4,12]; A7 min 6/16 >= 2), so plausible irregularity
does not flip them. The honest residual: the **base_rate=1 floor** (levels 1-3 add no real
rate) is a live UX gap the criteria do not test -- it cannot flip any A-verdict, but it is the
thing a live build would feel first (see What it did NOT settle).

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

- *Bugs:* **62 self-checks, 0 failed**, ending on `sys.exit(sc.report())` (exit 0 iff clean).
  They assert the load-bearing invariants directly: `upgrade_cost` matches `60*115^L//100^L`
  for L=0..10; the rate identity holds at 28 sampled (U,P); **tick over a full horizon ==
  `offline_progress` closed form** (exact, incl. a literal 1-second loop); `purchase_upgrade`
  raises on balance<cost and `apply_prestige` raises when not eligible (`expect_reject`);
  spending never grows lifetime while production grows both; O4/O6 durations positive; O6 award
  ==1 => cumulative bonus exactly linear; O3 lifetime monotone; and the S3 event-jump is
  **byte-identical to a literal per-second loop** over the first two resets (so the optimisation
  is faithful, not a shortcut that changes timing).
- *Seeded luck:* **not applicable and disclosed** -- the engine has no RNG, so there is no seed
  and no sampling variance; the "distribution" is a single exact trajectory. Reproducibility is
  therefore bit-identity, the strongest form (see gate 4), not cross-seed stability.
- *Cherry-picking:* the report is the **whole** scenario set -- all four S2 sub-scenarios
  (including N=8/24 whose first-prestige times sit *outside* an S5-style band but carry no
  criterion), the full 20-reset O6 table, and the negative headline (the floor smell). No band
  was moved and no scenario dropped to make a criterion pass; where a literal reading is
  arguable (A10), both readings are printed (see below).

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

The conclusion is re-derived at the policy edges: **S3 (1-s greedy)** and **S3b
(payback-gated)** reach first prestige at the *identical* 12573 s -- the ranking is
policy-insensitive because additive-linear effects make greedy optimal. Across check-in
cadence N in {0.25,2,8,24}h the pacing degrades smoothly and monotonically (first-prestige
3.75->6->16->48 h), exactly as the cost/effect shapes predict -- no cliff, no inversion. O6 is
tested to 20 resets (2x the ">=3" the criteria demand) and the shrinkage stays sub-geometric to
the edge. The one edge the criteria do **not** probe is the parameter grid itself (only the
single PROVISIONAL point is run) -- SIM-001 asked for the point, not a sweep; a sweep is the
natural next hardening if the floor smell is retuned.

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Yes -- the strongest gate. Committed code (engine byte-copied + driver), **one** documented
command (`python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py`), no argparse,
no flags, no external input, stdlib-only. Every scenario is **run twice and asserted
byte-identical** (canonical-JSON equality; `determinism_bytes` vendored from the harness), so
the whole O1-O6 + scorecard is deterministic by construction. Runs in < 1 s.

**5. LIMITS?** *"what this evidence does NOT show"*

It shows the PROVISIONAL parameters hit their pacing *targets* on the reference world; it does
**not** show they feel good live. It does not model real players (greedy/grid/no-churn
abstractions), does not test the parameter grid (single point), does not cover multi-generator
or multi-upgrade interaction, says nothing about T10 (no purchase path), and -- the sharpest
limit -- **does not flag the `base_rate=1` floor as a failure** because no criterion covers it,
even though it makes 3 of every 4 early "+25%" purchases inert. Launch telemetry needed for
what it cannot establish: real time-to-first-upgrade / time-to-first-prestige distributions,
per-visit purchase counts and session lengths, and day-2 retention past the first prestige --
those would confirm (or break) the "feels like opening a present" intent the targets encode.

### A note on A10's compound wording (disclosed, not reinterpreted)

A10's registered PASS condition is *"cumulative bonus growth across 20 resets is
**sub-exponential** (each reset's duration ratio non-decreasing toward 1)."* The load-bearing
clause -- sub-exponential cumulative bonus -- holds **unconditionally and exactly**: award is
`isqrt(lifetime//divisor)=1` at every reset, so cumulative bonus is perfectly **linear**
(10,20,...,200%), the design's whole anti-runaway intent (isqrt + linear +10%). The parenthetical
gloss ("ratios non-decreasing toward 1") describes the mechanism; the measured ratios **trend
up 0.918->0.966 toward 1 with no ratio below 0.5** (no super-geometric shrinkage -- the O6 alarm).
A strictly-monotone reading of the gloss shows **6 sub-1% dips** (e.g. 0.9175->0.9080) that are
pure integer-quantisation of the overlaid greedy-buy schedule, not a bonus-compounding effect --
they are printed in full in the O6 output. The scorecard scores A10 by its load-bearing
condition (sub-exponential + no super-geometric shrinkage + ratios trending to 1) = **PASS**,
and discloses the quantisation dips rather than hiding them; it does not soften a genuinely
failing criterion.

## EVIDENCE STRENGTH: moderate-strong -- gate PASS

No gate fully fails. Gates 2 and 4 are the **strongest possible** for this class: the sim runs
the *real* engine (zero mechanics gap), carries 62 exact self-checks including a
tick==offline-closed-form proof and an event-jump==per-second byte-equality proof, and is
bit-reproducible in < 1 s. Gate 1 is genuinely strong for S1/S3 (no player freedom) and only
*partial* for S2 (visit-grid quantisation, disclosed, non-flipping). It falls short of `strong`
for one honest reason (gate 3/5): a **single parameter point** is run, not a sweep, and the
live-UX floor smell is unmodelled -- so this settles "the pre-registered targets are met by
these numbers on this world," which is exactly what SIM-001 asked, at `moderate-strong`.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** **approve** -- 10/10 acceptance criteria PASS; the PROVISIONAL economy-v1
  parameter table graduates **PROVISIONAL -> SIM-PINNED** (economy-v1.md section Verdict semantics).
- **Ruling:** n/a (not needs-more-evidence).
- **Target:** `menno420/superbot-idle` (the economy-v1 doc + `idle_engine/economy.py` parameter
  table; the follow-up PR flips PROVISIONAL->SIM-PINNED in both, same-PR, per the integrity floor).
- **Recommended implementation:** keep all seven parameters as-is (they hit every pacing target
  with mid-band margin); pin them. **Named follow-up (not blocking the pin):** address the
  `base_rate=1` floor so the advertised "+25%/level" is felt every level, not every 4th -- raise
  `tier1.base_rate` (e.g. to >=4) or apply the upgrade/prestige multiplier before the floor;
  re-run this sim to confirm the pin survives, and add a small parameter sweep as harness hardening.
- **Guardrails:** the parity test (`tests/test_economy_design_doc.py`) already fails the build if
  the doc table and `economy.py` drift -- keep it; any retune must move doc + engine same-PR.
- **Telemetry:** on launch capture real time-to-first-upgrade, time-to-first-prestige, per-visit
  purchase counts, session length, and day-2 retention, to validate the abstracted player.
- **Codex review:** reply: pending

<!-- Outbox verdict-grammar block (README), emitted on finalization -- DRAFT, coordinator finalizes:
## VERDICT 006 - <ISO8601> - status: finalized
target: menno420/superbot-idle
idea: idea-engine control/outbox.md PROPOSAL 006 @ 7df1d6cd09d52ad8574b6f37adf00abb99179f5e (relays superbot-idle SIM-001 @ f11c71a52d4d2adf88b2bf11f5d1134bad495be2)
verdict: approve
evidence: simulation
report: sims/verdict-006-idle-economy-sim-kernel/ - run: python3 sims/verdict-006-idle-economy-sim-kernel/idle_economy_sim.py
recommendation: all 10 acceptance criteria PASS on the PROVISIONAL params -- graduate PROVISIONAL -> SIM-PINNED; non-blocking follow-up: fix the base_rate=1 floor (levels 1-3 add zero real rate) + add a parameter sweep
codex: PR #<n> comment - reply: pending
gate: PASS
-->

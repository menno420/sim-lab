# Session — VERDICT 062 — Chicken-farm faucet self-balance: does the hub farm's committed sink ("each hen costs more coins") actually keep the faucet from out-earning the committed E[!daily] anchor for any collector, or does the "conservative faucet" run away? (idea-engine PROPOSAL 051, game-mechanics r9)

> **Status:** complete
> 📊 Model: Claude Fable (Fable 5 family) · 2026-07-14 · verdict-062 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 051 (`## PROPOSAL 051 · 2026-07-14T00:00:51Z · status: sim-ready`, landed via idea-engine PR #373 → main a500048, merged 2026-07-14T00:04:18Z; claim landed via idea-engine PR #374 reserving the P051 intake + VERDICT 062 and this branch `claude/verdict-062-chicken-farm-faucet`; numbering INTAKE = proposal number, VERDICT 062 per the established P050→V061 offset map) — price the superbot hub farm's two never-quantified header claims (L1 "Buying hens scales the faucet but each costs more coins (the sink), so the loop stays self-balancing"; L2 "an idle player banks at most ~40 coins over ~100 min before the coop caps — a small fraction of a `!daily`") against the SAME repo's committed absolute anchor E[!daily] = 169201/100 = 1692.01 coins/day exact (economy_helpers `_DAILY_TIERS`), per the idea doc `ideas/superbot/chicken-farm-faucet-self-balance-2026-07-13.md` @ idea-engine main a500048 (blob pin a305c62), engine constants harvested FIRSTHAND @ superbot affd7ea1ae5163109527e59ce73b46f0a8c7866c (disbot/utils/farm/farm.py + farm_workflow.py + economy_helpers.py). Pinned model (integer seconds/coins/eggs): accrual per `farm.settle` — intervals = (now − updated_at) // 300, eggs' = min(cap, eggs + intervals·chickens), cap(L) = 20 + 15·L for L ≤ 10, sub-interval remainder preserved below cap, clock-to-now at cap; write semantics per `farm_workflow` pinned — collect settles, pays eggs·2 (EGG_VALUE = 2), persists (0, now) with the remainder DISCARDED; buy settles at the OLD flock size first (no retroactive laying); purchases only at check-ins; NO cooldown on the collect path; prices next hen round(40·1.55^(chickens−1)) to the 100-hen ceiling, next coop round(100·1.8^level) to L = 10, the fixture pinning the DERIVED integer tables (hen extras 0–14: 40, 62, 96, 149, 231, 358, 555, 860, 1333, 2066, 3202, 4963, 7692, 11923, 18480; coop L 0–9: 100, 180, 324, 583, 1050, 1890, 3401, 6122, 11020, 19836; coop total 44,506) re-derived under the pinned CPython minor and asserted equal before any cell runs. Player: one fresh farm (1 hen, coop 0, wallet 0), CLOSED wallet on every decision leg; check-ins at cadence Δ ∈ {900, 3600, 14400, 86400} s: settle + collect, then the purchase policy applied while it buys; policy family {GREEDY, PAIR (joint two-purchase payback ≤ 14 days), HEN-ONLY, COOP-ONLY, ALT}; marginal value on the exact steady-state rate R(n, L, Δ) = min(cap(L), n·⌊Δ/300⌋)·2·86400/Δ coins/day, payback = price / marginal-R, horizon H = 90 days. Arm A = DECISION (seedless deterministic exact integer trajectories, plateau as exact Fraction at the final state, wall day = first check-in where every remaining positive-marginal purchase has payback > 14 days, per-purchase log, cumulative spend, zero-marginal-hen share); Arm S = robustness (seeded: gaps uniform int {⌈Δ/2⌉..⌊3Δ/2⌋}, skip prob 1/10, N = 2,000/cell via random.Random(20261341), pinned loop and draw order gap-then-skip, plateau = mean coins/day over days 76–90; degenerate-jitter identity gate ≡ Arm A EVENT-FOR-EVENT per cell). Seeds 20261341 (Arm S main) / 20261342 (stability, N = 500, ruling through twin evaluators) / 20261343 (reporting legs: Δ ∈ {300, 604800}, κ ∈ {1/3, 2/3}, jitter widths {±1/4, ±3/4}·Δ, P_max ∈ {7, 28}, WHALE unbounded-wallet leg, knob table EGG_VALUE = 1 / LAY_INTERVAL = 600, design-ceiling row R(100, 10, Δ) = {32,640; 8,160; 2,040; 340}) / 20261344 (aux, never read by any decision number) — the ONLY four, pre-registered, strictly above the P050/V061 high-water 20261340. Decision rule pre-registered, evaluated IN ORDER: (1) REJECT FIRST iff Arm-A plateau(best-of-family, Δ) ≥ κ·E[!daily] = 169201/200 = 846.005 coins/day at ≥ 2 of 4 decision cadences AND the same cells confirm in the jittered Arm-S mean with ≥ 4·SE headroom AND each firing cell's closed-wallet cumulative spend to plateau ≤ 30·E[!daily]; (2) APPROVE iff plateau(best-of-family) < κ·E at EVERY cadence in both arms AND first 3 purchases each pay back ≤ 7 days at every cadence AND wall day ≥ 10 at ≥ 3 of 4 cadences, stability-reproduced; (3) NULL otherwise, five registered axes (cadence-straddle / idle-dead / family-split / arm disagreement / margin-thin). Gates F1–F6 (price tables incl. coop total 44,506; settle idempotence/composition/cap clamp/zero-hen clock/remainder preservation on a pinned state grid; L2 arithmetic — exactly 40 coins at t = 6,000 s, zero further at 7,200 s; E[!daily] = 169201/100 exact Fraction; daily-hen-worthlessness — 2nd-hen marginal exactly 0 at Δ = 86400 for EVERY coop level 0..10 since 288 ≥ 170; hand trajectory Δ = 3600 GREEDY check-ins 1–5 eggs {12, 12, 20, 20, 20} coins {24, 24, 40, 40, 40} buys {—, hen#2@40, —, —, coop L1@100} wallet {24, 8, 48, 88, 28}) + monotonicity theorems (R in n and L; plateau along the divisor chain 86400→14400→3600→900 at fixed state; wall in P_max; closed ≤ WHALE) + Arm-S degenerate ≡ Arm-A identity + draw-count sentinels (2/check-in) + twin independently-written decision evaluators + two-process byte identity by external sha256 + CPython minor pinned. Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT — plateaus 8,064 / 4,560 / 1,140 / 130 coins/day at Δ = 900/3600/14400/86400, three of four cells over the κ = 1/2 band, walls ~3.7/1.4/3.5/9.0 days. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner), zero repo/network reads at verdict time. Build subtree `sims/verdict-062-chicken-farm-faucet/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 051 + VERDICT 062 appended to sim-lab `control/outbox.md` only, never echoed to idea-engine).

## What happened

Built `sims/verdict-062-chicken-farm-faucet/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 051 block / idea doc @
idea-engine main a500048, the superbot head harvested FIRSTHAND @ affd7ea at
drafting; this session hermetic — zero repo/network reads at verdict time)
committed BEFORE the runner. Git trail (PR #120): 9310f03 (born-red card) ->
1be87ff (fixtures) -> b0c01ad (runner farm_faucet_sim.py + accepted run:
results.json, run-stdout.txt, README.md, REPORT.md) -> 336e0d2 (merge of
main after VERDICT 061 / PR #119 landed mid-session) -> 196399d (INTAKE 051
+ VERDICT 062 ledger) -> this flip. Claim-first: idea-engine PR #374, merged
before any sim-lab work landed.

**Run:** `SELF-CHECKS: 35 passed, 0 failed`, exit 0, ~63 s; stdout +
results.json byte-identical across two full process runs by external sha256
(run-stdout sha256 7c3f182c..., results sha256 fc7608e5..., re-confirmed on
a third timing run); CPython 3.11 pinned, asserted. Gates all green: F1-F6
exact (price tables incl. coop total 44,506; settle identities; the L2
40-coin gate; E[!daily] = 169201/100; daily-hen-worthlessness over all 11
coop levels; the hand trajectory), all four monotonicity theorems, Arm-S
degenerate jitter == Arm A EVENT-FOR-EVENT on all 20 cells with zero draws,
draw sentinels exact (228,644,714 / 57,160,786 / 48,796,580 on seeds
20261341/42/43; aux 20261344 zero-draw by getstate — new high-water
20261344), twin evaluators agree everywhere.

**Ruling: reject.** REJECT (checked FIRST) FIRES: plateau(best-of-family)
>= 169201/200 = 846.005 coins/day at 3 of 4 cadences — 8064 (GREEDY, 15 min,
9.53x the band) / 6720 (PAIR, 1 h) / 1320 (PAIR, 4 h) vs 130 (24 h, under) —
every firing cell Arm-S-confirmed (thinnest headroom 289.61 vs 4*SE 4.17),
every ladder self-funded (max spend 22,602 <= 30*E = 50,760.3). Mechanism:
below the cap a hen's marginal income is cadence-independent (576/day), so
the 1.55x sink admits 13 extra hens at any sub-4h cadence while the cap
zeroes exactly the 24 h audience — the sink binds only where the faucet was
already tiny. L2 itself is arithmetically exact (F3); L1's generalization
from it is what fails. Stability leg reproduces REJECT through both
evaluators; the same 3 cells fire across the whole kappa sweep and both
jitter widths. Drafter's disclosed landing reproduced EXACTLY on every
disclosed quantity — and the from-scratch agreement caught THIS session's
own scratch error (a hen-price index off-by-one predicting n=13), not the
drafter's.

Walls: none new — REPORT.md rode a shell heredoc per the standing V054-V060
Write-tool classification (report-file policy known from orders; not
re-probed this session; fixtures, the runner, README, and the card all went
through Write). ASK 003 corridor: main moved DURING this session (6cb58bb ->
d2261a1, VERDICT 061 via PR #119); merged main INTO the branch (336e0d2,
never rebase), blocks ordered after V061 — and the mtime defect then BIT
locally: post-merge `check --strict` reported all-green with this card still
in-progress (V061's completed card became mtime-newest), while CI's
added-card gate correctly held the born-red red (log verbatim:
"[session-card-hold] ... designed hold, not a defect") — disclosed here per
orders, not fought. Collision greps: VERDICT 062 zero hits at session-start
HEAD 6cb58bb and re-grepped at d2261a1 immediately before the append. One
local nuisance, not committed: `.substrate/guard-fires.jsonl` dirtied by
every local `check --strict`; restored before each commit. `control/
inbox.md`, both status heartbeats, and idea-engine's outbox untouched. PR:
https://github.com/menno420/sim-lab/pull/120 (READY; merge-on-green owns the
merge — zero agent merge/arm calls; CI polled 1 of <= 3 times pre-flip).

## 💡 Session idea

Payback-gated purchase-ladder registrations should ship the closed-form
ADMISSION SET as a fixture-level gate — which purchases the payback rule
admits, derived from the committed tables alone, no trajectory needed — and
this session is the existence proof of both halves. Below the cap the
marginal income of a generator is cadence-independent (here 576 coins/day
per hen), so the P_max rule admits exactly the prefix of the price ladder
with price <= marginal * P_max (here 8064): the entire GREEDY hen ladder,
the wall state, and therefore the plateau are TABLE LOOKUPS, not emergent
sim output. Shipping that one-line derivation in fixtures.json does three
things: (a) turns the headline plateau into a differential identity the
trajectory must reproduce (a stronger self-check than any invariant, in the
family of V060's closed-form-plateau idea but for the DECISION number, not a
reporting curve); (b) would have caught this session's only defect — the
scratch hand-derivation mis-indexed hen#14's price (11923 for 7692) and
predicted n=13, an error the admission-set formula cannot make because it
reads the table, not a hand-walk of it; (c) prices the knob sweep for free —
admission prefix as a function of (EGG_VALUE, LAY_INTERVAL, P_max) is
closed-form, so a drafter can pre-compute every knob row exactly instead of
disclosing approximations. Kin, deduped at flip time (grep .sessions/ +
control/outbox.md for "closed form", "admission", "ladder"): V060's 💡 ships
the exact safe INTERVAL of a reporting-only conditional curve; this ships
the exact PURCHASE SET behind the decision number itself — different object,
different consumer (the self-check gate vs the per-printer test). Anchors:
farm_faucet_sim.py `Ctx._qualify` (the payback gate the closed form
inverts), REPORT.md drafter-comparison paragraph (the off-by-one this idea
would have made impossible).

## ⟲ Previous-session review

PROPOSAL 051's drafting session (idea-engine PR #373) is the direct
predecessor, and its work product held up under zero-trust re-derivation
better than any predecessor yet: the disclosed expected landing reproduced
EXACTLY on every disclosed quantity — all four greedy plateaus, all four
walls, the 21,887-coin self-funded ladder, the n=8/L=5 myopic stop — turning
this verdict session into a digit-for-digit differential test that ended up
falsifying the VERDICT session's own scratch arithmetic instead of the
drafter's, which is the disclose-your-hand-harness norm working at full
strength. One genuine loose end: the parenthetical PAIR-edge figure ("joint
payback 7.6 days past the myopic stop") was not pinned to a state or a
price-index and did not reproduce as a number (the committed tables give a
~4.41-day joint payback for hen#9+coop at the n=8/L=5 stop; PAIR's actual
first pair fires even earlier) — the mechanism it flagged is real and
decision-relevant (PAIR pulled the 4 h cell over the band), but future
drafts should pin reporting-only parentheticals with the same state+index
rigor as decision claims, because the verdict session will try to reproduce
every number it is shown.

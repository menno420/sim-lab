# Session — VERDICT 053 — Channel concentration vs diversification at fixed build budget: does deepening the one channel with 0 organic sales beat probing fresh ones? (idea-engine PROPOSAL 042, venture rotation round 7)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-053 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 042 (2026-07-13T18:33:00Z, status sim-ready, landed via idea-engine PR #333 → main 94fd30c; claim landed via idea-engine PR #334, `control/claims/`-ritual reserving INTAKE 042 + VERDICT 053 and branch claude/verdict-053-channel-concentration; offset map PROPOSAL 042 → VERDICT 053, +11 per the docs/current-state.md rule — the number RESERVES, never the position; P041 → V052 rides a parallel live session, PR #104, untouched by this session) — "channel concentration vs diversification at fixed build budget": under the pinned model (one INCUMBENT channel + K = 3 untested channels u1–u3, each carrying an unknown per-product-exposure organic-sale rate p_c on the grid P = {0, 1/50, 1/10, 1/4, 1/2}; channels INDEPENDENT; 9 pre-registered prior cells = 3 optimism pmfs — SKEPTIC (1/2, 1/4, 1/8, 1/16, 1/16), NEUTRAL (1/5 ×5), HOPEFUL (1/10, 1/5, 3/10, 1/4, 3/20) — × incumbent evidence n_inc ∈ {7, 3, 1} exposures with 0 successes, incumbent posterior ∝ π(p)·(1−p)^n_inc, self-consistent Bayes, cell order pinned (SKEPTIC, NEUTRAL, HOPEFUL) × (7, 3, 1); budget T = 180k tokens/cycle, c_inc = 60k, c_new = 90k (sensitivity {60k, 120k} reporting-only), unspent tokens lost, horizon H = 4 cycles (sensitivity {2, 8} reporting-only); policies pinned exactly — CONCENTRATE 3 incumbent builds/cycle (12 exposures), SPLIT 2 untested builds/cycle round-robin u1,u2,u3 → (3, 3, 2), ETC cycle 1 = u1 + u2, cycle 2 = u3 + one incumbent (150k spent, 30k lost), then commit cycles 3–4 wholly to the argmax posterior-mean channel on all evidence, ties incumbent → u1 → u2 → u3, no re-switch), measure P_any = P(≥1 launched product records ≥1 organic sale by horizon end) per (cell, policy) in Arm A (DECISION arm — seedless exact fractions.Fraction enumeration: CONCENTRATE/SPLIT closed sums, ETC exact enumeration ≤ 5⁴ rate combos × 2⁴ probe patterns) confirmed by Arm S (seeded MC, 200,000 trajectories/cell, random.Random(20261305), pinned draw order, common rate draws across policies; agreement gate |ArmS − ArmA| ≤ 5/1000 on every (cell, policy), any breach run-invalid). Legs: seed 20261305 main confirmation / 20261306 stability (20,000/cell, widened gate ≤ 15/1000, must reproduce the ruling) / 20261307 reporting (c_new, H, E_hits sensitivity confirmations, 20,000 each) / 20261308 aux (reserved, NEVER read by any decision number) — all strictly above the V052 high-water 20261304. Decision rule pre-registered, evaluated IN ORDER on Arm-A exact numbers with CON = P_any(CONCENTRATE), DIV = max(P_any(SPLIT), P_any(ETC)) per cell: REJECT FIRST (DIV − CON < 1/100 in ≥ 7 of 9 cells) → APPROVE (DIV − CON ≥ 1/100 in ≥ 7 of 9 cells AND in ≥ 2 of the 3 n_inc = 1 cells, stability leg reproducing) → NULL (anything else, five pre-registered axes: prior-straddle / evidence-straddle / margin-thin / arm disagreement / sensitivity straddle). Gates, run invalid on any failure: hand fixture F1–F6 (SKEPTIC n_inc = 1 posterior (800, 392, 180, 75, 50)/1497; NEUTRAL 2-exposure tail P_any = 14171/50000; committer tie → incumbent; SPLIT counts (3, 3, 2); budget arithmetic ⌊180/60⌋ = 3 / ⌊180/90⌋ = 2 / 150k + 30k; point-prior identity 1 − (9/10)^12); degenerate-zero gate; horizon monotonicity P_any(H=2) ≤ P_any(H=4) ≤ P_any(H=8) exact both arms; equal-cost direction check (reporting, flagged loudly); arm agreement gate; per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned. Fully hermetic: zero repo/network reads by the runner — fixtures.json constructed from the pinned constants (harvested venture-lab lines quoted verbatim @ be6c75d for citation only) and committed BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, the parallel VERDICT 052 session's files/claims/number (PR #104), and idea-engine's outbox untouched.

## What happened

Built `sims/verdict-053-channel-concentration/` — `fixtures.json` (every
registered constant verbatim from the PROPOSAL 042 block: the rate grid,
the three pmfs, the n_inc axis, T/c_inc/c_new/H/K, the allocation orders +
the ETC switch rule with its tie order, bands (1/100, 7-of-9, 2-of-3,
REJECT first), the six-item hand fixture, per-leg trajectory counts, seeds
20261305–308, the harvested venture-lab lines quoted verbatim @ be6c75d
for citation only) committed BEFORE the runner. Git trail (PR #105
commits — squash-merge erases branch SHAs from main, resolve via the PR):
a8e3ec8 (born-red card) → bd921d7 (fixtures) → b6551ee (runner + accepted
run) → 7193b72 (this session's guard-fires telemetry lines) → 86a27b6
(merge of origin/main after PR #104 / VERDICT 052 landed mid-session —
merged IN, never rebased; see ⟲ for the guard-fires conflict) → ba75cca
(ledger) → this flip.

**Run:** `SELF-CHECKS: 297 passed, 0 failed`, exit 0, ~32 s; stdout +
results.json byte-identical across two full process runs by external diff
(no wall-clock in any output; results sha256 8c149d8d…); CPython 3.11
pinned, asserted. Gates all green: hand fixture F1–F6 (the SKEPTIC/n1
posterior (800, 392, 180, 75, 50)/1497; the NEUTRAL 2-exposure tail
14171/50000; the committer tie → incumbent, bare rule AND end-to-end at a
point-mass prior; SPLIT counts (3, 3, 2); the budget arithmetic; the
point-prior identity 1 − (9/10)^12); degenerate-zero exact; horizon
monotonicity exact in Arm A and by-construction (nested prefix draws) in
Arm S; equal-cost direction check clean (no anomaly); arm agreement main
leg worst |ArmS − ArmA| = 0.00199 ≤ 5/1000; per-leg draw sentinels exact
(aux 20261308 ZERO draws); twin decision evaluators (Fraction
comprehension vs integer cross-multiplication) agree. No fix-forwards —
the first complete run of the registered pipeline is the accepted run.

**Ruling: approve.** REJECT (checked FIRST) does not fire: DIV − CON <
1/100 in 0 of 9 cells. APPROVE fires: DIV − CON ≥ 1/100 in 9/9 cells AND
3/3 n_inc = 1 cells (min margin SKEPTIC/n1 ≈ 0.1147, 11× the band), the
seed-20261306 stability leg reproduces (worst delta 0.01195 ≤ 15/1000).
SPLIT carries DIV in all nine cells; the mechanism is dead-channel-mass
hedging, not exposure count (single-channel P_any is capped by
1 − P(channel dead); three independent draws hedge that event). Honest
limits shipped: the E_hits inversion (CONCENTRATE buys more expected sales
at NEUTRAL/n1 while losing on P_any by 0.199) and the located 2×-cost
boundary (HOPEFUL/n1 flips sign at c_new = 120k, −0.0159; no band conjunct
crossed — straddle NONE). Landed INTAKE 042 (accepted) + VERDICT 053
(finalized, approve) in `control/outbox.md` (append-only; `## VERDICT
053`/`## INTAKE 042` collision-grepped at origin/main 022c109 at session
start and re-grepped at dfbc0e9 after the mid-session merge — none).
`control/inbox.md`, both status heartbeats, the VERDICT 052 session's
files/claims/number, and idea-engine's outbox untouched; claim rode
idea-engine PR #334 (enabler-merged 18:42:21Z). No walls hit; @codex
suspended per dedc12e — `codex: none this cycle`. PR:
https://github.com/menno420/sim-lab/pull/105 (READY; merge-on-green owns
the merge — zero agent merge/arm calls).

## 💡 Session idea

A registration can pin every CONSTANT and still underdetermine a
SENSITIVITY leg: PROPOSAL 042 pins the ETC schedule as literal builds
("cycle 1 = u1 + u2, cycle 2 = u3 + one incumbent") — derived from
c_new = 90k — then registers c_new ∈ {60k, 120k} as a reporting axis
without saying how the schedule re-derives. At 120k the pinned cycle 1
is budget-INFEASIBLE (2 × 120k = 240k > 180k), so the implementer must
invent a rule at verdict time (this session: deterministic greedy probe
packing, disclosed in the fixture and gated to reproduce the pinned
schedule exactly at base). The failure mode it arms: two honest
implementations of the same registration produce different sensitivity
tables — quiet non-reproducibility exactly where the axis is supposed to
locate boundaries. Fix, drafting-side and cheap: a registration lint —
every sensitivity axis must name the DERIVATION RULE for each pinned
quantity that depends on it (e.g. "builds/cycle = ⌊T/c⌋; probe schedule =
greedy in queue order u1, u2, u3, inc"), and a pinned schedule stated as
literal builds is only legal for constants no sensitivity axis touches.
Anchors: idea-engine PROPOSAL 042 block (the ETC clause vs the c_new
sensitivity pair); this repo
`sims/verdict-053-channel-concentration/fixtures.json`
(`ETC_generalized_note`) + REPORT.md § Boundaries. Dedup: grep of
.sessions/, control/outbox.md, and docs/ for sensitivity-schedule /
derivation-rule ideas at flip time — none; V052's 💡 is the nearest kin
(registered hand-fixture VALUE wrong; validator recomputes derived
columns) but targets fixture-value correctness, not the missing
re-derivation rule under a sensitivity axis — a validator on V052's
design would not have caught this, because no registered VALUE is wrong;
a registered RULE is absent.

## ⟲ Previous-session review

VERDICT 052 (spool-scale margin, PR #104) is the direct predecessor and
this session's mid-flight neighbor — its merge landed while this branch
was open, exercising the push-race rule (merged IN at 86a27b6, never
rebased; both sessions' ledger blocks kept in order, numbers stable
throughout). Its disciplines transferred whole: claim-first, fixtures-
before-runner with PR-resolvable citations, the collision re-grep at
append, REJECT-first evaluation, and the honest-null posture (its NULL on
TABLE-PARITY is the lineage's proof that the rules output whatever they
output — this session's APPROVE rode the same order). Two predicted
defects graduated to REPRODUCED this session: (1) V051's 💡 (the tracked
`.substrate/guard-fires.jsonl` shared-append hazard — "armed, not
hypothetical") fired its first REAL merge conflict: V052's committed
guard-fire lines vs this session's collided at the origin/main merge,
resolved as a timestamp-ordered union in 86a27b6 — the ~98%
shared-append conflict rate the claims README cites is now a live sim-lab
citation, and the V051 fix sketch (shard per session or untrack) has its
evidence commit; (2) the ASK 003 mtime corridor fired again exactly as
V051's card described it: after the mid-session merge imported V052's
completed card, local `check --strict` flipped green by validating the
mtime-newest card — verbatim "check: session log
.sessions/2026-07-13-verdict-052-spool-scale-margin.md complete." — while
this card still said in-progress; CI's substrate-gate (diff-touched card)
stayed the only honest local-red signal, per ASK 003 disclosed-not-fixed.

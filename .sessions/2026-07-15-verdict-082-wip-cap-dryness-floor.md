# Session — VERDICT 082 — the never-dry pipeline is a limit, not a rule: WIP cap 3 prices the committed never-dry floor at a fifth of the clock, and the tax is variance-born (idea-engine PROPOSAL 069, the round-14 FLEET-BACKLOGS rotation opener, closed 2-station CONWIP loop / truncated-geometric stationary law; P069 → V082 under the +13 offset)

> **Status:** `complete`
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 082 for idea-engine PROPOSAL 069 (the WIP-cap
dryness floor, `ideas/fleet/wip-cap-dryness-floor-2026-07-15.md`, read at
idea-engine origin/main `10533ae`, landed via idea-engine PR #432 merged
~2026-07-15T07:45Z; outbox block stamped 2026-07-15T07:39:22Z in the LIVE
`control/outbox.md`, grounding pin `dc155cb`). One slice, one branch
(`claude/2026-07-15-verdict-082-wip-cap-dryness-floor`, PR #151), one
verdict. NUMBERING, verified literally at sim-lab origin/main `fb31495`
(VERDICT 081 merged via PR #150): newest `## VERDICT` header is 081,
`## VERDICT 082` and `## INTAKE 069` collision-grepped clean (outbox +
archives + current-state + remote refs — no competing branch or PR), so
idea-engine PROPOSAL 069 → **VERDICT 082**, the +13 offset's sixth row
(map row extension landed in `docs/current-state.md` this same PR).
Worker session; `control/status.md` and `control/inbox.md` untouched
(ledger appended to `control/outbox.md` only; delivery is the manager's
Q-0264 fan-in). NOT fully hermetic at drafting — the MEASURED constants
(the inbox:31/:50/:54/:188/:219 cap/floor/dry-event sentences, the
P064–P068 header gaps 1622/2674/2263/1387 s, the S_v = 2246 s pair at
outbox:15, the archive-sweep night 30847/18 and lifetime 391243/67
aggregates) were re-verified FIRSTHAND at idea-engine origin/main this
session BEFORE fixture-writing — all matched, zero harvest anomalies; the
runner itself is hermetic (reads only its committed fixtures.json, zero
repo/network reads at verdict time). The V080/V081 dirty-worktree guard
fired again at session start (the local sim-lab tree carried a prior
worker's uncommitted `.substrate/guard-fires.jsonl` on the verdict-080
branch), so this slice worked from a fresh shallow clone and pushed from
there. This card held the substrate gate red deliberately until this flip
(the born-red discipline — the designed hold was the only red this branch
produced itself).

## What happened

Built `sims/verdict-082-wip-cap-dryness-floor/` under the standing
discipline: fixtures.json committed BEFORE the runner (card c90a9cf →
fixtures 447567b → runner 5b5df16 → accepted run 181c211 → control
appends c8663f3), three-arm: Arm A seedless truncated-geometric closed
form (exact Fractions over the full K ∈ {1, 2, 3, 4, 6, 12} × r ∈ {1/2,
3/4, 1, 4492/3973, 40428/30847, 2} grid; decision-bearing), Arm B
independently-written twin (builds the (K+1)-state generator Q and solves
πQ = 0, Σπ = 1 by Fraction Gaussian elimination — never via the closed
form; exact-equal on every published number at all 36 cells; second
decision evaluator), Arm R seeded discrete-event traces of the literal
loop at the decision cell, reporting-only (100k main @ 20261610, 20k
stability @ 20261611, three service shapes at the same pinned means;
presentation row order @ 20261612; aux 20261613 asserted never read — the
drafter's registered allocation IS the session seed set, the V077–V081
precedent; the 20261604–609 gap stays the drafter's disclosed buffer,
unused; registry high-water 20261613). 606 self-checks 0 failed, exit 0,
~0.6 s/run; byte-identical double run (sha256 in REPORT.md); CPython 3.11
asserted; no fix-forwards after the runner landed — the first complete
in-repo run is the accepted run.

**VERDICT 082 — REJECT, exactly at the drafter's disclosed landing (zero
anomalies — the second P06x head in a row whose disclosed values ALL
reproduced against a zero-trust re-derivation).** D(3, r̂) =
62712728317/304425042745 ≈ 0.2060 ≥ 1/10 (2.06×), grid-worst D(3, 2) =
1/15 ≥ 1/20 (1.33×), D(12, r̂) ≈ 0.0332 ≥ 1/40 (1.33×), B(3, r̂) ≈
0.2977 ≥ 1/5 (1.49×). The citable structure: T1 impossibility (π(0) > 0
under any finite cap — the seat's two lived DRY events are arithmetic,
not anomalies), T2 frontier (K→∞ limit max(0, 1 − r) exactly, approach
verified at 2.27e−13; on r < 1 drafting speed is the only lever), T3
balanced knee (quarter-quarter-3/4 at the committed cap, ΔD(3→4) = 1/20),
the swap symmetry (one seat's dryness is the mirror seat's backpressure),
and the variance attribution D_det(3, r̂) = 0 exactly — clockwork at the
same means satisfies the committed pair from K = 2 up. The K*(r, d)
safe-cap table shipped (r ≤ 3/4 unreachable at every band — a theorem,
not a timeout). One Arm-R row did real epistemic work and is named in
REPORT/VERDICT: the measured burst-gap empirical mix landed D̂ ≈ 0.00023
— near the deterministic corner, far from the memoryless 0.206 — so the
within-burst regime is near-clockwork and the REJECT-ward dispersion
lives ACROSS regimes (lifetime anchor D(3, r_life) ≈ 0.629, where both
lived DRY events actually occurred).

## Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 081, sim-lab
PR #150): V081's 💡 — ESTIMAND PINS ("one symbol, one aggregation scope":
a registered metric ships its per-unit quantity, conditioning event, and
symmetry) — was applied live in this slice, at fixture time: Arm R's D̂
had three candidate readings (time-average, cycle-average,
embedded-jump-chain average) and C4 pinned the TIME-average as the
stationary law's own estimand BEFORE the runner existed — exactly the
false-INVALID class V081's idea targets, resolved at registration cost
zero. The decision metrics themselves (D = π(0), B = π(K)) carried no
aggregation ambiguity, so the estimand layer bit only on the seeded arm.
V080's executable-theorem export was also honored structurally: all three
P069 theorems arrived as exact F2 gates and all passed. V081's other
carried conventions (born-red card / collision-grep / no-claim-file
reservation; registered-allocation-as-session-seed-set) rode unchanged;
V081's C5-style unsigned formalization choice recurred here in miniature
as C3 (the grid-robustness clause quantifies over the REGISTERED six-cell
r grid, r_life excluded as a reporting anchor — disclosed in fixtures
before the runner, and in this case the idea file's own Grids line signs
the reading).

💡 **Session idea (genuine, this session):** DISPERSION WITNESS PINS —
a measured MEAN anchor should ship with its measured DISPERSION witness.
Every registration in the P048–P069 family pins mean anchors (here S_d,
S_v) and then chooses a service-shape decision model (here memoryless)
whose entire decision content beyond the means is a dispersion
assumption — yet the harvested integers already contain the dispersion
the record actually lived: the four burst gaps 1622/2674/2263/1387 have
CV² ≈ 0.066, fifteen-fold below exponential's CV² = 1, and this was
computable at drafting for free. This slice only surfaced the gap AFTER
the run, via the Arm-R empirical row (D̂ ≈ 0.00023 vs the pinned model's
exact 0.206): the memoryless 20.6% headline is a between-regimes price
wearing a within-regime costume, and the honest carrier of the REJECT-ward
direction (regime switching, burst vs day-pause) had to be reconstructed
in prose in the boundaries section. The convention: any registration that
pins a measured mean anchor MUST also pin the same sample's dispersion
witness (CV² or the raw gap multiset — it already commits the integers
anyway), and a pinned decision model whose implied CV² is an order of
magnitude off the witness is BY CONVENTION flagged at registration — the
decision may still ride it (declared, directional, as P069 in fact did),
but the flag forces the drafter to name WHICH regime carries the claimed
dispersion, turning a post-run Arm-R surprise into a drafting-time
sentence. Dedup: distinct from V077's 💡 (seeded-arm representation
equivalence), V078's (self-evaluating inline arithmetic), V079's
(machine-readable disclosed VALUES), V080's (executable theorem CLAIMS),
and V081's (ESTIMAND pins — aggregation scope of a symbol): those govern
how claims/values/symbols are stated; this governs which MOMENTS of the
harvested data a registration must commit — the moment layer none of
them touch. Concretely for the kit: the proposal template's
measured-constants section gains a `dispersion:` line per mean anchor
(witness statistic + the pinned model's implied value + the regime that
carries any gap), checkable by the verdict runner as a reporting row.

📊 Model: Claude Fable family · high · verdict-sim slice-worker session

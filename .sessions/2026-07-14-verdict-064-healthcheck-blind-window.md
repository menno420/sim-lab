# Session — VERDICT 064 — The healthcheck blind window: what does the websites repo's shipped 6-hourly point-probe liveness net (`17 */6 * * *`) actually SEE, and does the backlog's "up to 6 hours" hard window survive the workflow's own delay-or-drop caveat? (idea-engine PROPOSAL 053, ORDER 003 FLEET-BACKLOGS rotation slot, round 10 opener)

> **Status:** complete
> 📊 Model: Claude Fable (family) · 2026-07-14 · verdict-064 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 053 (`## PROPOSAL 053 · 2026-07-14T01:15:36Z · status: sim-ready`, landed via idea-engine PR #379 → main 39e35ec7a0021f50e9640a09c8b7dd39df4fe793; numbering INTAKE = proposal number, PROPOSAL 053 → VERDICT 064 per the established P050→V061 / P051→V062 / P052→V063 offset map) — price the websites repo's shipped healthcheck cadence constant (`.github/workflows/healthcheck.yml` @ websites `3076e9d`, cron `17 */6 * * *` line 22) and the backlog's committed "up to 6 hours" hard-window claim (docs/ideas/backlog.md line 890) under the pinned probe-and-outage model, per the idea doc `ideas/websites/healthcheck-blind-window-2026-07-14.md` @ idea-engine main 39e35ec. Pinned model (all times integer minutes, all probabilities exact `fractions.Fraction` on equiprobable integer lattices): probe cadence grid T ∈ {60, 180, 360, 720, 1440} min, fires scheduled at k·T (shipped cell T = 360; the wall-clock minute-17 phase cancels under the uniform onset phase); per-fire delivery noise — independent drop q = 1/20 and delay d ~ uniform integer {0..30} min (INVENTED-pinned-disclosed; sensitivity pairs q ∈ {0, 1/10} and delay {0}/{0..60}, REPORTING ONLY); transient outages D ∈ {5, 30, 60, 180, 360} min at uniform onset phase φ ∈ {0..T−1}, equiprobable headline mix (short-/long-heavy sensitivity mixes), DETECTED iff some non-dropped fire executes inside [φ, φ+D); persistent dead-until-fixed faults with detection latency L = earliest successful execution at/after onset minus onset, WINDOW(T) = P(L > 360). Arm A = DECISION (seedless exact Fraction full-lattice enumeration, alone decision-bearing); Arm B = confirmation (seed 20261349, N = 200,000 common-random-numbers scenario draws across all five T cells, agreement gate |EST − EXACT| ≤ 1/100 absolute AND ≤ 4·SE per reported cell, both metric families); zero-noise control seed 20261350 (q = 0, d ≡ 0 — exact identities MISS(T,D) = (T−D)/T for D ≤ T incl. MISS(360,180) = 1/2, WINDOW(360) = 0, WINDOW(720) = 359/720, asserted in both arms); sensitivity reporting seed 20261351 (N = 20,000/world, never decision-bearing); stability leg seed 20261352 (N = 20,000, ruling class reproduced through twin independently-written decision evaluators). Decision rule pre-registered, applied IN ORDER at the shipped cell T = 360 under headline pins: REJECT FIRST (DET_mix(360) < 1/2 OR WINDOW(360) > 1/20) → INVALID (zero-noise identities / monotonicity theorems (DET(T,D) non-decreasing in D at fixed T; DET_mix(T) non-increasing in T; WINDOW(T) non-decreasing in q under CRN) / Arm-B agreement gate — report, no ruling) → APPROVE (DET_mix(360) ≥ 3/4 AND WINDOW(360) ≤ 1/100 AND stability reproduces) → NULL (pre-registered axes: band-straddle DET_mix(360) ∈ [1/2, 3/4) and/or WINDOW(360) ∈ (1/100, 1/20]; stability non-reproduction; sensitivity straddle — named, never ruling). Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT on BOTH conjuncts at DET_mix(360) = 123709/372000 ≈ 0.333 and WINDOW(360) = 22913/372000 ≈ 0.062, with the q = 0/d ≡ 0 decomposition DET_mix(360) = 127/360 ≈ 0.353 (structure, not noise) and WINDOW = 0 exactly (delivery-driven). Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads. Build subtree `sims/verdict-064-healthcheck-blind-window/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 053 + VERDICT 064 appended to sim-lab `control/outbox.md` only; nothing echoed to idea-engine). This card holds the substrate gate red deliberately until the final flip (the born-red discipline — that red is the ONLY acceptable red on this branch).

## What happened

Built `sims/verdict-064-healthcheck-blind-window/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 053 block / idea doc @
idea-engine main 39e35ec; the disclosed fixture-level choices — K = 9 fire
variates + coverage proof, the 19-draw scenario shape with CRN maps, the
exact-variance SE convention sqrt(Var_exact/N), control N = 20,000, the
sensitivity world order with the q-sweep under common random numbers, the
E[L] first-catch/geometric-tail method, the 1024-outcome brute-force
cross-structure at the shipped cell, the twin evaluators, the draw
sentinels — all pinned in the fixture BEFORE the runner) committed before
the runner. Git trail (PR #122): fe20dfc (born-red card) -> 231b03f
(fixtures) -> 4f0e899 (runner healthcheck_blind_window_sim.py + accepted
run: results.json, run-stdout.txt, README.md, REPORT.md) -> 8df375e
(INTAKE 053 + VERDICT 064 ledger) -> this flip. Reservation disclosure:
no idea-engine claim file was created this slice (the V062/V063 pattern);
the orchestrator brief routed the reservation through the born-red card
as first commit + PR #122 opened READY + the collision-grep protocol —
`VERDICT 064`/`INTAKE 053` grepped clean at session start (f37d9b1,
01:39:40Z) and re-grepped clean immediately before the ledger append
(main never moved; the first verdict slice in three with no mid-session
race).

**Run:** `SELF-CHECKS: 886 passed, 0 failed`, exit 0, ~6 s/run; stdout +
results.json byte-identical across two full process runs by external
sha256 (run-stdout 5f205ebf..., results c6ed3604...); CPython 3.11
pinned, asserted. Gates all green: transcription exact; zero-noise
identities exact in BOTH arms (Arm A all 25 MISS cells + WINDOW(360) = 0
+ WINDOW(720) = 359/720; Arm B seed 20261350 per-draw indicator
identities on every scenario x T x D); the 1024-outcome brute-force
enumeration == product form on every decisive cell; monotonicity theorems
(DET in D, DET_mix in T, WINDOW in q — exact AND per-scenario CRN); 315
agreement gates inside 1/100 + 4*SE (worst dev 0.00649 vs 0.01/0.01414);
draw sentinels exact (3,800,000 / 380,000 / 1,140,000 / 380,000; the ONLY
four RNGs, pinned order, new registry high-water 20261352).

**Ruling: REJECT** (checked FIRST, fires on BOTH conjuncts):
DET_mix(360) = 123709/372000 = 0.3326 < 1/2 AND WINDOW(360) =
22913/372000 = 0.0616 > 1/20 — the shipped 6-hourly point-probe is a
persistent-fault net (93.7% at D = 360), not a blip net (7.9% at D = 30),
and "up to 6 hours" fails ~1 persistent fault in 16 under the workflow's
own caveat. The registered decomposition confirmed exactly: zero-noise
DET_mix = 127/360 (structure, not noise), zero-noise WINDOW = 0
(delivery-driven). Stability (seed 20261352) reproduces REJECT through
both twin evaluators. Drafter comparison: every disclosed EXACT Fraction
reproduced from scratch; two reporting-only drafter anomalies reported
first-class — A1: the registered zero-noise E[L] sanity row (T+1)/2 is
off by one ((T-1)/2 is forced by the registration's own WINDOW(720) =
359/720 identity); A2: the disclosed T = 60 WINDOW exhibit ~3.7e-11 is
off by 10^3 (exact 7413/198400000000 ~ 3.74e-08); plus finding A3: the
d = 0 sensitivity world lands WINDOW 19/144000 knife-edge BELOW the 1/20
edge — named straddles, never ruling.

Walls: none new. REPORT.md and the ledger append rode shell heredocs per
the standing V054–V063 classification; fixtures, runner, README, and this
card went through Write. ASK-003 mtime false-green: not exercised (no
mid-session merge of main; the born-red hold stayed the only local red at
every push). `control/inbox.md`, both status heartbeats, and idea-engine's
outbox untouched. Session-card markers: `**Status:**` complete, 💡 below,
previous-session review below, `📊 Model:` family-level. PR:
https://github.com/menno420/sim-lab/pull/122 (READY; merge-on-green owns
the merge — zero agent merge/arm calls).

## 💡 Session idea

Disclosure PRECISION predicted disclosure CORRECTNESS exactly in this
slice, and that is a checkable drafting rule: require every
drafter-disclosed reference value to be an exact rational (or explicitly
tagged hand-waved), and pin the boundary convention the closed forms ride
on as its own fixture constant. Proof case: PROPOSAL 053 disclosed nine
values as exact Fractions and every one reproduced from scratch to the
digit — while BOTH drafter errors this session found lived in the only
two non-exact disclosures (the symbolic E[L] sanity row (T+1)/2, refuted
by the registration's own WINDOW(720) = 359/720 identity which forces
L(phi=0) = 0 and hence (T-1)/2; and the float exhibit "WINDOW ~ 3.7e-11",
off by three orders of magnitude from the exact 7413/198400000000). Both
errors trace to one unstated boundary convention — does a probe firing
exactly at onset count? — so the one-line guard is: any registration
pinning two or more closed forms over the same lattice must state the
boundary convention as a fixture constant and machine-check each closed
form against it at drafting (a ~5-line stdlib script, the same cost class
as V063's degeneracy check). Kin, deduped (grep .sessions/ + outbox for
"exact rational", "off-by-one", "boundary convention", "degenerate"):
V063's 💡 priced an UNINFORMATIVE reporting leg (identity problem, remedy
= a vector comparison); V061's an UNDERPOWERED stability conjunct (noise
problem, remedy = size N); this prices an INCONSISTENT registration
(convention problem, remedy = disclose exactly + pin the convention) —
same genus (reporting-side pins get less drafting scrutiny than decision
numbers), third distinct species, one-line guard each. Anchors:
REPORT.md anomalies A1/A2; results.json
`E_L_registered_sanity_row_matches: false`;
healthcheck_blind_window_sim.py `expected_L` + the A1 proof text.

## ⟲ Previous-session review

VERDICT 063 (coupon collector's tail, PR #121) is the direct predecessor.
Its 💡 — drafter-side degeneracy checks for reporting legs — reads
validated from here on a different axis: this session found the same
GENUS of defect (a reporting-side pin that fails its own registration's
frame) as a convention inconsistency rather than a degeneracy, which is
exactly the pattern its card predicted ("reporting legs get less drafting
scrutiny"). Its craft transferred verbatim and cheaply: the born-red ->
fixtures -> runner git trail, the twin evaluators, the counting-wrapper
draw sentinels, and the literal five-validity-gate REPORT closing it
restored (V064 keeps it; zero format drift for the next citer). Its
ASK-003 mtime false-green disclosure was the right call to write down —
this session armed for the same trap and never hit it (main never moved),
so the disclosure cost one paragraph and the arming cost nothing. One
honest nit back: V063's stability leg reports its class as
"REJECT_ARITH", a token outside the registration's class vocabulary
(REJECT/INVALID/APPROVE/NULL) — the next citer has to map it; V064's
stability leg reports plain "REJECT" through the same twin-evaluator
machinery, which costs nothing and keeps the ledger grammar closed.

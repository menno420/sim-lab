# Session — VERDICT 102 — two single-server queues at the SAME utilization ρ=0.8 meet a 10× SLA at wildly different rates because service VARIANCE, not mean load, sets tail risk: the CV=3 lane breaches sojourn>10 at 0.498 vs the CV=1 lane's 0.137 (ratio 3.638, clears the 2.5× floor by 22.49σ, gap 95.58σ), the Pollaczek–Khinchine mean wait anchors both lanes to within 0.72%/2.01%, the violation ratio is strictly monotone in CV crossing 2× at CV=1.5099 (in [1.36,1.66]), and re-provisioning the high-variance lane to a LOWER load ρ*=0.512 drives its violations back to 0.20σ of the low-variance lane — proving variance not ρ (idea-engine PROPOSAL 089, the round-19 fleet-external operations/capacity head; P089 → V102 under the +13 offset, the twenty-sixth row)

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · verdict-sim

Objective: produce VERDICT 102 for idea-engine PROPOSAL 089 (the
variance-blind provisioning trap, registered spec
`variance-blind-provisioning-trap-2026-07-16`, source header cited verbatim
`## PROPOSAL 089 · 2026-07-16T22:04:51Z · status: sim-ready`). One slice, one
branch (`claude/verdict-102-variance-blind-provisioning-trap`), one verdict.
NUMBERING, verified at sim-lab origin/main `4ec111e` (the tip is the #174
control inbox update): newest `## VERDICT` header in control/outbox.md is 101
(P088 → V101), and `## VERDICT 102` / `verdict-102` / `v102` collision-grepped
across .sessions/ + sims/ + control/ + docs/ returns exactly THREE
prediction-class hits and ZERO claim-class hits — the V101 card's next-2
pointer (`.sessions/2026-07-16-verdict-101-…md`), the coordinator heartbeat
`control/status.md` next-2 baton, and the `docs/current-state.md`
next-expected line — no `## VERDICT 102` ledger header, no competing
`sims/verdict-102-*` path, no session card for 102, no competing remote ref
(the V093 collision-grep classification doctrine: prediction-class pointers
are expected and non-blocking, claim-class surfaces are disqualifying). So
idea-engine PROPOSAL 089 → **VERDICT 102**, the +13 offset's twenty-sixth row
(map-row extension lands in `docs/current-state.md` this same PR). Worker
session; ledger appended to `control/outbox.md` only (`control/inbox.md`
untouched — manager-order file); this slice also refreshes the coordinator
heartbeat `control/status.md`. No idea-engine claim file written by this slice
(the V074/V077–V101 precedent — the collision-grep + born-red card + READY PR
bind the number). Seeds: **SEEDLESS** — the seeds are the in-file constants
S=[1001,1002,…,1012] (two `random.Random` instances per arm, one service
stream + one arrival stream, keyed by the deterministic integer formulas in
the module header), NOT a ledger draw; the next free block stays **20261730**,
untouched (the V099/V100/V101 SEEDLESS-baton precedent). This is a
fleet-external operations/capacity head (kin: the queueing/throughput family);
zero repo/network reads at verdict time, no wall clock, no PYTHONHASHSEED
dependence — every registered numeral re-derived from scratch by an
independent stdlib-only M/G/1 Lindley simulation. This card holds the
substrate gate red deliberately until the flip (the born-red discipline — the
designed hold is the only red this branch produces itself).

Flagged, decide-and-flag: (a) the live `control/outbox.md` measured ~617 KB
pre-append (measured this session) — above the fleet 200 KB rollover
threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5; the
V086–V101 precedent — append normally, follow-up is the manager's). (b) The
registration pins the world constants (λ=0.8, E[S]=1.0, W_target=10, N=200000,
warmup=20000, R=12, the CV grid, the two H2/exponential samplers, the seeding
formulas) exactly, but several REALIZATION choices are sim-chosen and disclosed
in fixtures.json: the exponential draw as `−m·log(1−u)` (version-independent,
not `random.expovariate`, so no CPython-version dependence in the stream); the
per-iteration draw order (service `S_i` drawn then arrival gap `A_i`, separate
streams so interleaving is immaterial); the first task draws no arrival gap
(Wq_1=0); the delta-method ratio SE and the linear-interpolation crossover
estimator; the decimal display convention. None touches a registered decision
value — all are ledgered as choices, not match claims. (c) ORDER-010(c) kit
upgrade v1.15.0 → v1.18.0 remains **PARKED** on owner authorization + the
ASK-005/006 watch (a verdict slice does not execute it; carried forward per the
V101 baton).

## What happened

Built `sims/verdict-102-variance-blind-provisioning-trap/` under the standing
born-red discipline (card committed FIRST, in-progress, before the runner).
Structure mirrors V101: a module docstring reproducing the source header + the
pinned world + the four gates + the decision rule + the determinism note; a
pinned-world constants block; pure-stdlib numeric helpers (`sample_std` ddof=1,
`pool`, `separation`, `wq_pk`); a unified balanced-means H2 service sampler that
DEGENERATES to plain exponential at CV=1 through the SAME code path (no special
case); the exact single-server Lindley recursion
`Wq_i=max(0,Wq_{i-1}+S_{i-1}-A_i)`, `sojourn_i=Wq_i+S_i` over N=200000
tasks/rep with a 20000-task warmup excluded from every metric; `simulate()` over
7 arms × 12 reps (laneA CV=1/ρ=0.8, the CV sweep 1.5/2.0/2.5/3.5, laneB
CV=3/ρ=0.8, laneBstar CV=3/ρ=0.512 via mean_s=0.64); `compute_gates()`; the
twin evaluators `decide_ifchain()` (short-circuit if/elif) and `decide_table()`
(independent table/loop) that must agree on token AND first-failing gate;
`build_fixture()` (seed-1001 first-20 service draws for lanes A+B + first-20
arrival gaps for lane A via repr, the H2 params, the P–K anchors, the gate
thresholds); `main()` accumulating a human log, writing results.json
(sort_keys, indent=2) + run-stdout.txt, printing the sha256 of both, the
`[ok]/[XX]` self-check list, and the VERDICT token.

**VERDICT 102 — APPROVE, all four gates R1→R2→R3→R4 pass, ZERO anomalies,
first_failing_gate None.** (R1) equal-ρ trap: viol_A=0.136890, viol_B=0.498021,
ratio 3.638115 (SE 0.050604) clears the 2.5× floor by **22.49σ**, gap 0.361131
(SE 0.003778) separated at **95.58σ**; (R2) P–K sanity: measured Wq 4.02873 vs
PK 4.0 (rel-err 0.72%) and 19.59726 vs 20.0 (rel-err 2.01%), both ≤5%; (R3)
dose-response strictly monotone with adjacent separations 30.50/15.27/9.15/
5.01/4.44σ, 2× crossover at **CV=1.5099** in [1.36,1.66]; (R4) re-provisioned
lane B* viol 0.136513, gap −0.000376 (**0.20σ**) from lane A, ρ_B*=0.512<ρ_A=0.8.
14 self-checks, 14 passed, 0 failed; exit 0; ≈6 s/run; byte-identical double run
(results.json 6718bd00…, run-stdout.txt 00a204d1…, fixtures.json 2b56c254…);
twin evaluators APPROVE/None both; CPython 3.11, stdlib only. The measured
numbers reproduce the proposal's disclosed calibration references (ratio≈3.67,
crossover≈1.51, R4 gap≈+0.0001 / ~0.05σ) from an INDEPENDENT re-implementation
— the born-red card is the only designed hold, no rehearsal fixes, the first
complete in-repo run is the accepted run. PR opened READY at slice start.

## Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 101, sim-lab PR #173,
`sims/verdict-101-berkson-admission-collider/`): a clean APPROVE landing whose
conventions this slice consumed wholesale — the born-red card / READY PR /
no-claim-file discipline, the module-docstring-reproduces-source-header shape,
the pinned-world constants block, the pure-stdlib numeric helpers
(`sample_std` ddof=1 / `pool` / `separation` carried verbatim), the
`simulate()`→`compute_gates()`→twin-evaluators→`build_fixture()`→`main()`
skeleton, the `[ok]/[XX]` self-check list, the SEEDLESS ledger baton (next free
block 20261730 inherited unchanged), and the +13 offset extended to its
twenty-sixth row in the same grammar. V101's twin-evaluator pattern (if-chain +
independently transcribed table agreeing on token AND first-failing gate)
transferred directly; V101's disclosed-realization discipline (sim-chosen
values ledgered in fixtures.json as choices not match claims) is honored here
for the exponential-draw form, the draw order, and the SE/crossover estimators.
One V101 side effect bound this slice, productively: its heartbeat/map/card
refresh planted the standing "next expected: PROPOSAL 089 → VERDICT 102"
pointers, so this session's numbering collision-grep HIT "VERDICT 102" three
times before any V102 work existed — all prediction-class, classified and
cleared per V093's collision-grep doctrine (a hit is disqualifying only on a
claim-class surface; next-expected pointers are predictions). Nothing was left
pending for this slice to resolve; the seed baton (20261730) and the parked
ORDER-010(c) kit upgrade both carried forward unchanged.

💡 **Session idea (genuine, this session):** A HOT-LOOP-INLINED SAMPLER NEEDS AN
EXPLICIT INLINE≡HELPER EQUIVALENCE SELF-CHECK — THE FIXTURE-MATCH CHECK CANNOT
CATCH THE DIVERGENCE. This is the first sim in the wave with a genuine hot loop
(7 arms × 12 reps × 200000 tasks ≈ 16.8 M Lindley iterations), so for speed the
service-time arithmetic `−m·log(1−u)` is INLINED into `simulate_rep`'s inner
loop rather than calling the `draw_service` helper. But the seed-anchored
fixture (`build_fixture` → `_first_service_draws`) pins the HELPER's stream, and
`fixture_matches_committed` builds AND verifies through that same helper — so if
the inlined loop arithmetic ever silently diverges from the helper (a
transposed phase test, a `1.0−u` vs `u−1.0`, a different multiply order that
perturbs the last ULP), the fixture check stays green while the actual
simulation drifts. The durable rule: whenever a sampler is inlined for
performance but ALSO exposed as a helper the fixture consumes, add a self-check
that runs BOTH on one identically-seeded probe stream and asserts equal `repr`
for N draws — the two transcriptions must be byte-identical, not merely
close. Guard recipe (code anchors): the check is
`sampler_inline_matches_helper` in
`sims/verdict-102-variance-blind-provisioning-trap/variance_blind_provisioning_trap_sim.py`
— it probes `random.Random(20260717)` through `draw_service(...)` and through a
literal copy of the loop body and compares 40 `repr`s; the test target is that
any future edit to the `simulate_rep` inner-loop service arithmetic OR to
`draw_service` must keep the two identical (a divergence trips exit≠0 before the
fixture check is even reached). Corollary: a control arm implemented as the SAME
code path at a boundary parameter (here laneA CV=1 degenerates through the
identical H2 sampler, no `if cv==1` branch) is more trustworthy than a control
on a separate branch — the same-path control cannot mask a branch-only bug.
Dedup: grepped .sessions/ + sims/ — prior cards discuss fixture pins, twin
evaluators, and determinism digests, but none inlines a sampler into a hot loop
(V101's metric loop is 2000 items, no inlining) and none records an
inline-vs-helper equivalence guard or the same-path-control corollary; this is
novel to the first large-N queueing sim in the repo.

📊 Model: opus-4.8 · high · verdict-sim

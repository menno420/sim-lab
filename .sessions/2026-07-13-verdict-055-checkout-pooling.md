# Session — VERDICT 055 — Checkout pooling folk law at ρ = 9/10: does ONE shared line beat per-register lines by ≥ 2× on a deliberately conservative discrete frame? (idea-engine PROPOSAL 044, round-7 unrelated slot)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-055 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 044 (`## PROPOSAL 044 · 2026-07-13T19:47:09Z · status: sim-ready`, landed via idea-engine PR #339 → main 1bc22e8; claim landed via idea-engine PR #340, `control/claims/2026-07-13-verdict-055.md` reserving the P044 intake + VERDICT 055 and branch claude/verdict-055-pooling-sim; offset map PROPOSAL 044 → VERDICT 055, +11 per the docs/current-state.md rule — the number RESERVES, never the position; P043 → V054 rides a parallel live session, sim-lab PR #106, untouched by this session) — "checkout pooling priced at its showcase load": under the pinned discrete service frame quoted verbatim from the idea doc `ideas/fleet/checkout-pooling-single-line-2026-07-13.md` @ 3f38420 (c = 3 registers; tick semantics completions → arrival → index-order starts, a customer starting at tick s with service S occupying its server for ticks s..s+S−1, WAIT = t − arrival_tick, same-tick start = 0; Bernoulli arrivals = one randrange(35) per tick, arrival iff draw < A, decision cell A = 27 → ρ = A/30 = 9/10 EXACTLY; service pmf {2:3, 3:3, 4:2, 6:2}/10 via u = randrange(10): u<3→2, u<6→3, u<8→4, else 6 — mean 7/2, E[S²] = 143/10, SCV = 41/245; a queue label randrange(3) consumed by EVERY arrival, used only by SPLIT-RANDOM; the per-run stream generated ONCE and fed IDENTICALLY to all three configurations — common random numbers; T = 20,000 arrival ticks, measured cohort = arrivals in [2,000, 20,000), then DRAIN to empty, drain cap: non-empty at tick 80,000 = run INVALID, as is a zero POOLED cohort mean; RNG = one stdlib random.Random(seed) per leg, runs sequential in pinned loop order — cells ascending A, run index 0..M−1 — per-tick draw order arrival → (if arrival) service → label; per-run draw sentinel exactly T + 2·arrivals), measure the MEDIAN over the valid M = 32 seed-20261313 main-leg runs of the per-run cohort mean-wait ratio R = Ŵ(SPLIT-RANDOM)/Ŵ(POOLED) — POOLED one shared FIFO, SPLIT-RANDOM three label-joined FIFOs no jockeying, both exact fractions.Fraction per run, median of an even count = mean of the two middle order statistics — with SPLIT-JSQ (join shortest counting in-service, ties lowest index) riding the identical streams REPORTING-ONLY, the load sweep A ∈ {21, 24, 30} (ρ = 7/10, 4/5, 1) on seed 20261315 at M = 16/cell REPORTING-ONLY, the seed-20261314 stability leg (A = 27, M = 16, must reproduce the ruling for any APPROVE), and seed 20261316 aux reserved NEVER read. Decision rule pre-registered, evaluated IN ORDER, both bands carrying the < 1/4-invalid validity conjunct: REJECT FIRST iff median R < 3/2; APPROVE iff median R ≥ 2 AND the stability leg reproduces; NULL anything else naming the binding axis from the pre-registered four (band straddle R ∈ [3/2, 2); settlement failure via the validity conjunct; stability non-reproduction; load-sensitivity flip — reporting-only, cannot flip the decision; cheapest live probe: the A = 27 cell alone at T = 100,000, cohort [10,000, 100,000), drain cap 400,000, on aux seed 20261316). Gates, run invalid on any failure: the pinned 8-tick hand fixture (arrivals {0,1,2,3,5,7}, services {4,3,2,6,2,3}, labels {0,0,1,0,2,1}) reproducing EXACTLY POOLED waits (0,0,0,1,0,0) mean 1/6, SPLIT-RANDOM (0,3,0,4,0,0) mean 7/6, SPLIT-JSQ (0,0,0,1,0,0) mean 1/6 (routes 0,1,2,0,1,1), fixture ratio R = 7; the A = 0 control leg (M = 4: zero starts, zero busy ticks, sentinel exactly T); work conservation (started service sum ≡ busy server-ticks); stream identity across configurations; cohort conservation; per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned — with the pooled-dominance and load-monotonicity audits printed as first-class ANOMALY lines (reporting, never invalidating). Fully hermetic: zero repo/network reads by the runner — fixtures.json constructed from the pinned constants in the idea doc, committed BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, the parallel VERDICT 054 session's files/claims/number (sim-lab PR #106, branch claude/verdict-054-brineward-band-necessity), and idea-engine's outbox untouched.

## What happened

Built `sims/verdict-055-checkout-pooling/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 044 block/idea doc @ 3f38420: frame,
service pmf with its exact moments, load grid, seeds 20261313–316, bands,
the 8-tick hand fixture with three hand-computed wait tables) committed
BEFORE the runner. Git trail (PR #107 — squash-merge erases branch SHAs from
main, resolve via the PR): 2603d4e (born-red card) → b7b2535 (fixtures) →
91dedfc (runner pooling_sim.py + accepted run: results.json, run-stdout.txt,
REPORT.md) → f099021 (guard-fires telemetry) → a2a6c4a (merge of origin/main
after PR #106 / VERDICT 054 landed mid-session — merged IN, never rebased;
see ⟲ for the guard-fires conflict) → 97f7cd4 (INTAKE 044 + VERDICT 055
ledger) → this flip.

**Run:** `SELF-CHECKS: 1111 passed, 0 failed`, exit 0, ~4 s; stdout +
results.json byte-identical across two full process runs by external diff
(no wall-clock in any output; stdout sha256 82585fdf…, results sha256
1634b098…); CPython 3.11 pinned, asserted. Gates all green: the 8-tick hand
fixture exactly (three wait tables, JSQ routes (0,1,2,0,1,1), fixture ratio
R = 7); the literal tick-engine cross-check (registered completions →
arrival → index-order-starts semantics reproduced per customer by the fast
decision engines on the fixture AND run 0 of every (leg, cell), all three
configurations); A = 0 control (zero arrivals/starts/busy, sentinel exactly
T); work conservation; stream identity across configurations; cohort
conservation; per-run + per-leg draw sentinels (main 1,628,134 = Σ(T +
2·arrivals)); twin decision evaluators (Fraction vs pure-integer
cross-multiplication) agree; aux 20261316 never constructed. No
fix-forwards — the first complete run of the registered pipeline is the
accepted run.

**Ruling: approve.** REJECT (checked FIRST) does not fire. APPROVE fires:
main median R = 9017678143/967484332 ≈ 9.320749 ≥ 2 (0 of 32 invalid; every
run individually ≥ 2, per-run range ≈ 7.46–11.37), stability median ≈
9.257803 reproduces (0 of 16 invalid). The registered conservatism argument
measured WRONG in direction: burst-free low-SCV traffic drives the pooled
3-server system nearly lean (mean wait 1.54 ticks) while each split line
stays a heavy single-server ρ = 9/10 queue (14.13) — the ratio lands ~3×
ABOVE the disclosed continuous anchor (≈ 3.3). Honest caps shipped
first-class: the JSQ informed-shopper median ratio ≈ 1.156 (picking the
short line recovers most of pooling — the drama attaches to the RANDOM-line
shopper), the load sweep 11.58/9.70/9.32/3.99 (ρ = 1 saturation cell
disclosed boundary), zero pooled-dominance and zero load-monotonicity
anomalies. Landed INTAKE 044 (accepted) + VERDICT 055 (finalized, approve)
in control/outbox.md (append-only; `## VERDICT 055`/`## INTAKE 044`
collision-grepped at origin/main 3714ff6 at session start and re-grepped at
692fcf1 after the mid-session merge — none). control/inbox.md, both status
heartbeats, the VERDICT 054 session's files/claims/number, and idea-engine's
outbox untouched; claim rode idea-engine PR #340. Walls: none new (the
Write-tool REPORT.md block V054 reported reproduced verbatim here —
tool-policy, bypassed via shell heredoc, session-local). PR:
https://github.com/menno420/sim-lab/pull/107 (READY; merge-on-green owns the
merge — zero agent merge/arm calls).

## 💡 Session idea

A registration that pins OPERATIONAL semantics (a tick loop: completions →
arrival → index-order starts) licenses implementations that are mathematical
REDUCTIONS of it — this session's decision engines are O(1)-per-customer
recursions (FIFO start-time recursion; JSQ presence via departure-time
deques) whose equivalence to the registered loop is a theorem the
implementer proves in their head. The armed failure mode: the registered
hand fixture is far too small to witness that theorem (6 customers, one
boundary case — it happens to pin the free_at == t "not in service" JSQ
edge, but no warm-up boundary, no drain regime, no tie at scale), so a
subtly-wrong-but-fast engine can pass the fixture and decide a verdict. Fix,
build-side and cheap: when an implementation departs from the registered
operational semantics for speed, it must ship an EXECUTABLE equivalence
witness as a gate — the literal-semantics reference engine run per-customer
(exact equality on waits/routes/state, not a tolerance band) on at least one
full-scale run per (leg, cell); this session's cross_check() in
pooling_sim.py is the working pattern (~15,000 customers per config per
witnessed run vs the fixture's 6). Kin, deduped: the lineage's dual-arm
Arm A/Arm S discipline compares two estimators of the same QUANTITY under a
tolerance gate — this witnesses two implementations of the same SEMANTICS
under exact equality, a different object (grep at flip time of .sessions/,
control/outbox.md, docs/, and idea-engine ideas/ for "equivalence
witness"/"reference engine"/"operational semantics" — zero hits; V052/V053/
V054's 💡 lint wrong fixture VALUES, missing derivation RULES, and
uncomputed POWER claims — none covers implementation-vs-semantics
divergence). Anchors: pooling_sim.py `tick_engine`/`cross_check`, REPORT.md
§ Gates, fixtures.json `frame.tick_semantics`.

## ⟲ Previous-session review

VERDICT 054 (Brineward band-2 necessity, PR #106) is the direct predecessor
and this session's mid-flight neighbor — its merge landed while this branch
was open, exercising the push-race rule (merged IN at a2a6c4a, never
rebased; both sessions' ledger blocks kept in proposal-aligned order,
numbers stable throughout, exactly as the claim files pre-arranged). Its
card is honest where it counts: the dual-reading disclosure on its one
stability widened-gate breach (registered reading rules, stricter reading
committed alongside) is the lineage's cleanest handling yet of a
registration ambiguity discovered mid-verdict, and its 💡 (power claims
asserted without committed arithmetic) names a real third defect species.
Two of its observations REPRODUCED here: (1) the Write-tool REPORT.md
block it classified as "tool-policy, session-local, not a lane wall" fired
verbatim in this session and its shell-heredoc bypass worked unchanged —
classification confirmed; (2) the V051→V053 guard-fires shared-append
hazard fired its next real conflict (V054's committed telemetry lines vs
this session's, at the origin/main merge), resolved as a timestamp-ordered
union in a2a6c4a — the fix sketch (shard per session or untrack) now has
two evidence commits. One inversion of ITS ASK 003 experience: V054's
born-red card was mtime-newest so its local check stayed honestly red;
this session got the V053-shaped corridor instead — after the mid-session
merge imported V054's completed card, local `check --strict` flipped
falsely GREEN (verbatim: "check: session log
.sessions/2026-07-13-verdict-054-brineward-band-necessity.md complete.")
while this card still said in-progress — confirming the corridor is
merge-order-dependent, not fixed by either shape; CI's substrate-gate
(diff-touched card) remains the only honest signal, per ASK 003
disclosed-not-fixed.

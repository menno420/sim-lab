# Session — VERDICT 052 — Spool-scale go/no-go margin error budget: how many grams of pocket does the five-second "enough filament?" check need, and does the weigh-it-empty habit measurably pay? (idea-engine PROPOSAL 041, fleet-backlogs rotation round 7)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-052 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 041 (## PROPOSAL 041 · 2026-07-13T18:01:18Z · status: sim-ready, landed via idea-engine PR #331 → main 65dcf3a; claim landed FIRST via idea-engine PR #332 → main 498a88e, `control/claims/claude-verdict-052-spool-scale-margin.md`, reserving INTAKE 041 + VERDICT 052 and branch claude/verdict-052-spool-scale-margin — the claim-first ritual; offset map PROPOSAL 041 → VERDICT 052, +11 per the docs/current-state.md rule) — "spool-scale go/no-go margin error budget": price the two never-quantified lines of the curious-research spool-weight-scale build (`projects/spool-weight-scale/README.md` § Honest expectations + Stage 2, both @ a9fd5faa6a10b4d1364d205dbeac7a8678e1bd73) under the pinned scenario model quoted verbatim from the proposal. Pinned frame (every constant from the PROPOSAL 041 block, the source of truth): integer grams throughout; F ~ uniform {0..1000} (1 kg spool); W = F + E + ε_s, ε_s ~ uniform {−5..+5} (the cited ±5 g practical resolution); F̂ = W − Ê (no clamping); three tare regimes — R-OWN (E ~ U{80..306}, Ê = E + ε_t, ε_t ~ U{−2..+2}), R-TABLE (brand ~ U{201, 256, 225, 224}, Ê = seed, E = seed + δ, δ ~ U{−15..+15}), R-GUESS control (Ê = 193, E ~ U{80..306}); job Ĵ from the pinned mix (1/2 U{5..50}, 3/10 U{51..200}, 1/5 U{201..800}); U = Ĵ + ⌈Ĵ·u/100⌉, u ~ U{0..5}, ⌈a/b⌉ = −(−a//b); decision rule τ_M: START iff F̂ ≥ Ĵ + M, margin grid M ∈ {0, 5, 10, 15, 25, 40, 60, 100} g; outcome conventions pinned: RUN-OUT iff started AND U > F (U = F is NOT a run-out), FEASIBLE iff F ≥ U, FORGONE iff declined AND feasible. Metrics: RUNOUT(R, M) = P(run-out | started), FORGONE(R, M) = P(declined | feasible), exact Fractions in Arm A; Feas(R) = {M : RUNOUT ≤ 1/100 AND FORGONE ≤ 1/5}, M*(R) = min Feas(R). Arms: Arm A = seedless exact-Fraction enumeration over the integer error lattices (the DECISION arm; net-error convolution collapse permitted iff it reproduces the direct product enumeration EXACTLY on the pinned spot-check sub-grid Ĵ ∈ {20, 100, 400, 800} × u ∈ {0, 5} × all regimes × M ∈ {0, 25}); Arm S = seeded MC confirmation, 200,000 scenarios/regime, random.Random(20261301), pinned draw order (R-OWN → R-TABLE → R-GUESS; per scenario F → tare term(s) → ε_s → job class → Ĵ → u), common random numbers across the margin grid; agreement gate |ArmS − ArmA| ≤ 3/1000 on every RUNOUT cell, ≤ 1/100 on every FORGONE cell, any breach invalidating the run. Seeds registered: 20261301 main / 20261302 stability (20,000/regime, must reproduce the ruling) / 20261303 reporting (drift + sensitivity confirmations, 20,000 each) / 20261304 aux (reserved, NEVER read) — strictly above the P040/V051 high-water 20261300. Decision rule pre-registered, evaluated IN ORDER: REJECT FIRST (Feas(R-OWN) = ∅) → APPROVE (M*(R-OWN) ≤ 25 AND (Feas(R-TABLE) = ∅ OR M*(R-TABLE) ≥ M*(R-OWN) + 15) + seed-20261302 stability reproduction) → NULL (anything else, four pre-registered axes: big-pocket M*(R-OWN) ∈ (25, 100]; table-parity M*(R-TABLE) < M*(R-OWN) + 15; arm disagreement; sensitivity straddle — reporting legs name the axis, never flip the decision). Gates, run invalid on any failure: six-scenario hand fixture; zero-error identity leg (RUNOUT ≡ 0, FORGONE(0) = 0 exact); exact monotonicity in M in both arms; convolution spot-check at exact equality; arm agreement gate; per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned. Reporting-only (cannot flip): drift leg W' = W + d, d ~ U{0..+8}; sensitivity pairs ε_t {0}/{−5..+5}, δ {−8..+8}/{−30..+30}, u {0..2}/{0..10}, job mix {1/4, 1/4, 1/2}; per-job-class RUNOUT splits; R-GUESS expected-direction check (surprise printed as a first-class anomaly). Fully hermetic: zero repo/network reads by the runner — fixtures.json constructed from the pinned constants and committed BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched.

## What happened

Built `sims/verdict-052-spool-scale-margin/` — `fixtures.json` (every
registered constant verbatim from the PROPOSAL 041 block: all error lattices
with their sensitivity pairs, the four brand seeds, the job mix, the M grid,
bands 1/100 · 1/5 · 25 g · 15 g, the six-scenario hand fixture, per-leg
scenario counts 200k/20k/20k, seeds 20261301–304, the two harvested doc
lines verbatim @ curious-research a9fd5fa) committed BEFORE the runner. Git
trail (PR #104 commits — squash-merge erases branch SHAs from main, resolve
via the PR): 1eab24b (born-red card) → efc3849 (fixtures) → c4f5cc1 (runner
+ accepted run) → 965b39a (README + REPORT) → bdb9756 (ledger) → this flip.

**Run:** `SELF-CHECKS: 15 passed, 0 failed`, exit 0, ~14 s; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 3d735a6e… / 3b38dabc…); CPython 3.11 pinned, asserted. Gates all
green: six-scenario hand fixture; zero-error identity (exact zeros);
convolution spot-check EXACT on all 48 pinned cells (collapsed ≡ direct
product — the collapse is permitted, the ruling rides it); monotonicity in M
on all 25 (table, arm) combinations; arm agreement (max |ΔRUNOUT| 0.000951 ≤
3/1000, max |ΔFORGONE| 0.001283 ≤ 1/100); draw sentinels exact (main
4,000,000 / stability 400,000 / reporting 2,220,000, aux 20261304 ZERO
draws — new registry high-water 20261304); twin evaluators agree on main AND
stability inputs. No fix-forwards — the first complete run of the registered
pipeline is the accepted run.

**Ruling: null — TABLE-PARITY (pre-registered axis ii).** REJECT (checked
FIRST) does not fire: Feas(R-OWN) = the whole grid, M*(R-OWN) = 0
(RUNOUT(R-OWN, 0) = 18563243/3223848750 ≈ 0.005758 ≤ 1/100). APPROVE does
not fire: pocket conjunct holds (0 ≤ 25) but the habit conjunct fails —
M*(R-TABLE) = 0 < 15 (RUNOUT(R-TABLE, 0) ≈ 0.008084 ≤ 1/100); stability leg
reproduces the class. The habit's measured payoff is vs GUESSING
(M*(R-GUESS) = 60, the control row, expected direction) and vs a skipped
fresh tare (drift moves R-TABLE 0 → 5, R-OWN holds 0), not vs the seeded
table. No sensitivity straddle anywhere. Registered-fixture integrity note:
the idea doc's hand-fixture scenario 2 carried a trailing 'feasible' tag
contradicting the outbox block's own pinned convention (F = 100 < U = 103 →
infeasible); the registered convention won, pinned in fixtures.json +
REPORT.md, never absorbed. Landed INTAKE 041 (accepted) + VERDICT 052
(finalized, null) in `control/outbox.md` (append-only; `## VERDICT 052` /
`## INTAKE 041` collision-grepped at origin/main 022c109 at session start
and re-grepped immediately before the append — none; origin/main never
moved, no mid-session merge). `control/inbox.md`, both status heartbeats,
and idea-engine's outbox untouched; claim rode idea-engine PR #332 (merged →
main 498a88e). No walls hit; sim-lab branch push via the local git proxy
worked first try. @codex suspended per dedc12e — `codex: none this cycle`.
PR: https://github.com/menno420/sim-lab/pull/104 (READY; merge-on-green owns
the merge — zero agent merge calls).

## 💡 Session idea

A REGISTERED gate fixture with a wrong expected value survived the
drafter's entire probe battery and reached sim-ready: PROPOSAL 041's
six-scenario hand fixture tags scenario 2 (F = 100, U = 103) "feasible",
contradicting the same block's own pinned convention FEASIBLE iff F ≥ U —
a started run-out is definitionally infeasible, so the tag is impossible
under the registration it ships with. The verdict session had to adjudicate
doc-vs-convention at implementation time; the failure mode it arms is
nasty — a wrong hand tag either falsely invalidates a correct runner (the
gate is run-invalid-on-failure) or trains implementers to "fix" fixtures at
run time, exactly the fix-forward the discipline bans. Fix, cheap and
proposal-side: hand fixtures in proposals ship as a parseable block (JSON
in the idea doc, not prose arrows), and the DRAFTING session runs a
~20-line validator that recomputes every derived column from the block's
own pinned conventions before flipping the proposal to sim-ready — "hand-
computed at drafting" becomes "hand-computed AND machine-recomputed at
drafting", zero new tooling at verdict time. Anchors: idea-engine
`ideas/fleet/spool-scale-go-no-go-margin-2026-07-13.md` § Gates scenario 2;
the `outcome conventions pinned` clause in the PROPOSAL 041 outbox block;
this repo `sims/verdict-052-spool-scale-margin/fixtures.json`
(`discrepancy_note`) + REPORT.md § Hand-fixture disclosure. Dedup: grep of
.sessions/, control/outbox.md, and docs/ for hand-fixture/fixture-validator
ideas at flip time — none; the V048–V051 💡 lineage targets session-log
resolution, seed registries, the mtime corridor, and the guard-fires log,
never proposal-side fixture validation.

## ⟲ Previous-session review

VERDICT 051 (Schelling tipping, PR #102) is the direct predecessor. Its
disciplines transferred whole: fixtures-before-runner with PR-resolvable
citations, the collision-grep-at-append ritual, twin evaluators, and the
no-fix-forwards accepted-run rule. Its 💡 (the tracked shared-append
`.substrate/guard-fires.jsonl` as a merge-conflict machine, ~98% conflict
under concurrent sessions per the claims-layout sim) is CONFIRMED ARMED
here: this session's strict-gate runs appended session-log lines to the
tracked file mid-flight, unprompted (`git status` showed
`M .substrate/guard-fires.jsonl` before this flip; the flip commit carries
the appended lines as evidence, exactly as V051's did). No conflict
materialized only because no parallel verdict slice was in flight this
session (ledger tail V051 at branch cut AND at append) — the fix V051
sketched (shard per session card, or untrack + gitignore) is now two cards
deep and still unimplemented. V051's other live corridor (the mtime
false-green it reproduced, now ASK 003 in idea-engine's outbox) was NOT
exercised this session: origin/main never moved, so no mid-session merge
imported a fresher completed card and the local strict HOLD validated this
session's own card throughout — corridor dormant, still unguarded; the CI
substrate-gate remains the card-truth backstop.

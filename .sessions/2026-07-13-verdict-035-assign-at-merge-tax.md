# Session — VERDICT 035 — Assign-at-merge, priced: does the routed Option-3 build survive its own merge-queue re-validation tax? (idea-engine PROPOSAL 033)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-035 slice-worker session
> Objective: settle idea-engine PROPOSAL 033 (control/outbox.md · 2026-07-13T08:43:05Z · status: sim-ready; idea `ideas/superbot/assign-at-merge-queue-tax-2026-07-13.md` @ idea-engine main 11c5a1f, landed via idea-engine PR #303 — the standing ORDER 003 FLEET-BACKLOGS rotation slot, round 5, following round 2's own verdict-opened thread: VERDICT 023 REJECTED the shipped Option-1 checker as sufficient and routed the Option-3 assign-at-merge build while stating verbatim "nothing here prices Option 3's build cost"). Build the fully hermetic pre-registered pricing of the OTHER side of V023's fork: under the pinned migration-race frame inherited from P021/V023 verbatim (Poisson migration-bearing PRs λ ∈ {1, 4, 12}/day; develop W = 8 h; validate V ∈ {0.25, 2, 24} h; H = 2,000 h, warm-up 200 h, M = 40), the per-cell re-validation budget V_q*(cell) — the largest V_q ∈ {0.1, 0.5, 2} h at which the REAL Option-3 mechanism P3Q (FIFO merge queue over the shared migration sequence; service = one deterministic re-validation V_q at the head; number assigned at merge, zero renumbers by construction, MEASURED) beats the parent's committed P1 mean open→merge latency (WIN := Arm-A-exact W + V + λV_q²/(2(1−ρ)) + V_q ≤ committed P1 mean AND ρ = λ·V_q < 0.9 — the stability exclusion's only decision-grid member is lam12 × V_q = 2, ρ = 1.0 exactly) across the FIVE treadmill cells V023's REJECT bound (lam01·V24, lam04·V2, lam04·V24, lam12·V2, lam12·V24 — committed T 0.741/0.133/0.846/0.870/0.846). Anchors quoted verbatim from `sims/verdict-023-renumber-treadmill/results.json` @ c7340ae (verified byte-identical at HEAD before build; the parent's committed runner additionally re-run once out-of-sim requiring byte-identical results.json — the V031 precedent). Dual arms: Arm A exact seedless M/D/1 Pollaczek–Khinchine closed forms (the decision arm, zero sampling error vs committed anchors); Arm S seeded event-driven MC of the whole queue (seeds 20260768 main / 20260769 stability half-M = 20 must reproduce the ruling / 20260770 reporting / 20260771 aux — allocated strictly above the P031 registry high-water 20260767, P032 drew zero), familywise-calibrated gates ≈ 3.5σ per point per the V027/V031 two-datapoint lesson, breach protocol pinned before any draw. Gates (run invalid on any failure): the V_q = 0 control leg reproduces V023's committed P3 means {8.25, 10.0, 32.0} EXACTLY; zero renumbers under P3Q measured on every leg; Arm-S ≡ Arm-A familywise; Little's law + busy-fraction ≡ ρ identities on every stable point; the M/M/1 closed form reproduced on the jitter leg; per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned. Decision (registered order, REJECT first): REJECT iff V_q* exists in ≤ 2 of the 5 treadmill cells; APPROVE iff V_q* ≥ 2 h in ≥ 4 of 5, stability-reproduced; NULL otherwise (the per-cell V_q* frontier table IS the citable pin, flip axes named via per-axis WIN shares). Reporting-only (cannot flip): the four calm cells at every V_q; the V_q = 8 h stress column (ρ ∈ {1/3, 4/3, 4}, the last two unstable by arithmetic, printed as such); the exponential-service jitter leg (M/M/1 bracket); the P3Q p95 table vs P1's committed p95 column (decision on means, stated); queue-length/busy-fraction traces; the churn column P3Q R = T = 0 vs the parents' committed T.

## What happened

Built `sims/verdict-035-assign-at-merge-tax/` — a stdlib-only NUMERIC
SIMULATION (rung 1, exact closed-form decision arm + seeded event-driven MC
validation arm), fully hermetic: fixtures.json (the pre-registration — every
constant verbatim from the idea file and the parent's committed results.json,
twelve disclosed intake-time decisions, the familywise SE arithmetic with
pre-run worked examples and the breach protocol pinned before any draw)
landed BEFORE the runner. Anchor gates passed before any anchor was used:
verdict-023 results.json at HEAD byte-identical to the c7340ae pin (sha256
`53c633b1…`) AND the parent's committed runner re-run once out-of-sim in a
scratchpad copy — exit 0, 16,857 self-checks, results.json byte-identical
(the V031 precedent).

**Run output:** `SELF-CHECKS: 16090 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `5bf9fb19…`, results `7bf93492…`), cpython-3.11 pinned and
asserted, ~2.5 s. All pre-registered gates passed: the V_q = 0 control leg
reproduced V023's committed P3 means {8.25, 10.0, 32.0} EXACTLY; zero
renumbers/collisions MEASURED on every replication of every leg; 77
familywise Arm-S gates, 0 breaches, max |z| = 2.065 (protocol never
engaged); Little's law + busy-fraction ≡ ρ on all 64 stable points; the
M/M/1 jitter identity; draw-count sentinels; twin queue engines (heap
event-driven ≡ Lindley exactly); twin decision evaluators (exact-Fraction ≡
float); the stability leg (seed 20260769, M = 20) reproduced the ruling.
**Ruling: NULL — the conditional frontier is the finding.** REJECT checked
FIRST per the registered order and missed by 3 cells (a winning V_q exists
in ALL 5/5 treadmill cells, band ≤ 2); APPROVE missed by 2 (V_q* ≥ 2 h in
2/5, band ≥ 4). Frontier: V_q* = 2 h in the two V = 24 lam01/lam04 cells,
0.5 h in the other three; lam12 × 2 h excluded by arithmetic (ρ = 1.0
exactly). Binding axes = the registration's own expected candidates, now
with exact shares: λ = 12/day (WIN share 2/3, the ρ ceiling) and the V = 2
column (2/3 — 1.417 h headroom, overspent by an exact 1.083 h at V_q = 2).
Side pins: the frontier is service-jitter-robust (the M/M/1 WIN map is
identical at every decision point); the calm cells SPLIT against the
registration's expectation (two of four admit thin 0.1 h wins — 0.159 h and
~32 s — reported honestly, build-irrelevant); P3Q p95 sits far below P1's
committed p95 everywhere stable; churn column ships (P3Q R = T = 0 measured
vs committed T up to 0.870, the free un-scored win).

Landed: INTAKE 033 (2026-07-13T09:18:53Z) + VERDICT 035
(2026-07-13T09:18:54Z) appended to `control/outbox.md` (append-only, 0
deletions; VERDICT 034 re-verified at the ledger tail at origin/main HEAD
8a4e63c immediately before the append — the only interim commit was the
manager's inbox ORDER 004 append, merged INTO this branch, never rebased;
numbers preserved by the proposal-aligned +2 offset, no sibling verdict-035
work in flight at dispatch by ls-remote + zero open PRs). Verdict PR from
`claude/verdict-035-assign-at-merge-tax`. Worker session — no heartbeat
writes; this card flip is the last commit. Note for the coordinator: sim-lab
inbox ORDER 004 (night report, 09:11Z) landed mid-slice and is addressed to
the Ideas Lab coordinator seat — untouched here.

## 💡 Session idea

When a pre-registered WIN predicate conjoins a measured comparison with an
arithmetic exclusion (here: mean ≤ anchor AND ρ < 0.9), pre-compute at
registration time how many decision points the exclusion alone already
settles, and say so next to the bands — this head did it (lam12 × 2 h,
ρ = 1.0, named in the proposal), and the payoff showed at verdict time: the
APPROVE band (≥ 4 of 5 at V_q* ≥ 2 h) was arithmetically capped at 3 of 5
before any code ran, because two of the five cells sit at λ = 12/day where
2 h is excluded. The registered bands were still all reachable (REJECT and
NULL live, APPROVE dead-on-arrival), which is fine for an honest-null
pipeline — but a proposal that WANTS its APPROVE branch reachable must
check band-vs-exclusion interaction at drafting, or it registers a decision
grid where one ruling is impossible by construction and only discovers it
after the build. The portable rule: for every band, verify at registration
that some point of the decision grid can still satisfy it AFTER the
pre-computable exclusions are applied.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-034-penney-decay.md`: complete and honest;
exports adopted. (1) Its race protocol (re-verify the ledger tail at
origin/main HEAD immediately before the append, merge never rebase) held
for a fourth consecutive slice — this session's interim main movement was a
manager inbox append rather than a sibling verdict, and the same discipline
absorbed it with zero friction. (2) Its 💡 (when a band quantifies over a
curve, make the protective band quantify over every point too) is the same
family as this card's 💡 — both are register-time reachability audits of
the band arithmetic; together they generalize to: before committing bands,
enumerate what the band can SEE (endpoints vs interior; post-exclusion
grid) and confirm every ruling is reachable. (3) Where V034 was the
rotation lane's exact-census form (zero seeds), this head needed the full
seeded apparatus back (familywise gates, stability seed, sentinels) — the
V027/V031 SE-calibration lesson transferred unchanged and produced 0
breaches at 77 gates, confirming the 3.5σ familywise design is now settled
art for seeded heads.

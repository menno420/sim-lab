# Session — VERDICT 023 — migration renumber-treadmill residual (idea-engine PROPOSAL 021)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-023 slice-worker session
> Objective: settle idea-engine PROPOSAL 021 (control/outbox.md · 2026-07-13T02:36:37Z · status: sim-ready; idea `ideas/superbot/migration-renumber-treadmill-residual-2026-07-13.md`, landed via idea-engine PR #287, main `8022a9d`) — the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, round 2, harvested from the superbot section's 237-doc backlog (canonical doc `migration-number-collision-guard-2026-06-22.md` @ fd638e3, byte-same at live 4522522; the recorded incident is #1279's four-renumber afternoon). Build the fully hermetic pre-registered continuous-time event sim of migration-number races: PRs arrive Poisson λ ∈ {1, 4, 12}/day, develop W = 8 h, validate V ∈ {0.25, 2, 24} h; collision at merge-attempt iff the held number was merged by another PR since pick → renumber (fix latency d = 0.5 h) → re-validate; policies by pick time — P0 at open + each fix start (windows W+V then d+V), P1 re-pick at every push (every window = V, the shipped Option-1 checker's semantics), P3 assign-at-merge (exposure 0, MUST measure exactly zero collisions — built-in control); H = 2,000 h, first 200 h warm-up discarded, M = 40 reps per (cell, policy), `random.Random(20260723)`, pinned loop order; metrics on the post-warm-up merged population R = renumbers per merged PR and T = share with ≥ 2 renumbers, plus reporting-only latency inflation vs P3, max simultaneous holders, and the endogenous/exogenous amplification ratio vs the exact Arm-A closed forms P(N≥1) = p(w₁), P(N≥2) = p(w₁)·p(w₂), E[N] = p(w₁)·e^(λw₂), p(w) = 1 − e^(−λw). Validation gate: Arm S in exogenous mode (external Poisson appends, one focal PR, M = 20,000, seed 20260726) within 1.0 pp absolute of Arm A on P(N≥1) and P(N≥2) in every covered cell AND endogenous P3 exactly zero collisions, else the run is INVALID. Reporting-only legs: sensitivity d ∈ {0.25, 2}, W ∈ {1, 24}; jitter seed 20260725; stability M = 8 seed 20260724 (must reproduce the ruling); the #1279 anchor (λ=12/day, V=2, d=0.5, P0 — E[N] and P(N≥3), plausibility vs an n=1 anecdote, never a fit). Then issue exactly ONE of APPROVE (R ≤ 0.10 AND T ≤ 0.01 in ≥ 8 of 9 endogenous P1 cells, gate passed; checked FIRST) / REJECT (T > 0.05 in ≥ 5 of 9 cells → the per-cell residual-tax table rides to the Option-3 plan) / NULL (flip axis named via per-axis APPROVE-pass shares and median T; the conditional per-PR-class rule is the citable finding) per the decision rule registered in the idea file BEFORE any code existed, with the Poisson-arrivals and uniform-compliance boundaries stated (P1's residual is a FLOOR — APPROVE is the fragile direction).

## What happened

Built `sims/verdict-023-renumber-treadmill/` — a stdlib-only NUMERIC
SIMULATION (rung 1, dual-arm), fully hermetic: the sim reads exactly one file
(its own committed `fixtures.json` pre-registration, cross-checked at start)
and touches no repo state, network, or wall clock. The pre-registration (all
constants verbatim from the idea file, the pinned event/draw/loop order, the
decision rule with evaluation order, two fully hand-derived pin scenarios
with derivations, and the disclosed intake-time decisions — sensitivity and
jitter legs at M=8, the jitter redraw granularity, the warm-up/p95
conventions, and the exogenous two-round truncation) was committed BEFORE
the runner was written.

**Run output summary:** `SELF-CHECKS: 16857 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
`diff` + `cmp`), cpython-3.11 pinned and asserted, ~58 s. **Ruling: REJECT —
the shared append point must go; the Option-3 assign-at-merge build gets its
evidence row.** APPROVE checked first and FAILS (2/9 cells pass both bands
vs ≥ 8 — only the two V=0.25 fast-lane cells at λ ≤ 4/day). REJECT binds:
T > 0.05 in exactly 5/9 cells (bar ≥ 5), every member 2.7×–17× over the
band (T 0.133–0.870), nearest non-member at 42% of the band, and the
IDENTICAL five-cell set reproduced by the stability leg, the jitter leg, and
all four sensitivity legs. Validation gate PASS: exogenous Arm S max |dev| =
0.684 pp vs the 1.0 pp gate over all 36 comparisons; endogenous P3 measured
exactly zero collisions on every leg. Headline deliverable: the
endogenous/exogenous amplification ratio runs 0.96–25.8× — the (λ=12/day,
V=2) cell measures R = 44.4 against the closed form's E[N] = 1.72 (renumber
storms breed renumber storms), while the saturated V=24 high-λ cells
COLLAPSE the ratio (0.35, 1.2e-4) because the treadmill throttles its own
driver (merge throughput falls below λ). Latency tax up to 15.4× mean / 44×
p95 vs P3; max simultaneous holders of one number 967. #1279 anchor: Arm A
E[N] = 3.47, P(N≥3) = 0.506, P(N≥4) = 0.361 — the four-renumber afternoon
sits comfortably inside the model's mass (endogenously that cell runs
R = 88.5 under P0). Two amendments disclosed first-class, decision machinery
untouched: HAND-1's expected duration sum was a hand-arithmetic slip
(10 + 12.5 committed as 23.5; corrected to 22.5 after the engine AND the
independent replay both computed 22.5), and the first run exposed a
replay-twin bug (censored holders missing from its interval sweep — the
twin was wrong, the engine right; fixed twin-side, full re-run).

Slice boundary this cycle (the V015–V022 precedent): this session carries
the INTAKE 021 and VERDICT 023 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). Concurrency handled: VERDICT 022 (PROPOSAL 020) had
ALREADY landed at the ledger tail @ cf953a5 before this session's appends —
no reservation needed, numbers unconditional, noted in INTAKE 021's source
line. No @codex step — suspended per the outbox codex-line escalation @
dedc12e. Born-red card and complete flip land in one push (the V018–V022
choreography: `bootstrap.py check --strict` fails on an in-progress newest
card, and the strict-gate-before-every-push rule binds harder).

## Run command

```
python3 sims/verdict-023-renumber-treadmill/renumber_treadmill_sim.py
```

## 💡 Session idea

When a sim's validation arm is a closed form that EXPLODES in part of the
grid (here E[N] = p(w₁)e^(λw₂) ≈ 2.1×10⁵ renumbers per PR at λ=12/day,
V=24), that explosion is information, not just an implementation nuisance:
it marks exactly where the exogenous approximation stops describing any
system that has to conserve throughput, so pre-register the gate on
BOUNDED tail probabilities (P(N≥1), P(N≥2) — always in [0,1], always
checkable at fixed M) and let the unbounded moment be the analytic
DELIVERABLE the endogenous measurement is compared against. The
amplification ratio then tells a two-sided story a single-sided intuition
misses: the coupled system runs 26× HOTTER than the formula mid-grid
(feedback) and 10,000× COOLER at saturation (self-throttling) — both
directions measured against the same exact arm, and neither reachable by
the formula alone. Rule of thumb: gate on tails, deliver on moments.
Also exportable: model external world-events as degenerate agents through
the SAME engine (appends here = instant-merge W=V=0 PRs) — the validation
leg then exercises the very collision code path the decision leg uses,
instead of a parallel implementation that could diverge from it.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-021-backlog-low-water.md`: complete, honest,
and its exports are adopted here directly. (1) Its one-push born-red
choreography is followed verbatim. (2) Its fixtures-before-runner
discipline, including hand-derived pins WITH derivations committed before
code, is reused — and this session adds the honest coda that discipline
makes possible: one pin expectation carried a hand-arithmetic slip, and
because the derivation text was committed alongside the number, the slip
was auditable as a transcription error (the derivation's own components,
10 and 12.5, contradict its stated sum) rather than a silent re-fit; the
amendment is disclosed in-place in fixtures.json. (3) Its
draw-count-accounting export is generalized here to three draw families
(arrival gaps = arrivals + reps; jitter draws = 2·arrivals + 2·collisions;
exogenous gaps = appends + focals), each closing exactly. (4) Its twin
decision evaluators and trace-replay twin are reused, with the replay twin
deliberately restructured (no heap, set-membership collision test,
interval-sweep holder recount) — which paid for itself: the twin's
interval sweep initially missed censored holders and the exact-equality
check caught the 1-count discrepancy on a 225-holder pile-up. One
improvement carried forward rather than copied: V021's per-leg
fresh-Random first-draw check is subsumed here by the per-leg draw-count
identities, which police the whole stream rather than its head.

# Session — VERDICT 021 — backlog low-water signal threshold (idea-engine PROPOSAL 019)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-021 slice-worker session
> Objective: settle idea-engine PROPOSAL 019 (control/outbox.md · 2026-07-13T01:34:28Z · status: sim-ready; idea `ideas/fleet/backlog-low-water-signal-tuning-2026-07-13.md`, landed via idea-engine PR #284, main `f7906e5`) — the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, restarting the cycle after 017 unrelated / 018 venture. Build the fully hermetic pre-registered reorder-point sim for never-idle lane backlogs: discrete wakes H=2,000, b₀=6, R=4; per wake in pinned order (replenishment lands → consumption p_c ∈ {0.6, 1.0}, dry wake iff demand meets b=0 → organic arrival A1/A2/A3, A2 anchored to the websites backlog's observed multiset {2,4,5,11} → signal policy N ∈ {0(off),1,2,3,4,6}, one outstanding, +R at t+L, L ∈ {1,2,4}); 18 cells = 3 regimes × 2 p_c × 3 L, M=300 seeded reps per (cell,N), `random.Random(20260719)`, pinned loop order; metrics D = dry wakes / demand wakes, S = signals per 100 wakes, mean backlog (reporting); sensitivity legs R ∈ {2,8}, b₀ ∈ {3,12}, H=500 and a decision-stability leg M=50 seed 20260720, all reporting-only. Then issue exactly ONE of REJECT-a (D(0) ≤ 0.05 in ≥ 80% of cells, checked FIRST) / APPROVE (N* = smallest N with D ≤ 0.05 AND S ≤ 25 exists in ≥ 80% of cells AND median ΔD = D(0) − D(N*) ≥ 0.10 → threshold = grid-median N*, stating whether the bullet's "~3" lies within ±1) / REJECT-b (N* exists in < 50% of cells) / NULL (flip axis named via per-axis N*-exists shares and median ΔD) per the decision rule registered in the idea file BEFORE any code existed, with the n=4 anchor caveat and the latency-in-wakes mapping stated.

## What happened

Built `sims/verdict-021-backlog-low-water/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: the sim reads exactly one file (its own
committed `fixtures.json` pre-registration, cross-checked at start) and
touches no repo state, network, or wall clock. The pre-registration (all
constants verbatim from the idea file, the pinned wake/draw/loop order, the
decision rule with evaluation order, two fully hand-derived pin scenarios
with derivations, and ONE disclosed intake-time decision — sensitivity legs
at M=50, the idea file leaves their M unpinned) was committed BEFORE the
runner was written.

**Run output summary:** `SELF-CHECKS: 411339 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
diff), cpython-3.11 pinned, ~31 s. **Ruling: APPROVE — ship the signal; pin
the threshold.** REJECT-a checked first and FAILS (baseline D(0) ≤ 0.05 in
only 3/18 cells — organic refill does not suffice; A3 baselines run
0.75–0.85 dry). N* exists in 18/18 cells; median ΔD = 508,621/1,200,000 ≈
0.424 ≥ 0.10. **Grid-median N* = 1** — and the bullet's "~3" is NOT within
±1 of it: as a fleet default "~3" over-signals; it is exactly right only in
the two hardest cells (p_c=1.0, L=4, thin/bursty arrivals), where N=3 is the
structural-zero threshold (D(N*)=0 exactly on 600k wakes each). Alarm band
never binds at N* (max S 21.28 vs 25) and reproduces the analytic
steady-state law S ≈ 25·deficit/R. Stability leg (M=50, seed 20260720)
reproduces APPROVE with the identical N* map. The one disclosed fragility:
the R=2 sensitivity leg lands NULL under the rule (alarm budget d/R > 0.25
unsatisfiable in 4 cells) — carried as the approval's rider (the row assumes
the manager routes R ≈ 4 items per signal).

Slice boundary this cycle (the V015–V019 precedent): this session carries
the INTAKE 019 and VERDICT 021 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). Concurrency handled: a sibling session is landing
INTAKE 018 / VERDICT 020 (PROPOSAL 018) — not at HEAD e5e1bee at this
session's appends; 018/020 reserved for it, this session's numbers
unconditional, noted in INTAKE 019's source line. No @codex step — suspended
per the outbox codex-line escalation @ dedc12e. Born-red card and complete
flip land in one push (the V018/V019 choreography: `bootstrap.py check
--strict` fails on an in-progress newest card, and the
strict-gate-before-every-push rule binds harder).

## Run command

```
python3 sims/verdict-021-backlog-low-water/backlog_low_water_sim.py
```

## 💡 Session idea

A pre-registered "state whether the folklore constant survives" clause is a
cheap honesty ratchet other intakes should copy: this sim could have shipped
"APPROVE, threshold 1" and quietly buried the bullet's "~3" — but the idea
file forced the |3 − grid-median| ≤ 1 statement, and answering it surfaced
the real deliverable: a folklore constant that is WRONG as a default and
RIGHT as the hard-cell conditional (N=3 is structurally dry-proof exactly
where consumption is every-wake and routing is overnight). Rule of thumb:
when a harvested bullet carries an invented constant, pre-register a
distance test against the measured optimum — the pass/fail is less
interesting than WHERE the constant turns out to be right, which is what the
consumer (here the kit's per-lane override) actually needs. Also exportable:
when a policy's RNG draws are policy-independent by construction (draw
order: consumption, arrival-fire, batch-size — none reads N or L), the
draw-count accounting identity (2·H·reps + fires) is a one-line total-stream
integrity check that catches loop-order drift anywhere in a 65k-replication
run.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-019-irv-monotonicity.md`: complete, honest,
and its exports are adopted here directly. (1) Its one-push born-red
choreography is followed verbatim. (2) Its fixtures-before-runner
discipline, including hand-derived pins WITH derivations committed before
code, is reused as-is (two pins here, one exercising the tight gap = L
spacing bound). (3) Its independent re-implementation fidelity floor
translates here as the trace-replay twin simulator (different state layout,
no early exits) plus twin decision evaluators — the right shape when the
process is stochastic rather than enumerable. (4) Its
check-a-degenerate-leg-analytically export was applied prospectively: the
analytic steady-state alarm law (S ≈ 25·d/R) was derived while reading the
results and matched to 0.2% in the tightest cell, turning a would-be
coincidence into corroboration; the R=2 NULL was likewise explained
analytically (d/R > 0.25 ⇒ S-band unsatisfiable) rather than left as a
mystery row. One improvement carried forward rather than copied: V019's
first-draw seeding check is strengthened here into the full draw-count
accounting identity across all seven legs.

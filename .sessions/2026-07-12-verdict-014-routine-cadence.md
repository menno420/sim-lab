# Session — VERDICT 014 — routine-cadence economics (idea-engine PROPOSAL 012)

> **Status:** `complete`
> 📊 Model: fable-5 · 2026-07-12 · verdict-014 slice-worker session
> Objective: settle idea-engine PROPOSAL 012 (control/outbox.md @ ff48c2fad809ce7704bb66aafee42335efd5c3fd) — seeded discrete-event replay of trigger-arrival trace T (real ~12.2h corpus reconstructed from idea-engine control/status.md history fc0bab6..531b109, plus seeded Poisson/burst/empty-night variants) against policy grid G = {failsafe-2h, failsafe-1h, failsafe-30m, failsafe-2h + chain-15m-while-work-open, event-driven-only, hybrid(event-driven + failsafe-2h)} under cost model C (worker-turns), answering: which policy minimizes worker-turns per caught trigger subject to p95 catch-latency ≤ 2h, and is any policy strictly dominated across all trace variants.

## What happened

Built `sims/verdict-014-routine-cadence-economics/` — a stdlib-only seeded
discrete-event simulator (rung 1, NUMERIC SIMULATION) with trace T embedded
(4 replayable arrivals E1–E4 with per-event idea-engine evidence SHAs; E5
honestly timeless, rate-counted only; 3 null sweeps; all 12 reconstruction
gaps carried in `labels.json`). Grid: 6 policies × {real, 40-seed Poisson
λ=5/732, 40-seed burst, empty-night} × webhook-visible fraction
w ∈ {0,.25,.5,.75,1} × 2 catch definitions (def-A = to catching wake, def-B =
+31.4 min measured E4 done-when lag) = 144 cells, plus sensitivities S1–S8
(catch-def flips, chain-sweeps counterfactual, webhook-wake semantics,
work-window length, E2 arrival bound, E1+E2 fold, cron phase, alt-λ).

**Run output summary (final head):** `SELF-CHECKS: 272 passed, 0 failed`,
exit 0. Determinism PROVEN: two full process runs diffed byte-identical on
both stdout and results.json (external `diff`), plus an in-process
double-computation self-check. Headline: winner s.t. p95≤2h under def-A is
**hybrid(event-driven + failsafe-2h)** — the incumbent posture — at 1.75
turns/catch real (1.39–1.47 synthetic; margin +1.19–1.50 to failsafe-1h),
tied with plain failsafe-2h wherever the webhook class is empty (it is EMPTY
on the entire real trace; event-driven-only catches 0/4 there). Dominance:
failsafe-2h+chain-15m strictly dominated across ALL variants (chain re-arms
buy zero coverage — E2 live proof), plain failsafe-2h strictly dominated by
hybrid. def-B flips exactly the 2h family (real p95 121.4 fails by 1.4 min on
n=1; a 90-min cron-phase shift alone un-flips it — S7), making failsafe-1h the
cheapest survivor at ~1.9× cost. Observed real-night p95 was 178 min under
nominal failsafe-2h: sweep FIDELITY, not cadence, was the binding failure.
**Verdict: approve — keep hybrid, posture unchanged** (evidence: simulation,
gate PASS, strength moderate) — full ruling and paste-ready VERDICT 014 outbox
entry at the end of the sim's REPORT.md.

Slice boundary honored: control/ appends (INTAKE 012, VERDICT 014 outbox
entry, status.md heartbeat) are deliberately LEFT TO THE COORDINATOR — this
session touched only `sims/verdict-014-routine-cadence-economics/` and this
card, and the PR is opened DRAFT per the dispatching order; the coordinator
handles green/READY and the @codex comment. Do not merge — coordinator lands
this PR.

## Run command

```
python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py
```

## 💡 Session idea

When a sim's own self-check battery contradicts your hand-derivation, debug
the HAND-DERIVATION first with a 5-line REPL probe before touching the
engine: this session's only failing check was a wrong hand-count of chain
fires (the 510 chain fire coincides with E4's arrival — 25 turns, not 26/31),
and the fix was to the expectation, not the code. A self-check that failed
for the honest reason is worth more than one that passed: it proved the
counterfactual branch actually diverges. Pattern: commit the corrected
derivation as a comment next to the check so the next reader inherits the
arithmetic, not just the constant.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-013-oracle-copy-drift.md`: clean and complete —
its "💡 Session idea" (pick modeling shortcuts that help the OTHER side; a
reject needs abstractions biased toward the thing being rejected) was applied
here in mirror image: this verdict's likely answer was "keep the incumbent",
so the optimistic assumptions (webhook wakes sweep for free) were given to the
CHALLENGER policies and the incumbent still won; the one assumption favoring
the incumbent family (idealized sweep fidelity) was measured against the
observed night and disclosed as the largest gap. Its parked-READY/never-merge
slice boundary was carried over (as DRAFT per this order). Nothing to fix;
the OA-002 codex-cap wall it recorded still stands.

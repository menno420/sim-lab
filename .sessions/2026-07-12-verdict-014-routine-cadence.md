# Session — VERDICT 014 — routine-cadence economics (idea-engine PROPOSAL 012)

> **Status:** `in-progress`
> 📊 Model: fable-5 · 2026-07-12 · verdict-014 slice-worker session
> Objective: settle idea-engine PROPOSAL 012 (control/outbox.md @ ff48c2fad809ce7704bb66aafee42335efd5c3fd) — seeded discrete-event replay of trigger-arrival trace T (real ~12.2h corpus reconstructed from idea-engine control/status.md history fc0bab6..531b109, plus seeded Poisson/burst/empty-night variants) against policy grid G = {failsafe-2h, failsafe-1h, failsafe-30m, failsafe-2h + chain-15m-while-work-open, event-driven-only, hybrid(event-driven + failsafe-2h)} under cost model C (worker-turns), answering: which policy minimizes worker-turns per caught trigger subject to p95 catch-latency ≤ 2h, and is any policy strictly dominated across all trace variants.

## What happened

(in progress — born-red card; flipped complete at close-out)

## Run command

```
python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py
```

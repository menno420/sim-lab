# verdict-014 · routine-cadence-economics

Seeded discrete-event replay for the coordinator-seat wake-policy question.
Answers idea-engine PROPOSAL 012 (control/outbox.md @ `ff48c2fa`, idea
`ideas/fleet/routine-cadence-economics-sim-2026-07-12.md` @ `87f0dd2d`, probe
verdict PR #259 head `fc90d7f`): given trigger-arrival trace T (the real
~12.2h corpus reconstructed from idea-engine `control/status.md` history
`fc0bab6..531b109`, plus seeded Poisson/burst/empty-night variants) and cost
model C (1 worker-turn per pacemaker re-arm, 1 recon-worker-turn per failsafe
sweep, ~0 marginal per webhook wake), which policy in
G = {failsafe-2h, failsafe-1h, failsafe-30m, failsafe-2h+chain-15m-while-work-open,
event-driven-only, hybrid(event-driven+failsafe-2h)} minimizes worker-turns per
caught trigger subject to p95 catch-latency ≤ 2h — and is any policy strictly
dominated across all trace variants?

## Run (one command)

```
python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py
```

Exit 0 iff all 272 self-checks pass. Deterministic — every seed is a committed
constant (base `20260712`; 40 seeds per synthetic variant; a dedicated tag-RNG
stream keeps arrival times byte-identical across the webhook-fraction sweep);
no wall clock, no unseeded randomness, no network, no first-run fetch (trace T
is embedded, with evidence SHAs). stdout and `results.json` are byte-identical
across re-runs (verified by external `diff` of two full process runs, plus an
in-process double-computation self-check). Runtime ~2 s.

## Files

- `cadence_economics_sim.py` — stdlib-only discrete-event simulator: embedded
  real trace (4 replayable arrivals E1–E4; E5 rate-counted, honestly timeless)
  + seeded Poisson (λ = 5/732 min⁻¹, derived from the real corpus) / burst /
  empty-night variants × 6 policies × webhook-visible fraction
  w ∈ {0,.25,.5,.75,1} × 2 catch definitions (def-A = to catching wake, def-B =
  +31.4 min measured done-when lag) → 144-cell table, winners, strict-dominance
  analysis, sensitivity blocks S1–S8, 272 self-checks with hand-derived
  real-trace expectations.
- `labels.json` — the hand-transcribed trace-T audit ledger: every arrival and
  null sweep with its idea-engine evidence commit and per-event reason, the
  tagging rule, the observed (historical) catches, and all 12 documented
  reconstruction gaps. The sim cross-checks its embedded constants against it.
- `results.json` — committed run output: full per-cell sweep, winners with
  margins, dominance pairs, sensitivity blocks, audit, self-check tally.
- `REPORT.md` — the finalizable verdict report (validity gate + paste-ready
  VERDICT 014 outbox entry).

## Verdict (summary — full report in REPORT.md)

**approve — keep the incumbent hybrid posture; no cadence change.** Winner
subject to p95 ≤ 2h under catch-def-A on every variant with any inbox-only
arrivals: **hybrid(event-driven + failsafe-2h)** at 1.75 turns/catch real
(1.39–1.47 synthetic), tied with plain failsafe-2h whenever the webhook-visible
class is empty (as it is on the ENTIRE real trace — event-driven-only catches
0 of 4 there). Dominance verdict: **yes** — failsafe-2h+chain-15m is strictly
dominated across all variants (chain re-arms are pure cost for coverage; live
proof: E2 arrived while the chain was alive and waited ~2.7h for the next
sweep), and plain failsafe-2h is strictly dominated by hybrid over the full
grid. The one flip that matters: if catch latency is measured to done-when
evidence (def-B, E4's 2h01m), the whole 2h family misses the p95 ≤ 2h
constraint (real: by 1.4 min on n=1; synthetics: by ~25 min) and failsafe-1h
becomes the cheapest survivor at ~2× the turns. n=1 honesty: 3 usable latency
datapoints; a 90-min cron-phase shift alone flips the def-B result on the real
trace; and the real night's OBSERVED p95 was 178 min — it violated the 2h
constraint under its nominal failsafe-2h posture because one wake failed to
sweep, a failure mode no cadence in G fixes.

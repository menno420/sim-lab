# verdict-031 · lease-renewal claim expiry (V027's routed slice, priced)

Can the explicit `renewed:` stamp VERDICT 027 routed actually clear the
bands its silence-keyed parent failed — and with which constants (expiry
horizon θ_r, wake-cadence requirement, compliance floor)? Answers
idea-engine PROPOSAL 029 (control/outbox.md 2026-07-13T06:51:49Z, idea
`ideas/substrate-kit/lease-renewal-claim-expiry-2026-07-13.md`, landed via
idea-engine PR #297, main `0e168bf`) — the ORDER 004 rule-3 FLEET-BACKLOGS
rotation slot, round 4, following round 3's own verdict-opened thread
(P025 → V027 reject: "silence is the wrong signal — route the lease-renewal
slice"). Fully hermetic: every fixture a pinned constant committed with the
sim (V027's anchor constants and the two measured multisets travel inside
`fixtures.json`); zero repo/network reads at run time.

Model: an alive lane holds one claim H_c = 168 h, wakes every
p_w ∈ {2, 12, 24} h, re-stamps `renewed:` except an i.i.d. forget
p_f ∈ {0.02, 0.10, 0.25}; with p_d = 0.10 it dies at a uniform wake;
contenders (Poisson λ_c) take over claims overdue past θ_r ∈ {6…72} h.
T (twin risk) at λ_c = 1/4; O95 (deadlock cost) at λ_c = 1/12; C48
reporting-only via the restated distribution-free identity. 9 decision
cells × 5 θ_r. Arm A exact and seedless (trailing-run DP + exact mixture
quantile; cross-checked by an independent distribution DP, a 2^N
exact-Fraction brute force, and four hand pins); Arm S seeded event-driven
MC (seeds 20260756–59, gates pre-checked ≥ 2.5σ in the fixture BEFORE any
run). Chained anchor: the silence-baseline leg must reproduce V027's
committed Feas map exactly (it does; the committed V027 runner was also
re-run out-of-sim, byte-identical at `fcb39e3`).

Decision (registered order, REJECT first): REJECT iff Feas = ∅ in ≥ 5/9
cells → APPROVE iff a single θ_r† is feasible in ≥ 8/9 (gates + stability
holding) → NULL. **Result: NULL (APPROVE barred by the pre-pinned gate
protocol — 2 of 90 effective point-gates breached at ≤ 2.73σ, both pure
sampling noise at 16×; the exact arm met the APPROVE bands: coverage 8/9 at
48 h, 9/9 at 72 h).** The conditional rule ships; the warn-first
missed-renewal counter is the named live probe.

## Run (one command)

```
python3 sims/verdict-031-lease-renewal/lease_renewal_sim.py
```

Exit 0 iff all self-checks pass (1,691,638). Deterministic: byte-identical
stdout + `results.json` across two process runs by external diff,
cpython-3.11 pinned and asserted. No network, no git, no wall clock.
Progress goes to stderr only. ~9 s.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the decision rule with its evaluation order, the ≥ 2.5σ gate
  pre-check rule + handling protocol, the V027 chained-anchor contract, the
  two measured multisets, 13 intake-time decisions and 4 hand pins
  (committed BEFORE the runner; one pre-runner amendment, git history is
  the trail).
- `lease_renewal_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).

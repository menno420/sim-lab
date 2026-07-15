# verdict-086 — the write-contract rate-tier degeneracy (INTAKE 073)

Prices idea-engine PROPOSAL 073's harvested tension where it lives: the
mineverse mining-action WRITE contract commits a two-tier rate limit —
"**Burst**: 10 actions per 10 seconds. / **Sustained**: 60 actions per
minute." (docs/mining-write-contract.md:164-165 @ `b9ade33`) — whose
tiers have IDENTICAL average rates (B·T = S·w = 600, both exactly
1 action/s), with the window DISCIPLINE unstated, while the contract's
committed reference implementation (the shim) carries exactly ONE knob,
a sliding window (tests/shim/shim_bot.py:115, `_consume_budget`
:340-366), and the real executor is unbuilt (contract line 37; superbot
@ `f8e2313`). Three exact structure theorems carry the verdict: the
sustained tier is DEAD INK under every uniform discipline (two margin-0
contacts at 60 = S plus a 50-token bucket margin); the burst tier ALONE
under the two leakier disciplines breaks the sustained promise in the
worst 60 s span (fixed-adversarial 70 = 7/6·S, bucket 69 = 23/20·S,
boundary straddle 20 = 2B); and the committed constants sit exactly ON
the redundancy boundary (B·⌈T/w⌉ = S at equality; S = 50 flips live,
w = 7 dies by divisibility at 90 > 60). All decision arithmetic is
seedless exact integers/Fractions judged against the 21/20 band fixed
at registration (REJECT first). The runner is hermetic — it reads ONLY
`fixtures.json` (committed before the runner); the external grounding
pins were re-verified FIRSTHAND on read-only shallow clones BEFORE the
fixture was written (zero harvest anomalies).

## Run

```
python3 sims/verdict-086-write-contract-rate-tier-degeneracy/rate_tier_degeneracy_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~0.3 s. Every
decision number is an exact integer or Fraction; the seeded Arm R
carries no statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 073 block / idea file (the committed pair with its file:line
  pins, the slotted-time model and the four disciplines, the closed
  forms, the (B, w) × S × L grids, the decision cell, the F3 census
  anchors, the F4 pencil world, the F5 controls, the Arm-R parameters
  and seeds 20261650–653, the REJECT R1/R2/R3 bands, the margin ledger
  with its four REGISTERED margin-0 contacts, the disclosed Arm-R
  reporting landing), plus fixture-level conventions C1–C13 — committed
  BEFORE the runner, including C3 (disclosed Arm-R reporting mismatches
  raise first-class anomalies, never silent gates) and C5 (no
  UNregistered decision comparison may sit at margin 0 — the registered
  contacts are the head's thesis).
- `rate_tier_degeneracy_sim.py` — three-arm runner: Arm A seedless
  closed-form maxima + dead-tier invariant + redundancy law (exact;
  decision-bearing), Arm B INDEPENDENTLY-WRITTEN twin (greedy witnesses
  with matching combinatorial upper bounds, explicit alignment
  enumeration, exhaustive small-world searches incl. the 3⁴ pencil
  world, its own two-bucket trace + scaled exhaustive minimizer check,
  its own separating-schedule search; powers the second decision
  evaluator), Arm R seeded Poisson click streams through a VERBATIM
  re-implementation of the shim's `_consume_budget` (main 20261650 at
  50,000 events, stability 20261651 at 20,000, presentation shuffle
  20261652, aux 20261653 NEVER read; reporting-only) plus the
  deterministic obedient Retry-After client (an F3 gate: exactly 3600
  admits in 3600 s).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the full maxima/dead-tier/lattice surface, the
  margin ledger with the registered knife-edges, the F1–F6 gate
  results, the anomaly census (empty — the drafter's every disclosed
  numeral reproduced exactly, decision AND reporting), the Arm-R traces
  beside the theorem contacts, and the twin-arm / byte-identity notes.

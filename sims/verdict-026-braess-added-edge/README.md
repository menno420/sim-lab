# verdict-026 · braess-added-edge

How OFTEN and by HOW MUCH does adding a shortcut edge to the classic Braess
diamond RAISE the selfish-equilibrium total travel time? Answers idea-engine
PROPOSAL 024 (control/outbox.md 2026-07-13T04:21:12Z, idea
`ideas/fleet/braess-paradox-added-edge-2026-07-13.md`, landed via idea-engine
PR #290, main `b11e258`) — the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain
rotation slot, round 2: transportation / congestion routing games (Wardrop
selfish-user equilibrium), a fresh fleet-external domain after round 1's
social choice (PROPOSAL 017 → VERDICT 019). Fully hermetic per the PROPOSAL
017–023 precedent: both arms construct their entire world in-sim — zero
repo/network reads in the verdict session; Arm A has no PRNG at all.

Model: the pinned Braess diamond (nodes s,a,b,t; base edges e1=s→a, e2=a→t,
e3=s→b, e4=b→t; optional bridge e5=a→b enabling route s→a→b→t), unit demand
D=1 routed to the UNIQUE Wardrop user equilibrium under affine non-decreasing
latencies l_e(x)=a_e·x+b_e (a_e ≥ 0), equilibrium and total cost
C = Σ_e x_e·(a_e·x_e+b_e) computed exactly. **Arm A**: exhaustive integer
census (a_e,b_e) ∈ {0,1,2}² on e1..e4 × (a5,b5) ∈ {0,1}² on the bridge =
9⁴·4 = 26,244 raw fixtures, 0-cost-without fixtures excluded (effective N
reported), exact `fractions.Fraction` end to end — f_A (paradox frequency:
cost_with > cost_without), median-r and max-r among paradox fixtures
(r = cost_with/cost_without). **Arm S**: seeded continuous robustness —
a_e,b_e ~ U[0,2], `random.Random` seeds 20260740–43, 25,000 draws per seed
(100,000 pooled), documented float tolerance — pooled f_S. Bands registered
in the idea file BEFORE any code: APPROVE iff f_A ≥ 0.15 OR median-r ≥ 1.15;
REJECT iff f_A ≤ 0.03 AND max-r ≤ 1.05; NULL otherwise; non-NULL requires
the arm-agreement gate (|f_S − f_A| ≤ 1.0 pp AND same call).

## Run (one command)

```
python3 sims/verdict-026-braess-added-edge/braess_added_edge_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — Arm A is exact
platform-independent rational arithmetic with no PRNG; Arm S consumes exactly
10 uniforms per draw from `random.Random(<pinned seed>)` (draw-count
sentinels close exactly). No network, no git, no wall clock, no `hash()`.
stdout and `results.json` are byte-identical across process runs (verified by
external `diff` of two complete runs, cpython-3.11 pinned and asserted).
Progress goes to stderr only.

## Files

- `braess_added_edge_sim.py` — stdlib-only driver: primary solver = Beckmann
  candidate enumeration (simplex vertices + clamped edge-minimizers +
  interior stationary point via exact 2×2 solve) with per-fixture EXACT
  Wardrop variational-inequality verification (the verification, not the
  construction, carries the proof — plus essential uniqueness of equilibrium
  cost for monotone latencies); an independently written support-enumeration
  TWIN solver run on the FULL census (both networks) and on every 199th Arm-S
  draw; analytic gates g1–g6 (Wardrop VI everywhere; the affine Braess bound
  r ≤ 4/3 exact; the reversal-symmetry involution σ(e1..e5)=(e4,e3,e2,e1,e5)
  across the census; unused-bridge invariance both directions; CPython pin +
  byte-identity; exact draw-count sentinels); three hand-derived pins with
  committed derivations.
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file, the bands and arm-agreement gate,
  the model-basis declaration, seven disclosed intake-time decisions, and the
  three hand-derived pins with full derivations.
- `results.json` — committed run output: the full registered results table
  plus reporting-only breakdowns (paradox by bridge cell; improved/unchanged
  counts) and per-seed Arm-S counts.
- `REPORT.md` — the finalizable verdict report (validity gate + the
  VERDICT 026 ruling).

## Verdict (summary — full report in REPORT.md)

**null (the pre-registered straddle, arms agreeing — finalized)** — Braess's
paradox in this class is REAL but neither common nor large enough for a
blanket design rule, and too common/large to declare added edges
safe-by-default:

- **Arm A (exact):** N = 25,600 (644 zero-cost fixtures skipped of 26,244);
  paradox count 855 → **f_A = 171/5120 = 0.0334** (3.34%); **median r =
  80/77 ≈ 1.039**; **max r = 4/3 exactly** — the census contains the
  canonical worst case, so REJECT's magnitude leg (max-r ≤ 1.05) was
  unreachable, and its frequency leg missed too (0.0334 > 0.03 by 0.34 pp).
  APPROVE missed by 4.5× on frequency (0.0334 vs 0.15) and by 0.11 on
  median inflation (1.039 vs 1.15).
- **Arm S (continuous, 100,000 pooled draws):** f_S = 0.02908 (per-seed
  0.0304/0.0285/0.0292/0.0282), median r ≈ 1.005, max r ≈ 1.094 → same NULL
  call; **|f_S − f_A| = 0.43 pp ≤ 1.0 pp** — the integer grid is NOT a
  paradox-inflating artifact.
- **Reporting-only:** the bridge HELPS 15.3× more often than it hurts
  (improved 3,913 = 15.3% vs paradox 855 = 3.3%; unchanged 20,832 = 81.4%);
  free bridges hurt most (paradox 5.5–5.6% at b5=0 vs 1.1% at b5=1).
- **Model basis (declared):** the number is conditional on selfish Wardrop
  routing under uniform coefficients; under system-optimal routing the
  paradox cannot occur (f → 0).

358,476 self-checks, 0 failed; stdout + results.json byte-identical across
two full process runs by external diff on cpython-3.11; ~11 s per run.

# Session — VERDICT 026 — Braess's paradox added-edge frequency (idea-engine PROPOSAL 024)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-026 slice-worker session
> Objective: settle idea-engine PROPOSAL 024 (control/outbox.md · 2026-07-13T04:21:12Z · status: sim-ready; idea `ideas/fleet/braess-paradox-added-edge-2026-07-13.md`, the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain rotation slot, round 2 — transportation / congestion routing games, Wardrop selfish-user equilibrium, rotated to a fresh fleet-external domain after round 1's social choice (PROPOSAL 017 → VERDICT 019)). Build the fully hermetic pre-registered measurement of Braess's paradox frequency and magnitude on the pinned diamond (nodes s,a,b,t; base edges e1=s→a, e2=a→t, e3=s→b, e4=b→t; optional bridge e5=a→b; unit demand D=1 routed to the UNIQUE Wardrop user equilibrium under affine non-decreasing latencies l_e(x)=a_e·x+b_e, a_e≥0; equilibrium and total cost C=Σ_e x_e·(a_e·x_e+b_e) computed exactly). Arm A: exhaustive integer census (a_e,b_e)∈{0,1,2}² on e1..e4 × (a5,b5)∈{0,1}² on the bridge = 9⁴·4 = 26,244 raw fixtures, 0-cost-without fixtures excluded and effective N reported, all arithmetic exact `fractions.Fraction`, no PRNG — f_A (paradox frequency: cost_with > cost_without), median-r and max-r among paradox fixtures (r = cost_with/cost_without). Arm S: seeded continuous robustness — a_e,b_e ~ U[0,2], `random.Random` seeds 20260740/20260741/20260742/20260743, documented float tolerance on the paradox comparison, pooled f_S. Arm-agreement gate: |f_S − f_A| ≤ 1.0 pp AND both arms yield the SAME call, else NULL-by-arm-disagreement. Bands registered in the idea file BEFORE any code: APPROVE iff f_A ≥ 0.15 OR median-r ≥ 1.15; REJECT iff f_A ≤ 0.03 AND max-r ≤ 1.05; NULL otherwise. Byte-identical re-run (Arm A platform-independent exact rationals; Arm S pinned to a stated CPython minor version); model-basis caveat stated (selfish Wardrop routing under uniform coefficients; the single most-likely-to-flip alternative is system-optimal routing, under which Braess cannot occur and f → 0). Hermetic: zero repo/network reads at run time — both arms construct their entire world in-sim.

## What happened

Built `sims/verdict-026-braess-added-edge/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: the sim reads exactly one file (its own
committed `fixtures.json` pre-registration, cross-checked at start) and
touches no repo state, network, or wall clock; both arms construct their
entire world in-sim. The pre-registration (all constants verbatim from the
idea file, the bands and arm-agreement gate, the model-basis declaration,
SEVEN disclosed intake-time decisions, three hand-derived pins with full
derivations) was committed BEFORE the runner was written. A throwaway
scratchpad feasibility probe (solver approach + runtime) ran before the
fixtures commit and is disclosed inside fixtures.json — every decision
constant was already pinned by the idea file, so no free parameter remained
tunable by that peek.

**Run output summary:** `SELF-CHECKS: 358476 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
diff), cpython-3.11 pinned, ~11 s per run. **Ruling: NULL — the
pre-registered straddle, arms agreeing, finalized.** Arm A (exhaustive
integer census, exact Fractions, no PRNG): N = 25,600 (644 zero-cost
fixtures skipped of 26,244), paradox 855 → f_A = 171/5120 = 0.0334 EXACTLY;
median r = 80/77 ≈ 1.039; max r = 4/3 exactly (the canonical Braess
configuration lives in-census, a committed hand pin). APPROVE fails (0.0334
< 0.15; 1.039 < 1.15); REJECT fails (0.0334 > 0.03 by 0.34 pp; 4/3 > 1.05 —
the magnitude leg was unreachable by construction). Arm S (U[0,2]
continuous, seeds 20260740–43, 100,000 pooled): f_S = 0.02908, same NULL
call, |f_S − f_A| = 0.43 pp ≤ 1.0 pp — arm gate met; the integer grid is
not a paradox-inflating artifact. Reporting-only: the bridge HELPS 15.3%
vs hurts 3.3% (unchanged 81.4%), and free bridges hurt ~5× more often than
costly ones (5.5%/5.6% at b5=0 vs 1.1% at b5=1). Twin support-enumeration
solver exact on the full census, within 1e−6 on 504 strided draws; gates
g1–g6 all PASS (exact Wardrop VI everywhere, affine 4/3 theorem-bound,
reversal-symmetry involution, unused-bridge invariance, CPython pin +
byte-identity, exact draw-count sentinels).

Slice boundary this cycle (the V015–V025 precedent): this session carries
the INTAKE 024 and VERDICT 026 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). The tail at append was VERDICT 025 (PROPOSAL 023,
landed @ 0a8a222 by the sibling session while this sim was building) — the
branch was rebased onto it before the append, numbering unaffected, +2
offset preserved (P024 → V026), origin/main re-checked immediately before
the append. No @codex step — suspended per the outbox codex-line escalation
@ dedc12e. Born-red card and complete flip land in one push (the V018–V025
choreography). Hermeticity honored end-to-end: zero repo/network reads at
sim run time, Arm A carries no randomness at all.

## Run command

```
python3 sims/verdict-026-braess-added-edge/braess_added_edge_sim.py
```

## 💡 Session idea

When a sim's correctness argument rests on a THEOREM (here: Wardrop
equilibrium ⟺ Beckmann minimizer, plus essential uniqueness of equilibrium
cost for monotone latencies), make the theorem's hypothesis an executed
gate, not a comment: this sim never trusts its solver's construction —
every returned point is re-verified against the exact variational
conditions per fixture, so the candidate-enumeration solver could be
arbitrarily wrong and the run would still either produce a PROVEN
equilibrium cost or die red. The portable rule: prefer "construct cheaply,
verify exactly" over "construct provably" — the verification is usually a
few lines, covers every degenerate path the construction might mishandle
(singular Hessians, boundary optima, ties), and turns a subtle solver bug
into a loud gate failure. Paired bonus: when the domain has a known
worst-case theorem (the affine 4/3 Braess bound), assert it over the whole
census — a free theorem-gate that catches ratio-computation bugs with zero
extra machinery.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-024-keep-margins-noise.md`: complete and
honest; its exports are adopted here directly. (1) The one-push born-red
choreography is followed verbatim. (2) Fixtures-before-runner, including
hand-derived pins WITH derivations committed before code — reused (three
pins: the canonical Braess diamond 3/2→2 with r = 4/3; the all-constant
no-paradox fixture; a bridge-HELPS fixture 2→1); its "recompute every
hand-pin's closed form mechanically" export is moot here — the pins are
one-line exact rationals, asserted directly against the census in Fraction
arithmetic. (3) Its independently-written-twin pattern — reused as a
support-enumeration solver with its own latency/cost code paths, exact on
the full census rather than strided (the census is small enough to afford
it). (4) Its exact draw-count sentinel discipline — reused (10 uniforms per
Arm-S draw, fresh Random(seed) rejoining each leg's stream exactly); the
one-uniform-per-normal trick was not needed (no normals drawn). (5) Its
smoke-test-before-pinned-run practice — followed via the disclosed
scratchpad feasibility probe; NOTE the disclosure nuance this slice adds:
when the pinned seeds themselves get exercised pre-commit, say so in
fixtures.json and name why no free parameter remained tunable.

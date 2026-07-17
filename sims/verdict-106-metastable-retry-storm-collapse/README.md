# VERDICT 106 — Retry-amplified metastable overload collapse (P093)

## Question
Does a lane pool at ~60% utilization become BISTABLE above a critical retry-aggressiveness r_c≈0.57 — so a transient load blip tips it into a self-sustaining retry storm that persists after load falls back (hysteresis) — and is the fix a retry BUDGET rather than more lanes?

## Pinned world (one-liner)
c=100 lanes; failure p(x)=p0+(1−p0)·σ(k·(u−θ)) with u=x/c, p0=0.02, k=12.0, θ=1.05; mean-field balance x=λ+r·p(x)·x; pinned r=0.85, λ=60 (disclosed correction 70→60); retry-budget cap b=0.20; SEED_BASE=20260721; SIG=3.0.

## Model
Mean-field in-flight load x with F(x)=λ+r·p(x)·x−x; fixed points are roots of F, stability from sign of F′ (stable if F′<0). Collapsed mean-field root x*=λ/(1−r)=400 (u=4.0); healthy COLD root ≈61 (u≈0.61). Continuation quantity G(x)=x·(1−r·p(x)) with F=0⇔G=λ; its local max/min give the adiabatic sweep limits λ_up (COLD fold) and λ_down (HOT fold). Stochastic check: seeded Poisson-style noisy map started COLD vs HOT. Independent stdlib-only reimplementation from the registered spec — not the proposal dry-sim.

## Pre-registered decision rule
APPROVE iff R1 ∧ R2 ∧ R3 ∧ R4 (fired in order):
- R1: F has two stable roots COLD≈61 and HOT≈400 split by an unstable middle (a), AND a seeded stochastic run started COLD stays healthy while started HOT stays collapsed, separated ≥3σ (b).
- R2: hysteresis width = λ_up−λ_down ≈ 56, AND λ=60 shows coexistence (both stable).
- R3: fold width monotone non-decreasing in r; operating point λ=60 becomes bistable above r_c≈0.566 (where λ_down(r) crosses 60), monostable below.
- R4: with retry-budget cap b=0.20 (x=λ+min(r·p·x, b·λ)−x) the HOT root is eliminated — only COLD remains.

## How to run
    python3 metastable_retry_storm_sim.py
Writes results.json + run-stdout.txt + fixtures.json; regenerates identically (delete and rerun → byte-identical). Exits non-zero on any self-check failure, twin disagreement, or fixture drift. stdlib only. Twin evaluators: bisection vs secant root-finders; fold-via-G-extrema vs fold-via-root-count; if-chain vs table decision.

## Outcome
APPROVE (first-failing gate: none). Fixed points COLD 61.311 (stable), MIDDLE 104.748 (unstable), HOT 400.000 (stable, =x*). R1 stochastic separation 308.8σ (cold u=0.615, hot u=3.992). R2 λ_up=78.070, λ_down=22.679, width=55.391, coexistence at λ=60. R3 width monotone (max drop 0.0), r_c=0.5642. R4 cap collapses 3 roots→1 (HOT gone). 25/25 self-checks; twins agree APPROVE/None; double-run byte-identical.

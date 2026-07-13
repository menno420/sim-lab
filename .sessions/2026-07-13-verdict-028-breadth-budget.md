# Session — VERDICT 028 — round-3 breadth budget under the q99 bar (idea-engine PROPOSAL 026)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-028 slice-worker session
> Objective: settle idea-engine PROPOSAL 026 (control/outbox.md · 2026-07-13T05:40:19Z · status: sim-ready; idea `ideas/trading-strategy/round3-breadth-budget-q99-power-2026-07-13.md` @ idea-engine main 0716140, PR #293 — the ORDER 004 rule-3 VENTURE rotation slot, round 3, trading half). Build the fully hermetic pre-registered POWER measurement complementing VERDICT 024's null-side burden bar: plant per-instrument epoch drifts α_{j,e} = κ·(σ_d/√252)·g_{j,e} (redrawn every E bars) into V024's own committed panel machinery (in-repo byte-reuse @ sim-lab 5e356ed), sweep κ ∈ {0.5, 1.0, 2.0} × E ∈ {21, 63, 252} × ρ ∈ {0.0, 0.3, 0.6} = 27 decision cells, and measure the expected true-keep yield Y(cell, N) each nested design grid G6 ⊂ G10 ⊂ G24 ⊂ G96 harvests under its own in-run κ=0 null q99 bar b_N(ρ) (M = 1,000 per ρ), chained-anchored to V024's committed q99 values within ±0.05. Oracle margins θ_i = no-selection cell means (M = 400 per cell, seed 20260748), true edge θ ≥ 0.10, N* = smallest N within 5% of max yield, detectable = max_N Y ≥ 0.25. Gates, run invalid on any failure: chained anchors, k=9 identity (Δ ≡ 0 to 1e−12), independent-leg familywise (bars from leg A on a fresh M = 500 leg B, false-keep rate within 3 binomial SE of 0.01), oracle sign gates, cpython-3.11 pinned, stdout + results.json byte-identical across two process runs. Stability leg seed 20260749 (M = 200) must reproduce the ruling; seeds 20260750 validation + reporting (S_bh = 0 arm, RSV arm, marginal-config price list at N = 7), 20260751 aux. Decision (registered order): REJECT iff N* ≤ 10 in ≥ 80% of detectable cells; APPROVE iff N* ≥ 24 in ≥ 80% of detectable cells AND median Y(96) − Y(6) ≥ +0.25; NULL otherwise (or < 8/27 detectable), flip axis named per-axis + the lane's rank-autocorrelation live probe. Hermetic: zero repo/network reads at run time; zero real market bars; the owner-gated post-2026 protocol untouched.

## What happened

Built `sims/verdict-028-breadth-budget-power/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: the sim reads exactly one file (its own
committed `fixtures.json` pre-registration, cross-checked at start) and
touches no repo state, network, or wall clock. The pre-registration (all
constants verbatim from the idea file; V024 anchor constants at full
precision; 13 disclosed intake-time decisions) was committed BEFORE the
runner. V024's committed machinery was byte-reused and machinery identity
verified bit-exactly (same-seed panels + all 96 per-config deltas `==` the
parent's committed code at ρ ∈ {0.0, 0.3}).

**Three gate calibrations were re-based mid-session under the V027
disclosed-conflict protocol, each pinned in `fixtures.json`
(`gate_calibration_disclosure`) BEFORE the full decision run, none touching
a band, seed, M, the rule, or the evaluation order:** (1) at E=21 the
planted epochs align exactly with the 21-bar rebalance frame, so every
config's expected θ is identical (exact exchangeability) — the registered
strict sign gate is a fair coin per E=21 cell (P(all 9 pass) ≈ 2⁻⁹);
re-formed at E=21 only as matched 4·SE noise bands (found at the reduced-M
scratchpad smoke run, disclosed before any full run). (2) The registered
±0.05 anchor tolerance's "fresh-seed MC tolerance at M = 1,000" premise
measured FALSE with the parent's own committed code (q99(G6)|ρ=0 across
seeds {20260748, 111, 222, 333} = {0.3057, 0.3840, 0.3537, 0.4147} —
fresh-seed SD ≈ 0.046, a ~1.1σ gate): the first full-M attempt exited AT
the anchor gate before any decision number existed; the run-invalidating
anchor became the exact two-sample tail count X ~ BetaBinomial(1000; 11,
991), gate [1, 30], with the registered ±0.05 recorded per point (2/9
breached — quantile noise). (3) The familywise gate's unpriced bar-quantile
noise got a pinned leg-C handling protocol (aux M = 2,000/ρ) — armed but
UNUSED (0/12 breaches at the registered rule).

**Run output:** `SELF-CHECKS: 61890 passed, 0 failed`, exit 0, stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `ea8a6aee…`, results `5cdb9198…`), cpython-3.11 pinned,
~5.5 min/run, 729.2M draws sentinel-audited. **Ruling: APPROVE — blanket
breadth survives its own bar.** 11/27 cells detectable (floor 8; all 9
E=21 cells undetectable BY CONSTRUCTION — the alignment fact above; κ=0.5
detects only at (252, 0.6)); N* = 96 in 11/11 detectable cells (REJECT,
checked first: 0/11); median Y(96) − Y(6) = +14.2125 ≥ +0.25; stability
leg (seed 20260749, M = 200) reproduces APPROVE. Null bars b_N(ρ) ship as
a second independent draw of V024's table; marginal price list: direction
decoys are a pure tax (largest bar increase +0.0250, ΔY ≤ 0), short-horizon
additions nearly bar-free (+0.0009). Measured qualifiers in the verdict:
breadth pays through REDUNDANT truth, not coverage; the binding boundary is
detectability, so the lane's zero-cost rank-autocorrelation probe stays
recommended before the round-3 registration fixes N.

Landed: INTAKE 026 (2026-07-13T06:30:56Z) + VERDICT 028
(2026-07-13T06:30:57Z) appended to `control/outbox.md` (append-only);
verdict PR from `claude/verdict-028-breadth-budget`. Worker session — no
heartbeat writes; this card flip is the last commit.

## 💡 Session idea

Chained cross-verdict anchors should be registered as TWO-SAMPLE tests, never
as value tolerances: a committed empirical quantile is itself a draw (V024's
q99(G6)|ρ=0 carries a fresh-seed SD of ~0.046, measured this session with the
parent's own code), so "reproduce within ±0.05" is a ~1.1σ coin toss against
it even with bit-identical machinery. The portable fix used here: anchor on
the exact two-sample tail count X = #{child null draws ≥ parent committed
quantile} — under machinery identity X ~ BetaBinomial(n; m−k+1, k) exactly
(parent's k-th order statistic of m), which prices BOTH runs' noise with no
density estimation and turns the anchor into a calibrated ~3.3σ gate. The
deeper anchor is cheaper still and exact: when the parent's machinery lives
in the same repo, verify machinery identity BIT-EXACTLY (same-seed panel +
full delta vector `==`) and let the distributional test cover only what
bit-identity cannot (the new layer). Kit-worthy pair with V027's session
idea: registered tolerances on ANY estimated anchor should ship their
SE-multiple at registration time.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-027-claim-expiry.md`: complete and honest;
its exports are adopted here directly. (1) The born-red choreography and
fixtures-before-runner discipline followed verbatim. (2) Its headline export
— "do the SE arithmetic BEFORE the first draw and pin the handling protocol
in the fixtures" — was applied three times this session (E=21 sign-gate
exchangeability, the ±0.05 anchor premise, familywise bar-quantile noise),
each disclosed in `fixtures.json` with git history as the trail before the
full decision run; exactly the V027 protocol, and its predicted failure mode
(a registration tolerance sitting at ~1σ of the registered-n estimator)
recurred here on a THIRD gate class (quantile anchors, after V027's MC
gates), strengthening the case for the kit-level registration rule. (3) Its
"the decision arm carries no randomness where possible" export — transposed:
every band decision here is an exact integer/Fraction test on keep-count
sums, with twin decision evaluators required to agree.

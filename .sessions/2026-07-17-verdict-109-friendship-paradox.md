# VERDICT 109 — friendship-paradox epidemic sensors: degree-biased ("friend-of-friend") sensor placement detects an SI epidemic with a positive detection LEAD over uniform-random placement, and the effect is degree-variance-driven (vanishes under a degree-matched regular graph)

> **Status:** `complete`
> 📊 Model: agent · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Independent stdlib-only reverification of idea-engine PROPOSAL 096 (2026-07-17T13:24:56Z, sim-ready), offset +13 (P096 → V109): does friendship-paradox (degree-biased) sensor placement give a positive, decision-relevant detection LEAD over uniform-random placement on a heavy-tailed (Barabási–Albert) contact graph, and is that lead driven by degree variance — i.e. does it vanish on a degree-matched regular (W0) control?

## Constraints honored
- stdlib-only, hermetic, deterministic (byte-identical double run; own in-file seeds W1=20260717, W0=20260718, MC=777, independent of the proposal's draws).
- Independent re-implementation from the registered spec; each run uses its OWN committed degree-sequence moments as the R1 analytic anchor (pre-registered rule).
- Pre-registered gates R1→R4 evaluated in order, verdict never softened; twin evaluators must agree.

## Gate plan
- R1 (analytic anchor): friendship-paradox ratio E[k²]/E[k] from the committed W1 degree sequence vs a Monte-Carlo half-edge estimate (200000 draws, seed 777); PASS iff relerr < 2%.
- R2 (decision-relevant, W1 BA): mean detection lead (Random − FP) over T trials; PASS iff ≥ 3σ positive.
- R3 (negative control, W0 6-regular): same lead statistic; PASS iff NOT ≥ 3σ (effect must be degree-variance-driven, absent under degree-matching).
- R4 (sanity): committed moments reproduce the built degree sequence exactly (Σdeg = 2|E|), Var/E[k] < max degree, all finite detection times ≤ horizon, |mean lead| ≤ epidemic duration.

## ⟲ Previous-session review
Prior loop P095 → V108 (catch-up rubber-band controller-instability) landed APPROVE — sim-lab PR #181 (head 80cf099), sims/verdict-108-rubber-band-controller/. V108's independent-reimplementation discipline (own seeds, gate-outcome CONFIRM over digit-level reproduction) carries into this slice.

## 💡 Session idea
The R3 negative control is the load-bearing part of this verdict: the BA lead (+1.17 steps, 20σ) only *means* "friendship-paradox sensing works" because the degree-matched 6-regular control collapses it to −1.15σ — the advantage is degree variance, not sensor count. The proposal's own named follow-up F1 (sweep β and network family to map lead-time vs Var/E[k]) is the natural next slice: with W0 pinning the zero-variance floor and W1 the heavy-tail ceiling, a Var/E[k] sweep would turn this binary APPROVE into a calibrated dose-response curve — the strongest evidence that the effect tracks the Feld 1991 μ+σ²/μ prediction rather than the BA topology specifically.

📊 Model: agent · high · verdict-sim

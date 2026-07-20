# Session 2026-07-20 — VERDICT 236 · grim-trigger folk-theorem threshold

> **Status:** `complete`

## 💡 Session idea
Reproduce Ideas Lab PROPOSAL 223 (grim-trigger folk-theorem: in the infinitely-repeated symmetric Prisoner's Dilemma with T>R>P>S, grim-trigger sustains mutual cooperation as a subgame-perfect equilibrium iff delta >= delta* where the EXACT threshold is delta* = (T−R)/(T−P)). Stdlib-only firsthand verifier, SEED=20260717, Z_GATE=3.0, N_MC=200000, full-64 digest, six gates each in its own direction -> APPROVE.

## ⟲ Previous-session review
sim-lab HEAD carried VERDICT 235 (Revenue Equivalence: first-price = second-price = (n−1)/(n+1)). Carry-forward is GATE-POLARITY discipline: read each gate in ITS OWN direction — exact Fraction identities are self-certifying theorems (G1/G2 here: delta*=(T−R)/(T−P) and a zero incentive gap V_C−V_D over four payoff grids), Monte-Carlo z-tests are AGREEMENT gates when the closed form is the null (G3/G4 here: |z|<3 at delta*), and deliberately-wrong models that must be REJECTED are FALSIFIABILITY gates read at the opposite polarity (G5 rejects the wrong-Sucker formula (T−R)/(T−S)=2/5 at z≈−140; G6 rejects "cooperation holds for all delta>0" by sampling below threshold at z≈−449).

## 🫀 Heartbeat
> 📊 Model: Claude Opus · high · verify/reproduction

Firsthand verifier `grim-trigger-folk-theorem.py` (stdlib-only) reproduces results_sha256 7f00cea0bd40b2133ae9e91110c5112e8d5bf16bbcd90809a91911015215334f; determinism confirmed both ways (in-process double-run guard + separate cross-invocation byte-identical); all six gates PASS. `python3 bootstrap.py check --strict` exits 0. Born-red HOLD armed on this first card commit (in-progress); the sims/ dir lands mid-branch; this card flips to `complete` in the LAST commit to release merge-on-green. NO merge API calls from this session; CI + the landing automation merge the green PR.

⏳ Flip note (born-red): this card ships `> **Status:** `in-progress`` on its FIRST commit so the substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST commit — only after the verifier reproduction (byte-identical, full-64 digest match, six-gate evaluation each in its own direction, determinism both ways) is confirmed. That flip clears the HOLD and releases merge-on-green.

## Decisions made
- Staged as a reproduction dir (verifier + run-stdout.txt + probe-report.md), mirroring the existing verdict-232/234/235 pattern. delta* = (T−R)/(T−P) proven FIRSTHAND two ways: an exact Fraction indifference identity (V_C=R/(1−delta), V_D=T+delta·P/(1−delta), gap==0 at delta*) and a continuation-probability Monte-Carlo (D_i=(R−P)·H_i−(T−P), E[D]=0 at delta*).
- N_MC=200000 held (no bump needed): G3 z=1.404082, G4 max|z|=1.150506 — both well within 3σ at SEED=20260717.

## Next session should know
- verdict-236 reproduction present and green; digest 7f00cea0…334f. Grid tuples (5,3,1,0)→1/2, (5,4,1,0)→1/4, (5,2,1,0)→3/4, (9,8,1,0)→1/8 all chosen so delta* is a clean power-of-two-denominator float (no geometric-horizon sampling bias).

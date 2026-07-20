# VERDICT 247 reproduction — put-call parity holds exactly in a no-arbitrage binomial market (C − P = S₀ − K·R⁻ⁿ); reproduction-only, canonical ruling deferred

> **Status:** complete

📊 Model: Opus · high · verdict-reproduction
started: 2026-07-20T23:14:51Z

💓 Heartbeat:
- round/slot: sim-lab mirror · P234 → V247 (+13 offset)
- branch: claude/verdict-247-put-call-parity
- sim dir: sims/verdict-247-put-call-parity/
- verifier: byte-identical copy of idea-engine ideas/venture-lab/verify_234_put_call_parity.py
- SEED: 20260717 · results_sha256: 637c7b8a0b3a12090d377c4cf10994d81880aed0095bc3966a8a9328b587ede4
- determinism: in-process double-run IDENTICAL · separate re-invocation byte-identical
- G1 exact parity (Fraction, 4-market panel) · pass
- G2 MC agreement 400000 trials, z=−0.112845, |z|<3 · pass
- G3 invariance (volatility + scale) · pass
- G4 falsifiability naive undiscounted-strike z_naive=246.993214, |z|≥6 · pass
- all_pass: true · first_failing_gate: null · decision: sim-ready
- ruling: DEFERRED to coordinator VERDICT 247 slice (mirror does not advance verdict high-water)

⏳ Flip note (born-red): commits FIRST as in-progress to hold the PR red behind substrate-gate; flips to complete as the LAST commit after the sim dir, digest match, and four-gate eval land, releasing merge-on-green.

## What this verdict does
Reproduces idea-engine PROPOSAL 234 byte-for-byte in sim-lab and records the run. Reproduction-only: the canonical APPROVE/QUALIFIED/REJECT ruling and the verdict high-water belong to the coordinator-driven VERDICT 247 slice.

## Method
Copied the firsthand verifier verbatim, ran it twice as separate invocations (byte-identical), confirmed results_sha256 matches the proposal's disclosed full-64 digest, and captured stdout in run-stdout.txt.

## ⟲ Previous-session review
Mirrors the VERDICT 246 (secretary optimal-stopping) reproduction pattern — same born-red + digest-match + defer-ruling contract.

## 💡 Session idea
If the coordinator VERDICT 247 slice wants a stronger falsification, add a second naive alternative (parity with the WRONG discount horizon R⁻¹ instead of R⁻ⁿ) as a fifth-direction check.

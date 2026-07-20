# VERDICT 248 reproduction — value of a 2×2 zero-sum game is v = (a·d − b·c)/(a + d − b − c) (von Neumann minimax); reproduction-only, canonical ruling deferred

> **Status:** complete

📊 Model: Opus · high · verdict-reproduction
started: 2026-07-20T23:40:00Z

💓 Heartbeat:
- round/slot: sim-lab mirror · P235 → V248 (+13 offset)
- branch: claude/proposal-235-zerosum-value-mirror
- sim dir: sims/verdict-248-zerosum-2x2-value/
- verifier: byte-identical copy of idea-engine ideas/fleet/verify_235_zerosum_2x2_value.py
- SEED: 20260717 · results_sha256: a8d766a845b4cd53518fc572f30041dfb154148a67f399c39463476ec1e4276a
- determinism: in-process double-run IDENTICAL · separate re-invocation byte-identical
- G1 exact value identity (Fraction, 4-game no-saddle panel + saddle cross-check) · pass
- G2 MC agreement 400000 trials, z=0.345941, |z|<3 · pass
- G3 invariance (minimax guarantee + affine) · pass
- G4 falsifiability naive "value == pure security level = −1" z_naive=462.564053, |z|≥6 · pass
- all_pass: true · first_failing_gate: null · decision: sim-ready
- ruling: DEFERRED to coordinator VERDICT 248 slice (mirror does not advance verdict high-water)

⏳ Flip note (born-red): commits FIRST as in-progress to hold the PR red behind substrate-gate; flips to complete as the LAST commit after the sim dir, digest match, and four-gate eval land, releasing merge-on-green.

## What this verdict does
Reproduces idea-engine PROPOSAL 235 byte-for-byte in sim-lab and records the run. Reproduction-only: the canonical APPROVE/QUALIFIED/REJECT ruling and the verdict high-water belong to the coordinator-driven VERDICT 248 slice.

## Method
Copied the firsthand verifier verbatim, ran it twice as separate invocations (byte-identical), confirmed results_sha256 matches the proposal's disclosed full-64 digest, and captured stdout in run-stdout.txt.

## ⟲ Previous-session review
Mirrors the VERDICT 247 (put-call parity) reproduction pattern — same born-red + digest-match + defer-ruling contract.

## 💡 Session idea
If the coordinator VERDICT 248 slice wants a stronger falsification, add a second naive alternative (value == row-average of the reference matrix, or value == pure minimax = +1) as a fifth-direction check.

# Reproduction mirror — PROPOSAL 230 / VERDICT 243 (bilateral double auction)

> **Status:** `reproduction` — byte-identical verifier reproduced green. The canonical independent APPROVE/QUALIFIED/REJECT ruling is a separate coordinator-driven VERDICT 243 slice; this PR lands only the reproduction material and does not advance the verdict high-water.

## Source
idea-engine PROPOSAL 230 — ideas/venture-lab/bilateral-double-auction.py (branch claude/proposal-230-bilateral-double-auction). Byte-identical copy here: sims/verdict-243-bilateral-double-auction/bilateral-double-auction.py.

## Reproduced firsthand
- SEED=20260717, stdlib-only, Python 3.11.15.
- results_sha256 = 5052053d3a6cb6fb1419afe0846f4f339d3537057d6ee5fbeb8a86e9b9ea42c3 (full 64 hex), byte-identical across in-process double-run + separate re-invocation (see run-stdout.txt).
- G1 EXACT (Fraction): delta=1/4, realized=9/64, first_best=1/6, efficiency=27/32, deadweight=5/192, trade_prob=9/32.
- G2 MC N=200000: z_gains=−0.123561 (p̂=0.140558) vs 9/64; z_trade=−0.258615 (p̂=0.28099) vs 9/32; both |z|<3.
- G3: buyer & seller grid best-response argmax == closed-form b*(v)/s*(c) at all four probes; second exact route via difference density f_D(d)=1−d reproduces 9/64.
- G4: efficient rule agrees with 1/6 (z=−0.308089); equilibrium realized gains reject the naive-efficient 1/6 at z=−47.919492 (>6).

## Grounding (from the proposal, recorded for the ruling slice)
Wikipedia "Double auction" oldid 1346190881 sha1 ffbd1f23d644439cf57dfe7be48fc39990d9b68a. Quoted on the pinned revision: linear-strategy Bayesian Nash equilibrium existence under a uniform prior + the Myerson–Satterthwaite impossibility (IR/BB/IC/efficient, incl. the k=1 corollary). Derived firsthand: the 2/3, 1/12, 1/4 coefficients, the v−c≥1/4 threshold, 9/64, 1/6, 27/32, 5/192, the explicit Uniform[0,1] support, and the Chatterjee–Samuelson attribution.

## Deferred
The independent adversarial ruling (re-grounding quoted-vs-derived firsthand, re-evaluating each gate in its own direction, and the APPROVE/QUALIFIED/REJECT verdict) is the dedicated VERDICT 243 slice's deliverable.

# Session — VERDICT 243 reproduction mirror (bilateral double auction, from PROPOSAL 230)

> **Status:** `complete`
> Born-red HOLD (released): landed `in-progress` on the first commit to hold the PR red through substrate-gate, flipped to `complete` as the last commit once the byte-identical verifier, run-stdout, and repro-report were in place and verified. Merge-on-green lands it (ORDER 003, zero agent merge calls).

## 💡 Session idea

Reproduction mirror of idea-engine PROPOSAL 230 (round-54 offset +13): the Chatterjee–Samuelson k=1/2 bilateral double auction as a concrete Myerson–Satterthwaite signature. Buyer value v and seller cost c are independent Uniform[0,1]; the unique linear Bayes–Nash equilibrium is buyer bid b(v)=2v/3+1/12 and seller ask s(c)=2c/3+1/4; trade occurs iff v−c≥1/4. Expected realized gains from trade are exactly 9/64 versus first-best 1/6, so efficiency is exactly 27/32 and deadweight exactly 5/192. This PR lands ONLY the reproduction material (byte-identical verifier + firsthand run evidence + repro-report) under `sims/verdict-243-bilateral-double-auction/`; the canonical independent APPROVE/QUALIFIED/REJECT ruling is a separate coordinator-driven VERDICT 243 slice, and the verdict high-water is intentionally NOT advanced here.

## ⟲ Previous-session review

VERDICT 241 (random-walk no-return, PROPOSAL 228) verifier landed (#325). Round-54 rotation continues; this is a reproduction mirror of PROPOSAL 230, paired with idea-engine branch `claude/proposal-230-bilateral-double-auction`.

## 🫀 Heartbeat

`bilateral-double-auction.py` reproduced green byte-identical to idea-engine PROPOSAL 230 (IDEA_ENGINE_DIFF=0 against branch claude/proposal-230-bilateral-double-auction, path ideas/venture-lab/bilateral-double-auction.py, and SCRATCH_DIFF=0 against source): exit 0, SEED=20260717, Python 3.11.15, digest `5052053d3a6cb6fb1419afe0846f4f339d3537057d6ee5fbeb8a86e9b9ea42c3` (full 64 hex) byte-identical across in-process double-run and separate re-invocation (RERUN_DIFF=0). All four gates PASS each in its own direction: G1 EXACT (Fraction) delta=1/4, realized=9/64, first_best=1/6, efficiency=27/32, deadweight=5/192, trade_prob=9/32; G2 MC N=200000 z_gains=−0.123561 / z_trade=−0.258615 (both |z|<3); G3 buyer/seller grid best-response argmax == closed-form b*(v)/s*(c) at all four probes + second exact route via f_D(d)=1−d reproduces 9/64; G4 efficient rule agrees with 1/6 (z=−0.308089) while the equilibrium rejects the naive-efficient 1/6 at z=−47.919492 (>6). run-stdout.txt captures the full results dict + digest.

> 📊 Model: Claude Opus · high · reproduction-mirror

## Decisions made

- Reproduction-only: this PR lands the byte-identical verifier + firsthand run-stdout + repro-report under sims/verdict-243-bilateral-double-auction/ and nothing else. No APPROVE/QUALIFIED/REJECT ruling block was written.
- The canonical independent VERDICT 243 ruling is deferred to a dedicated coordinator-driven slice; the verdict high-water is intentionally NOT advanced.
- control/status.md was not touched. Merge-on-green lands this green claude/* PR (zero agent merge calls).

## Next session should know

- The canonical VERDICT 243 ruling (re-grounding quoted-vs-derived firsthand, re-evaluating each gate in its own direction, and the adversarial verdict) is a dedicated VERDICT 243 slice's deliverable, paired with idea-engine PROPOSAL 230.

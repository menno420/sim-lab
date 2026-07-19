# VERDICT 198 — bufferbloat standing queue (reproduce PROPOSAL 185)

PROPOSAL 185 claims that on a saturated FCFS server (offered load ρ = λ/μ > 1) the finite buffer K sits essentially full, so mean sojourn W ≈ (K − ρ/(ρ−1))/μ grows ~linearly in K while goodput stays pinned at the service rate μ. A bigger buffer buys a permanent standing queue — pure latency, zero throughput. This is bufferbloat. This verdict reproduces that mechanism byte-identically from the disclosed verifier.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · task-class simulation-reproduction
> **Result:** born-red HOLD — flips to `complete` on the last commit, after the verifier copy, run stdout, and probe report are committed and the control/status.md heartbeat is written.

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red. It flips to `complete` on the last commit, after the verifier copy, run stdout, and probe report are committed and the control/status.md heartbeat is written.

## Objective

Reproduce PROPOSAL 185 byte-identically in sim-lab: copy the disclosed verifier `ideas/fleet/bufferbloat_standing_queue.py` (idea-engine @0772612) into `sims/verdict-198-bufferbloat-standing-queue/`, run it under SEED=20260717, confirm determinism (in-process double-run plus a separate cross-invocation, byte-identical stdout), and compare the results-dict sha256 to the disclosed digest `d968600582b39bde30bbbead4b192a0d08c4d1bcb64c3b5c1a17f40924139142` across all 64 hex characters.

## GROUNDING (verified at HEAD)

The mechanism rests on the standing-queue law of a saturated FCFS buffer: under sustained overload (ρ = λ/μ > 1) the finite queue sits essentially full, so by Little's law mean sojourn W ≈ (K − ρ/(ρ−1))/μ is affine in K at slope 1/μ while the departure rate (goodput) saturates at μ regardless of K. This is confirmed live at the Wikipedia "Bufferbloat" article (revid 1354864082), which states verbatim: "In a first-in first-out queuing system, overly large buffers result in longer queues and higher latency, and do not improve network throughput." The Gettys & Nichols "Dark Buffers" framing is CITED-on-page; the gated claim — a bigger buffer under saturation buys more latency and the same goodput — IS live-supported.

## Constraints honored

- stdlib only (sys, math, json, hashlib, random, collections); Python 3.
- SEED = 20260717, Z_GATE = 3.0, TRIALS = 40, N_ARR = 20000, WARM = 4000, MU = 1.0, R_BASE = 1.25, R_SHIFT = 1.5, K_SMALL = 25, K_LARGE = 75, EPS = 0.02.
- Verifier copied byte-identically from idea-engine @0772612 (diff exit 0).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest; no on-disk JSON.

## Gate plan (to reproduce at HEAD), order G1 → G2 → G3

- **G1 — latency scales with buffer size:** paired ΔW = W(K_LARGE) − W(K_SMALL) > 0 at ≥ 3σ. Expect ΔW ≈ 49.954161, z ≈ +508.99; W(K_SMALL) ≈ 21.09712, W(K_LARGE) ≈ 71.05128, ratio ≈ 3.367819.
- **G2 — no goodput dividend:** |thr(K_SMALL) − thr(K_LARGE)| ≤ EPS·μ AND both ≥ (1−EPS)·μ. Expect thr(K_SMALL) ≈ 0.999952, thr(K_LARGE) ≈ 0.999687, gap ≈ 0.000265.
- **G3 — robust under a shifted load (ρ = 1.5):** ΔW > 0 at ≥ 3σ (expect ΔW ≈ 50.033018, z ≈ +581.38) AND the no-dividend bound holds (thr 1.000961 vs 1.000406, gap ≈ 0.000555).
- all_pass required; Z_GATE = 3.0.

## Probe questions

1. Does the results-dict sha256 from the in-branch run match the disclosed `d968600582…` digest across all 64 hex characters?
2. Is the copied verifier byte-identical to the idea-engine source (diff exit 0)?
3. Do the in-process double-run and a separate cross-invocation produce byte-identical stdout?
4. Does the live "Bufferbloat" source support the standing-queue law (bigger FIFO buffer → more latency, no throughput) that the gates test?

## Outcome

Reproduction pending — born-red HOLD. This section is filled at the flip commit, after the verifier is copied, the run stdout and probe report are committed, and the results-dict sha256 is compared to the disclosed digest across all 64 hex characters.

## ⟲ Previous-session review

Previous-session review: V197 (de Moivre small-sample variance, PROPOSAL 184) landed with digest MATCH and all gates PASS; the ruled verdict high-water is carried in the idea-engine outbox, not in sim-lab. This card follows the same born-red HOLD flow and leaves sim-lab's verdict high-water reference unchanged — V198 is ruled via the idea-engine outbox mirror.

## 💡 Session idea

The verifier holds K_SMALL/K_LARGE fixed at 25/75. A cheap extension: sweep K over {25, 50, 75, 100} at fixed ρ and regress mean W on K — the standing-queue law predicts a straight line of slope ≈ 1/μ through the origin-offset −ρ/(ρ−1)/μ, so the R² of that linear fit is a second, orthogonal confirmation of the affine-in-K claim beyond the single paired ΔW.

**Recommendation: pending reproduction (born-red HOLD).**

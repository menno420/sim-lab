# VERDICT 197 — de Moivre small-sample variance (reproduce PROPOSAL 184)

PROPOSAL 184 claims that when many units share one true success rate p but differ in sample size n, the standard deviation of each unit's observed rate is √(p(1−p)/n), so it shrinks as 1/√n. A naive leaderboard ranked by observed rate therefore surfaces the smallest-n units at BOTH the top and the bottom of the board — a sample-size illusion (de Moivre's equation, Wainer's "most dangerous equation"), not a quality signal. This verdict reproduces that mechanism byte-identically from the disclosed verifier.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · task-class simulation-reproduction
> **Result:** pending reproduction — filled at the flip commit.

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red. It flips to `complete` on the last commit, after the verifier copy, run stdout, and probe report are committed and the control/status.md heartbeat is written.

## Objective

Reproduce PROPOSAL 184 byte-identically in sim-lab: copy the disclosed verifier `ideas/fleet/demoivre_small_sample_variance.py` (idea-engine @ec4706b) into `sims/verdict-197-demoivre-small-sample/`, run it under SEED=20260717, confirm determinism (in-process double-run plus a separate cross-invocation, byte-identical stdout), and compare the results-dict sha256 to the disclosed digest `8b9506d1182b6c5f3121ff8b585dfb7032d47a337013e30d4f7fbfc1e0968871` across all 64 hex characters.

## GROUNDING (verified at HEAD)

The mechanism rests on the standard error of a proportion: SE = σ/√n, i.e. SD(observed rate) = √(p(1−p)/n), which shrinks as 1/√n. This is confirmed live at the Wikipedia "Standard error" article (oldid 1362665393), which the proposer pinned because there is no standalone "The Most Dangerous Equation" article and Wainer 2007 was not fetchable in-env. The de Moivre / Wainer framing is CITED-not-fetched and flagged as such in the proposal; the gated claim — the σ/√n scaling law that gate G1 tests — IS live-supported.

## Constraints honored

- stdlib only (sys, math, json, hashlib, random); Python 3.
- SEED = 20260717, Z_GATE = 3.0, TRIALS = 100, M = 800 units.
- Verifier copied byte-identically from idea-engine @ec4706b (diff exit 0).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest; no on-disk JSON.

## Gate plan (to reproduce at HEAD), order G1 → G2 → G3

- **G1 — scaling law:** Pearson corr(|r̂ − p|, 1/√n) > 0. Expect r ≈ 0.570449, z ≈ +238.77.
- **G2 — extremes small-n:** pop_mean_n − extremes_mean_n > 0. Expect ≈ 147.021788, z ≈ +213.05.
- **G3a — robust (shifted p = 0.1):** corr > 0. Expect ≈ 0.570124, z ≈ +219.52.
- **G3b — robust (shifted n-range [25,250]):** delta > 0. Expect ≈ 38.443275, z ≈ +129.56.
- all_pass required; Z_GATE = 3.0.

## Probe questions

1. Does the results-dict sha256 from the in-branch run match the disclosed `8b9506d1…` digest across all 64 hex characters?
2. Is the copied verifier byte-identical to the idea-engine source (diff exit 0)?
3. Do the in-process double-run and a separate cross-invocation produce byte-identical stdout?
4. Does the live "Standard error" source support the σ/√n law that gate G1 tests?

## Outcome

Pending reproduction — filled at the flip commit.

## ⟲ Previous-session review

Previous-session review: V196 (kingmaker skill-inversion, PROPOSAL 183) landed via sim-lab PR #271 @d52f095 with digest MATCH and all gates PASS; the ruled verdict high-water is carried in the idea-engine outbox, not in sim-lab. This card follows the same born-red HOLD flow and leaves sim-lab's verdict high-water reference unchanged — V197 is ruled via the idea-engine outbox mirror.

## 💡 Session idea

The verifier hard-codes P = 0.5, where p(1−p) is maximal. A cheap extension: sweep p across {0.1, 0.3, 0.5} and report whether the corr(|r̂ − p|, 1/√n) gate strengthens or weakens with p — it should scale with √(p(1−p)), giving a second, orthogonal confirmation of de Moivre's law beyond the single-p run.

**Recommendation: APPROVE — pending in-branch confirmation of the digest match and the σ/√n grounding; flips to complete once reproduction holds.**

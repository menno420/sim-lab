# VERDICT 166 — Kleinrock's conservation law holds under work-conserving priority scheduling: the load-weighted mean wait is invariant across FIFO, priority-short, and priority-long, so scheduling only redistributes delay (a zero-sum transfer) rather than reducing it

Reproduce PROPOSAL 153 (round-36 FLEET slot, P153 → V166, +13): clean-room re-run of the disclosed verifier `ideas/fleet/kleinrock_conservation_zero_sum.py` under SEED=20260717, confirm the byte-identical results-dict sha256 `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18`, and evaluate gates G1 (transfer real) → G2 (conservation leak under the 0.10 ceiling) → G3 (shifted-mix robustness) in order.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · high · review/verify

Born red by design: this card lands `in-progress` in the FIRST commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the deliberate LAST commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (born-red discipline). No gate is bypassed.

## Objective
Independently reproduce PROPOSAL 153's claim — that in a work-conserving single-server queue the load-weighted mean wait is conserved across scheduling disciplines, so priority scheduling transfers delay from short to long jobs zero-sum rather than eliminating it — by re-running the disclosed verifier clean-room and checking the disclosed digest and all three gates.

## GROUNDING (verified at HEAD)
- Reference verifier: `ideas/fleet/kleinrock_conservation_zero_sum.py` at idea-engine main 96e048c — file sha256 `72f740652714e76c4e9c83ed9844d66fa6dc8a41370d66e73f9a6a1e462faafb`, git blob `a9280c5519b1cca8308dc5652d5398028e495dfb`. Grounding: https://github.com/menno420/idea-engine/blob/96e048c/ideas/fleet/kleinrock_conservation_zero_sum.py@96e048c · fetched 2026-07-19T04:16:13Z
- Offset authority: PROPOSAL/VERDICT offset +13 (P153 → V166) per idea-engine control/outbox.md.
- Disclosed results-dict sha256: `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18`.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the verifier computes the digest at runtime and prints it to stdout; no JSON is written to disk.
- Pinned world: SEED=20260717, S1=1.0 S2=8.0 P(short)=0.8 RHO=0.85 N_JOBS=20000 WARMUP=4000 R_REPS=30; shifted world P(short)=0.6 S2=6.0 RHO=0.80.
- Work-branch non-contiguity: authored on claude/verdict-166-kleinrock-conservation; verdicts below the high-water may remain open.

## Constraints honored
- Byte-identical verifier copy (no edits); `diff` against the reference exits 0.
- Stdlib-only; SEED pinned; no network access.
- STDOUT-ONLY digest posture preserved; no JSON written to disk.
- Verdict decided strictly on reproduction output: APPROVE iff G1 and G2 and G3, else REJECT naming the first failing gate.

## Gate plan (disclosed → to reproduce), order G1 → G2 → G3
- G1 transfer_short_mean = +7.450148, z = +30.100904 vs 0 → transfer is real.
- G2 leak_mean = 0.040689, z = +12.680569, ceiling 0.10 → conservation holds.
- G3 shift_leak_mean = 0.023037, z = +23.740077 → robust under the shifted mix.
- all_pass = true, first_failing_gate = null.

## Probe questions (independent-audit checklist)
**1.** Does the copied verifier byte-match the idea-engine reference (file sha256 `72f7406…faafb`, blob `a9280c5…`, `diff` exit 0)?
**2.** Under SEED=20260717, does the in-process double-run assert identical, and does a separate cross-invocation reproduce byte-identical stdout?
**3.** Does the computed results-dict sha256 equal the disclosed `1b40af51…3153ee18`?
**4.** G1: is transfer_short_mean > 0 at z ≥ 3 (observed +7.450148, z +30.100904)?
**5.** G2: is leak_mean < 0.10 at z ≥ 3 below the ceiling (observed 0.040689, z +12.680569)?
**6.** G3: under the shifted mix, is leak < 0.10 at z ≥ 3 (observed 0.023037, z +23.740077), and does the conserved load-weighted wait hold near 28.18 across FIFO / priority-short / priority-long (spread ~0.08%)?

## Outcome — pending (fills at flip)
Reproduction and audit run after this born-red commit; the last commit records the verdict and flips Status to `complete`.

## ⟲ Previous-session review
Chains back to VERDICT 165 (Braess paradox). Confirmed on this branch: prior verdict cards land with the born-red HOLD and flip to `complete` on the last commit; this card follows the same discipline.

## 💡 Session idea
A shared assertion-helper that both the reference and the copied verifier import for the double-run/cross-invocation byte-match check would cut per-verdict boilerplate; noted for a future proposal, not acted on here.

# VERDICT 173 — Cauchy no-averaging: for i.i.d. draws from a Cauchy(x0, γ) distribution (a bell-shaped but heavy-tailed law with NO finite mean and NO finite variance), the sample mean of n draws is itself distributed EXACTLY as Cauchy(x0, γ) — identical to a single draw — so averaging does NOT concentrate the estimate, the standard error does NOT fall as 1/√n, and the Law of Large Numbers FAILS — the folk "average more samples and the estimate always tightens; the error shrinks like 1/√n, so just take more measurements" belief is FALSE for heavy-tailed (undefined-mean) data — the sample mean of a Cauchy sample has the SAME dispersion as one observation no matter how large n grows, because the heavy tails guarantee occasional extreme draws that dominate the average, so the √n error-reduction intuition is a property of finite-variance laws (where the CLT and LLN hold), not a universal law; the read is a no-concentration SIGN claim — averaging buys nothing for Cauchy data — but the exact result (mean-of-n ≡ single draw in distribution) is a property of the Cauchy (stable, α=1) law, and a finite-variance law recovers the usual 1/√n concentration, so where the concentration sits is a disclosed model-dependent field

Reproduce PROPOSAL 160 (P160 → V173, +13): Cauchy no-averaging / failure of the Law of Large Numbers. Under the pinned world each of TRIALS batches draws n i.i.d. Cauchy(x0, γ) samples, forms the empirical sample mean, and the dispersion of the sample mean is measured empirically across batches (not plugged from the closed form) and compared against the dispersion of a single draw and against the 1/√n concentration a finite-variance law would predict. The folk belief: "averaging always tightens — take more samples and the standard error shrinks like 1/√n." It is NOT: for Cauchy data the sample mean is itself Cauchy(x0, γ), so its dispersion does NOT shrink with n and the LLN/CLT √n-concentration fails. Model-basis caveat (P024 discipline): the head is EXACT GIVEN THE MODEL (i.i.d. Cauchy → stable-law sample mean identically distributed to one draw) — the SIGN (no concentration; averaging buys nothing) survives, but the exact no-shrink result is a property of the Cauchy (α=1 stable) law; a finite-variance law recovers 1/√n concentration, and that model-dependence is a disclosed descriptive field, not a hidden defect.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · high · review/verify

Born red by design: this card lands `in-progress` in the FIRST commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the deliberate LAST commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (CONVENTIONS born-red discipline). No gate is bypassed. This born-red HOLD is the ONLY reason the gate reads red pre-flip; a red gate AFTER the flip is a real defect, not the HOLD.

## Objective
Reproduce the committed P160 reference verifier byte-identical under its pinned world (SEED, TRIALS batches → between-batch dispersion measured empirically rather than plugged from the closed form, every float rounded to 6 dp before serialization) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest, (b) all gates hold in order, (c) the run is deterministic across a fresh cross-invocation double-run AND the script's own in-process double-run digest assert (byte-identical stdout, exit 0), (d) the headline reproduces (the Cauchy sample mean does NOT concentrate — its dispersion is that of a single draw, and the 1/√n error-reduction fails). Pre-registered decision rule (P160): APPROVE VERDICT 173 iff byte-identical + digest exact + all gates pass in order across a deterministic double-run + exit 0, else REJECT naming first_failing_gate. Target: sim-lab (VERDICT 173, +13 — PRIMARY); idea-engine mirror separate.

_Details to be filled at the flip commit — this card is born red to hold the PR._

## GROUNDING (verified at HEAD)
- Reference verifier: P160 source @ idea-engine — identity (sha256 / git blob) to be pinned in the reproduction commit.
- Offset authority: +13 (P160 → V173). Per idea-engine `control/outbox.md` P160 block + `control/status.md` — to confirm at HEAD.
- Domain reference: the Cauchy distribution's failure of the Law of Large Numbers — the sample mean of n i.i.d. Cauchy(x0, γ) draws is itself Cauchy(x0, γ) (a textbook property of the α=1 stable law), so averaging does not reduce dispersion.
- Disclosed digest: compact-canonical results-dict sha256 — to be reproduced EXACTLY in the reproduction commit.
- DIGEST POSTURE (expected): **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** per the proposal doc's disclosed posture (carried forward from V171/V172) — to confirm byte-exact.

## Constraints honored
Stdlib-only; verifier to be copied byte-identical (`diff` exit 0, sha256 match) in the reproduction commit; pinned SEED and world constants unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed; zero agent merge calls (merge-on-green lands claude/* on the green head SHA).

## Gate plan (to reproduce)
_To be filled at the flip commit._

## Probe questions (independent-audit checklist)
_To be filled at the flip commit._

## Outcome
_Pending — reproduction in progress. This card is born red; the outcome and verdict are recorded only at the deliberate flip commit._

## ⟲ Previous-session review
Prior card `2026-07-19-verdict-172-drop-rate-median-gap.md` (V172, P159 drop-rate median gap / geometric skew, round-37 GAME slot, +13) landed a CLEAN APPROVE and advances the verdict high-water to **V172**. CONTIGUITY: V172 → V173 are contiguous (union-max advances the high-water to **V173** on the flip). Items open/backfilled below the high-water are NOT closed by landing V173. DIGEST-POSTURE carry-forward expected unbroken (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY).

## 💡 Session idea
_To be filled at the flip commit._

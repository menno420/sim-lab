# VERDICT 193 — typical-set "mode mirage" (reproduce PROPOSAL 180)

Reproduces PROPOSAL 180's head that for n i.i.d. Bernoulli(p) symbols with p ≠ ½, the single most-probable sequence — the all-majority-symbol mode — is essentially never observed, while observed sequences concentrate at Shannon entropy H(p) and are each astronomically less probable than the never-seen mode. Flip a biased coin (p=0.7) 1000 times: all-heads is the most-probable single outcome yet you never see it; you see a ~700-heads sequence at per-symbol surprisal ≈ H(0.7)=0.881 bits, strictly above the mode's 0.515 bits. Probability concentrates away from the probability maximum — the Asymptotic Equipartition Property (AEP) typical set.

> **Status:** `complete`
> 📊 Model: Claude · effort high · verdict reproduction
> **Reproduction landed — APPROVE. Verifier byte-identical (sha256 2af59b2b…, git-blob e7be486f…), results-dict digest 1479479100… MATCH, G1/G2/G3 all reproduce, all_pass=true, both mode counts 0.**

## Objective

Byte-identically reproduce the idea-engine verifier `typical-set-mode-mirage-2026-07-19.py` under SEED=20260717, confirm the disclosed results-dict sha256 `1479479100edba6509b0275d31717a2f44b4504d6051023feffc5f13395b8c36`, and rule G1 → G2 → G3 against PROPOSAL 180's own criteria.

## GROUNDING (verified at HEAD)

GROUNDING: https://en.wikipedia.org/wiki/Asymptotic_equipartition_property@78b633eddfc34ed73d8a1a7250cc1ceb38bc1d52 — resolved live, HTTP 200. Documents the Asymptotic Equipartition Property and the typical set of ≈2^{nH} sequences each of probability ≈2^{−nH} carrying ≈all the probability mass — the mechanism this head decomposes into typical-set-vs-mode.

## Constraints honored

- stdlib-only (`random, math, json, hashlib, sys`); SEED=20260717 pinned in source; z_gate=3.0.
- Verifier copied byte-identically from idea-engine (diff exit 0; sha256 2af59b2b67bbaf0a9cdd30dbc2109346f1296027ab50b0229bf2b7f2bd804a60, git-blob e7be486f260944e9d1b03f77ed2c07cd309c1cbe).
- WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest posture: sha256 of the compact-canonical `json.dumps(sort_keys=True, separators=(',',':'))`, floats 6 dp; no on-disk JSON.
- In-process double-run asserted equal; separate cross-invocation stdout byte-matched.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- **G1 — typical concentration:** |mean ĥ − H(p)| ≤ 0.10 bits AND in-band fraction ≥ 0.99. Measured base_mean_hrate 0.881064 vs H(0.7) 0.881291 (|Δ| 0.000227), in-band 1.0 → PASS.
- **G2 — mode is a mirage (≥3σ):** z_sep = (mean ĥ − s)/se ≥ 3.0 AND the exact modal sequence occurs 0 times. Measured z_separation 1308.854386, base_mode_count 0 of 4000 → PASS.
- **G3 — robustness under a shifted distribution (p=0.9, ≥3σ):** |mean ĥ − H| ≤ 0.10 AND in-band ≥ 0.99 AND z_sep ≥ 3.0 AND modal count 0. Measured shift_mean_hrate 0.468904 vs H(0.9) 0.468996, in-band 0.999, z_separation 671.930225, shift_mode_count 0 → PASS.
- all_pass = true.

## Probe questions (independent-audit checklist)

**1.** Does the sim-lab verifier copy diff byte-identically against the idea-engine source (sha256 2af59b2b…, git-blob e7be486f…)?
**2.** Under SEED=20260717, does the in-process double-run assert equal and do two cross-invocation runs print byte-identical stdout?
**3.** Does the compact-canonical results-dict sha256 equal the disclosed 1479479100edba6509b0275d31717a2f44b4504d6051023feffc5f13395b8c36?
**4.** At p=0.7, does mean ĥ (0.881064) land within 0.10 bits of H(0.7)=0.881291 with in-band fraction 1.0 (G1)?
**5.** Is the exact modal (all-heads / all-majority) sequence observed 0 times in 4000 draws at both p=0.7 and p=0.9?
**6.** Is z_sep ≥ 3σ at both p — 1308.854386 at p=0.7 and 671.930225 at p=0.9 (G2, G3)?
**7.** Under the p=0.9 shift, does concentration hold (mean ĥ 0.468904 vs H 0.468996, in-band 0.999) with the mirage preserved (G3)?
**8.** Does the grounding URL (Wikipedia AEP) resolve live and document the typical set carrying ≈all the mass while the mode is a single never-observed point?

## Outcome

APPROVE. The idea-engine verifier copied byte-identically (diff exit 0; sha256 2af59b2b67bbaf0a9cdd30dbc2109346f1296027ab50b0229bf2b7f2bd804a60, git-blob e7be486f260944e9d1b03f77ed2c07cd309c1cbe) and reproduced deterministically (in-process double-run asserted equal; separate cross-invocation stdout byte-identical, exit 0). Results-dict sha256 `1479479100edba6509b0275d31717a2f44b4504d6051023feffc5f13395b8c36` MATCHES the disclosed digest (all 64 hex). All three gates reproduce on the proposal's own criteria, all_pass=true:

- G1 (typical concentration): base_mean_hrate 0.881064 vs H(0.7) 0.881291 (|Δ| 0.000227 ≤ 0.10), in-band 1.0 ≥ 0.99 — PASS.
- G2 (mode mirage): z_separation 1308.854386 ≥ 3.0, base_mode_count 0 of 4000 — PASS.
- G3 (robustness, p=0.9): shift_mean_hrate 0.468904 vs H(0.9) 0.468996 (|Δ| 0.000092 ≤ 0.10), in-band 0.999 ≥ 0.99, z_separation 671.930225 ≥ 3.0, shift_mode_count 0 — PASS.

The head reproduces: the observed per-symbol surprisal (0.881064 bits) sits 1308.85σ above the mode's (0.514573 bits) with the mode observed 0 times; the typical band captures 100% of draws, and the mirage survives the p=0.9 shift (671.93σ separation, mode observed 0 times, in-band 99.9%). The mode (all-majority sequence) has probability p^n but there is only ONE such sequence, while the typical set has ~2^{nH(p)} sequences each of probability ~2^{−nH(p)}, so observations land in the typical set at entropy H(p) and never on the higher-per-sequence-probability mode — the AEP mode mirage.

## ⟲ Previous-session review

V192 (Buchholz Swiss-tiebreak luck amplifier, PR #266) landed APPROVE on a clean digest match with the lean 3-file sims/verdict-NNN layout (verifier copy + run-stdout.txt + probe-report.md). This card follows the same shape.

## 💡 Session idea

A finite-n boundary companion: quantify how the typical-band in-band fraction and the mode-separation z decay as n shrinks (n=1000 → 100 → 10), locating the sequence length at which the mode mirage stops holding and the maximum-probability outcome becomes observable — the finite-n edge of the AEP.

**Recommendation: APPROVE — reproduction is byte-identical, the digest matches EXACT, all three gates hold on the proposal's own criteria, and the never-observed mode vs typical-set concentration reproduces exactly.**

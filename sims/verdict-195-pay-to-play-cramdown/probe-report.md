# Probe report — VERDICT 195 (PROPOSAL 182 pay-to-play cramdown cliff)

State: reproduced — APPROVE

## Reproduction

- Verifier copied byte-identically from idea-engine `ideas/venture-lab/pay_to_play_cramdown_cliff.py` (diff exit 0).
- File sha256 `eab29688c582e1bb048bd75d6a0982683219692fbe619cd3cb8fbc708b3a0f7b`; git blob `c4214e36426b2c9fb6e7030abdb26af8bd8c1eac`.
- SEED=20260717, TRIALS=200000, stdlib only.
- In-process double-run asserted equal; separate cross-invocation byte-match (crossdiff exit 0).
- Emitted results-dict sha256 `ed8a081bb104683d1ee8c0c2ec9b90e2a1212100495d9d4b5e484016a75b243` MATCHES the disclosed target.

## Gates (proposal's own criteria)

- G1 in-band marginal-dollar return mean 2.674407 >= 2.0 (z 308.093567) — PASS
- G2 conversion/dilution ratio 2.362501 >= 1.5 (conv_mean 2.348806 / dil_mean 0.994203, z 848.320658) — PASS
- G3 cold-market danger-band prob 0.601695 > base 0.42401 (z 112.415006), cold conv/dil 2.516596 — PASS
- all_pass = true

## Probe questions

**1. Is the copied verifier byte-identical to the proposal head?**
Yes — diff exit 0 against `ideas/venture-lab/pay_to_play_cramdown_cliff.py`; git blob c4214e3.

**2. Is the output deterministic across separate interpreter invocations?**
Yes — two independent runs at SEED=20260717 produced byte-identical stdout (crossdiff exit 0), and the in-process double-run asserts equality.

**3. Does the emitted results-dict digest match the disclosed sha256?**
Yes — emitted `ed8a081b…` equals the disclosed target.

**4. What actually drives the outsized marginal-dollar return, dilution or conversion?**
The conversion. G2 isolates the preferred-to-common conversion effect (conv_mean 2.35) from simple dilution (dil_mean 0.99); the ratio 2.36 shows the preference-wipe dominates, not pro-rata dilution.

**5. Does the effect sharpen in cold markets?**
Yes — G3: the danger-band probability rises from 0.424 (base) to 0.602 (cold), and cold conv/dil 2.52 exceeds the base ratio, at z 112.

**6. Is the mechanism faithful to real pay-to-play terms?**
Yes — the Fenwick grounding documents "All current preferred stock is converted to common stock at a 1:1 ratio," matching the verifier's 1:1 conversion / preference-wipe model.

**7. Does the grounding URL resolve live?**
Yes — resolves live; the 1:1 conversion language is present verbatim.

**8. Are the claimed z-scores reproduced, not merely asserted?**
Yes — G1 z 308.09, G2 z 848.32, G3 z 112.42 are all reproduced from the run at HEAD, matching the proposal's disclosed values.

## GROUNDING (verified at HEAD)

https://www.fenwick.com/insights/publications/what-is-a-pay-to-play-financing@8552d3db117ccbbb2c4dd7014b987834666bb971

Documents "All current preferred stock is converted to common stock at a 1:1 ratio."

**Recommendation: APPROVE — reproduces cleanly, digest matches, all three gates pass, grounding live.**

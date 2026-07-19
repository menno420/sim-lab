# VERDICT 194 — Bloom-filter optimal-k FPR floor (reproduce PROPOSAL 181)

Reproduces PROPOSAL 181's head that a Bloom filter's false-positive rate is convex (U-shaped) in the number of hash functions k, minimized at k* = (m/n)·ln2 — past the optimum each extra hash SETS another bit, saturates the array faster, and makes false positives WORSE, not better; and the achievable minimum is floored at φ = (½)^{(m/n)·ln2} ≈ 0.6185^{(m/n)}, set by bits-per-element ALONE so no choice of k crosses it. At 8 bits/element the FPR is 11.79% at k=1, bottoms at 2.22% at k*=6 (on the memory floor φ=2.14%), then climbs back to 4.93% at k=12. The lever a team chasing fewer false hits actually needs is bits-per-element (m/n), not more hashes.

> **Status:** `in-progress`
> 📊 Model: Opus · high · verdict-reproduction
> **Reproduction in progress — reproducing PROPOSAL 181 at SEED=20260717; disclosed results-dict digest 3fdfc867… to be confirmed, gates G1/G2/G3 to be ruled in order.**

## Objective

Byte-identically reproduce the idea-engine verifier `bloom-optimal-k-fpr-floor-2026-07-19.py` under SEED=20260717, confirm the disclosed results-dict sha256 `3fdfc867123a80a1476d414610413060c24b3580841f1d808dac10a75f8b5d7f`, and rule G1 → G2 → G3 against PROPOSAL 181's own criteria.

## GROUNDING (verified at HEAD)

GROUNDING: https://en.wikipedia.org/wiki/Bloom_filter@15d7f16cabd1b2e9f33543aa383f4aee8a81896b — to resolve live (HTTP 200) at reproduction. Documents the optimal k = (m/n)·ln2 minimizing FPR = (1 − e^{−kn/m})^k (Bloom 1970), and Kirsch–Mitzenmacher double hashing (h_i = g1 + i·g2) — the mechanism this head decomposes into the U-shaped FPR curve and its bits-per-element floor.

## Constraints honored

- stdlib-only (`hashlib, json, math`); SEED=20260717 pinned in source; Z_GATE=3.0, TOL=0.20.
- Verifier to be copied byte-identically from idea-engine (diff exit 0; sha256 + git-blob to be recorded).
- WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest posture: sha256 of the compact-canonical `json.dumps(sort_keys=True, separators=(',',':'))`, floats 6 dp; no on-disk JSON.
- In-process double-run asserted equal; separate cross-invocation stdout byte-matched.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- **G1 — optimum dominance (c=8):** both ends of the k-sweep beat the optimum — z of (FPR[k=1] − FPR[k*]) and z of (FPR[2k*] − FPR[k*]) both > 0 and both z ≥ 3. Expect FPR 11.79% at k=1 (z 118.376354) and 4.93% at k=12 (z 42.297910) both above the 2.22% optimum at k*=6 → PASS expected.
- **G2 — more hashes hurt (the head) + memory floor:** penalty = FPR[2k*] − FPR[k*] > 0 with z ≥ 3, AND the achieved optimum sits at the floor φ (|FPR[k*] − φ| ≤ 0.20·φ and no tested k beats φ by >20%). Expect penalty +2.71 points (z 42.297910), FPR[k*] 2.22% on floor φ=2.14% → PASS expected.
- **G3 — robustness under shifted config (c=12):** G1 dominance + past-optimum penalty persist with z ≥ 3, optimum again on its floor. Expect dominance z 129.804852 (k=1) and 18.148262 (k=16), penalty positive, FPR[k*] 0.33% on floor φ=0.31% → PASS expected.
- all_pass expected true.

## Probe questions (independent-audit checklist)

**1.** Does the sim-lab verifier copy diff byte-identically against the idea-engine source (sha256 + git-blob to be recorded)?
**2.** Under SEED=20260717, does the in-process double-run assert equal and do two cross-invocation runs print byte-identical stdout?
**3.** Does the compact-canonical results-dict sha256 equal the disclosed 3fdfc867123a80a1476d414610413060c24b3580841f1d808dac10a75f8b5d7f?
**4.** At c=8, do both k=1 (11.79%, z 118.4) and k=2k*=12 (4.93%, z 42.3) exceed the k*=6 optimum (2.22%) at ≥3σ (G1)?
**5.** Is the past-optimum penalty real — FPR[2k*] − FPR[k*] = +2.71 points at z 42.3 > 0 and ≥3σ (G2 head)?
**6.** Does the optimum sit on the bits-per-element floor (FPR[k*] 2.22% vs φ 2.14%, within TOL 20%) with no tested k beating φ (G2 floor)?
**7.** Under the c=12 shift, do dominance (z 129.8 / 18.1) and the penalty (z 18.1) persist with the optimum on φ(12)=0.31% (G3)?
**8.** Does the grounding URL (Wikipedia Bloom filter) resolve live and document k* = (m/n)·ln2 and FPR = (1 − e^{−kn/m})^k?

## Outcome

_Pending — reproduction in progress. Gates G1 → G2 → G3 to be ruled against PROPOSAL 181's own criteria; results-dict sha256 to be compared against the disclosed `3fdfc867123a80a1476d414610413060c24b3580841f1d808dac10a75f8b5d7f`; determinism to be confirmed via in-process double-run assert + separate cross-invocation byte-match at SEED=20260717._

## ⟲ Previous-session review

V193 (typical-set "mode mirage", PROPOSAL 180) landed APPROVE on a clean digest match (1479479100…) with the lean 3-file sims/verdict-NNN layout (verifier copy + run-stdout.txt + probe-report.md). This card follows the same shape. High-water taken as MAX = V193 pre-flip; V194 to advance it on a clean landing (union-max, no regress).

## 💡 Session idea

A counting-Bloom / cuckoo-filter companion head: quantify whether the same past-optimum U-curve and bits-per-element floor hold once deletions and fingerprint eviction enter the picture — the natural next FLEET-slot decomposition of probe-count vs fill on a shared substrate.

**Recommendation: PENDING — reproduction underway; APPROVE iff the verifier copies byte-identically, the disclosed digest matches, and G1/G2/G3 all hold on the proposal's own criteria at SEED=20260717.**

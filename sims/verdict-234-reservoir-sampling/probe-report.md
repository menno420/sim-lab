# PROPOSAL 221 → VERDICT 234 — Probe report (reservoir sampling, Algorithm R)

> A single streaming pass that never revisits an item and never knows the stream
> length n in advance nonetheless leaves EVERY one of the n items in the size-k
> reservoir with probability EXACTLY k/n — the same k/n whether the item arrived
> first, in the fill window, or dead last. Algorithm R (Waterman; Knuth TAOCP
> Vol.2; Vitter): fill the first k slots, then for each later item i draw
> j uniform in [1, i] and, iff j ≤ k, overwrite reservoir slot j.

- **Slice:** round-52, P221 → V234 (+13 offset), UNRELATED lane
- **Branch:** `claude/p221-reservoir-sampling`
- **Sim dir:** `sims/verdict-234-reservoir-sampling/`
- **Verifier:** `reservoir-sampling-uniform.py` (stdlib-only, SEED = 20260717)
- **Recommendation: sim-ready**

## Q1 — Is the verifier stdlib-only and single-seeded?

Yes. Imports are `hashlib`, `json`, `math`, `random`, `fractions.Fraction` —
all Python-3 stdlib, no third-party. `SEED = 20260717`; ALL randomness comes
from one `random.Random(SEED)` created in `run_battery()` and consumed in a
fixed, documented order: G2 draws `MC_TRIALS = 80000` Algorithm-R runs per config
(in `CONFIGS` order), then G3 draws the shuffled-order MC and the subset tally,
then G4 draws the buggy-model MC — back-to-back, no interleaving. No wall-clock,
no OS entropy, no `os.urandom`. Runtime ≈ 6.7 s for the full double-run (well
under the ~90 s budget).

## Q2 — Is the exact core computed as a LITERAL Fraction product (not hardcoded)?

Yes. `inclusion_prob_exact(i, n, k)` multiplies the survival product out term by
term in a loop over `fractions.Fraction` — it does NOT return the telescoped
`k/n`:

- item `i ≤ k`: `prob = 1`; then `for t in k+1..n: prob *= Fraction(t-1, t)`.
- item `i > k`: `prob = Fraction(k, i)`; then `for t in i+1..n: prob *= Fraction(t-1, t)`.

The literal product is then compared for exact equality against `Fraction(k, n)`.
No float appears in the exact gate; floats occur only in the Monte-Carlo
z-scores (G2/G3a/G4), which are agreement/rejection gates.

## Q3 — G1 (EXACT identity): does it PASS in its own direction?

PASS — direction is "any analytic inclusion probability ≠ k/n ⇒ FAIL." For BOTH
configs, for EVERY item i in 1..n, the literal Fraction product equals
`Fraction(k, n)` exactly:

| config (n,k) | items checked | target k/n | all items == k/n |
|--------------|---------------|-----------|------------------|
| (40, 8) | 40 | 1/5 | ✅ |
| (25, 5) | 25 | 1/5 | ✅ |

Sampled structurally-interesting positions confirm the flat profile: for (40,8)
items i = 1 (fill, first), 8 (fill, last), 9 (first replacement candidate), 40
(last item) all give the literal product **1/5**; likewise for (25,5) items
1, 5, 6, 25 all give **1/5**. A self-certifying identity — exact Fraction
equality, no slack — and it holds across the fill boundary (i ≤ k) and the
replacement regime (i > k) identically.

## Q4 — G2 (Monte-Carlo agreement): does it PASS in its own direction?

PASS — direction is max |z| < 3 (agreement; small z is the pass). Direction:
max |z| ≥ 3 over the probe set ⇒ FAIL. For each config the empirical inclusion
frequency of the probe items {1, k, k+1, n} over 80000 runs agrees with p = k/n
= 0.2, z = (freq − p)/√(p(1−p)/T):

| config | probes | per-probe z | max \|z\| | all < 3σ |
|--------|--------|-------------|-----------|----------|
| (40, 8) | {1, 8, 9, 40} | 0.397748, −0.760140, 0.220971, 0.265165 | **0.760140** | ✅ |
| (25, 5) | {1, 5, 6, 25} | 0.963433, 1.078338, 0.689429, 1.175565 | **1.175565** | ✅ |

Every probe |z| < 3 on the fixed seed; the empirical inclusion frequency tracks
k/n across the fill boundary, the first replacement slot, and the last item.

## Q5 — G3 (Robustness): order-independence AND subset-uniformity?

PASS — direction: dependence on stream order OR non-uniform k-subsets ⇒ FAIL.

**(a) Order-independence.** Shuffling the arrival order of the 40 item
identities (fixed seed) and re-measuring the SAME probe identities over 80000
runs on (40,8) leaves every probe within 3σ of k/n:

| probe identity | z | within 3σ |
|----------------|---|-----------|
| 1  | 1.122532 | ✅ |
| 8  | 0.919239 | ✅ |
| 9  | −1.210920 | ✅ |
| 40 | −2.306936 | ✅ |

max |z| = **2.306936** < 3 — inclusion rides on k/n regardless of the position
an identity happens to arrive at.

**(b) Subset-uniformity.** For SUBSET_CFG = (6,3) over 150000 runs, all
C(6,3) = **20** distinct reservoir 3-subsets appear, and their counts are uniform
by chi-square vs the expected 7500 each: **χ² = 15.0832 < 43.8** (df = 19,
~0.001 critical). min count 7399, max count 7636. Not just the per-item marginals
but the full joint distribution over k-subsets is uniform — Algorithm R draws
each k-subset with probability 1/C(n,k), the strong form of correctness.

Both legs hold ⇒ G3 PASS.

## Q6 — G4 (FALSIFIABILITY): is the wrong model rejected in its own direction?

PASS — direction: PASS iff the buggy model is REJECTED at max |z| ≥ 6. The
"unconditional-replace" BUG (for i > k pick j uniform in [1,k] and ALWAYS
replace reservoir[j−1], omitting the j ≤ i acceptance gate) deviates hugely from
k/n on UR_CFG = (40,8), 40000 runs:

| probe | buggy freq | z vs k/n | deviates (\|z\|≥6) |
|-------|-----------|----------|--------------------|
| 1  | 0.013450 | −93.275 | ✅ |
| 8  | 0.013150 | −93.425 | ✅ |
| 9  | 0.015350 | −92.325 | ✅ |
| 40 | 1.000000 | **400.000** | ✅ |

max |z| = **400.0** (the last item ALWAYS occupies a slot under the bug, so its
inclusion is 1.0 vs the true 0.2; early items survive only ≈ (7/8)³² ≈ 0.014 vs
0.2). k/n is correctly REJECTED for the buggy model — far past the |z| ≥ 6 floor.
A second, purely analytic "first-k" naive model (inclusion = 1 for i ≤ k, else 0)
is also rejected: it predicts 1/1 for items 1, 8 and 0/1 for items 9, 40, each
≠ the true 1/5. Both wrong models rejected ⇒ G4 PASS.

## Q7 — Determinism: do both legs hold?

Yes. **In-process double-run:** `__main__` builds the results dict twice and
prints `determinism_double_run=True` (compact-canonical JSON byte-identical
before exit 0). **Cross-invocation:** two separate `python3` processes produced
byte-identical stdout (sha256 of each captured stdout =
`703f6048dd5e4a775ea8cb79fede6b11c00ce52db4bbc82e0cc54e856121afe7`, identical).
The results-dict full-64 digest is
`721cabd10d50672c6ddae8a893c0cc773c727fdb9f6d789e27aa8e7ad7dd0190` — printed on
the `results_sha256=` line, exact 64-char compare, no truncation. Digest posture:
WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's
own sha256 IS the digest (`json.dumps(r, sort_keys=True, separators=(",",":"))`
→ `hashlib.sha256`); the dict carries no hash of itself and no time/random-address
content (seed is fixed). Exit code 0, `sim_ready=True`. Captured stdout is in
`run-stdout.txt`.

## Q8 — Grounding: is the result byte-pinned to a source, caveat honest?

Yes. Source: Wikipedia **"Reservoir sampling"**, oldid **1365118921**
(2026-07-20T10:42:39Z), `action=raw` wikitext. Raw-wikitext sha1 =
`daf21f648c352d230e4640de6a7574aaf9ac83fc` (22639 bytes), matching the MediaWiki
API-reported revision sha1 (independent 3-way match: API `rvprop=sha1` =
locally-computed `sha1(raw bytes)`). URL@sha1:
`https://en.wikipedia.org/w/index.php?title=Reservoir_sampling&action=raw&oldid=1365118921@sha1:daf21f648c352d230e4640de6a7574aaf9ac83fc`

- **On-page (confirmed present):** Algorithm R with the Waterman / Knuth TAOCP
  (2nd ed., pp.138–139) / Vitter (1985) attributions; the fill-then-replace
  structure (`§ History and Algorithm R`); and the correctness proof stating
  literally *"all inputs have an equal probability k/(i+1) of being included in
  the reservoir … Algorithm R produces a uniform random sample"* — the survival
  step `k/i × (1 − 1/(i+1)) = k/(i+1)` is exactly the Fraction product this sim
  multiplies out (at i = n it is the k/n claim).
- **Off-page (correctly absent):** the page proves uniformity analytically by
  induction; it does NOT contain this sim's firsthand computational verification
  — the SEED = 20260717, the specific (n,k) configs, the Monte-Carlo z-scores,
  the C(6,3) subset chi-square, the unconditional-replace falsifiability leg, or
  the results_sha256.

Caveat is honest — it neither oversells (does not claim Wikipedia contains the
Monte-Carlo / chi-square / falsifiability verification) nor undersells (the
Algorithm R uniform-inclusion result and its k/(i+1)→k/n proof are literally on
the pinned revision); the firsthand enumeration-of-fractions + Monte-Carlo +
subset-uniformity + falsifiability proof is disclosed as reproduction, not
citation.

## Recommendation

**Recommendation: sim-ready.** Stdlib-only single-seeded verifier; the exact
core is a LITERAL `fractions.Fraction` product (multiplied out, not hardcoded to
k/n) confirmed equal to Fraction(k,n) for every item in both configs; all four
pre-registered gates PASS in their own directions — G1 EXACT identity (every item
== k/n across the fill/replacement boundary), G2 Monte-Carlo agreement
(max |z| = 1.175565 < 3), G3 robustness (order-independence max |z| = 2.306936
< 3 AND subset-uniformity χ² = 15.0832 < 43.8 over all 20 subsets), G4
falsifiability (the unconditional-replace bug rejected at max |z| = 400.0 ≥ 6
plus the analytic first-k model rejected); determinism holds on both the
in-process double-run and the separate cross-invocation (byte-identical stdout);
and the result is byte-pinned to Wikipedia oldid 1365118921 (sha1 3-way match)
with an honest firsthand-vs-cited caveat.

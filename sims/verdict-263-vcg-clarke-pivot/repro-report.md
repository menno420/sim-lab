# VERDICT 263 reproduction mirror — Vickrey–Clarke–Groves (Clarke-pivot) multi-unit uniform-price mechanism, PROPOSAL 250

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 263 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 250 (fleet · Vickrey–Clarke–Groves / Clarke-pivot — multi-unit single-demand uniform-price mechanism: efficient allocation, externality payments, dominant-strategy truthfulness)
**Lane:** P250 → V263 (+13 offset)
**Verifier:** `verify_250_vcg_clarke_pivot.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 7b0758bc85433ed89f640bbe47aba2a4dd63bf337ab9b3a0a19c6a4497319f2b` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (`fractions.Fraction`, zero tolerance) — for each instance build the efficient allocation (the `k` highest-value bidders win) and compute each winner's Clarke-pivot payment as its externality on the others, `W_{-i}(without i) − W_{-i}(with i)`, entirely over `Fraction`; assert every winner's externality payment equals the SAME uniform price `= (k+1)-th highest valuation` and revenue `= k · price`. On the fixed instance `n=5, k=2, v=(10,8,6,4,2)`: winners `{10,8}`, each pivot payment `6/1`, `uniform_price=6/1`, `revenue=12/1`, all winners same price. Cross-checks: a tie instance `v=(10,8,8,4,2)` (price `8`), the `k=3` triple (price `4`, revenue `12`), and `k=1` which recovers single-item **second-price** (winner `{10}`, price `8` = 2nd-highest). `total_mismatches = 0` on every instance. `z` not applicable, reported `null`/`"exact"` → PASS
- **G2 Monte-Carlo agreement** (i.i.d. profiles) — the exact expected uniform price `E[V_{(k+1):n}]` is computed by FULL enumeration of the `6^5 = 7776` valuation profiles (`exact_mean_true = 7/1`), then estimated from `200000` random profiles: `sample_mean = 700641/100000 ≈ 7.006410`, `sample_std ≈ 2.351116`, giving `z = 1.2193` against the exact mean, `|z| = 1.2193 < 3` (Z_ACCEPT = 3.0). Profiles are i.i.d. draws, so the plain standard error is honest (`iid_se_is_honest = true`, no batch-means correction needed) → PASS
- **G3 invariance / equivariance** — two independent invariances, both EXACT: (a) **DSIC** — hold the other bidders fixed and vary a winner's own report across all `24` values that keep it winning (`7…30`); its Clarke payment stays the single value `6/1` (`distinct_payments = ["6/1"]`), confirming the payment is independent of the winner's own report; (b) **relabel equivariance** — apply the fixed node relabel `σ = [2,0,3,1,4]`, re-run the mechanism on the permuted bidder set and assert winners and payments map through `σ` exactly (`winners_original {0,1}` → `winners_relabelled {0,2}`, `mismatches = 0`, `payment_mismatches = 0`). `total_mismatches = 0`, `z` not applicable → PASS
- **G4 falsifiability** — on the SAME i.i.d. sample, the naive foil "uniform price = lowest WINNING bid (the `k`-th highest = 2nd highest)" is REJECTED at `z = −378.9138`, `|z| = 378.9138 ≫ 6` (`exact_mean_foil = 5831/648 ≈ 8.998457`, Z_REJECT = 6.0) while the same sample agrees with the true `(k+1)`-th-highest price at `|z| = 1.22` — the teeth: charging winners the lowest winning bid instead of the highest losing bid destroys the pivot property and truthfulness → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

For a multi-unit single-demand VCG (Clarke-pivot) mechanism allocating `k` identical units to `n` unit-demand bidders, the efficient allocation awards the units to the `k` highest-value bidders, and each winner's Clarke-pivot payment equals its externality on the others, `W_{-i}(\text{without } i) − W_{-i}(\text{with } i)`, which collapses to the SAME uniform price = the `(k+1)`-th highest valuation (the highest losing bid); truthful reporting is a dominant strategy and expected revenue `= k · E[V_{(k+1):n}]`. On the fixed instance `n = 5, k = 2, v = (10, 8, 6, 4, 2)`: winners `{10, 8}`, uniform price `6`, revenue `12`, pivots `6/6` (both winners pay the uniform `6`). At `k = 1` the mechanism recovers the single-item **second-price** auction (winner pays the 2nd-highest bid). The plausible naive belief that winners should pay the lowest winning bid (the `k`-th highest) rather than the highest losing bid (the `(k+1)`-th highest) is shown false on the same evidence (rejected at `|z| ≈ 378.9`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_250_vcg_clarke_pivot.py` (verifier file sha256 `8319b3192f3dc823939084b02105c37cdcb43bde6cede81e7fffabdab59ebf4e`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the exact-`Fraction` kernel is deterministic rational arithmetic; a single `random.Random(SEED)` is seeded once and consumed in a fixed order across the Monte-Carlo profiles; every rational serializes via `str(Fraction)` as `"num/den"`, integer counts as ints, and every z-value via a fixed `f"{z:.4f}"` string; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned reference revision and the quoted/derived split live with the source PROPOSAL 250, and the canonical grounding review belongs to the coordinator-driven VERDICT 263 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 263 slice, not here._

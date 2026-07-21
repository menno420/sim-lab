# VERDICT 264 reproduction mirror — Bulgarian solitaire: triangular-number staircase fixed point and k²−k convergence bound, PROPOSAL 251

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 264 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block. `control/status.md` is untouched.

**Source proposal:** idea-engine PROPOSAL 251 (fleet · combinatorial dynamics / integer partitions / Bulgarian solitaire — a deterministic self-map on partitions of `n`: on a triangular total every partition converges to the unique period-1 staircase fixed point within exactly `k²−k` steps; a non-triangular total never settles)
**Lane:** P251 → V264 (+13 offset)
**Verifier:** `verify_251_bulgarian_solitaire.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random)
**SEED:** 20260717
**Command:** `python3 verify_251_bulgarian_solitaire.py` (run from inside this directory; captured in `run-stdout.txt`)

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = f9fdd4c7a787d5b559248f8897ca00d82fa3e556535f67fd552a6854e0b19537` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (exact integer arithmetic, zero tolerance) — for `k=1..8` (`n = T_k` up to 36) enumerate ALL partitions of `T_k`, iterate each orbit to the staircase `δ_k = (k,…,1)`, count nonconvergent, and record `M(k) =` max steps-to-fixed-point; assert `M(k) == k²−k` exactly. Per-`k` `M(k) ∈ {0,2,6,12,20,30,42,56}` all matching `k²−k`, `total_nonconvergent = 0`, `num_partitions {1,3,11,42,176,792,3718,17977}`. The max-over-orbits route and the closed-form `k²−k` route are independent and agree with equality. `z` not applicable, reported `null`/`"exact"` → PASS
- **G2 Monte-Carlo agreement** (i.i.d. partition draws) — at `k=6` (`n=21`, 792 partitions) full enumeration gives the exact population `μ = 20.167929`, `σ = 8.471034` of steps-to-fixed-point; then `N_mc = 40000` UNIFORM partitions of `T_6` drawn with the seeded Nijenhuis–Wilf RANPAR sampler give sample mean `x̄ = 20.167375`, `z = (x̄−μ)/(σ/√N) = −0.0131`, `|z| = 0.0131 < 3` (Z_ACCEPT = 3.0), `convergence_rate = 1.000000` (100% reach `δ_6` within `k²−k = 30` steps). Each random partition's step-count is an INDEPENDENT draw, so the plain i.i.d. SE is honest (no thinning / batch means; stated in the verifier docstring) → PASS
- **G3 invariance** (own direction, exact, 0 mismatches) — two independent invariances: (a) **conservation** — over ALL enumerated orbits (`k=1..8`) `sum(step(p)) == sum(p)` at EVERY step, `908472` steps checked, `0` violations (card total `n` is the invariant); (b) **order-invariance** — for `1400` seeded RANPAR samples, `bulgarian_step` of a randomly SHUFFLED tuple equals `bulgarian_step` of the canonical descending tuple, `0` mismatches (the map is a function of the multiset, not pile order). `total_mismatches = 0`, `z` not applicable → PASS
- **G4 falsifiability** (own direction, OPPOSITE polarity to G2) — the "non-triangular `n` also has a unique period-1 fixed point" foil is REJECTED: (i) exact witness — all `19` non-triangular `n` in `[2,25]` (excluding `{1,3,6,10,15,21}`) exhibit a period>1 cycle, smallest `n=2` cycle `(1,1) → (2)`; (ii) MC — `N = 40000` (random non-triangular `n`, RANPAR partition) pairs, fraction landing in a period>1 cycle `f = 1.000000` (foil predicts 0), `z_foil = 40000.5000 ≫ Z_REJECT = 6.0`. The teeth: a non-triangular total never settles — it orbits — so "always converges to a unique fixed point" is false → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

For Bulgarian solitaire — the deterministic self-map `step(p) = sort_desc([x−1 for x in p if x−1 > 0] + [len(p)])` on integer partitions of `n` — if `n = T_k = k(k+1)/2` is triangular then from EVERY partition of `T_k` the iteration converges to the unique period-1 fixed point, the staircase `δ_k = (k, k−1, …, 2, 1)`, and the MAX steps over all partitions of `T_k` is EXACTLY `k²−k` (Wikipedia states "`k²−k` moves or fewer" — an upper bound; the exact tightness, that some partition attains equality, is derived here by full enumeration for `k=1..8`). On the headline instance `k=6, n=T_6=21`: all `792` partitions converge to `δ_6 = (6,5,4,3,2,1)`, `M(6) = 30 = 6²−6`, mean steps `μ ≈ 20.17`. If `n` is not triangular, NO fixed point exists — every orbit lands in a limit cycle of period > 1 (smallest witness `n=2`: `(1,1) ↔ (2)`). The plausible over-generalization that non-triangular `n` also settle to a unique fixed point is shown false on the same evidence (rejected at `|z_foil| ≈ 4·10⁴`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_251_bulgarian_solitaire.py` (verifier file sha256 `a317b1f8a61826cb96cf62c6beffb2c0e8c1762b16840c1c87d9d2bb35fdf326`). The copy in this directory carries the same sha256 and `diff` against the source is empty (exit 0), confirming a byte-for-byte reproduction of the source verifier; stdlib-only (json, hashlib, math, random), no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (`random.seed(SEED)` is re-seeded at the START of each Monte-Carlo gate so gate order cannot perturb the payload; cycles serialize as their lexicographically-smallest rotation, every float via a fixed `f"{x:.6f}"` / `f"{z:.4f}"` string, counts as ints; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned reference revision (Wikipedia "Bulgarian solitaire", oldid 1340511625, raw-wikitext sha1 `f5566931386c46e2b0d37407d24ac25fa8dcd9a3`) and the quoted/derived split live with the source PROPOSAL 251, and the canonical grounding review belongs to the coordinator-driven VERDICT 264 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 264 slice, not here. No `## VERDICT` block, no verdict high-water advance, `control/status.md` untouched._

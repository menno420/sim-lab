# VERDICT 258 reproduction mirror — open-addressing unsuccessful search under uniform hashing: with m slots and n occupied (load factor α=n/m) the EXPECTED number of probes is EXACTLY (m+1)/(m−n+1), rising monotonically to the classic 1/(1−α), PROPOSAL 245

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 258 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 245 (fleet · hashing / load-balancing — open-addressing unsuccessful-search expected probes is exactly (m+1)/(m−n+1))
**Lane:** P245 → V258 (+13 offset)
**Verifier:** `verify_245_open_addressing_probes.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 98d7398935db83b93f4e5b71ef4393abf487d3bc4371018d0d9d16e4f75e1746` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT identity** (`fractions.Fraction`, zero tolerance) — over the battery `{(1,0),(2,1),(3,2),(5,3),(10,7),(13,0),(16,8),(23,17),(50,35),(100,70),(128,96),(257,200)}` the finite sum-of-products definition `Σ_{i=0}^{n} C(n,i)/C(m,i)`, the closed form `(m+1)/(m−n+1)`, and the hockey-stick ratio `C(m+1,n)/C(m,n)` are EXACTLY equal — `mismatches = 0`, `anchor_mismatches = 0`, **max discrepancy exactly 0** (z not applicable, reported `null`/`"exact"`). Anchors `(1,0)→1`, `(2,1)→3/2`, `(3,2)→2`, `(10,7)→11/4` pinned → PASS
- **G2 Monte-Carlo agreement** — headline `(m=100, n=70)`, `N = 200000` i.i.d. uniform-hashing unsuccessful searches (uniformly random probe permutation per trial via the seeded RNG, `n` occupied, count probes to the first empty slot); `mean_hat = 3.2596` vs `E_exact = 101/31 ≈ 3.2581`, `z = 0.2616711626`; `|z| < 3` (Z_ACCEPT = 3.0). The trials are INDEPENDENT (one probe-count per trial) so NO thinning is needed → PASS
- **G3 invariance / robustness** — the expected probe count depends ONLY on `(m,n)`, not on WHICH slots are occupied: config A (occupied = first `n` slots) `z = 0.3374925104`, config B (occupied = fixed pseudo-random `n`-subset) `z = −1.1046610225`, two-sample invariance `z = 1.0187955206`, all `|z| < 3`. Exact monotone-convergence sub-check at `α = 7/10` over `m ∈ {10,100,1000,10000,100000}` → `11/4, 101/31, 143/43, 10001/3001, 100001/30001` strictly increasing, every term strictly below the limit `10/3`, approaching it → PASS
- **G4 falsifiability** — on the SAME headline `(100,70)` sample, the naive belief "expected probes = `1/(1−α)` exactly at finite `(m,n)`" = `10/3 ≈ 3.333` is REJECTED at `z = 12.5653466132 ≫ 3` (Z_REJECT = 3.0), while the same sample agrees with the exact `101/31` at `|z| = 0.26` — the teeth: `1/(1−α)` is a limit, not a finite-table equality → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In an open-addressing hash table under the UNIFORM-HASHING model — each key's probe sequence is a uniformly random permutation of all `m` slots — with `m` slots and `n` occupied (load factor `α = n/m`), the expected number of probes in an UNSUCCESSFUL search is EXACTLY `E_unsucc(m,n) = (m+1)/(m−n+1)`. This follows from the exact combinatorial definition `E = Σ_{i≥0} P(first i probes all occupied) = Σ_{i=0}^{n} C(n,i)/C(m,i)`, which equals `(m+1)/(m−n+1)` by the hockey-stick identity (`C(n,i)/C(m,i) = C(m−i,n−i)/C(m,n)` ⇒ `Σ = C(m+1,n)/C(m,n) = (m+1)/(m−n+1)`). As `m, n → ∞` at fixed `α` it increases monotonically to the classic `1/(1−α)`. The plausible naive belief that `1/(1−α)` holds exactly at finite `(m,n)` is shown false on the same evidence: at `m=100, n=70` the truth is `101/31 ≈ 3.258`, not `10/3 ≈ 3.333` (rejected at `|z| ≈ 12.57`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_245_open_addressing_probes.py` (verifier file sha256 `ac4642df4a3b77fe35c418ffba9d2038589d9463cb1c40e1f341e0d371c5c5ab`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the exact-`Fraction` kernel is deterministic rational arithmetic; a single `random.Random(SEED)` is seeded once and consumed in a fixed order across all Monte-Carlo legs; every float serializes via a fixed format string and every exact rational via `str(Fraction)`; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revision ("Open addressing", oldid 1353211902) and the quoted/derived split live with the source PROPOSAL 245, and the canonical grounding review belongs to the coordinator-driven VERDICT 258 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 258 slice, not here._

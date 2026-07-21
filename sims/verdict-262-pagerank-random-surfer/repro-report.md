# VERDICT 262 reproduction mirror — PageRank / random-surfer stationary distribution on a fixed 4-node directed graph (0→{1,2}, 1→{2,3}, 2→{0}, 3→{} dangling), damping d=1/2, uniform teleport 1/N: the row-stochastic Google matrix has the EXACT rational left-eigenvector π=(52/179, 40/179, 50/179, 37/179), PROPOSAL 249

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 262 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 249 (fleet · PageRank / random-surfer — exact stationary distribution of the Google matrix on a fixed 4-node directed graph)
**Lane:** P249 → V262 (+13 offset)
**Verifier:** `verify_249_pagerank_random_surfer.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 18ba2ac7a7bfe36dc476214f79d55c26c3e212d8073d581ae226da55d4154355` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (`fractions.Fraction`, zero tolerance) — build the row-stochastic Google matrix `G` exactly (non-dangling row `G[i][j]=d·A[i][j]/outdeg(i)+(1−d)/N`; dangling row uniform `1/N`), solve `π` by Gaussian elimination over Fraction on `(Gᵀ−I)` with the `Σπ=1` constraint → `π=(52/179,40/179,50/179,37/179)`; `πG=π` with **max residual exactly 0** on every entry and `Σπ=1` exactly; the independent **adjugate/cofactor null-vector** of `(Gᵀ−I)` equals `π` exactly (`adjugate_mismatches=0`); exact power iteration from uniform converges to `π` within `1e-18` in 32 iters (corroboration — `λ₂≠0` so an exact stochastic matrix never reaches `π` in finitely many exact steps). `z` not applicable, reported `null`/`"exact"` → PASS
- **G2 Monte-Carlo agreement** (batch means) — ONE random-surfer chain (with prob `1−d` teleport uniformly, else follow a uniform out-link, dangling⇒teleport), burn-in `50000`, then `200` batches × `20000` steps = `4 000 000` post-burn-in steps; per-node batch-means `z` against `π`: node0 `−1.7965`, node1 `−0.3012`, node2 `0.8511`, node3 `0.8993`, **max|z| = 1.7965 < 3** (Z_ACCEPT = 3.0). Random-walk occupancy is autocorrelated, so batch means (batches ≫ mixing time) give an honest SE → PASS
- **G3 equivariance / invariance** — apply the fixed non-trivial node relabel `σ = [2,0,3,1]`, rebuild `G` and re-solve `π` on the permuted graph exactly, assert it equals `σ(π_original)` exactly: `relabel_mismatches = 0` (`π_permuted = (40/179, 37/179, 52/179, 50/179) = σ(π)`) → PASS
- **G4 falsifiability** — on the SAME batch-means sample, the naive hypothesis "π ∝ in-degree" = `(1/5, 1/5, 2/5, 1/5)` is REJECTED at **max|z| = 646.5432 ≫ 6** (node2 `−646.54`, node0 `568.61`, Z_REJECT = 6.0) while the same sample agrees with the true `π` at `max|z| = 1.80` — the teeth: raw in-degree ignores that a link's weight is itself set by the linking node's PageRank and the damping/teleport structure → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

On the FIXED directed graph of `N = 4` nodes with out-links `0→{1,2}`, `1→{2,3}`, `2→{0}`, `3→{}` (node 3 DANGLING — no out-links), the PageRank random-surfer process with damping `d = 1/2` and uniform teleport `1/N` has the EXACT rational stationary distribution `π = (52/179, 40/179, 50/179, 37/179) ≈ (0.2905, 0.2235, 0.2793, 0.2067)`, the unique probability vector with `πG = π`. The row-stochastic Google matrix `G` gives a non-dangling row `i` the weights `G[i][j] = d·(A[i][j]/outdeg(i)) + (1−d)/N` and the dangling row the uniform `1/N`. Notably node 2 (in-degree 2) ranks BELOW node 0 (in-degree 1), because a link's weight is set by the linking node's own PageRank and the damping/teleport structure — so the plausible naive belief that the stationary attention share is proportional to raw in-degree, `(1/5, 1/5, 2/5, 1/5)`, is shown false on the same evidence (rejected at `max|z| ≈ 646.5`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_249_pagerank_random_surfer.py` (verifier file sha256 `3e1e7647fb485f0739ebce9f4d3f288f09ea5c97b15115e7166cf91324f812c1`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the exact-`Fraction` kernel is deterministic rational arithmetic; a single `random.Random(SEED)` is seeded once and consumed in a fixed order across the whole chain; every rational serializes via `str(Fraction)` as `"num/den"`, integer visit counts as ints, and every z-value via a fixed `f"{z:.4f}"` string; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revision ("PageRank", oldid 1364775010) and the quoted/derived split live with the source PROPOSAL 249, and the canonical grounding review belongs to the coordinator-driven VERDICT 262 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 262 slice, not here._

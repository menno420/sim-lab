# VERDICT 260 reproduction mirror — Green Hackenbush is Nim (colon principle), PROPOSAL 247

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 260 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 247 (PR #868, merge `a4ae8d3038cdf538fb6c7edb936b95a90b063289`)
**Lane:** P247 → V260 (+13 offset)
**Verifier:** `verify_247_green_hackenbush_nim.py` (byte-identical copy of the firsthand idea-engine verifier `ideas/superbot-games/verify_247_green_hackenbush_nim.py`; stdlib only: hashlib, itertools, json, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = f1967eac6a0158fb4b1546facd309355577f251033067167296f6b921903c0b9` — byte-identical to the idea-engine source digest.
- determinism triple: default run · `--selfcheck` (in-process double-run, SELFCHECK OK) · separate re-invocation — all byte-identical.
- **G1 EXACT identity** (integer/XOR only, zero tolerance) — over an EXHAUSTIVE enumeration of all rooted trees with ≤ 7 edges (200 distinct trees) PLUS a random battery of larger trees and forests (up to 14 edges, max `34` edges reached), the closed-form `colon_value(pos)` equals the ground-truth `grundy(pos)` mex-DP oracle at every position: `800` positions checked, `mismatches = 0`. Anchors pinned — bamboo(3,5,7) `grundy = colon = 3^5^7 = 1`, Y-tree `grundy = colon = 1`, explicit tree `grundy = colon = 4` → PASS
- **G2 MC agreement** (`|z| < 3`) — finite model of `k=3` bamboo forests, each stalk length uniform in `{1..8}` (`512` equally-likely forests). All 512 solved with the ground-truth engine for the exact P-density `p0 = 21/256 ≈ 0.08203` (`p0_count = 42`); `N = 200000` i.i.d. forests classified P/N by the same engine, `p_hat = 0.08248`, binomial `z = 0.7313341378`; `|z| < 3` → PASS
- **G3 invariance / robustness** — (a) relabel / child-order invariance: over `200` random trees, both `grundy` and `colon_value` survive a random vertex relabeling fixing ground 0, `relabel_discrepancies = 0`. (b) optimal-play robustness: the theory-optimal player (moves to a grundy-0 successor via the engine) beats a random opponent in every game — `360` games played, `optimal_play_losses = 0` → PASS
- **G4 falsifiability** (`|z| > 5` each) — on the SAME model, two plausible Nim mistakes (arithmetic instead of XOR) are rejected against the engine's true P-density far outside 5σ: Foil A "sum parity" (`q_A = 1/2`) at `|z| = 373.4412407863`, Foil B "sum mod 3" (`q_B = 85/256`) at `|z| = 236.9775442593`, while the same sample agrees with the exact `p0` at `z = 0.73` → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In Green Hackenbush a rooted forest of "green" edges hangs from a single ground vertex; a move removes one edge and every edge no longer connected to the ground is then deleted, normal play. The Sprague-Grundy value has a closed form via the COLON PRINCIPLE — `sub(v, parent) = XOR over children c of (1 + sub(c, v))`, `sub(leaf) = 0`, and `value(forest) = XOR over ground's neighbours r of (1 + sub(r, 0))`. The consequence is that Green Hackenbush IS Nim: a bamboo forest of stalk-lengths `(a1,…,ak)` has value `a1 XOR … XOR ak`, a first-player win iff the nim-sum is non-zero. Reproduced here by an independent `grundy` mex-DP oracle that does NOT assume the theorem, compared position-by-position against the closed-form `colon_value`, with the game engine alone driving every Monte-Carlo classification: exact identity holds with zero mismatches, the engine's P-density matches Monte-Carlo inside 3σ, and both natural arithmetic foils are rejected beyond 200σ.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/superbot-games/verify_247_green_hackenbush_nim.py` (verifier file sha256 `da7f11191025addd748d29a49d22eb9173bd05ab8775bf8458a62e65b31b639b`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. `build_results()` is a pure function of SEED and the fixed model params (no wall clock, no hostname, no unseeded randomness; `random` is reseeded at the start of every sampling gate so results are position-independent; every float is rounded to 10 decimals before hashing), so the in-process double-run (`--selfcheck`) and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned source references and the quoted/derived split live with the source PROPOSAL 247, and the canonical grounding review belongs to the coordinator-driven VERDICT 260 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 260 slice, not here._

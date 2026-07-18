# Probe report — VERDICT 132 · PRD proc-rate compression (P119 → V132, +13)

**Verdict: APPROVE** (exact reproduction) — ruling + card flip WITHHELD for dispatcher audit (PHASE 1).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/prd_proc_compression.py` — `diff` exit **0**, git blob `4d4e1865d9eb05e0cd5b625258c80cc5e0852f81`, file sha256 `b2aef76244a566cb8879e7850eea324bdfc39a13aa20eabc872697903d9426d2`.
- Pinned world: **SEED=20260717**, ATTEMPTS=**2000000**, C_NAIVE=0.25, TARGET=0.25, SIGMA_GATE=3.0, EFF_MIN=0.40, SOLVED_MAX=0.15. Stdlib-only (random, math, json, hashlib).
- DIGEST POSTURE: digest computed over `json.dumps(results, sort_keys=True, separators=(",",":"))` **before** the `results_sha256` field is added; the on-disk `prd_proc_compression_results.json` is pretty-printed (indent=2) **with** that field, so its own `sha256sum` (`d045daa6…`) is NOT the digest. The disclosed digest is the `Results-JSON sha256:` stdout line / the file's `results_sha256` field.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P119 outbox) | `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` |
| cross-invocation A (fresh `python3`) | `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` |
| cross-invocation B (fresh `python3`) | `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` |
| in-process invocation 1 | `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` |
| in-process invocation 2 | `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` |

**All four computations == the disclosed digest EXACTLY.** all_pass=true, exit 0, byte-identical across runs.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** naive-C overshoot | eff_naive 0.450684 ≥ 0.40, z=146.3107, z_vs_null_0.25=**655.4296σ** | eff_naive **0.450684**, z=**146.3107**, z_vs_null_0.25=**655.4296** | **PASS** |
| **G2** solve-C-fixes-it | c_solved 0.084744 ≤ 0.15, eff_solved 0.24998 vs 0.25 \|z\|=0.0637 | c_solved **0.084744**, eff_solved **0.24998**, z=**−0.0637** | **PASS** |
| **G3** anchor + anti-streak | eff_naive 0.450684 vs cf 0.450704 \|z\|=0.0589; streak 3 < 51 | z_anchor **−0.0589**; PRD streak **3** < random **51** | **PASS** |

## Analytic anchors & sim (all match disclosed exactly)
- **E[N]=2.21875**, eff_naive_closed_form=**0.450704**, c_solved=**0.084744**, eff_solved_closed_form=0.25, PRD max-streak bound ⌈1/C⌉−1=**3**.
- Sim: eff_naive **0.450684** (max streak **3**), eff_solved **0.24998** at C=0.084744 (max streak 11), eff_random **0.249999** (max streak **51**).

**Headline:** setting the PRD increment equal to the nominal rate (C=0.25) ships a proc that fires at **0.4507** — **655σ** above the intended 0.25, ~80% too often. Solving for C (**0.0847**, a third of nominal) recovers 0.25. PRD's real product is the **streak bound (3 misses vs true-random's 51)**, not a rate change.

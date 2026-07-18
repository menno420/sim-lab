# Probe report — VERDICT 135 · NRR composition mirage (P122 → V135, +13)

**Verdict: APPROVE** (exact reproduction) — born-red card flip released on this audited ruling.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/venture-lab/nrr_composition_mirage.py` — `diff` exit **0**, git blob `3285a22e9af9fb7ca46364384398bed54c64750c`, file sha256 `da6c1893b2c4c3255c08142790e74ea1e795f9b6a97400bf70fabfbfb6fe0bf2`, **250** lines / **10447** bytes.
- Pinned world: **SEED=20260717**, TRIALS=**400**, N_ACCOUNTS=**20000**, F_WHALE=**0.10**, R_BIG=**100.0**, R_SMALL=**1.0**, P_WHALE=**0.95**, EXP_WHALE=**1.30**, P_MINNOW=**0.60**, EXP_MINNOW=**1.00**, SIGMA_GATE=**3.0**, GAP_MIN=**0.05**. Stdlib-only (random, math, json, hashlib); no numpy/scipy.
- DIGEST POSTURE: **NO-SELF-FIELD / COMPACT-STDOUT** — this DIFFERS from the V133/V134 SELF-FIELD/pretty-on-disk posture. The verifier computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical)`, then prints the compact canonical line, then `sha256: <digest>`, then the summary + 3 gate lines + `ALL_PASS: True`, and writes **no** results.json. The results-dict carries **no** `results_sha256` field.
- Reconciliation (honest): because the verifier writes no on-disk json, the committed `nrr_composition_mirage_results.json` here **IS** the exact compact canonical bytes that were hashed — the verbatim first line of `run-stdout.txt`, stored with **no trailing newline** (1161 bytes, last byte `}`). Re-hashing that file's content therefore reproduces the disclosed digest directly: `sha256(file) = de67af4a…d3bb` (both raw and after `rstrip(b"\n")`, since there is no trailing newline). `run-stdout.txt` is consequently the compact canonical line + `sha256:` + summary + 3 gate lines + `ALL_PASS: True` — **not** pretty JSON; that is correct for this posture.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P122 outbox) | `de67af4a73bb810deefa5a916bbf76a1bc7a8fa141ae3f26fdcd755eb582d3bb` |
| cross-invocation A (fresh `python3`) | `de67af4a73bb810deefa5a916bbf76a1bc7a8fa141ae3f26fdcd755eb582d3bb` |
| cross-invocation B (fresh `python3`) | `de67af4a73bb810deefa5a916bbf76a1bc7a8fa141ae3f26fdcd755eb582d3bb` |
| in-process double-run (run() ×2, hashed in-process) | `de67af4a73bb810deefa5a916bbf76a1bc7a8fa141ae3f26fdcd755eb582d3bb` (both) |

**All computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run. Re-hash of the committed `nrr_composition_mirage_results.json` == `de67af4a…d3bb`.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** NRR-vs-logo divergence | mean=**0.547811** (se 0.000307) ≥ 0.05, z=**1621.337** | mean **0.547811** (se 0.000307), z **1621.337** | **PASS** |
| **G2** concentration control | mean=**0.519328** (se 0.000298) ≥ 0.05, z=**1575.1311**, sign_flip=**True** | mean **0.519328** (se 0.000298), z **1575.1311**, sign_flip **True** | **PASS** |
| **G3** closed-form anchor match | z_nrr_dollar=**0.4169**, z_nrr_equal=**0.7515** (both \|z\|<3) | z_nrr_dollar **0.4169**, z_nrr_equal **0.7515** | **PASS** |

First-failing gate: **none**. all_pass=**true**.

## Sim & anchors (all match disclosed exactly)
- Closed forms (from the pinned constants): nrr_dollar_cf=**1.182569** (=W_WHALE·EM_WHALE+(1−W_WHALE)·EM_MINNOW), nrr_equal_cf=**0.6635** (=F_WHALE·EM_WHALE+(1−F_WHALE)·EM_MINNOW), logo_ret_cf=**0.635** (=F_WHALE·P_WHALE+(1−F_WHALE)·P_MINNOW). Derived constants: whale_revenue_share W_WHALE=**0.917431**, EM_WHALE=**1.235**, EM_MINNOW=**0.6**.
- Sim (means over 400 trials): NRR_dollar **1.182695** (se 0.000302), logo_ret **0.634884** (se 0.000168), NRR_equal **0.663366** (se 0.000178); G1 divergence **0.547811** (se 0.000307), G2 concentration **0.519328** (se 0.000298), sign_flip **True** (NRR_equal 0.663366 < 1.0 < 1.182695 NRR_dollar).
- G3 anchor match: NRR_dollar 1.182695 vs closed-form 1.182569 → \|z_nrr_dollar\|=**0.4169** (<3); NRR_equal 0.663366 vs closed-form 0.6635 → \|z_nrr_equal\|=**0.7515** (<3) — the sim reproduces both weighted closed forms.

**Headline:** dollar-weighted NRR reads **1.1827** (>100%, "negative net churn", best-in-class) while logo (count-weighted) retention is only **0.634884** — a third of customers gone — a **0.547811** divergence at **1621σ**; and equal-weighting every account collapses NRR to **0.663366** (<1.0, contracting per logo), a **0.519328** concentration gap at **1575σ** with the sign flip NRR_equal < 1 < NRR_dollar. The >100% is pure revenue concentration (10% whales owning **91.7%** of revenue expanding at 1.235× while the minnow tail churns), a Simpson-style weighting mirage — the sim reproduces both weighted closed forms within 3σ (0.42σ / 0.75σ) and byte-for-byte across cross-invocations, all gates ≥3σ. **APPROVE.**

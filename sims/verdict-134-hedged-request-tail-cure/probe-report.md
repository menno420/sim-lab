# Probe report — VERDICT 134 · hedged-request tail cure (P121 → V134, +13)

**Verdict: APPROVE** (exact reproduction) — born-red card flip released on this audited ruling.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/hedged_request_tail_cure.py` — `diff` exit **0**, git blob `5bd1866e2432bd0e6f90289ea4bac7971e32bbfd`, file sha256 `be975454449d39e75f6bf543e952622e3df8966921190f16667d8fb2cd82f1c6`, **254** lines / **11916** bytes.
- Pinned world: **SEED=20260717**, MEAN_FAST=**10.0**, MEAN_SLOW=**200.0**, P_STRAGGLER=**0.05**, N_REQUESTS=**20000**, TRIALS=**200**, HEDGE_PCTL=**0.95**, CAPTURE_MIN=**0.80**, LOAD_MAX=**0.08**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy.
- DIGEST POSTURE: SELF-FIELD / stdout-line (the P119/V132/V133 posture). The digest is computed over `json.dumps(results, sort_keys=True, separators=(",",":"))` **before** the `results_sha256` field is added; the on-disk `hedged_request_tail_cure_results.json` is pretty-printed (indent=2, sort_keys) **with** that field, so its own `sha256sum` is NOT the digest. The disclosed digest is the `Results-JSON sha256:` stdout line / the file's `results_sha256` field.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P121 outbox) | `a76ef737962bd9c3663399dc19425dc3ca697c6d8775be682c3a128aa76b1b4e` |
| cross-invocation A (fresh `python3`) | `a76ef737962bd9c3663399dc19425dc3ca697c6d8775be682c3a128aa76b1b4e` |
| cross-invocation B (fresh `python3`) | `a76ef737962bd9c3663399dc19425dc3ca697c6d8775be682c3a128aa76b1b4e` |
| in-process double-run | deterministic (identical per-trial draws run-to-run) |

**Both cross-invocations == the disclosed digest EXACTLY.** all_pass=true, exit 0, byte-identical across runs (cross-invocation stdout diff exit **0** AND results-json diff exit **0**); the in-process double-run reproduced identical per-trial p99 draws.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** hedge collapses the tail | z=**283.5451** | z=**283.5451** | **PASS** |
| **G2** the knee (capture + load) | z_capture=**237.7642**, capture=**0.889581**, hedge-load=**0.04995** ≤ 0.08 | z_capture **237.7642**, capture **0.889581**, hedge-load **0.04995** ≤ 0.08 | **PASS** |
| **G3** almost-free efficiency | z=**282.3895** | z=**282.3895** | **PASS** |

First-failing gate: **none**. all_pass=**true**.

## Sim & anchors (all match disclosed exactly)
- Closed-form mixture anchors (exact CDF percentiles by bisection): mixture p95=**45.388281**, mixture p99=**321.887582**, full-dup extra load=**1.0**.
- Sim: mean p99 baseline **322.613793** (se 0.973275), mean p99 hedge@p95 **60.701541** (se 0.120278), mean p99 full-dup **28.232104** (se 0.043837), mean tail-cut (base−hedge) **261.912252** (se 0.923706), mean hedge-fire fraction **0.04995** (se 0.0), mean capture ratio **0.889581** (se 0.000377), mean efficiency edge **4949.106846** (se 17.525819).
- Efficiency: hedge tail-cut per unit load **5243.488535** vs full-dup **294.381688** — ratio **17.811871×**.

**Headline:** a single-replica request has a p99 latency of **322.61** dominated by the straggler tail. Deferring a second copy to the **p95** delay (d=45.39) — firing on only **4.995%** of requests (extra load ≈0.05, not the +100% of full duplication) — collapses the p99 to **60.70**, a **261.91** cut (**283.5σ**), recovering **88.96%** of full duplication's tail collapse (**237.8σ** above the 80% floor). Because the hedged tail survives only when BOTH independent copies straggle (≈p²≈0.0025, past p99), the tail cure is almost free: its tail-reduction PER UNIT of extra load (**5243.5**) beats full duplication's (**294.4**) by **17.8×** (**282.4σ**). The last ~11% of tail benefit that full duplication buys BEYOND the p95 hedge costs ~20× the load — the knee — so fleet dispatch should tie-hedge after ~p95 rather than duplicate.

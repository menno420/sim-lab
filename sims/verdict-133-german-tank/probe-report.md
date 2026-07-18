# Probe report — VERDICT 133 · German-tank MVUE (P120 → V133, +13)

**Verdict: APPROVE** (exact reproduction) — born-red card flip released on this audited ruling.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/german_tank_mvue.py` — `diff` exit **0**, git blob `de5487e5bf706163188f811b97ed3b4723fc148a`, file sha256 `130ebaafa72f8931440ac929954f8b0987d14ff947d5e7b09f36e8fe5b006aaf`, **188** lines / **8497** bytes.
- Pinned world: **SEED=20260717**, N_TRUE=**1000**, K=**5**, SAMPLES=**4000**, TRIALS=**200**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy.
- DIGEST POSTURE: SELF-FIELD / stdout-line (the P119/V132 posture). The digest is computed over `json.dumps(results, sort_keys=True, separators=(",",":"))` **before** the `results_sha256` field is added; the on-disk `german_tank_mvue_results.json` is pretty-printed (indent=2, sort_keys) **with** that field, so its own `sha256sum` (`145db407…`) is NOT the digest. The disclosed digest is the `Results-JSON sha256:` stdout line / the file's `results_sha256` field.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P120 outbox) | `37cea2bfb9b3f60c564d78bb6e5b31c9fcfe8ee7cb11c2fbafe38ddf9af31531` |
| cross-invocation A (fresh `python3`) | `37cea2bfb9b3f60c564d78bb6e5b31c9fcfe8ee7cb11c2fbafe38ddf9af31531` |
| cross-invocation B (fresh `python3`) | `37cea2bfb9b3f60c564d78bb6e5b31c9fcfe8ee7cb11c2fbafe38ddf9af31531` |
| in-process invocation 1 | `37cea2bfb9b3f60c564d78bb6e5b31c9fcfe8ee7cb11c2fbafe38ddf9af31531` |
| in-process invocation 2 | `37cea2bfb9b3f60c564d78bb6e5b31c9fcfe8ee7cb11c2fbafe38ddf9af31531` |

**All four computations == the disclosed digest EXACTLY.** all_pass=true, exit 0, byte-identical across runs (cross-invocation stdout diff exit 0 AND results-json diff exit 0).

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** MVUE-unbiased | mean N̂ 999.927753 vs 1000, \|z\|=**0.3941** | mean N̂ **999.927753**, \|z\|=**0.3941** | **PASS** |
| **G2** max-biased-low + MVUE-above-max | z_bias=**1086.0456**, z_above=**694.9667** | z_bias **1086.0456**, z_above **694.9667** | **PASS** |
| **G3** anchor-match + efficiency | z_var_match=**0.9831**, z_efficiency=**344.4929** | z_var_match **0.9831**, z_efficiency **344.4929** | **PASS** |

## Analytic anchors & sim (all match disclosed exactly)
- Closed-form anchors: E[m]=**834.166667**, bias_max (N−E[m])=**165.833333**, Var(N̂)=**28457.0**, Var(Ñ)=**66399.666667**, efficiency ratio (K+2)/3=**2.333333**.
- Sim: mean N̂ **999.927753** (se 0.1833), mean sample max **834.106461** (se 0.15275), N̂-above-max gap **165.821292** (se 0.238603), Var(N̂) **28509.405891** (se 53.306373), Var(Ñ) **66476.372769** (se 96.462074), variance gap **37966.966877** (se 110.211166).

**Headline:** the naive "population = largest serial seen" (sample max **834.11**) sits **1086σ** BELOW the true N=1000, while the MVUE that EXTRAPOLATES ABOVE the largest observed serial averages **999.93** (within 0.39σ of N) — landing **165.82** ABOVE the max (**695σ**) — and reproduces the exact closed-form variance **28457** (0.98σ) while beating the unbiased mean-doubling estimator on variance by **37967** (**344σ**). The best estimate of a population size is LARGER than the largest one you have seen, and the max-based correction is minimum-variance.

# Probe report — VERDICT 150 · service-variance wait tax (P137 → V150, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/fleet/service_variance_wait_tax.py` at `f008e13` (PROPOSAL 137, round-32 FLEET slot OPENER, landed via idea-engine #577). Permalink: https://github.com/menno420/idea-engine/blob/f008e130a058b1a62b92d053bb6fd315ec730ac4/ideas/fleet/service_variance_wait_tax.py

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/service_variance_wait_tax.py` — `diff` exit **0**, file sha256 `945c0af9bc496522f1b03935afa975a89386a58ab76a246c870a3a2cc6c97974`, git blob `c13e49f78abac8ff39dd62514e37a97413c18624`, **174** lines / **5592** bytes.
- Pinned world: **SEED=20260717**, **RHO=0.8**, **MEAN_SERVICE=1.0** (so λ=ρ/E[S]=0.8), **N_JOBS=600000**, **WARMUP=150000**, **REPLICATIONS=30**, **CV2_H2=4.0**, **Z_GATE=3.0**. Stdlib-only (hashlib, json, math, random); no numpy/scipy.
- Method: the exact single-server FIFO **Lindley recursion** W_{i+1}=max(0, W_i+S_i−T_i) with interarrivals T_i~Exp(λ) and service S_i drawn per distribution under test (D deterministic, M exponential, H2 balanced-means two-phase hyperexponential). Because Lindley waits are **autocorrelated**, naive std/√n is invalid; the verifier uses the **METHOD OF INDEPENDENT REPLICATIONS** — each of 30 replications runs N_JOBS with a WARMUP discard and contributes ONE sample (its post-warmup mean W_q), replications get independent 64-bit sub-seeds from a master `random.Random(SEED)`, and z=(grand_mean−W_q_theory)/(std_across_reps/√R). PASS iff |z|<3.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode("utf-8")).hexdigest()`, then PRINTS the pretty `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump printed on stdout — recompute over the compact form. The compute entry is `run()`, so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P137 outbox / verifier `Results-JSON sha256:` line) | `ab44d56a22c24f83c4a2048af56dc3dbdbf462d3aa9990bd19c64426891e4307` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `ab44d56a22c24f83c4a2048af56dc3dbdbf462d3aa9990bd19c64426891e4307` |
| cross-invocation B (fresh `python3`) | `ab44d56a22c24f83c4a2048af56dc3dbdbf462d3aa9990bd19c64426891e4307` |
| in-process run 1 (`run()` compact-hashed) | `ab44d56a22c24f83c4a2048af56dc3dbdbf462d3aa9990bd19c64426891e4307` |
| in-process run 2 (`run()` compact-hashed) | `ab44d56a22c24f83c4a2048af56dc3dbdbf462d3aa9990bd19c64426891e4307` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across cross-invocation A/B (stdout diff exit **0**) and across the in-process double-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** M/D/1 (C²=0) grand-mean vs P-K anchor 2.0 | z **+0.496** | grand_mean **2.002221** vs wq_theory **2.000000**, z **+0.496222**, se **0.004476**, std **0.024515**, \|z\| < 3.0 | **PASS** |
| **G2** M/M/1 (C²=1) grand-mean vs P-K anchor 4.0 | z **−0.934** | grand_mean **3.987717** vs wq_theory **4.000000**, z **−0.934478**, se **0.013144**, std **0.071994**, \|z\| < 3.0 | **PASS** |
| **G3** M/H2/1 (C²=4) grand-mean vs P-K anchor 10.0 | z **−1.838** | grand_mean **9.921619** vs wq_theory **10.000000**, z **−1.837859**, se **0.042648**, std **0.233594**, \|z\| < 3.0 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- **P-K closed forms (no RNG):** W_q = (ρ/(1−ρ))·E[S]·(1+C²)/2 at ρ=0.8, E[S]=1.0 gives (ρ/(1−ρ))·E[S]=4.0, so W_q = 4.0·(1+C²)/2 = **2.0** (C²=0), **4.0** (C²=1), **10.0** (C²=4) — the exact 1:2:5 spread. (Floating point: 2.0000000000000004 / 4.000000000000001 / 10.000000000000002.)
- **H2 balanced-means params (C²=4, mean 1.0):** p1=½(1+√((4−1)/(4+1)))=**0.8872983346207417**, branch means b1=1/(2·p1)=**0.5635083268962916**, b2=1/(2·p2)=**4.436491673103709** — yielding overall mean 1.0 and C²=4 exactly.
- **G1 (deterministic M/D/1, C²=0):** the MC grand-mean queue wait **2.002221** matches the P-K anchor **2.0** within z=**+0.496** — the baseline: with zero service variance the wait is the pure load term.
- **G2 (exponential M/M/1, C²=1):** the MC grand-mean **3.987717** matches the P-K anchor **4.0** within z=**−0.934** — DOUBLE the deterministic wait at the SAME ρ=0.8 and SAME E[S]=1.0, from service variance alone.
- **G3 (hyperexponential M/H2/1, C²=4):** the MC grand-mean **9.921619** matches the P-K anchor **10.0** within z=**−1.838** — 5× the deterministic wait, completing the 1:2:5 variance-only spread; the tax factor (1+C²)/2 is a multiplicative term utilization/throughput math never sees.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = any fleet-ops / SRE / capacity planner reading a latency-vs-utilization dashboard (request-serving fleets, RPC backends, job queues, disk/IO schedulers — any single-server FIFO stage). The transferable correction: **at fixed utilization and fixed mean service, queue wait scales with (1+C²)/2 — the service-time variance — so two stages at identical load and throughput can differ 5× in latency.** A utilization/throughput dashboard is BLIND to this: it shows ρ and jobs/sec, never Var(S). To act on it: measure the service-time CoV (not just the mean), attack variance directly (bound tail service times, split heterogeneous work into separate queues so each is near-deterministic, cap retries that fatten the service distribution), and read latency SLOs against C² not just ρ. Adjacent to but DISTINCT from P089 variance-blind-provisioning-trap (which prices the SLA-violation RATE and the (1+CV²) CAPACITY-provisioning correction across two lanes); this is the pure Pollaczek–Khinchine queue-WAIT LAW across D/M/H2 at fixed ρ and fixed mean — the tax itself, not the provisioning response. Also distinct from the inspection-paradox wait inflation (observer / size-biased sampling of a renewal process, not the M/G/1 equilibrium wait) and from checkout-pooling M/M/c consolidation (server count, not service variance).

# Probe report — VERDICT 162 · coordinated omission (P149 → V162, +13)

**Verdict: APPROVE** (exact reproduction, clean) — byte-identical verifier copy (`diff` exit 0) + exact digest reproduction across a cross-invocation double-run, the script's in-process double-run assert, and the byte-identical copy + all three gates PASS in order G1 → G2 → G3, exit 0. Clean (not QUALIFIED like V159): the proposal's declared model choices are conservative-DIRECTION only — none flips a gate SIGN or the order-of-magnitude — so there is no regime-dependent headline to bound. Both loops run on the byte-identical server, stall schedule, and per-replicate service-time list; only the pacing differs, so the ~104× reported-tail gap is attributable to the MEASUREMENT METHOD alone. Born-red card flip is the deliberate LAST commit releasing the substrate-gate HOLD; landing via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/fleet/coordinated_omission.py` at `d615489` (PROPOSAL 149, round-35 FLEET slot, landed via idea-engine #602). Permalink: https://github.com/menno420/idea-engine/blob/d615489/ideas/fleet/coordinated_omission.py — blob at that commit `d276fb5047473a5bc569f8747c1dd7a04311bbc5` (verified `git rev-parse d615489:ideas/fleet/coordinated_omission.py`).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/coordinated_omission.py` — `diff` exit **0**, file sha256 `6780d06a213ad27d218331447bb922898a1eb8aa716396bf343590c16eda762c`, git blob `d276fb5047473a5bc569f8747c1dd7a04311bbc5`, **12310** bytes, 323 lines. Stdlib-only (hashlib, json, math, random); no numpy/scipy.
- Pinned world: **SEED=20260717**, R=200 replicates (replicate i seeded `random.Random(SEED+i)`), λ=1000 → τ=1 ms, horizon T=1.0 s, base service Exp(mean μ_s=0.1 ms) utilisation μ_s/τ=0.1, n_stalls=6 stalls of D=50 ms (D/τ=50) at per-replicate non-overlapping cell offsets shared by both loops, N_svc=12000 pre-drawn service times, q=0.99 nearest-rank, z_gate=3.0. Server FROZEN during each stall; both loops consume the SAME per-replicate service-time list.
- Method: one FIFO server measured two ways over identical inputs — OPEN-LOOP (arrivals at fixed k·τ, FIFO, latency = completion − arrival) vs CLOSED-LOOP (one outstanding, dispatch_{i+1}=completion_i, latency = completion − dispatch); CO-CORRECTION back-fills each closed sample L>τ with L−τ, L−2τ, … down to >τ (HdrHistogram `recordValueWithExpectedInterval`). Per replicate: p99 of {open, closed, corrected} + stall-overlap counts; z = mean/se across replicates vs H0 mean 0.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — results dict carries NO `results_sha256` field; `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, asserts an in-process double-run byte-identity, prints the gate lines + pretty `json.dumps(indent=2)` dump + `Results-JSON sha256` line, writes NO file; floats rounded 6 dp. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P149 outbox done-when line) | `12d3ce4fce9a4f1cc218be0ee6f5dbc945d42a5e45173a46044704524dbfab5d` |
| cross-invocation A (committed `run-stdout.txt`) | `12d3ce4fce9a4f1cc218be0ee6f5dbc945d42a5e45173a46044704524dbfab5d` |
| cross-invocation B (fresh `python3`) | `12d3ce4fce9a4f1cc218be0ee6f5dbc945d42a5e45173a46044704524dbfab5d` |
| byte-identical copy | `12d3ce4fce9a4f1cc218be0ee6f5dbc945d42a5e45173a46044704524dbfab5d` |
| in-process double-run assert (script's own) | PASS (digest == digest2) |

**All reproduced digests == the disclosed digest EXACTLY** (all 64 hex). all_pass=**true**, first_failing_gate=**null**, exit **0** on every invocation; stdout byte-identical across fresh invocations (`cmp` exit 0). The pretty indent=2 stdout dump is a distinct serialization of the same dict; the digest preimage is the compact-canonical form.

## Gates (disclosed → reproduced), order G1 → G2 → G3
| gate | criterion | disclosed | reproduced | result |
|---|---|---|---|---|
| **G1** tail-blindness | mean log(open_p99/closed_p99), z ≥ 3 one-sided | mean **+4.643332** se **0.001853** z **+2505.733369** | identical to the digit | **PASS** |
| **G2** omitted-backlog | mean(open−closed stall count), z ≥ 3 one-sided | mean **+294.635** se **0.05723** z **+5148.278412** | identical to the digit | **PASS** |
| **G3** correction-recovery | mean log(corrected_p99/closed_p99), z ≥ 3 one-sided | mean **+4.408601** se **0.001691** z **+2606.670555** | identical to the digit | **PASS** |

First-failing gate: **none**. Order G1 → G2 → G3 held; every disclosed statistic reproduced to the digit.

## Descriptive (all match disclosed exactly)
- mean_open_p99 = **0.048583** s, mean_closed_p99 = **0.000468** s → mean_open_over_closed_p99 = **103.855766** (~104× understatement from pacing alone).
- mean_open_stall_count = **300.635** vs mean_closed_stall_count = **6.0** → excess **294.635** (≈ 6 stalls × ~50 = D/τ coordinated backlog omitted by the closed loop).
- mean_corrected_p99 = **0.03842** s → mean_recovery_fraction = **0.788774** (the HdrHistogram back-fill recovers ~79% of the closed→open p99 gap).
- Params reproduced: seed **20260717**, replicates **200**, lam **1000.0**, tau **0.001**, horizon_T **1.0**, mu_service **0.0001**, utilisation **0.1**, stall_D **0.05**, n_stalls **6**, D_over_tau **50.0**, n_svc **12000**, percentile_q **0.99**, z_gate **3.0**; all_pass **true**, first_failing_gate **null**, exit **0**.

## Why APPROVE (clean), not QUALIFIED
The proposal's Model basis declares three choices — "flagged not hidden," its words — and each is CONSERVATIVE-DIRECTION: (i) the server is FROZEN for a fixed stall D (the classic GC/safepoint/failover pause); relaxing to a load-dependent slowdown only ENLARGES the open-loop backlog, deepening the understatement — the closed-loop bias is a floor, not a fragile point estimate. (ii) Base service is Exp(μ_s) at low utilisation so the between-stall path is fast and the closed loop's few inflated samples sit ABOVE its own p99 (which is why the closed p99 is blind); at higher utilisation the closed baseline rises but the open-vs-closed p99 gap persists as long as D ≫ τ. (iii) The CO-correction uses expected-interval τ=1/λ, exactly HdrHistogram's `recordValueWithExpectedInterval`; the recovery fraction (~0.79) is descriptive, not gated — G3 only asserts the correction lifts the tail significantly, which holds for any D ≫ τ. None of the three flips a gate SIGN or the order-of-magnitude — contrast V159, where the G2 autocorrelation SIGN inverted between accelerator and ratchet regimes and the verifier shipped no control world, earning the QUALIFIED downgrade. Here every gate is a definitional contrast on the byte-identical server / stall schedule / service-time list, so the ~104× tail understatement rests on the load generator's PACING alone. No headline is regime-contingent → clean APPROVE.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = any operator who reads a p99/p99.9 off a synchronous / closed-loop latency harness (JMeter/wrk/ab-style benchmarks, database-driver latency tests, RPC dashboards, browser synthetic monitors, and — for the fleet — task-completion / CI-step / tool-call / agent-loop latency timers). The transferable correction: **a closed-loop / synchronous load generator CANNOT measure the tail it stalls in — during any stall it has one request outstanding and omits the ~D/τ coordinated backlog, so its reported p99 is set by the MEASUREMENT METHOD, not the system, and understates the truth by orders of magnitude (here ~104×).** To act on it: drive load OPEN-LOOP / constant-arrival (decouple issue time from completion time), OR apply an HdrHistogram-style coordinated-omission correction (`recordValueWithExpectedInterval`) to the recorded samples — either restores the tail; a bigger sample count or more warm-up does NOT. Reference: Gil Tene, "How NOT to Measure Latency" / HdrHistogram. DISTINCT from the V158 cache-stampede closed-form APPROVE (a real origin-herd law): this head is a MEASUREMENT artifact about the load generator, not a property of the system under test.

# Probe report — VERDICT 166 · Kleinrock's conservation law: scheduling a single-server fleet queue is zero-sum (P153 → V166, +13)

**Verdict: APPROVE** (exact reproduction, clean) — byte-identical verifier copy (`diff` exit 0), exact results-dict digest reproduction across a cross-invocation double-run (`diff` exit 0), the script's own in-process double-run assert (`results == again`, PASS), and an independent in-process import-and-rehash. All three gates PASS in order G1 → G2 → G3, `all_pass=true`, `first_failing_gate=null`, exit 0. Clean: the head claim (single-server M/G/1, two job classes, `sum_i rho_i W_i` invariant across FIFO / priority-to-short / priority-to-long) reproduces to the digit; the three disciplines are scored on the SAME arrival+service realization per replication (common random numbers, one `random.Random(SEED+r)` stream per rep), so the wait swing is attributable to the DISCIPLINE alone, not to differences in the work sampled.

Source: idea-engine `ideas/fleet/kleinrock_conservation_zero_sum.py` at commit `96e048c` (PROPOSAL 153, round-36 FLEET slot, landed via idea-engine #613). Blob at that commit `a9280c5519b1cca8308dc5652d5398028e495dfb` (verified `git rev-parse 96e048c:ideas/fleet/kleinrock_conservation_zero_sum.py` == the committed copy's blob).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/kleinrock_conservation_zero_sum.py` — `diff` exit **0**, file sha256 `72f740652714e76c4e9c83ed9844d66fa6dc8a41370d66e73f9a6a1e462faafb`, git blob `a9280c5519b1cca8308dc5652d5398028e495dfb`, **10107** bytes, 295 lines. Stdlib-only (hashlib, json, math, random, collections.deque); no numpy/scipy.
- Pinned world: **SEED=20260717**. Base two-class M/G/1 dispatch queue — short-job mean service S1=**1.0**, long-job mean service S2=**8.0**, short-job arrival fraction P1=**0.8**, target utilization RHO=**0.85**, N_JOBS=**20000** per replication, WARMUP=**4000** discarded completions, R_REPS=**30** independent replications. Derived loads: lam=**0.354167**, rho1=**0.283333**, rho2=**0.566667**. Shifted (robustness) config — P1_SHIFT=**0.6**, S2_SHIFT=**6.0**, RHO_SHIFT=**0.80** (S1_SHIFT=1.0), seeded `SEED+100000`. Conservation-leak ceiling G2_MAX_LEAK=**0.10**, SIGMA=**3.0**. FIFO, PRIO_SHORT and PRIO_LONG are all evaluated on the SAME `gen_jobs` realization each replication.
- Method: a discrete-event single non-preemptive work-conserving server, run on each discipline over identical common-random-number arrival+service streams. `transfer_short = rho1*(W1_fifo − W1_short)` (rho-weighted wait short jobs SAVE under priority-to-short); `transfer_long = rho2*(W2_short − W2_fifo)` (rho-weighted wait long jobs PAY). Kleinrock's law makes these two equal, so the leak `|transfer_short − transfer_long| / transfer_short → 0`. Gates: one-sample z, z=(mean−h0)/(sd/sqrt(n)); G1 h0=0 (transfer sign/magnitude), G2/G3 h0=0.10 (leak below the ceiling, z sign flipped so "below ceiling" reads positive), z_gate=3.0, require z≥3.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries NO `results_sha256` field; `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, builds a SECOND independent results dict via a second `run()` and asserts `results == again` (in-process double-run byte-identity), prints the gate lines + the pretty `json.dumps(results, indent=2, sort_keys=True)` dump + the `Results-JSON sha256` line, writes NO file; floats rounded 6 dp. The disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (VERDICT 166 done-when line) | `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18` |
| cross-invocation A (committed `run-stdout.txt`) | `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18` |
| cross-invocation B (fresh `python3`) | `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18` |
| in-process double-run assert (script's own `results == again`) | PASS |
| in-process import + rehash (independent, `run()` twice in ONE process) | `1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18` (both runs, equal) |

**All reproduced digests == the disclosed digest EXACTLY** (all 64 hex). `all_pass=`**true**, `first_failing_gate=`**null**, exit **0** on every invocation; stdout byte-identical across the two fresh cross-invocations (`diff` exit 0). The pretty indent=2 stdout dump is a distinct serialization of the same dict; the digest preimage is the compact-canonical form.

## Gates (disclosed → reproduced), order G1 → G2 → G3
| gate | criterion | reproduced | result |
|---|---|---|---|
| **G1** swing is real | `transfer_short_mean > 0`, z ≥ 3 vs 0 | transfer_short_mean **+7.450148**  z **+30.100904** | **PASS** |
| **G2** conservation | leak_mean **< 0.10**, z ≥ 3 below the 0.10 ceiling | leak_mean **0.040689**  z **+12.680569** | **PASS** |
| **G3** robustness | shifted-mix leak **< 0.10**, z ≥ 3 below the 0.10 ceiling | shift_leak_mean **0.023037**  z **+23.740077** | **PASS** |

First-failing gate: **none**. Order G1 → G2 → G3 held. G3 re-runs the leak gate on a SHIFTED class mix + utilization (P1 0.8→0.6, S2 8.0→6.0, RHO 0.85→0.80) — a materially different queue — and the conservation leak stays well below the ceiling (0.023 at ~23.7σ).

## Descriptive (observed this run)
- Short-job swing under priority-to-short: `W1_fifo=`**33.088966** → `W1_prio_short=`**6.794325** — short jobs jump the queue and their mean wait collapses ~4.9×.
- Long-job payback under priority-to-short: `W2_fifo=`**33.186088** → `W2_prio_short=`**46.364871** — long jobs pay the rho-weighted saving back. (The long-job mean wait under the PRIO_LONG discipline is computed internally — `simulate(jobs, "PRIO_LONG")`, line 177 — but is NOT surfaced as a scalar in stdout; the PRIO_LONG discipline is observable only through its conserved sum below. So the "long-job under FIFO vs priority-long" scalar contrast is not emitted; the FIFO long-job wait is `W2_fifo=`33.186088.)
- Conserved load-weighted-wait sum `sum_i rho_i W_i` across the three disciplines: FIFO=**28.180657**, priority-short=**28.198485**, priority-long=**28.177276**. Spread max−min = 0.021209 = **0.075%** of the ~28.185 mean — invariant to well within a tenth of a percent across three structurally different disciplines. This is the conservation law in the raw numbers: reordering WHO waits (short W1 33.09→6.79, long W2 33.19→46.36) leaves the rho-weighted aggregate essentially fixed.
- Params reproduced: seed **20260717**, n_jobs **20000**, warmup **4000**, reps **30**, s1 **1.0** / s2 **8.0**, p1 **0.8**, rho **0.85**, lam **0.354167**, rho1 **0.283333** / rho2 **0.566667**; shift p1 **0.6** / s2 **6.0** / rho **0.80**; g1_swing_real **true**, g2_conservation **true**, g3_robust **true**, all_pass **true**, first_failing_gate **null**, exit **0**.

## Probe questions — answered
**1. Verifier byte-match (sha256 / blob / diff exit 0)?** YES. `diff idea-engine/ideas/fleet/kleinrock_conservation_zero_sum.py sims/verdict-166-kleinrock-conservation/kleinrock_conservation_zero_sum.py` exit **0**; file sha256 `72f740652714e76c4e9c83ed9844d66fa6dc8a41370d66e73f9a6a1e462faafb`, git blob `a9280c5519b1cca8308dc5652d5398028e495dfb`, **10107** bytes, 295 lines — sha256 and blob match the disclosed expectations, and the blob equals `git rev-parse 96e048c:ideas/fleet/kleinrock_conservation_zero_sum.py` (the pinned P153 source). Plain `cp`, no edits.

**2. In-process double-run identical AND cross-invocation stdout byte-identical?** YES on both. The script's own `main()` asserts `results == again` (a second full `run()`) and the assert did NOT fire — exit 0. A fresh second `python3` invocation to a temp file `diff`'d against the committed `run-stdout.txt` exit **0** (byte-identical across invocations; temp file discarded). An independent in-process import ran `run()` twice in ONE process — both dicts equal and both rehash to the disclosed digest.

**3. Results-dict sha256 == disclosed `1b40af51…3153ee18`?** YES — **MATCH**, exactly (all 64 hex). Printed `Results-JSON sha256: 1b40af51baa24c2041bbd822b190e5447c6299840604822580b3b3bb3153ee18` == disclosed, reproduced across cross-invocation A (committed stdout), fresh invocation B, and independent in-process rehash. Computed over the compact-canonical serialization, not the pretty indent=2 dump.

**4. G1 — `transfer_short_mean > 0` at z ≥ 3?** YES. transfer_short_mean **+7.450148** at z **+30.100904** (≫ 3σ vs 0) — priority-to-short genuinely moves a large, rho-weighted amount of wait; the swing is real, not noise. `g1_swing_real=true`.

**5. G2 — `leak_mean < 0.10` at z ≥ 3 below the ceiling?** YES. leak_mean **0.040689** (~4.1% residual) at z **+12.680569** below the 0.10 ceiling — the rho-weighted saving short jobs gain is paid back by long jobs to within ~4%, well inside the conservation ceiling. `g2_conservation=true`.

**6. G3 — shifted-mix leak < 0.10 at z ≥ 3, and conserved sum ~28.18 across the three disciplines (actual spread %)?** YES on both counts. Under the shifted class mix + utilization (P1 0.6, S2 6.0, RHO 0.80) the leak is shift_leak_mean **0.023037** (~2.3%) at z **+23.740077** below the 0.10 ceiling — robustness holds. The base conserved load-weighted-wait sum is FIFO **28.180657**, priority-short **28.198485**, priority-long **28.177276** — all ~**28.18**, actual spread (max−min)/mean = **0.075%**. `g3_robust=true`.

## Why APPROVE (clean)
All three gates pass in order (G1 +30.1σ, G2 +12.7σ, G3 +23.7σ), `all_pass=true`, `first_failing_gate=null`, exit 0; the results-dict digest matches the disclosed value exactly; determinism holds three ways (script's own `results == again` assert, byte-identical stdout across fresh invocations, and an independent in-process rehash). The head claim is a definitional conservation contrast on the SAME common-random-number work per replication, so the collapse of short-job wait (33.09→6.79), the offsetting long-job payback (33.19→46.36), and the near-invariant load-weighted aggregate (28.18 ± 0.075%) rest on the scheduling DISCIPLINE alone. Nothing in the run reads as regime-contingent or self-referential. APPROVE conditions — all three gates PASS AND digest MATCH AND determinism holds — are all met.

Recommendation: APPROVE

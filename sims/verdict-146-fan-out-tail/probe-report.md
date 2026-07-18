# Probe report — VERDICT 146 · fan-out tail amplification (P133 → V146, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/fleet/fan_out_tail_amplification.py` at `12bd4ec` (PROPOSAL 133, round-31 FLEET slot).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/fan_out_tail_amplification.py` — `diff` exit **0**, file sha256 `8f971ee0bb9a612b01ba85a6a5acfea0015d8f7c079c5fc0299a3e18435d3c7e`, git blob `021a63b372008055ac1e18c666a1b6915bb048ea`, **136** lines / **4237** bytes. Permalink: https://github.com/menno420/idea-engine/blob/12bd4eccf88acba8c5977f013f80d67eba9cdd25/ideas/fleet/fan_out_tail_amplification.py
- Pinned world: **SEED=20260717**, TRIALS=**120000**, P_LEAF=**0.01**, N_GRID=(**10, 69, 100, 200**), Z_GATE=**3.0**. Stdlib-only (hashlib, json, math, random); no numpy/scipy; Python 3.11.15. `run()` builds one `random.Random(SEED)` stream and, for each N in N_GRID in fixed order, draws N Bernoulli(p) leaf outcomes per trial over TRIALS trials, recording the fraction of requests with ≥1 slow leaf and the mean slow-leaf count; it then evaluates the three z-gates against the closed forms P_slow(N)=1−(1−p)^N (binomial se) and mean slow leaves = N·p (se from Binomial variance N·p(1−p)). Gate z-scores are on the ESTIMATED statistic via its standard error — the P104..V147 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 126–132 in the script text, not assumed. The computation lives in `run()` (returns the results dict), so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P133 outbox / verifier `Results-JSON sha256:` line) | `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` |
| cross-invocation B (fresh `python3`) | `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced the identical results dict AND identical digest run-to-run (`run()` #1 == `run()` #2 as dicts). Independent recompute confirms the WHOLE-DICT posture (the dict carries no `results_sha256` field) and that re-parsing the pretty stdout dump → compact re-serialize → sha256 reproduces the same digest.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** union-bound tail (\|z\| < 3σ vs P_slow(100)=1−0.99^100) | z **−0.336** | p_slow_hat **0.6335** vs exact **0.633968**, z **−0.3362996260670384**, \|z\| < 3.0 | **PASS** |
| **G2** median crossover (N*=69 bracketed, \|z\| < 3σ vs P_slow(69)) | z **−0.015**, N*=**69** | n_star **69**, bracket **True**, root **68.96756393652842**, p_slow_hat **0.5001416666666667** vs exact **0.500162970100801**, z **−0.014759452902530413** | **PASS** |
| **G3** mean-slow-leaves linear (\|z\| < 3σ vs N·p=1.0 at N=100) | z **+0.055** | mean_slow_leaves_hat **1.0001583333333333** vs exact **1.0**, z **+0.05512459105261225**, \|z\| < 3.0 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- **Closed forms:** P_slow(N)=1−(1−p)^N; crossover N*=ceil(ln2/(−ln(1−p))) refined to the smallest integer with P_slow(N)≥0.5 — real-valued root ln2/(−ln0.99)=**68.96756393652842**, n_star=**69** (bracket P_slow(68)=**0.496660**<0.5≤P_slow(69)=**0.500163**); mean slow leaves = N·p (linear).
- **G1 (union-bound tail, headline):** MC slow fraction at N=100 = **0.6335** vs exact P_slow(100)=1−0.99^100=**0.6339676587267709**, z = (p_hat−p0)/√(p0(1−p0)/T) = **−0.3362996260670384**, |z| < 3σ — the whole-request slow rate lands on the exact union closed form; a 1% per-leaf tail becomes a 63.4% request tail at N=100.
- **G2 (median crossover):** n_star=**69** is the smallest N with P_slow(N)≥0.5 (bracket=**True**), matching the analytic median N*=ln2/(−ln0.99)=**68.967564**; MC slow fraction at N*=69 = **0.5001416666666667** vs exact **0.500162970100801**, z = **−0.014759452902530413**, |z| < 3σ — the median request is slow at a ~69-way fan-out, not at the naive N≈1/p=100.
- **G3 (mean-slow-leaves linear):** MC mean slow leaves at N=100 = **1.0001583333333333** vs exact N·p=**1.0**, z = (mean_hat−mean0)/√(Np(1−p)/T) = **+0.05512459105261225**, |z| < 3σ — the AVERAGE slow-leaf count is merely linear (~1 leaf), decisively separated from the 63.4% request tail: the tail is amplified by the union over leaves, not by the mean.
- **Per-N table (exact / MC):** N=10 → P_slow 0.095618 / 0.0959, mean 0.1 / 0.1002; N=69 → P_slow 0.500163 / 0.500142, mean 0.69 / 0.688133; N=100 → P_slow 0.633968 / 0.6335, mean 1.0 / 1.000158; N=200 → P_slow 0.866020 / 0.866742, mean 2.0 / 2.003908.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/fleet/fan_out_tail_amplification.py \
   sims/verdict-146-fan-out-tail/fan_out_tail_amplification.py
diff idea-engine/ideas/fleet/fan_out_tail_amplification.py \
     sims/verdict-146-fan-out-tail/fan_out_tail_amplification.py    # exit 0
sha256sum <both>   # 8f971ee0bb9a612b01ba85a6a5acfea0015d8f7c079c5fc0299a3e18435d3c7e (both)

# cross-invocation A/B (fresh processes)
python3 fan_out_tail_amplification.py > run-stdout.txt       # exit 0
python3 fan_out_tail_amplification.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d

# in-process double-run + independent compact-digest recompute
python3 -c "run() x2; sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs 4b3de50…131c42d == disclosed; dict identical run-to-run
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, sha256 `8f971ee0…d3c7e`), the results-dict sha256 reproduces the disclosed digest `4b3de5012a6cedc99de8e446c3fdd0aa79b1988fd0594c3cbb9e33702131c42d` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The claim holds: an all-of-N scatter-gather inherits the union tail P_slow(N)=1−(1−p)^N, so a 1%-per-leaf tail makes the median of a ~69-way fan-out slow while the mean slow-leaf count stays linear at N·p. The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.

# Probe report — VERDICT 147 · cohort-blended LTV understatement (P134 → V147, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/venture-lab/blended_churn_ltv_understatement.py` at `12bd4ec` (PROPOSAL 134, round-31 VENTURE slot).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/venture-lab/blended_churn_ltv_understatement.py` — `diff` exit **0**, file sha256 `85a4bc96b61b49a59be82524f572cbafd57b385ece59805924d817458f6d0c38`, git blob `b481160ff856517e194dda73b323fd90711992f8`, **197** lines / **7302** bytes. Permalink: https://github.com/menno420/idea-engine/blob/12bd4eccf88acba8c5977f013f80d67eba9cdd25/ideas/venture-lab/blended_churn_ltv_understatement.py
- Pinned world: **SEED=20260717**, TRIALS=**200000**, SIGMA=**3.0**, margin m=**1.0**, WIDE churn band c ~ U[**0.05, 0.35**] (retention 65%–95%, mean churn 0.20), NARROW churn band c ~ U[**0.19, 0.21**] (same mean churn 0.20, tiny spread). Stdlib-only (random, math, json, hashlib); no numpy/scipy. `run()` seeds `random.seed(SEED)` once on a single stream, draws `random.uniform` per trial into the WIDE band then the NARROW band in fixed order, records per-trial LTV = m/c and the gap LTV − naive, and evaluates the three z-gates against the closed forms E[m/c]=m(ln b − ln a)/(b − a) and naive m/E[c]=2m/(a+b). Gate z-scores are on the ESTIMATED statistic via its standard error (se = sample-sd/√TRIALS for the mean; pooled se for the wide−narrow difference), the P104..P131 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 174–194 in the script text, not assumed. The computation lives in `run()` (returns the results dict), so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P134 outbox / verifier `Results-JSON sha256:` line) | `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` |
| cross-invocation B (fresh `python3`) | `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced the identical results dict AND identical digest run-to-run (`run()` #1 == `run()` #2 as dicts).

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** understatement bias (WIDE gap > 0 at ≥3σ) | z **171.221384** | wide_gap_mean **1.489529** > 0, z **171.221384** ≥ 3.0 | **PASS** |
| **G2** matches closed form (\|z\| < 3σ vs E[m/c]=6.486367) | z **0.363449** | wide_ltv_mean **6.489529** vs exact **6.486367**, z **0.363449**, \|z\| < 3.0 | **PASS** |
| **G3** dispersion-driven (WIDE − NARROW gap > 0 at ≥3σ, narrow gap < 0.05) | z **170.572090**, narrow gap **0.004628** | gap_diff **1.484901** > 0, z **170.57209** ≥ 3.0, narrow_gap_mean **0.004628** < 0.05 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- **Closed forms:** exact true LTV wide E[m/c]=m(ln b − ln a)/(b − a)=ln(7)/0.30=**6.486367**; naive blended LTV wide m/E[c]=2m/(a+b)=**5.000000**; exact gap wide **1.486367**; second-order gap wide 2(b−a)²/[3(a+b)³]=**0.937500**. Narrow band (same mean churn 0.20): exact true LTV narrow **5.004173**, naive **5.000000**, exact gap narrow **0.004173**.
- **G1 (understatement bias, headline):** MC WIDE gap mean = **1.489529** > 0 (wide_ltv_mean **6.489529**), z = wide_gap_mean/se = **171.221384** ≥ 3σ — the blended-churn LTV strictly understates the per-customer average LTV; the understatement bias is real and massively separated from zero.
- **G2 (matches closed form):** MC WIDE mean LTV = **6.489529** vs the EXACT closed form E[m/c] = ln(7)/0.30 = **6.486367**, z = **0.363449**, |z| < 3σ — the simulator reproduces the exact convex-mean anchor (a no-significant-deviation bracket gate), so the ~30% understatement (5.0 vs 6.486367) is the true Jensen gap, not a sampling artifact.
- **G3 (dispersion-driven):** WIDE gap **1.489529** − NARROW gap **0.004628** = gap_diff **1.484901** > 0, z (pooled se) = **170.572090** ≥ 3σ, and the NARROW-band gap **0.004628** < 0.05 (negligible). Holding mean churn fixed at 0.20 and collapsing the spread from [0.05,0.35] to [0.19,0.21] collapses the understatement from 1.49 to ~0.005 — the gap is driven by churn DISPERSION, not level, as the second-order term m·Var(c)/c̄³ predicts.

> NOTE on the narrow-band gap: the exact closed-form narrow gap is **0.004173** (deterministic), while the MC narrow_gap_mean is **0.004628** — both ≪ 0.05, both confirm the near-vanishing narrow-band understatement; the MC value **0.004628** is the one baked into the authoritative digest and reproduced bit-for-bit.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/venture-lab/blended_churn_ltv_understatement.py \
   sims/verdict-147-cohort-ltv-understatement/blended_churn_ltv_understatement.py
diff idea-engine/ideas/venture-lab/blended_churn_ltv_understatement.py \
     sims/verdict-147-cohort-ltv-understatement/blended_churn_ltv_understatement.py   # exit 0
sha256sum <both>   # 85a4bc96b61b49a59be82524f572cbafd57b385ece59805924d817458f6d0c38 (both)

# cross-invocation A/B (fresh processes)
python3 blended_churn_ltv_understatement.py > run-stdout.txt       # exit 0
python3 blended_churn_ltv_understatement.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b

# in-process double-run + independent compact-digest recompute
python3 -c "run() x2; sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs f45e6609…f489b == disclosed; dict identical run-to-run
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, sha256 `85a4bc96…d0c38`), the results-dict sha256 reproduces the disclosed digest `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The claim holds: blended-churn LTV = m/c̄ understates true E[m/c] by ~30% on the wide band (5.0 vs 6.486367), driven by dispersion (narrow-band gap collapses to 0.004628). The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.

# Probe report — VERDICT 143 · the annual-prepay financing trap (P130 → V143, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/venture-lab/annual_prepay_financing_trap.py` at main `e8c0193` (PROPOSAL 130).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/venture-lab/annual_prepay_financing_trap.py` — `diff` exit **0**, file sha256 `ef7b1bd46b2d48c8a0fb0cbe6324363f26666427d93ff9f86799c4542ae686fb`, git blob `576d5beec53a8e820345f6a388775d0555d1ee81`, **307** lines / **14624** bytes. Permalink: https://github.com/menno420/idea-engine/blob/e8c019308c77396e51aaea9ff398c77bf8b065f5/ideas/venture-lab/annual_prepay_financing_trap.py
- Pinned world: **SEED=20260717**, TRIALS=**400**, SIGMA=**3.0**, N_CUSTOMERS=**8000**, MONTHS=**12**, DISCOUNT=**1/6** (0.166667), R_TRUE_MONTHLY=**0.01**, SHAPE=**64.0**, MSPEND0=**100.0**, APR_GAP_MIN=**0.15**, NPV_GAP_MIN=**0.03**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Per-customer independent cost of capital r_i=R_TRUE·Gamma(SHAPE,1/SHAPE) (unit-mean, CV=1/√SHAPE=12.5%) and monthly spend m_i~Uniform[0,2·MSPEND0] drawn INDEPENDENTLY of r_i; r* by bisection on S(r)=12(1−d). Gate z-scores are on the ESTIMATED MEAN via its standard error (se=std/√TRIALS), the P104..P129 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 282–303 in the script text, not assumed. The computation lives in `run()` (returns the results dict), so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P130 outbox / verifier `Results-JSON sha256:` line) | `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` |
| cross-invocation B (fresh `python3`) | `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** implied-financing-rate (mean(APR_implied−APR_true)≥0.15, z≥3) | mean **0.384680**, z **24078.7034** | mean **0.384680**, z **24078.7034** | **PASS** |
| **G2** deadweight-NPV control (mean NPV gap≥0.03, z≥3, sign_block) | mean **0.114002**, z **22938.9668**, sign_block True | mean **0.114002**, z **22938.9668**, sign_block True | **PASS** |
| **G3** IRR/break-even-discount anchor (\|z\|<3, apr_anchor_ok, irr_unique) | ratio_dev **−0.000000**, \|z\| **0.0031**, both True | ratio_dev **−0.000000**, \|z\| **0.0031**, both True | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Closed-form: annual_multiple=12(1−d)=**10.0** months; r*=**0.035032**/mo; APR_implied=(1+r*)^12−1=**0.511621**; S(0.01)=pv_multiple_at_r_true=**11.367628** months; APR_true=**0.126825**; fair d*=1−S(r_true)/12=**0.052698**; over_discount_ratio d/d*=**3.162697×**.
- G1 (implied-financing-rate, headline): mean(APR_implied − APR_true_i)=**0.384680** ≥ 0.15, z=**24078.7034σ** — the annual-prepay discount is implicit borrowing at an APR (0.511621) far above the firm's real cost of capital (0.126825).
- G2 (deadweight-NPV control): mean NPV gap per $ of annual list=**0.114002** ≥ 0.03, z=**22938.9668σ**, with the four-part sign block — NPV_annual **0.833333** < NPV_monthly **0.947335** (per $ monthly list), APR_implied **0.511621** > APR_true **0.126825**, offered d **0.166667** > fair d* (sampled d_star_mean) **0.052665**, cash pulled forward 12(1−d)=10.0 < 12 — sign_block=**True**. At the real cost of capital the discounted annual deal destroys ~11.40% of contract value vs monthly billing.
- G3 (IRR/break-even-discount anchor): dollar-weighted PV multiple − count-mean PV multiple = **−0.000000**, |z|=**0.0031** < 3 (spend-independence: ticket size m_i and capital cost r_i drawn independently ⇒ the discount identity is spend-independent, mean-zero), apr_anchor_matches_analytic_irr=**True** (|APR_implied−IRR|<1e-9), irr_unique_sign_change=**True** (the incremental cash flow [12(1−d)−1, −1,…,−1] changes sign exactly once on a 20000-point grid ⇒ IRR well-defined, Descartes/Norström).

## Reproduction commands (verbatim)
```
# byte-identical copy
diff idea-engine/ideas/venture-lab/annual_prepay_financing_trap.py \
     sims/verdict-143-annual-prepay-trap/annual_prepay_financing_trap.py   # exit 0
sha256sum <both>   # ef7b1bd46b2d48c8a0fb0cbe6324363f26666427d93ff9f86799c4542ae686fb (both)

# cross-invocation A/B (fresh processes)
python3 annual_prepay_financing_trap.py > run-stdout.txt      # exit 0
python3 annual_prepay_financing_trap.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b

# in-process double-run + independent compact-digest recompute
python3 -c "import run() x2, sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs cf0d9e72…cae7b == disclosed
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0), the results-dict sha256 reproduces the disclosed digest `cf0d9e72622af9a3d595f687855624ce92ad426ec4c8f640940000e07afcae7b` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3. The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.

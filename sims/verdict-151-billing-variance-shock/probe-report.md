# Probe report — VERDICT 151 · usage-based billing variance shock (P138 → V151, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/venture-lab/usage_based_billing_variance_shock.py` at `c02df30` (PROPOSAL 138, round-32 VENTURE slot, landed via idea-engine #578). Permalink: https://github.com/menno420/idea-engine/blob/c02df30ad80e69f1b300d471f51a7ce7c4c8f687/ideas/venture-lab/usage_based_billing_variance_shock.py

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/venture-lab/usage_based_billing_variance_shock.py` — `diff` exit **0**, file sha256 `e9945e69f9cf89347f1ac55341f7428e2d4021d3e7c1b21fb9269f52c3160da1`, git blob `785588ff32930cd13b27f32223d8d519e0c360e2`, **230** lines / **9576** bytes.
- Pinned world: **SEED=20260717**, **N=400** accounts, **K_SHAPE=4.0** (so CV_account=1/√4=**0.5**), **N_BATCH=60**, **BATCH_MONTHS=250**, **SIGMA=3.0**. Concentrated book Zipf mᵢ=1/i (i=1..400); uniform control mᵢ=mean(concentrated) (SAME N, SAME total mean, SAME per-account CV). Stdlib-only (hashlib, json, math, random); no numpy/scipy.
- Method: each month draws N independent per-account usages Uᵢ~Gamma(K_SHAPE, mᵢ/K_SHAPE) (so E[Uᵢ]=mᵢ, CV(Uᵢ)=1/√K_SHAPE=0.5) and sums to monthly revenue R; a batch is BATCH_MONTHS months and yields one CV estimate = sample_sd/sample_mean of the monthly revenues. Because the sampling SE of a ratio estimator CV_hat=s/x̄ has no clean normal-theory form, the verifier uses **BATCH MEANS / the METHOD OF INDEPENDENT REPLICATIONS** — N_BATCH=60 independent batches, each one CV sample, drawn in fixed order (concentrated then uniform, batch by batch) from a single `random.seed(SEED)` stream; SE = sd(batch CVs)/√N_BATCH, distribution-free and valid.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the pretty `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization, NOT the pretty indent=2 dump printed on stdout — recompute over the compact form. The compute entry is `run()`, so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P138 outbox / verifier `Results-JSON sha256:` line) | `4cd2fd286d5530ce001dc49becb80c29ced6484b834e051be59ed2acbf7a7d6b` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `4cd2fd286d5530ce001dc49becb80c29ced6484b834e051be59ed2acbf7a7d6b` |
| cross-invocation B (fresh `python3`) | `4cd2fd286d5530ce001dc49becb80c29ced6484b834e051be59ed2acbf7a7d6b` |
| in-process run 1 (`run()` compact-hashed) | `4cd2fd286d5530ce001dc49becb80c29ced6484b834e051be59ed2acbf7a7d6b` |
| in-process run 2 (`run()` compact-hashed) | `4cd2fd286d5530ce001dc49becb80c29ced6484b834e051be59ed2acbf7a7d6b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across cross-invocation A/B (stdout diff exit **0**) and across the in-process double-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | criterion | disclosed | reproduced | result |
|---|---|---|---|---|
| **G1** diversification shortfall exists (conc CV > naive) | conc CV − naive > 0 AND z ≥ 3σ (one-sided /se) | z **+116.537** | conc CV **0.096707** vs naive **0.025000**, diff **0.071707**, z **+116.537002** | **PASS** |
| **G2** matches exact closed form CV_account·√HHI | \|z\| < 3σ bracket | z **−1.343** | conc CV **0.096707** vs exact **0.097533**, z **−1.343306**, \|z\| < 3.0 | **PASS** |
| **G3** concentration-driven (conc CV > unif CV; unif ≈ naive) | conc − unif > 0 AND z ≥ 3σ AND unif–naive gap < 0.01 | z **+113.523**, gap **5e-06** | conc CV **0.096707** vs unif **0.025005**, diff **0.071702**, z **+113.523243**, unif–naive gap **5e-06** < 0.01 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & closed forms (all match disclosed exactly)
- **Closed forms (no RNG, computed from the deterministic size vectors):** HHI_concentrated=**0.038051**, N_eff_concentrated=1/HHI=**26.280443**, CV(R)_exact_concentrated=CV_account·√HHI=**0.097533**, HHI_uniform=**0.0025** (=1/N=1/400 exactly, Cauchy–Schwarz equality case), CV_exact_uniform=**0.025000**, CV_naive_lln=CV_account/√N=**0.025000**, volatility_multiplier=CV(R)_exact/CV_naive=**3.901339**.
- **G1 (diversification shortfall exists):** the concentrated-book MC CV **0.096707** exceeds the naive LLN prediction **0.025000** by z=**+116.537** — the coefficient of variation does NOT fall like 1/√N; the folk smoothing never arrives because ~374 of the 400 accounts contribute negligibly to variance.
- **G2 (matches the exact closed form):** the concentrated-book MC CV **0.096707** lands on the exact Herfindahl prediction CV_account·√HHI=**0.097533** within z=**−1.343** (|z|<3σ) — the shortfall IS exactly √HHI, not a magnitude artifact.
- **G3 (concentration-driven):** with SAME N=400, SAME total mean revenue, SAME per-account CV=0.5, the uniform book's MC CV collapses to **0.025005** (matching naive 1/√N within gap **5e-06**) while the concentrated book stays at **0.096707** — z=**+113.523** separation, isolating size concentration (HHI) as the sole driver. The uniform book realizes HHI=1/N (Cauchy–Schwarz equality); Zipf heterogeneity raises HHI 15.2× so N_eff falls from 400 to 26.28.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = any operator / CFO / RevOps owner forecasting revenue or risk from a book of independent usage-priced (consumption / metered / pay-as-you-go) accounts — usage-based SaaS, cloud/API metered billing, transaction-fee marketplaces, any revenue = sum of many independent per-account draws. The transferable correction: **revenue volatility is set by the effective account count N_eff = 1/HHI, NOT the raw count N — under any size heterogeneity CV(R) = CV_account·√HHI ≥ CV_account/√N, so a book that "has hundreds of accounts" can be as volatile as one with a couple dozen.** A count-based dashboard ("N accounts, LLN smooths us") is BLIND to this: it sees the customer count, never the Herfindahl concentration. To act on it: compute HHI = Σ(share²) on revenue share (not the count), read N_eff = 1/HHI as the TRUE diversification, size cash buffers / covenants / forecasts against N_eff, and cut the tax by cutting concentration — cap single-account revenue share, diversify the size distribution, hedge the top accounts — because adding small accounts to a heavy-tailed book barely moves N_eff. DISTINCT from a correlation-driven variance floor (independent accounts here; the driver is size HETEROGENEITY / Herfindahl concentration, not covariance ρσ² on identical units) and from a Jensen convexity bias in a POINT estimate (this is a second-moment RISK result: the point mean E[R] is unbiased, only the dispersion is understated).

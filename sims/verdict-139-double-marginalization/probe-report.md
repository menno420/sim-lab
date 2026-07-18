# Probe report — VERDICT 139 · partner-channel margin stacking / double marginalization (P126 → V139, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `## PROPOSAL 126 · 2026-07-18T08:24:18Z · status: sim-ready`.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/venture-lab/partner_channel_margin_stacking.py` — `diff` exit **0**, git blob `147f842d0379d04bc690f9b356128fba9ded53ca`, file sha256 `926c1ac622979dc9824360d471b97614ceade9069f664530f3ea319b2b5f0c71`, **301** lines / **13271** bytes. Landed via idea-engine PR #552, main `2feefd9`.
- Pinned world: **SEED=20260717**, TRIALS=**400**, N_CONSUMERS=**8000**, VMAX0=**100.0**, COST=**20.0**, SHAPE=**64.0** (per-trial market-size multiplier VMAX_t=VMAX0·Gamma(SHAPE,1/SHAPE), unit mean, CV=1/√SHAPE=12.5%), SIGMA=**3.0**, PRICE_GAP_MIN=**5.0**, PROFIT_GAP_MIN=**1.0**. Stdlib-only (random, math, json, hashlib, bisect); no numpy/scipy. Per trial: draw the market-size multiplier → compute the closed-form successive-markup equilibria (P_int, w*, P_dec) → sample N_CONSUMERS willingness-to-pay ~ Uniform[0,VMAX_t], sort, realized demand D(p) by bisection, realized per-consumer profits π_int=(P_int−C)·D(P_int) and π_channel=(P_dec−C)·D(P_dec); a no-RNG fine-grid argmax at VMAX0 confirms the closed-form prices maximize true-demand profits so the two-stage equilibrium EMERGES. Gate z-scores are on the ESTIMATED MEAN via its standard error (se=std/√TRIALS).
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the P105/P109/P110/P114/P118/P122 family, DIFFERS from the V126/V138 SELF-FIELD/PRETTY-ON-DISK posture. `run()` returns a results dict that carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, and PRINTS `canonical` (stdout line 1) then `sha256: <digest>` (stdout line 2), plus the summary + 3 gate lines + `ALL_PASS: True`. It writes NO results file. The disclosed digest is thus the sha256 of the compact-canonical results dict exactly as printed on stdout line 1 — there is no on-disk json to reconcile. Classified against `main()` lines 278–297 in the script text, not assumed.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P126 outbox / verifier `sha256:` line) | `301d998e27bbaa8363526410d1a0e093de2993559de230f37c37792fef8bdd98` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `301d998e27bbaa8363526410d1a0e093de2993559de230f37c37792fef8bdd98` |
| cross-invocation B (fresh `python3`) | `301d998e27bbaa8363526410d1a0e093de2993559de230f37c37792fef8bdd98` |
| in-process double-run #1 (run(), hashed compact in-process) | `301d998e27bbaa8363526410d1a0e093de2993559de230f37c37792fef8bdd98` |
| in-process double-run #2 (run() again, hashed compact in-process) | `301d998e27bbaa8363526410d1a0e093de2993559de230f37c37792fef8bdd98` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** channel price inflation | mean(P_dec−P_int)=**20.008129** ≥ 5.0, z=**98.1336** (se **0.152936**) | mean **20.008129**, se **0.152936**, z **98.1336** | **PASS** |
| **G2** deadweight profit-destruction | mean(π_int−π_channel)=**3.994668** ≥ 1.0, z=**78.2751** (se **0.038258**), sign_block **True** | mean **3.994668**, se **0.038258**, z **78.2751**, sign_block **True** | **PASS** |
| **G3** double-marginalization anchor | profit-dev **0.009009** \|z\|=**0.7935** / quantity-dev **0.000147** \|z\|=**0.7888** < 3, grid_argmax_confirms **True** | profit-dev **0.009009** z **0.7935**, quantity-dev **0.000147** z **0.7888**, grid_argmax **True** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Closed form (successive-markup FOCs): P_int=(VMAX+C)/2=**60**, w*=(VMAX+C)/2=**60**, P_dec=(3·VMAX+C)/4=**80**; scale-free anchors π_channel/π_int=**3/4=0.75**, Q_dec/Q_int=**1/2=0.5**.
- Observed: P_int **60.016258** (se 0.305871), P_dec **80.024387** (se 0.458807), π_int **16.014708** (se 0.146592), π_channel **12.020041** (se 0.110641), Q_int **0.398369** (se 0.000662), Q_dec **0.199332** (se 0.000379); realized profit ratio **0.750563** (≈3/4), quantity ratio **0.500369** (≈1/2); grid_argmax_confirms_closed_form **True**.

**Headline:** adding an INDEPENDENT margin-setting channel partner is NOT "list price minus their cut". Two firms each applying a profit-maximizing markup in series STACK the markups (double marginalization) — the street price P_dec **80.024387** lands ABOVE the vertically-integrated monopoly price P_int **60.016258** by **20.008129** (**z=98.1σ**, G1), a ~33% retail inflation, and the combined channel profit π_channel **12.020041** falls strictly BELOW the integrated profit π_int **16.014708** by **3.994668** (**z=78.3σ**, G2, sign_block True) — vendor+partner COMBINED keep a SMALLER pie, at a higher price and lower quantity (Q_dec **0.199332** < Q_int **0.398369**): a deadweight loss, not a redistribution. The realized quantities reproduce the exact double-marginalization ratios (profit **0.750563**≈3/4, quantity **0.500369**≈1/2) within 3σ (|z_profit|=**0.7935**, |z_quantity|=**0.7888**, G3), and a fine-grid argmax confirms the closed-form prices are the true profit-maximizers (grid_argmax_confirms_closed_form=**True**) — the two-stage equilibrium EMERGES, byte-for-byte across cross-invocations and an in-process double-run. Operator lesson: evaluate a channel on the COMBINED-pie effect, and kill the second independent markup — a two-part tariff (wholesale AT COST + fixed franchise fee), a resale-price ceiling, a revenue-share that makes the partner price as if it owned the full margin, or vertical integration / agency pricing. Anchor: double marginalization (Cournot/Spengler), with vertical integration as the canonical cure. **APPROVE.**

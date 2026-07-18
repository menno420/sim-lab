# Probe report — VERDICT 136 · hard-close snipe clearing leak (P123 → V136, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS. Born-red card flip WITHHELD to the later landing stage (this seat reproduces and records the verdict; it does not self-land).

Source: idea-engine `## PROPOSAL 123 · 2026-07-18T07:20:34Z · status: sim-ready`.

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/snipe_clearing_leak.py` — `diff` exit **0**, git blob `a0d92cc0a2385538955950c29dae1968bf0a29b7`, file sha256 `85f489bfb6fdd7a7b18b2b6e8e51a96b36ef70a64cd7585cb98c904ed0872485`, **155** lines / **5663** bytes.
- Pinned world: **SEED=20260717**, TRIALS=**100000**, K=**8**, SIGMA_GATE=**3.0**, Q_STAR=**0.15**, Q_LO=**0.05**, Q_HI=**0.25**, Q_LEVELS=**[0.0, 0.05, 0.15, 0.25]** (0.0 first = placebo/specificity). Stdlib-only (random, math, json, hashlib); no numpy/scipy. Paired common-random-numbers: the same K valuation draws and the same K transmission draws feed every q level, coupling the estimators for a low-variance dose-response.
- DIGEST POSTURE: **NO-SELF-FIELD / COMPACT-STDOUT** — matches the V135 exemplar, DIFFERS from the V133/V134 SELF-FIELD/pretty-on-disk posture. `main()` computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode())` (L143–144), then prints the PRETTY dump `json.dumps(results, indent=2, sort_keys=True)` (L145), then `Results-JSON sha256: <digest>` (L146), then the 3 gate lines + `ALL_PASS: True`, and writes **no** results.json. The results-dict carries **no** `results_sha256` field.
- Reconciliation (honest): because the verifier writes no on-disk json, the committed `snipe_clearing_leak_results.json` here **IS** the exact compact canonical bytes that were hashed — `json.dumps(results, sort_keys=True, separators=(",",":"))`, stored with **no trailing newline** (528 bytes, last byte `}`). Re-hashing that file's content therefore reproduces the disclosed digest directly: `sha256(file) = 2344cfb8…c18e8`. ONE honest divergence from the V135 exemplar's on-disk convention: this verifier's STDOUT is PRETTY JSON (indent=2), not the compact canonical line, so `run-stdout.txt` is the pretty dump + `Results-JSON sha256:` line + 3 gate lines + `ALL_PASS: True` — the compact canonical bytes live only in the committed `snipe_clearing_leak_results.json`, which is what re-hashes to the digest. (V135's verifier printed compact-on-stdout; this one prints pretty-on-stdout but the digest is over the identical compact canonical, so the on-disk results.json convention — compact bytes, no trailing newline, re-hashes to the digest — is preserved exactly.)

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P123 outbox / verifier `Results-JSON sha256:`) | `2344cfb88d01022b4b6e3e119af4ce675b454e4ef6aa5e4465610600771c18e8` |
| cross-invocation A (fresh `python3`) | `2344cfb88d01022b4b6e3e119af4ce675b454e4ef6aa5e4465610600771c18e8` |
| cross-invocation B (fresh `python3`) | `2344cfb88d01022b4b6e3e119af4ce675b454e4ef6aa5e4465610600771c18e8` |
| in-process double-run (run() ×2, hashed in-process) | `2344cfb88d01022b4b6e3e119af4ce675b454e4ef6aa5e4465610600771c18e8` (both) |
| re-hash of committed `snipe_clearing_leak_results.json` (528 bytes) | `2344cfb88d01022b4b6e3e119af4ce675b454e4ef6aa5e4465610600771c18e8` |

**All computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** existence | leak_star_mean=**0.03904223** > 0, z=**135.3738** ≥ 3σ | leak_star_mean **0.03904223**, z **135.3738** | **PASS** |
| **G2** dose-response | dose_mean=**0.06175681** > 0, z=**163.6733** ≥ 3σ (paired) | dose_mean **0.06175681**, z **163.6733** | **PASS** |
| **G3** specificity | max\|placebo leak @q=0\| = **0.0** exactly | max\|placebo leak @q=0\| **0.0** (0.000e+00) | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Closed form (soft close): e_soft **0.7773411** reproduces (K−1)/(K+1)=**0.77777778** (E[v_(2)] for iid Uniform(0,1), K=8).
- Binomial-mixture closed form (hard close at q*): E[P_hard](q*)=Σ_m C(K,m)(1−q)^m q^(K−m)·(m−1)/(m+1) over the transmitted count m~Binomial(K,1−q). e_hard_theory_star=**0.73856236** vs e_hard_sim_star=**0.73829887** → theory_abs_err=**0.00026349** (the leak matches the order-statistics law thinned by transmission failure).
- Leak curve (mean P_soft − P_hard, rising in q): q=0.05 **0.01172271**, q*=0.15 **0.03904223** (= **5.022535%** of the soft-close clear), q=0.25 **0.07347951**. At q=0 the two rules coincide: max|placebo leak| = **0.0** exactly (the effect vanishes when the friction is removed).

**Headline:** a hard-close (fixed-deadline) auction clears at a second-price over only the bids that TRANSMIT; with last-instant snipes dropping at rate q, the effective field is thinned and the clear lands BELOW the full-field competitive second price v_(2). The leak is real and monotone: **0.03904223** at q*=0.15 (**5.022535%** of the clear) at **135σ**, it grows dose-responsively (leak(0.25) − leak(0.05) = **0.06175681** at **164σ** under paired common-random-numbers), and it vanishes EXACTLY at q=0 (max|placebo|=**0.0**, hard-close = soft-close when nothing drops) — so the effect is caused by the transmission friction q, not an artifact. The sim reproduces the binomial-mixture closed form E[P_hard](q*) within **2.6e-4** and the soft-close clear (K−1)/(K+1) exactly, byte-for-byte across cross-invocations and an in-process double-run. The anti-snipe (auto-extend) timer is therefore an economic mechanism — a seller→best-connection value transfer plus an AH-cut gold-sink under-drain that scales with q — not UX politeness. Anchor: Roth & Ockenfels, "Last-Minute Bidding and the Rules for Ending Second-Price Auctions", American Economic Review 92(4), 2002. **APPROVE.**

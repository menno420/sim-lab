# Probe report — VERDICT 148 · balance-triangle pick-rate inversion (P135 → V148, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/superbot-games/balance_triangle_pick_rate_inversion.py` at `06d72c4` (PROPOSAL 135, round-31 GAME slot).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/balance_triangle_pick_rate_inversion.py` — `diff` exit **0**, file sha256 `659b49a4a38ff96a28e81529533d88271cee5a8f88eecb20269c1e517cc09974`, git blob `04997dae5536da9e6128e7dd2ae81f71be3bddd1`, **211** lines / **8935** bytes. Permalink: https://github.com/menno420/idea-engine/blob/06d72c4de68064601088927ed2c4e884d02d0a6b/ideas/superbot-games/balance_triangle_pick_rate_inversion.py
- Pinned world: **SEED=20260717**, TRIALS=**200000**, SIGMA_GATE=**3.0**; SKEWED margins a/b/c=**0.4/0.2/0.2**, SYMMETRIC **0.2/0.2/0.2**. Order is (R, P, S) throughout. Stdlib-only (hashlib, json, math, random); no numpy/scipy; Python 3.11.15. `run()` builds one `random.Random(SEED)` stream and, in fixed order, (G1) samples the opponent from the closed-form mix x*=(0.25,0.50,0.25) and measures each pure row action's MC mean payoff vs value 0; (G2) samples the opponent uniform on the SKEWED matrix and measures R's MC edge vs 0 and vs the exact anchor (a−c)/3; (G3) samples the opponent uniform on the SYMMETRIC matrix and measures R's MC edge vs 0 alongside the exact all-zero exploitability. Gate z-scores are on the ESTIMATED statistic via its standard error (se=√(var/trials)) — the P104..V147 /se convention.
- Skew-symmetric model: payoff matrix M (row's expected score vs column, order R,P,S) = [[0,−c,a],[c,0,−b],[−a,b,0]] with M=−Mᵀ ⇒ value 0, symmetric optimum x* solving Mx*=0 ⇒ x*_R:x*_P:x*_S = b:a:c. SKEWED (a=0.4,b=0.2,c=0.2) ⇒ x*=(0.25,0.50,0.25); SYMMETRIC (0.2,0.2,0.2) ⇒ (1/3,1/3,1/3).
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` in the script text, not assumed. The computation lives in `run()`, so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P135 outbox / verifier `Results-JSON sha256:` line) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |
| cross-invocation B (fresh `python3`) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |
| reparse-stdout → compact re-serialize → sha256 (independent recompute) | `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced the identical results dict AND identical digest run-to-run (`run()` #1 == `run()` #2 as dicts). Independent recompute confirms the WHOLE-DICT posture (the dict carries no `results_sha256` field) and that re-parsing the pretty stdout dump → compact re-serialize → sha256 reproduces the same digest.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** equilibrium/indifference (max\|z\| < 3σ vs value 0, opponent x*=(0.25,0.50,0.25)) | max\|z\| **1.314** | means R/P/S **+0.000556/+0.000387/+0.000719**, z R/P/S **+1.014/+1.226/+1.314**, max\|z\| **1.3143865915026838** < 3.0 | **PASS** |
| **G2** inversion (R vs uniform > 0, z_exist ≥ 3σ, z_anchor < 3σ vs (a−c)/3) | R **+0.06721**, z_exist **+120.37**, z_anchor **+0.975** | R **+0.0672109999998512** > 0, z_exist **+120.3689727128182** ≥ 3, anchor (a−c)/3 **0.06666666666666667**, z_anchor **+0.9748529872924236** < 3 | **PASS** |
| **G3** placebo (symmetric max\|exact\|==0.0 exactly AND \|z\| < 3σ vs 0) | max\|exact\| **0.0**, z **+0.594** | max\|exact\| **0.0** exactly (R/P/S all 0.0), MC R-vs-uniform **+0.000217**, z **+0.5939951919337725** < 3 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- **Closed forms:** skew-symmetric equilibrium x*_R:x*_P:x*_S = b:a:c ⇒ SKEWED x*=(0.25, 0.50, 0.25), SYMMETRIC (1/3, 1/3, 1/3); exact payoff of each pure row action vs the uniform meta = row-sum/3 ⇒ SKEWED (R,P,S)=(+0.0666667, 0.0, −0.0666667), the R edge being (a−c)/3; SYMMETRIC exactly (0.0, 0.0, 0.0).
- **G1 (equilibrium/indifference):** opponent fixed at x*=(0.25,0.50,0.25); each pure action's MC mean payoff vs 0 — R **+0.000556** (z **+1.014**), P **+0.000387** (z **+1.226**), S **+0.000719** (z **+1.314**); max\|z\|=**1.3143865915026838** < 3σ — x* makes the whole field indifferent, so it solves Mx*=0 and the game value is 0.
- **G2 (inversion, headline):** SKEWED triangle, opponent uniform; best pure response R MC payoff **+0.0672109999998512** > 0, z_exist = mean/se = **+120.3689727128182** ≥ 3σ (the uniform "equal pick rates" meta is decisively exploitable), AND matches the exact anchor (a−c)/3 = **0.06666666666666667** by z_anchor = **+0.9748529872924236** < 3σ. Because the equilibrium weights are the INVERSE margins (b, a, c), buffing a raises x*_P (P's share ∝ a) and leaves x*_R ∝ b unchanged relative — the folk "buff R → R played more" is reversed into "buff R → its counter P is played more."
- **G3 (placebo):** SYMMETRIC triangle; exact uniform-exploitability of every action is **0.0** (max\|·\|=**0.0** exactly), and the MC best-action-vs-uniform payoff is **+0.000217** by z = **+0.5939951919337725** < 3σ — when the three margins are equal the uniform meta is exactly the equilibrium and non-exploitable, so the G2 effect is caused by margin ASYMMETRY, not by the sim.
- **Equilibrium mixes reproduced:** x*_skewed = {R: 0.25, P: 0.5, S: 0.25}; x*_symmetric = {R: 0.3333333333333333, P: 0.3333333333333333, S: 0.3333333333333333}.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/superbot-games/balance_triangle_pick_rate_inversion.py \
   sims/verdict-148-balance-triangle/balance_triangle_pick_rate_inversion.py
diff idea-engine/ideas/superbot-games/balance_triangle_pick_rate_inversion.py \
     sims/verdict-148-balance-triangle/balance_triangle_pick_rate_inversion.py   # exit 0
sha256sum <both>   # 659b49a4a38ff96a28e81529533d88271cee5a8f88eecb20269c1e517cc09974 (both)

# cross-invocation A/B (fresh processes)
python3 balance_triangle_pick_rate_inversion.py > run-stdout.txt      # exit 0
python3 balance_triangle_pick_rate_inversion.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b

# in-process double-run + independent compact-digest recompute
python3 -c "run() x2; sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs 92de2d54…24a4b == disclosed; dict identical run-to-run
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, sha256 `659b49a4…c09974`), the results-dict sha256 reproduces the disclosed digest `92de2d5454c34f274869bc83d302682909b376380c16e60b6afcb12756424a4b` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The claim holds: a weighted rock-paper-scissors triangle is a skew-symmetric zero-sum game whose Nash equilibrium plays each unit in proportion to the INVERSE margins (x*_R:x*_P:x*_S = b:a:c), so buffing a unit's margin can LOWER its own pick rate and RAISE its counter's while the value stays 0, and the intuitive uniform meta is exploitable by exactly (a−c)/3 — "balance = equal pick rates" inverted. The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.

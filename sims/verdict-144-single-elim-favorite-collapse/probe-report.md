# Probe report — VERDICT 144 · single-elimination favorite-collapse (P131 → V144, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/superbot-games/single_elim_favorite_collapse.py` at main `cf2e20f` (PROPOSAL 131).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/superbot-games/single_elim_favorite_collapse.py` — `diff` exit **0**, file sha256 `7bb7611fe7fe500625667e144828f82c83bb2b380a9407c46274d922762bc2a5`, git blob `54fa50fbcbb8c0ce192bc82aa0d04aaf81ab9fc1`, **168** lines / **6130** bytes. Permalink: https://github.com/menno420/idea-engine/blob/cf2e20f/ideas/superbot-games/single_elim_favorite_collapse.py
- Pinned world: **SEED=20260717**, TRIALS=**200000**, FAVORITE_STRENGTH=**3.0** → P_MATCH=**0.75**, ROUNDS=**(2, 4, 6, 8)** → N=**4, 16, 64, 256**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Each trial simulates the favorite's actual R-match knockout path — `rng.random() < P_MATCH` per round off the SINGLE pinned `random.Random(SEED)` stream, breaking on the first loss — over ROUNDS in fixed order; records the MC favorite title frequency at each R. Exact closed-form anchors (no RNG): P_title(R)=p^R. Gate z-scores are on the observed proportion via its standard error (Bernoulli se=√(p0(1−p0)/TRIALS) for the frequency/proportion; delta-method se for the ratio), the P104..P132 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` calls `run()`, computes `payload=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(payload.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 142–164 in the script text, not assumed. The computation lives in `run()` (returns the results dict), so the in-process double-run calls `run()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P131 outbox / verifier `Results-JSON sha256:` line) | `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` |
| cross-invocation B (fresh `python3`) | `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` |
| in-process double-run #1 (`run()`, compact-hashed in-process) | `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` |
| in-process double-run #2 (`run()` again, compact-hashed in-process) | `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced the identical results dict AND identical digest run-to-run (`run()` #1 == `run()` #2 as dicts).

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** sim-correct (MC title freq at R=8 within 3σ of closed form 0.75^8) | freq **0.100455** vs closed **0.1001129150390625**, z **+0.510** | freq **0.100455**, closed **0.1001129150390625**, z **+0.5096944639694352** | **PASS** |
| **G2** geometric haircut (MC ratio P(8)/P(4) within 3σ of anchor 0.75^4; constant haircut) | ratio_mc **0.318571** vs anchor **0.31640625**, z **+0.916** | ratio_mc **0.3185710208353154**, anchor **0.31640625**, z **+0.9163465017212093** | **PASS** |
| **G3** inversion (MC P(fav loses) at R=6 > 0.5, within 3σ of anchor 1−0.75^6=0.822021) | frac **0.82266** > 0.5, anchor **0.822021484375**, z **+0.747** | frac **0.82266**, anchor **0.822021484375**, z **+0.7465538727644705**, majority **True** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Closed-form title probabilities P_title(R)=0.75^R: R=2→**0.5625**, R=4→**0.31640625**, R=6→**0.177978515625**, R=8→**0.1001129150390625**. MC title freqs: R=2→**0.562975**, R=4→**0.31533**, R=6→**0.17734**, R=8→**0.100455**.
- **G1 (sim-correct, headline):** MC favorite title frequency at R=8 (256 entrants) = **0.100455** vs closed form 0.75^8=**0.1001129150390625**, se=√(p0(1−p0)/TRIALS), z=**+0.5096944639694352** — |z| < 3σ, the Monte-Carlo frequency lands on the exact closed-form anchor p^8.
- **G2 (geometric haircut):** MC ratio P_title(8)/P_title(4) = **0.3185710208353154** vs the anchor p^4=0.75^4=**0.31640625**, z (delta method) = **+0.9163465017212093** < 3σ — the multiplicative per-round haircut is the constant p=0.75; each added round is the SAME haircut, not a "truer test".
- **G3 (inversion):** at R=6 (64-player esports bracket) MC P(favorite loses) = 1−0.17734 = **0.82266** > 0.5 (majority=**True**), anchor 1−0.75^6=**0.822021484375**, z (Bernoulli se) = **+0.7465538727644705** < 3σ — a 3× favorite is dethroned in the majority of runs, the favorite's title probability is only ≈**17.8%** (0.75^6=0.177978), reversing the "bigger tournament rewards the best" folk belief.
- Model: Bradley–Terry paired comparison — one favorite of strength f=3 vs N−1 indistinguishable normals of strength 1, per-match p=f/(f+1)=**0.75** constant every round under ANY seeding, exact title probability P_title(R)=p^R strictly decreasing in R. The fix is DEPTH per round (best-of-N → win prob toward 1) or a group/Swiss stage, not more single-elim rounds and not seeding.

> NOTE: the idea-engine outbox dry-sim narrative and this reproduction agree to the digit on every reported figure (MC freqs, gate z's, ratio 0.318571, P(fav loses)=0.82266); the reproduced digest `00280618…` matches the disclosed digest EXACTLY over the whole dict, so the exact dict values are reproduced bit-for-bit.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/superbot-games/single_elim_favorite_collapse.py \
   sims/verdict-144-single-elim-favorite-collapse/single_elim_favorite_collapse.py
diff idea-engine/ideas/superbot-games/single_elim_favorite_collapse.py \
     sims/verdict-144-single-elim-favorite-collapse/single_elim_favorite_collapse.py   # exit 0
sha256sum <both>   # 7bb7611fe7fe500625667e144828f82c83bb2b380a9407c46274d922762bc2a5 (both)

# cross-invocation A/B (fresh processes)
python3 single_elim_favorite_collapse.py > run-stdout.txt       # exit 0
python3 single_elim_favorite_collapse.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2

# in-process double-run + independent compact-digest recompute
python3 -c "run() x2; sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs 00280618…c2a0f2 == disclosed; dict identical run-to-run
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, sha256 `7bb7611f…762bc2a5`), the results-dict sha256 reproduces the disclosed digest `002806188054a6eb2f768208f52629d0a3bd0d14624e0489e480efcf86c2a0f2` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.

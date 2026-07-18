# Probe report — VERDICT 149 · base-rate PPV collapse at low prevalence (P136 → V149, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green, zero agent merge calls.

Source: idea-engine `ideas/fleet/base_rate_ppv_collapse.py` at `06d72c4` (PROPOSAL 136, round-31 UNRELATED slot CLOSER).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/base_rate_ppv_collapse.py` — `diff` exit **0**, file sha256 `aae78a6a7db0380f77c8793c71d476b5d5a45a52b5e9d421ad7195f4fb1c2694`, git blob `9aef51ad0201b7c77698a19f4e122ffb08d80abe`, **209** lines. Permalink: https://github.com/menno420/idea-engine/blob/06d72c4de68064601088927ed2c4e884d02d0a6b/ideas/fleet/base_rate_ppv_collapse.py
- Pinned world: **SEED=20260717**, **N=2,000,000** individuals per scenario, **sens=spec=0.99**, two prevalence scenarios **A prev=0.01** and **B prev=0.001**, **SIGMA_GATE=3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. `run()` seeds `random.seed(SEED)` once on a single stream, and for each scenario draws N individuals — diseased w.p. `prev`, then positive w.p. `sens` if diseased else `1−spec` — tallying TP/FP/TN/FN, forming the empirical PPV = TP/(TP+FP) and positive-rate = (TP+FP)/N, and evaluating three z-gates against the exact closed forms PPV=(sens·prev)/(sens·prev+(1−spec)(1−prev)) and positive-rate p0=sens·prev+(1−spec)(1−prev). Gate z-scores are on the observed proportion vs the closed-form null via a Bernoulli standard error (se=√(PPV0(1−PPV0)/n_pos) for the posteriors, se=√(p0(1−p0)/N) for the positive-rate), the P104..P134 /se convention.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>` and the three gate summary lines. It writes NO results file. **Twist (P127+):** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. The verifier additionally carries an in-process double-run assertion (run()×2 compact-hashed equal).

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P136 outbox / verifier `Results-JSON sha256:` line) | `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8` |
| cross-invocation B (fresh `python3`) | `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the verifier's own in-process double-run assertion (run() twice, compact-hashed) passes.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** posterior=0.5 (empirical PPV(prev=0.01) vs exact 0.5) | z **−0.898** | emp_ppv_a **0.497746** vs anchor **0.500000**, z **−0.898**, se **0.00250908**, \|z\| < 3.0 | **PASS** |
| **G2** positive-rate (empirical posrate(prev=0.01) vs exact 0.0198) | z **+0.563** | emp_positive_rate_a **0.019856** vs anchor **0.019800**, z **+0.563**, se **9.85088e-05**, \|z\| < 3.0 | **PASS** |
| **G3** collapse deepens (empirical PPV(prev=0.001) vs exact 0.0901639) | z **+1.188** | emp_ppv_b **0.092466** vs anchor **0.090164**, z **+1.188**, se **0.00193830**, \|z\| < 3.0 | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- **Closed forms (no RNG):** exact PPV at prev=0.01 = (0.99·0.01)/(0.99·0.01+0.01·0.99) = **0.500000** (the knife-edge prev*=1−q=0.01); exact positive-rate at prev=0.01 = sens·prev+(1−spec)(1−prev) = **0.019800**; exact PPV at prev=0.001 = (0.99·0.001)/(0.99·0.001+0.01·0.999) = **0.0901639**.
- **Scenario A tallies (prev=0.01):** TP=**19766**, FP=**19945**, TN=**1960116**, FN=**173**, n_pos=**39711**, emp_ppv=**0.497746**, emp_positive_rate=**0.0198555**.
- **Scenario B tallies (prev=0.001):** TP=**2019**, FP=**19816**, TN=**1978151**, FN=**14**, n_pos=**21835**, emp_ppv=**0.092466**, emp_positive_rate=**0.0109175**.
- **G1 (posterior=0.5, headline):** the MC empirical PPV at prev=0.01 = **0.497746** matches the exact anchor **0.500000** within z=**−0.898** (Bernoulli se over the positives) — a "99%-accurate" positive at 1% prevalence is a **coin flip**, not near-certainty; the intuition confuses sens=P(positive|disease) with its converse P(disease|positive).
- **G2 (positive-rate):** the MC empirical positive-rate at prev=0.01 = **0.019856** matches the exact anchor **0.019800** within z=**+0.563** — the firing rate is the Bayes denominator TP+FP, confirming the tallies form the right object.
- **G3 (collapse deepens):** the MC empirical PPV at prev=0.001 = **0.092466** matches the exact anchor **0.0901639** within z=**+1.188** — the posterior collapses FURTHER as prevalence falls (0.5→~0.09), because true positives (∝prev) are swamped by the false positives from the huge healthy majority (∝1−prev); the base-rate mechanism made quantitative.

## Transferable correction (lane consumer, Q-0264)
Lane CONSUMER = any operator/clinician/analyst reading a rare-event positive flag (medical screen, fraud/anomaly/intrusion alert, spam/content-moderation flag, multiple-comparison "significant" winner, any rare-class classifier). The transferable correction: **a positive result updates you from the prior prevalence to the posterior PPV=(sens·prev)/(sens·prev+(1−spec)(1−prev)), NOT to the test's accuracy.** With a symmetric q-accurate test the posterior is only ½ at prevalence 1−q and collapses ~linearly in the base rate below that, so mass-screening a rare condition produces mostly false positives no matter how good the test. To make a positive mean something: either raise the pre-test probability (target a higher-prevalence subgroup) or confirm with a second independent test (each independent positive multiplies the likelihood ratio sens/(1−spec) again), and always report precision (=PPV) at the DEPLOYED base rate, never the raw accuracy — this is base-rate neglect / the false-positive paradox / the prosecutor's fallacy. Adjacent to but DISTINCT from P072 pooled-screening-prevalence-wall: P072 prices test-COUNT economics (how many tests, PERFECT tests); P136 is the posterior meaning of ONE positive (IMPERFECT tests — precisely the sensitivity/specificity<1 follow-up P072 named out-of-scope).

## Previous-session review
Prior loop landed VERDICT 147 (P134 cohort-blended LTV understatement, round-31 VENTURE slot, +13, sim-lab PR #220 @c6bf5e5b, digest f45e6609…f489b) — APPROVE, byte-identical reproduction across cross-invocation A/B + an in-process double-run, all three gates PASS in order. It held the whole-dict / no-self-field / stdout-only digest posture verbatim; this V149 slice inherits it unchanged and closes round-31 on the verdict side at the UNRELATED slot.

## Reproduction commands (verbatim)
```
# byte-identical copy
cp idea-engine/ideas/fleet/base_rate_ppv_collapse.py \
   sims/verdict-149-ppv-collapse/base_rate_ppv_collapse.py
diff idea-engine/ideas/fleet/base_rate_ppv_collapse.py \
     sims/verdict-149-ppv-collapse/base_rate_ppv_collapse.py   # exit 0
sha256sum <both>   # aae78a6a7db0380f77c8793c71d476b5d5a45a52b5e9d421ad7195f4fb1c2694 (both)

# cross-invocation A/B (fresh processes)
python3 base_rate_ppv_collapse.py | tee run-stdout.txt       # exit 0
python3 base_rate_ppv_collapse.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0, file sha256 `aae78a6a…c2694`), the results-dict sha256 reproduces the disclosed digest `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8` EXACTLY across cross-invocation A/B, and all three gates PASS in order G1→G2→G3 (verifier exit 0, all_pass=true). The claim holds: by Bayes the posterior of one positive is PPV=(sens·prev)/(sens·prev+(1−spec)(1−prev)) — a function of the BASE RATE, not the accuracy — so a 99%-accurate positive is EXACTLY a coin flip at 1% prevalence and collapses to ~9.0% at 0.1%. The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green, zero agent merge calls.

## Probe questions

**1.** The verifier pins two prevalence scenarios (1% and 0.1%); would a THIRD scenario at prev=1−q from the OTHER side (e.g. prev=0.99) be a useful placebo gate — confirming the posterior symmetry PPV(1−q)=NPV(q) — or does adding it dilute the headline coin-flip result the two-scenario design isolates?

**2.** G1/G2/G3 all land near-anchor (|z| all < 1.2, the MC sitting on its exact closed forms); is the pre-registered SIGMA_GATE=3.0 doing real work here, or should a base-rate object like this instead gate on a TIGHT two-sided bracket (e.g. |z|<0.5 pass, |z|>3 hard-fail, between = flag) to catch a subtly-wrong RNG that a 3σ band would wave through?

**3.** The transferable correction names "confirm with a second independent test" as the cure; the round-32+ MULTI-test verifier would pin how much a confirmatory positive drags the posterior back up (LR=sens/(1−spec) compounding) — should that head reuse THIS pinned world (sens=spec=0.99, prev A/B) so the single-test PPV here is the exact prior the two-test object updates from, making the two cards a matched pair?

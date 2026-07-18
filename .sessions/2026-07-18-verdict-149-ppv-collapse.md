# VERDICT 149 — base-rate PPV collapse at low prevalence

Reproduce PROPOSAL 136 (round-31 UNRELATED slot CLOSER, P136 → V149, +13): does a "99%-accurate" positive test result mean ~99% chance of disease? It does NOT. By Bayes the posterior of one positive is P(disease|positive)=PPV=(sens·prev)/(sens·prev+(1−spec)(1−prev)) — a function of the BASE RATE, not the accuracy; the folk intuition confuses the forward conditional sens=P(positive|disease) with its converse (base-rate neglect / the false-positive paradox / the prosecutor's fallacy). At sens=spec=0.99 the posterior is EXACTLY 0.5 at prevalence 1% (the knife-edge prev*=1−q) and COLLAPSES to ~0.0901639 at prevalence 0.1%, because true positives (∝prev) are swamped by false positives (∝1−prev).

> **Status:** `complete`
> 📊 Model: Claude Opus · high · review/verify

Born red by design: this card landed `in-progress` in the branch's first commit, holding the substrate-gate HOLD red until byte-identical reproduction was proven and audited (merge-on-green). The LAST commit flips it to `complete`, clearing the HOLD.

## Objective
Reproduce the committed P136 verifier `ideas/fleet/base_rate_ppv_collapse.py` byte-identical under SEED 20260717, confirm the whole-dict compact-canonical results sha256 matches the disclosed digest EXACTLY, and confirm all three pre-registered ≥3σ gates PASS against the proposal's criteria in order G1→G2→G3.

## GROUNDING (verified at HEAD)
- P136 outbox block — idea-engine `control/outbox.md` @ `06d72c4`: https://github.com/menno420/idea-engine/blob/06d72c4de68064601088927ed2c4e884d02d0a6b/control/outbox.md
- P136 verifier — idea-engine `ideas/fleet/base_rate_ppv_collapse.py` @ `06d72c4`: https://github.com/menno420/idea-engine/blob/06d72c4de68064601088927ed2c4e884d02d0a6b/ideas/fleet/base_rate_ppv_collapse.py — file sha256 `aae78a6a7db0380f77c8793c71d476b5d5a45a52b5e9d421ad7195f4fb1c2694`
- Disclosed results-dict sha256: `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8`
- Pins: SEED 20260717 · N 2,000,000 per scenario · sens=spec 0.99 · prev A 0.01 / prev B 0.001 · SIGMA_GATE 3.0

## Constraints honored
- Byte-identical verifier (`diff` exit 0) — no edits to the reproduced source.
- Stdlib only (`random, math, json, hashlib`); no numpy/scipy.
- Deterministic: cross-invocation double-run byte-identical + in-process double-run assertion.
- Whole-dict / no-self-field / stdout-only digest posture — no results.json artifact (matches disclosed posture + the V146/V147 exemplars).

## Gate plan (disclosed → reproduced), order G1→G2→G3
- **G1** posterior=0.5 (headline): empirical PPV(prev=0.01)=0.497746 vs exact anchor 0.500000 → z=−0.898, |z| < 3σ → **PASS**
- **G2** positive-rate: empirical positive-rate(prev=0.01)=0.019856 vs exact anchor 0.019800 → z=+0.563, |z| < 3σ → **PASS**
- **G3** collapse deepens: empirical PPV(prev=0.001)=0.092466 vs exact anchor 0.0901639 → z=+1.188, |z| < 3σ → **PASS**

## Outcome — APPROVE (exact reproduction)
Byte-identical reproduction under SEED 20260717: verifier copied verbatim (`diff` exit 0, file sha256 `aae78a6a7db0380f77c8793c71d476b5d5a45a52b5e9d421ad7195f4fb1c2694`, git blob `9aef51ad`, 209 lines), whole-dict compact-canonical results sha256 = `89c4bd02969e51bfed210680af0d73869f93fde23149f1cc238ba77b895faac8`, exactly matching the disclosed digest and the verifier's printed `Results-JSON sha256` line, reproduced identically across cross-invocation A/B (stdout diff exit 0). All three ≥3σ gates PASS in order G1→G2→G3 with the disclosed z-values (−0.898 / +0.563 / +1.188), all_pass=true, exit 0. Scenario A (prev=0.01): TP=19766 FP=19945 n_pos=39711 emp_ppv=0.497746 posrate=0.019856; scenario B (prev=0.001): TP=2019 FP=19816 n_pos=21835 emp_ppv=0.092466. The claim holds: by Bayes the posterior of one positive is PPV=(sens·prev)/(sens·prev+(1−spec)(1−prev)) — a function of the BASE RATE, not the accuracy — so a 99%-accurate positive is EXACTLY a coin flip at 1% prevalence and collapses to ~9.0% at 0.1%. **APPROVE.** Probe report: `sims/verdict-149-ppv-collapse/probe-report.md`.

## ⟲ Previous-session review
Prior loop landed VERDICT 147 (P134 the cohort-blended LTV understatement, round-31 VENTURE slot, +13, sim-lab PR #220 @c6bf5e5b, digest f45e6609…f489b) — APPROVE, byte-identical reproduction across cross-invocation A/B + an in-process double-run, all three gates PASS in order (G1 understatement bias z=171.221384, G2 convex closed-form bracket z=0.363449, G3 dispersion-driven z=170.572090). It held the whole-dict / no-self-field / stdout-only digest posture verbatim and left its own PR URL to be backfilled into the merged card (the same continuity nit it flagged against V144's un-backfilled `(this PR)`). This V149 card inherits that posture and the ⟲ discipline unchanged and closes round-31 on the verdict side at the UNRELATED slot.

## 💡 Session idea
Base-rate neglect (P136) and P108 regression-to-the-mean are the same error wearing two coats — both act on the wrong conditional (P(disease|positive)≠P(positive|disease); E[true|observed]≠observed). The natural round-32+ follow-up already named in the P136 card is the MULTI-test posterior: two independent positives multiply the likelihood ratio LR=sens/(1−spec) again, so a G-gate pinning how much a confirmatory second independent positive drags the posterior back up as a function of the deployed base rate — quantifying the operational cure (raise pre-test probability OR confirm independently) rather than only naming it — is the distinct verifier object worth pre-registering next.

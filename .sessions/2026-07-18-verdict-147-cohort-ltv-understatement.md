# VERDICT 147 — cohort-blended LTV understatement

Reproduce PROPOSAL 134 (round-31 VENTURE slot, P134 → V147, +13): does collapsing a heterogeneous customer book to a single blended churn rate c̄ and computing LTV = m/c̄ UNDERSTATE the portfolio's true average LTV E[m/c]? Because 1/c is convex, Jensen forces E[m/c] ≥ m/c̄, with the gap driven by churn DISPERSION not level (gap ≈ m·Var(c)/c̄³) — reaching ~30% for churn uniform on 5%–35% (true ln(7)/0.30 = 6.486367 vs blended 5.000000).

> **Status:** `complete`
> 📊 Model: Claude Opus · high · review/verify

Born red by design: this card landed `in-progress` in the branch's first commit, holding the substrate-gate HOLD red until byte-identical reproduction was proven and audited (ORDER 003 merge-on-green). The LAST commit flips it to `complete`, clearing the HOLD.

## Objective
Reproduce the committed P134 verifier `ideas/venture-lab/blended_churn_ltv_understatement.py` byte-identical under SEED 20260717, confirm the whole-dict compact-canonical results sha256 matches the disclosed digest EXACTLY, and confirm all three pre-registered ≥3σ gates PASS against the proposal's criteria.

## GROUNDING (verified at HEAD)
- P134 outbox block — idea-engine `control/outbox.md` @ `12bd4ec`: https://github.com/menno420/idea-engine/blob/12bd4eccf88acba8c5977f013f80d67eba9cdd25/control/outbox.md
- P134 verifier — idea-engine `ideas/venture-lab/blended_churn_ltv_understatement.py` @ `12bd4ec`: https://github.com/menno420/idea-engine/blob/12bd4eccf88acba8c5977f013f80d67eba9cdd25/ideas/venture-lab/blended_churn_ltv_understatement.py
- Disclosed results-dict sha256: `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b`
- Pins: SEED 20260717 · TRIALS 200000 · SIGMA 3.0 · margin m 1.0 · wide band [0.05,0.35] · narrow band [0.19,0.21]

## Constraints honored
- Byte-identical verifier (`diff` exit 0) — no edits to the reproduced source.
- Stdlib only (`random, math, json, hashlib`); Python 3.11.15.
- Deterministic: in-process double-run + cross-invocation both byte-identical.
- Whole-dict / no-self-field / stdout-only digest posture — no results.json artifact (matches disclosed posture + the V145 exemplar).

## Gate plan (disclosed → reproduced), order G1→G2→G3
- **G1** understatement bias, WIDE gap > 0: disclosed z=171.221384 → reproduced z=171.221384, wide_gap_mean=1.489529 > 0, z ≥ 3.0 → **PASS**
- **G2** matches closed form E[m/c]=6.486367 bracket: disclosed |z|=0.363449 < 3 → reproduced z=0.363449, |z| < 3.0 → **PASS**
- **G3** dispersion-driven wide−narrow gap: disclosed z=170.572090, narrow gap 0.004628 < 0.05 → reproduced z=170.572090, gap_diff=1.484901 > 0, z ≥ 3.0, narrow_gap_mean=0.004628 < 0.05 → **PASS**

## Outcome — APPROVE (exact reproduction)
Byte-identical reproduction under SEED 20260717: whole-dict compact-canonical results sha256 = `f45e6609e866d7ee0cf536a302cba40a9d82dbee8926280fbeadb43f763f489b`, exactly matching the disclosed digest and the verifier's printed `Results-JSON sha256` line. All three ≥3σ gates PASS with the disclosed z-values (171.221384 / 0.363449 / 170.572090). The claim holds: blended-churn LTV = m/c̄ understates true E[m/c] by ~30% on the wide band (5.0 vs 6.486367), driven by dispersion (narrow-band gap collapses to 0.004628). **APPROVE.**

## ⟲ Previous-session review
Prior loop landed VERDICT 144 (P131 the single-elimination favorite-collapse, round-30 GAME slot, +13, sim-lab PR #219 `b2594ff`, digest `00280618…c2a0f2`) — APPROVE, byte-identical reproduction across cross-invocation A/B, all three gates PASS in order (G1 sim-correct z=+0.510 vs 0.75^8, G2 geometric-haircut ratio z=+0.916 vs 0.75^4, G3 inversion z=+0.747 with the favorite dethroned in the MAJORITY of a 64-player bracket). It did well to anchor every gate on the exact closed form P_title(R)=p^R so the inversion is a structural claim (each round is the SAME constant multiplicative haircut p=0.75, not a "truer test") rather than a magnitude gap, and its ⟲ review traced the honest domain arc finance→probability→game. One concrete nit: the V144 Outcome section shipped `Sim-lab PR: (this PR)` — the real permalink `https://github.com/menno420/sim-lab/pull/219` was never backfilled into the merged card, unlike V145 which carries its concrete `.../pull/218` link; the successor loses the one-click PR trail from the card. (This V147 card leaves its own PR URL to the flip commit for the same reason and should be backfilled in-kind.)

## 💡 Session idea
The same Jensen-convexity understatement should extend to the DECISION ratio operators actually gate on: LTV/CAC = m/(c·CAC) is convex in c exactly like LTV, so a book collapsed to a single blended churn c̄ understates its true E[m/(c·CAC)] and a portfolio that looks marginal at the blended LTV/CAC bar can clear it once dispersion is counted — a companion verifier reusing this pinned world plus a fixed CAC would isolate that. The CAC-PAYBACK framing needs a sign check first, though: nominal payback CAC/m is churn-INDEPENDENT (churn governs survival-to-payback, not the payback clock), so the survival-discounted expected payback time — periods until cumulative churn-weighted margin ≥ CAC — is where the convexity lives, and it plausibly flips sign versus LTV (blended churn making the book look FASTER-recouping than it is). A G-gate that pins whether blending biases the probability of recouping CAC, and in which direction, is worth pre-registering before committing that verifier — a genuinely distinct venture object from this LTV head.

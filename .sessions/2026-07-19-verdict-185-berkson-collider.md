# VERDICT 185 — Berkson's collider paradox (reproduce PROPOSAL 172)

Selection manufactures correlation from nothing: rank a large population by the additive composite score X+Y of two STATISTICALLY INDEPENDENT traits and keep only the top decile, and inside that elite the two traits become NEGATIVELY correlated — even though across the full population their correlation is exactly zero. Conditioning on a high value of the sum X+Y is conditioning on a COLLIDER (X → S ← Y), and collider conditioning opens a spurious path between the parents: within the survivors a shortfall on one trait must be compensated by a surplus on the other, so the elite trades one gift off against the other. This is Berkson's paradox (Berkson 1946) — the "compensation" is an artifact of the selection cut, not a real trade-off in the population. Reproduction of the verifier at SEED=20260717 is targeted to be byte-identical across invocations, the results-dict digest is targeted to match the disclosed value, and all three pre-registered gates (G1 → G2 → G3) are expected to pass. **This card is provisional — work in-progress.**

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD.** This card lands `in-progress` on its first commit to hold the PR red under the substrate-gate; it flips to `complete` on the last commit once the sim directory, run-stdout, and probe report are in place and the heartbeat is stamped. Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective
Reproduce PROPOSAL 172 (mapped to VERDICT 185 at the +13 offset) from a byte-identical copy of its verifier, confirm determinism and the disclosed digest, and evaluate the proposal against its OWN pre-registered gates G1 → G2 → G3. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)
- Verifier (sim copy, intended): `sims/verdict-185-berkson-collider/berkson_collider.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/<lane>/berkson_collider.py` — exact path to be confirmed against the landed idea-engine merge SHA before the copy.
- Offset authority: +13 (P170 → V183, P171 → V184); P172 → V185, next slot in the ladder.
- Pinned world (intended, to be read from the verifier, not invented): SEED=20260717 · Z_GATE=3.0 · two INDEPENDENT traits X, Y (standard-normal, population corr 0) · composite score S = X+Y · selection cut = top decile of S (keep top 10%) · large population N with R replications · shifted-world robustness leg (heavier tail / different cut fraction) for G3. All constants to be taken verbatim from the committed verifier.
- Domain reference: Berkson's paradox / collider bias — https://en.wikipedia.org/wiki/Berkson%27s_paradox and https://en.wikipedia.org/wiki/Collider_(statistics) — to be verified live (HTTP 200) this session.
- Disclosed digest: TO BE READ from PROPOSAL 172 / the idea-engine source at HEAD — pending; the reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (expected) — the results dict carries no digest field; `main()` runs `run()` twice, asserts the two compact-canonical (sorted-keys, fixed-dp-rounded) serializations are identical, prints the indent=2 dump, then the `Results-JSON sha256:` line. No JSON is written to disk. To be confirmed against the verifier.

## Constraints honored
- Verifier to be copied byte-identically from the idea-engine source; no edits.
- Stdlib-only (`math`, `json`, `hashlib`, `random`); Python 3.
- Seed pinned in-source (`SEED = 20260717`); no environment override (the SEED env var is expected inert).
- Gates to be evaluated against the proposal's own pre-registered thresholds, not re-invented.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3
- G1 — collider-induced negative correlation (head): across R randomized replications the sample correlation of X and Y WITHIN the selected top decile is strictly negative at ≥3 sigma, rejecting the "independent traits stay uncorrelated" folk null (population corr ≈ 0 confirmed as the control).
- G2 — mechanism / closed-form anchor: the elite correlation matches the analytic collider-conditioning prediction (truncation of a bivariate-normal sum induces a negative within-group correlation set by the cut fraction), with the measured value inside tolerance of the closed form (|z| < 3 anchor match), NOT merely "some negative number".
- G3 — robustness / shifted world: under a heavier-tailed trait distribution AND/OR a different (stricter) selection cut the within-elite correlation stays negative at ≥3 sigma and deepens as the cut tightens — the artifact is not Gaussian- or decile-specific.

## Probe questions (independent-audit checklist)
**1.** Is this genuine collider bias or merely "conditioning on a sum forces a trade-off" restated? The traits are INDEPENDENT in the population (control corr ≈ 0); the negative elite correlation appears ONLY after conditioning on the collider S = X+Y — to be demonstrated by G1 against the population control, not asserted.
**2.** Is the negative correlation a float/tie artifact of the cut? G2's closed-form match (truncated-bivariate-normal prediction) is to prove the elite correlation equals the analytic collider value, not an accident of the sampling.
**3.** Gaussian-only artifact? G3 repeats under a heavier-tailed trait law and a stricter cut; the negative within-group correlation must persist and deepen.
**4.** Is the top-decile cut cherry-picked? The cut fraction is a disclosed knob; G3's stricter-cut leg is exactly the sensitivity check, and the direction (tighter cut → more negative) is the collider prediction, not a tuned choice.
**5.** Does the "manufactured from independence" claim hold? The population control correlation (≈ 0, no selection) is reported alongside the elite correlation (< 0), so the gap IS the selection artifact, measured not assumed.
**6.** Is determinism real? To be confirmed by cross-invocation `diff` exit 0 and the results-dict sha256 reproducing the disclosed digest EXACTLY.
**7.** Cherry-picked N or seed? Results are across R randomized replications at SEED=20260717 pinned, not one draw.
**8.** Real phenomenon or textbook toy? Berkson's paradox is the documented explanation for spurious negative correlations among selected populations (admitted patients, hired candidates, funded startups, elite-cohort trait trade-offs) — the selection-induced collider correlation is the cited core.

## Outcome
**PENDING — born-red HOLD in force.** Reproduction not yet landed. This section flips to APPROVE / QUALIFIED-APPROVE / REJECT on the last commit, once: the verifier copy is byte-identical to the idea-engine source (`diff` exit 0, file sha256 + git blob recorded), determinism holds (cross-invocation `diff` exit 0 + in-process double-run assert), the results-dict digest reproduces the disclosed value EXACTLY, and gates G1 → G2 → G3 are evaluated in order against the proposal's own thresholds. Verdict rendered here only after the run is in; the card holds `in-progress` (PR red) until then.

## ⟲ Previous-session review
VERDICT 184 (Colonel Blotto evenness trap, reproduce P171, round-40 GAME slot) landed APPROVE (results-dict digest `05afdeff…5be63` MATCH, verifier byte-identical file sha256 `5c889837…`, all three gates G1 evenness-beaten → G2 concede-arithmetic identity → G3 robustness plus the non-gated deficit demo passing on the proposal's own thresholds); its card and sim dir are contiguous on main. This card continues the loop at the next slot (P172 → V185, +13) and, on its flip to `complete`, will advance the verdict high-water V184 → V185 by union-max; no regression.

## 💡 Session idea
The verifier conditions on a HARD top-decile cut of the sum. A follow-up could sweep the cut fraction continuously and plot the induced within-elite correlation against selectivity — turning the single-decile result into a dose-response curve (more selective → more negative), and add a SOFT-selection variant (probabilistic admission increasing in S) to show the collider bias survives when the gate is noisy rather than a sharp threshold — closer to how real admissions/hiring/funding filters actually select.

**Recommendation (provisional): reproduce PROPOSAL 172 (Berkson's collider paradox) at SEED=20260717; on a byte-identical copy with the disclosed digest matching and G1/G2/G3 passing on the proposal's own thresholds, APPROVE and advance the verdict high-water V184 → V185. Final recommendation rendered in Outcome once the run lands.**

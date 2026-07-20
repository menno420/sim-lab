# VERDICT 221 — Pólya urn reinforcement ends uniform: a rich-get-richer urn started at one black + one white finishes on a coin toss. In the classic two-colour Pólya urn (start 1 black + 1 white, each draw replaced with one extra ball of the colour drawn), the black-ball count after n draws is EXACTLY uniform on {1,…,n+1}, and the black fraction is a bounded martingale converging to Beta(1,1)=Uniform(0,1); shifting the start to 2 black + 1 white bends the finish to Beta(2,1) with mean 2/3 — reproduce PROPOSAL 208

- **Slice:** sim-lab VERDICT 221 (reproduce and rule on PROPOSAL 208; P208 → V221, +13 offset; lane superbot-games)
- **Source proposal:** PROPOSAL 208 — Pólya urn reinforcement → uniform finish (idea-engine); verifier landed on origin/main at commit `cc60755` (idea-engine PR #768)
- **Verifier (source):** `ideas/fleet/polya_urn_reinforcement_uniform_finish.py` (idea-engine) — copied byte-identical into this sim dir as `polya_urn_reinforcement_uniform_finish.py`
- **Reproduced by:** copy the verifier byte-identical (diff exit 0), run it, capture stdout, recompute the results-dict sha256 and confirm full-64 match; two cross-invocation runs byte-identical
- **Timestamp (date -u):** 2026-07-20T11:09:28Z
- **SEED:** 20260717 · **params:** N_ENUM_MAX=20, N_MC=200, M_MC=20000, START_SYM=(1,1), START_SHIFT=(2,1)

## 📊 Model: Opus family · high effort · verdict-reproduction

## Ruling: APPROVE

Fully reproduced. The results-dict sha256 `d566e380865bfb7089d5042ed7169edfddc7cab7f112af80de6ef2c29c91aa68`
matches the disclosed PROPOSAL 208 digest across all 64 hex characters — printed by the verifier AND
independently recomputed here by re-canonicalizing the printed results dict (0 divergence). The verifier
was copied byte-identical (diff exit 0). All five gates PASS each read in its own direction; the G1 and
G4 legs are self-certifying EXACT-Fraction identities (`max_abs_deviation == "0"`, not tuned tolerances).
The head is honestly scoped to the classic two-colour Pólya urn and is externally grounded to a
sha1-pinned Wikipedia revision whose martingale/Beta-limit sentence and symmetric worked example
firsthand-support the uniform-finish leg. **Ruling: APPROVE.**

## Head

Pólya urn reinforcement ends uniform. In the classic two-colour Pólya urn started at 1 black + 1 white —
draw a ball uniformly at random, return it, and add one MORE ball of the same colour ("the rich get
richer") — the number of black balls after n draws is EXACTLY uniform on {1, 2, …, n+1}: every attainable
black-count is equally likely. Equivalently the black fraction is a bounded martingale that converges to
Beta(1,1) = Uniform(0,1), so the long-run share is a fair coin toss even though every step reinforces the
current leader. This is the α=β=1 special case of the general result that the terminal share is
Beta(α, β) for a start of α black + β white: shifting to 2 black + 1 white bends the finish to Beta(2,1),
mean 2/3. The exact black-count law is decided in exact Fraction arithmetic (Beta-binomial(n; α, β)), so
the uniform and shifted identities are theorems, not tolerances.

## Reproduction

- Verifier copied byte-identical: `diff ideas/fleet/polya_urn_reinforcement_uniform_finish.py sims/verdict-221-polya-urn-uniform/polya_urn_reinforcement_uniform_finish.py` → **exit 0**.
- results-dict sha256 posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical dict's own sha256 IS the digest (`json.dumps(results, sort_keys=True, separators=(",",":"))`, exact Fractions serialized as "num/den" strings, floats rounded to fixed dp, no self-referential sha field).
- Disclosed digest:              `d566e380865bfb7089d5042ed7169edfddc7cab7f112af80de6ef2c29c91aa68`
- Reproduced (printed by run):   `d566e380865bfb7089d5042ed7169edfddc7cab7f112af80de6ef2c29c91aa68`
- Independently recomputed:      `d566e380865bfb7089d5042ed7169edfddc7cab7f112af80de6ef2c29c91aa68` — recomputed OUTSIDE the verifier by parsing the printed results dict from `run-stdout.txt`, re-serializing compact-canonical (`sort_keys=True, separators=(",",":")`), and hashing sha256 → identical across all 64 hex chars.
- **FULL-64 EXACT MATCH** (printed == independently-recomputed == disclosed target). The printed token is 64 hex chars, no truncation.
- Full reproduction stdout: `run-stdout.txt`.

## Determinism

- In-process double-run: the verifier recomputes in-process and reports `in_process_double_run = "IDENTICAL"`; the run exited 0, so the in-process guard held.
- Cross-invocation: two separate process invocations → byte-identical whole files including the digest line, `diff` **exit 0**.
- G5 gate: `{in_process_double_run: "IDENTICAL", pass: true}`.

## Gate evaluation (against PROPOSAL 208's OWN criteria, in order — each read in ITS direction)

- **G1 — EXACT uniform black-count law** (symmetric start (1,1), n=1..20; direction: exact-agreement, Fraction, zero deviation). The exact-enumeration black-count distribution equals the uniform law `P(K_n=k) = 1/(n+1)` == Beta-binomial(n; 1, 1) for every n in range: `max_abs_deviation = "0"`. Witness law at n=3: `["1/4","1/4","1/4","1/4"]` (all four attainable counts equally likely). **max_abs_deviation == "0" → PASS.** (Self-certifying: an exact-0 Fraction deviation is a theorem, not a tuned tolerance.)
- **G2 — reinforcement does NOT wash out to a point mass** (M=20000; direction: high z = SIGNAL, dispersion does not vanish, LLN defeated). The Monte-Carlo variance of the terminal black share `observed_var = 0.0838204573` sits far ABOVE the law-of-large-numbers null `lln_null_var = 0.00125` (`se_null = 1.2500313e-05`) and essentially at the uniform prediction `uniform_pred_var = 0.0833333333`: `z = 6605.4714 > threshold 3.0`. The i.i.d. control (`iid_observed_var = 0.0012472517`) collapses to the null, confirming the spread is reinforcement, not sampling noise. **z = 6605.4714 ≥ 3 → PASS.** (EFFECT gate: a LARGE z is the PASS direction.)
- **G3 — the terminal share is genuinely Uniform(0,1)** (direction: low |z| = AGREEMENT, Monte-Carlo converges to the exact uniform law). The Monte-Carlo mass in the middle third [1/3, 2/3] `mc_middle_third_rate = 0.3263` stays within a few σ of the exact uniform `exact_middle_third_prob = 0.3333333333` (`se = 0.0033333333`): `abs_z = 2.11 < threshold 3.0`. **abs_z = 2.11 < 3.0 → PASS.** (CONVERGENCE gate: a SMALL |z| is the PASS direction.)
- **G4 — SHIFT start (2,1) bends the finish to Beta(2,1)** (direction: exact-agreement to Beta(2,1) + mean shifts many σ from 1/2). The exact black-count law matches Beta-binomial(n; 2, 1): `exact_max_abs_deviation = "0"`; and the Monte-Carlo mean terminal share `mc_mean_share = 0.6665581281` lands at the predicted `predicted_mean = 0.6666666667` and is many σ ABOVE 1/2: `z_vs_half = 100.9484 > threshold 3.0`. **exact_max_abs_deviation == "0" AND z_vs_half = 100.9484 large → PASS.** (Dual-direction gate: exact identity + large shift-z.)
- **G5 — determinism** (direction: byte-identical). In-process double-run `IDENTICAL` AND two separate-invocation processes diff **exit 0**. **PASS.**

Overall: gates {G1:true, G2:true, G3:true, G4:true, G5:true}, `all_gates_pass: true`, no first-failing gate.

## Grounding

- External, sha1-pinned: Wikipedia "Pólya urn model", oldid **1334383855**, raw-wikitext sha1 `ac150a6b0ddb3f3d3f8d54b040ce1ed29a0fbbf8` (byte-pinned; matches the disclosed grounding token).
- Firsthand support for the martingale / Beta-limit CORE: **"It is a martingale and converges to the beta distribution when n → ∞."** This is exactly the limit leg of the head — the black fraction is a bounded martingale whose limit law is Beta.
- Firsthand support for the uniform-finish leg: the page carries the symmetric **x = y = 1 → uniform 1/(n+1)** worked example directly, which is precisely the G1 identity (every black-count equally likely).
- **Scope assessment (the load-bearing honesty check):** the page states the general Beta(α, β) limit and gives the symmetric x=y=1 → uniform result as its own worked example. The proposal's split — symmetric start ends Uniform(0,1), shifted (2,1) start ends Beta(2,1) — is a FAIR reading of the source: the uniform result IS the on-page worked example of the general-Beta statement, and the shift to Beta(2,1) is the same general formula at (α,β)=(2,1). No over-claim; the general-Beta / symmetric-uniform structure is on-page.

## Novelty

Distinct from every prior head. Search across `ideas/**` for Pólya / Polya urn / reinforcement / rich-get-richer / preferential-attachment returns nothing prior as a built head. Adjacent but distinct: martingale/optional-stopping heads (this is a martingale CONVERGENCE to a non-degenerate Beta limit, not a stopping identity); the balls-in-urns / occupancy heads (no reinforcement dynamic). No prior head computes the Pólya black-count law or the Beta terminal-share result.

## Ruling evidence summary

VERDICT 221 reproduces PROPOSAL 208 bit-exact: the verifier copied byte-identical (diff exit 0), the results-dict sha256 `d566e380865bfb7089d5042ed7169edfddc7cab7f112af80de6ef2c29c91aa68` matches the disclosed digest across all 64 hex characters — printed AND independently recomputed outside the verifier (0 divergence) — and determinism holds (in-process double-run IDENTICAL AND two cross-invocation processes byte-identical, diff exit 0). All five pre-registered gates PASS each read in its own direction: G1's EXACT-Fraction uniform black-count law (`max_abs_deviation="0"` over n=1..20 vs 1/(n+1); self-certifying), G2's HIGH-z LLN separation (z=6605.4714, observed share-variance 0.0838204573 vs LLN null 0.00125 — reinforcement keeps the spread), G3's LOW-z convergence (mc_middle_third 0.3263 vs exact 1/3, abs_z=2.11<3), G4's SHIFT identity + effect (`exact_max_abs_deviation="0"` vs Beta-binom(2,1), mc_mean_share 0.6665581281, z_vs_half=100.9484), and G5's determinism. The martingale/Beta-limit core is externally grounded to a sha1-pinned Wikipedia revision (oldid 1334383855, wikitext sha1 `ac150a6b0ddb3f3d3f8d54b040ce1ed29a0fbbf8`) via "It is a martingale and converges to the beta distribution when n → ∞" plus the symmetric x=y=1 → uniform 1/(n+1) worked example, with the symmetric-uniform / shifted-Beta split a FAIR reading of the on-page general-Beta statement. The head is genuinely distinct from prior shipped heads. Source commit `cc60755`. **Ruling: APPROVE.**

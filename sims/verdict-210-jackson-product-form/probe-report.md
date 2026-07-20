# VERDICT 210 — Jackson product-form independence: reproduce PROPOSAL 197

- **Slice:** VERDICT 210 · PROPOSAL 197 (P197 → V210, +13 offset)
- **Source proposal:** idea-engine `control/outbox.md` `## PROPOSAL 197 · 2026-07-20T04:40:15Z · status: sim-ready`
- **Verifier (source):** idea-engine `ideas/fleet/jackson-product-form-independence.py` (landed origin/main squash `8b57115`, PR #733)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-210, HEAD-synced idea-engine `8b57115` / sim-lab `f9191f3`
- **Timestamp (date -u):** 2026-07-20T05:14:24Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`) · Z_GATE=3.0

## Head

In an OPEN network of M/M/1 stations that feed each other with feedback routing,
the internal flow between stations is provably **not Poisson** (bursty, CV²≠1),
yet the joint stationary queue-length law factors **EXACTLY** into independent
M/M/1 marginals

    π(n₁,…,n_M) = ∏ᵢ (1−ρᵢ) ρᵢ^{nᵢ},   ρᵢ = λᵢ/μᵢ,

where the λᵢ solve the traffic equations λᵢ = λ0ᵢ + Σⱼ λⱼ R_{ji}, and the
equal-time cross-station correlation is **exactly zero**. Coupled feedback queues
are instantaneously independent M/M/1s (Jackson 1957 / BCMP). The counter-intuitive
point: product-form independence is INSENSITIVE to how bursty the internal flow is.

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` → **exit 0**.
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process exit 0.
- **Results-dict sha256 (compact-canonical, `sort_keys=True, separators=(",",":")`):**
  `29d55fa57612782046831e792beb1584cb5c688bc181b6363d12774b56cae258`
  — **EXACT MATCH** to the disclosed PROPOSAL 197 digest across all **64** hex
  characters (byte-for-byte string equality, hex-char count = 64, no truncation).
- Run scale: `n_events = 800000`, `n_batches = 30`, `warmup_events = 50000` per set.

## Determinism

- **In-process double-run** — `main()` serializes the results dict twice and asserts
  `j1 == j2` ("in-process double-run mismatch" otherwise); assertion holds, exit 0.
- **Separate cross-invocation** — two independent Python invocations produced the
  identical results-dict sha256 `29d55fa…cae258` = `29d55fa…cae258` → **byte-identical**.

## Exact-arithmetic self-certification (the load-bearing evidence)

The EXACTLY-TRUE gate is not a statistical estimate — it is exact rational
arithmetic. The verifier constructs the closed-form product measure
π(n)=∏(1−ρᵢ)ρᵢ^{nᵢ} with ρᵢ as exact `fractions.Fraction`, solves the traffic
equations in exact rationals (traffic-equation residual **0**), and checks that
this measure satisfies the CTMC global-balance equations at every interior state
of the 0..3 cube:

- **Set 1** (`set1_strong_feedback`, ρ = 1/2, 4/7, 2/3):
  `exact_balance_max_abs_residual = 0/1` over **64** states.
- **Set 2** (`set2_partial_cycle`, ρ = 4/7, 2/3, 1/2):
  `exact_balance_max_abs_residual = 0/1` over **64** states.

A zero residual in `Fraction` arithmetic is self-certifying: the product measure
IS the stationary distribution, with no sampling error, and is independently
re-checkable state-by-state. This is what makes the APPROVE clean.

## Gate evaluation (against PROPOSAL 197's OWN criteria, in order)

- **G1 — EXACTLY-TRUE:** exact-Fraction product measure solves CTMC global balance,
  `exact_balance_max_abs_residual = 0/1` over 64 interior states for **both** param
  sets; traffic-equation residual 0. **g1_pass = true.**
- **G2 — ≥3σ NON-POISSON** (SIGNAL gate — a LARGE z is the PASS condition): the
  merged feedback stream into the feedback station is genuinely non-Poisson.
  - Set 1: feedback_station=1, CV²=1.404111, cv2_se=0.019995,
    **z_nonpoisson = 20.210254 ≥ 3 → PASS** (arrivals_recorded 246263, 30 batches).
  - (Set 2 is a weaker-feedback configuration: CV²=1.008110, z_nonpoisson=2.066678
    — closer to Poisson; the ≥3σ non-Poisson demonstration is carried by Set 1, and
    Set 2 shows the independence STILL holds even when the internal flow is nearly
    Poisson.)
  - **g2_pass = true.**
- **G3 — PRODUCT-FORM-HOLDS** (AGREEMENT gate — a SMALL z is the PASS condition):
  marginal means match the M/M/1 closed form and equal-time cross-station
  correlations are zero, all |z| < 3.
  - Set 1 marginal means: 1.001852 vs 1.0 (z=0.133253), 1.347086 vs 1.333333
    (z=0.575864), 2.044631 vs 2.0 (z=0.983478) — all < 3.
  - Set 1 pairwise correlations: 1-2 z=0.233043, 1-3 z=0.336708, 2-3 z=0.455705 — all < 3.
  - Set 2 marginal means: 1.348295 vs 1.333333 (z=1.224147), 2.035241 vs 2.0
    (z=1.098711), 0.992916 vs 1.0 (z=0.591916) — all < 3.
  - Set 2 pairwise correlations: 1-2 z=0.677484, 1-3 z=0.424487, 2-3 z=0.395371 — all < 3.
  - **g3_pass = true.**
- **G4 — ROBUSTNESS:** Set 2 (`set2_partial_cycle`, a different routing matrix +
  service rates, ρ = 4/7, 2/3, 1/2) independently re-passes both the EXACTLY-TRUE
  (residual 0/1 over 64 states) and PRODUCT-FORM-HOLDS (all |z| < 3) gates — the
  result is not an artifact of one parameterization. **g4_pass = true.**

**all gates pass in order**, first failing gate = none.

## Grounding

- **Source:** Wikipedia "Jackson network" oldid **1358616430**, raw wikitext
  (`action=raw`, MediaWiki API).
- **Fetch:** raw-wikitext sha1 `2bb20c407ea3d109bc936dabc7039de2f671b7cb` —
  **EXACT MATCH** to the disclosed pin (MediaWiki-API confirmed).
- **Content:** the wikitext states the Jackson-network product-form theorem — the
  stationary distribution factors as a product of per-station M/M/1 terms
  ∏ᵢ (1−ρᵢ) ρᵢ^{nᵢ} with the utilizations ρᵢ = λᵢ/μᵢ driven by the traffic
  (rate) equations — and notes that the internal flows in a network with feedback
  are **not in general Poisson**, which is exactly the tension the verifier
  demonstrates (non-Poisson internal flow, yet exact product-form independence).

## Ruling evidence summary

Digest matches full-64 exact; verifier byte-identical (diff exit 0); deterministic
(in-process double-run + cross-invocation byte-identical); the EXACTLY-TRUE gate is
exact-rational with zero global-balance residual over 64 states for both param sets
(self-certifying, no sampling); G2 delivers a genuine ≥3σ non-Poisson signal
(z=20.21, Set 1), G3 confirms product-form marginals + zero cross-correlation (all
|z|<3, both sets), G4 re-passes on a second configuration; grounding resolves
byte-exact and states the product-form theorem + non-Poisson-internal-flow fact.
Exact self-certifying identity + externally grounded head → a **clean APPROVE**.
Final ruling is the coordinator's: **APPROVE**.

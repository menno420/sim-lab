# VERDICT 211 — Pandora's Box reservation-index rule: reproduce PROPOSAL 198

- **Slice:** VERDICT 211 · PROPOSAL 198 (P198 → V211, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 198 — Weitzman's Pandora's Box: the optimal search order IGNORES expected rewards
- **Verifier (source):** idea-engine `ideas/venture-lab/pandora-box-reservation-index-2026-07-20.py` (git blob `68c692db226f53087ff3a496a3e7dbb4419a4d75`, origin/main `a69cc7c`)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-211, HEAD-synced idea-engine `a69cc7c` / sim-lab `af94513`
- **Timestamp (date -u):** 2026-07-20T05:26:39Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `itertools`, `json`, `math`, `random`, `fractions`) · Z_GATE=3.0

## Head

In sequential search with costly inspection (Weitzman 1979), N closed boxes each
cost `c_i` to open and reveal a reward `R_i` drawn from a known discrete
distribution; you open boxes one at a time (paying each cost), may stop at any
moment, and collect the single best reward seen (outside option 0, no
discounting). The optimal policy does **NOT** open boxes in decreasing order of
expected reward. It assigns each box a **reservation value** `z_i` solving

        c_i = E[(R_i − z_i)^+]

and opens boxes in decreasing order of `z_i`, stopping the moment the best reward
in hand ≥ the largest reservation value among the still-closed boxes. Three
exactly-true consequences: (a) you can rationally DECLINE a box whose expected
prize exceeds every value already held; (b) a LOWER-MEAN, higher-spread box can be
optimal to open FIRST; (c) the index-rule expected value **EXACTLY equals** the
brute-force optimum over ALL policies (Weitzman's theorem) — the simple index
rule leaves nothing on the table.

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` → **exit 0** (git blob `68c692db226f53087ff3a496a3e7dbb4419a4d75` on both sides).
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process **exit 0**.
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True, separators=(",",":"))`):**
  `a0cb19cc5574c17ea982580f1546a46ece84d9a32fbd06beb1e3290cacd1fcad`
  — **EXACT MATCH** to the disclosed PROPOSAL 198 digest across all **64** hex
  characters (byte-for-byte string equality, hex-char count = 64, no truncation).
  The verifier also PRINTS this digest (`RESULTS_SHA256=…`); an independent
  out-of-band recompute (`hashlib.sha256(v.canonical(v.compute()))`) reproduces the
  same 64 hex — both agree.
- Digest posture: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the compact-canonical
  results dict's own sha256 IS the digest; it is not a field inside the dict.
- Run scale: `N_boxes = 4`, `M_instances = 400` per regime, two regimes (base + costs×3).

## Determinism

- **In-process double-run** — `main()` calls `compute()` twice and asserts
  `canonical(r1) == canonical(r2)` ("non-deterministic: double-run diverged"
  otherwise); assertion holds, exit 0. Independently re-verified: two in-process
  `compute()` canonical serializations are byte-identical.
- **Separate cross-invocation** — two independent `python3` invocations produced
  **byte-identical stdout** (`cmp` clean), hence the identical results-dict sha256
  `a0cb19c…1fcad`. A fresh `random.Random(SEED)` is created at the start of each
  `compute()`, so in-process and cross-invocation both reproduce identically.

## Exact-arithmetic self-certification (the load-bearing evidence)

The EXACTLY-TRUE gate is not a statistical estimate — it is exact rational
arithmetic. Reservation values `z_i` are solved as exact `fractions.Fraction`
(the solver reconstructs `E[(R−z)^+]` and asserts it equals `c` EXACTLY on the
returned root); all three policy evaluators — brute-force `optimal_value`,
forced-index `index_policy_value`, mean-greedy `greedy_mean_value` — recurse over
the search tree in exact `Fraction`, ZERO floating point. The G1 equality
`index_policy_value == optimal_value` is therefore an exact-rational identity per
instance, not a tolerance test. Only the G2/G4 surprise z-score (which needs a
square root) touches float, and is rounded to 10 dp for byte-stable serialization.
An exact `Fraction` equality is self-certifying and independently re-checkable
instance-by-instance — this is what makes the APPROVE clean.

## Gate evaluation (against PROPOSAL 198's OWN criteria, in order)

- **G1 — EXACT (index == optimal):** the reservation-index policy value equals the
  brute-force optimum for EVERY instance, both regimes, in exact `Fraction`.
  `base_mismatch_count = 0` (over 400) and `shift_mismatch_count = 0` (over 400) —
  **0 mismatches / 800 instances**. This is the firsthand proof of Weitzman's
  theorem (the index rule is optimal). **g1_pass = true.** *(core proof)*
- **G2 — SURPRISE (≥3σ regret vs mean-greedy)** — a LARGE z is the PASS condition:
  the mean-greedy heuristic is genuinely, significantly SUBOPTIMAL vs the
  reservation-index optimum. Mean regret (optimal − greedy) = `0.6668916165`
  (exact `3913166353771/5867769600000`), std `0.7876…`, **`z_regret = 15.507320578
  ≥ 3`**, positive regret on **289/400** instances. **g2_pass = true.**
- **G3 — NON-MONOTONICITY witness** — reservation order ≠ expected-reward order and
  the optimum opens a lower-mean box first / declines a higher-mean box:
  - `z_order_ne_mean_order_count = 305 / 400` (reservation order differs from the
    mean order),
  - `lower_mean_opened_first_count = 153 / 400` (optimum opens a strictly-lower-mean
    box FIRST),
  - `decline_higher_mean_count = 236 / 400` (index-optimal policy STOPS at a
    reachable state while an unopened box still has E[R] > best in hand),
  - **witness:** the optimum opens **box 1** (mean `17/3`, z `34/5`) BEFORE the
    higher-mean **box 0** (mean `29/4`, z `16/3`); optimal value `55/9`, index value
    `55/9` (equal), mean-greedy value `11/2` (strictly worse). A lower-mean box is
    opened first and the mean-greedy heuristic leaves `55/9 − 11/2 = 1/18` on the
    table on this instance.
  - **g3_pass = true.**
- **G4 — ROBUSTNESS / SHIFT (costs × 3):** the shifted regime independently
  re-passes both the EXACT gate (`mismatch_count = 0` over 400) and the surprise
  gate — mean regret `3.7351738463`, **`z_regret = 19.0496891702 ≥ 3`**, positive
  regret on `321/400`. The result is not an artifact of one cost scale.
  **g4_pass = true.**

**all gates pass in order**, `first_failing_gate = null`, `all_pass = true`.

## Grounding

- **Source:** Wikipedia "Search theory" oldid **1347561989**, raw wikitext
  (`index.php?title=Search_theory&oldid=1347561989&action=raw`, MediaWiki API).
- **Fetch:** revision resolves (HTTP 200, 20419 bytes); raw-wikitext sha1
  `1f24a2c787536d8aa6cfd57447678b1a7a8ccd13` — **EXACT MATCH** to the disclosed pin.
- **Content:** the revision states the Pandora's-box model AND the reservation/index
  rule in prose. It introduces "Pandora box problems … introduced by Martin
  Weitzman" (citing Weitzman 1979, *Optimal Search for the Best Alternative*,
  Econometrica 47(3):641–654) and states: "Pandora associates to each box a
  **reservation value**. Her optimal strategy is to open the boxes by decreasing
  order of reservation value until the opened box that maximizes her payoff exceed
  highest reservation value of the remaining boxes. This strategy is referred as
  the Pandora's rule." — exactly the decreasing-`z_i` index rule the verifier
  proves.
- **Disclosed caveat (judged fairly disclosed):** the DEFINING equation
  `c_i = E[(R_i − z_i)^+]` is in the on-page-cited Weitzman 1979 primary source, not
  written in this revision's prose (the revision names the reservation value and the
  opening/stopping rule but does not spell out the equation that defines `z_i`). The
  caveat was disclosed up front; the reservation-value + index/stopping rule — the
  claim the verifier actually reproduces — IS stated in the revision, and the
  defining equation is one click away in the cited primary. Fair.

## Ruling evidence summary

Digest matches full-64 exact (`a0cb19c…1fcad`, printed + independently recomputed,
both agree, 64 hex no truncation); verifier byte-identical (diff exit 0, blob
`68c692d`); deterministic (in-process double-run assert + cross-invocation
byte-identical stdout); the EXACT gate G1 is exact-rational `index_policy_value ==
optimal_value` with **0 mismatches over 800 instances** across both regimes —
a firsthand, self-certifying proof of Weitzman's optimality theorem, not a
sampling estimate; G2 delivers a genuine ≥3σ surprise (`z_regret=15.51`,
positive regret 289/400) showing mean-greedy is significantly suboptimal; G3
exhibits non-monotonicity with a concrete `Fraction` witness (box 1 opened before
higher-mean box 0; 305/400 order-flips, 236/400 declines); G4 re-passes under
costs×3 (0 mismatches, `z_regret=19.05`); grounding resolves byte-exact and states
the Pandora's-box model + reservation/index rule, with the defining-equation-in-
cited-primary caveat fairly disclosed. Exact self-certifying identity + externally
grounded head → **APPROVE**. Final ruling is the coordinator's: **APPROVE**.

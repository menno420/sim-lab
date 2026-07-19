# VERDICT 178 — memoryless-pm-waste: probe report (reproduced)

Answers to the born-red session-card probe questions, filled with the actual
numbers reproduced this session from the byte-identical P165 verifier
(`sims/verdict-178-memoryless-pm-waste/memoryless_pm_waste.py`, SEED = 20260717
pinned in-source at line 56). Full stdout is captured in `run-stdout.txt`.

**Math sanity note (age-replacement renewal reward on an exponential).** Lifetime
L ~ Exp(λ). Policy(T) renews at min(L, T): if L ≤ T the renewal is an unplanned
failure (cost c_fail), else a planned replacement (cost c_plan), with
c_fail > c_plan. For the exponential, E[cycle] = (1 − e^{−λT})/λ and
P(L ≤ T) = 1 − e^{−λT}, so the long-run failure rate = P(L≤T)/E[cycle] = **λ for
EVERY T** — the memoryless invariance: a survived unit is as-good-as-new, so the
threshold T is invisible to the failure process. The long-run cost rate, by
contrast, strictly RISES as T shrinks (run-to-failure is the T→∞ limit). The
reproduced closed forms confirm this: `theory.exp_failure_rate_invariant = 1.0`,
`theory.exp_rtf_cost_rate = 5.0` (= λ·c_fail), and
`theory.exp_pm_cost_rate = 6.541494` (T_PM = 0.5) — the Monte-Carlo means
(`base.rtf_cost_rate = 5.000151`, `base.pm_cost_rate = 6.541129`) match the closed
forms to sampling error. The benefit of age-replacement is a property of an
INCREASING hazard (Weibull shape k > 1, wear-out), reproduced here as a disclosed
NON-GATED crossover (see Q3).

---

**1. Does the results-dict sha256 reproduce the disclosed digest EXACTLY across a fresh cross-invocation double-run AND the script's in-process double-run assert, computed over the COMPACT-canonical serialization (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)? State the reproduced digest.**

Yes. Reproduced compact-canonical results-dict sha256:
`0a9c4406e8abc9a6fa51b80a0101c6f55277f3304c3d8b468b13f4600424bd69`
— EQUAL to the disclosed digest. It reproduces three independent ways: (a) the
script's own in-process double-run assert (`assert h1 == h2` in `main()`) passes
and the script prints `Results-JSON sha256: 0a9c4406…24bd69`; (b) two fresh
`SEED=20260717 python3` invocations produced byte-identical stdout (`diff`
exit 0), both exit 0; (c) an independent recomputation over the compact-canonical
serialization (`json.dumps(obj, sort_keys=True, separators=(",",":"))` → sha256
of the UTF-8 bytes, floats rounded to 6 dp, no self-referential digest field,
nothing written to disk) yields the same digest. Posture confirmed WHOLE-DICT /
NO-SELF-FIELD / STDOUT-ONLY.

**2. Is the verifier byte-identical to the P165 source at its pinned idea-engine identity (`diff` exit 0, file sha256 / git blob / byte count / line count)? State the exit codes and the pinned identity.**

Yes. The verifier was extracted from idea-engine at merge SHA `c1282fa`
(`ideas/fleet/memoryless_pm_waste.py`, added by PR #642) and copied unchanged.
`diff` between the idea-engine source and the committed copy exits 0.
Pinned identity (source == copy):
- file sha256 `0c12b3235a951ac219e2248a690938edf0d56496d42c737ecff9780bb8e85ff3`
- git blob `0c87ccf8a279bdfdeed1a8519eba9afd06c1be3c`
- 9446 bytes, 258 lines
- stdlib only (`math, json, hashlib, random`)

**3. Do all three gates PASS in the pre-registered order (z_gate = 3.0), all_pass=true, first_failing_gate=null, exit 0?**

Yes — `all_pass = true`, `first_failing_gate = null`,
`gates = {G1_cost_penalty: true, G2_benefit_absent: true, G3_robustness: true}`,
exit code 0 (`main()` raises `SystemExit(0 if all_pass else 1)`). Reproduced
statistics, read VERBATIM from the stdout JSON — **note the ACTUAL verifier gates
differ from the card's pre-registered Gate plan (documented under Q7 below):**

- **G1_cost_penalty** (`z_cost ≥ 3` one-sided AND `cost_penalty_pct > 0`): base
  `pm_cost_rate = 6.541129` vs `rtf_cost_rate = 5.000151`,
  `cost_penalty_pct = 30.81864`, `z_cost = +362.634738` → PASS. The
  age-replacement policy costs strictly MORE per unit time than run-to-failure.
- **G2_benefit_absent** (`z_benefit ≥ 3`, directional): a promised
  10%-of-λ failure-rate reduction (`promised_reduction = 0.1`) is REJECTED against
  the observed `failure_rate_reduction = 8.1e-05` (`pm_failure_rate = 0.999949`
  vs `rtf_failure_rate = 1.00003`), `z_benefit = +111.984471` → PASS. The failure
  rate is unchanged at λ — PM buys zero reliability gain.
- **G3_robustness** (under a SHIFTED exponential λ'=1.7, c_fail'=8.0, T'=0.3:
  `z_cost ≥ 3` AND `z_benefit ≥ 3` AND `cost_penalty_pct > 0`):
  `pm_cost_rate = 16.149977` vs `rtf_cost_rate = 13.598299`,
  `cost_penalty_pct = 18.764686`, `z_cost = +159.820952`;
  `promised_reduction = 0.17` vs `failure_rate_reduction = 0.000595`
  (`pm_failure_rate = 1.699192` vs `rtf_failure_rate = 1.699787`),
  `z_benefit = +82.044394` → PASS. G1 and G2 both hold again under a different
  rate, cost pair, and threshold.

**Weibull wear-out regime — an ACTUAL GATE or a disclosed NON-GATED field?**
It is a **disclosed NON-GATED diagnostic**, reported under the `crossover` key,
NOT a gate. Reproduced: `weibull_shape = 2.5`, `weibull_best_t = 0.55`,
`weibull_best_cost_rate = 3.071961`, `weibull_rtf_cost_rate = 5.0`,
`weibull_beats_rtf = true` — an increasing-hazard Weibull at the same mean life
admits a finite T* (≈ 0.55) whose long-run cost rate (3.071961) BEATS
run-to-failure (5.0). The verifier's own docstring (lines 25, 42–43) states this
explicitly: "The paradox dissolves for a Weibull wear-out lifetime (disclosed
crossover, non-gated)." It bounds the claim but is not enforced as a gate.

**4. Is the headline read correctly — on a memoryless / constant-hazard component the failure rate under an age-replacement policy equals λ for every interval τ, so preventive maintenance adds cost for zero reliability gain, and the benefit reappears only once the hazard is increasing — and NOT "preventive maintenance always reduces the failure rate, so a shorter PM interval always buys fewer failures"?**

Yes. Reproduced: the age-replacement failure rate equals λ to Monte-Carlo
precision (`pm_failure_rate = 0.999949` ≈ `rtf_failure_rate = 1.00003` ≈ λ = 1.0;
`failure_rate_reduction = 8.1e-05`, i.e. essentially zero against a promised 0.1),
while the cost rate is strictly higher (`cost_penalty_pct = 30.82%`). The folk
belief "shorter PM interval always buys fewer failures" is directly falsified —
the interval T is invisible to the failure process on a constant hazard. The
benefit reappears only once the hazard increases: the disclosed Weibull(2.5)
crossover shows a finite T*=0.55 beating run-to-failure (`weibull_beats_rtf =
true`). Head SIGN reproduced exactly.

**5. Is the model-basis caveat correctly weighed as CONSERVATIVE-DIRECTION / DISCLOSED-DESCRIPTIVE (a clean posture, not a defect)?**

Yes, as a caveat — the failure-rate invariance is an EXACT property of the
exponential renewal model: the reproduced closed forms
(`exp_failure_rate_invariant = 1.0`, `exp_rtf_cost_rate = 5.0`,
`exp_pm_cost_rate = 6.541494`) match the Monte-Carlo means to sampling error, and
the SIGN (PM leaves the failure rate at λ and only adds cost; the benefit needs an
increasing hazard) is distribution-independent within the class. The one declared
modelling choice — a single-component renewal process with instantaneous perfect
replacement and equal-cost accounting — is flagged in the docstring, not hidden:
downtime-avoidance value, imperfect maintenance, and repair-vs-replace logistics
are disclosed descriptive fields that could shift the exact cost figures but not
the failure-rate SIGN. This caveat, on its own, supports a clean posture. The
qualification on the overall verdict (Q7) is a separate matter — the plan-vs-
verifier GATE divergence — not this model caveat.

**6. Could the failure-rate invariance be a seed fluke? Is the effect structural, and is determinism confirmed both ways?**

Not a seed fluke — the effect is structural. The failure rate sits at λ in BOTH
the base world (`pm_failure_rate = 0.999949` vs λ = 1.0) and the shifted world
(`pm_failure_rate = 1.699192` vs λ' = 1.7), and the closed-form
`exp_failure_rate_invariant = 1.0` confirms the invariance is algebraic
(P(L≤T)/E[cycle] = λ for every T), not a chance seed alignment. The cost penalty
is enormous (`z_cost = +362.63` base, +159.82 shifted) and the benefit-absence
z is +111.98 base / +82.04 shifted, over 30 replicates each. Determinism confirmed
both ways: (a) the script's in-process double-run assert (`assert h1 == h2`)
passes before printing; (b) two fresh `SEED=20260717 python3` invocations produced
byte-identical stdout (`diff` exit 0), both exit 0, both printing
`Results-JSON sha256: 0a9c4406…24bd69`. Single `random.Random(20260717)` stream;
`rng.expovariate` is the only stochastic call; all dict floats rounded to 6 dp
before serialization.

**7. Plan-vs-verifier gate divergence (documented, as V177 did for its G3).**

The born-red card's **Gate plan** section pre-registered a different gate set than
the committed P165 verifier actually implements. This is disclosed here explicitly
and the ruling is judged against the VERIFIER's actual gates:

| Slot | Card's planned gate | Verifier's ACTUAL gate |
|------|---------------------|------------------------|
| G1 | `head_pm_waste` — total maintenance ACTIONS under PM > run-to-failure (one-sided z ≥ 3), failure count not reduced | `G1_cost_penalty` — long-run COST RATE(PM) − COST RATE(RTF) > 0 at z ≥ 3 (measures cost rate, not action count) |
| G2 | `mechanism_memoryless` — ANCHOR / MATCH gate, `\|z\| < 3`: age-replacement failure rate EQUALS λ | `G2_benefit_absent` — DIRECTIONAL z ≥ 3 REJECTING a promised 10%-of-λ reduction (not a two-sided match gate) |
| G3 | `wearout_reverses` — increasing-hazard Weibull (k > 1), PM STRICTLY reduces the failure count, z ≥ 3 (a GATE) | `G3_robustness` — under a SHIFTED exponential (λ', costs', T'), G1 and G2 both hold again |
| — | (Weibull was the planned G3) | Weibull wear-out present only as a NON-GATED disclosed `crossover` field |

The divergence is broader than V177's (which reframed a single gate, G3). Here two
of the three gates differ in KIND (G2: a directional benefit-rejection instead of
a `|z| < 3` anchor match; G3: a shifted-exponential robustness gate instead of the
Weibull wear-out reversal), plus G1 measures cost rate rather than action count,
and the head's essential "benefit reappears under increasing hazard" clause — the
Weibull wear-out reversal — is exercised only as a NON-GATED diagnostic, not a
pre-registered gate. The verifier is internally consistent: its own docstring
(lines 36–43) documents exactly this gate set and labels the Weibull crossover
"non-gated." The HEAD claim SIGN is fully reproduced by the verifier's gates
(G2's near-zero measured reduction confirms the memoryless invariance; the
crossover field confirms Weibull beats RTF); it is the gate STRUCTURE that
diverges from the card plan.

---

## Recommendation: QUALIFIED-APPROVE

Reproduction is defect-free: the compact-canonical digest reproduces the disclosed
`0a9c4406…24bd69` EXACTLY three ways; the verifier is byte-identical to the P165
source at idea-engine `c1282fa` (`diff` exit 0, blob `0c87ccf8…`, sha256
`0c12b323…`, 9446 bytes / 258 lines); all three gates PASS in order
(`all_pass = true`, `first_failing_gate = null`), exit 0; determinism is confirmed
both ways; and the reproduced Monte-Carlo means match the closed forms
(`exp_pm_cost_rate 6.541494 ≈ 6.541129`, `exp_rtf_cost_rate 5.0 ≈ 5.000151`,
`exp_failure_rate_invariant 1.0`). The head SIGN — memoryless PM adds cost for
zero failure-rate reduction, benefit only under increasing hazard — reproduces
exactly.

The verdict is **QUALIFIED** (not clean) for one honest reason, and it is a
plan-vs-verifier matter, not a reproduction defect: the committed verifier's gate
STRUCTURE diverges from the card's pre-registered Gate plan on two of three gates
(G2 is a directional benefit-rejection, not the planned `|z| < 3` anchor match;
G3 is a shifted-exponential robustness gate, not the planned Weibull wear-out
reversal), and the headline's "benefit reappears once the hazard is increasing"
clause is exercised only as a NON-GATED disclosed `crossover` field
(`weibull_beats_rtf = true`, T*=0.55, cost 3.071961 < 5.0), never enforced as a
gate. The verifier is internally consistent and self-discloses this posture; the
qualification records that the enforced gate set is not the one the card
pre-registered, and that the wear-out half of the thesis is diagnostic rather than
gated. Everything the verifier actually gates reproduces cleanly.

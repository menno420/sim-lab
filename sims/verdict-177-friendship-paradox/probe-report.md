# VERDICT 177 — friendship paradox: probe report (reproduced)

Answers to the born-red session-card probe questions, filled with the actual
numbers reproduced this session from the byte-identical P164 verifier
(`sims/verdict-177-friendship-paradox/friendship_paradox.py`, SEED = 20260717
pinned in-source). Full stdout is captured in `run-stdout.txt`.

**Math sanity note (size-bias identity).** Following an edge to a neighbor is a
*size-biased* draw over nodes: node *i* is reached with probability
proportional to its degree, k_i / Σ_j k_j, so high-degree nodes are
over-represented exactly in proportion to their degree. The mean degree of that
size-biased endpoint is therefore the friend mean
ν = Σ k_i² / Σ k_i = <k²>/<k>, whereas a uniformly random person has the plain
mean μ = <k>. Since <k²> = <k>² + Var(k), the two factor as
ν = <k>+ Var(k)/<k> = μ + Var(k)/μ, so the friend−person gap is exactly
ν − μ = Var(k)/μ ≥ 0, strict whenever Var(k) > 0. This is why the friend mean
is E[k] + Var(k)/E[k], not E[k].

---

**1. Does the results-dict sha256 reproduce the disclosed digest EXACTLY across a fresh cross-invocation double-run AND the script's in-process double-run assert, computed over the COMPACT-canonical serialization (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY)? State the reproduced digest.**

Yes. Reproduced compact-canonical results-dict sha256:
`0df9954e7378ae4c896e892c4614ff2967a117b646276fdde3f21ec874b0bd4f`
— EQUAL to the disclosed digest. It reproduces three independent ways: (a) the
script's own in-process double-run assert (`assert h1 == h2`) passes and the
script prints `Results-JSON sha256: 0df9954e…b0bd4f`; (b) two fresh `python3`
invocations produced byte-identical stdout (`diff` exit 0); (c) an independent
recomputation over the compact-canonical serialization
(`json.dumps(results, sort_keys=True, separators=(",",":"))` → sha256 of the
UTF-8 bytes, floats rounded to 6 dp, no self-referential digest field, nothing
written to disk) yields the same digest. Posture confirmed WHOLE-DICT /
NO-SELF-FIELD / STDOUT-ONLY.

**2. Is the verifier byte-identical to the P164 source at its pinned idea-engine identity (`diff` exit 0, file sha256 / git blob / byte count / line count)? State the exit codes and the pinned identity.**

Yes. The verifier was extracted from idea-engine at merge SHA `1145ecd`
(`git show 1145ecd:ideas/fleet/friendship_paradox.py`) and copied unchanged.
`diff` between the extracted source and the committed copy exits 0.
Pinned identity (source == copy):
- file sha256 `df4719e08f99310b993200ccaa59374d3c8fc473c074da04e11efc442a5acee1`
- git blob `b4ba462923d9ca222469d9cd48e8664e3a541024`
- 8167 bytes, 236 lines
- stdlib only (`math, json, hashlib, random`)

**3. Do all three gates PASS in the pre-registered order (z_gate = 3.0; G1 directional z ≥ 3, G2 anchor match |z| < 3, G3 near-zero/robustness), all_pass=true, first_failing_gate=null, exit 0?**

Yes — `all_pass = true`, `first_failing_gate = null`, `gates = [true, true, true]`,
exit code 0. Reproduced statistics:
- **G1 head_friendship_gap** (one-sided z ≥ 3): gap_mean = 0.575478,
  gap_se = 0.012362, z = +46.553724, all_networks_positive = true → PASS.
- **G2 mechanism (size-biased MC vs closed form <k²>/<k>)** (anchor, |z| < 3):
  mean standardized residual z = −0.867047, |z| = 0.867 < 3 → PASS.
- **G3 robustness (heavier tail α = 2.6)** (z ≥ 3 AND gap > base): gap_mean =
  2.011742 > base 0.575478, gap_se = 0.17395, z = +11.565060,
  heavier_tail_bigger_gap = true, all_networks_positive = true → PASS.

Note on the card's G3 framing: the session card describes G3 as
`vanishes_on_regular` (a degree-matched regular control at the same E[k]). The
committed P164 verifier instead implements G3 as a *heavier-tailed shift*
(α 3.5 → 2.6) that keeps the gap ≥ 3σ positive AND strictly larger than base —
the same "the gap is degree-variance-driven, not a mean artifact" claim exercised
from the other direction (grow Var/μ rather than zero it). The reproduced code,
digest, and gate results are governed by the committed verifier; the regular-graph
control is a descriptive re-statement in the card, not what the byte-identical
verifier computes. The head SIGN and mechanism are unaffected.

**4. Is the headline read correctly — neighbor's expected degree strictly exceeds the node's own by exactly Var[k]/E[k], vanishing at Var[k]=0 — and NOT "following an edge samples a typical person"?**

Yes. Reproduced: friend mean ν = <k²>/<k> exceeds person mean μ = <k> by exactly
Var(k)/μ. The identity residual `identity_max_abs_residual = 0.0` (max over all
40 base networks of |(ν−μ) − Var/μ|) confirms the gap IS Var(k)/μ, not an
approximation. `var_over_mean_mean_base = 0.575478` equals the measured
`gap_mean = 0.575478`. The folk "edge-follow samples a typical person, so the
neighbor's expected degree is just E[k]" is inverted: edge-following is size-biased
toward high degree, so the neighbor's expected degree is E[k] + Var(k)/E[k]. The
excess is strict here (Var(k) > 0) and would vanish only on a regular graph.

**5. Is the model-basis caveat correctly weighed as CONSERVATIVE-DIRECTION / DISCLOSED-DESCRIPTIVE (a clean APPROVE, not a defect)?**

Yes. The head is an *objective identity of the degree distribution*: μ = <k> and
ν = <k²>/<k> are pure functionals of the drawn degree sequence, and ν − μ = Var/μ
is exact (residual 0.0). The one declared modelling choice — the degree
distribution is Pareto-tailed integer degrees (α > 2, finite variance) — is
flagged, not hidden. The SIGN of the effect follows from Var(k) ≥ 0 and is
distribution-independent; G3 re-derives it under a different, heavier tail
(α = 2.6), where the gap grows to 2.011742 as Var/μ predicts. Assortativity and
weighted/temporal contact dynamics are disclosed descriptive fields that could
shift the per-person magnitude but not the SIGN. The exact gap figures (0.575478
base, 2.011742 heavier tail) are pinned to (α, DEG_SCALE, N) and flip no gate sign
and no order of magnitude → clean APPROVE posture.

**6. Could the gap sign be a seed fluke? Is the effect structural, and is determinism confirmed both ways?**

Not a seed fluke — the effect is structural. The gap is positive in EVERY one of
the R = 40 base networks (`all_networks_positive = true`) and in every one of the
40 heavier-tail networks, at z = +46.55 (base) and z = +11.57 (heavier tail);
the identity residual 0.0 shows the gap is algebraically Var(k)/μ, not a chance
alignment of one seed. The G2 anchor is two-sided (|z| = 0.87 < 3): the
size-biased Monte-Carlo friend-mean matches the closed form to sampling error, so
a wrong mechanism would show |z| ≫ 3, not a small residual. Determinism confirmed
both ways: (a) the script's in-process double-run assert (`assert h1 == h2`)
passes before printing; (b) two fresh `python3` invocations produced
byte-identical stdout (`diff` exit 0), both exit 0, both printing
`Results-JSON sha256: 0df9954e…b0bd4f`. Single `random.Random(20260717)` stream;
`random.paretovariate` / `random.choices` are the only stochastic calls; all dict
floats rounded to 6 dp before serialization.

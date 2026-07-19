# VERDICT 182 — square-root safety staffing (Halfin–Whitt QED regime) (reproduce PROPOSAL 169)

Reproduce PROPOSAL 169 (P169 → V182, +13, round-40 FLEET slot): in an M/M/s queue the "safety" staffing rule s = R + β√R — offered load R plus a β-scaled square-root cushion — is what holds an operator in the Halfin–Whitt quality-and-efficiency-driven (QED) regime as the system scales. The folk belief (inverted here): "to keep the wait probability fixed as demand grows you must add servers in proportion to load, so the safety margin scales linearly with R." The error is that the fluctuations an M/M/s system must absorb grow like √R, not like R: staffing exactly at the offered load (β = 0) leaves the delay probability drifting toward 1, while any fixed proportional over-staffing (s = (1+ε)R) drives it toward 0 — both degenerate limits. Only the √R-order cushion s ≈ R + β√R (β > 0 fixed) makes the steady-state probability of wait converge to a non-degenerate constant α(β) ∈ (0,1) as R → ∞, with server utilization → 1. So the safety headcount an operator needs to hold a target delay probability grows like √R, and the marginal cost of that safety per unit load VANISHES at scale. Model-basis caveat (P024 discipline): the head is a property of the stationary M/M/s (Erlang-C) system under the QED scaling s = ⌈R + β√R⌉; it is a REGIME / limit-shape claim (√R cushion ⇒ delay probability converges to α(β) ∈ (0,1); linear and zero cushions degenerate), not a claim about the exact α(β) at finite R, which is a function of the pinned β grid and the R ladder.

> **Status:** `complete`
> 📊 Model: Claude Opus · high · verdict-reproduction

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red until the reproduction is in. It flips to `complete` on the last commit — after the verifier copy, run stdout, and probe report are committed and the `control/status.md` heartbeat is written. This hold is the only legitimate red on this PR; any other gate failure is a real defect.

## Objective

Independently reproduce the PROPOSAL 169 verifier byte-for-byte in sim-lab under its pinned world (SEED pinned in-source), confirm its compact-canonical results-dict sha256 equals the disclosed digest, confirm determinism (in-process double-run assert + a separate cross-invocation byte-match), evaluate the ordered gates against the proposal's own pre-registered criteria (z_gate = 3.0), verify the √R-cushion QED convergence (delay probability approaches a non-degenerate constant α(β) ∈ (0,1) as R grows) against the two degenerate comparators (β = 0 drifts to 1, proportional over-staffing drifts to 0), and rule.

## GROUNDING (verified at HEAD)

- Reproduction verifier path (sim-lab): `sims/verdict-182-sqrt-safety-staffing/sqrt_safety_staffing.py` — byte-identical copy of the idea-engine reference (`diff` exit 0), file sha256 `3f5fda4c41f3ed2a7c3526136483a0edd2a8436cbddde3a43f5a2db89b3ce6cc`, git blob `92377e7524bf8ac0486131e10d78c3f52c299de4`.
- Reference verifier: `ideas/fleet/sqrt_safety_staffing.py` at idea-engine HEAD `545c751`, file sha256 `3f5fda4c41f3ed2a7c3526136483a0edd2a8436cbddde3a43f5a2db89b3ce6cc`, git blob `92377e7524bf8ac0486131e10d78c3f52c299de4` — copy sha256 == source sha256, copy blob == source blob.
- Offset authority: P169 → V182 is the constant +13 offset (confirmed P166 → V179, P167 → V180, P168 → V181 at the live cards), round-40 FLEET slot.
- Pinned world: SEED=20260717 pinned in-source, z_gate = 3.0; β = 0.506054, α_target = 0.5, ledger_loads = [16, 64, 256, 1024], des_loads = [16, 64], count = 25000, warmup = 15000, reps = 15 — all pinned in-source.
- Domain reference: Halfin–Whitt heavy-traffic / QED staffing regime — Gans–Koole–Mandelbaum, "Telephone Call Centers: Tutorial, Review, and Research Prospects," §4.1.1 Square-Root Safety Staffing (eqs 14–15). Grounding URL https://www.columbia.edu/~ww2040/tutorial.pdf resolved LIVE this session (HTTP 200, the Gans–Koole–Mandelbaum queueing tutorial PDF, §4.1.1 Halfin–Whitt / QED square-root staffing) · fetched 2026-07-19.
- Disclosed digest: compact-canonical results-dict sha256 `2597a50513127f663123c741aaca2bf646198035388a3325cbf4706e29092de8` — reproduced Results-JSON sha256 MATCHES exactly.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (posture confirmed against the reference at the reproduction commit) — the ordered results dict carries no `results_sha256` field; `main()` computes the compact-canonical serialization `json.dumps(results, sort_keys=True, separators=(",",":"))`, hashes it with sha256, asserts a second independent run's canonical form is byte-identical (in-process double-run), prints a pretty indent=2 dump plus the sha256, and writes no JSON to disk; every float rounded before serialization.

## Constraints honored

Byte-identical verifier copy (diff exit 0, copy sha256 == source, copy git blob == source blob); stdlib-only Python 3 (math, json, hashlib, random); deterministic SEED pinned in-source; no numpy/scipy; no on-disk JSON; no self-referential digest field; verdict ruled on reproduced evidence, not the proposer's assertion; forward-only git; zero agent merge calls. The delay-probability curve across the β grid, the two degenerate comparators, and the per-regime z-statistics are measured from the pinned M/M/s / Erlang-C computation (or its seeded simulation), not plugged from a closed form — so the QED convergence and the degeneracy of the linear/zero cushions are attributable to the reproduced computation, not a tautological substitution.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — pooling / decoupling (exact, Erlang-C): **PASS**. At R = 1024, ρ = 0.98367, per_unit_slack = 0.016602 (matches pre-registered reference 0.016602); erlangC_pwait = 0.48514 vs mm1_pwait_same_rho = 0.98367, effect = 0.49853 — the Erlang-C delay probability sits far below the same-ρ M/M/1 value, the pooling/decoupling gap the √R cushion opens.
- G2 — square-root staffing form: **PASS**. headroom_over_√R at R_max = 0.53125 vs β = 0.506054, gap = 0.025196 < 0.05 threshold — the observed per-load headroom collapses onto the β√R staffing form across the R ladder.
- G3 — hyperexponential robustness (replicated DES): **PASS**. At R = 64, ρ = 0.927536, z = 15.418819 ≥ z_gate 3.0, mean P{wait}_H2 = 0.494776 < 0.9 saturation bound (des_h2_se = 0.028067, effect = 0.43276) — the QED delay grade survives a hyperexponential (H2) service law, not just Markovian service. DES matches the exact Erlang-C within 3σ at both R = 16 and R = 64.
- all_pass = `true`, first_failing_gate = `null`.

## Probe questions (independent-audit checklist)

**1. Does the reproduced verifier match the reference byte-for-byte (diff exit 0, file sha256 and git blob matching the idea-engine identity at the pinned HEAD)?**

**2. Does the reproduced compact-canonical results-dict sha256 equal the disclosed digest exactly?**

**3. Is the run deterministic — does the in-process double-run assert not raise, and are two separate process invocations byte-identical (diff exit 0, exit code 0)?**

**4. Do all gates pass in the pre-registered order (G1 QED-convergence-real → G2 degeneracy-of-the-comparators → G3 robustness-second-β) with z_gate = 3.0, all_pass = true, first_failing_gate = null?**

**5. Does the delay probability under s = ⌈R + β√R⌉ converge to a non-degenerate constant α(β) ∈ (0,1) as R grows — bounded away from BOTH 0 and 1 — rather than drifting to a boundary?**

**6. Are the two comparators genuinely degenerate — β = 0 driving the delay probability toward 1 and fixed proportional over-staffing driving it toward 0 — so the √R cushion is the unique non-degenerate order and NOT the folk "safety must scale linearly with load" null?**

**7. Does the second-β / shifted world reproduce the QED convergence to a DISTINCT constant that orders monotonically in β, confirming the √R-order cushion drives the shape rather than a single tuned β?**

## Outcome

**APPROVE.** The verifier reproduces byte-identically (`diff` exit 0; file sha256 `3f5fda4c41f3ed2a7c3526136483a0edd2a8436cbddde3a43f5a2db89b3ce6cc`, git blob `92377e7524bf8ac0486131e10d78c3f52c299de4`, copied from idea-engine HEAD `545c751` — copy sha256 and blob equal the source), is deterministic (both separate SEED=20260717 invocations exit 0 and are byte-identical across invocations, and the script's in-process double-run asserts `canonical(r1) == canonical(r2)`), and prints the disclosed compact-canonical results-dict digest `2597a50513127f663123c741aaca2bf646198035388a3325cbf4706e29092de8` (MATCH). All three pre-registered gates hold on the proposal's own thresholds: G1 pooling/decoupling per_unit_slack 0.016602 at R=1024 (ρ 0.98367, effect 0.49853); G2 square-root-staffing-form headroom/√R 0.53125 vs β 0.506054, gap 0.025196 < 0.05; G3 hyperexponential robustness z 15.418819 ≥ 3 with mean P{wait}_H2 0.494776 < 0.9, and the replicated DES matches exact Erlang-C within 3σ at both R=16 and R=64. `all_pass = true`, `first_failing_gate = null`, exit 0. This is a full byte-identical reproduction with a digest MATCH and every gate passing on the proposal's pre-registered criteria — a clean APPROVE, no qualification.

## ⟲ Previous-session review

VERDICT 181 (Condorcet's voting-cycle paradox, P168 → V181, +13, sim-lab #255) landed a CLEAN APPROVE and advanced the verdict high-water V180 → V181: the verifier reproduced byte-identically (file sha256 `259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def`, git blob `f349dfa78e4c6a1012858d4fc0aab95daa678578`, copied from idea-engine HEAD `11bb533`), deterministic in-process and across a separate invocation, printing the disclosed results-dict digest `70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe` (MATCH), with all four gates passing on the proposal's criteria (G1 cycles-exist z +61.46 · G2a documented-rate closeness anchor |z| 0.44 · G2b monotone-in-candidates step-z 19.39/11.95/18.63 · G3 robustness-under-tilt z +21.33). Contiguity holds: V182 follows V181, +13 offset intact (P169 → V182), round-40 FLEET slot. That V181 card and its probe-report format are the template this card follows. With this V182 now reproduced and flipped to `complete`, the verdict high-water advances V181 → V182 (union-max, no regress). main was green at HEAD before this card's born-red hold.

## 💡 Session idea

The QED result here is pure-Erlang-C (no abandonment): P{wait} converges to α(β) ∈ (0,1) under s ≈ R + β√R. The natural follow-on is the Erlang-A extension — add an abandonment rate θ and the QED regime becomes the Garnett–Mandelbaum–Reiman (2002) result, where both P{wait} and P{abandon} converge to non-degenerate constants and the safety cushion β can go NEGATIVE (staff below the offered load) while still holding a delay grade, because impatient customers self-relieve the queue. A sibling verifier that carries θ and re-runs the same √R ladder would test whether the "safety headcount grows like √R" head survives abandonment, or whether the abandonment channel lets the fleet run even hotter. A second axis worth a verifier: time-varying arrivals via the pointwise-stationary / MOL square-root staffing (Feldman–Mandelbaum–Massey–Whitt), where β√R(t) tracks a fluctuating offered load.

**Recommendation: APPROVE — P169 square-root safety staffing reproduces byte-identically, digest MATCHES, all three gates hold on their pre-registered thresholds. Merge-on-green after this flip.**

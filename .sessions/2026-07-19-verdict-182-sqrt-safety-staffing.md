# VERDICT 182 — square-root safety staffing (Halfin–Whitt QED regime) (reproduce PROPOSAL 169)

Reproduce PROPOSAL 169 (P169 → V182, +13, round-40 FLEET slot): in an M/M/s queue the "safety" staffing rule s = R + β√R — offered load R plus a β-scaled square-root cushion — is what holds an operator in the Halfin–Whitt quality-and-efficiency-driven (QED) regime as the system scales. The folk belief (inverted here): "to keep the wait probability fixed as demand grows you must add servers in proportion to load, so the safety margin scales linearly with R." The error is that the fluctuations an M/M/s system must absorb grow like √R, not like R: staffing exactly at the offered load (β = 0) leaves the delay probability drifting toward 1, while any fixed proportional over-staffing (s = (1+ε)R) drives it toward 0 — both degenerate limits. Only the √R-order cushion s ≈ R + β√R (β > 0 fixed) makes the steady-state probability of wait converge to a non-degenerate constant α(β) ∈ (0,1) as R → ∞, with server utilization → 1. So the safety headcount an operator needs to hold a target delay probability grows like √R, and the marginal cost of that safety per unit load VANISHES at scale. Model-basis caveat (P024 discipline): the head is a property of the stationary M/M/s (Erlang-C) system under the QED scaling s = ⌈R + β√R⌉; it is a REGIME / limit-shape claim (√R cushion ⇒ delay probability converges to α(β) ∈ (0,1); linear and zero cushions degenerate), not a claim about the exact α(β) at finite R, which is a function of the pinned β grid and the R ladder.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · high · verdict-reproduction

Born-red HOLD: this card's first commit lands `in-progress`, holding the substrate-gate red while the byte-identical verifier copy, run-stdout, and probe-report are committed in a separate reproduction commit; the card flips `complete` last — after the coordinator heartbeat — which releases the gate. The Outcome below is intentionally unfilled (`_Pending reproduction — filled at flip._`) in this first commit; the digest, gate statistics, and verdict are PENDING until the reproduction is proven and independently audited. This born-red hold is the only legitimate red on this PR; any other gate failure is a real defect.

## Objective

Independently reproduce the PROPOSAL 169 verifier byte-for-byte in sim-lab under its pinned world (SEED pinned in-source), confirm its compact-canonical results-dict sha256 equals the disclosed digest, confirm determinism (in-process double-run assert + a separate cross-invocation byte-match), evaluate the ordered gates against the proposal's own pre-registered criteria (z_gate = 3.0), verify the √R-cushion QED convergence (delay probability approaches a non-degenerate constant α(β) ∈ (0,1) as R grows) against the two degenerate comparators (β = 0 drifts to 1, proportional over-staffing drifts to 0), and rule.

## GROUNDING (verified at HEAD)

- Reproduction verifier path (sim-lab): `sims/verdict-182-sqrt-safety-staffing/sqrt_safety_staffing.py` — to be a byte-identical copy (`diff` exit 0) of the idea-engine reference. _Reference identity (file sha256, git blob, HEAD sha) PENDING — recorded at the reproduction commit._
- Reference verifier: `ideas/fleet/sqrt_safety_staffing.py` at idea-engine HEAD `<pending>`, file sha256 `<pending>`, git blob `<pending>`.
- Offset authority: P169 → V182 is the constant +13 offset (confirmed P166 → V179, P167 → V180, P168 → V181 at the live cards), round-40 FLEET slot.
- Pinned world: SEED pinned in-source, z_gate = 3.0; β grid and R ladder pinned in-source (recorded verbatim at the reproduction commit).
- Domain reference: Halfin–Whitt heavy-traffic / QED staffing regime — https://en.wikipedia.org/wiki/Erlang_(unit) (Erlang-C / M/M/s) and the Halfin–Whitt (1981) square-root safety-staffing result. _Live-fetch anchor (URL@revision + fetch timestamp, HTTP status, quoted mechanism) PENDING — recorded at the reproduction commit._
- Disclosed digest: compact-canonical results-dict sha256 `<pending>`.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (posture confirmed against the reference at the reproduction commit) — the ordered results dict carries no `results_sha256` field; `main()` computes the compact-canonical serialization `json.dumps(results, sort_keys=True, separators=(",",":"))`, hashes it with sha256, asserts a second independent run's canonical form is byte-identical (in-process double-run), prints a pretty indent=2 dump plus the sha256, and writes no JSON to disk; every float rounded before serialization.

## Constraints honored

Byte-identical verifier copy (diff exit 0, copy sha256 == source, copy git blob == source blob); stdlib-only Python 3 (math, json, hashlib, random); deterministic SEED pinned in-source; no numpy/scipy; no on-disk JSON; no self-referential digest field; verdict ruled on reproduced evidence, not the proposer's assertion; forward-only git; zero agent merge calls. The delay-probability curve across the β grid, the two degenerate comparators, and the per-regime z-statistics are measured from the pinned M/M/s / Erlang-C computation (or its seeded simulation), not plugged from a closed form — so the QED convergence and the degeneracy of the linear/zero cushions are attributable to the reproduced computation, not a tautological substitution.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — QED-convergence-real (under s = ⌈R + β√R⌉ with β > 0 fixed, the delay probability converges to a non-degenerate constant α(β) ∈ (0,1) as R climbs the ladder — the spread across the top of the R ladder collapses toward α(β), rejecting any "delay probability must drift to a boundary" null): _statistic + z PENDING — reproduced at flip._
- G2 — degeneracy-of-the-comparators (the β = 0 exact-offered-load rule drives the delay probability toward 1, and a fixed proportional over-staffing s = ⌈(1+ε)R⌉ drives it toward 0 — both degenerate, straddling the QED constant and confirming √R is the unique non-degenerate cushion order): _statistic + z PENDING — reproduced at flip._
- G3 — robustness-second-β / shifted-world (at a second pinned β the QED convergence persists to a distinct constant α(β') ∈ (0,1) and orders monotonically in β, confirming the head is the √R-order cushion and not a single-β artifact): _statistic + z PENDING — reproduced at flip._
- all_pass = `<pending>`, first_failing_gate = `<pending>`.

## Probe questions (independent-audit checklist)

**1. Does the reproduced verifier match the reference byte-for-byte (diff exit 0, file sha256 and git blob matching the idea-engine identity at the pinned HEAD)?**

**2. Does the reproduced compact-canonical results-dict sha256 equal the disclosed digest exactly?**

**3. Is the run deterministic — does the in-process double-run assert not raise, and are two separate process invocations byte-identical (diff exit 0, exit code 0)?**

**4. Do all gates pass in the pre-registered order (G1 QED-convergence-real → G2 degeneracy-of-the-comparators → G3 robustness-second-β) with z_gate = 3.0, all_pass = true, first_failing_gate = null?**

**5. Does the delay probability under s = ⌈R + β√R⌉ converge to a non-degenerate constant α(β) ∈ (0,1) as R grows — bounded away from BOTH 0 and 1 — rather than drifting to a boundary?**

**6. Are the two comparators genuinely degenerate — β = 0 driving the delay probability toward 1 and fixed proportional over-staffing driving it toward 0 — so the √R cushion is the unique non-degenerate order and NOT the folk "safety must scale linearly with load" null?**

**7. Does the second-β / shifted world reproduce the QED convergence to a DISTINCT constant that orders monotonically in β, confirming the √R-order cushion drives the shape rather than a single tuned β?**

## Outcome

_Pending reproduction — filled at flip._

## ⟲ Previous-session review

VERDICT 181 (Condorcet's voting-cycle paradox, P168 → V181, +13, sim-lab #255) landed a CLEAN APPROVE and advanced the verdict high-water V180 → V181: the verifier reproduced byte-identically (file sha256 `259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def`, git blob `f349dfa78e4c6a1012858d4fc0aab95daa678578`, copied from idea-engine HEAD `11bb533`), deterministic in-process and across a separate invocation, printing the disclosed results-dict digest `70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe` (MATCH), with all four gates passing on the proposal's criteria (G1 cycles-exist z +61.46 · G2a documented-rate closeness anchor |z| 0.44 · G2b monotone-in-candidates step-z 19.39/11.95/18.63 · G3 robustness-under-tilt z +21.33). Contiguity holds: V182 follows V181, +13 offset intact (P169 → V182), round-40 FLEET slot. This V182 is BORN RED and NOT yet reproduced — the digest MATCH and gate results remain PENDING until the flip commit; the verdict high-water stays at V181 until this card flips to `complete`. No high-water regression. main was green at HEAD before this card's born-red hold.

## 💡 Session idea

_Pending — recorded at flip._

# VERDICT 227 — PROPOSAL 214 (symmetric Nash bargaining: the threat-point pass-through ∂x₁/∂d₁ = ½)

**Ruling: APPROVE**

Reproduced byte-exact; all four pre-registered gates independently confirmed each in its own direction; determinism holds in-process and cross-invocation.

Headline: raise your BATNA by a dollar and the symmetric Nash bargain hands you exactly fifty cents. Under the symmetric Nash bargaining solution with transferable utility, `x₁ = d₁ + ½·(S−d₁−d₂)`, so raising your own disagreement payoff d₁ by δ (total S held fixed) raises your negotiated share x₁ by exactly δ/2 — the pass-through ∂x₁/∂d₁ = ½. The folk "one-for-one" intuition (a better outside option is captured in full) is false: the other half dissolves into the shrinking surplus (S−d₁−d₂ drops by the same dollar). The closed form equals exhaustive Nash-product enumeration exactly, a Rubinstein alternating-offers negotiation gives β̂≈0.5 that rejects the folk β=1 by ~1917σ, the generalized α-solution passes through 1−α exactly, and surplus conservation falsifies the folk accounting.

Verified 2026-07-20T14:02Z (`date -u`).

## Reproduction
- Source verifier: idea-engine `ideas/venture-lab/batna-half-passthrough-nash-bargaining-2026-07-20.py`, copied **byte-identical** (`diff` source↔copy exit 0) to `sims/verdict-227-nash-bargaining/batna-half-passthrough-nash-bargaining-2026-07-20.py`.
- SEED=20260717, stdlib-only (`hashlib`, `json`, `random`, `fractions.Fraction`).
- `results_sha256 = 47e09254b86486e2cdff63e54ec8a276287f4f00806cf32e0fb52daa5cb4f434` — **FULL-64 EXACT** match to the disclosed PROPOSAL 214 digest (64 hex chars, exact string compare, no truncation; printed by the verifier AND independently `grep`-extracted identical, printed length confirmed = 64).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of itself. Human G2 detail is written to stderr and is NOT part of the digested stdout.

## Determinism
- In-process double-run guard: `main()` runs `battery()` twice and asserts `canonical(r1) == canonical(r2)` before hashing; the run exits 0, so the assert held. The stderr `G2-detail` line is emitted twice (once per battery call) and is byte-identical across the two, corroborating in-process stability of the stochastic gate.
- Cross-invocation: a second separate process run produced byte-identical stdout (`diff run-stdout.txt run2.txt`, exit 0) and the same full-64 digest.

## Gate evaluation (each read in ITS OWN direction, against the proposal's OWN criteria)

- **G1 — EXACT (closed-form Nash split == exhaustive Nash-product argmax) — PASS.** For all 200 randomized problems the symmetric closed-form split `x₁ = d₁ + ½·(S−d₁−d₂)` equals the exhaustive argmax of the Nash product `(x₁−d₁)(x₂−d₂)` over a Fraction-exact half-integer grid, and the maximizer is unique each time: `exact_argmax_matches_closed_form = 200/200`, `unique_maximizer = 200/200`, `problems = 200`. Direction: zero-tolerance Fraction equality AND unique maximizer — any mismatch or tie FAILS. The closed form is not an approximation of the argmax; it IS the argmax, certified to the bit.
- **G2 — SURPRISE (pass-through is ½ NOT the folk one-for-one) — PASS.** A simulated Rubinstein alternating-offers negotiation (N=100000 per batch) estimates the pass-through β̂ by bumping d₁ by δ=6 with total S held fixed: `beta_hat_round3 = 0.5` (raw β̂=0.500275). Against the folk full-pass-through null β=1: `z_folk = 1917.499` (≫3σ) → `rejects_folk_full_passthrough_at_3sigma = true`. Consistent with ½: |β̂−0.5|=0.000275 ≤ 0.02 → `consistent_with_half = true`, with `z_half = 1.054 < 3` (not distinguishable from ½). The two fire together: the estimator both certifies the ½ head AND separates from the folk one-for-one by a colossal margin — the whole surprise is that the intuitive accounting is wrong by a factor of two. Direction: reject folk β=1 at ≥3σ AND land consistent-with-½.
- **G3 — ROBUSTNESS (asymmetric α pass-through = 1−α exactly) — PASS.** Across the nine bargaining-power values α ∈ {1/10, 1/5, 3/10, 2/5, 1/2, 3/5, 7/10, 4/5, 9/10} the generalized Nash pass-through `∂x₁/∂d₁` equals `1−α` exactly (Fraction), row-by-row: (1/10→9/10), (1/5→4/5), (3/10→7/10), (2/5→3/5), (1/2→1/2), (3/5→2/5), (7/10→3/10), (4/5→1/5), (9/10→1/10) — `passthrough_equals_one_minus_alpha = true`. Every value lies strictly in (0,1) — fractional, never the folk 1.0 — `passthrough_strictly_between_0_and_1 = true`. And doubling the pie S leaves the pass-through unchanged (pie-size invariance is folded into the same exact check). Direction: exact `1−α` equality, strictly interior, pie-size invariant. The symmetric ½ is the α=1/2 special case of a general exact law.
- **G4 — EXACT + FALSIFIABILITY (conservation + IR AND folk falsified) — PASS.** For all 200 randomized problems surplus conservation `x₁+x₂ = S` holds (`surplus_conservation_holds = 200/200`) and individual rationality `x₁≥d₁, x₂≥d₂` holds (`individual_rationality_holds = 200/200`). And the deliberately-wrong folk accounting — capture the full δ into x₁ while holding the counterparty's x₂ fixed — is rejected in every problem because it sums to S+δ and violates conservation while the true bumped split still conserves: `folk_full_passthrough_falsified = 200/200`. The gate can fail (a folk split that conserved would not falsify), so passing 200/200 is informative. Direction: exact conservation + IR under the correct split AND strict conservation-violation of the folk accounting.

`all_pass = true`. The counterintuitive head — half of any threat-point gain reaches your share and half dissolves into the shrinking surplus — holds under zero-tolerance Fraction equality (G1/G3/G4, self-certifying) and is corroborated on a stochastic Rubinstein world where the folk one-for-one null is rejected by ~1917σ (G2).

### Observed vs disclosed (all match)
| Quantity | Disclosed / expected | Observed |
|---|---|---|
| results_sha256 | 47e09254…f434 | 47e09254…f434 (full-64) |
| G1 exact_argmax_matches_closed_form | 200 | 200 |
| G1 unique_maximizer | 200 | 200 |
| G2 beta_hat (round3) | ≈0.5 | 0.5 (raw 0.500275) |
| G2 z_folk (reject β=1, ≥3σ) | ≈1917.5 | 1917.499 |
| G2 z_half (consistent-with-½, <3) | ≈1.05 | 1.054 |
| G3 passthrough == 1−α (9 α's) | true | true (all 9 rows) |
| G3 strictly in (0,1) | true | true |
| G4 surplus_conservation_holds | 200 | 200 |
| G4 individual_rationality_holds | 200 | 200 |
| G4 folk_full_passthrough_falsified | 200 | 200 |

## Decision
All four gates pass in their stated directions; the full-64 digest matches the disclosed value exactly; determinism holds in-process (double-run assert) and cross-invocation (byte-identical stdout). **VERDICT 227 = APPROVE** (P214 → V227, +13 offset, lane VENTURE — the venture slice of the round-51 cycle).

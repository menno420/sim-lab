# VERDICT 267 reproduction mirror — monopoly optimal markup equals the reciprocal price-elasticity: exact Lerner-index identity on linear demand, iid Monte-Carlo agreement, currency-scale invariance, and the revenue-maximisation falsification, PROPOSAL 254

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 267 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block. `control/status.md` is untouched.

**Source proposal:** idea-engine PROPOSAL 254 (fleet · microeconomics / market power — a monopolist facing linear inverse demand `p(q) = a − b·q` with constant marginal cost `c` sets `q* = (a−c)/(2b)`, `p* = (a+c)/2`, `π* = (a−c)²/(4b)`, and the Lerner index of market power obeys the exact identity `L = (p*−c)/p* = (a−c)/(a+c) = 1/|ε*|` — the optimal markup equals the RECIPROCAL of the absolute price-elasticity of demand at the optimum)
**Lane:** P254 → V267 (+13 offset)
**Verifier:** `verify_254_monopoly_lerner_markup.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: argparse, hashlib, json, math, random, fractions, sys)
**SEED:** 20260717
**Command:** `python3 verify_254_monopoly_lerner_markup.py` (run from inside this directory; captured in `run-stdout.txt`)

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 025706848687e612a0f1b6d9e5c6bef64c9e0fc09748dd9cc93ee7626003f0c3` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · `--selfcheck`: byte-identical · separate re-invocation: byte-identical
- **G1 EXACT** (`fractions.Fraction`, no float in the identity) — the monopoly first-order condition and the Lerner / reciprocal-elasticity identity checked two independent ways and SWEPT over five rational triples `(1,1,1/4),(3,2,1),(5,7,2),(10,1,3),(2,3,1/2)`: (i) FOC cross-check `MR(q*) = a − 2b·q* == c` exactly (setting `MR = MC` recovers `q*`); (ii) reciprocal-elasticity cross-check `L(a,b,c) == 1/|ε*(a,b,c)| == (a−c)/(a+c)` exactly. `sweep_pass = [true, true, true, true, true]`, `all_exact_pass = true`. This gate is EXACT, so z is not applicable → reported `"exact — z=n/a"` → PASS
- **G2 Monte-Carlo agreement** (iid — NO thinning) — a unit mass of consumers with valuation `v ~ Uniform(0, a)` via `random.Random(SEED)`; buyer `i` purchases iff `v_i ≥ p*`, so the per-consumer profit at `p*` is `(p*−c)` if `v ≥ p*` else `0`, and the sample mean estimates `π*`. Over `N_MC = 2000000` iid draws, `n_buy = 749815`, `z = (mean − float(π*))/SE = −0.2702` with the honest plain-iid `SE = float(p*−c)·sqrt(q*(1−q*)/N)` (no batch means), `|z| = 0.2702 < 3` (Z_ACCEPT = 3.0) → PASS
- **G3 invariance** (currency-scale invariance, own direction) — the Lerner index is UNIT-FREE: rescaling the currency by `λ` (`a→λa, b→λb, c→λc`) leaves `q*` unchanged and `L` unchanged. For `λ ∈ {2, 3, 100, 1/7}` the verifier asserts `lerner(λa,λb,λc) == lerner(a,b,c)` exactly via `Fraction`; `lambda_pass = [true, true, true, true]`, `q_star_invariant = true`, `all_exact_pass = true`. Genuine economic content: market power is scale-free. This gate is EXACT → reported `"exact — z=n/a"` → PASS
- **G4 falsifiability** (reject at large |z|, own direction, SAME SEED stream as G2) — the pre-registered naive foil is "revenue maximisation equals profit maximisation" → price at `p_rev = a/2` (ignores cost). Exactly `π(p_rev) = 1/8`, strictly below `π* = 9/64` (`exact_gap = 1/64 > 0`, `exact_dominates = true`). On the SAME SEED-derived draws the per-consumer difference `(profit_at_p* − profit_at_p_rev)` estimates `π* − π(p_rev) = 1/64 > 0`; `z_foil = 189.8672 ≫ 3` → the "revenue-max is optimal" null is REJECTED while the same evidence accepts profit-max. The teeth: ignoring marginal cost overprices output and strictly forgoes profit; the same evidence discriminates the two rules → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

Monopoly optimal markup equals the reciprocal price-elasticity of demand. A monopolist facing LINEAR inverse demand `p(q) = a − b·q` (`0 ≤ c < a`, `b > 0`) with constant marginal cost `c` maximises profit at `q* = (a−c)/(2b)`, `p* = (a+c)/2`, `π* = (a−c)²/(4b)`, and the resulting Lerner index of market power satisfies the exact identity `L = (p*−c)/p* = (a−c)/(a+c) = 1/|ε*|`, where `|ε*| = (a+c)/(a−c)` is the absolute price-elasticity of demand evaluated at the optimum. This is the textbook monopoly markup rule specialised to the linear model: the fractional markup over marginal cost equals the RECIPROCAL of the elasticity the firm faces — more inelastic demand buys more market power. Headline instance `a = 1, b = 1, c = 1/4` gives `p* = 5/8`, `q* = 3/8`, `π* = 9/64`, `L = 3/5`, `1/|ε*| = 3/5`. The identity is verified in exact rational arithmetic two independent ways and swept over five triples (G1); a unit-mass consumer microfoundation (`v ~ Uniform[0, a]`, buy iff `v ≥ p`, demand fraction `(a−p)/a`) yields an iid Monte-Carlo estimator of `π*` agreeing with the closed form at `z = −0.27` over 2,000,000 draws (G2); the index is currency-scale invariant (`λ ∈ {2, 3, 100, 1/7}`, G3); and the single most plausible confusion — maximising revenue (price at `a/2`, ignoring cost) instead of profit — is shown strictly sub-optimal on the same evidence, rejected at `z_foil = 189.87` with exact profit gap `1/64` (G4).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_254_monopoly_lerner_markup.py` (verifier file sha256 `84530ee2ce5e1178a17dd8192861f012f99887a4729f747b48ced3eef208b11c`). The copy in this directory carries the same sha256 and `diff` against the source is empty (exit 0), confirming a byte-for-byte reproduction of the source verifier; stdlib-only (argparse, hashlib, json, math, random, fractions, sys), no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (`random.Random(SEED)` fixes the Monte-Carlo draws so gate order cannot perturb the payload; G2 and G4 share ONE SEED stream; every float enters the hashed payload via a fixed `f"{x:.4f}"` / string form, every exact quantity as a `str(Fraction)` `num/den`; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run, the `--selfcheck` path, and the separate subprocess re-invocation are byte-identical and the `results_sha256` reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned reference revisions and the quoted/derived split live with the source PROPOSAL 254, and the canonical grounding review belongs to the coordinator-driven VERDICT 267 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 267 slice, not here. No `## VERDICT` block, no verdict high-water advance, `control/status.md` untouched._

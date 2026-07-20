# VERDICT 213 — Banach's matchbox problem: the residual-count K when one pocket is first found empty has pmf P[K=k]=C(2N−k,N)·2^−(2N−k) and E[K] ~ 2√(N/π)−1 — reproduce PROPOSAL 200

> **Status:** in-progress

📊 Model: Claude Opus · effort high · task-class verdict-reproduction

started: 2026-07-20T06:28:12Z

Born-red HOLD (ACTIVE): this card ships `> **Status:** in-progress` on its FIRST
commit so the substrate born-red gate holds the PR red until the slice is genuinely
done; it will flip to `complete` as the deliberate LAST commit, only after the sim dir
(byte-identical verifier copy + reproduction stdout), the digest match (full-64
exact: `e162890…c576f56`), the in-order EXACT-PMF / SIGNAL-3σ / SIM-AGREEMENT /
ASYMPTOTIC-ROBUSTNESS gate evaluation (all PASS), the determinism check (in-process
double-run guarded), the grounding check (Wikipedia "Banach's matchbox problem"
oldid 1356179739, raw wikitext sha1 2a9bfea32a4ea817258b2a97ef8366cbaf7e6ec3
byte-exact), and the probe-report have ALL landed — that flip clears the HOLD and
releases merge-on-green.

## What this verdict does

Reproduces PROPOSAL 200 (P200 → V213, +13 offset): Banach's matchbox problem. A
mathematician keeps two matchboxes, one in each pocket, each initially holding `N`
matches. Each time a match is needed a pocket is chosen by a fair coin (prob 1/2
each) and one match is removed; eventually a pocket is chosen and found EMPTY. `K` is
the number of matches remaining in the OTHER box at that instant. The claim: `K` has
the exact probability mass function `P[K = k] = C(2N−k, N−k)·(1/2)^(2N−k)` (equal by
the C(a,b)=C(a,a−b) symmetry to `C(2N−k, N)·2^−(2N−k)`), and its mean grows like the
asymptotic `E[K] ~ 2√(N/π) − 1`. Copies the disclosed verifier
`ideas/fleet/banach_matchbox_residual.py` byte-identical into
`sims/verdict-213-banach-matchbox/`, reproduces the results-dict sha256, confirms
determinism, and evaluates the four gates in order against the proposal's OWN
criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0, git blob
  `f08cb3b3be6e11f11cd5c7f85523356462b9ed4a`), stdlib-only (`hashlib`, `json`,
  `math`, `random`, `fractions`), SEED=20260717, Z_GATE=3.0.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical
  results dict's own sha256 IS the digest (`json.dumps(d, sort_keys=True,
  separators=(",",":"))`); target
  `e162890959eba728cf83004508a213f3585009bcc8fbc6e8bebdab753c576f56` to be matched
  across all 64 hex (printed `results_sha256=…` AND independently recomputed), to be
  confirmed byte-identical across two fresh cross-invocation runs.
- Determinism: in-process double-run guard; the Monte-Carlo gate constructs a fresh
  `random.Random(SEED)` so the two builds draw the identical stream.
- Gates (in order, against the proposal's OWN criteria):
  - **G1 EXACT PMF / EXPECTATION** (Fraction-exact, wants closed form == DP): for
    `N ∈ {10, 50}` the exact `Fraction` pmf equals the dynamic-programming pmf term
    by term, each pmf sums to exactly 1, and `E[K]` from the closed form equals the
    DP `E[K]` exactly — `N=10` exact `707825/262144 ≈ 2.700138`, `N=50` exact
    `1115296899859219265664919877185/158456325028528675187087900672 ≈ 7.038513`.
  - **G2 SIGNAL 3σ** (wants a real, significant effect): `z2 = 1839.497873 ≥ 3`.
  - **G3 SIM AGREEMENT** (wants `|z| < 3`): the 2,000,000-trial Monte-Carlo mean
    `7.04112` agrees with the exact `E[K]≈7.038513`, `z3 = 0.681218`, `|z3| < 3`.
  - **G4 ASYMPTOTIC ROBUSTNESS** (wants monotone approach to the constant from
    above): the ratios `(E[K]+1)/√N = 1.170086 → 1.136817 → 1.130493` for
    `N ∈ {10, 50, 200}` decrease monotonically and every one exceeds
    `2/√π = 1.128379`, consistent with `E[K] ~ 2√(N/π) − 1`.
  - `all_pass = true`.
- Grounding: Wikipedia "Banach's matchbox problem" oldid 1356179739, raw wikitext
  (MediaWiki `action=raw`), 2819 bytes, sha1
  `2a9bfea32a4ea817258b2a97ef8366cbaf7e6ec3` byte-exact to the disclosed pin (matches
  local `sha1sum` AND the MediaWiki API `rvprop=sha1`); the article states the pmf
  `P[K=k]=C(2N−k,N−k)(1/2)^(2N−k)` and the asymptotic `2√(N/π)−1`. A disclosed
  stray-"r" typo is confined to the exact-expectation line, does not touch the pmf or
  the asymptotic, and is fairly disclosed / non-fatal.

## ⟲ Previous-session review

Previous-session review: VERDICT 212 (Vickrey second-price auction, truthful bidding
weakly dominant, PROPOSAL 199) landed complete with a full-64 digest MATCH
(`a96d59f…6527c`) and all four gates PASS via the born-red HOLD choreography —
`in-progress` first commit, deliberate `complete` flip last. Its carry-forward was
that the load-bearing evidence is the EXACT / EXHAUSTIVE gate (G1's zero strict
deviations, G2's exact `Fraction` expectation), with the eye-catching Monte-Carlo
z-scores merely corroborating, never primary. V213 inherits that discipline: here the
firsthand proof is again the exact gate — G1 checks the closed-form `Fraction` pmf
against an independent DP for `N ∈ {10, 50}` term-by-term with `E[K]` exact-equal —
and it adds a distinct z-score trap to keep straight: G2's huge `z2 = 1839.50` is a
SIGNAL test (the effect is real) while G3's small `z3 = 0.68` is an AGREEMENT test
(the sim matches the exact value, `|z| < 3`) — reading them by the same rule inverts
the meaning of a PASS. Standing non-contiguity persists: V137 (P124), V132 (P119),
and the round-26 FLEET-slot V126 (P113) remain open BELOW the high-water; landing
V213 does not imply every lower verdict is closed.

## 💡 Session idea

G4 certifies the approach to the asymptotic constant only through the ratio
`(E[K]+1)/√N` at the coarse grid `N ∈ {10, 50, 200}`, showing it decreases toward
`2/√π = 1.128379` from above. That establishes monotone-from-above on three points but
never quantifies the RATE. The asymptotic `E[K] = 2√(N/π) − 1 + o(1)` predicts a
specific next-order correction; a cheap orthogonal extension reusing the exact
`E[K]` closed form verbatim would compute the residual
`r(N) = E[K] − (2√(N/π) − 1)` across a denser `N` grid and check that `r(N) → 0` and,
sharper, that `r(N)·√N` settles toward the theory's `−1/(4)·√(1/π)`-scale next term —
turning "monotone from above on three points" into a measured convergence-rate
witness. Only a sibling diagnostic changes; the exact closed form and the
digest-bearing results dict stay untouched.

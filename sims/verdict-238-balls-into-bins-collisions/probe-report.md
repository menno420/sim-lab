# PROPOSAL 225 → VERDICT 238 — Probe report (balls into bins, expected collision count)

> Throw m balls independently and uniformly into n bins (equivalently, hash m
> keys into n buckets). Count one COLLISION for every unordered PAIR of balls
> that share a bin: X = Σ over bins of C(load, 2). The expected number of
> colliding pairs is EXACTLY E[X] = C(m,2)/n = m(m−1)/(2n) — a closed-form
> rational, for every (m, n) — by linearity of expectation over the C(m,2)
> pairs, each colliding with probability exactly 1/n. It is quadratic in m
> (pairs, not balls), and the naive m²/(2n) shortcut overstates it by exactly
> m/(2n).

- **Slice:** round-54, P225 → V238 (+13 offset), FLEET lane
- **Branch:** `claude/p225-balls-in-bins`
- **Sim dir:** `sims/verdict-238-balls-into-bins-collisions/`
- **Verifier:** `balls-into-bins-collision-count.py` (stdlib-only, SEED = 20260717)
- **Recommendation: sim-ready**

## Q1 — Is the verifier stdlib-only and single-seeded?

Yes. Imports are `hashlib`, `json`, `math`, `random`, `fractions.Fraction` —
all Python-3 stdlib, no third-party. `SEED = 20260717`; ALL randomness comes
from one `random.Random(SEED)` created in `run_battery()` and consumed in a
fixed, documented order: G2 draws `MC_TRIALS = 200000` balls-into-bins trials
per config (in `CONFIGS` order), then G3 draws the robustness sweep
(`SWEEP_TRIALS = 120000` each, in `SWEEP` order), then G4 draws the
falsifiability sample on `FALSIFY_CFG` — back-to-back, no interleaving. No
wall-clock, no OS entropy, no `os.urandom`.

## Q2 — Is the exact core computed as a LITERAL Fraction identity (not hardcoded)?

Yes — and via THREE independent routes asserted equal. `exact_pairsum(n,m)`
adds `Fraction(1, n)` out in a double loop over all C(m,2) unordered pairs (it
never substitutes the closed form). `exact_perbin(n,m)` sums the per-bin
contribution `n * (Fraction(C(m,2)) / Fraction(n*n))`. `exact_closed(n,m)` is
`Fraction(m*(m-1), 2*n)`. G1 asserts `route_a == route_b == route_c` exactly.
No float appears in the exact gate; floats occur only in the Monte-Carlo
z-scores (G2/G3/G4), which are agreement/rejection gates.

## Q3 — G1 (EXACT identity): does it PASS in its own direction?

PASS — direction is "any of the three routes ≠ the others ⇒ FAIL." For every
config all three exact routes coincide:

| config (n,m) | C(m,2) pairs | pair-sum (a) | per-bin (b) | closed (c) | equal |
|--------------|--------------|--------------|-------------|------------|-------|
| (365, 23) | 253 | 253/365 | 253/365 | 253/365 | ✅ |
| (256, 64) | 2016 | 63/8 | 63/8 | 63/8 | ✅ |
| (1000, 100) | 4950 | 99/20 | 99/20 | 99/20 | ✅ |

A self-certifying identity — exact Fraction equality across a literal
pair-by-pair sum, a per-bin linearity route, and the closed form. Three
independent algebraic paths must all reduce to the same rational.

## Q4 — G2 (Monte-Carlo agreement): does it PASS in its own direction?

PASS — direction is |z| < 3 (agreement; small z is the pass). For each config
the sample mean of X over 200000 trials is compared to the exact E with
z = (mean − E)/(sample_sd/√T):

| config | E_exact | sample_mean | z | \|z\| < 3 |
|--------|---------|-------------|---|-----------|
| (365, 23) | 0.693150685 | 0.691765 | −0.745423 | ✅ |
| (256, 64) | 7.875 | 7.868810 | −0.988399 | ✅ |
| (1000, 100) | 4.95 | 4.942470 | −1.509722 | ✅ |

Every config's empirical collision-pair mean tracks m(m−1)/(2n) within 3σ on
the fixed seed.

## Q5 — G3 (Robustness): sweep AND exact scaling?

PASS — direction: any swept config disagrees (|z| ≥ 3) OR the scaling identity
fails ⇒ FAIL.

**(a) Sweep.** Four further configs, 120000 trials each, all agree:

| config | E_exact | sample_mean | z | within 3σ |
|--------|---------|-------------|---|-----------|
| (365, 30) | 1.191780822 | 1.192666667 | 0.281804 | ✅ |
| (128, 40) | 6.09375 | 6.088858333 | −0.687537 | ✅ |
| (500, 50) | 2.45 | 2.446266667 | −0.830305 | ✅ |
| (64, 16) | 1.875 | 1.879950000 | 1.261990 | ✅ |

max |z| = **1.261990** < 3.

**(b) Exact scaling.** The ratio E(n, 2m)/E(n, m) equals (2m)(2m−1)/(m(m−1))
as identical `Fraction`s, independent of n:

| base (n,m) | E(2m)/E(m) | predicted | equal |
|------------|-----------|-----------|-------|
| (365, 23) | 45/11 | 45/11 | ✅ |
| (256, 64) | 254/63 | 254/63 | ✅ |

Doubling the balls multiplies the expected collisions by (2m)(2m−1)/(m(m−1)) →
4 — the quadratic-in-m signature, exact. Both legs hold ⇒ G3 PASS.

## Q6 — G4 (FALSIFIABILITY): is the wrong model rejected in its own direction?

PASS — direction: PASS iff each wrong model is REJECTED at |z| ≥ 6. On the
(256,64) sample whose mean AGREES with the exact 63/8 at z = −0.576503:

| model | value | z vs sample | rejected (\|z\|≥6) |
|-------|-------|-------------|--------------------|
| exact m(m−1)/(2n) | 7.875 | −0.576503 | — (agrees, <3σ) |
| naive m²/(2n) | 8.0 | **−20.566187** | ✅ |
| ordered m(m−1)/n | 15.75 | **−1259.926656** | ✅ |

The naive shortcut m²/(2n) drops the self-pair −1 and overstates the exact
answer by exactly m/(2n) = 64/512 = **1/8** (`naive_overstatement_exact`);
it is rejected at z = −20.57. The ordered-pair count double-counts every pair
and is rejected at z = −1259.93. Both wrong models rejected at |z| ≥ 6,
opposite polarity to the G2/G3 agreement ⇒ G4 PASS.

## Q7 — Determinism: do both legs hold?

Yes. **In-process double-run:** `__main__` builds the results dict twice and
prints `determinism_double_run=True` (compact-canonical JSON byte-identical
before exit 0). **Cross-invocation:** separate `python3` processes produced
byte-identical stdout (sha256 of each captured stdout =
`df886c2d1102774119b971fe56c55edc62c282f6c1dba7ebf512ad95d9e48279`, identical).
The results-dict full-64 digest is
`874a5b611f327149714d07b841bb4285481bbb223086823a5980b5ae6a31a57a` — printed on
the `results_sha256=` line, exact 64-char compare, no truncation. Digest
posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical
results dict's own sha256 IS the digest (`json.dumps(r, sort_keys=True,
separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of itself
and no time/random-address content (seed is fixed). Exit code 0,
`sim_ready=True`. Captured stdout is in `run-stdout.txt`.

## Q8 — Grounding: is the result byte-pinned to a source, caveat honest?

Yes. Source: Wikipedia **"Birthday problem"**, oldid **1357361405**, `action=raw`
wikitext. Raw-wikitext sha1 = `d876b4f46b64278277ad0cf4b4bdf2ea0f271be1`
(52676 bytes), matching the MediaWiki API-reported revision sha1 (independent
3-way match: API `rvprop=sha1` = locally-computed `sha1(raw bytes)`). URL@sha1:
`https://en.wikipedia.org/w/index.php?title=Birthday_problem&action=raw&oldid=1357361405@d876b4f46b64278277ad0cf4b4bdf2ea0f271be1`

- **On-page (confirmed present, QUOTED):** the C(m,2) = m(m−1)/2 pair count,
  literally *"the birthday comparisons will be made between every possible pair
  of individuals. With 23 individuals, there are 23×22/2 = 253 pairs"*; the
  Poisson mean *"Poi(C(23,2)/365) = Poi(253/365) ≈ Poi(0.6932)"* used to
  approximate the collision distribution — 253/365 being exactly this sim's E
  at (m=23, n=365); the linearity-of-indicator-variables method (used on-page
  for the expected number of people with a shared birthday); and the
  hash-table / hash-collision framing.
- **Off-page (correctly absent, DERIVED):** the general exact closed form
  E = m(m−1)/(2n) as a labeled expected-collision-count formula. The page
  supplies the pair count, the per-pair probability 1/d, the linearity method,
  and the single numeric rate 253/365 — but presents 253/365 as the mean of an
  APPROXIMATING Poisson, never the general exact formula. (A separate on-page
  quantity — the "number of people who repeat a birthday",
  Σ q(k−1;d) = n − d + d((d−1)/d)ⁿ — is the expected count of balls in an
  OCCUPIED bin, a DIFFERENT object, kin to this sim's rejected ordered/impostor
  legs.) The SEED, the (n,m) configs, the three-route Fraction identity, the
  Monte-Carlo z-scores, the exact-scaling ratio, and the m²/(2n)
  falsifiability rejection are the verifier's OWN firsthand computations.

Caveat is honest — it attributes the pair count and the 253/365 rate as QUOTED
and the general exact m(m−1)/(2n) as DERIVED from those on-page ingredients; it
neither oversells (does not claim Wikipedia states the general closed form or
the Monte-Carlo/falsifiability verification) nor undersells (the pair count and
the Poisson rate are literally on the pinned revision).

## Recommendation

**Recommendation: sim-ready.** Stdlib-only single-seeded verifier; the exact
core is computed THREE independent ways (a literal Σ `Fraction(1,n)` over all
C(m,2) pairs, the per-bin linearity route, and the closed form) all confirmed
equal — 253/365, 63/8, 99/20 across the three configs; all four pre-registered
gates PASS in their own directions — G1 EXACT three-route identity, G2
Monte-Carlo agreement (z = −0.745423 / −0.988399 / −1.509722, all < 3), G3
robustness (four-config sweep all |z| < 3 max 1.261990 AND exact-scaling
Fraction identity n-independent), G4 falsifiability (the naive m²/(2n) shortcut
rejected at z = −20.566187 with overstatement exactly m/(2n) = 1/8, plus the
ordered-pair impostor rejected at z = −1259.926656); determinism holds on both
the in-process double-run and the separate cross-invocation (byte-identical
stdout); and the result is byte-pinned to Wikipedia oldid 1357361405 (sha1
3-way match) with an honest QUOTED-vs-DERIVED caveat.

# VERDICT 217 — hat-check invariance: for a uniform random permutation of n items the number of fixed points (patrons handed back their own coat) has mean EXACTLY 1 for every n≥1 and variance EXACTLY 1 for every n≥2; the chance of a full derangement (nobody's own coat) is D_n/n! → 1/e ≈ 0.3679; and the whole fixed-point count converges to Poisson(1) — reproduce PROPOSAL 204

> **Status:** complete

📊 Model: Claude Opus · effort high · verdict-reproduction

started: 2026-07-20T09:06:45Z

💓 Heartbeat: round-slot FLEET P204 → V217 (+13) reproduction on branch
`claude/verdict-217-hat-check`; sim dir `sims/verdict-217-hat-check-invariance/`
(byte-identical verifier copy + reproduction stdout + grounding wikitext + probe-report),
digest full-64 EXACT (`7b99e650…46dfb0`), all four gates PASS in order (G1 EXACT Fraction
enumeration n=1..8: E==1 all n≥1, Var==1 all n≥2, D_n brute==inclusion-exclusion==recurrence
[0,1,2,9,44,265,1854,14833]; G2 derangement floor n=200,M=80000 p_derange 0.369875,
z_floor +40.937939 ≥3σ above the 0.30 folk floor, z_inv_e 1.169146 within 3σ of 1/e; G3
n-invariance range 0.021875 < 0.05 across n∈{10,100,1000,2000}; G4 Poisson(1) Pearson χ²
1.36372 < 18.467 df=4 α=0.001), determinism in-process double-run identical (assert, no
divergence) + two cross-invocation processes byte-identical, grounding byte-pinned
(Wikipedia "Rencontres numbers" oldid 1340506236, raw-wikitext sha1
`256b0417a6785bd9d1e50a6aa9766175ee329dc5`, API-reported sha1 matches). Born-red HOLD armed
on the first card commit; released on the deliberate `complete` flip. PR #292.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so
the substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It
flips to `complete` as the deliberate LAST commit — only after the sim dir (byte-identical
verifier copy + reproduction stdout + grounding wikitext + probe-report), the digest match
(full-64 exact `7b99e650…46dfb0`), the in-order G1/G2/G3/G4 gate evaluation (all PASS), the
determinism check (in-process double-run identical AND two cross-invocation processes
byte-identical), and the grounding check have ALL landed — that flip clears the HOLD and
releases merge-on-green. NO merge API calls are made from this session; CI + the landing
automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 204 (P204 → V217, +13 offset, lane superbot fleet): **hat-check
invariance.** A coat-check clerk loses the ticket stubs and returns n coats uniformly at
random — a random permutation π of the patrons. A patron is a *fixed point* iff π returns
their own coat. The head is a triple invariance: (1) the EXPECTED number of matches is
EXACTLY 1 for every crowd size n≥1 (linearity of expectation: each patron matches with
probability 1/n, summed over n patrons) and the VARIANCE is EXACTLY 1 for every n≥2; (2)
the probability that NOBODY gets their own coat (a full derangement) is
`D_n/n! = Σ_{k=0}^n (-1)^k/k!` which converges to `1/e ≈ 0.3679` — not "essentially never";
(3) the whole fixed-point count converges in distribution to Poisson(1). Copies the
disclosed verifier `ideas/fleet/hat-check-fixed-points-invariance.py` byte-identical into
`sims/verdict-217-hat-check-invariance/`, reproduces the results-dict sha256, confirms
determinism, and evaluates the four gates in order against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0), stdlib-only (`json`, `hashlib`,
  `math`, `random`, `fractions`, `itertools`), SEED = 20260717. One seeded RNG is consumed
  in gate order G2 → G3 → G4.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results
  dict's own sha256 IS the digest (`json.dumps(d, sort_keys=True, separators=(",",":"))`);
  target `7b99e6504b7cfa776ce871b7756b2ff71ed5bcd025e9dd6134d0f8d8e246dfb0` matched across
  all 64 hex chars, identical across two fresh cross-invocation runs.
- Gates (in order, against the proposal's OWN criteria — read each in ITS direction):
  - **G1 EXACT (Fraction, exhaustive enumeration n=1..8; direction: every identity exact)**
    — E==1 for all n≥1, Var==1 for all n≥2 (Var==0 at n=1); the derangement count D_n
    computed three ways (brute enumeration == inclusion-exclusion `n!·Σ(-1)^k/k!` ==
    recurrence `D_n=(n-1)(D_{n-1}+D_{n-2})`) agrees with zero tolerance: D_0..8 =
    [1,0,1,2,9,44,265,1854,14833]. **PASS.**
  - **G2 ≥3σ derangement floor (n=200, M=80000; direction: one-sided up past the 0.30 folk
    floor AND within 3σ of 1/e)** — p_derange 0.369875, z_floor +40.937939 (clears the
    "essentially never" 0.30 floor by >40σ), z_inv_e 1.169146 (within 3σ of 1/e =
    0.3678794). **PASS.**
  - **G3 n-invariance (n∈{10,100,1000,2000}; direction: mean does NOT move with crowd
    size)** — cross-scale mean range 0.021875 < 0.05, every mean within 0.05 of 1. **PASS.**
  - **G4 Poisson(1) shape (n=100, M=80000; direction: χ² < crit ⇒ fit not rejected)** —
    Pearson χ² 1.36372 < 18.467 (df=4, buckets k=0,1,2,3,≥4, α=0.001). **PASS.**
- Grounding: Wikipedia "Rencontres numbers" oldid 1340506236, raw-wikitext sha1
  `256b0417a6785bd9d1e50a6aa9766175ee329dc5` (byte-pinned; MediaWiki API-reported sha1
  matches). Caveat: the page STATES the facts (E=1 by linearity of expectation, Poisson(1)
  moments, `D_{n,k}/n! → e^{-1}/k!`), the verifier PROVES them (exact `Fraction`
  enumeration).

## ⟲ Previous-session review

Previous-session review: VERDICT 216 (voting power is not voting weight — under a weighted
voting game `[q; w_1..w_n]` a voter's Banzhaf / Shapley–Shubik power is NOT proportional to
its weight; the `[51; 50,49,1]` witness has the 49-bloc power == the 1-bloc power, PROPOSAL
203 → V216) landed complete with a full-64 digest MATCH (`660bb1e5…ece254`) and all four
gates PASS via the born-red HOLD choreography — `in-progress` first commit, deliberate
`complete` flip last. Its carry-forward was GATE-POLARITY discipline: read each gate in ITS
OWN direction — V216's G1/G2/G3 were EXACT `Fraction`/exhaustive-enumeration gates (any
mismatch FAILS) while ONLY G4 was a ≥3σ SIGNAL gate (a LARGE z is the PASS). V217 re-tunes
that mix AGAIN: G1 is an EXACT gate (exact `Fraction` E/Var identities + three-way D_n
agreement, self-certifying, no sampling); G2 is a ≥3σ FLOOR gate with a TWO-SIDED leg (a
LARGE z_floor is the PASS — the derangement rate must clear the folk 0.30 floor — but the
consistency leg needs a SMALL |z_inv_e| < 3, so reading G2 as a single-polarity gate would
misjudge it); G3 is an AGREEMENT gate (a SMALL cross-scale range < 0.05 is the PASS — a
large range would FAIL, the opposite of a signal gate); G4 is a GOODNESS-OF-FIT gate (a
SMALL χ² is the PASS — χ² below the critical value means the Poisson(1) fit is not
rejected). The load-bearing evidence is the EXACT G1 block (E==1/Var==1 and
brute==incexc==recurrence D_n), with G2/G3/G4 corroborating at scale. Standing
non-contiguity persists: V137 (P124), V132 (P119), and the round-26 FLEET-slot V126 (P113)
remain open BELOW the high-water; landing V217 does not imply every lower verdict is closed.

## 💡 Session idea

The three invariances (E==1, Var==1, D_n/n!→1/e) are all corollaries of the SAME exact
fact: the number of fixed points has FACTORIAL MOMENTS all equal to 1 up to order n — i.e.
`E[X·(X-1)···(X-j+1)] = 1` for every j ≤ n, because the number of ordered j-tuples of
patrons who ALL match is exactly `(n-j)!` and there are `n!/(n-j)!` such tuples in
expectation-weighted count, giving `E[falling-factorial_j(X)] = 1`. A cheap orthogonal
extension that reuses `enumerate_exact` verbatim would ADD a deterministic "factorial-moment
gate": for n=1..8 confirm the j-th factorial moment is EXACTLY 1 (as a `Fraction`) for all
j ≤ n and STRICTLY LESS THAN 1 for j > n — this is the single exact identity from which
E=1 (j=1), Var=1 (j=2 gives E[X(X-1)]=1 ⇒ E[X²]=2 ⇒ Var=1), and the Poisson(1) limit
(Poisson(1) has ALL factorial moments 1) simultaneously fall out. It turns three separately
stated gate facts into ONE self-certifying combinatorial witness — the falling-factorial
enumeration — that is the real engine behind "hat-check invariance," while the
digest-bearing results dict and the four shipped gates stay byte-identical; only a sibling
exact factorial-moment gate is added.

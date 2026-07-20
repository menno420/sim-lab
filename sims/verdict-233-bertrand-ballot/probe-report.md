# PROPOSAL 220 → VERDICT 233 — Probe report (Bertrand's ballot theorem)

> In a count where candidate A finishes with a votes and candidate B with
> b < a votes, and the ballots are opened in uniformly random order, the
> probability that A is STRICTLY ahead of B at EVERY prefix of the count
> (A leads wire-to-wire, never tied, never behind) is EXACTLY (a−b)/(a+b).
> Equivalently the number of favourable countings is (a−b)/(a+b)·C(a+b, a).
> The probability rides ONLY on the winning-margin ratio — NOT on A's overall
> vote share a/(a+b).

- **Slice:** round-52, P220 → V233 (+13 offset), UNRELATED lane
- **Branch:** `claude/proposal-220-bertrand-ballot`
- **Sim dir:** `sims/verdict-233-bertrand-ballot/`
- **Verifier:** `bertrand-ballot-lead-throughout.py` (stdlib-only, SEED = 20260717)
- **Recommendation: sim-ready**

## Q1 — Is the verifier stdlib-only and single-seeded?

Yes. Imports are `hashlib`, `itertools`, `json`, `math`, `random`,
`fractions.Fraction` — all Python-3 stdlib, no third-party. `SEED = 20260717`;
ALL randomness comes from one `random.Random(SEED)` created in `run_battery()`
and consumed in a fixed, documented order: for each (a,b) in `MC_PAIRS`
(in listed order) `MC_T = 200000` ballot shuffles are drawn back-to-back via
`rng.shuffle` before the next pair. No wall-clock, no OS entropy, no `os.urandom`.

## Q2 — Is the exact core encoded with Fraction (no floats in exact gates)?

Yes. The brute favourable count is a full enumeration over the `C(a+b,a)`
placements of the A-ballots (`itertools.combinations`), and every exact
comparison uses `fractions.Fraction`: G1 tests `Fraction(brute, C(a+b,a)) ==
Fraction(a−b, a+b)`, G2 tests `Fraction(a−b,a+b) == Fraction(ka−kb, ka+kb)` and
`Fraction(fav, total) == base`. No float appears in any exact gate; floats occur
only in the Monte-Carlo z-scores (G3/G4), which are agreement/rejection gates.

## Q3 — G1 (EXACT identity): does it PASS in its own direction?

PASS — direction is exact Fraction equality. For all six pairs
{(3,1),(4,2),(5,2),(5,3),(6,3),(7,2)} the brute favourable count over ALL
distinct arrangements divides C(a+b,a) to exactly (a−b)/(a+b):

| (a,b) | favourable | C(a+b,a) | brute prob | closed form | equal |
|-------|-----------|----------|-----------|-------------|-------|
| (3,1) | 2  | 4  | 1/2 | 1/2 | ✅ |
| (4,2) | 5  | 15 | 1/3 | 1/3 | ✅ |
| (5,2) | 9  | 21 | 3/7 | 3/7 | ✅ |
| (5,3) | 14 | 56 | 1/4 | 1/4 | ✅ |
| (6,3) | 28 | 84 | 1/3 | 1/3 | ✅ |
| (7,2) | 20 | 36 | 5/9 | 5/9 | ✅ |

A self-certifying combinatorial theorem — exact equality, no slack.

## Q4 — G2 (EXACT scale-invariance): does it PASS in its own direction?

PASS — direction is exact Fraction equality. On base (2,1) with ratio 1/3, for
k ∈ {1,2,3,5} the scaled ratio `Fraction(ka−kb, ka+kb)` equals the base 1/3
exactly, AND the brute count identity still holds on each enumerable scaled
case: (2,1)→1/3, (4,2)→5/15=1/3, (6,3)→28/84=1/3, (10,5)→1001/3003=1/3. This
pins that the probability depends only on the margin ratio, not on scale.

## Q5 — G3 (Monte-Carlo agreement): does it PASS in its own direction?

PASS — direction is |z| ≤ 3 (agreement, small z is the pass). For each MC pair
the empirical lead-throughout rate over 200000 shuffles agrees with (a−b)/(a+b):

| (a,b) | target | empirical mean | z | within 3σ |
|-------|--------|----------------|---|-----------|
| (3,1) | 1/2 = 0.5 | 0.50114 | 1.01965 | ✅ |
| (5,2) | 3/7 ≈ 0.428571 | 0.42719 | −1.2489 | ✅ |
| (7,3) | 2/5 = 0.4 | 0.39957 | −0.392605 | ✅ |

`mc_stats` returns (mean, se) with se = sqrt(p(1−p)/T) (binomial SE).

## Q6 — G4 (FALSIFIABILITY): is the naive model rejected in its own direction?

PASS — direction is naive REJECTED at |z| > 5, on the SAME sample that agrees
with the true law (G3). The plausible-but-wrong model "prob = a/(a+b)" (A's vote
share = P(first vote is A)) is rejected at huge |z|:

| (a,b) | naive a/(a+b) | empirical mean | z_naive | rejected |
|-------|---------------|----------------|---------|----------|
| (3,1) | 3/4 = 0.75 | 0.50114 | −222.587729 | ✅ |
| (5,2) | 5/7 ≈ 0.714286 | 0.42719 | −259.552892 | ✅ |
| (7,3) | 7/10 = 0.7 | 0.39957 | −274.303069 | ✅ |

The identical Monte-Carlo sample simultaneously CONFIRMS (a−b)/(a+b) (|z|≤3, G3)
and REFUTES a/(a+b) (|z|≫5) — the sharpest falsifiability posture. An EXACT leg
also confirms the corrupt count formula a/(a+b)·C(a+b,a) ≠ the brute favourable
count on all six G1 pairs.

## Q7 — Determinism: do both legs hold?

Yes. **In-process double-run:** `__main__` builds the results dict twice and
prints `determinism_double_run=True` (compact-canonical JSON byte-identical
before exit 0). **Cross-invocation:** two separate `python3` processes print the
identical `results_sha256` line. Full-64 digest:
`d52f08b930d92b01ee8d0f81089974843262710f301dd738594602bf3d4378aa` — printed on
the `results_sha256=` line, exact 64-char compare, no truncation. Exit code 0,
`sim_ready=True`. Captured stdout is in `run-stdout.txt`.

## Q8 — Grounding: is the theorem byte-pinned to a source, caveat honest?

Yes. Source: Wikipedia **"Bertrand's ballot theorem"** (the title "Bertrand's
ballot problem" is a redirect to it), oldid **1361316938**, `action=raw`
wikitext. Raw-wikitext sha1 = `45e367783ba2926b9ff7c826b97dba3206c45219`,
matching the MediaWiki API-reported revision sha1 (independent 3-way match).
URL@sha1:
`https://en.wikipedia.org/w/index.php?title=Bertrand%27s_ballot_theorem&action=raw&oldid=1361316938@sha1:45e367783ba2926b9ff7c826b97dba3206c45219`

- **On-page (confirmed present):** the theorem and its answer, in the page's
  own variables p (= a), q (= b). Line 2: *"In an election where candidate A
  receives p votes and candidate B receives q votes with p > q, what is the
  probability that A will be strictly ahead of B throughout the count … The
  answer is"* → line 4: `\frac{p-q}{p+q}`. The favourable-count form
  `\binom{p+q}{q}\frac{p-q}{p+q}` is on line 125, and the reflection/cycle-lemma
  proofs are on-page (lines 90, 108).
- **Off-page (correctly absent):** the page proves the theorem analytically
  (reflection, cycle lemma, induction, martingale); it does NOT contain this
  sim's firsthand computational verification — the SEED = 20260717, the specific
  (a,b) grids, the Monte-Carlo procedure, or the results_sha256. The a/(a+b)
  term does appear on-page (line 101) but only as P(last vote is A) inside the
  inductive step — NOT as the answer, so the G4 naive model is a genuine
  impostor the page distinguishes.

Caveat is honest — it neither oversells (does not claim Wikipedia contains the
Monte-Carlo verification) nor undersells (the analytic theorem and its
(p−q)/(p+q) answer are literally on the pinned revision); the firsthand
enumeration + Monte-Carlo proof is disclosed as reproduction, not citation.

## Recommendation

**Recommendation: sim-ready.** Stdlib-only single-seeded verifier; the exact
core encoded with `Fraction` over full enumeration; all four pre-registered
gates PASS in their own directions (G1/G2 exact Fraction identities, G3 two-sided
Monte-Carlo agreement |z|≤3, G4 falsifiability with the naive vote-share model
rejected at |z|≫5 on the same sample plus an exact corrupt-count leg);
determinism holds on both the in-process double-run and the separate
cross-invocation; and the theorem is byte-pinned to Wikipedia oldid 1361316938
(sha1 3-way match) with an honest firsthand-vs-cited caveat.

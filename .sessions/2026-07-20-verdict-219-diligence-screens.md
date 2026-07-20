# VERDICT 219 — Independent positives MULTIPLY the odds: k conditionally-independent symmetric screens (AND rule) compose by likelihood-ratio product, so the k-th screen need only clear (odds-against)^(1/k) — the k-th-root diligence ladder. At a 1% base rate TWO independent 95% screens (AND) flag a ~78%-good shortlist that one 99% screen cannot (a single test sits at the PPV knife-edge ≈0.5), while the gain VANISHES exactly when the screens are redundant (ρ=1 collapses PPV to the single-screen 0.161) — reproduce PROPOSAL 206

> **Status:** in-progress

📊 Model: Claude · high effort · verdict-reproduction

started: 2026-07-20T10:14:29Z

💓 Heartbeat: round-slot VENTURE P206 → V219 (+13) reproduction on branch
`claude/verdict-219-diligence-screens`; sim dir `sims/verdict-219-diligence-screens/`
(byte-identical verifier copy + reproduction stdout + cross-invocation stdout + probe-report),
digest target full-64 `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6`, four gates
evaluated each in its own direction (G1 EXACT three-way identity direct==odds-form==exhaustive-
enumeration 27 cells 0 mismatches; G2 k-th-root ladder exact boolean [p·a^k>(1−p)(1−a)^k]==[PPV_k>½]
36 cells 0 violations + strictly-decreasing clearing ladder 100/91/83 for k=1,2,3 at p=1/100; G3 ≥3σ
M=400000 two-screen empirical PPV 0.789277 z_majority=47.85 vs single-screen PPV_1=0.161; G4
correlation-nullification PPV(ρ=1)==PPV_1 exactly + strictly decreasing over ρ∈{0,¼,½,¾,1} + odds-
multiplication identity 12 cells 0 mismatches), determinism in-process double-run IDENTICAL + two
cross-invocation processes byte-identical, grounding byte-pinned (Wikipedia "Likelihood ratios in
diagnostic testing" revid 1363827685, raw-wikitext sha1 `bd86f75187e89db916dbd57fcbdcca2e9fd95d1a`).
Born-red HOLD armed on this first card commit; released later by a deliberate `complete` flip. PR
born-red until then.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the
substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to
`complete` as the deliberate LAST commit — only after the sim dir (byte-identical verifier copy +
reproduction stdout + cross-invocation stdout + probe-report), the digest match (full-64 exact
`b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6`), the four-gate evaluation each in
its own direction (all PASS), the determinism check (in-process double-run identical AND two cross-
invocation processes byte-identical), and the grounding check have ALL landed — that flip clears the
HOLD and releases merge-on-green. NO merge API calls are made from this session; CI + the landing
automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 206 (P206 → V219, +13 offset, lane venture): **independent positives multiply the
odds.** For k conditionally-independent symmetric screens combined under the AND rule, the posterior
odds are the prior odds times the product of per-screen likelihood ratios —
`posterior_odds = prior_odds·(a/(1−a))^k` — so the k-th screen need only be about
`(odds-against)^(1/k)` accurate (the **k-th-root ladder**). At a 1% base rate, TWO independent 95%
screens (AND rule) flag a ~78%-good shortlist that a single 99% screen cannot (one test sits at the
base-rate PPV knife-edge, ≈0.5), and the advantage **vanishes exactly** when the screens are redundant:
at correlation ρ=1 the two-screen PPV collapses to the single-screen value 0.161. Copies the disclosed
verifier `ideas/venture-lab/independent_screens_odds_ladder.py` byte-identical into
`sims/verdict-219-diligence-screens/`, reproduces the results-dict sha256, confirms determinism, and
evaluates the four gates each in its own direction against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0), stdlib-only (`json`, `hashlib`, `math`,
  `random`, `fractions`), SEED = 20260717 (one `random.Random(SEED)` consumed only by G3 in fixed order).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own
  sha256 IS the digest (`json.dumps(d, sort_keys=True, separators=(",",":"))`); target
  `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6` matched across all 64 hex chars,
  identical across two fresh cross-invocation runs.
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 EXACT three-way identity (27 cells; direction: exact Fraction equality, 0 mismatches)** —
    `ppv_direct == ppv_odds == ppv_enum` as exact `Fraction`s (direct Bayes, odds-form, integer-
    population exhaustive enumeration) across 3 base-rates × 3 accuracies × 3 k. PASS iff mismatches==0.
  - **G2 k-th-root ladder (36 cells; direction: exact boolean match, 0 violations, ladder strictly
    decreasing)** — the root-free polynomial test `p·a^k > (1−p)(1−a)^k` equals `PPV_k > ½` in every
    cell, AND at p=1/100 the minimal integer-percent accuracy clearing majority is 100/91/83 for
    k=1,2,3 (strictly decreasing). PASS iff boolean_violations==0 AND strictly decreasing.
  - **G3 ≥3σ vs folk intuition (M=400000; direction: z_majority ≥ 3)** — two-independent-screen
    empirical PPV clears ½ by many sigma while one screen of the same accuracy is far minority.
    passed_total=4551, PPV_emp=0.789277 within 3·SE of closed 0.784783, z_majority=47.85, single-screen
    PPV_1=0.161. PASS iff z≥3 AND emp within 3·SE of closed.
  - **G4 correlation-nullification (direction: PPV(ρ=1)==PPV_1 exact AND strictly decreasing in ρ;
    odds identity 12 cells 0 mismatches)** — over ρ∈{0,¼,½,¾,1} PPV=[0.784783,0.391176,0.262766,
    0.199072,0.161017] strictly decreasing, PPV at ρ=1 equals the single-screen 19/118 exactly; the
    odds-multiplication identity `odds = prior·∏LR_i` holds exactly (12 cells, 0 mismatches) with
    k-needed monotone in p. PASS iff corr_violations==0 AND ident_violations==0.
- Grounding: Wikipedia "Likelihood ratios in diagnostic testing" revid 1363827685, raw-wikitext sha1
  `bd86f75187e89db916dbd57fcbdcca2e9fd95d1a` (byte-pinned, matches the MediaWiki API + sha1sum).
  Firsthand-supports the odds-multiplication core: "The pretest odds of a particular diagnosis,
  multiplied by the likelihood ratio, determines the post-test odds." Honest caveat: the page states
  odds×LR (its direct iterate is successive multiplication) but does NOT itself prove the k-th-root
  ladder (G2) or correlation-nullification (G4) — the verifier proves those firsthand (0 violations),
  anchored to the page's Bayes claim by G1's exact three-way identity.

## ⟲ Previous-session review

Previous-session review: VERDICT 218 (Bélády's anomaly — FIFO page replacement is non-monotone in the
number of frames: on `[1,2,3,4,1,2,5,1,2,3,4,5]` FIFO faults 9 at 3 frames but 10 at 4 frames while
LRU, a stack algorithm, is provably immune, PROPOSAL 205 → V218) landed complete with a full-64 digest
MATCH (`e5c3517c…3bf7bff`) and all four gates PASS via the born-red HOLD choreography — `in-progress`
first commit, deliberate `complete` flip last. Its carry-forward was GATE-POLARITY discipline: read
each gate in ITS OWN direction (V218 mixed an EXACT witness gate, an EXHAUSTIVE both-zero gate, a ≥3σ
SIGNAL gate, and a two-legged ROBUSTNESS gate). V219 re-tunes that mix again: G1 is EXACT (a three-way
Fraction identity — any single mismatch FAILS), G2 is EXACT-BOOLEAN + a strictly-decreasing ladder (the
root-free polynomial must agree with PPV>½ in every cell AND 100/91/83 must strictly decrease), G3 is a
≥3σ SIGNAL gate (a LARGE z is the PASS — opposite polarity to G1/G2), and G4 is a NULLIFICATION gate
(the PASS is that redundancy exactly ERASES the second screen — PPV(ρ=1)==PPV_1 — plus an exact odds-
identity). The load-bearing evidence is the EXACT G1/G4 identity block (the three-way Bayes/odds/
enumeration equality and the exact odds-multiplication identity), with G2's ladder and G3's ≥3σ signal
corroborating that the composition is real at integer-exact and Monte-Carlo scale. Standing non-
contiguity persists: V137 (P124), V132 (P119), and the round-26 FLEET-slot V126 (P113) remain open
BELOW the high-water; landing V219 does not imply every lower verdict is closed.

## 💡 Session idea

The k-th-root ladder and the correlation-nullification gate are two faces of ONE quantity: the
**effective number of independent screens** k_eff. A cheap orthogonal extension that reuses
`ppv_two_with_correlation` verbatim would ADD a deterministic "k_eff gate": for a given correlation ρ
between two nominally-independent 95% screens, solve for the k_eff such that k_eff INDEPENDENT screens
reproduce the SAME posterior as the two correlated ones — k_eff falls smoothly from 2 (at ρ=0) to 1 (at
ρ=1), and the k-th-root ladder read at k_eff predicts the realized PPV. This turns the two separate
results (the ladder counts screens; the nullification gate discounts redundancy) into a single
continuous statement — redundancy is just a fractional screen — from which correlation-nullification is
the ρ→1 endpoint rather than a separate check. The digest-bearing dict and the four shipped gates stay
byte-identical; only a sibling exact k_eff gate is added.

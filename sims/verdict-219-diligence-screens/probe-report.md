# VERDICT 219 — Independent positives MULTIPLY the odds: k conditionally-independent symmetric screens (AND rule) compose by likelihood-ratio product, so the k-th screen need only clear (odds-against)^(1/k) — the k-th-root diligence ladder. At a 1% base rate two independent 95% screens flag a ~78%-good shortlist that a single 99% screen cannot, and the gain vanishes exactly when the screens are redundant (ρ=1 collapses PPV to the single-screen 0.161) — reproduce PROPOSAL 206

- **Slice:** sim-lab VERDICT 219 (reproduce and rule on PROPOSAL 206; P206 → V219, +13 offset; round-49 VENTURE slot)
- **Source proposal:** PROPOSAL 206 (idea-engine control/outbox.md, `## PROPOSAL 206 · 2026-07-20T09:52:48Z · status: sim-ready`); verifier landed on origin/main as squash 5d25021 (idea-engine PR #763)
- **Verifier (source):** `ideas/venture-lab/independent_screens_odds_ladder.py` (idea-engine) — copied byte-identical into this sim dir
- **Reproduced by:** copy the verifier byte-identical (diff exit 0), run it, capture stdout, recompute the results-dict sha256 and confirm full-64 match; two cross-invocation runs byte-identical
- **Timestamp (date -u):** 2026-07-20T10:14:29Z
- **SEED:** 20260717

## 📊 Model: Claude · high effort · verdict-reproduction

## Ruling: APPROVE

Fully reproduced. Digest `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6` matches the disclosed PROPOSAL 206 sha256 across all 64 hex characters; all four gates PASS each in its own direction (decision: sim-ready); the odds-multiplication core is externally grounded to a sha1-pinned Wikipedia revision with the k-th-root ladder and correlation-nullification proved firsthand at 0 violations; and the head is genuinely distinct from the shipped single-test knife-edge (P136 → V149).

## Head

Independent positives MULTIPLY the odds. For k conditionally-independent symmetric screens combined under the AND rule, `posterior_odds = prior_odds·(a/(1−a))^k` — so the k-th screen need only be ~`(odds-against)^(1/k)` accurate (the k-th-root ladder). At a 1% base rate, two independent 95% screens (AND rule) flag a ~78%-good shortlist (PPV = 361/460 ≈ 0.7848) that one 99% screen cannot (a single test at the base-rate knife-edge sits at PPV ≈ 0.5), and the gain vanishes exactly when the screens are redundant (at correlation ρ=1 the two-screen PPV collapses to the single-screen 19/118 ≈ 0.161).

## Reproduction

- Verifier copied byte-identical: `diff ideas/venture-lab/independent_screens_odds_ladder.py sims/verdict-219-diligence-screens/independent_screens_odds_ladder.py` → exit 0.
- results-dict sha256 posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical dict's own sha256 IS the digest.
- Disclosed digest:   `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6`
- Reproduced digest: `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6`
- **FULL-64 EXACT MATCH** — byte-grep confirms exactly one occurrence of the full 64-hex token; the printed token is 64 hex chars, no truncation.
- Full reproduction stdout: `run-stdout.txt` (cross-invocation copy `run-stdout-2.txt`).

## Determinism

- In-process double-run: `main()` runs `compute()` twice and asserts the canonical compact-JSON byte-equal before hashing — stdout `in_process_double_run: IDENTICAL`.
- Cross-invocation: two separate process invocations → `run-stdout.txt` and `run-stdout-2.txt`, `diff` exit 0 (byte-identical whole files including the digest line).

## Gate evaluation (against PROPOSAL 206's OWN criteria, in order — each read in ITS direction)

- **G1 EXACT three-way identity** (27 cells; direction: exact Fraction equality, mismatches==0): `ppv_direct == ppv_odds == ppv_enum` (direct Bayes, odds-form `prior_odds·(a/(1−a))^k`, integer-population exhaustive enumeration) across 3 base-rates × 3 accuracies × 3 k. **mismatches=0 → PASS.**
- **G2 k-th-root ladder** (36 cells; direction: exact boolean match, violations==0, ladder strictly decreasing): `[p·a^k > (1−p)(1−a)^k] == [PPV_k > ½]` in every cell, and at p=1/100 the minimal clearing accuracy is 100/91/83 % for k=1,2,3 (strictly decreasing). **boolean_violations=0, ladder [100,91,83] strictly decreasing → PASS.**
- **G3 ≥3σ vs folk intuition** (M=400000; direction: z_majority ≥ 3): two-screen empirical PPV=0.789277 (within 3·SE=0.006045 of closed 0.784783), z_majority=47.851639, single-screen contrast PPV_1=0.161017, passed_total=4551. **z≈47.85 ≥ 3 → PASS.**
- **G4 correlation-nullification** (direction: PPV(ρ=1)==PPV_1 exact AND strictly decreasing in ρ; odds identity 12 cells 0 mismatches): over ρ∈{0,¼,½,¾,1} PPV=[0.784783,0.391176,0.262766,0.199072,0.161017] strictly decreasing, PPV(ρ=1)=19/118 exactly equals the single-screen PPV; odds-multiplication identity `odds=prior·∏LR_i` holds exactly (12 cells, mismatches=0), k-needed [1,1,2,3] monotone in p. **corr_violations=0, ident_violations=0 → PASS.**

Overall: `decision: sim-ready`, gates {G1:true,G2:true,G3:true,G4:true}, all_pass=true, no first-failing gate.

## Grounding

- External, sha1-pinned: Wikipedia "Likelihood ratios in diagnostic testing", revid **1363827685** (pageid 935451), raw-wikitext sha1 `bd86f75187e89db916dbd57fcbdcca2e9fd95d1a` — MediaWiki API sha1 AND local `sha1sum` both equal the disclosed value.
- Firsthand support for the odds-multiplication CORE: "The pretest odds of a particular diagnosis, multiplied by the likelihood ratio, determines the post-test odds. This calculation is based on Bayes' theorem." (formula form on the page: `posttest odds = pretest odds × likelihood ratio`).
- Honest caveat (non-blocking): the article establishes odds×LR (whose k-fold iterate is P206's `prior_odds·∏LR_i`, anchored to the page by G1's exact three-way identity) but does NOT itself state the k-th-root ladder (G2) or correlation-nullification (G4); those are proved firsthand by the verifier at 0 violations. The "core-on-page, ladder/nullification-firsthand" split is FAIR — the load-bearing base identity is revision-pinned externally and the novel extensions are exactly what a firsthand verifier is for.

## Novelty

Genuinely DISTINCT from the shipped base-rate-ppv-collapse (PROPOSAL 136 → VERDICT 149, `ideas/fleet/base_rate_ppv_collapse.py`): that head is the SINGLE-test PPV knife-edge (one test at sens=spec=0.99, prev=0.01 gives posterior exactly 0.5 — critical accuracy a* = 1 − base_rate). P206 is the MULTI-test composition — odds multiplication over k screens, the k-th-root ladder, and correlation-nullification — that P136 explicitly left un-built. No verifier code overlap (disjoint functions and gates).

## Ruling evidence summary

VERDICT 219 reproduces PROPOSAL 206 bit-exact: the verifier copied byte-identical (diff exit 0), the results-dict sha256 `b04322fa5698021f2a78679abd43cdc3c3a878cbd4c5692a2376d222833e98c6` matches the disclosed digest across all 64 hex characters (single unique 64-hex token, no truncation), and determinism holds (in-process double-run IDENTICAL and two cross-invocation processes byte-identical). All four pre-registered gates PASS each read in its own direction: G1's exact three-way Bayes/odds/enumeration identity (27 cells, 0 mismatches), G2's k-th-root ladder (36-cell exact boolean match + the strictly-decreasing 100/91/83 clearing ladder), G3's ≥3σ two-screen majority (z=47.85, PPV_emp=0.789 vs single-screen 0.161), and G4's correlation-nullification (PPV(ρ=1)=19/118 exactly equals the single-screen PPV, odds-multiplication identity 12 cells 0 mismatches). The odds-multiplication core is externally grounded to a sha1-pinned Wikipedia revision (revid 1363827685, wikitext sha1 `bd86f75187e89db916dbd57fcbdcca2e9fd95d1a`), with the ladder and nullification proved firsthand — a fair split anchored by G1's exact identity. The head is genuinely distinct from the shipped single-test knife-edge (P136 → V149). **Ruling: APPROVE.**

# VERDICT 215 — Condorcet's jury theorem, the dark side: for p < 1/2 majority-vote accuracy is DECREASING in the jury size (optimal jury = a single voter) — reproduce PROPOSAL 202

- **Slice:** VERDICT 215 · PROPOSAL 202 (P202 → V215, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 202 — the DARK SIDE of Condorcet's jury theorem: for a jury of `n` independent voters each individually correct with probability `p`, majority vote beats a single voter and converges to certainty as `n → ∞` when `p > 1/2`; but when `p < 1/2` majority-vote accuracy is DECREASING in `n`, so adding voters makes things WORSE and the optimal jury is a SINGLE voter; at `p = 1/2` it is flat at `1/2` for every `n` (`ideas/venture-lab/condorcet-jury-committee-2026-07-20.md`)
- **Verifier (source):** idea-engine `ideas/venture-lab/condorcet-jury-committee-2026-07-20.py` (sha256 `97512e57dce05cf89e01e4da125509e879f8c2776ed214487b626600110383e5`); landed at idea-engine PR #750 / squash `43df276`
- **Reproduced by:** sim-lab session 2026-07-20-verdict-215, branch `claude/verdict-215` (built off origin/main `b9701d9`)
- **Timestamp (date -u):** 2026-07-20T07:43Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`)

## Head

Condorcet's jury theorem: `n` independent voters each vote correctly with probability
`p`; the majority verdict is correct with probability `M(n,p) = Σ_{k>n/2} C(n,k) p^k
(1−p)^{n−k}`. The LIGHT SIDE (classic) is `p > 1/2` ⇒ `M(n,p)` increasing in `n` and
`→ 1`. The head here is the **DARK SIDE** — the exact symmetric corollary for `p < 1/2`:
`M(n,p)` is then **DECREASING in `n`** and `→ 0`, so adding voters makes the jury WORSE
and the **optimal jury consists of a single voter**; at `p = 1/2` it is flat at `1/2` for
every `n`. The verifier certifies this three ways: a Monte-Carlo agreement gate at
`p = 0.60` and `p = 0.40`, an EXACT `2^n` exhaustive enumeration equated to the closed-form
`Fraction` `M(n,p)` over `n ∈ {1,3,5,7,9}` (with the monotone direction in each regime),
and a distribution-free gate (monotone value-transform + heavy-tailed Cauchy latent).

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` →
  **exit 0**. sha256 identical on both sides:
  `97512e57dce05cf89e01e4da125509e879f8c2776ed214487b626600110383e5`; sim-lab git blob
  `d4a46897ccb58ce12ae8afe3ef06f190e2276e08`. Source landed at idea-engine PR #750 /
  squash `43df276`.
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process
  **exit 0** (`all_pass = true`).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`; whole-dict, no self-field, stdout-only):**
  - disclosed (PROPOSAL 202): `e37537a46ae122d030e858f1f21015b2f528ab84d567a5b13227cf1905eaf1df`
  - reproduced (this run):    `e37537a46ae122d030e858f1f21015b2f528ab84d567a5b13227cf1905eaf1df`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality,
    single unique 64-hex token, no truncation). The verifier PRINTS this digest
    (`RESULTS_SHA256 = …` in `run-stdout.txt`).

## Determinism

- **In-process:** `double_run_identical=true` (the verifier runs its stochastic pipeline
  twice within one process and asserts the two results are identical — printed
  `double_run_identical=true` in `run-stdout.txt`).
- **Separate cross-invocation:** two independent `python3` invocations both printed
  `RESULTS_SHA256=e37537a46ae122d030e858f1f21015b2f528ab84d567a5b13227cf1905eaf1df`
  (identical results-dict digest both times).
- The verifier pins every Monte-Carlo stream off `SEED=20260717`, so the whole-dict
  sha256 is a reproducible `DETERMINISM DIGEST` with no self-field.

## Gate evaluation (against PROPOSAL 202's OWN criteria, in order)

Each gate is read in ITS OWN direction. **G1 and G3's statistical legs are AGREEMENT
gates** (a SMALL |z| is the PASS — the empirical rate must SIT ON the closed form; a HIGH
z would FAIL them). **G2 is an EXACT gate** (exhaustive enumeration must EQUAL the closed
form exactly). Reading G1/G3 as SIGNAL gates would invert the PASS.

- **G1 — STATISTICAL AGREEMENT (DIRECTION: small |z|, within 3σ; `T_mc = 200000`,
  `N_mc = 101`):**
  - above `p = 0.60`: empirical `0.97912` vs closed form `M(101,0.60) = 0.979103309`,
    `|z| = 0.0521848522` — within 3σ. **PASS.**
  - below `p = 0.40`: empirical `0.020815` vs closed form `M(101,0.40) = 0.020896691`,
    `|z| = 0.2554090111` — within 3σ. **PASS.**
  - Both legs confirm the dark-side value quantitatively: at `p = 0.40 < 1/2`, a
    101-voter majority is correct only `~2.09%` of the time (vs `40%` for a single
    voter) — the jury is far WORSE than one voter.
- **G2 — EXACTLY-TRUE (DIRECTION: exact `==`; exhaustive `2^n` ≡ closed-form
  `Fraction`, `n ∈ {1,3,5,7,9}`):** `enum_equals_closed_form_exact = true` for all three
  probability regimes:
  - `p = 3/5` (`> 1/2`): `M_grid = {1: 3/5, 3: 81/125, 5: 2133/3125, 7: 11097/15625,
    9: 286497/390625}`, **strictly increasing toward 1**, endpoint OK.
  - `p = 2/5` (`< 1/2`): `M_grid = {1: 2/5, 3: 44/125, 5: 992/3125, 7: 4528/15625,
    9: 104128/390625}`, **strictly decreasing toward 0**, endpoint OK — the dark side,
    exact.
  - `p = 1/2`: `M_grid = {1: 1/2, 3: 1/2, 5: 1/2, 7: 1/2, 9: 1/2}`, **flat at 1/2**,
    `M(3,½) = ½`, endpoint OK.
  - The three regimes `p < ½ → 0` / `p > ½ → 1` / `p = ½ = ½` all hold exactly.
    **PASS.**
- **G3 — DISTRIBUTION-FREE (two legs):**
  - EXACT leg: a monotone value-transform of the latent leaves every vote unchanged —
    `votes_bit_identical = true`, `rate_exactly_equal = true` (monotone rate `0.979245`
    == Bernoulli rate `0.979245`). **PASS.**
  - STATISTICAL leg (DIRECTION: small |z|): an INDEPENDENT heavy-tailed **Cauchy** latent
    gives rate `0.97911` vs closed form `0.979103309`, `|z| = 0.020919597` — within 3σ.
    **PASS.** Confirms the result is distribution-free (depends only on the sign / above-
    threshold probability, not on the latent's tail).

`all_pass = true`, `first_failing_gate = null`.

## Grounding

- **Source:** Wikipedia "Condorcet's jury theorem" oldid **1364571286** (raw wikitext).
- **Byte-pin:** raw wikitext sha1 **`1e6130332a53f4c8b92aa3872a25019b5f871ded`**, byte
  length **12161** — BOTH match the disclosed pin (`cjt-oldid-1364571286.wikitext` in the
  sim dir).
- **Content:** the article states the dark side **verbatim**: *"if p is less than 1/2 …
  then adding more voters makes things worse: the optimal jury consists of a single
  voter."* This is exactly the head the verifier reproduces (G2's `p = 2/5` grid
  decreasing toward 0, single-voter optimal). External byte-pinned citation — **STRONG.**

## Novelty

Assessed against the shipped corpus: SUBSTANTIVELY DISTINCT from the two prior shipped
Condorcet angles.
- **(a) Correlation-floor (→ VERDICT 142):** correlated-vote accuracy caps at
  `A_∞ = Φ(Φ⁻¹(p)/√ρ) < 1` for `p > ½` — a latent-Gaussian model with a CORRELATION
  lever; it never touches the `p < ½` regime and its mechanism is the correlation ceiling,
  not the below-average decay.
- **(b) Voting-cycle (PROPOSAL 168 → VERDICT 181):** Condorcet's PARADOX — the
  intransitive majority cycle in social choice over rankings — a DIFFERENT theorem
  entirely.
- **P202's head** is the classic INDEPENDENT jury theorem's `p < ½` regime: the exact
  binomial-tail identity and "optimal below-average jury = a single voter". Different
  mechanism, different regime, no verifier overlap. The dedup disclosure is present and
  honest and does NOT block APPROVE.
- **Honest caveat (recorded):** the `p < ½` result is the exact **symmetry-mirror** of
  the classic `p > ½` limit (`M(n,p) + M(n,1−p) = 1` for odd `n` — a known textbook
  corollary, faithfully reproduced/verified here, not a new discovery). But it is distinct
  from the shipped corpus and fully grounded, so **APPROVE stands, not QUALIFIED.**

## Ruling evidence summary

Digest matches full-64 exact
(`e37537a46ae122d030e858f1f21015b2f528ab84d567a5b13227cf1905eaf1df`, printed
`RESULTS_SHA256 =` line, single unique 64-hex token, no truncation); verifier
byte-identical (`diff` exit 0, sha256 `97512e57…`, git blob `d4a46897…`, source at PR
#750 / squash `43df276`); deterministic (in-process `double_run_identical=true` AND two
cross-invocation processes both `e37537a4…eaf1df`). All three gates hold in their stated
directions: **G1** small-|z| AGREEMENT (`0.0521848522` above, `0.2554090111` below, both
within 3σ), **G2** EXACT `2^n ≡ Fraction` enumeration across `n ∈ {1,3,5,7,9}` (increasing
at `3/5`, decreasing at `2/5`, flat `½` at `½`), **G3** DISTRIBUTION-FREE (votes
bit-identical under monotone transform; heavy-tailed Cauchy leg `|z| = 0.020919597` within
3σ). Grounding is byte-pinned and STRONG (Wikipedia "Condorcet's jury theorem" oldid
1364571286, raw wikitext sha1 `1e6130332a53f4c8b92aa3872a25019b5f871ded`, 12161 bytes),
and the article states the dark side verbatim. Novelty is substantively distinct from V142
(correlation-floor) and V181 (voting-cycle), with an honest symmetry-mirror caveat that
does not block. Reproduces the disclosed digest byte-for-byte, all gates hold in
direction, external grounding supports the head → **APPROVE**. (Run stdout:
`run-stdout.txt`.)

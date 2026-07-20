# VERDICT 212 — Vickrey second-price auction: truthful bidding b=v is a WEAKLY DOMINANT strategy — the shade v·(n−1)/n that STRICTLY helps in first-price is useless (weakly hurts) in Vickrey — reproduce PROPOSAL 199

> **Status:** complete

📊 Model: Claude Opus · effort high · task-class verdict-reproduction

started: 2026-07-20T06:04:16Z
flipped: 2026-07-20T06:08:40Z

Born-red HOLD (CLEARED): this card shipped `> **Status:** in-progress` on its FIRST
commit so the substrate born-red gate held the PR red until the slice was genuinely
done; it now flips to `complete` as the deliberate LAST commit, only after the sim dir
(byte-identical verifier copy + reproduction stdout), the digest match (full-64
exact: `a96d59f…6527c`), the in-order EXHAUSTIVE-DOMINANCE / EXACT-EXPECTATION /
MONTE-CARLO-CONTRAST / ROBUSTNESS gate evaluation (all PASS), the determinism check
(in-process double-run guarded), the grounding check (Wikipedia "Vickrey auction"
oldid 1338833083, raw wikitext sha1 398d2e4148cc7ee83f1343f720f6e243926bb895
byte-exact), and the probe-report have ALL landed — that flip clears the HOLD and
releases merge-on-green.

## What this verdict does

Reproduces PROPOSAL 199 (P199 → V212, +13 offset): the Vickrey second-price
auction truthfulness theorem. In a sealed-bid second-price (Vickrey) auction the
highest bidder wins but PAYS the second-highest bid; bidding your true value `b = v`
is a WEAKLY DOMINANT strategy — no matter what the other bidders do, no other bid
does strictly better and some bids do strictly worse. The sharp contrast that makes
this non-trivial: the symmetric first-price equilibrium shade `s = v·(n−1)/n`
STRICTLY raises expected surplus in a first-price auction, but the SAME shade is
useless in a Vickrey auction — it can only weakly LOWER surplus, never raise it,
because a bidder's payment does not depend on their own bid (only on whether they
win). Copies the disclosed verifier
`ideas/superbot-games/vickrey-truthful-dominance-2026-07-20.py` byte-identical into
`sims/verdict-212-vickrey-truthful/`, reproduces the results-dict sha256, confirms
determinism, and evaluates the four gates in order against the proposal's OWN
criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0, git blob
  `a3ccd070682205118a0c622dcf8243c543c0eafb`), stdlib-only (`hashlib`, `json`,
  `math`, `random`, `fractions`, `itertools`), SEED=20260717, Z_GATE=3.0.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical
  results dict's own sha256 IS the digest (`json.dumps(d, sort_keys=True,
  separators=(",",":"))`); target
  `a96d59f378e5d04a4e211dafafa22244e09d22126ba2c9b1e5f1cc0bdeb6527c` matched across
  all 64 hex (printed `results_sha256:` AND independently recomputed — both agree),
  byte-identical across two fresh cross-invocation runs.
- Determinism: in-process double-run guard (`main()` builds the results twice and
  exits 3 with "NON-DETERMINISTIC: in-process double-run diverged" if the canonical
  serializations differ); the guard holds, exit 0.
- Gates (in order, against the proposal's OWN criteria):
  - **G1 EXHAUSTIVE weak dominance** (integer-exact, wants 0 strict deviations):
    n=3, v≤4, b≤6 — over EVERY opponent bid profile and focal value on the grid,
    `deviations_strictly_better = 0`, `profiles_truthful_optimal = 245/245`
    (100%), and non-vacuous (`truthful_strictly_better_instances = 485 > 0`). The
    firsthand proof that truthful bidding weakly dominates.
  - **G2 EXACT-EXPECTATION contrast** (Fraction-exact closed form, wants sign
    match): n=3, v≤6, 343 profiles — `E[Δ firstprice] = +114/343 > 0` (shading
    helps in first-price), `E[Δ vickrey] = −27/343 ≤ 0` (shading weakly hurts in
    Vickrey), and `E[truthful first-price surplus] = 0/1` EXACTLY.
  - **G3 MONTE-CARLO surprise** (wants high z for first-price, z≤0 for Vickrey):
    n=3, v≤12, 200000 draws — `z_firstprice = +192.175024 ≥ 3` (the shade
    genuinely helps in first-price), `z_vickrey = −155.312083 ≤ 0` (the same shade
    never helps in Vickrey).
  - **G4 ROBUSTNESS / shift** (wants 0 mismatches): n=2 shift (v≤6, b≤8, 63
    profiles) deviations=0; n=4 shift (v≤3, b≤5, 864 profiles) deviations=0; and
    the G3 contrast persists under a shifted range (n=4, v≤20): `z_firstprice =
    +156.675416`, `z_vickrey = −142.040465`.
  - `all_pass = true`.
- Grounding: Wikipedia "Vickrey auction" oldid 1338833083, raw wikitext (MediaWiki
  `action=raw`), 12916 bytes, sha1 `398d2e4148cc7ee83f1343f720f6e243926bb895`
  byte-exact to the disclosed pin; the section "== Proof of dominance of truthful
  bidding ==" proves truthful bidding is weakly dominant (both the overbid and
  underbid cases), supporting the head. Strong external byte-pinned grounding.

## ⟲ Previous-session review

Previous-session review: VERDICT 211 (Weitzman's Pandora's Box reservation-index
rule, PROPOSAL 198) landed complete with a full-64 digest MATCH
(`a0cb19c…1fcad`) and all four gates PASS via the born-red HOLD choreography —
`in-progress` first commit, deliberate `complete` flip last. Its carry-forward was
that the load-bearing evidence can be an EXACT `Fraction` identity (G1: 0 mismatches
over 800 instances), not a z-score, and that eye-catching surprise z-scores must not
be mistaken for the theorem-grade evidence. V212 inherits that discipline and sharpens
it with a POLARITY split WITHIN one Monte-Carlo gate: G3 here is a two-sided contrast
where the SAME shade must produce a LARGE positive z in first-price (z=+192.18, help
is real) AND a NON-positive z in Vickrey (z=−155.31, help is absent) — reading either
z in isolation is a trap; the PASS is the *contrast*. And as in V211 the firsthand
proof is the exact/exhaustive gate: G1's `deviations_strictly_better = 0` over a full
enumeration and G2's exact `E[Δ vickrey] = −27/343 ≤ 0` are the load-bearing facts,
with G3/G4's big z-scores the corroborating (not primary) signal. Standing
non-contiguity persists: V137 (P124), V132 (P119), and the round-26 FLEET-slot V126
(P113) remain open BELOW the high-water; landing V212 does not imply every lower
verdict is closed.

## 💡 Session idea

G2 reports the Vickrey shade's expected surplus delta as a single aggregate
(`E[Δ vickrey] = −27/343`, strictly negative) — it certifies that shading weakly
hurts in expectation, but never localizes WHERE the −27/343 is generated. The
weak-dominance theorem says the shade `s = v·(n−1)/n` never helps *pointwise* in
Vickrey; it can only differ from truthful when the shade flips the win/lose outcome,
i.e. when `s < max_opp ≤ v` (truthful would have won and captured `v − max_opp > 0`,
but the shade loses and gets 0). A cheap orthogonal extension reusing the exact
`g2_exact_expectation` loop verbatim: for each profile also record whether the shade
strictly changed the Vickrey outcome, and sum the exact surplus lost on exactly those
profiles. My hypothesis is that the entire `−27/343` is concentrated on the thin band
of profiles where `s < max_opp ≤ v` — a "the whole loss is a dropped-win" one-liner —
turning the abstract "shading weakly hurts" into a crisp, countable witness set that
mirrors G1's exhaustive-dominance proof from the expectation side. Only the
bookkeeping inside `g2_exact_expectation` changes; the closed-form arithmetic and the
digest-bearing results dict stay untouched (the extension would live in a sibling
diagnostic, not the digest path).

# REPORT — VERDICT 057: keyword tiling vs independent picks (PROPOSAL 046)

**Ruling: approve** — per the pre-registered rule, evaluated IN ORDER, REJECT
FIRST, margin m = 1/50 exact, on Arm-A exact numbers.

- **REJECT (checked FIRST) does not fire:** R ≥ 1/50 in 9 of 12 cells (REJECT
  needs 0 of 12).
- **APPROVE fires:** R ≥ 1/50 in **9 of 12** cells (band: ≥ 9) AND in **3 of
  3** γ = 1/4 cells (band: ≥ 2), AND the seed-20261322 stability leg
  reproduces the ruling (its own R table lands the same APPROVE band, 9 of
  12 / 3 of 3) through both twin evaluators (Fraction comparisons vs
  pure-integer cross-multiplication, opposite iteration orders — agree on
  Arm A and stability inputs).

## The 12-cell R table (Arm A exact; floats for reading, exact rationals in results.json)

| cell | γ=0 | γ=1/4 | γ=1 | γ=4 |
|------|-----|-------|-----|-----|
| LOW  | +0.0189 (miss) | +0.7179 ✓ | +1.2277 ✓ | +1.4472 ✓ |
| MED  | −0.3779 (miss) | +0.1542 ✓ | +0.4664 ✓ | +0.5461 ✓ |
| HIGH | −0.3150 (miss) | +0.0654 ✓ | +0.1559 ✓ | +0.0899 ✓ |

The three misses are exactly the γ = 0 column: with zero same-catalog rank
dilution, collisions are pure position-stacking and GREEDY wins MED (−38%)
and HIGH (−32%) outright while LOW lands just under the margin (+1.89% <
2%). At every nonzero registered γ — including the weakest, γ = 1/4, the row
the APPROVE band deliberately conditions on — tiling buys 6.5% to 145%
catalog discovery traffic. The map's cannibalization theory carries the
ruling: first-claim-wins pays exactly when same-shelf catalog dilution is
nonzero at all, and pays most where registers spread (LOW row: tiled titles
keep uncontested high-Zipf shelves).

## Run evidence

- Command: `python3 tiling_sim.py` — exit 0, **389 self-checks, 0 failed**,
  ~4 s, stdlib-only, hermetic (reads only its own fixtures.json), no
  wall-clock in any output.
- **Byte identity:** stdout + results.json byte-identical across two full
  process runs by external diff. sha256 stdout (run-stdout.txt)
  `8718612ac21b352cfbc9914be7b06a2d4f9b2c6b8b7f2adcb146e1c537caf0c2`;
  results.json
  `b5eb7feec036181e8303a29cada761e3d6b27241d2b905fa9b5c363069f3da58`.
- **Seeds:** 20261321 main / 20261322 stability / 20261323 reporting /
  20261324 aux registered-never-drawn (no RNG constructed with it,
  asserted) — strictly above the P045/V056 high-water 20261320. NEW REGISTRY
  HIGH-WATER 20261324.
- **CPython pinned:** 3.11, asserted at startup.
- **Draw sentinels exact:** main 7,200,000 = 12 × 200,000 × 3 / stability
  720,000 / reporting 2,160,000 = 3 scenarios × 12 × 20,000 × 3.
- **Arm agreement:** main gate ≤ 5/1000 PASS all 24 world-cells (worst
  0.002411); stability gate ≤ 15/1000 PASS (worst 0.006509); reporting
  confirmations PASS (worst 0.009559).

## Gates (all green)

F1 normalization (Σw = Σv = 1, w1/w2 = 2 exact); F2 two-title hand world
exact (T_GREEDY(γ=1) = 1/4, T_GREEDY(γ=0) = 1/2, T_TILE = 5/12 at every γ);
F3 tie order (external 3/4 above catalog 3/4; lower title index; claim order
t = 1..14); F4 β pmf; F5 dilution identities (f, f/2, f/9 exact); F6
theorems — T_TILE exactly γ-invariant in the zero-fallback LOW row,
non-increasing in γ in the fallback rows (MED, HIGH), T_GREEDY non-increasing
in γ in every row, degenerate all-fits-zero ⇒ T = 0; allocation sanity
(exactly 7 + 2 distinct claims per title, both policies, all rows; TILE
same-cell pairs ≡ counted fallback shares); GREEDY collision monotonicity
LOW ≤ MED ≤ HIGH held (18 ≤ 49 ≤ 78 extra claims — no anomaly).

## Allocation facts (reporting)

- GREEDY colliding claims (Σ(j−1), kw+cat): LOW 18 (9 cells) / MED 49 (28) /
  HIGH 78 (32).
- TILE fallback shares: LOW 0 + 0 / MED 9 kw + 5 cat / HIGH 35 kw + 12 cat.
  Note an expectation miss in the PROPOSAL 046 prose (not in any registered
  gate): the outbox block expected keyword tiling to exhaust only in HIGH;
  measured, MED keywords also exhaust (9 fallback shares — 98 claims into 89
  reachable cells is a pigeonhole, so this was structural). No registered
  gate or band references that expectation; F6a's conditional form (zero
  fallback ⇒ invariance) absorbed it. Disclosed rather than smoothed.

## Reporting-only legs (cannot flip; one straddle FIRED)

- Mass split (1/2, 1/2): APPROVE-band, 10 of 12. Flatter β
  (1/3, 4/15, 1/5, 2/15, 1/15) with full allocation re-derivation:
  APPROVE-band, 9 of 12 — the registration's named most-likely flip (steep β
  disclosed GENEROUS TO APPROVE) did NOT flip the band at the registered
  flatter leg.
- **Straddle FIRED (named, reporting-only):** mass split (4/5, 1/5) lands
  NEITHER-BAND — 8 of 12 cells, 2 of 3 γ = 1/4 cells (HIGH γ = 1/4 drops
  under the margin when keyword mass dominates). The APPROVE leans on the
  3/5–2/5 split width: a keyword-dominated discovery world thins the
  category-side gains that carry HIGH γ = 1/4 over the line.
- Margin sweep: m = 1/100 → 10 of 12 (LOW γ = 0 at +1.89% clears the softer
  bar); m = 1/25 → 9 of 12 (unchanged). The ruling is margin-stable at the
  harsher registered sweep point.
- Per-title tiling tax and keyword/category decomposition: full exact tables
  in results.json (`per_title_traffic_primary`, `decomp_*`).

## Honesty notes / boundaries (from the registration, stated with the ruling)

- **Knife-edge disclosure:** the APPROVE cell count sits exactly at the band
  edge (9 of 12, band ≥ 9) — the γ = 0 column is the entire miss set. The
  finding one notch finer than the band: tiling pays IFF same-catalog
  dilution is nonzero (γ ≥ 1/4 everywhere on the registered grid), and at
  γ = 0 exactly the convention is dead weight or worse (MED −38%, HIGH −32%).
  The registered APPROVE band anticipated precisely this shape (its γ = 1/4
  conjunct exists so the ruling never leans on strong dilution alone), so
  APPROVE issues; the γ = 0 boundary rides every citation.
- **Invented-widths boundary:** γ, both Zipf shapes, β, the external profile,
  the windows/homes, and the mass split carry NO live datapoint anywhere in
  the fleet (catalog pre-launch, zero organic sales) — the fired (4/5, 1/5)
  straddle marks where the split width bites. The map's own C2
  page-co-occurrence browse check (one owner session once two titles are
  live) is the named cheapest live probe measuring γ's counterpart.
- **Click-model boundary:** the steep primary β is GENEROUS TO APPROVE
  (penalizes same-shelf stacking); the registered flatter leg holds the band,
  so the APPROVE does not rest on the steep pin alone — but a genuinely flat
  scroll-deep world is out of registered scope.
- **Static-ranking / single-phrase-session boundaries:** C1's also-bought
  mechanism is dynamic in reality, modeled as static dilution; no cross-shelf
  substitution — both named out of registered scope by the registration.

## Conformance disclosures

- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run. Fixtures committed BEFORE the runner (git trail: born-red
  card → fixtures.json → runner + this accepted run).
- sha256 (full, from the two-process diff): stdout
  `8718612ac21b352cfbc9914be7b06a2d4f9b2c6b8b7f2adcb146e1c537caf0c2`
  (run-stdout.txt), results.json
  `b5eb7feec036181e8303a29cada761e3d6b27241d2b905fa9b5c363069f3da58`.

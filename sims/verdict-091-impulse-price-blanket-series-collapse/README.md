# verdict-091 — the impulse-price blanket series collapse (INTAKE 078)

Prices idea-engine PROPOSAL 078 exactly where it lives: venture-lab's
catalog-wide impulse-price blanket — "No $0.99 impulse price recommended
(drops to 35%)" — is stamped on **26 vetting packets** @ `021cba9`,
justified in exactly two as "70% of $3.99 beats 35% of $0.99 **at any
plausible volume ratio**" (`the-twelfth-cake.md:106–107`, inherited
verbatim by `de-driekoningentaart.md:106–108`), and TAUGHT as
transferable procedure by the catalog's own sellable product
(`candidates/ai-novella-production-kit/guide/06-pricing-and-listing.md`:
"the *procedure* transfers") — while the sentence never computes the
volume ratio it declares implausible. Exact `fractions.Fraction`
arithmetic on the plan's own committed royalty hard fact (70% only on
$2.99–$9.99 inclusive, 35% outside, per-MB fee on the 70% tier only)
gives it three structures no committed doc states: **T2 — the BAR LAW**:
the standalone break-even volume ratio is EXACTLY twice the price ratio
(the 2 being the tier ratio 70/35) — **266/33 ≈ 8.06** at the committed
($3.99, $0.99) pair, 998/99 at $4.99, 598/99 at the band floor; the
blanket is RIGHT standalone. **T1 — the BORDER HALVING**: the royalty
function jumps by a factor of EXACTLY 2 at $2.99, leaving a forbidden
per-sale band [2093/2000, 2093/1000) whose **width (2093/2000) exactly
equals its own lower edge** — two registered margin-0 contacts; no
committed price can earn between $1.0465 and $2.093 per sale. **T3 —
the SERIES COLLAPSE**: for book 1 of a K-book series with per-boundary
read-through r (downstream books stay at the committed series-matched
price under BOTH arms), the bar m\*(K, r) collapses — at the catalog's
own complete 3-book Night Kiln ($4.99 committed): **m\*(3, 3/4) =
18463/11271 ≈ 1.6381 ≤ 2**, a mere doubling; at the Marmalade packet's
own committed 36-book Peridale comp: **≈ 1.2907 ≤ 4/3**; exact K→∞
crossing at **r\* = 400/899**. **T5 — KU DAMPENING signed**: with borrow
share β the bar decreases strictly toward 1 at every J — the lever
shrinks, never flips (named cell 5489/3691). The same tree commits the
repair text once and defers it (`the-marmalade-post.md:93–95`: "if a
later series has 3+ books, a book-1 promo price becomes a real ⚑ owner
decision — flagged for then, not now") — "then" is already on `main`.
All decision arithmetic is seedless exact Fractions (REJECT checked
first); the m\*_∞(9/10)-vs-11/10 knife-edge (margin exactly 91/90810) is
registered and EXCLUDED from every decision clause. The runner is
hermetic — it reads ONLY `fixtures.json` (committed before the runner);
every COMMITTED external constant was re-verified firsthand at
venture-lab `021cba9` BEFORE the fixture was written, and the V049
anchor roy(0.99) = 693/2000 was read at this repo's own
`sims/verdict-049-ku-exclusivity/REPORT.md:27`.

## Run

```
python3 sims/verdict-091-impulse-price-blanket-series-collapse/impulse_price_blanket_series_collapse_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, < 0.1 s. Every
decision number is an exact Fraction; the seeded Arm R carries no
statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 078 block / idea file (the tiers and band edges, the promo
  and committed prices, the K anchors and r/β/J/δ grids, the census
  grammar + the 26-file list + the pinned whitespace-collapsed excerpts
  that carry the hermetic recount, the Night Kiln word counts, the V049
  external anchor, the F-census anchors as [num, den] VALUE PAIRS (the
  V090 session idea applied), the four typed must-equal contacts
  C1–C4, the REGISTERED Arm-R draw-order grammar with seeds
  20261700–703 and the disclosed previews, the decision rule with its
  knife-edge exclusion gate, the typed margin-ledger cells). Sim-chosen
  values disclosed as vacancies: the census grammar/file-list
  derivation, the m\*(36, r) row beyond the two named cells, the fee
  sweep beyond the $3.99 row, the Arm-R income-accumulation convention
  and promo-arm values.
- `impulse_price_blanket_series_collapse_sim.py` — the three-arm runner
  (A seedless exact-Fraction closed forms / B independently-written
  per-mass ledger twin with its own decision evaluator / R seeded
  reporting-only finite-cohort traces under the registered grammar).
- `results.json` — canonical machine-readable outputs (sorted keys, no
  timestamps): the border/band contacts, the bar table with the fee
  sweep, the full m\*(K, r) surface with r\* and the excluded
  knife-edge, the KU rows, the census recount, the Arm-R traces, the
  decision clauses, the structured anomaly census, the seed registry.
- `run-stdout.txt` — the accepted run's stdout.
- `REPORT.md` — the ruling against the pre-registered bands, the
  numbers, the margin ledger, falsifiability, and the consequence
  hand-off.

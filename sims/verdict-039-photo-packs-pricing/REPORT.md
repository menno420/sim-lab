# REPORT — Photo-packs pricing: PWYW vs $5 fixed, a $3 anchor, and a two-pack bundle (idea-engine ORDER 006 SIM-REQUEST 1, seat venture-lab)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 006 · 2026-07-13T09:02Z.
> Packet read READ-ONLY at `menno420/venture-lab` @
> `847b636f174d439949afeffac55025dde814514b`.
> Run: `python3 sims/verdict-039-photo-packs-pricing/photo_packs_pricing_sim.py`

Binding spec, verbatim (ORDER 006 `do:`, SIM-REQUEST 1):

> (1) PHOTO PACKS — PWYW-vs-$5, a $3 anchor, and a two-pack bundle (the
> packs themselves are hard-gated on owner-held originals; the pricing
> verdict is serveable now);

The packet's own asked-for quantities, verbatim (vetting packet §3 @ 847b636):

> Genuine uncertainty flagged as SIM-REQUEST (via outbox lane, not this
> packet): (1) PWYW vs fixed $5 conversion for cold wallpaper packs;
> (2) whether saturated golden-hours should anchor at $3 instead; (3)
> two-pack bundle price. No cited evidence either way — defaults above
> stand until simulated or measured.

## METHOD LABEL: `simulation` (exact-analytic decision arms + seeded gates)

Method ladder rung 1 — NUMERIC with an exact core: every decision quantity
is a closed-form `Fraction` (zero sampling error); the only RNG is two
seeded robustness legs (seeds **20260790 / 20260791**, registered in
fixtures.json strictly above the recorded fleet high-water 20260775 with a
deliberate +14 gap for the in-flight sibling slices V036/V038) that act as
sign-agreement GATES on the exact frontier logic — reporting-only, no seed
can move the ruling. 4,761 self-checks, 0 failed, exit 0.

## PREMISE (verified at drafting, pinned into fixtures.json — hermeticity by construction)

The sim reads exactly ONE file (its committed `fixtures.json`) and touches
no repo state, network, or wall clock. Every constant is quoted verbatim
with source path@SHA (all @ venture-lab `847b636`):

- **Default price:** "$5 fixed per pack, both packs, Gumroad direct"
  (vetting §3; `packs.json price_usd: 5`; OWNER-QUEUE D7 default, floor $3).
- **Gumroad direct fees:** 10% + $0.50/transaction + ~2.9% + $0.30
  processing → net(p) = 0.871p − 0.80 (MARKET-PLAN §(a)); **Discover** flat
  30% → net(p) = 0.70p; **Ko-fi free** 5% + ~3% + $0.30 → net(p) = 0.92p −
  0.30.
- **Packet worked nets reconciled exactly:** $5 direct = 711/200 = $3.555
  (packet's ≈$3.56 rounds up); Discover $3.50 exact; Ko-fi $4.30 exact.
- **Fee-floor rule reproduced exactly:** fixed fees $0.80 exceed 25% of
  price below $3.20; at the $3 anchor itself the share is 4/15 ≈ 26.7% —
  the $3 anchor sits ON the packet's own "do not price under $3" line.
- **Demand reality:** "$0–30 / first 90 days cold; the cited $10-total
  creator anecdote is the realistic anchor" (vetting §3) — no projection
  is made anywhere in this verdict.
- **Hard gate honored:** "photo packs (owner-held originals)" (MORNING
  TALLY) — this verdict prices; it cannot and does not unblock the build.

**Recorded gaps (G1–G6, registered before the runner):** G1 no PWYW
conversion/mean-payment data (the packet's verbatim "No cited evidence
either way") · G2 no $3-vs-$5 elasticity data · G3 no bundle-mix data ·
G4 no absolute demand data · G5 processor rates are cited approximations ·
G6 the sellable artifact does not exist (owner-gated). **ASSUMED (A1–A4,
flagged):** bundle weak-dominance frame (adding a listing does not shrink
the buyer pool; decision leg at fresh-buyer rate f = 0, the conservative
end) · processor rate fixed at the packet's cited values (±0.6pp bracket
ships) · PWYW takers pay ≥ floor or $0 with fees only on paid transactions ·
grid spans are registered bands, not measurements.

## What the sim MODELS (per committed baseline buyer — one $5 single-pack buyer on the picked channel)

- **FIXED_5:** E[net] = net(5) = **$3.555 exact** (direct). Zero unmeasured
  parameters.
- **PWYW:** E[net] = u·net(w̄) — u = paid PWYW transactions per baseline
  buyer, w̄ = mean paid amount; both unmeasured (G1).
- **ANCHOR_3:** E[net] = ρ·net(3) — ρ = unit-sales ratio at $3 vs $5;
  unmeasured (G2).
- **BUNDLE_2PACK:** ΔE[net] vs no-bundle = t·(net(b) − 2·net(5)) +
  (1−t)·g·(net(b) − net(5)) + f·net(b); mix (t, g, f) unmeasured (G3),
  decision at f = 0.

## MEASURED (exact, no sampling error; decision channel = Gumroad direct, the packet's D6 default)

- **$3 anchor bar:** ANCHOR_3 ≥ FIXED_5 ⇔ **ρ ≥ 3555/1813 = 1.960838** —
  the $3 price must deliver **+96.1% unit sales to tie**. Mechanism: price
  falls 40% but net-per-sale falls **49.0%** (1742/3555), because the $0.80
  fixed fees don't scale down. Channel frontier: Ko-fi bar 215/123 ≈ 1.748,
  Discover 5/3 ≈ 1.667 — the anchor is hardest to justify exactly where the
  packet defaults (direct). WIN region: 21/41 grid points (ρ ≥ 2.0), all
  above any measured datum (none exists).
- **PWYW frontier:** PWYW ≥ FIXED_5 ⇔ u·net(w̄) ≥ 3.555. Landmarks: at
  paid parity u = 1 it needs **mean voluntary payment w̄ ≥ $5.00 exactly**;
  at the packet's own $3 floor it needs u ≥ 3555/1813 — **the same
  +96.1% bar as the $3 anchor** (PWYW averaging the floor IS $3 pricing);
  at w̄ = $4 it needs u ≥ 1.3245. WIN region: 217/651 cells, every one
  conditioned on unmeasured (u, w̄).
- **Two-pack bundle dominance band:** net(b) ≥ 2·net(5) ⇔ **b ≥ 7910/871 =
  $9.0815**. Inside [$9.0815, $10] the bundle is **weakly dominant under A1
  at f = 0: 441/441 mix cells non-losing per registered price point** —
  worst case $0, and every two-pack buyer strictly gains the saved second
  per-transaction fixed fee (at $10.00: **+$0.80 exactly**; at $9.99: net
  $7.90129, **+$0.79129** vs two separate $5 sales). Below b*: at $8 the
  bundle loses $0.942 per cannibalized two-pack buyer and needs upgrade
  share g ≥ 0.942·t/(2.613·(1−t)) — measured mix required (G3). Channel
  caveat that ships with the number: on **Discover b* = $10.00 exactly**
  (no fixed fee → zero demand-free discount room); Ko-fi b* = 445/46 =
  $9.6739.
- **Processing-rate bracket (reporting-only, cannot flip):** at 2.3%/3.5%
  processing the anchor bar stays within [1.94, 1.99] and b* moves ~±6¢ —
  no decision margin's sign moves anywhere in the bracket (G5).
- **Scale rendering (reporting-only, packet's own band):** at the $10-anchor
  / $30-cap gross scenarios (2 / 6 sales at $5): FIXED_5 nets $7.11 /
  $21.33; the same units at $3 net $3.63 / $10.88 — **an unforced −49% net
  cut** if the anchor ships without its +96.1% uplift.

## RULING (pre-registered rule, evaluated in order): **R3-CONDITIONAL-DEFAULT**

- R1 PWYW-WINS requires a MEASURED (û, ŵ) clearing the frontier — **cannot
  fire**: the packet states verbatim "No cited evidence either way" (G1).
- R2 ANCHOR-WINS requires a MEASURED unit ratio ρ̂ ≥ 3555/1813 — **cannot
  fire** (G2).
- **R3 fires** (G1/G2/G3 all open; dominance band non-empty): **keep the
  packet's own $5-fixed default per pack** (net $3.555/sale exact — the
  only arm with zero unmeasured parameters; OWNER-QUEUE D7 stands
  unchanged) **and ADD the two-pack bundle priced inside [$9.09, $10] —
  recommend $9.99** (net $7.90129/sale exact; weakly dominant under A1:
  cannot lose at any registered mix, strictly banks the $0.80 fee save on
  every two-pack buyer). **The $3 anchor is not recommendable** without a
  measured ≈2× unit uplift — and it sits on the packet's own fee floor
  (fixed fees 26.7% of price). **PWYW is not recommendable as a
  replacement** — its win needs mean voluntary payment ≥ $5 at paid parity
  or the same 2× bar at the $3 floor, all unmeasured. **Deep-discount
  bundles (< $9.09) park** behind the measured mix frontier.

## The 8-question battery (idea-engine README.md "probe battery v0", per ORDER 006)

1. **What is this really?** A four-arm expected-net comparison fully
   determined by the packet's own cited fee schedules except for buyer
   behavior the packet itself declares unmeasured. The fee structure does
   the deciding: $0.80 of every transaction is fixed, so cheap prices and
   split transactions are taxed — which makes the $3 anchor expensive and
   the bundle free money above b*.
2. **What is the possibility space?** Arms: PWYW, $5 fixed, $3 anchor,
   two-pack bundle; unmodeled hybrids re-priceable from the same kernel:
   PWYW-with-$5-floor (per-sale it can't lose vs $5; its conversion-side
   risk is exactly G1), $3 anchor on Ko-fi only (bar drops to 1.748),
   bundle-on-Discover (b* = $10 → pointless), $4 anchor (bar 3555/2684 ≈
   1.324).
3. **Most advanced capability from the simplest implementation?** The exact
   channel-frontier table: three linear net functions turn every pricing
   question the packet asked into one closed-form inequality — and convert
   any future measured rate into an instant decision by lookup.
4. **What breaks it?** A measured PWYW dataset clearing u·net(w̄) ≥ 3.555
   (R1 flips it); a measured 2× elasticity at $3 (R2); a real
   choice-overload effect violating A1 (the bundle add would then need
   measured traffic data); processor-rate drift beyond the bracketed
   ±0.6pp (G5); Gumroad fee-schedule changes (all frontiers recompute,
   same kernel).
5. **What does it unlock?** OWNER-QUEUE D7 keeps its default with evidence
   instead of instinct; a new bundle row becomes queueable the day the
   packs clear the originals gate; the same fee-kernel re-prices the other
   two venture pricing SIM-REQUESTs in ORDER 006 (Ship-It bundle anchors,
   cookbook PWYW) by fixture swap.
6. **What does it depend on?** The pinned MARKET-PLAN fee schedules, the
   vetting §3 defaults, A1–A4 as flagged — and nothing else; the owner's
   D6 storefront pick only selects which frontier column applies (the
   ruling states the decision on the D6 default, direct).
7. **Which lane should build it?** None — nothing to build. The packs are
   owner-gated on originals (G6); venture-lab consumes this verdict via
   manager relay; the only "build" is the named measurement, which needs a
   live listing first.
8. **Smallest shippable slice?** When the originals gate clears: publish
   both packs at $5 (D7 unchanged) plus one bundle listing at $9.99 —
   zero new decisions required, both numbers carried by this verdict; the
   PWYW/anchor questions stay parked on their frontiers until live sales
   data exists.

## VALIDITY GATE (what would invalidate this verdict)

- A **measured** PWYW pair (û, ŵ) with û·net(ŵ) ≥ 3.555 → PWYW wins by R1;
  the committed frontier converts the measurement by lookup, no re-run.
- A **measured** $3-vs-$5 unit ratio ρ̂ ≥ 3555/1813 → the anchor wins by R2.
- **Measured bundle mix** (t, g, f) → bundle prices below $9.09 become
  decidable from the committed $8-frontier; a measured f > 0 only
  strengthens the bundle add (one-sided in its favor — stated).
- Evidence **against A1** (bundle listing shrinking total buyers) → the
  bundle add loses its dominance claim and needs traffic data.
- A fee-schedule change off the pinned constants → all frontiers recompute
  (same kernel, new fixtures).
- LIMITS: no sales projection is made (the packet's "$0–30 / first 90 days
  cold" stands); the ruling ranks pricing arms per committed buyer, it does
  not size demand; the packs remain hard-gated on owner-held originals
  (G6) — nothing here queues a publish click.

## DETERMINISM

`SELF-CHECKS: 4761 passed, 0 failed`, exit 0. Decision arms exact
(Fractions); seeds 20260790/20260791 drive gate legs only. stdout and
results.json byte-identical across two full process runs by external
`diff` (empty); sha256 stdout
`af734e5a10800259dd0b5f8f55f33bcb8eda0b39404c2106d7b697b7911d1869`,
results.json
`5e41cdf1036a025a08e690bff04cc84aad6310cd6611cfec48dfa05a7cec558f`.

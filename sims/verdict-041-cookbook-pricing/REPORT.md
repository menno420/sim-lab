# REPORT — Narrow-TAM cookbook pricing: $19 fixed vs PWYW (idea-engine ORDER 006 SIM-REQUEST 3, seat venture-lab; canonical case: Merge-Wall Cookbook $19)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 006 · 2026-07-13T09:02Z.
> Packet read READ-ONLY at `menno420/venture-lab` @
> `f15e9f187b41f7f968f67e22200f18d4a89dfcde`.
> Run: `python3 sims/verdict-041-cookbook-pricing/cookbook_pricing_sim.py`

Binding spec, verbatim (ORDER 006 `do:`, SIM-REQUEST 3):

> (3) NARROW-TAM COOKBOOKS — $19 fixed vs PWYW (canonical case: Merge-Wall
> Cookbook $19).

The packet's own request, verbatim (MORNING TALLY @ f15e9f1):

> SIM-REQUEST: photo packs PWYW-vs-$5 + $3 anchor + two-pack bundle · bundle
> $59 vs $64/$68 anchors · $19 fixed vs PWYW for narrow-TAM cookbooks ·
> owner sandbox repo to production-verify merge-on-green.yml.

Kernel lineage: VERDICT 039's target line pre-named this inheritance
verbatim — "the cookbook PWYW question inherits this verdict's PWYW
frontier form directly" — and VERDICT 040 restated it ("the same exact
fee-kernel re-prices it by fixture swap, per the V037/V039 kernel
lineage"). This report is that inheritance, executed.

## METHOD LABEL: `simulation` (exact-analytic decision arms, zero RNG)

Method ladder rung 1 — NUMERIC with a fully exact core: every decision
quantity is a closed-form `Fraction` (zero sampling error) and **zero seeds
are drawn** (the V037/V038 degenerate-case precedent — a fully exact head
draws nothing; the fleet seed high-water stands at **20261280**, claimed by
V043 and recorded at origin/main `68c9317`, untouched here). Twin
evaluators (Fraction expected-value comparison vs pure-integer
cross-multiplied inequality) agree on all 3 × 1,829 grid cells. 5,612
self-checks, 0 failed, exit 0.

## PREMISE (verified at drafting, pinned into fixtures.json — hermeticity by construction)

The sim reads exactly ONE file (its committed `fixtures.json`) and touches
no repo state, network, or wall clock. Every constant is quoted verbatim
with source path@SHA (all @ venture-lab `f15e9f1`):

- **Committed price:** "$19 one-time — set at intake … and recorded
  identically in the listing copy, the click-script, and here"
  (merge-wall-cookbook vetting §3; INTAKE.md "Conservative revenue
  estimate: $19 one-time").
- **Price chain:** "$15 (kill-rule kit, false-green) < **$19** =
  template-packs $19 PWYW < SWTK $29 live (PR #86) < field-manual $39 <
  membership-kit $49" (vetting §3). Template-packs is the ONLY in-catalog
  PWYW listing ($19 suggested) and it is **not live** (⚑D click still
  queued).
- **Fee kernels (V037/V039/V040 lineage):** Gumroad direct 10% +
  $0.50/transaction + ~2.9% + $0.30 → net(p) = 0.871p − 0.80 (MARKET-PLAN
  §(a)); Discover flat 30% → 0.70p; Ko-fi free 5% + ~3% + $0.30 → 0.92p −
  0.30. Decision channel = Gumroad direct (the cookbook's own §7 default;
  "same account as the SWTK live listing").
- **Fee-floor rule reproduced exactly:** "Below ~$3 the fixed fees ($0.50 +
  ~$0.30) eat >25% of price — do not price under $3" (photo-packs §3) —
  crossing exactly $3.20; a zero-minimum PWYW admits payments below it, and
  a payment nets NEGATIVE below 800/871 ≈ $0.9185.
- **Demand reality:** "Conservative first-90-day: 0–3 sales ($0–$57). Zero
  distribution = $0" (INTAKE.md) — no projection is made anywhere.
- **Kill rule:** "within 30 days, ≥1 sale OR ≥30 reads from the
  agent-builder audience. Else ledgered negative" (INTAKE.md) — the
  $0-taker reads-leg is modeled as taker-count arithmetic, never revenue.
- **TAM/WTP:** "High-intent but small TAM (people building self-merging
  agent fleets)"; "Narrow but real pain; those who have it have few
  alternatives, so moderate WTP + some moat" (INTAKE.md scoring rows).

**Recorded gaps (G1–G6, registered before the runner):** G1 (CRITICAL) no
measured PWYW conversion, taker-rate, or mean-payment data exists anywhere
in the repo, and zero organic sales data exists for ANY product (the only
PWYW listing is not live; "unverified until first sale") — the exact mirror
of V039's G1 · G2 no absolute demand data · G3 processor rates are cited
approximations · G4 no Lemon Squeezy fee schedule in the packet (owner's
alternative storefront) · G5 the product is publish-ready but NOT live —
this verdict prices, it does not publish · G6 no reads/downloads telemetry
exists. **ASSUMED (A1–A5, flagged):** PWYW takers pay ≥ floor or $0 with
fees only on paid transactions · processor rate fixed at cited values
(±0.6pp bracket ships) · grid spans are registered bands, not measurements
(w̄ capped at $29 = the catalog's next rung, SWTK live) ·
downloads-as-reads is the seat's call, not asserted · mechanism-neutral
traffic (any PWYW entry-rate lift IS the unmeasured u — no double-count).

## What the sim MODELS (per committed baseline buyer — one $19-fixed cookbook buyer on the decision channel)

- **FIXED_19:** E[net] = net(19) = **$15.749 exact** (direct). Zero
  unmeasured parameters.
- **PWYW_MIN0** ($19 suggested, $0 minimum): E[net] = u·net(w̄) — u = paid
  PWYW transactions per baseline buyer, w̄ = mean paid amount, z = $0-taker
  share ($0 takes net exactly $0 and drop out of revenue; they feed only
  the reads-leg reporting). The linearity step is exact for any payment mix
  with mean w̄. All three unmeasured (G1).
- **PWYW_MIN3 / PWYW_MIN5:** same form with the listing floor enforcing
  w̄ ≥ m (m = 3 is the smallest floor honoring the packet's own fee-floor
  rule).
- **PWYW_MIN19** (= $19 fixed + voluntary overpay): net per paid sale ≥
  net(19) for every payment by construction — weakly dominant PER PAID
  SALE; its entire risk is conversion-side (u < 1 if the "minimum $19"
  framing deters), u unmeasured (G1). The mirror of V039's parked
  PWYW-with-$5-floor.

## MEASURED (exact, zero sampling error; decision channel = Gumroad direct, the cookbook's §7 default)

- **Per-sale nets at $19:** direct **15749/1000 = $15.749** · Ko-fi 859/50
  = $17.18 · Discover 133/10 = $13.30. Committed conservative band (0–3
  sales / 90 days): gross $0/$19/$38/$57 → net **$0 / $15.749 / $31.498 /
  $47.247** direct.
- **THE PWYW FRONTIER:** PWYW ≥ FIXED_19 ⇔ **u·net(w̄) ≥ 15.749** (paying
  takers only; z drops out of revenue entirely). **Kernel-invariance
  theorem, proven per channel:** at taker parity u = 1 the flip needs mean
  voluntary payment **w̄ ≥ $19.00 EXACTLY — on every affine kernel**
  (direct, Ko-fi, Discover, and any future channel): the same kernel sits
  on both sides, so all channel dependence collapses into the
  per-transaction fixed-fee drag. PWYW wins only via u > 1 outrunning the
  sub-$19 payment mix and that drag.
- **u_min landmarks (direct), u_min(w̄) = 15749/(871w̄ − 800):** w̄ = $15 →
  **u ≥ 15749/12265 ≈ 1.2841**; w̄ = $10 → **u ≥ 15749/7910 ≈ 1.9910**
  (Ko-fi 859/445 ≈ 1.9303, Discover 19/10 = 1.9 exactly); w̄ = $5 → u ≥
  15749/3555 ≈ **4.4301** (above the registered u-band); w̄ = $3 → u ≥
  15749/1813 ≈ **8.6867** (PWYW averaging the $3 floor needs ~8.7× taker
  volume); w̄ = $29 → u ≥ 15749/24459 ≈ 0.6439.
- **Within the registered u ≤ 3 band, no mean payment below 18149/2613 ≈
  $6.9457 can win at all** — which is why the m = 0/3/5 floor variants have
  IDENTICAL win regions on the grid (803/1829 cells each, direct): the
  sub-$7 territory the floors fence off is territory PWYW had already lost.
  FIXED_19 wins 1,026/1,829 cells; the m = 19 variant wins 473/651 of its
  cells (it loses exactly the u < 1 cells — conversion risk made visible).
- **THE SPLIT-TRANSACTION FEE DRAG (the mechanism, exact):** k paid takers
  gross-splitting one $19 net 16.549 − 0.80k: k=1 **$15.749** · k=2
  $14.949 · k=3 $14.149 · k=4 $13.349 · k=5 $12.549 — every extra paid
  transaction costs exactly **$0.80**. Gross-equal PWYW volume is strictly
  worse than one fixed sale.
- **Fee-floor arithmetic (packet's rule, reproduced):** fixed-fee share
  4/15 ≈ 26.7% at $3 · 16% at $5 · 4/95 ≈ 4.2% at $19; the 25% crossing is
  exactly $3.20; a zero-minimum PWYW payment nets negative below 800/871 ≈
  $0.9185 — the m = 3 floor honors the packet's own rule by construction.
- **Reads-leg bars (reporting-only, A4/G6):** $0-takers cost nothing and
  earn nothing but may serve the kill rule's ≥30-reads leg: downloads per
  baseline buyer = u/(1−z); reaching 30 downloads in the 30-day window from
  the band's full 3 baseline buyers needs **u/(1−z) ≥ 10** (at u = 1: z ≥
  0.9 — a 10× download multiplier); from 1 buyer, u/(1−z) ≥ 30. The
  "PWYW's free takers save the kill clock" story is therefore ALSO an
  unmeasured audience-scale claim, now with exact bars.
- **Processing-rate bracket (reporting-only, cannot flip):** net(19) at
  2.3%/2.9%/3.5% = $15.863/$15.749/$15.635 — and by kernel-invariance the
  u = 1 parity bar stays $19.00 at every rate.

## RULING (pre-registered rule, evaluated in order): **R3-CONDITIONAL-DEFAULT**

- R1 MEASURED-PWYW-WINS requires a MEASURED (û, ŵ̄) clearing the frontier —
  **cannot fire**: no PWYW conversion, taker-rate, or mean-payment
  measurement exists anywhere in the repo, and no product has any organic
  sales data (G1; the only PWYW listing, template-packs, is not live).
- R2 FULL-BAND-DOMINANCE — **does not fire, proven by count**: PWYW wins
  803/1,829 registered cells and FIXED_19 wins 1,026/1,829 — neither arm
  dominates the band (PWYW_MIN19 dominates per PAID SALE but its u is free
  on [0, 3], so it cannot dominate per baseline buyer).
- **R3 fires** (G1 open, no dominance): **keep the committed $19 one-time
  fixed** (net $15.749/sale exact — the only arm with zero unmeasured
  parameters, committed at intake + vetting §3 + the precedent chain, and
  holding the catalog's $19 rung shared with template-packs). **PWYW (any
  sub-$19 floor) parks** behind the measured frontier u·net(w̄) ≥ 15.749
  with its landmark bars (w̄ ≥ $19.00 exactly at u = 1; u ≥ 1.99 at w̄ =
  $10; u ≥ 1.28 at w̄ = $15). **PWYW_MIN19 ships as the one variant that
  cannot lose per paid sale**, parked on its conversion-side risk (G1) —
  named, not recommended.

## The 8-question battery (idea-engine README.md "probe battery v0", per ORDER 006)

1. **What is this really?** A two-mechanism expected-net comparison fully
   determined by the packet's own fee schedules except for buyer behavior
   the packet itself says has never been measured. The affine fee kernel
   does the deciding: at taker parity PWYW must average EXACTLY the fixed
   price on every channel, and every extra paid transaction is taxed $0.80
   — so PWYW's only winning story is unmeasured volume (u > 1), which is
   precisely the narrow-TAM axis the intake scores low (Distribution 3/5,
   "small TAM").
2. **What is the possibility space?** Arms: $19 fixed; PWYW min $0/$3/$5/
   $19 — plus re-priceable-from-the-same-kernel hybrids: PWYW on Ko-fi
   (u_min at w̄=$10 drops to 1.9303), a $15 fixed down-rung or $29 up-rung
   (each is one fixture swap; the chain pins both neighbors), launch-window
   PWYW then fixed (decidable by the same frontier on the window's
   measured pair).
3. **Most advanced capability from the simplest implementation?** The
   kernel-invariance theorem: one measured (u, w̄) pair from ANY PWYW
   listing on ANY channel re-prices EVERY product in the catalog by
   arithmetic — PWYW measurement is a catalog-level asset, not a
   per-product cost. The designated instrument already exists in the queue:
   the template-packs $19 PWYW listing (same audience, same rung).
4. **What breaks it?** A measured pair clearing u·net(w̄) ≥ 15.749 (R1
   flips it by lookup); evidence that the PWYW mechanism itself changes
   listing traffic beyond u (A5); a storefront off the committed kernels —
   Lemon Squeezy has no fee schedule in the packet (G4); fee-schedule
   changes (all frontiers recompute, same kernel); treating $0 downloads
   as "reads" without the seat ratifying A4.
5. **What does it unlock?** The cookbook's §7 price row keeps its default
   with evidence instead of instinct; the ruling generalizes to every
   narrow-TAM cookbook the order's plural asks about (same kernel, same
   frontier form — only the committed price swaps); the reads-leg bars
   give the kill rule's second leg its first exact arithmetic.
6. **What does it depend on?** The pinned MARKET-PLAN fee schedules, the
   intake/vetting committed $19, the precedent chain, A1–A5 as flagged —
   and nothing else. The owner's §7 storefront pick selects which frontier
   column applies; the decision is stated on the default (direct).
7. **Which lane should build it?** None — nothing to build. The cookbook
   is publish-ready up to the owner gate (G5); venture-lab consumes this
   verdict via manager relay; the only "build" is the named measurement,
   which needs a live PWYW listing first (template-packs, already queued).
8. **Smallest shippable slice?** When the owner clicks: publish the
   cookbook at $19 fixed exactly as queued — zero new decisions, the price
   row already says $19. The PWYW question stays parked on its frontier
   until the template-packs listing (or any live PWYW period) produces the
   catalog's first measured (u, w̄) pair.

## VALIDITY GATE (what would invalidate this verdict)

- A **measured** PWYW pair (û, ŵ̄) with û·net(ŵ̄) ≥ 15.749 → PWYW wins by
  R1; the committed frontier converts the measurement by lookup, no re-run.
- **COMPARABLE TO LIVE?** The arms are priced on the packet's own cited fee
  schedules in one per-committed-buyer frame; the cross-mechanism asymmetry
  the frame cannot see (PWYW entry-rate effects) is exactly the unmeasured
  u the ruling refuses to invent — the frontier ships instead of a guess.
- **UNCORRUPTED?** 5,612 self-checks, 0 failed; every decision quantity is
  a closed-form Fraction; constants quoted verbatim with path@SHA into
  fixtures.json committed BEFORE the runner (git-trail ordered: cc58391
  precedes 98e4f89); twin evaluators agree on all 5,487 grid cells; the
  packet's own fee-floor rule and the V039 kernel pins reproduced exactly.
- **ROBUST?** Not knife-edge — the ruling turns on the packet's verbatim
  no-measurement state (G1), not on a margin; the parity bar is
  kernel-invariant so no fee imprecision can move it; the processing
  bracket moves no sign; the nearest judgment line (the $29 grid cap) is a
  registered band edge, and a wider band only grows the already-non-empty
  win regions — R2/R3 cannot flip on it.
- **REPRODUCIBLE?** One command, no flags, stdlib-only, hermetic (reads
  exactly one file); ZERO seeds drawn (high-water 20261280 untouched);
  stdout + results.json byte-identical across two full process runs by
  external diff (sha256 pinned below).
- **LIMITS?** Ranks price mechanisms per committed buyer — does not size
  demand or project sales (the intake's "0–3 sales ($0–$57) / Zero
  distribution = $0" stands verbatim); the reads-leg is taker arithmetic
  under A4, not a retention claim; the cookbook stays owner-gated (G5) —
  this verdict prices, it does not publish.

## DETERMINISM

`SELF-CHECKS: 5612 passed, 0 failed`, exit 0. All decision quantities exact
(Fractions); **zero seeds drawn** — fleet high-water 20261280 untouched.
stdout and results.json byte-identical across two full process runs by
external `diff` (both empty); sha256 stdout
`82b81adccd8967b3e704d1e7291e12dba8b7f2b7f25c6323de91d1389e07e8f4`,
results.json
`01236225249b98419627d57ba79c0ba31755f713456f3a14d2a50bcec57cbd65`.

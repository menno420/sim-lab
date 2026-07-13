# REPORT — Ultramarine serial pricing: per-episode $2.99 vs $4.99 single volume vs free-first-episode funnel (idea-engine ORDER 005 SIM-REQUEST 1, seat venture-lab)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 005 ·
> 2026-07-13T07:51:32Z. Packet read READ-ONLY at `menno420/venture-lab` @
> `58cdb145dd524e8289a72a0bfd3d63a66ad0101b`.
> Run: `python3 sims/verdict-037-venture-serial-pricing/serial_pricing_sim.py`

Binding spec, verbatim (ORDER 005 `do:`, SIM-REQUEST 1):

> (1) VENTURE SERIAL PRICING — venture-lab asks for a pricing verdict on its
> Ultramarine serial (per-episode ~$2.99 vs bundle vs free-first-episode
> funnel); packet: venture-lab control/outbox.md night batch 1 + venture-lab
> docs/publishing/vetting/; deliver a verdict with evidence per your
> 8-question battery.

The packet's own asked-for quantity, verbatim (serial-edition NOTES.md
§ Market position @ 58cdb14):

> SIM-REQUEST: serial vs single-volume pricing feasibility — model
> carry-through breakeven (what episode-2/3 continuation rate makes
> 3 × $2.99 beat 1 × $4.99 per browsing reader) before any publish decision.

## METHOD LABEL: `simulation` (exact-analytic)

Method ladder rung 1 — NUMERIC, but with ZERO RNG: every arm is a
closed-form expected-value expression evaluated in exact `Fraction`
arithmetic, so there is no sampling error anywhere and no seed is drawn
(the fleet seed high-water mark 20260775 is untouched). Sweep grids
(21×21 per arm pair) exist only to render the frontier as a WIN map and to
force twin-evaluator agreement (expected-value comparison vs frontier
inequality) on every cell — 934 self-checks, 0 failed, exit 0.

## PREMISE (verified at drafting, pinned into fixtures.json — hermeticity by construction)

The sim reads exactly ONE file (its committed `fixtures.json`) and touches
no repo state, network, or wall clock. Every constant is quoted verbatim
with source path@SHA (all @ venture-lab `58cdb14`):

- **Episodes:** 3 — 9,188 / 9,849 / 10,399 words, 29,436 total (`wc -w`,
  the packet's own count); base manuscript 27,865 words.
- **Serial price:** $2.99/episode — "the KDP 70%-royalty floor ($2.99–$9.99
  band per `docs/publishing/CHECKLIST.md` §4; ≈ $2.09/episode at 70% before
  delivery fee)".
- **Single volume ("bundle" arm):** vetted band $3.99–$5.99 → recommended
  $4.99 (≈ $3.49/sale), fallback $3.99 (vetting packet §4).
- **Royalty:** "KDP pays 70% only on ebooks priced $2.99–$9.99 (below/above
  → 35%, delivery fee applies on the 70% tier). A $0.99 impulse price means
  35%" (CHECKLIST.md §4, lines 58–60).
- **Packet arithmetic reconciled exactly:** full serial run grosses $8.97,
  nets $6.279 exact (the packet's ≈$6.27 rounds $2.09×3); the packet's
  "2–3× revenue" framing is **1.7977× exact on net** (6279/3493) — the sim
  decides on net.
- **Packet's own caveat, verbatim:** "serialization economics are
  unverified … carry-through rates that nobody has measured for this
  catalog … literary historical fiction is not a proven Kindle serial
  category … Kindle Vella, shut down in early 2025 … A $2.99 price on a
  ~9–10k-word episode also risks poor value perception … Unknown-author
  base case remains ≈ $0 either way; no sales projection is made."

**Recorded gaps (G1–G6, registered before the runner):** G1 no measured
ep2/ep3 carry-through anywhere in the packet · G2 no free→paid conversion
or acquisition-multiplier data · G3 no committed platform mechanism for a
permanently-$0.00 KDP listing (the packet's own platform pins stop at the
$0.99→35% tradeoff) · G4 no entry-rate data ($2.99-vs-$4.99 first-purchase
propensity) · G5 delivery fee magnitude unpinned ("text-only file is
small"; serial pays it 3×) · G6 KU page-read economics carry no committed
KENP rate (the vetting packet's own "realistic first revenue surface").

## What the sim MODELS (per committed browsing reader — the packet's frame)

- **SERIAL:** E[net] = r·(1 + p2 + p2·p3), r = 0.70·$2.99 = **$2.093 exact**.
- **SINGLE:** E[net] = s = 0.70·$4.99 = **$3.493 exact** — zero unmeasured
  parameters.
- **FREE_FUNNEL:** E[net] = m·r·(q2 + q2·q3) — ep1 free, m = free readers
  acquired per counterfactual committed buyer.

## MEASURED (exact, no sampling error)

- **The asked-for breakeven:** SERIAL ≥ SINGLE ⇔ **p2·(1+p3) ≥ 200/299 =
  0.668896**. Landmarks: p2 ≥ **33.4%** (100/299) if every ep2 buyer
  finishes (p3 = 1); p2 ≈ **45.9%** symmetric (p3 = p2); p2 ≥ **66.9%**
  (200/299) if ep3 never sells. WIN region: 235/441 grid cells — real but
  entirely dependent on the unmeasured G1 rates.
- **Full carry-through ceiling:** serial nets $6.279 vs $3.493 —
  **1.7977×**, the packet's best case, reachable only at p2 = p3 = 1.
- **Free-first-episode funnel:** FREE ≥ SINGLE ⇔ **m·q2·(1+q3) ≥ 499/299 =
  1.668896**. At m = 1 the win region is 16/441 cells and needs
  **q2 ≥ 83.4%** even with perfect ep3 carry (symmetric ≈ 88.5%) —
  implausible-tier conversion, and the $0.00 listing mechanism itself is
  unpinned (G3). Identity: at equal rates and m = 1, SERIAL − FREE = r
  **exactly** ($2.093, the paid-ep1 margin) — a free episode 1 can only win
  through the acquisition multiplier m (m* ≈ 3.34 at q = 50% symmetric,
  m* ≈ 1.19 at q = 75%; exact table in results.json), and m is unmeasured
  (G2).
- **Delivery-fee sensitivity (reporting-only, cannot flip):** any per-unit
  fee f raises the serial breakeven monotonically (serial pays f three
  times) — the decision was taken at f = 0, the direction FAVORABLE to
  serial, so the ruling is conservative against the fee gap (G5).

## RULING (pre-registered rule, evaluated in order): **R3-CONDITIONAL-DEFAULT**

- R1 SERIAL-WINS requires a MEASURED continuation pair clearing the
  frontier — **cannot fire**: the packet states verbatim that no
  carry-through rate has been measured (G1).
- R2 SINGLE-WINS-UNCONDITIONAL requires B > 2 — false (B = 0.6689; the
  serial CAN win in a real region).
- **R3 fires:** no measured continuation/conversion/multiplier datum exists
  and 0 < B ≤ 2 → recommend the only arm with **zero unmeasured
  parameters**: **publish the single volume at the vetted $4.99**
  (net $3.493/sale exact; band $3.99–$5.99, fallback $3.99 — the vetting
  packet §4 numbers stand). **Serial parks** behind one named measurement:
  observed carry-through p2·(1+p3) ≥ 200/299 (e.g. ≥ 45.9% symmetric).
  **Free-first-episode is not recommendable**: its win bar must clear BOTH
  an unmeasured behavioral bar (83.4%+ conversion at m = 1, or a measured
  m ≥ the m* table) AND an unpinned platform mechanism (G3).
- This is the pre-registered conditional branch, not a stretch: the
  frontier table IS the citable pin — any future measured (p2, p3) converts
  to a decision by table lookup, no re-run.

## The 8-question battery (idea-engine README.md "probe battery v0", per ORDER 005)

1. **What is this really?** A three-arm expected-net-royalty comparison over
   one fixed 29,436-word manuscript, fully determined by exact KDP royalty
   arithmetic except for reader-behavior rates the packet itself declares
   unmeasured. The pricing question is really a *measurement* question.
2. **What is the possibility space?** Arms: à-la-carte serial, single
   volume, free-ep1 funnel; unmodeled hybrids: publish BOTH (serial + the
   volume as its own omnibus; cannibalization unmeasured), KU-first
   strategy (G6), $3.99 fallback single (breakeven becomes p2·(1+p3) ≥
   0.3344 — computable from the same kernel).
3. **Most advanced capability from the simplest implementation?** The exact
   closed-form frontier: one Fraction inequality per arm pair. No MC, no
   seeds, zero sampling error — and it converts ANY future measured rate
   into an instant verdict.
4. **What breaks it?** A measured entry-rate asymmetry (G4: if $2.99 entry
   ≫ $4.99 entry, the per-committed-reader frame under-credits serial);
   a pinned permafree mechanism (G3) plus a measured m clearing m*;
   a real delivery fee large enough to matter (G5, direction already
   conservative); KU page-reads dominating à-la-carte sales (G6).
5. **What does it unlock?** The vetting packet's §7 owner price click gets
   a decision table instead of a guess; the same kernel re-prices every
   future serial candidate in the catalog (Slow Word, Weigh House novella
   cuts) by swapping three fixture numbers.
6. **What does it depend on?** The pinned KDP 70% band constants
   (CHECKLIST §4), the vetted $4.99 single-volume recommendation, and the
   G1/G2 measurements it names — nothing else; the owner's D3 retitle
   decision (Widow's Blue vs Ultramarine) is orthogonal to pricing.
7. **Which lane should build it?** None — there is nothing to build.
   Publishing is owner-gated (vetting packet §7); venture-lab consumes this
   verdict via manager relay; the only "build" is the named measurement,
   which requires a live listing first.
8. **Smallest shippable slice?** Publish the single volume at $4.99 (already
   publish-ready up to the owner gate per the vetting packet's own verdict
   line); the serial edition stays committed and ready, re-decidable by
   table lookup the day carry-through data exists.

## VALIDITY GATE (what would invalidate this verdict)

- A **measured** episode-2/3 carry-through pair clearing p2·(1+p3) ≥
  200/299 → serial wins by R1; this verdict's default flips by its own
  table.
- A **pinned** $0.00-listing mechanism PLUS measured funnel data clearing
  m·q2·(1+q3) ≥ 499/299 → the funnel arm re-enters.
- Entry-rate data showing materially higher first-purchase propensity at
  $2.99 → the per-committed-reader frame under-credits serial; re-run with
  an entry multiplier arm.
- A single-volume price outside the pinned $3.99–$5.99 band, or a royalty
  regime change off the pinned 70%/$2.99–$9.99 constants → all frontiers
  recompute (same kernel, new fixtures).
- KU page-read revenue measured to dominate à-la-carte revenue for this
  catalog → the à-la-carte ruling scope (G6) no longer covers the real
  decision.
- LIMITS: no sales projection is made (the packet's "unknown-author base
  case ≈ $0" stands); the ruling ranks arms per committed reader, it does
  not size the market; cannibalization between simultaneously-published
  serial and volume is out of scope.

## DETERMINISM

`SELF-CHECKS: 934 passed, 0 failed`, exit 0. ZERO RNG. stdout and
results.json byte-identical across two full process runs by external
`diff` (empty); sha256 results.json `f6e3abba8fccd0512428c53eef6e25793b…`,
stdout `27838b1e0ab1f15a46a428c37d7afc87…`.

# REPORT — Ship-It Bundle pricing: $59 vs $64 vs $68 anchor points (idea-engine ORDER 006 SIM-REQUEST 2, seat venture-lab)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 006 · 2026-07-13T09:02Z.
> Packet read READ-ONLY at `menno420/venture-lab` @
> `6ecc46040ff20c418bd2b65c66a7b8d29c786a7c`.
> Run: `python3 sims/verdict-040-shipit-bundle-pricing/bundle_pricing_sim.py`

Binding spec, verbatim (ORDER 006 `do:`, SIM-REQUEST 2):

> (2) SHIP-IT BUNDLE — $59 vs $64/$68 anchor points;

with the ORDER's packet pointer for the venture-pricing triplet, verbatim:

> VENTURE PRICING (3 — packet: venture-lab control/outbox.md "night-run
> MORNING TALLY" ~05:00Z; listings/gates in venture-lab
> docs/publishing/OWNER-QUEUE.md)

The packet's SIM-REQUEST line, verbatim (MORNING TALLY @ 6ecc460):

> SIM-REQUEST: photo packs PWYW-vs-$5 + $3 anchor + two-pack bundle ·
> bundle $59 vs $64/$68 anchors · $19 fixed vs PWYW for narrow-TAM
> cookbooks · owner sandbox repo to production-verify merge-on-green.yml.

Evidence delivered per the idea-engine 8-question probe battery
(idea-engine README.md § "The probe battery (v0 — the core method)" @
8218d66, inherited from ORDER 005's "deliver a verdict with evidence per
your 8-question battery" clause) — all 8 probes committed in
`results.json` → `probe_battery_v0`, one probe per question, each grounded
in a packet constant or explicitly marked NOT MEASURED.

## METHOD LABEL: `simulation` (exact-analytic + one validation-only seeded leg)

Method ladder rung 1 — every decision quantity is a closed-form
`fractions.Fraction` expected value on the pinned constants, so there is no
sampling error in any decision path. Sweep grids (101-point retention grid ×
3 anchor pairs) render the frontiers as WIN maps and force twin-evaluator
agreement (Fraction product comparison vs integer cross-multiplication
frontier inequality) on every cell. ONE registered seed **20260880**
(strictly above the visible fleet high-water 20260775, +105 buffer clearing
the in-flight V038/V039 sibling reservations) drives a VALIDATION-ONLY leg:
30,000 uniform retention draws, twin evaluators must agree on every draw and
the empirical win share must sit within 4σ of the exact frontier share — it
cannot flip the decision. 46 self-checks, 0 failed, exit 0.

## PREMISE (verified at drafting, pinned into fixtures.json — hermeticity by construction)

The sim reads exactly ONE file (its committed `fixtures.json`) and touches
no repo state, network, or wall clock. Every constant is quoted verbatim
with source path@SHA (all @ venture-lab `6ecc460`):

- **Components:** Membership-Site Boilerplate Kit **$49** + Agent-Workflow
  Template Pack **$19 PWYW-suggested** → separate total **$68**
  (`candidates/BUNDLE-LISTING.md` § Pricing).
- **Committed bundle price:** **"$59 one-time fixed; $68-separate comparison
  cited in the copy"** (`docs/publishing/OWNER-QUEUE.md` Ship-It Bundle
  click-run; same constant in `bundle-starter.md` §3/§7).
- **Committed copy claims:** "it saves $9 and one checkout"
  (BUNDLE-LISTING FAQ); "$9 off as 'a modest, honest nudge,' not a
  manufactured discount anchor" (bundle-starter §3).
- **Coherence floor:** the bundle must not undercut the $49 kit alone
  (bundle-starter §3, the packet's own rule).
- **Gumroad direct fees (the packet's one committed schedule):** "flat 10%
  platform fee + $0.50 per transaction … payment processing (~2.9% + $0.30)
  … roughly ~12.9% + $0.80 per sale"
  (`candidates/photo-packs/MARKET-PLAN.md`, cited by photo-packs vetting
  §3) → net(P) = 0.871·P − 0.80.
- **Demand data:** NONE — "Honest null: no evidence exists on
  bundle-vs-separate conversion for this catalog (zero sales history on the
  components themselves)"; "Conservative expectation (Q-0259.4): 0–2
  sales/month absent distribution" (bundle-starter §3, verbatim).
- **Hard gate:** "HARD-GATED: blocked until the ⚑B and ⚑D component publish
  clicks are executed. NO ungated bundle click is queued" (bundle-starter
  header) — the pricing verdict is serveable now; publishing stays
  owner-gated (gap G5).
- **The $64 anchor has NO packet source** — it appears only in the
  SIM-REQUEST lines themselves; as a displayed "bought separately"
  comparison it would be arithmetically false ($49+$19=$68); as a charged
  price it is modeled here (gap G3).

Gaps G1–G6 registered in fixtures.json; nothing not in the packet was
invented — every unmeasured quantity is reported as a frontier (bar), never
an estimate.

## RESULTS (exact)

Per-sale nets under the cited fee schedule (Fraction-exact):

| anchor | gross | net/sale | buyer saves vs $68-separate | committed "saves $9" copy |
|---|---|---|---|---|
| **$59** (committed) | 59 | **$50.589** | $9 | TRUE |
| **$64** (unsourced) | 64 | **$54.944** | $4 | FALSE |
| **$68** (= separate total) | 68 | **$58.428** | $0 | FALSE — rationale void |

Reference rows: both-separate (suggested $19 paid) nets **$57.628** (two
transactions — the $68 bundle nets exactly **+$0.80** more, one fixed fee
saved); kit-alone nets **$41.879** (a $59 bundle buyer is worth **+$8.710**
net over a kit-alone buyer — the G6 cannibalization ladder).

**Retention frontiers** (the asked-for decision quantity — what a future
measurement must clear; higher anchor wins iff retention r ≥ net(lo)/net(hi)):

- $64 beats $59 iff **r ≥ 50589/54944 ≈ 0.9207** (retain ≥ 92.07% of $59's
  buyers) — equivalently $59 needs +8.61% more buyers to beat $64.
- $68 beats $59 iff **r ≥ 5621/6492 ≈ 0.8658** — $59 needs +15.50% more.
- $68 beats $64 iff **r ≥ 13736/14607 ≈ 0.9404**.
- Fee-sensitivity (gap G4, reporting-only): fee-free bounds 59/64 =
  0.921875 · 59/68 ≈ 0.867647 · 16/17 ≈ 0.941176 — each within **0.19 pp**
  of its cited-fee frontier; any affine fee aP+b (a < 1) preserves
  net-ordering, so fee imprecision cannot flip anything.
- **Materiality bound** at the packet's own 0–2 sales/month: choosing $59
  over $68 costs at most **$15.678/month** net; over $64 at most
  **$8.710/month**. The wrong-anchor risk is capped and small.

**Seller cost of the committed $9 nudge:** exactly **$7.039** net per
both-buyer (0.871·9 minus the $0.80 saved second-transaction fee).

## RULING — R3-CONDITIONAL-DEFAULT (pre-registered order): recommend **$59**

- **R1 MEASURED-DEMAND: cannot fire** — the packet states verbatim that zero
  sales history exists for the bundle or either component (G1).
- **R2 DOMINANCE SCREEN: false** — net is strictly increasing in price while
  retention is free on [0,1]; no anchor dominates (checked at both ends).
- **R3 FIRES** — with zero measured demand, the default is the only anchor
  with zero unmeasured parameters AND committed packet support: **$59**
  (committed listing copy, queued click, vetted §3). Charging $64 or $68
  instead requires an unmeasured retention rate ≥ its frontier AND
  falsifies the committed "saves $9 and one checkout" copy without a
  committed replacement; $64 additionally has zero packet provenance (G3);
  $68 voids the bundle's entire stated rationale (buyer discount $0).
- $64/$68 **PARK** behind the named measurement: any future measured
  retention pair decides by frontier lookup — no re-run.

## VALIDITY GATE

**PASS** — inputs were REAL packet constants: every number in the decision
path is quoted verbatim with path@SHA from venture-lab @ `6ecc460` into the
pre-registered fixtures.json (committed before the runner; git-trail
ordered); nothing was invented — the three quantities the packet does not
carry (demand/retention G1, PWYW minimum G2, exact processing fee G4) enter
only as frontiers/bounds explicitly marked NOT MEASURED.

- COMPARABLE: all three anchors priced in the packet's own frame (committed
  both-products buyer) under the packet's own fee schedule; the one hidden
  asymmetry (PWYW minimum, G2) is disclosed with direction.
- UNCORRUPTED: 46 self-checks 0 failed; every decision quantity
  exact-Fraction closed form; twin evaluators agree on all 303 grid cells
  and all 30,000 seeded draws; hand-derived pins reproduced. ONE
  pre-registration correction, disclosed: a reporting-only sensitivity pin
  (fee-free-vs-cited frontier gap) said 0.13 pp, the runner's own self-check
  caught the slip (actual max gap 0.18 pp on the 68v59 pair), corrected to
  0.19 pp post-first-run with the git trail as the record — no decision
  band, frontier, net, or rule was touched.
- ROBUST: the ruling turns on the packet's own verbatim "zero sales
  history" statement, not on a margin; frontiers are monotone in every
  unpinned nuisance; fee imprecision bounded at < 0.19 pp on the frontier.
- REPRODUCIBLE: one command, no flags, stdlib-only, hermetic; stdout +
  results.json byte-identical across two full process runs by external diff
  — sha256 results `efd027e9ae1886e6921ec050ae2279d1eea6396d0682e6609f22efa7945d5c28`,
  stdout `d14f5215b9daf160ea1312c69aa8dcbfde01cd28eb861e27b0cb8ee5a5b9d07a`;
  seed 20260880 registered (validation leg only).
- LIMITS: ranks anchors per committed buyer — does not size the market or
  project sales (the packet's "0–2 sales/month" stands); the
  bundle-vs-component cannibalization counterfactual is unmeasured (G6,
  ladder shipped); the displayed-anchor reading of "$64/$68" is settled by
  the packet itself ($68-separate is already committed in copy; a displayed
  $64 would be arithmetically false and violates the packet's committed
  anti-fake-anchor stance); publish timing stays owner-gated (G5).

## SEEDS

`20260880` — validation-only leg (30,000 uniform retention draws; twin
evaluator agreement + 4σ frontier-share check). Strictly above the visible
fleet high-water `20260775` (V037 fixtures registry line) with a +105 buffer
for the in-flight V038/V039 sibling reservations. New visible high-water:
**20260880**.

## PACKET PINS

- `menno420/idea-engine` @ `8218d6630f53633461d993d9a3caa4ad54ab251d`
  (ORDER 006 binding text + the probe-battery spec in README.md).
- `menno420/venture-lab` @ `6ecc46040ff20c418bd2b65c66a7b8d29c786a7c`
  (READ-ONLY blob-filtered clone): `control/outbox.md` MORNING TALLY +
  NIGHT REPORT · `docs/publishing/OWNER-QUEUE.md` ·
  `docs/publishing/vetting/bundle-starter.md` ·
  `candidates/BUNDLE-LISTING.md` · `candidates/photo-packs/MARKET-PLAN.md`.
  (The sibling V037 read the packet at `58cdb14`; main had advanced to
  `6ecc460` at this slice's read — all bundle constants identical at both.)

# Session — VERDICT 040 — Ship-It Bundle pricing: $59 vs $64 vs $68 anchor points for the Membership Kit + Template Pack Gumroad bundle (idea-engine ORDER 006 SIM-REQUEST 2, requesting seat venture-lab)

> **Status:** complete
> 📊 Model: fable (Claude Fable 5 family) · 2026-07-13 · verdict-040 slice-worker session
> Objective: serve SIM-REQUEST 2 of idea-engine `control/inbox.md` ORDER 006 @ 8218d66 — "(2) SHIP-IT BUNDLE — $59 vs $64/$68 anchor points;" (packet: venture-lab control/outbox.md "night-run MORNING TALLY" ~05:00Z; listings/gates in venture-lab docs/publishing/OWNER-QUEUE.md; evidence per the idea-engine 8-question probe battery, README.md § "The probe battery (v0 — the core method)", per the ORDER 005 battery clause the ORDER 006 items inherit). Packet read read-only at venture-lab @ 6ecc46040ff20c418bd2b65c66a7b8d29c786a7c (blob-filtered clone; the sibling V037 pin 58cdb14 superseded at this read). Build a fully hermetic pre-registered exact-analytic pricing sim (rung 1 — exact Fraction arms; ONE registered seed 20260880 for a reporting/validation-only frontier-agreement leg, strictly above the visible fleet high-water 20260775 with a +105 buffer for the in-flight V038/V039 sibling reservations) in `sims/verdict-040-shipit-bundle-pricing/`: fixtures.json (constants quoted verbatim with source path@SHA + decision bands + decision rule mapping outcomes → {recommend $59 | $64 | $68 | NULL}) committed BEFORE the runner; exact net-per-sale under the packet's cited Gumroad fee schedule at each anchor; exact retention-breakeven frontiers between anchors; twin evaluators; byte-identical double run proven by external diff. Land INTAKE simreq-004 + VERDICT 040 in `control/outbox.md` (append-only; VERDICTs 038/039 were RESERVED by in-flight sibling slices serving ORDER 005 item 2 and ORDER 006 item 1 — both landed mid-slice and origin/main was merged INTO this branch, tail re-verified at ed2abe2 immediately before the append). Worker session — no control/status.md or control/inbox.md writes anywhere; venture-lab and idea-engine untouched.

## What happened

Built `sims/verdict-040-shipit-bundle-pricing/` — an exact-analytic pricing
sim (rung 1: every decision quantity a closed-form Fraction; the one
registered seed 20260880 drives a validation-only twin-evaluator agreement
leg that cannot flip the decision). Pre-registration `fixtures.json`
(constants verbatim with venture-lab path@SHA pins @ 6ecc460, decision
bands, rule R1–R4 mapping outcomes → {recommend $59 | $64 | $68 | NULL},
gaps G1–G6, seed) committed BEFORE the runner (git trail: b0a2743 precedes
8f40e19). Packet read read-only from a blob-filtered clone of
menno420/venture-lab @ 6ecc46040ff20c418bd2b65c66a7b8d29c786a7c;
venture-lab and idea-engine untouched.

**Run output:** `SELF-CHECKS: 46 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 results `efd027e9…`, stdout `d14f5215…`). Twin evaluators (Fraction
product comparison vs integer cross-multiplication frontier inequality)
agreed on all 303 grid cells and all 30,000 seeded validation draws;
hand-derived exact pins (nets 50.589/54.944/58.428, frontiers 50589/54944,
5621/6492, 13736/14607, the +$0.80 saved-fee identity) all reproduced. ONE
pre-registration correction, disclosed in fixtures + report: a
reporting-only sensitivity pin (fee-free-vs-cited frontier gap) said
0.13 pp; the runner's own self-check caught the arithmetic slip (actual max
0.18 pp on the 68v59 pair) and it was corrected to 0.19 pp post-first-run —
no decision band, frontier, net, or rule touched.

**Ruling: R3-CONDITIONAL-DEFAULT — recommend the committed $59** (registered
order): R1 measured-demand cannot fire — the packet states verbatim "no
evidence exists on bundle-vs-separate conversion for this catalog (zero
sales history on the components themselves)"; R2 dominance-screen false —
net strictly increasing in price, retention free on [0,1]; R3 fires — $59
is the only anchor with zero unmeasured parameters AND committed packet
support (BUNDLE-LISTING § Pricing, OWNER-QUEUE click row, bundle-starter
§3/§7), and the only one under which the committed "saves $9 and one
checkout" copy stays true. $64 parks behind measured retention ≥
50589/54944 ≈ 0.9207 (and carries ZERO packet provenance — it exists only
in the SIM-REQUEST line; a displayed $64 comparison would be arithmetically
false since $49+$19=$68); $68 parks behind ≥ 5621/6492 ≈ 0.8658 and voids
the bundle's committed rationale (buyer discount $0). Materiality bound at
the packet's own 0–2 sales/month: the conservative choice costs at most
$15.678/month net. No number invented anywhere; the frontier table is the
citable pin (future measured retention decides by lookup, no re-run).

Landed: INTAKE simreq-004 (2026-07-13T10:22:13Z) + VERDICT 040
(2026-07-13T10:22:14Z) appended to `control/outbox.md` (append-only, 20
insertions 0 deletions; VERDICTs 038 @ ed2abe2 and 039 @ 8bc5637 landed
mid-slice and origin/main was merged INTO this branch — never rebased —
with the tail re-verified immediately before the append; numbers preserved,
no renumber). Worker session — no control/status.md or control/inbox.md
writes in any repo; this card flip is the last commit.

## 💡 Session idea

When a requester's own ask introduces a constant with no provenance (the
$64 here — present in the SIM-REQUEST line, absent from every packet
document), treat provenance itself as a measured finding: pin the absence
with the search that established it, model the constant anyway in the frame
where it is coherent (charged price), and let the ruling separate the two
readings (a charged $64 is parkable; a displayed $64 is arithmetically
false and violates the packet's own anti-fake-anchor stance). The payoff:
the verdict answers the question as asked without laundering an unsourced
number into the packet's constant set.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-037-venture-serial-pricing.md`: complete and
honest; exports adopted. (1) Its zero-unmeasured-parameters default rule
(💡: "for revenue-arm comparisons, always report which arms need zero
unmeasured parameters; that set is the only honest default under total data
absence") applied directly as this head's R3 — the committed $59 is exactly
that arm. (2) Its race protocol (re-verify the ledger tail at origin/main
HEAD immediately before the append; merge, never rebase) held again — this
time absorbing TWO mid-slice sibling landings (V038, V039) with reserved
numbers, zero renumbering. (3) One deviation from its clean pre-registration
record: this head shipped a disclosed post-registration correction to a
reporting-only pin, caught by the sim's own self-check — the honest-fix
path (correct + disclose + git trail) beat the alternative of leaving a
known-false pin in the registration.

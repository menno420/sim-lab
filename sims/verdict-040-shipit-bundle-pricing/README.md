# verdict-040 · shipit-bundle-pricing

Serves **idea-engine ORDER 006 SIM-REQUEST 2** (control/inbox.md @ 8218d66;
requesting seat **venture-lab**): "(2) SHIP-IT BUNDLE — $59 vs $64/$68
anchor points;". Packet read READ-ONLY at menno420/venture-lab @
`6ecc46040ff20c418bd2b65c66a7b8d29c786a7c` (`control/outbox.md` "night-run
MORNING TALLY" + `docs/publishing/OWNER-QUEUE.md` +
`docs/publishing/vetting/bundle-starter.md` + `candidates/BUNDLE-LISTING.md`
+ `candidates/photo-packs/MARKET-PLAN.md` fee schedule).

Fully hermetic: every constant is quoted verbatim with its source path@SHA in
the committed `fixtures.json` (the pre-registration — decision bands and the
decision rule landed BEFORE the runner existed; git trail: fixtures commit
precedes the runner commit). The sim reads exactly ONE file (its own
fixtures.json) and touches no repo state, network, or wall clock.

Model (exact, per committed both-products buyer — the packet's own frame:
"The bundle is only for people who want both"), Gumroad direct fees as cited
(net(P) = 0.871·P − 0.80):

- **A59** — charge the committed $59: net **$50.589** exact. Zero unmeasured
  parameters; the click is already queued at it.
- **A64** — charge $64 (the SIM-REQUEST's middle anchor — NO packet source
  anywhere, gap G3): net **$54.944** exact.
- **A68** — charge $68 (the separate-total; buyer discount $0): net
  **$58.428** exact. Nets exactly +$0.80 over both-separate (one fixed fee).

Retention frontiers (a higher anchor wins iff it retains ≥ net(lo)/net(hi)
of the lower anchor's buyers): **$64 beats $59 iff retention ≥ 50589/54944 ≈
0.9207 · $68 beats $59 iff ≥ 5621/6492 ≈ 0.8658 · $68 beats $64 iff ≥
13736/14607 ≈ 0.9404**. The packet has ZERO demand data (its own verbatim
honest null), so the frontiers are bars, not estimates.

**Ruling: R3-CONDITIONAL-DEFAULT — recommend the committed $59.** $64/$68
park behind the measured-retention frontiers (decision-by-lookup). 46
self-checks, 0 failed; stdout + results.json byte-identical across two
process runs; one registered seed 20260880 (validation-only leg).

Run: `python3 sims/verdict-040-shipit-bundle-pricing/bundle_pricing_sim.py`

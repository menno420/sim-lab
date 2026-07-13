# verdict-039 · photo-packs-pricing

Serves **idea-engine ORDER 006 SIM-REQUEST 1** (control/inbox.md @ 8218d66;
requesting seat **venture-lab**): a pricing verdict on the photo packs
(Dutch Skies + Golden Hours) — PWYW vs $5 fixed, a $3 anchor, and a
two-pack bundle. The packs themselves are hard-gated on owner-held
originals; per the order text the pricing verdict is serveable now. Packet
read READ-ONLY at menno420/venture-lab @
`847b636f174d439949afeffac55025dde814514b` (`control/outbox.md` "night-run
MORNING TALLY" + `docs/publishing/OWNER-QUEUE.md` D6/D7 +
`docs/publishing/vetting/photo-packs.md` §3/§7 +
`candidates/photo-packs/MARKET-PLAN.md` §(a) fee schedules).

Fully hermetic: every constant is quoted verbatim with its source path@SHA
in the committed `fixtures.json` (the pre-registration — arms, decision
bands, decision rule, and seeds landed BEFORE the runner existed; git
trail: fixtures commit precedes the runner commit). The sim reads exactly
ONE file (its own fixtures.json) and touches no repo state, network, or
wall clock.

Model (per committed baseline buyer — one $5 single-pack buyer on the
picked channel; decision channel = Gumroad direct, the packet's D6 default,
net(p) = 0.871p − 0.80):

- **FIXED_5** — the packet default: E[net] = $3.555 exact. Zero unmeasured
  parameters.
- **PWYW** — E[net] = u·net(w̄); u = paid takes per baseline buyer, w̄ =
  mean paid amount, both unmeasured (G1).
- **ANCHOR_3** — E[net] = ρ·net(3); ρ = unit-sales ratio at $3 vs $5,
  unmeasured (G2). Bar: **ρ ≥ 3555/1813 ≈ 1.9608** (+96.1% units to tie).
- **BUNDLE_2PACK** — add a bundle at price b; dominance band **b ≥
  7910/871 ≈ $9.0815** (net(b) ≥ two singles even at full cannibalization;
  at $10 the gain is the saved second fixed fee, +$0.80 exactly).

**Ruling: R3-CONDITIONAL-DEFAULT** per the pre-registered rule — no
measured conversion/elasticity/mix datum exists in the packet (its own §3
says "No cited evidence either way"), so: keep **$5 fixed per pack** (D7
unchanged) and **add the two-pack bundle at $9.99** (in-band, net $7.90129
exact, +$0.79129 vs two singles); the $3 anchor and PWYW park behind named
measurements (frontier tables committed); bundle prices below $9.09 park
behind the measured mix frontier.

## Run (one command)

```
python3 sims/verdict-039-photo-packs-pricing/photo_packs_pricing_sim.py
```

Exit 0 iff all self-checks pass (4,761 passed, 0 failed). Deterministic —
decision arms are exact Fraction closed forms; seeds **20260790/20260791**
(registered strictly above the fleet high-water 20260775, +14 gap left for
the in-flight sibling slices V036/V038) drive sign-agreement gate legs
only; stdout + results.json byte-identical across runs by external diff.

Files: `fixtures.json` (pre-registration) · `photo_packs_pricing_sim.py`
(runner) · `results.json` (committed output) · `REPORT.md` (verdict
evidence — the 8-question battery + validity gate).

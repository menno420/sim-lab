# Session — VERDICT 039 — Photo-packs pricing: PWYW vs $5 fixed, a $3 anchor, and a two-pack bundle (idea-engine ORDER 006 SIM-REQUEST 1, requesting seat venture-lab)

> **Status:** complete
> 📊 Model: fable (Claude Fable 5 family) · 2026-07-13 · verdict-039 slice-worker session
> Objective: serve SIM-REQUEST 1 of idea-engine `control/inbox.md` ORDER 006 @ 8218d66 — "(1) PHOTO PACKS — PWYW-vs-$5, a $3 anchor, and a two-pack bundle (the packs themselves are hard-gated on owner-held originals; the pricing verdict is serveable now);" Packet read read-only at venture-lab @ 847b636f174d439949afeffac55025dde814514b (blob-filtered clone): control/outbox.md "night-run MORNING TALLY" + docs/publishing/OWNER-QUEUE.md D6/D7 + docs/publishing/vetting/photo-packs.md §3/§7 + candidates/photo-packs/MARKET-PLAN.md (a) fee schedules. Build a fully hermetic pre-registered pricing sim (rung 1 — exact Fraction decision arms; a small seeded robustness leg, seeds strictly above the fleet high-water 20260775) in `sims/verdict-039-photo-packs-pricing/`: fixtures.json (constants quoted verbatim with source path@SHA + decision bands + decision rule + seeds) committed BEFORE the runner; four arms (PWYW, FIXED_5, ANCHOR_3, BUNDLE_2PACK) on the packet's cited Gumroad/Ko-fi/Discover fee arithmetic; exact breakeven frontiers; twin evaluators; byte-identical double run proven by external diff. Land INTAKE simreq-003 + VERDICT 039 in `control/outbox.md` (append-only; VERDICT 036 and VERDICT 038 are RESERVED for in-flight sibling slices — tail re-verified at origin/main HEAD immediately before the append). Worker session — no control/status.md or control/inbox.md writes anywhere; venture-lab and idea-engine untouched.

## What happened

Built `sims/verdict-039-photo-packs-pricing/` — an exact-analytic pricing
sim (rung 1: every decision quantity a closed-form Fraction, zero sampling
error; the only RNG is two sign-agreement gate legs on seeds
20260790/20260791, registered strictly above the recorded fleet high-water
20260775 with a deliberate +14 gap for the in-flight siblings — V036 landed
mid-slice having drawn exactly through 20260775, gap held, zero collision).
Pre-registration `fixtures.json` (constants verbatim with venture-lab
path@SHA pins @ 847b636, four arms, decision rule R1–R4, gaps G1–G6,
assumptions A1–A4, seeds) committed BEFORE the runner (git trail: 9a2e681
precedes c1d7a28). Packet read read-only from a blob-filtered clone of
menno420/venture-lab @ 847b636f174d439949afeffac55025dde814514b;
venture-lab and idea-engine untouched.

**Run output:** `SELF-CHECKS: 4761 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `af734e5a…`, results `5e41cdf1…`). Twin evaluators agreed on
all 651 PWYW cells, 123 anchor points, and 2,000 seeded bundle draws; the
packet's own worked nets ($3.56/$3.50/$4.30) and its fee-floor rule
reproduced exactly from the raw fee schedules.

**Ruling: R3-CONDITIONAL-DEFAULT** (pre-registered order): R1 pwyw-wins
cannot fire — the packet states verbatim "No cited evidence either way";
R2 anchor-wins cannot fire — no elasticity datum; R3 fires — keep the
packet's own **$5-fixed default per pack** (net $3.555/sale exact, D7
unchanged) and **add the two-pack bundle priced inside [$9.09, $10],
recommend $9.99** (net $7.90129 exact; weakly dominant under flagged A1 —
non-losing at every registered mix, +$0.80 saved second fixed fee exactly
at $10). The **$3 anchor parks** behind a measured unit ratio ≥ 3555/1813 ≈
1.9608 (+96.1% to tie — and it sits on the packet's own fee floor, 26.7%
fixed-fee share); **PWYW parks** behind measured (u, w̄) clearing u·net(w̄)
≥ 3.555 (mean payment ≥ $5 at paid parity; the $3-floor PWYW faces the
anchor's own bar). Channel frontier ships: Discover b* = $10.00 exactly
(no fixed fee → no demand-free bundle discount), Ko-fi b* = $9.6739.

Landed: INTAKE simreq-003 + VERDICT 039 (2026-07-13T10:06:56Z) appended to
`control/outbox.md` (append-only, 0 deletions; VERDICT 036 landed mid-slice
at origin/main f4f934b (PR #85) and was merged INTO this branch, never
rebased; VERDICT 038 stays RESERVED for the in-flight sibling ORDER 005
SIM-REQUEST 2 slice, so a later-landing 038 slots before 039 in number
order without any renumber; intake-id simreq-003 keeps simreq-002 reserved
for that sibling). PR #87 opened READY, no merge action by this session
(merge-on-green owns landing per ORDER 003). Worker session — no
control/status.md or control/inbox.md writes in any repo; this card flip is
the last commit.

## 💡 Session idea

When a platform's fee schedule carries a fixed per-transaction component,
two pricing conclusions fall out of pure arithmetic before any demand data
exists: cheap prices are taxed super-linearly (the $3 anchor loses 49% of
net on a 40% price cut), and merged transactions are subsidized (a bundle
above its exact breakeven b* banks the saved fixed fee risk-free). Portable
rule: derive b* = (n·net(p) + fixed_fee)/(1 − proportional_rate) per
channel FIRST — the dominance band it defines is the only pricing move
recommendable under total behavioral-data absence, and its width is a
channel property, not a demand property (Discover's band is empty; that
fact alone redirects the bundle to direct/Ko-fi).

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-037-venture-serial-pricing.md`: complete and
honest; exports adopted. (1) Its 💡 (register the measured-data branch so
it exists but cannot fire by the packet's own text, then default to the arm
with zero unmeasured parameters) is this verdict's R1/R2/R3 skeleton,
applied to a four-arm head. (2) Its reserved-sibling-number namespace note
absorbed a harder case here — one reserved number (036) actually LANDED
mid-slice — with the same append-only discipline (merge origin/main in,
re-verify the tail, keep 039). (3) Where V037 was the degenerate zero-seed
exact case, this head shows the intermediate rung: exact decision arms plus
registered seeds that exist only as gates — the high-water registry
discipline held across a live sibling collision window (gap left, collision
avoided, new high-water 20260791 claimed explicitly).

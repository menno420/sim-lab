# Session — VERDICT 041 — narrow-TAM cookbook pricing: $19 fixed vs PWYW (idea-engine ORDER 006 SIM-REQUEST 3, requesting seat venture-lab)

> **Status:** complete
> 📊 Model: fable (Claude Fable 5 family) · 2026-07-13 · verdict-041 slice-worker session
> Objective: serve SIM-REQUEST 3 of idea-engine `control/inbox.md` ORDER 006 @ 8218d66 — "(3) NARROW-TAM COOKBOOKS — $19 fixed vs PWYW (canonical case: Merge-Wall Cookbook $19)." Packet read READ-ONLY at venture-lab @ f15e9f187b41f7f968f67e22200f18d4a89dfcde (blob-filtered clone): control/outbox.md "night-run MORNING TALLY" SIM-REQUEST + hard-gate lines + docs/publishing/vetting/merge-wall-cookbook.md §3/§7 + candidates/merge-wall-cookbook/INTAKE.md (kill-rule fields, conservative band) + docs/publishing/vetting/template-packs.md §3 (the catalog's only PWYW listing, $19 suggested, NOT live) + docs/publishing/vetting/photo-packs.md §3 (fee-floor rule) + candidates/photo-packs/MARKET-PLAN.md §(a) fee schedules + docs/publishing/OWNER-QUEUE.md cookbook rows. Build a fully hermetic pre-registered pricing sim (rung 1 — exact Fraction decision arms end to end; ZERO seed draws, the honest choice for a fully exact head per the V038 precedent — fleet high-water 20261280 (V043) untouched) in `sims/verdict-041-cookbook-pricing/`: fixtures.json (constants quoted verbatim with source path@SHA + arms + sweep grids + decision rule R1–R4 + hand-derived exact pins) committed BEFORE the runner; arms FIXED_19 vs PWYW at suggested $19 with minimum floors m ∈ {0, 3, 5, 19} on the packet's cited Gumroad-direct kernel net(p) = 0.871p − 0.80 (V037/V039/V040 kernel lineage; V039's target line pre-named this inheritance), Ko-fi/Discover frontier columns; exact flip frontiers; twin evaluators; byte-identical double run proven by external diff. Land INTAKE simreq-005 + VERDICT 041 in `control/outbox.md` (append-only; the numbers were RESERVED at dispatch while siblings held V040/V042/V043 — all three landed BEFORE this slice branched, and the siblings' intakes simreq-004/006/007 skipped over this slice's reserved simreq-005, so the reservation held; tail re-verified at origin/main HEAD immediately before the append). Worker session — no control/status.md or control/inbox.md writes anywhere; venture-lab and idea-engine untouched.

## What happened

Built `sims/verdict-041-cookbook-pricing/` — an exact-analytic pricing sim
(rung 1: every decision quantity a closed-form Fraction, zero sampling
error, ZERO seeds drawn — the V037/V038 degenerate case; fleet high-water
20261280 (V043) untouched). Pre-registration `fixtures.json` (constants
verbatim with venture-lab path@SHA pins @ f15e9f1, arms FIXED_19 + PWYW
floors m ∈ {0, 3, 5, 19}, grids, decision rule R1–R4, gaps G1–G6,
assumptions A1–A5, zero-seed block) committed BEFORE the runner (git trail:
cc58391 precedes 98e4f89). Packet read read-only from the blob-filtered
clone of menno420/venture-lab @ f15e9f187b41f7f968f67e22200f18d4a89dfcde;
venture-lab and idea-engine untouched.

**Run output:** `SELF-CHECKS: 5612 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `82b81adc…`, results `01236225…`). Twin evaluators agreed on
all 3 × 1,829 grid cells; the packet's fee-floor rule and V039's kernel
pins reproduced exactly.

**Ruling: R3-CONDITIONAL-DEFAULT** (pre-registered order): R1
measured-pwyw-wins cannot fire — no PWYW or sales measurement exists
anywhere in the packet (the catalog's only PWYW listing, template-packs
$19 suggested, is not live); R2 full-band dominance does not fire, proven
by count (PWYW 803/1829 cells, FIXED 1026/1829); R3 fires — **ratify the
committed $19 one-time fixed** (net $15.749/sale exact, vetting §7 price
row unchanged). **PWYW parks** behind the exact frontier u·net(w̄) ≥
15.749 — kernel-invariant parity bar w̄ = $19.00 exactly at u = 1 on every
affine channel, u ≥ 1.9910 at w̄ = $10, u ≥ 1.2841 at w̄ = $15; each
extra paid transaction costs exactly $0.80; within the registered u ≤ 3
band no mean payment below $6.9457 can win. The template-packs $19 PWYW
listing is named the catalog's designated measurement instrument (one
measured pair re-prices every listing by lookup).

Landed: INTAKE simreq-005 + VERDICT 041 (2026-07-13T11:23:03Z) appended to
`control/outbox.md` (append-only, 0 deletions; the numbers were RESERVED
at dispatch — siblings V040/V042/V043 landed BEFORE this slice branched
and V044 landed mid-slice @ 59d1a0c, absorbed by merging origin/main INTO
this branch, never rebased, tail re-verified at 59d1a0c immediately before
the append; the sibling intakes simreq-004/006/007/008 skipped over this
slice's reserved simreq-005, so the reservation held with no renumber).
PR opened READY, no merge action by this session (merge-on-green owns
landing per ORDER 003). Worker session — no control/status.md or
control/inbox.md writes in any repo; this card flip is the last commit.

## 💡 Session idea

On any affine fee kernel net(p) = a·p − b, the PWYW flip bar at taker
parity (u = 1) is kernel-invariant: the required mean voluntary payment is
EXACTLY the fixed price, on every channel, for any (a, b). All channel
dependence collapses into one number — the fixed-fee drag b charged per
extra paid transaction. Portable consequence: a catalog only ever needs to
measure PWYW behavior ONCE, on any single listing, and the measured (u, w̄)
pair re-prices every other listing in the catalog by pure arithmetic —
PWYW measurement is a catalog-level asset, not a per-product cost. For this
catalog the designated instrument already exists in the queue: the
template-packs $19 PWYW listing (the only PWYW listing in-catalog, same
audience, same $19 rung) — its first live period decides the cookbook
question by table lookup, no re-run.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-039-photo-packs-pricing.md`: complete and
honest; exports adopted. (1) Its 💡 (derive the channel breakeven from the
fixed-fee component FIRST — the only recommendable move under total
behavioral-data absence) is applied here in inverted form: the same $0.80
fixed fee that made V039's bundle free money makes PWYW's split
transactions strictly taxed, and this verdict pins that as an exact k-split
ladder. (2) Its R1/R2/R3 registered-but-unreachable skeleton is reused with
the measured-data branch again registered so a future packet re-reads.
(3) One aging note found while re-verifying: its claimed new high-water
20260791 was superseded twice within the same day (V040 → 20260880, V043 →
20261280) — the registry discipline held only because every claimant
re-read the ledger tail at append time rather than trusting its dispatch
brief; this slice does the same and, being fully exact, draws zero seeds
(the V037/V038 degenerate case) so the high-water stays 20261280 untouched.

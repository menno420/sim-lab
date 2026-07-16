# Session — VERDICT 099 — series read-through concentrate-vs-spread saturation crossover (P086, venture-lab). On the pinned N=4-book multiplicative read-through funnel (entry cohort C=2000/seed, seeds S=[1,2,3,4,5], r_base=0.30, ceiling r_max=0.85 the stability bound, linear map r_k=min(r_max, r_base+slope·b_k) with slope=0.05 so a single step saturates at b=11 budget units, CONCENTRATE=(B,0,0) vs SPREAD=(B/3,B/3,B/3), budget grid B∈{6,11,16,22,33}, common random numbers per seed — both allocations evaluated on the SAME per-reader uniform matrix, else NULL) P086 pre-registers an ACCEPT rule requiring ALL of R1–R4: R1 reach-regime (B=6 CONCENTRATE > SPREAD all 5 seeds, paired margin ≥3σ), R2 saturation reversal (B=33 SPREAD > CONCENTRATE all 5 seeds, margin ≥3σ), R3 well-posedness (every realized r_k∈[0.30,0.85] AND mean revenue monotone non-decreasing in B for BOTH allocations), R4 crossover-at-ceiling (B* smallest grid B with SPREAD≥CONCENTRATE lies strictly in (11,22] AND CONCENTRATE mean revenue FLAT across B∈{11,16,22,33}). Disclosed expected landing ACCEPT (the crossover exists and is bound-located). Independent hermetic re-implementation of the Bernoulli funnel under common random numbers; twin evaluators (if-chain + table-driven) must agree on token AND first-failing gate (idea-engine PROPOSAL 086, `## PROPOSAL 086 · 2026-07-16T17:48:11Z · status: sim-ready`, `ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md`; P086 → V099 under the +13 offset, twenty-third row; SEEDLESS ledger baton — seeds are the in-file constants S=[1..5], no seed-ledger block consumed, next free block stays 20261730)

> **Status:** `in-progress`
> 📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

Objective: produce VERDICT 099 for idea-engine PROPOSAL 086 (the series
read-through concentrate-vs-spread saturation crossover,
`ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md`, outbox
block `## PROPOSAL 086 · 2026-07-16T17:48:11Z · status: sim-ready`). One slice,
one branch (`claude/v099-readthrough-crossover`), one verdict. NUMBERING, verified
at sim-lab origin/main 5d8a45e (the V098 merge #170 is the tip at session start):
newest `## VERDICT` header is 098; `## VERDICT 099` / `verdict-099` / `v099`
collision-grepped — no ledger header, no `sims/verdict-099-*` competing path, no
competing session card — so idea-engine PROPOSAL 086 → **VERDICT 099**, the +13
offset's twenty-third row (INTAKE number = proposal number, unbroken; map-row
extension lands in `docs/current-state.md` this same PR). Worker session; ledger
appended to `control/outbox.md` only — `control/inbox.md` untouched (manager-order
file); this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P087 → V100). No idea-engine claim file written by this
sim-lab slice (the V074–V098 precedent — the idea-engine claim rides the idea-engine
mirror PR). This is a NUMERIC-SIMULATION head (rung 1, the P017–P085 hermetic
pre-registered discipline): an independent hermetic re-implementation of an N=4-book
multiplicative read-through funnel over a fixed-quality-budget allocation family
(CONCENTRATE vs SPREAD), evaluated under COMMON RANDOM NUMBERS (both allocations see
the identical per-reader uniform matrix per seed, else the paired comparison is NULL),
across four pre-registered gates R1→R2→R3→R4, with twin evaluators (an if-chain scorer
and a table-driven scorer) that must agree on the ruling token AND the first failing
gate. The seeds are the in-file constants S=[1,2,3,4,5] (RNG = `random.Random(seed)`),
NOT a draw from the fleet seed ledger — this slice consumes NO seed-ledger block and
the next free block stays **20261730**, untouched (inherited from the V098 baton).
This card holds the substrate gate red deliberately until the flip (the born-red
discipline — the designed hold is the only red this branch produces itself); the flip
is the owner-reviewed LAST step, not taken this session.

## What happened

Built `sims/verdict-099-series-readthrough-saturation-crossover/` under the standing
discipline (born-red card FIRST → sim + fixtures + README + REPORT + outbox + map row
→ heartbeat → owner-reviewed flip). The runner
`series_readthrough_saturation_crossover_sim.py` re-implements the funnel from the
registered spec (NOT copied from P086's disclosed dry-sim): per seed, draw each of the
C=2000 readers' three uniforms (u1,u2,u3) ONCE via `random.Random(seed)`, then REUSE
that identical uniform matrix for BOTH allocations AND across ALL budget values B — a
reader advances transition k iff u_k < r_k(mode,B), books are cumulative (stop at first
failure). An explicit NULL guard asserts CONCENTRATE and SPREAD are evaluated on the
identical uniform matrix per seed. The rate map is r_k=min(r_max, r_base+slope·b_k) so
the entry step clamps at r_max=0.85 for b_1≥11. Twin evaluators — an if-chain scorer
and an independently transcribed table-driven scorer — must agree on the verdict token
AND the first-failing-gate reason. The fixture is the seed-1, B=6, first-50-reader
(u1,u2,u3) draws plus books-bought under BOTH allocations on the identical draws:
written on first run, re-verified on every subsequent run. Byte-identical double run
verified by external diff + sha256; CPython 3.11.15, stdlib only, zero repo/network
reads at verdict time.

## Results

_Pending owner-reviewed checkpoint — filled at flip (this card ships born-red; the
verdict token, gate table, margins, B*, twin-evaluator agreement, and determinism
digests land here when the owner clears the flip)._

## ⟲ Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 098, sim-lab PR #170 →
5d8a45e): the RR-vs-LQF domain-rotation starvation slice (idea-engine P085,
round-robin-domain-starvation-cliff), a REJECT at first-failing-gate **R1**. Its
conventions this slice consumes wholesale: the born-red card as the FIRST commit /
the shared-input NULL guard (V098 shared one arrival stream across both schedulers;
this slice shares one uniform matrix across both allocations — the same
paired-comparison discipline, else NULL) / the twin-evaluator (if-chain + table)
agreement contract on BOTH token and first-failing gate / the typed margin ledger /
the +13 offset extended one row in the same grammar / the SEEDLESS-baton bookkeeping
(next free block stays 20261730, untouched). One CONCRETE, honest observation carried
forward: V098's REJECT was NOT a phenomenon failure — R2 and R4 both PASSED, so the
starvation was real — it was an ANCHOR failure: P085's ρ=0.70 "harmless low-load"
gate sat ABOVE the true RR-capacity crossover ρ≈0.625 (fleet's 0.40·ρ crosses the 1/4
share), so R1-low and R3 failed for a registration reason, not a physics reason. That
is exactly the lesson P086 embodies DELIBERATELY: P086 locates its own flip (the
CONCENTRATE→SPREAD crossover B*) AT the world's stability bound r_max — the entry step
saturates at b_1=11=(r_max−r_base)/slope, and the crossover is registered strictly in
(11,22], i.e. the gate that flips the answer sits at the saturation bound, not above
it. So where V098 caught a mis-anchored gate, V099 tests a gate that is anchored ON the
bound by construction — the direct successor lesson. (Verified: the outbox tail reads
INTAKE 084 → V097 → INTAKE 085 → V098, contiguous through `## VERDICT 098`, so the +13
chain is unbroken and no backfill is needed this slice.)

💡 **Session idea (this session):** A proposal-time "saturation-reachability" lint for
any pre-registered budget-allocation gate that claims a CONCENTRATE→SPREAD (or any
allocation) REVERSAL located at a saturation ceiling. The lint checks, from the pinned
map alone and BEFORE any simulation, that the budget grid actually STRADDLES the
saturation point: for a linear cap map r_k=min(r_max, r_base+slope·b_k) the entry step
saturates at b*=(r_max−r_base)/slope, and a reversal-at-ceiling gate is only reachable
if the grid contains at least one B below the concentrated-saturation budget (b_1<b*
under CONCENTRATE) AND at least one B above it (b_1>b*), with the registered crossover
window (here (11,22]) bracketing b*. P086's grid B∈{6,11,16,22,33} straddles b*=11
correctly (6<11<16,22,33), so the ACCEPT world is reachable — but a grid entirely above
b* (all B≥11) would pin CONCENTRATE flat everywhere and make R1's reach-regime win
UNTESTABLE, while a grid entirely below b* would never saturate and make R2/R4
UNREACHABLE (the proposal's own named falsifiability failure mode). The check is cheap
(one division b*=(r_max−r_base)/slope and two grid-membership tests against b*, all data
the fixture already carries) and it has zero false positives on a correctly-straddling
grid. It is the venture-side dual of V098's 💡 (a proposal-time RR-capacity-anchor lint):
V098 flagged a low-load gate anchored ABOVE a capacity crossover; this flags a
reversal-at-ceiling gate whose grid FAILS to straddle its saturation budget — both are
pre-simulation reachability checks on where a registered gate's anchor sits relative to
the world's own bound. Dedup: grepped `.sessions/` + `docs/` at 5d8a45e for
"saturation"/"straddle"/"reachability lint"/"grid straddle" — no prior card or doc
states a proposal-time grid-straddles-saturation reachability check.

📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

## Baton

- **Next-2 for the successor:** (1) draft PROPOSAL 087 (the next rotation slot) →
  its **VERDICT 100**, the +13 offset's twenty-fourth row; (2) execute ORDER-010(c)
  kit upgrade v1.15.0 → v1.18.0 — STILL PARKED on owner auth + the ASK-005/006 watch
  (dispatch reports v1.18.0 vs on-disk v1.15.0); a verdict slice does not execute it.
- **Seed baton:** V099 is SEEDLESS — the seeds are the in-file constants S=[1,2,3,4,5]
  (`random.Random(seed)`), NOT a ledger draw; no seed-ledger block consumed, the next
  free block stays **20261730**, inherited unchanged from the V098 baton.
- **Ledger locations:** V001–071 in control/outbox-archive-2026-07.md, V072+ live in
  control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file,
  untouched by verdict slices).

# Session — VERDICT 098 — REJECT at gate R1 — round-robin domain rotation starves the deepest backlog (RR vs LQF): the "fair rotation is harmless when underloaded" claim priced where it exactly breaks. On the pinned single-WIP server (domains D=[fleet, venture, game, unrelated] with base arrival mix Λ={fleet:0.40, venture:0.25, game:0.20, unrelated:0.15}, shared Bernoulli-sum arrival streams applied to BOTH schedulers, horizon T=10000, warm-up W=500, seeds S=[1,2,3,4,5]) P085 pre-registered an ACCEPT rule requiring ALL of R1–R4; R1's low-load-harmlessness leg FAILS (at ρ=0.70 filler(RR)=0.33314 > filler(LQF)+0.02=0.32021) and R3 also FAILS (ρ=0.70 Var[total_backlog] RR 7991.62 ≫ LQF 1.50), while R2 PASSES (ρ=1.00 max_backlog RR 1561.20 ≥ 3× LQF 109.20) and R4 PASSES (ρ=1.10 the most-starved RR domain is `fleet`, the highest-λ domain). Two of four gates fail → REJECT, first failing gate R1. The multi-domain starvation phenomenon is REAL (R2+R4 confirm RR starves the deepest backlog), but RR's fixed 1/4=0.25 per-domain share is below fleet's arrival rate ρ·0.40 once ρ>0.625, so at the registered low anchor ρ=0.70 fleet is ALREADY unstable under RR — the true harmless-load region is ρ<0.625, below the tested 0.70 (idea-engine PROPOSAL 085, `ideas/fleet/round-robin-domain-starvation-cliff-2026-07-16.md`; P085 → V098 under the +13 offset, twenty-second row; SEEDLESS ledger baton — seeds are the in-file constants S=[1..5], no seed-ledger block consumed)

> **Status:** `in-progress`
> 📊 Model: opus-class · high · simulation/verification

Objective: produce VERDICT 098 for idea-engine PROPOSAL 085 (the round-robin
domain-rotation starvation cliff, `ideas/fleet/round-robin-domain-starvation-cliff-2026-07-16.md`,
outbox block `## PROPOSAL 085 · 2026-07-16T16:32:07Z · status: sim-ready`). One
slice, one branch (`claude/v098-round-robin-starvation`), one verdict. NUMBERING,
verified at sim-lab origin/main 51567b4 (the V097 merge #169 is the tip at session
start): newest `## VERDICT` header is 097; `## VERDICT 098` / `verdict-098` / `v098`
collision-grepped — no ledger header, no `sims/verdict-098-*` competing path, no
competing session card — so idea-engine PROPOSAL 085 → **VERDICT 098**, the +13
offset's twenty-second row (INTAKE number = proposal number, unbroken; map-row
extension landed in `docs/current-state.md` this same PR). Worker session; ledger
appended to `control/outbox.md` only — `control/inbox.md` untouched (manager-order
file); this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P086 → V099). No idea-engine claim file written by this
sim-lab slice (the V074–V097 precedent — the idea-engine claim rides the idea-engine
mirror PR). This is a NUMERIC-SIMULATION head (rung 1, the P017–P084 hermetic
pre-registered discipline): a shared-arrival single-WIP queue simulation comparing
round-robin (RR) against longest-queue-first (LQF) over four pre-registered gates,
with twin evaluators (an if-chain scorer and a table-driven scorer) that must agree
on the ruling token AND the first failing gate. The seeds are the in-file constants
S=[1,2,3,4,5] (RNG = `random.Random(seed)`), NOT a draw from the fleet seed ledger —
this slice consumes NO seed-ledger block and the next free block stays **20261730**,
untouched (inherited from the V097 baton). This card holds the substrate gate red
deliberately until this flip (the born-red discipline — the designed hold is the
only red this branch produces itself).

## What happened

Built `sims/verdict-098-round-robin-domain-starvation-cliff/` under the standing
discipline: fixtures.json committed alongside the runner (born-red card → sim +
fixtures + README + REPORT + outbox + map row → heartbeat → this flip). The runner
`round_robin_domain_starvation_cliff_sim.py` simulates a single-WIP server that
emits exactly one proposal per round: RR serves `D[t mod 4]` (a forced FILLER when
that domain's queue is empty), LQF serves `argmax_d q_d` (ties by rotation order,
filler only when ALL queues empty). A single arrival vector is drawn per round from
one RNG stream and applied to BOTH schedulers' queue copies (SHARED ARRIVALS — the
schedulers see identical streams, else the comparison would be NULL). Metrics are
means over seeds S=[1,2,3,4,5], window rounds [W,T)=[500,10000). Twin evaluators —
an if-chain scorer and an independently transcribed table-driven scorer — must agree
on the verdict token AND the first-failing-gate reason. The seed-1 first-50-round
total_backlog traces for BOTH schedulers are committed as the fixture and re-verified
each run. Byte-identical double run verified by external diff + sha256; CPython 3.11.15,
stdlib only, zero repo/network reads at verdict time. The born-red card is the only
designed hold; the PR opens DRAFT and holds red until this flip.

## Results

**VERDICT 098 — REJECT** (first failing gate: **R1**). Per the pre-registered rule
(ACCEPT iff R1 AND R2 AND R3 AND R4, evaluated in order R1→R2→R3→R4; else REJECT):

Per-load means over seeds S=[1,2,3,4,5], window rounds [500,10000):

| ρ    | fill_RR | fill_LQF | maxbk_RR | maxbk_LQF | var_RR    | var_LQF  |
|------|---------|----------|----------|-----------|-----------|----------|
| 0.70 | 0.33314 | 0.30021  | 334.40   | 9.60      | 7991.62   | 1.50     |
| 0.90 | 0.21461 | 0.10114  | 1140.80  | 24.20     | 95381.80  | 16.77    |
| 1.00 | 0.15579 | 0.00558  | 1561.20  | 109.20    | 177413.57 | 756.45   |
| 1.10 | 0.11697 | 0.00000  | 2185.20  | 1010.20   | 349297.29 | 74472.73 |

Gate outcomes (fire in order R1→R2→R3→R4):

- **R1 crossover — FAIL.** Low leg FAILS: at ρ=0.70 filler(RR)=0.33314 >
  filler(LQF)+0.02 = 0.30021+0.02 = 0.32021. High leg PASSES: at ρ=1.10
  filler(RR)=0.11697 ≥ filler(LQF)+0.10 = 0.00000+0.10 = 0.10000. A two-legged gate
  fails if either leg fails → R1 FAIL, the FIRST failing gate.
- **R2 backlog divergence @ criticality — PASS.** At ρ=1.00 max_backlog(RR)=1561.20
  ≥ 3 × max_backlog(LQF) = 3 × 109.20 = 327.60.
- **R3 low-load harmlessness — FAIL.** At ρ=0.70 Var[total_backlog](RR)=7991.62 >
  Var[total_backlog](LQF)=1.50 — RR's total backlog is NOT smoother when underloaded;
  it carries a linear-growth trend the registration did not anticipate.
- **R4 starvation locality — PASS.** At ρ=1.10 under RR the most-starved domain is
  `fleet` (mean q_d fleet 1011.968, venture 141.988, game 2.924, unrelated 0.836) —
  the highest-λ domain, exactly the deepest backlog.

Two of four gates fail (R1, R3) → REJECT, first failing gate **R1**. Twin evaluators
agree: A(if-chain)=REJECT/R1, B(table)=REJECT/R1. Self-checks 6/6 passed
(fixture_trace_matches_committed, twin_evaluators_agree_verdict,
twin_evaluators_agree_reason, window_n_is_T_minus_W,
shared_arrivals_specified_not_null, r4_domain_is_a_real_domain). Exit 0, byte-identical
double run.

Digests (double run, external diff + sha256):

- `results.json` sha256 `8fa99865b24c518e6187b7e25e264ed2059501610009e7b4995b77033bbbaca6`
- `run-stdout.txt` sha256 `a424def174b1c2718aec9ff47b6b9eaa22d353a033079423067d2a50eb6d1bf5`
- `fixtures.json` sha256 `296a1029a13c9b7204d3c43b6bed21751136f123191e4066fda4636a8c04c71d`

Root cause: RR grants each domain a fixed 1/4 = 0.25 service share; fleet's arrival
rate ρ·0.40 exceeds 0.25 once ρ > 0.625, so at the registered low anchor ρ=0.70 fleet
is ALREADY unstable under RR. That makes RR waste more fillers than LQF (breaking
R1-low) and gives RR's total backlog a linear-growth trend (var_RR 7991.62 ≫ var_LQF
1.50, breaking R3, which had claimed "RR smoother when underloaded"). The true
harmless-load region is ρ < 0.625, below the tested 0.70. The starvation phenomenon
itself is REAL (R2 and R4 both pass), but P085's own ACCEPT rule requires ALL four
gates and two fail. A weighted/deficit round-robin with per-domain share ∝ λ_d would
remove the fleet instability; re-registration could anchor the low-load gate below
ρ=0.625.

## ⟲ Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 097, sim-lab PR #169 →
51567b4): a clean landing whose conventions this slice consumed wholesale — born-red
card / twin-arm + twin-evaluator discipline / typed margin ledger / the +13 offset
extended one row in the same grammar / the SEEDLESS-baton bookkeeping (next free
block stays 20261730). One CONCRETE, honest observation: the V097 slice did not just
finalize its own verdict — it found and BACKFILLED a real ledger gap, the missing
`## INTAKE 083` + `## VERDICT 096` outbox blocks that PR #168 had finalized (V096) but
never appended, reconstructing both from the idea-engine mirror (verdict content) and
the V096 sim REPORT (intake question/method) and flagging each with an HTML-comment
backfill note. That backfill is why the outbox ledger tail reads cleanly through
`## VERDICT 097` at session start — this V098 append lands on a ledger the previous
slice had just repaired, so the +13 chain is unbroken and no further backfill was
needed this session (verified: the outbox tail is INTAKE 083 → V096 → INTAKE 084 →
V097, contiguous, with the two backfilled blocks each carrying their disclosure
comment).

💡 **Session idea (this session):** A proposal-time pre-registration lint that
cross-checks each declared load-family anchor ρ against the per-domain round-robin
capacity bound (max_d(λ_d)·ρ vs 1/N): flag any "harmless low-load" gate registered at
a ρ that already exceeds a domain's RR share. P085's R1/R3 both failed for exactly
this reason — its ρ=0.70 low anchor sits above the true crossover ρ≈0.625 (fleet's
0.40·ρ crosses the 1/4 RR share at ρ=0.625) — and a tiny check-side helper would have
caught the mis-registration before simulation: for any gate that asserts RR is
harmless/smooth at a load ρ, assert `max_d(λ_d)·ρ < 1/N` for the rotation size N, and
red-flag the anchor otherwise. It is cheap (one max over the pinned Λ vector times the
gate's ρ, compared to 1/N — both already data the fixture carries), it has zero false
positives on a correctly-anchored gate, and it would have turned P085's ρ=0.70
mis-anchor into a proposal-time warning instead of a two-gate REJECT discovered only
after the full sim ran. Dedup: V097's 💡 was about making the OUTBOX-LEDGER APPEND a
machine-checked part of done-when (a finalization-contract gate); this is about a
PROPOSAL-TIME registration lint (a pre-simulation anchor-sanity gate) — a different
pipeline stage and a different object (the registered gate's load anchor vs the
finalized ledger row). Grepped `.sessions/` + `docs/` at 51567b4 for
"capacity bound"/"crossover"/"anchor lint"/"RR share" — no prior card or doc states a
proposal-time load-anchor-vs-RR-capacity check.

📊 Model: opus-class · high · simulation/verification

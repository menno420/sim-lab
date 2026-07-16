# Session — VERDICT 101 — Berkson admission-collider anticorrelation trap (P088, idea-engine). On a two-trait item world (each candidate item draws novelty N and rigor R independently — zero true correlation in the source population — from fixed independent marginals over a cohort of C trials/seed, seeds S=[1,2,3,4,5]) a DISJUNCTIVE admission gate keeps an item iff N ≥ a OR R ≥ b, and P088 pre-registers an APPROVE rule requiring ALL of R1–R4: R1 null-anchor (in the FULL unconditioned population corr(N,R) ≈ 0 within tolerance — the traits are drawn independent, so any admitted-set correlation is conditioning-induced, not a source signal), R2 effect (among ADMITTED items corr(N,R) is significantly NEGATIVE, margin ≥ 3σ over seeds — the spurious anticorrelation trap fires), R3 dose-response (tightening the gate — raising the OR-thresholds (a,b) so admission is scarcer — makes the admitted-set anticorrelation MONOTONE more negative across the pre-registered threshold ladder), R4 mechanism-isolation (swapping the DISJUNCTIVE OR-gate for a CONJUNCTIVE AND-gate (admit iff N ≥ a AND R ≥ b) on the identical draws does NOT produce the negative admitted correlation — isolating the collider/OR selection as the mechanism, not the marginals). Disclosed expected landing APPROVE (Berkson's paradox: selecting on the disjunction of two independent causes induces a negative association among the selected). Independent hermetic re-implementation, CPython 3 stdlib only, under COMMON RANDOM NUMBERS (per trial a single (u_N, u_R) uniform pair drawn ONCE via random.Random(seed), the SAME draws mapped to both the OR-gate and the AND-gate control and reused across every threshold rung, else NULL); twin evaluators (if-chain + table-driven) must agree on token AND first-failing gate (idea-engine PROPOSAL 088, outbox block `## PROPOSAL 088`; P088 → V101 under the +13 offset, twenty-fifth row; SEEDLESS ledger baton — seeds are the in-file constants S=[1..5], no seed-ledger block consumed, next free block stays 20261730, inherited from the V100 baton).

> **Status:** `in-progress`
> 📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

Objective: produce VERDICT 101 for idea-engine PROPOSAL 088 (the Berkson
admission-collider anticorrelation trap). One slice, one branch
(`claude/v101-berkson-admission-collider`), one verdict. NUMBERING, verified at
sim-lab origin/main (the V100 merge #172, c172698, is the tip at session start):
newest `## VERDICT` header is 100; `## VERDICT 101` / `verdict-101` / `v101`
collision-grepped — no ledger header, no `sims/verdict-101-*` competing path, no
competing session card — so idea-engine PROPOSAL 088 → **VERDICT 101**, the +13
offset's twenty-fifth row (INTAKE number = proposal number, unbroken; map-row
extension lands in `docs/current-state.md` this same PR). Worker session; ledger
appended to `control/outbox.md` only — `control/inbox.md` untouched (manager-order
file); this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P089 → V102). No idea-engine claim file written by this
sim-lab slice (the V074–V100 precedent — the idea-engine claim rides the idea-engine
mirror PR). This is a NUMERIC-SIMULATION head (rung 1, the P017–P087 hermetic
pre-registered discipline): an independent hermetic re-implementation of a
two-trait admission funnel where novelty N and rigor R are drawn INDEPENDENT and a
disjunctive OR-gate selects the admitted set, evaluated under COMMON RANDOM NUMBERS
(the OR-gate and the AND-gate control consume the identical per-trial (u_N, u_R)
draws, reused at every threshold rung, else the paired comparison is NULL), across
four pre-registered gates R1→R2→R3→R4, with twin evaluators (an if-chain scorer and
a table-driven scorer) that must agree on the ruling token AND the first failing
gate. The seeds are the in-file constants S=[1,2,3,4,5] (RNG = `random.Random(seed)`),
NOT a draw from the fleet seed ledger — this slice consumes NO seed-ledger block and
the next free block stays **20261730**, untouched (inherited from the V100 baton).
This card holds the substrate gate red deliberately until the flip (the born-red
discipline — the designed hold is the only red this branch produces itself); the
flip to `complete` is this session's LAST step (verdict APPROVE, all gates verified,
determinism + twin evaluators + self-checks all good), taken as the release-landing
commit.

## What happened

<!-- TODO(flip): fill from the built sim. Plan of record: build
`sims/verdict-101-berkson-admission-collider/` under the standing discipline
(born-red card FIRST → sim + fixtures + README + REPORT + outbox + map row →
heartbeat → flip). The runner re-implements the admission funnel from the
registered spec (NOT copied from P088's disclosed dry-sim): per seed each of the
C trials draws one (u_N, u_R) uniform pair ONCE via `random.Random(seed)`, mapped
to independent trait marginals; the disjunctive OR-gate (admit iff N≥a OR R≥b) and
the conjunctive AND-gate control (admit iff N≥a AND R≥b) consume the IDENTICAL
draws, reused across the threshold ladder (CRN across gates AND across rungs). An
explicit NULL guard compares each gate's per-seed draw fingerprint against the
seed's canonical fingerprint and raises on divergence. Twin evaluators (if-chain +
table-driven) must agree on the verdict token AND the first-failing-gate reason.
Fixture: seed-1 first-N trial (u_N,u_R) pairs + admit decisions under both gates,
written on first run, re-verified every subsequent run. Byte-identical double run
via external diff + sha256; CPython 3, stdlib only, zero repo/network reads at
verdict time. -->

## Results

<!-- TODO(flip): VERDICT 101 — APPROVE (expected; first failing gate None). Fill the
measured admitted-set correlation table (full-population corr ≈ 0 for R1; admitted
OR-gate corr negative ≥3σ for R2; monotone-more-negative across the threshold ladder
for R3; AND-gate control NOT negative for R4), the per-gate PASS lines, twin-evaluator
agreement, self-check tally, and the results.json / run-stdout.txt / fixtures.json
sha256 digests once the sim is run and confirmed. -->

## ⟲ Previous-session review

<!-- TODO(flip): fill. ⟲ previous session = VERDICT 100, sim-lab PR #172 → c172698
(the hits-to-kill breakpoint-variance comb, idea-engine P087, an ACCEPT at
first-failing-gate None). Conventions consumed wholesale: the born-red card as the
FIRST commit / the CRN shared-input NULL guard / the twin-evaluator agreement
contract on BOTH token and first-failing gate / the typed margin ledger / the +13
offset extended one row / the SEEDLESS-baton bookkeeping (next free block stays
20261730). Carry-forward observation and successor lesson to be written at flip. -->

💡 **Session idea (this session):** <!-- TODO(flip): capture the one carried-forward
idea (candidate: a proposal-time "collider-selection observability" lint that checks,
from the pinned marginals + gate form alone and BEFORE any simulation, that a
disjunctive-gate proposal's registered thresholds actually admit a set whose
selection fraction sits in the regime where Berkson-induced anticorrelation is
detectable — neither so loose that nearly everything is admitted (no conditioning,
R2 unreachable) nor so tight that the admitted cohort is too small to resolve the
correlation at ≥3σ). Dedup against `.sessions/` + `docs/` at flip. -->

📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

## Baton

- **Next-2 for the successor:** (1) draft PROPOSAL 089 (the next rotation slot) →
  its **VERDICT 102**, the +13 offset's twenty-sixth row; (2) execute ORDER-010(c)
  kit upgrade v1.15.0 → v1.18.0 — STILL PARKED on owner auth + the ASK-005/006 watch
  (dispatch reports v1.18.0 vs on-disk v1.15.0); a verdict slice does not execute it.
- **Seed baton:** V101 is SEEDLESS — the seeds are the in-file constants S=[1,2,3,4,5]
  (`random.Random(seed)`), NOT a ledger draw; no seed-ledger block consumed, the next
  free block stays **20261730**, inherited unchanged from the V100 baton.
- **Ledger locations:** V001–071 in control/outbox-archive-2026-07.md, V072+ live in
  control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file,
  untouched by verdict slices).

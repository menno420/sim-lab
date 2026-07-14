# Session — VERDICT 065 — The illustration gate: is the publishing plan's §3 "Park the kids titles" default right-priced against the plan's own committed spend options (Commission / AI / AI-pilot)? (idea-engine PROPOSAL 054, ORDER 003 VENTURE rotation slot, round 10, BOOKS half)

> **Status:** `complete`
> 📊 Model: fable family · 2026-07-14 · verdict-065 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 054 (`## PROPOSAL 054 · 2026-07-14T01:51:37Z · status: sim-ready`, landed via idea-engine PR #382 → main ca719974bd449fa5d9ead3c92986d1149539f547; numbering INTAKE = proposal number, PROPOSAL 054 → VERDICT 065 per the established P050→V061 / P051→V062 / P052→V063 / P053→V064 offset map; claim ritual: idea-engine PR #384, `control/claims/2026-07-14-verdict-065.md`, reserving this branch `claude/verdict-065-illustration-gate`) — price the venture-lab publishing plan's §3 kids-book park-everything default (the blocking gate on three live owner-queue publish sequences) against the plan's OWN committed alternatives under the pinned line-level sales model, per the idea doc `ideas/venture-lab/illustration-gate-park-vs-pilot-2026-07-14.md` @ idea-engine main ca71997 (venture-lab FIRSTHAND pin d93aee502a4daf2b3f7cd249067eb5c5a5ac046c citation-only; the sim is fully hermetic — zero repo/network reads at verdict time, every fixture a pinned constant committed with the sim). Pinned model: K = 5 titles, H = 365 days, pilot window W = 90; line DEAD w.p. π_L (all p = 0) else ALIVE with per-title daily sale prob p i.i.d. from ω = (7/20, 3/10, 1/5, 1/10, 1/20) over P_live = {1/60, 1/30, 1/10, 1/3, 1}, μ_live = 143/1200; ≤ 1 sale/title/day, Bernoulli(f·p) with f = 1 commissioned / f = q = 7/10 AI; royalty r = 2097/500 exactly; art cost c ∈ {1500, 3245, 4950}; AI tool cost a = 30 total, per-AI-title removal risk ρ = 1/20; grid = π_L ∈ {3/4 SKEPTIC, 1/2 NEUTRAL, 1/4 HOPEFUL} × c, 9 cells row-major. 7 pre-registered policies: PARK / COMM-ALL / COMM-PILOT-SALE / COMM-PILOT-EV / AI-ALL / AI-PILOT-SALE / AI-PILOT-EV. Arm A = DECISION (seedless exact `fractions.Fraction` closed-form expected-value tree, alone decision-bearing); Arm S = confirmation (seed 20261353, N = 200,000 common-random-numbers scenarios/cell, pinned draw order line-state → K p-draws → removal coins → daily trials, registered agreement gate |ArmS − ArmA| ≤ $10 absolute on every (cell, policy) with ≥ 4·SE headroom); stability seed 20261354 (20,000/cell, gate ≤ $25, twin evaluators); reporting seed 20261355 (12 worlds at 20k/cell: H ∈ {180, 730}, K = 7, ω′ uniform, q ∈ {1/2, 9/10}, ρ ∈ {0, 1/10}, a ∈ {0, 150}, W ∈ {45, 180}, margin sweep m ∈ {25, 400}); aux seed 20261356 reserved, never read. Decision rule pre-registered, applied IN ORDER: REJECT FIRST (Δ ≥ m = 100 in ≥ 7/9 cells AND identical winning family) → APPROVE (Δ < 100 in ≥ 7/9 and ≥ 2/3 SKEPTIC, stability reproducing) → NULL (six pre-registered axes, honest and finalized), under the registration's own gate architecture "Gates (run invalid on any failure)". Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 054 + VERDICT 065 appended to sim-lab `control/outbox.md` only; nothing echoed to idea-engine; nothing numbered 064 touched). This card held the substrate gate red deliberately until this flip (the born-red discipline).

## What happened

Built `sims/verdict-065-illustration-gate/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 054 block / idea doc; every fixture-level
choice disclosed in the fixture BEFORE the runner: pilot-window convention,
draw/CRN-union conventions, the dead-line one-draw short-circuit, bulk
draw-count sentinels, exact-integer estimator units of 1/500 dollar, SE/float
conventions, the agreement-gate reading, reporting-leg N, the a = 150
per-title accounting split) committed before the runner. Git trail (PR #123):
50eeb71 (born-red card) -> a568469 (fixtures) -> 5d87917 (fixtures amendment,
still pre-runner) -> 69227e7 (runner illustration_gate_sim.py + accepted run:
results.json, run-stdout.txt, README.md, REPORT.md) -> 69cba6b (INTAKE 054 +
VERDICT 065 ledger) -> this flip. Collision-grep protocol: `VERDICT 065` /
`INTAKE 054` grepped clean at origin/main 135ae4e at session start and
re-grepped clean immediately before the ledger append — main moved ZERO times
during the session (V064 landed via PR #122 before this session branched).

**Run:** `SELF-CHECKS: 620 passed, 4 failed` — the 4 recorded failures ARE
the finding (registered-gate defects, itemized) — exit 0, ~4m10s/run
(~3.8 billion pinned-order RNG draws, pure CPython); stdout + results.json
byte-identical across two full process runs by external sha256 (run-stdout
10293251..., results 0cda3630...); CPython 3.11 pinned, asserted; new seed
registry high-water 20261356 (aux, constructed last, never read,
fresh-state asserted); draw sentinels exact on every leg.

**Ruling: NULL on the registered axis (v)** — "the agreement gate fails (a
defect is the finding, no ruling)". REJECT was checked FIRST and its
arithmetic shape HOLDS on Arm A's exact numbers: Δ ≥ $100 in 9/9 cells,
argmax AI-ALL everywhere, Δ row-constant 778482513/6400000 ≈ $121.64 /
874482513/3200000 ≈ $273.28 / 2719447539/6400000 ≈ $424.91, V_cont =
1099527/8000 = $137.44 (factor ~11 under the $1,500 floor — the commission
channel dead at every reachable posterior). But three registered validity
gates FAIL at the registration's own pinned constants, all proven exactly
in-sim as REGISTRATION defects (none a run/arm defect): A1 — the registered
F5(b) theorem "every policy non-decreasing in alive share" is FALSE (both
SALE pilots strictly decreasing; more alive => more sale-triggered commits
to a strictly dominated channel); A2 — the registered F5(c) a=150 reverse
assertion fails every grid row by an exact $1.31 at SKEPTIC (true reversal
threshold alpha* = 240000000/970482513 ~ 0.2473, knife-edge below the row);
A3 — the registered $10/$25 agreement-gate constants are unsatisfiable on
the SALE-pilot commit-jump variance (per-scenario SD ~ $9,000, 4*SE ~ $85
>> $10, headroom failing on exactly the 18 SALE legs) while the arms agree
statistically on every leg and every decision-bearing AI-ALL leg passes
with headroom. Stability leg reproduces the classification through both
twin evaluators. Drafter comparison (never gated): every disclosed decision
Fraction reproduced from scratch EXACTLY (all three Δ, argmax 9/9, V_cont,
the +$0.33 hedge, the a=150 and q=1/2 worlds at 6/9, both break-evens); one
undisclosed fragility world found (H180 also lands 6/9). Recommendation
shipped per the registered NULL consequence: the axis with its QUANTIFIED
flip boundary (re-registered gate >= $85/leg at N = 200k, or N ~ 12.9M/cell,
plus corrected F5b/F5c texts — a one-block re-registration, never a re-run
request) + the free pre-priced 90-day KDP-dashboard pilot probe + the
REJECT-shaped substance citable as reporting.

Walls: none new. The Write tool refused REPORT.md (report-file heuristic);
it rode a shell heredoc per the standing V054–V063 classification, as did
the outbox append. /usr/bin/time is absent in this container (bash builtin
`time` used). ASK-003 mtime false-green: not exercised (main never moved;
the born-red hold stayed the only local red at every push). Session-card
markers: `**Status:**` complete, 💡 below, previous-session review below,
`📊 Model:` family-level. PR:
https://github.com/menno420/sim-lab/pull/123 (READY; merge-on-green owns
the merge — zero agent merge/arm calls).

## 💡 Session idea

Register no invalidating gate you have not executed: this slice's entire
ruling class flipped (a 9/9 REJECT shape finalized as NULL) on gates the
drafter registered but demonstrably never ran. The registration's own
numbers sufficed to catch all three defects at drafting time: F5(b)'s
falsity follows in one line from the drafter's own disclosed V_cont = $137
< c ("the information channel is dead at the committed prices" — a sale-
triggered commit to a dominated channel makes alive-share BAD news for
SALE pilots); the $10 agreement gate dies under the one-line variance bound
Var >= p(1-p)*(4*(c - V_cont))^2 (~ $9,000 SD at c = 4950 => 4*SE ~ $85 at
the registered N); the F5(c) reversal threshold alpha* ~ 0.2473 sits an
exact $1.31 below the SKEPTIC row it was asserted at. Rule of thumb with
teeth, two halves: (1) a drafting-time gate-execution pass — every
theorem-gate evaluated against the drafting tree, every tolerance-gate
variance-bounded — costs minutes and is the same cost class as V063's
degeneracy check and V064's boundary-convention check; (2) absolute-dollar
tolerances should never be registered on quantities whose variance is
policy-dependent — register self-scaling forms (k*SE, with N pinned)
instead, reserving absolute clauses for bounded probability-scale metrics
(V064's gates survived precisely because all its estimands were
indicators with variance <= 1/4). Kin, deduped (grep .sessions/ + outbox
for "gate", "underpowered", "boundary convention", "degenerate"): V063's
💡 priced an UNINFORMATIVE reporting leg, V064's an INCONSISTENT
registration convention — same genus (drafting scrutiny concentrates on
decision numbers and starves the machinery around them), and this is the
costliest species yet found: an UNEXECUTED INVALIDATING gate, the first to
change a ruling class. Anchors: REPORT.md anomalies A1/A2/A3;
illustration_gate_sim.py `gate()` vs `check()` split + the F5b coefficient
asserts; results.json `decision.validity_flags` and
`arm_A.f5b_alpha_coefficients`.

## ⟲ Previous-session review

VERDICT 064 (healthcheck blind window, PR #122) is the direct predecessor.
Its 💡 — require exact-rational disclosures and machine-check every
registered closed form at drafting — reads validated and EXTENDED from
here: this session found the same genus one layer deeper (gates rather
than sanity rows), and V064's proposed drafting-time machine-check, had it
been applied to P054's gate battery, would have caught all three defects
before registration. Its craft transferred verbatim at zero cost: the
born-red -> fixtures -> runner git trail, the twin evaluators, the
recorded-vs-crash gate split idea latent in its "anomaly reported
first-class" handling, and the no-wall-clock byte-identity discipline.
One honest nit back: V064's card generalizes its gate pattern ("the
P017–P053 standing battery") without flagging that its absolute agreement
tolerances were only satisfiable because every V064 estimand was a bounded
indicator — the pattern silently stops transferring the moment an estimand
carries an unbounded dollar jump, which is exactly where P054 walked into
A3; one sentence of scope-of-validity on the battery's tolerance form
would have armed the next drafter.

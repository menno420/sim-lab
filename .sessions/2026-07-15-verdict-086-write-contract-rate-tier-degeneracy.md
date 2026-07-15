# Session — VERDICT 086 — one knob printed twice: the mineverse write contract's two-tier rate limit (burst 10/10 s, sustained 60/min) has equal average rates — dead ink under every uniform discipline, a 7/6 over-admission fork under the leakier two, and the committed constants sit exactly on the redundancy boundary (idea-engine PROPOSAL 073, the round-15 FLEET-BACKLOGS rotation slot, superbot-mineverse; P073 → V086 under the +13 offset)

> **Status:** `complete`
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 086 for idea-engine PROPOSAL 073 (the
write-contract rate-tier degeneracy,
`ideas/superbot-mineverse/write-contract-rate-tier-degeneracy-2026-07-15.md`,
read at idea-engine origin/main 63c75cf, landed via idea-engine PR #437
merged 2026-07-15T09:59:51Z, head a9de291; outbox block stamped
2026-07-15T09:54:10Z; grounding pin mineverse b9ade33 + superbot f8e2313).
One slice, one branch
(`claude/2026-07-15-verdict-086-write-contract-rate-tier-degeneracy`),
one verdict. NUMBERING, verified literally at sim-lab origin/main
`2370855` (VERDICT 085 merged via PR #154): newest `## VERDICT` header
is 085, `## VERDICT 086` and `## INTAKE 073` collision-grepped clean
(outbox + archives + current-state + sims + remote refs — no competing
branch or PR), so idea-engine PROPOSAL 073 → **VERDICT 086**, the +13
offset's tenth row (map-row extension lands in `docs/current-state.md`
this same PR). Worker session; `control/status.md` and `control/inbox.md`
untouched (ledger appended to `control/outbox.md` only; delivery is the
manager's Q-0264 fan-in). This head is NOT fully hermetic at the harvest
level: the committed constants carry file:line pins into
menno420/superbot-mineverse @ b9ade33 (docs/mining-write-contract.md
:164-165, tests/shim/shim_bot.py:29/:115/:340-366) and an executor-unbuilt
pin into menno420/superbot @ f8e2313 — ALL re-verified FIRSTHAND this
slice on read-only shallow clones (both clones landed at exactly the
pinned HEADs; every quoted line matched verbatim; zero harvest anomalies)
BEFORE the fixture was written; the runner itself is hermetic (reads only
its own fixtures.json). This slice worked from a NEW fresh shallow clone
(`sim-lab-v086`) and pushes from there (the V080–V085
fresh-clone-on-dirty-tree guard, carried). This card held the substrate
gate red deliberately until the flip (the born-red discipline — the
designed hold was the only red this branch produced itself).

## What happened

Built `sims/verdict-086-write-contract-rate-tier-degeneracy/` under the
standing discipline: fixtures.json committed BEFORE the runner (card
66a17b4 → fixtures 455c93a → runner b8adf5c → accepted run 54e986e →
control appends + map row 2f638d8), three-arm: Arm A seedless
closed-form exact maxima (N_slide = B·⌈L/w⌉, N_fixed_adv =
B·(⌈(L−δ)/w⌉+1), N_fixed_aligned = B·L/w for w | L, N_bucket =
B + ⌊(L/δ−1)·(B/w)·δ⌋) + the dead-tier invariant + the redundancy law +
the separating triple (decision-bearing); Arm B INDEPENDENTLY-WRITTEN
twin — greedy schedule witnesses with matching combinatorial upper
bounds (partition / token conservation), explicit alignment enumeration,
exhaustive small-world searches ((6,2,2)/(7,3,2)/(5,5,3)/(8,4,1)/(9,3,3)
plus the 3⁴ pencil world), its own two-bucket min-level trace plus a
scaled exhaustive minimizer confirmation, its own separating search —
exact-equal on every number (the second decision evaluator recomputes
from Arm B alone); Arm R seeded Poisson click streams (offered 2/s)
through a VERBATIM re-implementation of the shim's `_consume_budget`,
reporting-only (main 20261650 at 50,000 events, stability 20261651 at
20,000, presentation shuffle 20261652; aux 20261653 asserted never read
— the drafter's registered set IS the session seed set, the V077–V085
precedent; 20261644–649 stays the disclosed in-flight gap, unused;
registry high-water 20261653), plus the DETERMINISTIC obedient
Retry-After client as an F3 gate. 141 self-checks, 141 passed, 0 failed;
exit 0; ~0.3 s/run; byte-identical double run (results f8a2f527…,
run-stdout 83280c95…, sha256 in REPORT.md); CPython 3.11 asserted; no
fix-forwards after the runner landed — the first complete in-repo run is
the accepted run (the committed pipeline was rehearsed to green OUTSIDE
the repo first, the prior sessions' dryrun precedent). PR #155 opened
READY.

**VERDICT 086 — REJECT, all three registered clauses exact, ZERO
anomalies.** R1: the sustained tier never rejects under any uniform
discipline — sliding contact 60 = S, aligned-fixed contact 60 = S (the
61-request probe is rejected by the BURST tier first), sustained-bucket
min level exactly 50 over 600 s (invariant + greedy trace in both arms +
exhaustive scaled-world confirmation). R2: fixed-adversarial 70 = 7/6·S
(×10/9 over the 21/20 band), bucket 69 = 23/20·S (×23/21;
closed-interval exhibit 70 — the pair {69, 70} convention-robust),
straddle 20 = 2B exactly. R3: B·T = S·w = 600 at EQUALITY in the
redundancy law (B·⌈T/w⌉ = 60 = S); the S = 50 witness (six 10-bursts,
60 admits > 50) is burst-sliding feasible; the w = 7 world dies by
divisibility (90 > 60); the S = 70 world carries the third registered
contact (fixed 70 = 70). Granularity triple (60, 70, 69) identical at
δ ∈ {1, 1/2, 1/5} in BOTH arms; grid rows (20,10) → 120/140/138 (every S
live) and (5,10) → 30/35/34 (every S dead); pencil world 4/6/5 with the
exhaustive 3⁴ check. The anomaly census ran honestly and came back
EMPTY: every disclosed numeral — decision AND reporting, including the
seeded Arm-R landing (23270/26730 of 50,000; 9183/10817 of 20,000; both
worst-window contacts exactly 60) and the obedient client's exact
3600/3600 s — reproduced from scratch; the P073 drafter's
NO-DERIVED-LITERALS claim survived zero-trust re-derivation intact. The
one genuinely working committed part stated back to the lane: the shim's
Retry-After formula is an exact sustained-rate governor (an obedient
client self-paces to precisely 1/s).

## Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 085, sim-lab
PR #154): V085's 💡 — GATE THE ARGMIN, NOT JUST THE VALUE (every
extremal claim carries its search domain `over: D` and witness `arg: w`,
and the verdict runner re-runs the search over D and gates the WITNESS)
— was applied LIVE this slice and P073 PASSED it: every extremal claim
in the registration (the four discipline maxima at every L, the grid
rows, the bucket minimum) states its domain (span length × discipline ×
grid cell) and its witness (the burst schedules, the greedy front-load
trace), and Arm B re-ran every search over its stated domain with its
own code (greedy witness + matching upper bound = the exact extremum,
alignment enumerated, small worlds exhausted) — every argmax/witness
matched the drafter's, unlike V085's P072 where the re-search caught
three argmin misattributions. V085's C3 disclosed-anchor convention rode
as this slice's C3 and earned its keep in the NEGATIVE direction: the
census compared six seeded reporting values and four census summaries
against the disclosed landing and found ZERO mismatches — the honest
empty census is itself the V085 precedent honored (the census must be
able to come back empty without being skipped). V084's RAN-vs-DERIVED
provenance was checked at fixture time: P073 tagged every numeral RAN
and the zero-trust re-derivation confirmed all of them. V083's margin
ledger rode as fixture C5 and surfaced this head's distinctive geometry:
FOUR margin-0 cells sit in the decision surface BY REGISTRATION (the
thesis itself), which forced the C5 gate to split must-equal from
must-clear rows (see 💡). The born-red card / collision-grep /
no-claim-file reservation, the registered-allocation-as-session-seed-set
convention, and the fresh-clone-on-dirty-tree guard all rode unchanged.

💡 **Session idea (genuine, this session):** TYPE THE MARGIN-LEDGER ROWS
— MUST-EQUAL vs MUST-CLEAR. V083's ledger convention ("no decision
clause rests on a margin-0 cell") treats margin 0 as a hazard; this head
is the first whose THESIS is margin 0 — four registered contacts
(sliding 60 = S, aligned-fixed 60 = S, the S = 70 world's 70 = 70, the
lattice equality 60 = 60) where the committed constants sit exactly ON
the degeneracy surface. The naive ledger rule would flag the head's own
finding as a defect; dropping the rule would let genuine knife-edge
hazards hide. The fix this slice prototyped (fixture C5): every ledger
row carries a TYPE — **must-clear** rows (unregistered inequalities)
gate margin > 0 and report their clearance (×10/9, ×23/21, +30, +10,
49 tokens), while **must-equal** rows (registered contacts) gate the
EQUALITY two-sided — a nonzero margin in EITHER direction is the
failure, because drift off the contact falsifies the boundary-location
claim itself. The general lesson for the kit: a registration that
claims "the constants sit exactly on a boundary" must register its
contacts as must-equal ledger rows, and the verdict gate must enforce
both row types — margin-0-as-thesis and margin-0-as-hazard are
distinguished by REGISTRATION, not by inspection at verdict time.
Dedup: V083's 💡 created the ledger and its single no-margin-0 gate;
V084's provenance and V085's argmin-witness ideas govern where a
literal came from and which point wins a search — none types the
ledger's rows, and none states the two-sided equality gate for
registered contacts (this slice's C5 handling of the four contacts is
the prototype; P073's margin-ledger paragraph registered the contacts
as knife-edges but the row-typing rule is new here).

📊 Model: Claude Fable family · high · verdict-sim slice-worker session

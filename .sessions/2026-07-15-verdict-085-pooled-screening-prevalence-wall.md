# Session — VERDICT 085 — the pool test is not free: Dorfman batched screening has an exact prevalence wall (p* = 1 − 3^(−1/3) ≈ 0.3066) above which every batch size loses to one-at-a-time, and the cautious pair-pool is dominated everywhere (idea-engine PROPOSAL 072, the round-14 UNRELATED rotation slot, combinatorial group testing; P072 → V085 under the +13 offset)

> **Status:** `complete`
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 085 for idea-engine PROPOSAL 072 (the
pooled-screening prevalence wall,
`ideas/fleet/pooled-screening-prevalence-wall-2026-07-15.md`, read at
idea-engine origin/main, landed via idea-engine PR #436 merged
2026-07-15T09:19:39Z, head 4d1b86b; outbox block stamped
2026-07-15T09:15:21Z; grounding pin idea-engine e17ebe7). One slice,
one branch (`claude/2026-07-15-verdict-085-pooled-screening-prevalence-wall`),
one verdict. NUMBERING, verified literally at sim-lab origin/main
`237b24a` (VERDICT 084 merged via PR #153): newest `## VERDICT` header
is 084, `## VERDICT 085` and `## INTAKE 072` collision-grepped clean
(outbox + archives + current-state + sims + remote refs — no competing
branch or PR), so idea-engine PROPOSAL 072 → **VERDICT 085**, the +13
offset's ninth row (map-row extension lands in `docs/current-state.md`
this same PR). Worker session; `control/status.md` and `control/inbox.md`
untouched (ledger appended to `control/outbox.md` only; delivery is the
manager's Q-0264 fan-in). This head is FULLY HERMETIC (the P017–P071
precedent): every model constant is invented-but-pinned in the proposal
block — there is no external repo to re-verify, the whole world is the
pinned cost law T(n, p) = 1/n + 1 − (1 − p)^n and its committed grids —
so the fixture-write copied the registration verbatim and the runner
re-derives the entire surface from scratch. This slice worked from a NEW
fresh shallow clone (`sim-lab-v085`) and pushes from there (the
V080–V084 fresh-clone-on-dirty-tree guard, carried). This card held the
substrate gate red deliberately until the flip (the born-red discipline
— the designed hold is the only red this branch produces itself).

## What happened

Built `sims/verdict-085-pooled-screening-prevalence-wall/` under the
standing discipline: fixtures.json committed BEFORE the runner (card
744038b → fixtures 8dcb03b → runner 657fba4 → accepted run d372c64 →
control appends 34930ca), three-arm: Arm A seedless closed-form exact
T(n, p) census over the 12 × 64 grid + the integer-power wall certificate
(3²>2³, 3⁴>4³, 3⁵>5³, 2⁴=4², (n+1)^n < n^(n+1) for n ∈ {3..64}) + the
T2/T3 polynomial identities by exact coefficient match AND 102-point grid
enumeration + optimal-n* search (decision-bearing); Arm B
independently-written binomial outcome-tree recomputation of T with its
OWN n* search and its OWN wall check (q^n vs 1/n directly, no certificate
reuse), exact-equal on every rational on the whole grid (the second
decision evaluator recomputes from Arm B alone); Arm R seeded
Monte-Carlo screening careers at (p, n) ∈ {(1/100, 11), (1/10, 4),
(2/5, 3)}, reporting-only (main 20261640 at N = 100,000, stability
20261641 at N = 40,000, presentation shuffle 20261642; aux 20261643
asserted never read — the drafter's registered set IS the session seed
set, the V077–V084 precedent; 20261634–639 stays the disclosed in-flight
gap, unused; registry high-water 20261643). 1607 self-checks, 1607
passed, 0 failed — NO sim self-check is designed to fail (the three
above-wall slips are anomalies via C3, not gate failures); exit 0;
~1.2 s/run; byte-identical double run (results 66e6e1f3…, run-stdout
d261168e…, sha256 in REPORT.md); CPython 3.11 asserted; no fix-forwards
after the runner landed — the first complete in-repo run is the accepted
run. PR #154 opened READY.

**VERDICT 085 — REJECT, all three registered clauses exact, with THREE
named anomalies (one family, all reporting-side, ruling untouched).** The
wall is real: pooling helps iff 3q³ > 1 iff p < p* = 1 − 3^(−1/3) ≈
0.306566 (integer-power certified, argmin n^(−1/n) = 3), matching the
grid scan at every prevalence (helps {1/100…3/10}, fails {1/3, 2/5, 1/2,
2/3, 9/10}). R1 at p = 2/5: strict wall T(n) > 1 for every n ∈ {2..64}
AND practical min ≥ 21/20 (true min T(8, 2/5) = 3463137/3125000 ≈ 1.1082,
margin ×1.0554). R2: the identity holds by exact coefficient match, floor
1/54 at q = 2/3 only. R3: T*(1/100) = 21512792031541191037911/1100…000
≈ 0.195571 ≤ 1/4 at n* = 11 (×1.2783). The falsifiability world (delete
the 1/n term) verifiably flips to APPROVE (min T̃ = 0.64 at p = 2/5), and
the p = 3/10 straddle (T(3) = 2971/3000 < 1) helps one grid step below
the wall — both non-REJECT rulings genuinely reachable. **The anomalies,
all one family (an argmin conflation), none touching a decision clause's
truth:** A1 — the disclosed practical-grid min "419/375 at n = 3" is
wrong; the TRUE min over {2..8} at p = 2/5 is T(8, 2/5) at n = 8, because
above the wall T(n, 2/5) = 1/n + 1 − (3/5)^n descends toward 1⁺ as n
grows (the 1/n term dominates the vanishing (3/5)^n), so the pool-grid
minimum sits at the LARGEST n, not the wall-optimal n = 3 (a DIFFERENT
optimization); the R1 damage clause still fires on the true min. A2 —
"min over {2..64} at p = 1/3 = 28/27 at n = 3" is the same slip; the true
grid min is at n = 64 ≈ 1.015625 (28/27 is the n = 3 LOCAL min, correct as
such); pure reporting, no clause reads it. A3 — "the best batch above the
wall wastes 11.7%" inherits A1: the best practical batch (n = 8) wastes
10.82%. The proposal's Q8 anticipated exactly this ("the more interesting
outcome — DISAGREES and pins the drafter's error, which the pre-registered
rule then rules on honestly"); the wall theorem itself (n = 3 minimizes
n^(−1/n)) is CORRECT and gated green — the census anchors misapplied it to
a fixed-prevalence pool-grid minimization.

## Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 084, sim-lab
PR #153): V084's 💡 — NO DERIVED LITERALS (tag every registration numeral
RAN vs DERIVED; the verdict runner gates RAN mismatches and treats
DERIVED mismatches as expected-correction rows) — was checked LIVE this
slice and found necessary but NOT sufficient for P072's failure mode.
P072's drafter RAN everything (the V080 lesson honored — the twin
agreement on the 12 × 64 grid, both identities, all seven helping-cell
census anchors, the F4 pencil world, the three REJECT margins all
reproduced exactly), and the anomalies are NOT DERIVED-from-a-limit slips
(the V084 family): 419/375 IS exactly T(3, 2/5), a RAN number — the
defect is that it was attached to the wrong CLAIM ("it's the min over
{2..8}") when the argmin is elsewhere. A pure RAN/DERIVED provenance tag
passes this literal (it was run) and a pure value-gate passes it
(419/375 = T(3, 2/5) exactly) — the mismatch is only visible if the
runner re-runs the EXTREMAL SEARCH over the stated domain, which this
slice did (C3 disclosed-anchor comparison re-derives every above-wall
summary). V083's MARGIN-LEDGER convention rode as fixture C5 and earned
its loop: it surfaced that the R1 damage margin is ×1.0554 on the TRUE
min (not the disclosed ×1.0641) and that no decision clause rests on the
two registered knife-edges (R2's q = 2/3 equality, T3's q² = 1/2 zero).
V081's ESTIMAND and V082's DISPERSION conventions were checked at fixture
time: Arm R's estimand (mean tests/item) and draw discipline (n
Bernoulli/pool) are pinned in the fixture, and P072 carries no
measured-mean anchors (its constants are exact rationals, dispersion-free
— Arm R is reporting-only with no gate). The born-red card /
collision-grep / no-claim-file reservation, the registered-allocation-
as-session-seed-set, and the fresh-clone-on-dirty-tree guard all rode
unchanged.

💡 **Session idea (genuine, this session):** GATE THE ARGMIN, NOT JUST
THE VALUE — every EXTREMAL claim a registration makes ("the min / max /
best / worst / only X over domain D is v") must carry its search DOMAIN
`over: D` and its witness `arg: w`, and the verdict runner must RE-RUN the
search over D and gate the WITNESS (argmin/argmax/the satisfying set),
not merely check that v is the stated value. The evidence from this slice
is decisive: P072's drafter ran a correct VALUE (419/375 = T(3, 2/5)
exactly, a genuine RAN literal) but attached it to a false SELECTION
CLAIM ("the min over {2..8}") — three times, one family (A1/A2/A3), each
because above the wall the pool-grid minimum sits at the largest n while
the drafter reported the wall-optimal n = 3 (the argmin of a DIFFERENT
functional, n^(−1/n)). This is a NEW failure class, orthogonal to the
prior six 💡: V078's self-evaluating inline arithmetic (prose consistency
of stated arithmetic), V079's machine-readable disclosed VALUES (anchor
FORMAT), V080's executable theorem CLAIMS (theorems enumeration-verified
— P072 complied here, its theorems are all green), V081's ESTIMAND pins,
V082's DISPERSION pins, V083's MARGIN ledgers (where a claim sits in the
decision geometry), and V084's RAN-vs-DERIVED PROVENANCE (which passes a
RAN literal at the wrong argmin). Those govern arithmetic, format,
theorem-claims, estimands, moments, geometry, and provenance; NONE gates
the SELECTION SEMANTICS of an extremum — a value-correct, provenance-clean
literal can still name the wrong argmin, and only a domain-scoped
re-search catches it. Concretely for the kit: the proposal template's
census/anchor lines gain an `over:`/`arg:` pair on every extremal claim,
and the verdict fixture convention inherits it so an argmin mismatch with
a value match is born a first-class "extremal-misattribution" anomaly
(this slice's C3 handling of A1/A2/A3 is the prototype). Dedup: distinct
from V084's provenance idea precisely because the literal here IS RAN and
value-correct — the routing is not gate-vs-correct by provenance but
re-search-the-domain by claim type.

📊 Model: Claude Fable family · high · verdict-sim slice-worker session

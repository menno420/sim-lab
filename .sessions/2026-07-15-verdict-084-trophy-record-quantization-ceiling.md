# Session — VERDICT 084 — the personal best is a finite resource: the committed 2-decimal weight grid caps every species' trophy ladder, the modal chase provably completes in ~148 casts, and no committed knob can extend it (idea-engine PROPOSAL 071, the round-14 GAME rotation slot, superbot hub fishing; P071 → V084 under the +13 offset)

> **Status:** `complete`
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 084 for idea-engine PROPOSAL 071 (the
fishing trophy-record quantization ceiling,
`ideas/superbot/fishing-trophy-record-quantization-ceiling-2026-07-15.md`,
read at idea-engine origin/main `e17ebe7`, landed via idea-engine PR #435
merged 2026-07-15T08:55:30Z; outbox block stamped 2026-07-15T08:52:10Z in
the LIVE `control/outbox.md`; grounding pin superbot
`f8e2313a087e18cb32e88269d468b0b30a41fad9`). One slice, one branch
(`claude/2026-07-15-verdict-084-trophy-record-quantization-ceiling`),
one verdict. NUMBERING, verified literally at sim-lab origin/main
`bf398f9` (VERDICT 083 merged via PR #152): newest `## VERDICT` header is
083, `## VERDICT 084` and `## INTAKE 071` collision-grepped clean
(outbox + archives + current-state + sims + remote refs — no competing
branch or PR), so idea-engine PROPOSAL 071 → **VERDICT 084**, the +13
offset's eighth row (map row extension lands in `docs/current-state.md`
this same PR). Worker session; `control/status.md` and
`control/inbox.md` untouched (ledger appended to `control/outbox.md`
only; delivery is the manager's Q-0264 fan-in). Committed constants
re-verified FIRSTHAND at superbot `f8e2313` (read-only shallow fetch of
exactly that pin) this session BEFORE fixture-writing:
`disbot/utils/fishing/weight.py` (_BASE 0.18 / _EXP 1.65 / _SPREAD
0.65–1.55, `nominal = round(_BASE * rank**_EXP, 2)`, `roll = max(0.01,
round(nominal * r.uniform(0.65, 1.55), 2))`, the retention-hook header
sentences verbatim), `fishing_workflow.py:267` strictly-greater PB
compare, `rewards.py:48` the single `roll_weight` call site + the
`rank**(-1/pull)` mix law at line 46, ROD_LADDER pulls
1.00/1.10/1.25/1.45/1.70, weather rarity_mult 1.0/1.0/1.08/1.12/1.30,
FISH_PER_LEVEL 3 / MAX_LEVEL 7 / band = 3·level clamped, fish.json 21
shore ranks 1..21 + 11 deepwater rows, the pinned 21 nominals against
the formula, `db/games/fishing.py` GREATEST + "strictly less" docstring,
the design-doc "🏅 New personal best!"/"long-tail" sentences, the
bait/gear/venue zero-`weight`-hits negative, AND the n3 display probe
(`views/fishing/menu.py:106` renders `{best:g}kg` — 6 significant
digits, never coarser than the 2-dp storage grid) — ALL MATCHED, zero
harvest anomalies. The runner is hermetic (reads only its committed
fixtures.json, zero repo/network reads at verdict time); the DECISION
arms are seedless exact rationals. The V080–V083 dirty-worktree guard
fired again at session start (the local sim-lab tree carried a prior
worker's uncommitted `.substrate/guard-fires.jsonl` plus a stray
verdict-078 `__pycache__/`, parked on the verdict-080 branch), so this
slice worked from a NEW fresh shallow clone (`sim-lab-v084`) and pushes
from there. This card holds the substrate gate red deliberately until
the flip (the born-red discipline — the designed hold is the only red
this branch produces itself).

## What happened

Built `sims/verdict-084-trophy-record-quantization-ceiling/` under the
standing discipline: fixtures.json committed BEFORE the runner (card
ec202bb → fixtures 92fcff4 → runner 1c7a145 → accepted run 0371703 →
control appends 3cc3f70), four-arm: Arm A seedless closed-form interval
census + suffix-sum record laws (exact Fractions over all 21 ranks +
hand world + refinement grids; decision-bearing), Arm B
independently-written boundary-sweep census + explicit t-DP twin
(exact-equal on every registered rational, in memory — the >4300-digit
large-rank E_life rationals gated without printing, per the drafter's
disclosed print hazard and fixture C9; the second decision evaluator
recomputes from Arm B alone), Arm F the committed roll re-implemented
verbatim (float round + random.uniform, seed 20261630; support equality
GATED green on ranks {1, 2, 3, 21} at 400k draws — the n2 float axis
disarmed by measurement), Arm R seeded career traces at the decision
cell, reporting-only (2,000 × 2,000-cast careers @ 20261631, 500
stability @ 20261632; aux 20261633 asserted never read — the drafter's
registered allocation IS the session seed set, the V077–V083 precedent;
the 20261624–629 gap stays the drafter's disclosed buffer, unused;
registry high-water 20261633). 323 self-checks, 322 passed, 1 failed —
the single failure is the DESIGNED C12 strict-reading refinement leg,
pre-disclosed in fixtures before the runner existed; exit 0 under the
disclosed exit contract; ~21 s/run; byte-identical double run (sha256
in REPORT.md); CPython 3.11 asserted; no fix-forwards after the runner
landed — the first complete in-repo run is the accepted run. PR #153
opened READY.

**VERDICT 084 — REJECT, all three registered clauses exact at the
decision cell, with TWO named anomalies (the streak of zero-anomaly
heads ends honestly at three).** The minnow — modal at every committed
cell, L1-gated — has exactly 17 possible weights (4/81 + 15 × 5/81 +
2/81), a reachable ceiling at 2/81 (kill horizon 1527502293/10346336 ≈
147.64 casts; onboarding ≈ 74.25), E[lifetime PBs] =
11736310749428605/3026966925030048 ≈ 3.8773 ≤ 4, and strict sub-1/t
cadence for every t ∈ 2..50 (P(PB at 2) = 3083/6561 ≈ 0.46990). Career
total ≈ 153.3824 vs the divergent continuous benchmark (99.2 @ 2,000,
181.4 @ 100,000). The anomalies, both drafter hand-slips of one ln-10
family, neither touching a decision number: **A1** — the registered
refinement band (ln 10 ± 1/10 per grid decade) MISSES decade 1 (exact
2.176943, off 0.1256): at 3 dp the support edges 0.117 = N·13/20 and
0.279 = N·31/20 land ON-GRID, restructuring both edge atoms to exact
half-cells — a one-time correction; decade 2 = 2.299806 lands inside at
0.0028; the lemma's direction stands; applied as registered under the
C12 strict reading (disclosed with the pre-verified miss IN the fixture,
before the runner) and per the registered REJECT-first order the ruling
is untouched. **A2** — the disclosed APPROVE-world horizon "≈ 1,480
casts" is the naive ×10 scaling; the exact 3-dp re-census gives
p_ceiling = 1/324 (0.279 on-grid halves the top cell) → horizon 1181.10
casts; the one-character APPROVE flip SURVIVES (163 rungs ≥ 100,
1181.10 ≥ 1000) — wrong number, right conclusion; same family's
"+2.3/species (+48 total)" corrects to +2.1836 (+45.856). The scrutiny
findings the slice was asked for: the C5 band-margin ledger (no clause
margin-0; the E_life clause is the thinnest at 0.12275 = 3.1%) and the
species sweep — rank 1 is the ONLY species inside the REJECT bands
(rank 2: 52 rungs, E_life ≈ 5.099), so the REJECT is modal-species-
specific and rides entirely on the L1 gate, named for the manager
beside the recommendation.

## Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 083, sim-lab
PR #152): V083's 💡 — MARGIN LEDGERS, NOT KNIFE-EDGE EXCEPTIONS (a
registration's fragility surface must be enumerated by predicate over
the whole decision geometry, with a gate that no decision clause,
witness, or recommendation leg rests on a margin-0 cell) — was applied
LIVE this slice as fixture convention C5: P071 registered no knife-edge
exclusion at all, so the predicate was keyed to this head's geometry
(exact clause-to-band margins + the per-species band sweep), and it
EARNED ITS LOOP: it surfaced that the E_life clause clears by only
3.1% and that rank 1 is the only species inside the REJECT bands — the
fragility axis (L1-dependence) now named beside the recommendation
rather than implicit. V081's ESTIMAND-pin and V082's DISPERSION-WITNESS
conventions were checked at fixture time: Arm R's estimand and draw
discipline are pinned in the fixture (arm_r block), and P071 carries no
measured-mean anchors (its committed constants are exact code
constants, dispersion-free). One registered-text-wins call made and
disclosed BEFORE the runner (C12): P071's refinement band is ambiguous
between per-decade-strict and two-decade-average readings; the strict
reading was pinned, the average published as reporting — and the strict
leg failed as pre-verified, logged first-class (A1), ruling untouched
per the registered REJECT-first order. V083's other carried conventions
(born-red card / collision-grep / no-claim-file reservation;
registered-allocation-as-session-seed-set; fresh-clone-on-dirty-
worktree) rode unchanged; the dirty-worktree guard fired for the fifth
slice running.

💡 **Session idea (genuine, this session):** NO DERIVED LITERALS —
tag every numeric literal a registration writes down with its
provenance, RAN (came out of an executed computation at the registered
cell) or DERIVED (scaled/estimated from a law), and make the verdict
runner treat RAN mismatches as gate failures but DERIVED mismatches as
expected-correction rows. The evidence from this slice is clean: P071's
drafter ran the decision numbers live (the V080 lesson, honored — all
of them reproduced exactly, 17 rungs / 2/81 / the 16-digit E_life
rational / the kill identity), but two registration numbers were
DERIVED from asymptotic scaling instead of run — the refinement band
(ln 10 ± 1/10, ignoring the first decade's lawful edge-restructuring
correction of −0.126) and the APPROVE-world horizon (~1,480 from the
naive ×10 of p_ceiling, vs 1181.10 from the actual 3-dp census where
0.279 lands on-grid) — and BOTH failed to reproduce while 100% of the
RAN literals held. Hand-derivation from a limit law is a different
failure class from a typo: it fails in a correlated family (every
number sharing the scaling assumption breaks together, as here), and a
provenance tag lets the runner route the family correctly (re-derive
and correct, don't gate) instead of the drafter guessing tolerance
bands around limits. Dedup: distinct from V078's 💡 (self-evaluating
inline arithmetic — prose consistency of stated arithmetic), V079's
(machine-readable disclosed VALUES — the format of anchors), V080's
(executable theorem CLAIMS — theorems must be enumeration-verified at
drafting; P071 complied for theorems and still shipped two derived
non-theorem literals), V081's (ESTIMAND pins), V082's (DISPERSION
pins), and V083's (MARGIN ledgers — where claims may sit in the
decision geometry): those govern claims, values, symbols, moments, and
geometry; this governs the PROVENANCE of registration numerals and the
verdict-side gate-vs-correct routing. Concretely for the kit: the
proposal template's model/gates sections gain a per-literal `prov:`
tag (RAN cell=… / DERIVED from=…), and the verdict fixture convention
inherits it so a DERIVED mismatch is born an expected-correction row
(this slice's A1/A2 handling is the prototype).

📊 Model: Claude Fable family · high · verdict-sim slice-worker session

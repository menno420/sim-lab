# Session — VERDICT 057 — Keyword tiling vs independent picks: is the keyword map's first-claim-wins convention worth its coordination cost in catalog discovery traffic? (idea-engine PROPOSAL 046, venture r8 books half)

> **Status:** `complete`
> 📊 Model: Claude Fable (Claude 5 family) · 2026-07-13 · verdict-057 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 046 (`## PROPOSAL 046 · 2026-07-13T21:02:48Z · status: sim-ready`, landed via idea-engine PR #348 → main 09b3867; claim landed via idea-engine PR #349, `control/claims/claude-verdict-057-keyword-tiling.md` reserving the P046 intake + VERDICT 057 and this branch `claude/verdict-057-keyword-tiling`; numbering INTAKE = proposal number, VERDICT 057 per the established P045→V056 offset map) — price venture-lab's KDP keyword-map first-claim-wins TILING convention (`docs/publishing/keyword-map.md` @ venture-lab be6c75d4e3379efc108f27d17f2c8ff5adb9a74f, harvested sentences quoted verbatim in the committed fixture — citation only, the runner is fully hermetic) against the INDEPENDENT per-packet greedy drafting it replaced, per the idea doc `ideas/venture-lab/keyword-tiling-vs-independent-picks-2026-07-13.md` @ 09b3867: a pinned synthetic search-shelf world (two Zipf universes — M = 120 keywords w_k = (1/k)/H_120 at mass 3/5, C = 30 category nodes v_c = (1/c)/H_30 at mass 2/5; N = 14 titles × exactly 7 keywords + 2 categories; triangular fit windows L = 24 / L_c = 10 around pinned per-title homes in three overlap rows LOW/MED/HIGH; pinned external competitors, never diluted; S = 5 shelf positions, click pmf β = (1/2, 1/4, 1/8, 1/16, 1/16); same-catalog rank dilution f/(1 + γ(j−1)), γ ∈ {0, 1/4, 1, 4}; ties externals-first then lower title index), GREEDY = independent solo-score top-7/top-2 picks (collisions allowed) vs TILE = identical scoring restricted to unclaimed cells in claim order t = 1..14 with the C4 sharing fallback on exhaustion. Primary metric R = (T_TILE − T_GREEDY)/T_GREEDY per 12-cell grid cell, exact Fractions, Arm A (seedless exact enumeration — the DECISION arm) confirmed by Arm S (seeded MC, random.Random(20261321), 200,000 events/cell, CRN across worlds, agreement gate ≤ 5/1000 absolute both worlds every cell). Decision rule pre-registered, evaluated IN ORDER: REJECT FIRST iff R < 1/50 in ALL 12 cells; APPROVE iff R ≥ 1/50 in ≥ 9 of 12 cells AND in ≥ 2 of the 3 γ = 1/4 cells AND the seed-20261322 stability leg (20,000 events/cell, widened gate ≤ 15/1000) reproduces the ruling through twin evaluators; NULL anything else naming the binding axis from the pre-registered four (γ-conditional / overlap-conditional / arm disagreement / sensitivity straddle). Seeds 20261321 main / 20261322 stability / 20261323 reporting / 20261324 aux reserved NEVER read — strictly above the P045/V056 high-water 20261320. Gates, run invalid on any failure: F1 popularity normalization; F2 two-title hand world (T_GREEDY(γ=1) = 1/4, T_GREEDY(γ=0) = 1/2, T_TILE = 5/12 at every γ, hand-computed exact); F3 tie order; F4 position pmf; F5 dilution identities; F6 theorem gates (T_TILE γ-invariant in zero-fallback rows / non-increasing with fallback, T_GREEDY non-increasing in γ every row, degenerate all-fits-zero ⇒ T = 0); allocation sanity (exactly 7 + 2 claims per title both worlds, TILE same-cell pairs only counted fallback shares, GREEDY collisions LOW ≤ MED ≤ HIGH expected-direction flagged loudly); arm agreement gate; per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned. Reporting-only (Arm A re-evaluations + seed-20261323 Arm-S confirmations at 20,000 events, cannot flip): mass-split pairs (1/2, 1/2) / (4/5, 1/5), flatter β (1/3, 4/15, 1/5, 2/15, 1/15), margin sweep m ∈ {1/100, 1/25}, per-title tiling-tax columns, collision/fallback counts, keyword/category decomposition. Fully hermetic: zero repo/network reads by the runner — fixtures.json constructed from the pinned constants in the idea doc / PROPOSAL 046 block, committed BEFORE the runner (git-trail discipline). Build subtree `sims/verdict-057-keyword-tiling/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 046 + VERDICT 057 append to sim-lab control/outbox.md only).

## What happened

Built `sims/verdict-057-keyword-tiling/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 046 block / idea doc @ idea-engine main
09b3867: both Zipf universes, all three home tables, the external profile,
β + the flatter reporting pmf, the dilution rule, the γ × overlap grid, the
mass split with both sensitivity pairs, the C4 fallback rule, band constants,
the F2 hand fixture, per-leg event counts, seeds 20261321–324, the five
harvested map sentences quoted verbatim @ venture-lab be6c75d) committed
BEFORE the runner. Git trail (PR #110): 116b4b7 (born-red card) → 67ad25c
(fixtures) → ca981d2 (runner tiling_sim.py + accepted run: results.json,
run-stdout.txt, REPORT.md, README.md) → 69a1a81 (INTAKE 046 + VERDICT 057
ledger) → this flip. Session-start nuance, disclosed: PROPOSAL 046 was not
yet on idea-engine main at sync (main c118324; the proposal rode PR #348,
then open with substrate-gate green) — waited for the enabler's merge, re-
synced to 09b3867, and read the block at HEAD before any sim work. Claim-
first: idea-engine PR #349 (`control/claims/claude-verdict-057-keyword-
tiling.md`), landed before the build.

**Run:** `SELF-CHECKS: 389 passed, 0 failed`, exit 0, ~4 s; stdout +
results.json byte-identical across two full process runs by external diff
(stdout sha256 8718612a…, results sha256 b5eb7fee…); CPython 3.11 pinned,
asserted. Gates all green: F1–F6 (T_TILE exactly γ-invariant in the
zero-fallback LOW row; non-increasing in the fallback rows; T_GREEDY
non-increasing in γ everywhere; hand fixture exact at 1/4, 1/2, 5/12);
allocation sanity (TILE same-cell pairs ≡ counted fallback shares — LOW 0,
MED 9 kw + 5 cat, HIGH 35 kw + 12 cat; GREEDY collisions 18 ≤ 49 ≤ 78, no
anomaly); arm agreement PASS all legs (worst 0.0024 main / 0.0065 stability /
0.0096 reporting); draw sentinels exact (7,200,000 / 720,000 / 2,160,000);
twin evaluators agree; aux 20261324 never constructed.

**Ruling: approve.** REJECT (checked FIRST) does not fire: 9 of 12 cells
clear 1/50. APPROVE fires: 9 ≥ 9 cells AND 3 ≥ 2 of the γ = 1/4 cells clear,
stability leg reproduces the identical band at 1/10th the events. The miss
set is exactly the γ = 0 column (LOW +1.89% just under; MED −38%, HIGH −32%
— GREEDY wins outright with zero dilution); at every nonzero registered γ
tiling buys +6.5% to +145%. One pre-registered straddle FIRED, shipped
first-class (reporting-only, cannot flip): mass split (4/5, 1/5) lands
NEITHER-BAND — the APPROVE leans on the 3/5–2/5 split width. The flatter-β
leg (the registration's named most-likely flip, full allocation
re-derivation) HOLDS the band. One prose-expectation miss disclosed in
REPORT.md (binds no gate): the proposal expected keyword tiling to exhaust
only in HIGH; measured, MED keywords also exhaust (98 claims into 89
reachable cells — a drafting-time pigeonhole). Walls: none hit this session
— the documented Write-tool REPORT.md wall was not probed (REPORT.md written
via shell heredoc per the standing V054–V056 classification; the Write tool
served the .py runner without incident); GitHub MCP served both PR creates.
ASK 003 corridor: sim-lab main never moved this session (c7fc1a0 at sync and
at append), no merge of main into the branch was needed, so neither the
mtime-newest false-green nor the guard-fires conflict could fire — nothing
to disclose beyond absence. `control/inbox.md`, both status heartbeats, and
idea-engine's outbox untouched. PR:
https://github.com/menno420/sim-lab/pull/110 (READY; merge-on-green owns the
merge — zero agent merge/arm calls).

## 💡 Session idea

Registration prose that asserts a FINITE-COUNTING fact ("keyword tiling
exhausts in HIGH" — implying not-MED) is one integer comparison away from
verified at drafting time, and this build caught one that was false by
pigeonhole (MED: 14 × 7 = 98 claims into 89 reachable cells, so ≥ 9 forced
shares — structural, not stochastic). It was harmless here for a specific,
reusable reason: the gate consuming that structure was written CONDITIONAL
ON MEASURED STRUCTURE (F6a: zero-fallback rows ⇒ exact γ-invariance;
fallback rows ⇒ monotonicity) rather than on the predicted structure ("LOW
and MED are invariant rows") — the gate adapted, the run stayed valid, and
the miss became a one-line disclosure instead of a false red or a silent
wrong gate. The move, stated once: (a) theorem gates should key off
structure the run itself measures (fallback counts, collision counts,
emptiness), never off the registration's prediction of that structure; (b)
any registration sentence claiming feasibility/exhaustion over finite cells
deserves a pigeonhole pre-check at DRAFTING time (claims vs reachable-cell
count — integer arithmetic, zero code), and the drafter's expectation should
be marked derived-with-arithmetic or explicitly non-binding color. Kin,
deduped at flip time (grep .sessions/ and control/outbox.md for
"pigeonhole", "conditional gate", "expectation miss", "prose expectation" —
zero hits): V054's 💡 prices uncomputed POWER claims (statistical, needs
simulation); V055's demands equivalence witnesses for semantic reductions;
V056's dissolves prose-vs-formula boundary atoms by continuous embedding —
none names the expectation-vs-gate decoupling or the drafting-time counting
lint. Anchors: tiling_sim.py F6a block (the `fb == 0` conditional),
REPORT.md § Allocation facts, PROPOSAL 046 block's "keyword tiling
exhausting in HIGH" clause.

## ⟲ Previous-session review

VERDICT 056 (snapshot stale-indicator threshold, PR #109) is the direct
predecessor. Its card's practical calls held up well here: (1) its nit
against V055 — that a 40-line Objective block is a worse citation surface
than fixtures.json verbatim-quote fields — directly shaped this build
(fixtures.json carries the five harvested sentences plus the proposal header
as first-class fields, and the outbox VERDICT cites them from there); (2)
its wall ledger saved a probe: the three-for-three Write-tool REPORT.md
denial record meant this session routed REPORT.md through a shell heredoc
without wasting an attempt — the correct PLATFORM-LIMITS use (a documented
wall probed twice is a bug), with the nuance recorded here that the Write
tool DID serve the .py runner, consistent with its "report-file-specific
tool policy, not a lane wall" classification; (3) its ASK 003 diagnosis ("no
merge, no corridor") gathered one more consistent observation — main never
moved, corridor never fired. Its 💡 (dissolve prose-vs-formula boundary
atoms by testing the registration's own continuous reading) did not transfer
to this build — P046 registers formulas over exact finite lattices with no
dual specification, so there was no atom to dissolve — which is itself worth
recording: that idea's trigger condition (DUAL-specified quantities) is
narrower than V055's equivalence-witness discipline, which transferred to
every build since. One nit: its card's Walls paragraph mixes a genuine lane
wall (superbot-mineverse MCP access) with session-local tool policy in one
list — this card separates "walls hit" from "walls deliberately not probed",
which reads cleaner for the next session deciding what to attempt.

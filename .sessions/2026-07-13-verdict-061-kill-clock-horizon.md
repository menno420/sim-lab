# Session — VERDICT 061 — Kill-clock horizon: is the products lane's shipped T+14 zero-sale kill clock right-sized against its own two other committed clock values (T+7, T+30) on proven-product throughput? (idea-engine PROPOSAL 050, venture r9 products half)

> **Status:** complete
> 📊 Model: Claude Fable (family) · 2026-07-13 · verdict-061 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 050 (`## PROPOSAL 050 · 2026-07-13T23:26:05Z · status: sim-ready`, landed via idea-engine PR #371 → main 3b9b26ca9a8a5faef52bef0750a2b691d56a031e; claim landed via idea-engine PR #372, `control/claims/2026-07-13-verdict-061.md` @ main 2089860 reserving the P050 intake + VERDICT 061 and this branch `claude/verdict-061-kill-clock`; numbering INTAKE = proposal number, VERDICT 061 per the established P049→V060 offset map) — price the venture products lane's shipped T+14 zero-sale kill clock against the lane's own two OTHER committed clock values (the T+7 checkpoint and the 30-day signal window) as a censored-observation renewal problem, per the idea doc `ideas/venture-lab/kill-clock-horizon-2026-07-13.md` @ idea-engine main 3b9b26c. Pinned model: time in whole days, ONE experimental slot, horizon H = 90 slot-days; each launched product draws true per-day organic-sale probability p i.i.d. from the cell prior over P = {0, 1/60, 1/30, 1/14, 1/7}; priors SKEPTIC (3/4, 1/10, 3/40, 1/20, 1/40) / NEUTRAL (1/2, 1/8, 1/8, 1/8, 1/8) / HOPEFUL (1/4, 1/4, 1/4, 3/20, 1/10); build downtime B ∈ {2, 5, 10}; 9 cells = prior × B in pinned order (SKEPTIC, NEUTRAL, HOPEFUL) × (B = 2, 5, 10); policy KILL@T for T ∈ {7, 14, 30}: first sale on day x ≤ T → graduation (slot freed, B build days, fresh draw), zero sales through day T → kill (B build days, fresh draw), live-at-horizon contributes nothing; G(cell, T) = expected graduations in H slot-days, EXACT. Arm A = DECISION (seedless exact fractions.Fraction renewal DP, the ruling rides it alone); Arm S = confirmation (seeded MC, N = 200,000 per (cell, clock) via random.Random(20261337), pinned cell/clock order, pinned draw order p-then-daily-trials; gate |ArmS − ArmA| ≤ 3/200 absolute per leg AND ≥ 4·SE headroom asserted, any breach invalidating the run). Seeds 20261337 main / 20261338 stability (20,000 traj, widened gate ≤ 3/50, twin evaluators must reproduce the ruling) / 20261339 reporting-only legs / 20261340 aux (never read by any decision number) — the ONLY four, pre-registered, strictly above the P049/V060 high-water 20261336. Decision rule pre-registered, evaluated IN ORDER (margin m = 1/20 exact): (1) REJECT FIRST iff D(cell) = (max_T G − G(14))/G(14) ≥ 1/20 in ≥ 7 of 9 cells AND dir agreeing (all SHORTER or all LONGER) in every such cell; (2) APPROVE iff D < 1/20 in ≥ 7 of 9 cells AND in ≥ 2 of 3 SKEPTIC cells AND the stability leg reproduces; (3) NULL otherwise, five registered axes (direction-straddle / build-cost-conditional / margin-thin under m ∈ {1/50, 1/10} / arm disagreement / sensitivity straddle — reporting legs never flip). Gates F1–F5 (pmf normalization; p = 0 / p = 1 point-mass identities with (30, 15, 9) at H = 90; truncated-geometric identity + monotone-in-T; hand world H = 6, B = 1, T = 2, p = 1/2 ⇒ G = 31/16 via the pinned chain; G non-increasing in B, all-dead exact zeros with kills ≡ renewals, slot-day accounting identity = H exact) + draw-count sentinels + twin evaluators + two-process byte identity by external sha256 + CPython minor pinned. Reporting-only: full 9 × 3 G table with D + directions, kills / idle days / wasted graduations per cell, per-p conditional graduation split, H ∈ {60, 180}, grid P′ = {0, 1/90, 1/45, 1/21, 1/10}, graduation-blocks-slot world, margin sweep m ∈ {1/50, 1/10}. Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): APPROVE thinly — D = 0 in 5/9, SKEPTIC/B=2 ≈ 0.0440 SHORTER, NEUTRAL/B=2 ≈ 0.0699 SHORTER (only over-margin cell), HOPEFUL/B=2 ≈ 0.0036 SHORTER, HOPEFUL/B=10 ≈ 0.0482 LONGER. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); the harvested kill-clock/evidence lines carry their DOUBLE pin (venture-lab be6c75d via idea-engine outbox 763b19e) and the quoted access denial — P050 is hermetic-by-registration, no venture-lab read attempted. Build subtree `sims/verdict-061-kill-clock-horizon/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 050 + VERDICT 061 appended to sim-lab `control/outbox.md` only).

## What happened

Built `sims/verdict-061-kill-clock-horizon/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 050 block / idea doc @
idea-engine main 3b9b26c, the harvested kill-clock/evidence lines quoted
with their double pin be6c75d-via-763b19e and the drafting-time access
denial; hermetic by registration — zero repo/network reads at verdict time,
no venture-lab read attempted, deny-wins) committed BEFORE the runner. Git
trail (PR #119): f959b1a (born-red card) -> f8e702a (fixtures) -> 932eca9
(runner kill_clock_sim.py + accepted run: results.json, run-stdout.txt,
README.md) -> 3ec5ee7 (INTAKE 050 + VERDICT 061 ledger + REPORT.md) -> this
flip. Claim-first: idea-engine PR #372 (claim @ 2089860), landed before any
sim-lab work.

**Run:** `SELF-CHECKS: 959 passed, 0 failed`, exit 0, ~3m46s/run (~581M RNG
calls, pure CPython); stdout + results.json byte-identical across two full
process runs by external sha256 (run-stdout 239bdb66..., results
97e9aaac...); CPython 3.11 pinned, asserted. Gates all green: transcription
gates exact; F1-F5 (pmf sums; p=0/p=1 point-mass identities incl. (30, 15,
9) at H=90; truncated-geometric identity + monotone-in-T; hand world
31/16 via the pinned chain; B-monotonicity in every world; all-dead zeros
with kills == renewals and the closed-form kill count; slot-day accounting
= H exact on all 27 legs); twin in-process Arm-A computations (scalar DP vs
bookkeeping DP) identical rationals; twin evaluators agree on every table;
Arm S main (seed 20261337, N=200,000/leg) within 3/200 + 4*SE on all 27
legs, worst |dev| 0.005503; draw sentinels exact per leg and per seed
(380,890,538 / 38,085,547 / 162,191,295 / 0 aux — the ONLY four RNGs,
pinned order, new registry high-water 20261340).

**Ruling: null (margin-thin axis).** REJECT (checked FIRST) does not fire
(1 over-margin cell vs 7 required). APPROVE arithmetic FIRES on Arm A
exact numbers (D < 1/20 in 8 of 9 cells, 3/3 SKEPTIC) but its registered
stability conjunct fails: the seed-20261338 leg passes its widened 3/50
agreement gate everywhere, yet the twin evaluators on the 20,000-trajectory
table land over=3/under=6 — the two DISCLOSED near-edge cells (SKEPTIC/B=2
true D 0.043963, HOPEFUL/B=10 true D 0.048155, gaps 0.0060/0.0018 to the
1/20 edge) sit inside MC noise (4*SE up to 0.041). Named axis: the
registered (iii) MARGIN-THIN, with the exact flip boundary m* =
D(SKEPTIC/B=2) = 0.043963... committed as an exact rational; the sweep
straddles it (m=1/50 -> NULL_ARITH with directions straddling, m=1/10 ->
APPROVE_ARITH). Drafter reference reproduced EXACTLY (5 zero-D cells, all
four nonzero cells to 4dp with directions) — no drafter arithmetic error;
the registration's own confirmation machinery declines the thin APPROVE.
The citable sharpening held: T=30 is argmax only in HOPEFUL/B=10, beaten in
the other 8 cells. The NULL was accepted as it landed — no re-roll toward
the disclosed APPROVE; the first complete run of the registered pipeline is
the accepted run.

Walls: none new. REPORT.md rode a shell heredoc per the standing V054-V060
classification (report-file-specific tool policy; fixtures, runner, README,
and this card all went through Write — zero wasted probes). ASK 003
corridor: sim-lab main never moved during the session (6cb58bb at sync, at
the pre-append re-grep, and at flip), so no merge of main into the branch
was needed and the mtime-newest false-green could not fire; local
`check --strict` showed only the born-red HOLD every time. Both collision
greps empty (session start and pre-append, `## INTAKE 050` / `## VERDICT
061` at origin/main 6cb58bb). One preflight disclosure: the idea-engine
clone arrived with kit-telemetry dirt (`.substrate/guard-fires.jsonl`
modified) and the CLAUDE.md preflight hard reset discarded it before a
rescue branch was cut — telemetry-only, never pushed; sim-lab's own
guard-fires dirt was restored before every commit, never staged.
`control/inbox.md`, both status heartbeats, and idea-engine's outbox
untouched. PR: https://github.com/menno420/sim-lab/pull/119 (READY;
merge-on-green owns the merge — zero agent merge/arm calls).

## 💡 Session idea

A registration whose APPROVE conjunct requires an MC stability leg to
reproduce the ruling should DISCLOSE the conjunct's reproduction
probability at drafting time, computed from its own disclosed landing — a
power calculation for the certification step. This session is the proof
case: the drafter disclosed near-edge cells at D = 0.0440 and 0.0482
against the 0.05 margin, and at N = 20,000 the D-hat noise (SE ~ 0.01 per
cell, positively biased by the max in D's numerator) makes P(both cells
stay under the edge AND the 7-of-9 count holds) roughly a coin flip — so
"APPROVE, thinly" was always more likely to land NULL than APPROVE under
its own registered machinery, and that fact was computable BEFORE any code
existed from the four disclosed D values plus the trajectory-SD bound the
registration itself states (SD ~ 0.5-1.5). Disclosing P(reproduce) does
three things: (a) turns the stability N into a designed quantity (pick N
so the conjunct certifies at, say, >= 95% under the disclosed landing)
instead of an inherited constant; (b) makes a thin landing's fragility a
REGISTERED number, so a stability-declined APPROVE reads as the
registration working, not the sim misbehaving; (c) gives the NULL axis its
flip boundary for free (the margin at which P(reproduce) crosses 1/2 —
here just above m* = 0.043963). Kin, deduped at flip time (grep outbox +
.sessions/ for "power", "coin flip", "stability leg"): VERDICT 022's
intake disclosed an AGREEMENT gate as "~1 MC standard error, a coin flip
on noise" and re-read its granularity at intake — a validity-gate fix;
this prices the DECISION-stability conjunct's certification power against
the disclosed landing, a different object (decision conjunct vs validity
gate) with a different remedy (size N or disclose P, at drafting). Anchors:
kill_clock_sim.py stability section; REPORT.md "Stability result"; the
VERDICT 061 gate line's ROBUST clause.

## ⟲ Previous-session review

VERDICT 060 (magnet press-fit band, PR #118) is the direct predecessor. Its
closing nit — prefer class-agnostic "ruling class reproduces through the
twin evaluators" stability forms over bespoke APPROVE-shaped ones — is
exactly the form PROPOSAL 050 registered, and this session shows the nit
was necessary but not sufficient: class-reproduction stability is
well-shaped yet UNDERPOWERED for a thin landing (the conjunct declined an
APPROVE whose arithmetic was correct to 4dp against the drafter), which is
what this session's 💡 prices. Its git-trail discipline (born-red card ->
fixtures -> runner + accepted run, no fix-forwards) transferred verbatim
and made the uncorrupted claim a one-line citation. One honest nit back:
V060's card says its stability leg "reproduces the class at 1/10 the
samples" as evidence of robustness — true there because REJECT cleared its
band by 1.68x, but the phrasing invites reading stability reproduction as
a robustness BONUS rather than a conjunct with its own error rate; V061 is
the counterexample where that error rate bit, on the registration's own
disclosed near-edge numbers.

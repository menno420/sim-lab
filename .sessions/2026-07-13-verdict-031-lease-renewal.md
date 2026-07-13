# Session — VERDICT 031 — lease-renewal claim expiry: pricing V027's routed slice before the kit builds it (idea-engine PROPOSAL 029)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-031 slice-worker session
> Objective: settle idea-engine PROPOSAL 029 (control/outbox.md · 2026-07-13T06:51:49Z · status: sim-ready; idea `ideas/substrate-kit/lease-renewal-claim-expiry-2026-07-13.md` @ idea-engine main 0e168bf, PR #297 — the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, round 4, following round 3's own verdict-opened thread: VERDICT 027 REJECTED silence-keyed claim expiry and routed the lease-renewal `renewed:` slice while its LIMITS line left the mechanism undesigned). Build the fully hermetic pre-registered dual-arm measurement of the renewal-race model: an alive lane holds one work claim H_c = 168 h (decision-binding; H_c ∈ {4, 24} h reporting-only), wakes on deterministic cadence p_w ∈ {2, 12, 24} h, re-stamps `renewed:` each wake EXCEPT an i.i.d. forget w.p. p_f ∈ {0.02, 0.10, 0.25}; with p_d = 0.10 the lane instead dies silent at a uniform wake (p_d NOT a decision axis — T conditions on alive claims, O95 on dead ones, V027's construction); contenders check at Poisson λ_c and take over any claim whose renewal is overdue past θ_r ∈ {6, 12, 24, 48, 72} h; T at the fastest tempo λ_c = 1/4 h⁻¹, O95 at the slowest decision tempo λ_c = 1/12 h⁻¹, the C48 column reporting-only with V027's distribution-free identity restated by citation. 9 decision cells = 3 p_w × 3 p_f, 45 decision points. Arm A exact and seedless (T by finite DP over the ≤ 84-wake lattice — a run of j consecutive forgets exposes (j·p_w − θ_r)⁺ hours, P(takeover) = 1 − E[exp(−λ_c·total exposure)]; O95 by the exact mixture quantile of (θ_r − A)⁺ + Exp(λ_c) with A the lattice-valued renewal age at death); Arm S seeded event-driven MC (M_S = 4,000 per point, seed 20260756, pinned loop order; gates pre-checked at ≥ 2.5σ of the registered-M_S estimators BEFORE any run — the V027 pipeline lesson as a design rule; stability leg seed 20260757 M_S = 1,000 must reproduce the ruling; reporting-only legs seed 20260758 — wake jitter, H_c ∈ {4, 24}, p_d ∈ {0.02, 0.30}, the C48 column, the empirical-anchor leg at the two quoted measured multisets (11 claim lifetimes median 2.65 h, 19 heartbeat gaps median 1.08 h); aux stream seed 20260759 never read by any decision number; seeds 20260756–59 strictly above the P027 high-water 20260755). CHAINED ANCHOR: a silence-keyed baseline leg re-computes V027's committed exact closed form at V027's committed regime constants and must reproduce its committed Feas map EXACTLY ({R1-C4, R1-C12, R2-C12}, θ* = {48, 24, 72}, no others). Bands inherited VERBATIM from V027: Feas(cell) = {θ_r : T ≤ 0.05 AND O95 ≤ 120 h}. Decision (registered order, REJECT first): REJECT iff Feas = ∅ in ≥ 5/9 cells; APPROVE iff ∃ single θ_r† feasible in ≥ 8/9 cells, stability-reproduced (ships the pinned row: θ_r† + compliance floor + wake-cadence requirement + whether the planted WORK_CLAIM_STALE_HOURS = 72 lies at θ_r†); NULL otherwise (flip axis named via per-axis shares and median θ*). Hermetic: every fixture a pinned constant committed with the sim; zero repo/network reads at run time; stdout + results.json byte-identical across two process runs by external diff.

## What happened

Anchor FIRST: before any build, the committed V027 runner was re-run in a
scratchpad copy — exit 0, 4,975,945 self-checks, `results.json`
byte-identical to the committed file at main `fcb39e3`, committed Feas map
confirmed ({R1-C4: {48, 72}, R1-C12: {24, 48, 72}, R2-C12: {72}}, 6/9
infeasible). Then built `sims/verdict-031-lease-renewal/` — stdlib-only
NUMERIC SIMULATION (rung 1), fully hermetic (reads only its own committed
`fixtures.json`, cross-checked at start). Fixtures committed BEFORE the
runner (13 intake-time decisions — most load-bearing the overdue-convention
derivation, the unique reading satisfying both the registered run-exposure
formula and the registered p_f = 0 self-check; 4 hand pins; the ≥ 2.5σ gate
pre-check rule with its breach protocol pinned before any draw); one
pre-runner fixtures amendment pinned the leg-E forget probability.

**Run:** `SELF-CHECKS: 1,691,638 passed, 0 failed`, exit 0, ~9 s;
byte-identical stdout + results.json across two process runs by external
diff (sha256 stdout `e71c191a…`, results `5245a14b…`). In-sim chained anchor
reproduced V027's committed Feas map exactly. Exact arm: NO cell infeasible
(REJECT, checked first, missed 0/9 vs ≥ 5/9); coverage per θ_r
6/12/24/48/72 h = 2/4/6/**8/9** of 9 — θ_r† = 48 h by the min rule, the
planted 72 h the unique full-coverage horizon; the orphan band binds
nowhere (max O95 107.9 h < 120). ΔFeas on shared bands: silence 3/9 →
renewal 9/9. Arm S: registered gates breached 2 + 5 of 45 each (predicted
sub-2.5σ pre-run); effective ≥ 2.5σ gates breached 2 of 90 (max z 2.73σ),
both pure sampling noise at 16×. Stability leg reproduces the pattern.
**Ruling: NULL (APPROVE barred by the pre-pinned gate protocol)** — an
honest NULL: the diagnostics distinguish noise for the reader, they do not
un-bar the clause. The conditional rule ships (72 h clears both bands in
all 9 swept cells; 48 h everywhere except daily × sloppy; compliance floors
0.25/0.10; the jitter leg shows twin-safety collapses under irregular wakes
at the same mean — grace must budget the gap tail); the warn-first
missed-renewal counter is the named live probe.

Landed: INTAKE 029 (2026-07-13T07:36:09Z) + VERDICT 031
(2026-07-13T07:36:10Z) appended to `control/outbox.md` (append-only;
VERDICT 029 = PROPOSAL 027's landed on the sibling branch @ 76dc487 BEFORE
this append — tail re-verified, numbers kept per the reserved +2 offset);
verdict PR from `claude/verdict-031-lease-renewal`. Worker session — no
heartbeat writes; this card flip is the last commit.

## 💡 Session idea

Register MC agreement-gate tolerances FAMILYWISE, not per-point. Two data
points now: V027's absolute gates sat at 0.7–1.6σ (breaches certain,
predicted pre-run); P029 "applied the lesson" by pre-checking per-point
tolerances at ≥ 2.5σ — but 2.5σ two-sided across ~90 point-gates still
carries ~50% aggregate breach odds, and this run drew the unlucky half:
2/90 breaches (z ≤ 2.73σ, noise-confirmed at 16×) barred an APPROVE whose
band arithmetic had full-cell margins. The portable rule: at registration,
size the per-point multiplier so the EXPECTED FAMILY breach count is ≪ 1
(e.g. ~3.5σ for 90 gates), or register the M that makes the absolute
tolerances clear that bar — per-point σ thinking silently converts a
30-minute re-run into a verdict-grade outcome difference. Cheapest
conversion here, named in the verdict: identical committed sim at
M_S ≈ 16,000, pure mechanics.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-029-comp-stipend.md` (the sibling that
landed while this slice ran): complete and honest — its born-red
choreography, fixtures-before-runner trail, and its one disclosed
hand-pin correction (expectation recomputed, disclosed in three places, no
constant touched) are the right template for mid-flight corrections; this
session needed the same class of move once (a fixtures amendment pinning
the leg-E forget probability BEFORE the runner existed) and followed its
disclosure pattern. Its race handling (merge-not-rebase on a PUSHED branch,
numbers reserved not positional) was reused here in the cheaper form
available to an unpushed branch (re-stack onto the advanced origin/main,
tail re-verified pre-append). One export it could not give: its gates
passed clean, so the familywise-tolerance lesson above (this card's 💡) is
new material, not inherited.

# Session — VERDICT 036 — Drift-regime observability: is the arm of V024's conditional trust rule readable from the basket stream in time to act? (idea-engine PROPOSAL 034)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-036 slice-worker session
> Objective: settle idea-engine PROPOSAL 034 (control/outbox.md · 2026-07-13T09:12:01Z · status: sim-ready; idea `ideas/trading-strategy/xsec-drift-regime-observability-2026-07-13.md` @ idea-engine blob 5e094c88, main eea4e5b — the standing ORDER 003 VENTURE rotation slot, round 5, trading half). Build the fully hermetic pre-registered operating-characteristic sweep: under the pinned two-arm drift-regime stream (per-bar Sharpe units x_t = μ_{s_t} + ε_t, ε i.i.d. N(0,1); state D mean δ = 1.15/√252 = 0.07244319066010188 — V024's matched arm — state Z mean 0; ρ-invariant by construction, asserted; 2-state Markov chain with geometric sojourns, 9 decision cells (S_D, S_Z) ∈ {126, 252, 1008}², stationary start, T = 2,595 bars, scoring t ∈ [252, T), M = 1,000 paths per cell), which of the 18 pre-registered cheap detectors — statistic ∈ {trailing annualized Sharpe SR_w with PINNED vol normalizer, trailing up-share UP_w} × w ∈ {63, 126, 252} × threshold position λ ∈ {0.3, 0.5, 0.7} (SR threshold h = λ·1.15; UP threshold u = 1/2 + λ·(p_D − 1/2), p_D = Φ(δ) = 0.528875393055249) — removes at least +0.10 of trust-misallocation rate vs the EXACT best-static-prior baseline min(π_D, π_Z) per cell (ΔE_oracle, the V032 beat-the-best-static discipline), in BOTH Arm A (exact, seedless: pure-window Gaussian/Binomial OCs via math.erf/math.comb, exact occupancies, baselines, flip-count expectations, the full ceiling table) and Arm S (seeded MC of the full switching stream; seeds 20260772 main / 20260773 stability (M = 250, must reproduce the ruling) / 20260774 reporting / 20260775 aux, allocated strictly above the P033 registry high-water 20260771; familywise-calibrated frozen-state gates per the V027/V031 lesson, swap and ρ-invariance identities, draw-count sentinels, twin decision evaluators, two-process byte-identity, CPython minor pinned). Reporting-only legs that cannot flip the decision: post-flip lag tables; ΔE_always vs the de-facto always-trust rule; the realized-sd SR variant; and the occupancy-graded bar leg — V024's committed G6 machinery at IID/ρ = 0.3 (J = 9, T = 2,595, R3 rule verbatim, G6 only, M = 400 per point, seed 20260774), φ_D ∈ {0, 0.25, 0.5, 0.75, 1}, chained to the committed anchor pair q99(G6) = 0.604101 at φ = 0 and 0.366902 at φ = 1 (machine-read @ cd47c06) via pre-pinned tail-count tolerances. Decision (registered order, REJECT first): REJECT iff NO variant clears ΔE_oracle ≥ +0.10 in ≥ 3 of 9 cells; APPROVE iff ONE variant (same statistic, w, λ) clears it in ≥ 7 of 9, stability-reproduced; NULL otherwise (the per-cell frontier is the citable pin, flip axes named via per-axis pass shares).

## What happened

Built `sims/verdict-036-drift-observability/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: fixtures.json (the pre-registration —
every constant verbatim from the idea file, both V024 anchors machine-read
@ cd47c06, all 36 frozen-gate tolerances pre-pinned with their SE
arithmetic, 15 disclosed intake-time decisions) landed one commit BEFORE
the runner; scratchpad pilot on throwaway seeds 990101–04 only.

**Run output:** `SELF-CHECKS: 489 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `026353f0…`, results `ab8bf6b8…`), ~92 s per run,
cpython-3.11 pinned. Every registered gate passed on the first accepted
committed run: frozen-state 36/36 (max |dev|/tol 0.287), occupancy/flip
27/27 on exact closed-form variances, SR swap transpose 90/90 (max |z|
2.04 vs 4.5), ρ-invariance byte-identity (50 paths × 2 scales × 18
variants), both V024 tail-count anchors (N_exc 3 and 3 vs bands ≤ 12),
draw sentinels exact over 113,142,000 uniforms, twin G6 + twin decision
evaluators, determinism replays. **Ruling: REJECT — cheap drift-gating
never materially pays; build no lane tooling.** REJECT checked FIRST per
the registered order and met with structure to spare: no variant clears
ΔE_oracle ≥ +0.10 in ≥ 3 of 9 cells — measured max 1 of 9 (only the
(1008,1008) corner pays; best row SR w=252 λ=0.5 at +0.1660), the
second-best cell misses by 0.41 pp, the third-best by 2.8 pp, and Arm A's
exact ceiling arithmetic closes 6 of 9 cells before any mixing (at
min(π_D, π_Z) ≤ 1/3 the +0.10 band is unreachable even at the pure-window
ceiling). Binding axis min-sojourn (pass shares 126/252/1008 = 0/0/0.833).
Stability leg (seed 20260773, M = 250) reproduces REJECT. Side pins:
ΔE_always spans +0.609 to −0.323 (the detector beats always-trust only
where V024's zero-drift null already withholds trust); vol estimation is
free (|ΔBA| ≤ 0.0004); the occupancy-graded bar's BODY (q50/q90)
interpolates monotonically between the committed arms while its q99 tail
stays per-arm at M = 400 (reported, not smoothed).

Landed: INTAKE 034 (2026-07-13T09:55:51Z) + VERDICT 036
(2026-07-13T09:55:52Z) appended to `control/outbox.md` (append-only, 0
deletions; tail re-verified at origin/main HEAD 38ac71a immediately before
the append — VERDICT 035, NIGHT-REPORT 001, and the out-of-queue
SIM-REQUEST pair simreq-001/VERDICT 037 all landed mid-slice; V037's own
sequence note RESERVED number 036 for this slice, so the pair keeps
INTAKE 034 / VERDICT 036 by the +2 offset and lands after 037 in FILE
order with number order intact; origin/main merged INTO this branch,
never rebased). Verdict PR from `claude/verdict-036-drift-observability`.
Worker session — no heartbeat writes; this card flip is the last content
change before the single push. Seed registry: 20260772–75 consumed — new
high-water 20260775.

## 💡 Session idea

When a pre-registered gate asserts an identity "exactly in the analytic
arm" over a detector FAMILY, check at drafting time that the identity
survives every member's discreteness — here the swap identity
(relabel D↔Z, λ → 1−λ, transpose the confusion matrix) is exact for the
Gaussian SR family but is broken for the Binomial UP family by the ceil
threshold's asymmetry between Bin(w, p_D) and Bin(w, 1/2): the cross-cell
transpose misses by O(discreteness) ≈ 3 pp at w = 63 — two orders above
MC SE, so a naively scoped MC gate would have failed a CORRECT sim. The
fix that preserved the registration's content (committed in fixtures.json
BEFORE the runner, with the arithmetic reason): scope the Arm-S
statistical transpose to the continuous family, and carry the discrete
family's swap content in the form that IS exact — the mirror identity
P(Bin(w,p) ≥ k) = P(Bin(w,1−p) ≤ w−k) via two independently written
routines plus the tie-free pathwise complement. The portable rule: a
symmetry gate registered over a mixed continuous/discrete family needs a
per-family exactness check at design time, or the gate calibration lesson
(V028) repeats as a gate SEMANTICS lesson.

## ⟲ Previous-session review

Prior cards `2026-07-13-verdict-035-assign-at-merge-tax.md` (the sibling
flagged in flight at dispatch) and
`2026-07-13-verdict-037-venture-serial-pricing.md` (the out-of-queue
SIM-REQUEST slice that landed mid-build): both complete and honest;
exports adopted. (1) V035's 💡 (verify every registered band is reachable
AFTER pre-computable exclusions) was applied at intake here: the ceiling
arithmetic showed 6 of 9 cells closed for the +0.10 band, which leaves
REJECT and NULL live and APPROVE reachable only through the three
balanced cells — tighter than the drafting text stated ("every band
reachable" holds only variant-wise, not cell-wise), disclosed in the
REPORT's ceiling section rather than discovered post-hoc. (2) V037's
number-reservation note ("a later-landing 036 slots before it in number
order without renumbering") is the reserved-number discipline working in
its hardest case yet — an out-of-queue verdict OVERTAKING a reserved
number — and this slice consumed the reservation exactly as written:
zero renumbering, file order ≠ number order, both orders reconcilable
from the sequence notes alone. (3) The V035 pattern of exact-arm-decides
/ MC-arm-validates transferred cleanly: where V035's decision arm was
closed-form queueing vs committed anchors, this head's decision needed
the MC arm (mixed-window path dependence has no closed form), so the
exact arm was pointed at the CONTROLS instead — the same discipline,
opposite arm assignment, both honest.

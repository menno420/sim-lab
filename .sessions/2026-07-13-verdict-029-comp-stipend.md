# Session — VERDICT 029 — comp/stipend envelope: the LAST routed lever (idea-engine PROPOSAL 027)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-029 slice-worker session
> Objective: settle idea-engine PROPOSAL 027 (control/outbox.md · 2026-07-13T06:04:37Z · status: sim-ready; idea `ideas/superbot/casino-comp-stipend-envelope-2026-07-13.md`, the ORDER 004 rule-3 GAME-MECHANICS rotation slot, round 3 — round 1 P020 → V022 rejected the odds lever, round 2 P023 → V025 rejected the entry-fee lever; this head prices the comp/stipend lever, the LAST of VERDICT 022's routed non-odds levers, ON V025's measured surviving substrate). Build the fully hermetic pre-registered four-band measurement: B₀ = 1,000 chips, F = 10, cap c = 5 FIXED, shapes T1/T2 (T3 excluded by citation + one monotonicity spot cell), takes t ∈ {0.05, 0.10} + t=0 control reporting-only; comp designs D1 qualified stipend / D2 handle rebate (cap 2σ·B₀) / D3 loss rebate — D1/D2 over σ ∈ {0.02, 0.05, 0.10, 0.20}, D3 over ρ ∈ {0.2, 0.4, 0.6, 0.8}; 48 decision cells + 4 σ=0 baseline cells that must reproduce V025's committed rows; policies R1/R5/RG/MC and profiles CASUAL/GRINDER/COMPULSIVE verbatim from V025 with comp counted in final wealth; a per-design FARMER family (wash-qualifier / cap-chaser / 12-variant stopper grid) attacking the new MINT band (max over policies ∪ farmers of E[session net incl. comp] ≤ 0). Arm A exact (comp-shifted binomial/DP FUN for all cells, σ=0 Fractions equal to V022/V025's committed values by exact rational equality, D1≡D2 and D3≡baseline FUN identities, the (σ−t)·B₀ pump line, exact banded-Fraction stopper DP on T1, t=0 P_double = 1/3); Arm S seeded MC `random.Random(20260752)` M = 5,000/2,000/500 with the 1.0 pp agreement gate, stability leg seed 20260753 (half M) must reproduce the ruling, reporting legs seed 20260754 (t=0 control, compulsive, house-net table, T3 monotonicity spot cell, aggregated-draw spot check), aux stream seed 20260755. Decision (registered order): REJECT iff no (design, size) rescues C1 = (T1, t=0.10) and none rescues C2 = (T2, t=0.05); APPROVE iff some design rescues C1 at ≥ 2 consecutive sizes all-four-pass, stability-reproduced; NULL otherwise with the per-design signature table as the pin. Hermetic: zero repo/network reads at run time; byte-identical re-run on pinned cpython-3.11.

## What happened

Built `sims/verdict-029-comp-stipend/` — a stdlib-only NUMERIC SIMULATION
(rung 1), fully hermetic: the sim reads exactly one file (its own committed
`fixtures.json` pre-registration, cross-checked at start). The
pre-registration (all constants verbatim from the idea file; EIGHTEEN
disclosed intake-time decisions including the σ = t boundary rule, MINT
exact-where-covered, the D3 stopper ρ-invariance, and the pre-run
gate-calibration SE arithmetic per the V027 lesson; five hand-derived pins
with committed derivations; both parents' anchor Fractions and measured rows
quoted verbatim from the committed files @ 5e356ed) was committed BEFORE the
runner. A scratchpad feasibility probe ran before the fixtures commit and is
disclosed inside fixtures.json.

**The one honest correction this slice:** the first full run failed
hand-pin 1 and nothing else of substance — the pin's originally committed
derivation asserted 5 tickets on its final round where the bank (400 cu)
affords only 4 under the registered b ≤ ⌊bankroll/F⌋ rule; the kernel AND
the independently written twin both followed the registered rule and agreed
with each other (124 tickets / 2,480 cu rebate / final 80 cu). The pin's
EXPECTATION was hand-recomputed and corrected before the accepted runs, with
the correction disclosed in `fixtures.json`
(`hand_derived_pins[0].derivation_correction`), in REPORT.md §2, and here.
No decision constant, band, seed, M, or convention changed.

**Run output summary (accepted runs):** `SELF-CHECKS: 2668600 passed, 0
failed`, exit 0, stdout + results.json byte-identical across two full
process runs (external diff + sha256), cpython-3.11 pinned, ~6.8 min per
run; draw sentinels closed at 935,017,192 (primary) + 467,352,942
(stability) uniforms. **Ruling: NULL — the registered straddle, stability-
reproduced, twin-evaluator-agreed.** C1 = (T1, t=0.10) IS rescued but only
one size deep: clean at D1/D2 σ=0.05 (exact FUN 0.3069 vs baseline 0.1346;
MINT max −5.0 units exact; SINK 0.0000), BOUNDARY at σ=0.10 = t (farmer EV
= (σ−t)·B₀ = 0 exactly — the pre-named mint knife-edge, registered as
unable to support APPROVE), exact MINT failure at σ=0.20 (+0.10·B₀). C2 =
(T2, t=0.05) is censoring-indeterminate across its whole column (R1-grinder
cap_frac 0.0115–0.0340 vs the 1% line — the parent's own committed 0.0095
knife-edge re-measured on the other side, worsened by every comp design);
D2 σ=0.05 genuinely closes the SAFE gap (0.0316 vs parent 0.0608) but sits
ON the σ=t boundary; D3 ρ ≥ 0.6 MINTS through the PLAIN CASUAL PLAYER
(+1.05/+3.07 units EXACT at t=0.05) — the optimal-stopping farmer is
strictly weaker (T1 stopper max EV −2.68). Unanticipated clean band,
reporting-only: D3 ρ ∈ {0.2, 0.4, 0.6} composes with T2 at t=0.10 (wipe
0.1778 → exactly 0; FUN 0.2671; three consecutive clean sizes at a
non-target cell). Gates: 66 pooled probability points, max 0.8854 pp,
ZERO breaches (the pre-disclosed SE arithmetic priced stopper points at
~1.6σ; the 8× aux protocol stayed idle); 164 EV gates at 4·SE all pass;
identity gate EXACT (the grid's third chained verdict on one binomial);
V025 baseline rows reproduced (surviving cell worst-wipe 0.0020 vs 0.0024;
C2 0.0552 vs 0.0608; price tag 4.86%/24.98% vs 5.155%/25.18%); T3
monotonicity spot 0.2135 → 0.3180 (comp raises P_double, exclusion
direction verified).

Slice boundary this cycle (the V015–V028 precedent): this session carries
the INTAKE 027 and VERDICT 029 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). The tail at branch time was VERDICT 027 @ 5e356ed;
VERDICT 028 (P026, the sibling venture slot) landed @ fe51983 mid-slice and
origin/main was merged INTO this branch (never rebased) before the outbox
append — numbering +2 offset preserved (P027 → V029), re-verified at
origin/main HEAD immediately before the append. No @codex step — suspended
per the outbox codex-line escalation @ dedc12e. Born-red card and complete
flip land in one push (the V018–V028 choreography).

## Run command

```
python3 sims/verdict-029-comp-stipend/comp_stipend_sim.py
```

## 💡 Session idea

Hand-derived pins should be REPLAYED against a reference implementation of
the single rule they exercise before being committed, not just hand-checked:
pin-1's error (forgetting the affordability clamp on the terminal round) is
exactly the class of error a 10-line scratchpad replay would have caught at
drafting, and the asymmetry is instructive — the KERNEL was right because it
implements the registered rule once, while the PIN was wrong because a human
re-derived the rule inline. The portable rule: every hand pin ships with a
mechanical replay (however trivial), and a pin/kernel disagreement is
resolved by re-deriving the pin against the registered rule text BEFORE
suspecting the kernel — while disclosing the correction at every layer, as
here, so a corrected pin can never silently become a fitted one. Second
export: registering "boundary cells cannot support APPROVE" BEFORE the run
turned what would have been an agonizing judgment call (a σ=t cell with
farmer EV exactly 0 completing a 2-size band) into a mechanical lookup — the
σ=t knife-edge was disclosed in the proposal itself, and pinning its
decision treatment in fixtures made the NULL unarguable.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-028-breadth-budget.md` (the sibling venture
slot, landed mid-slice): complete and honest; its exports are adopted here.
(1) The one-push born-red choreography — followed verbatim. (2) Its
in-repo byte-reuse discipline (V024 machinery identity-verified) —
transposed: this slice REUSES V025's kernel shape and quotes both parents'
committed constants into fixtures with exact-equality gates, the
three-generation chain's comparability contract. (3) Its
detectability-floor-first evaluation-order discipline — mirrored here as
the registered REJECT → APPROVE → NULL order with the boundary rule pinned
before any draw. (4) The V027 card's gate-calibration lesson (register SE
arithmetic before the run) — applied at registration in
`gate_calibration_disclosure`; this slice's gates then passed with zero
breaches, which is what a correctly calibrated registration looks like.

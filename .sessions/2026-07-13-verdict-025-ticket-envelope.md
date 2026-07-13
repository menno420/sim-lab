# Session — VERDICT 025 — entry-fee ticket envelope (idea-engine PROPOSAL 023)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-025 slice-worker session
> Objective: settle idea-engine PROPOSAL 023 (control/outbox.md · 2026-07-13T03:53:03Z · status: sim-ready; idea `ideas/superbot/casino-entry-fee-ticket-envelope-2026-07-13.md`, the ORDER 004 rule-3 GAME-MECHANICS rotation slot, round 2 — the direct successor to VERDICT 022's REJECT of the odds lever, whose "Named follow-ups" list requested this head verbatim: "an entry-fee/prize-table envelope sim — the SAFE-band successor question"). Build the fully hermetic pre-registered successor-envelope sweep for the entry-fee-with-prize structure: B₀ = 1,000 integer chips, ticket price F = 0.01·B₀ = 10 (a table constant no policy can escalate); prize schedules paying multiples of F with probabilities scaled by (1−t) so E[prize] = (1−t)·F exactly — T1 double-up {2F w.p. (1−t)/2, the FUN leg the IDENTICAL binomial to VERDICT 022's G1 reference (pre-registered cross-verdict identity)}, T2 tiered {8F, 3F, 1F w.p. (1−t)·{0.05, 0.10, 0.30}, per-ticket variance 3.4·F² at t=0}, T3 jackpot {25F, 5F w.p. (1−t)·{0.024, 0.08}, variance 16·F²}; take grid t ∈ {0.01, 0.02, 0.05, 0.10} + t=0 control (reporting-only); per-round ticket caps c ∈ {5, 25, 100} (max per-round spend {5%, 25%, 100%}·B₀ — the exact mirror of the parent's m-grid, every cell naming its parent cell); re-buy policies with b ≤ c and b ≤ ⌊bankroll/F⌋, a round's b tickets resolving as b INDEPENDENT draws (per-round volatility √b, not b — the structure lever under test): R1 b=1, R5 b=min(5,·), RG greedy b=max affordable, MC chase b=min(2^L,·) with L = consecutive net-losing rounds reset on a net win; profiles CASUAL (100 rounds or bankroll < F; P_ahead = P(final > B₀), P_wipe = P(final ≤ 0.1·B₀)), GRINDER (to ≥ 2·B₀ or ≤ 0.5·B₀, hard cap 4,000 rounds; P_double, > 1% cap-hits marking the cell indeterminate — a NULL path, never silently absorbed; measured P_double a LOWER bound so SINK failures stand), COMPULSIVE (reporting-only, R1, to ruin or 20,000 rounds); 36 decision cells = 3 shapes × 4 takes × 3 caps. Arm A (analytic, seedless, exact rationals): FUN for ALL 36 cells (T1 binomial via math.comb REQUIRED to reproduce VERDICT 022's committed G1 reference values exactly, e.g. 0.2738 at 0.05; T2/T3 by exact integer-support DP convolution, 100 steps, fractions.Fraction), two-boundary gambler's-ruin closed forms for GRINDER on T1×R1 (unit steps of F, span 150, start 50 above the lower boundary), an exact T1×R1 CASUAL wipe DP, and the t=0 control P_double = 1/3 exactly by optional stopping. Arm S (seeded MC): random.Random(20260730), pinned loop order (shape, t ascending, c ascending, policy R1/R5/RG/MC, profile casual → grinder → compulsive, replications sequential, one rng.random() per ticket), M = 5,000 casual / 2,000 grinder / 500 compulsive per cell-policy; the 1.0 pp Arm-A agreement gate or the run is invalid; half-M stability leg seed 20260731 must reproduce the ruling; aggregation spot-check seed 20260732; aux self-check stream seed 20260733 (never read by any decision number). Bands held from the parent BY DESIGN: FUN P_ahead ≥ 0.25 · SAFE max-policy P_wipe ≤ 0.05 · SINK max-policy P_double ≤ 0.10; E*(g, c) = take rates where all three hold, determinate cells only. Then issue exactly ONE of REJECT (E* = ∅ at EVERY cap in ≥ 2/3 shapes, both arms where covered — checked FIRST) / APPROVE (∃ cap c* with ∩_g E*(g, c*) ⊇ 2 consecutive take-rate grid points, stability-reproduced) / NULL (anything else — the per-shape envelope table IS the pin, flip axis named via per-axis envelope shares; indeterminate cells route to NULL, never to APPROVE) per the decision rule registered in the idea file BEFORE any code existed, with the bankroll-RELATIVE boundary and the V001/V008 earn-rate-baseline caveat restated verbatim, the i.i.d.-ticket and finite-policy-set boundaries stated, the four chained anchors (parent near-miss T1 (t=0.05, c=5) vs 0.2738/0.0895/0.1358; T2/T3 SINK wall vs 0.195–0.323; t=0 control; expected-loss price tag) shipped as reporting-only legs that cannot flip the decision, and the per-shape envelope table shipped on EVERY outcome. Hermetic: zero repo/network reads at run time; the parent's anchor constants quoted verbatim from its committed REPORT.md/results.json @ fda94d0 into fixtures.json.

## What happened

Built `sims/verdict-025-ticket-envelope/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: the sim reads exactly one file (its
own committed `fixtures.json` pre-registration, cross-checked at start in
Fractions) and touches no repo state, network, or wall clock. The
pre-registration (all constants verbatim from the idea file, the pinned
loop/draw order, the decision rule with evaluation order, TWELVE disclosed
intake-time decisions, two hand-derived pin scenarios with full
derivations, and VERDICT 022's committed G1 identity values + anchor
constants quoted verbatim @ fda94d0) was committed BEFORE the runner was
written. The full self-check battery was smoke-tested on a throwaway seed
at reduced M before any pinned-seed run (only the agreement gate tripped
there, at ~2 SE of the smoke M's noise — the mechanics all passed).

**Run output summary:** `SELF-CHECKS: 1925723 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs
(external diff), cpython-3.11 pinned, ~5.2 min per run, 1,214,568,503
primary + 605,734,597 stability per-ticket draws, sentinels closing
exactly. **Ruling: REJECT — the pre-registered rule fires first** (E* = ∅
at every cap in 2/3 shapes: T2, T3), stability-reproduced with the
IDENTICAL envelope map. The headline chained measurement rides with equal
prominence: E*(T1, c=5) = {0.05} — the parent's near-miss cell transposed
now passes ALL THREE bands (FUN 0.2738 exact-identical by the
cross-verdict identity gate, 5/5 Fractions equal; worst-policy P_wipe
0.0024 vs the parent's 0.1358 SAFE failure, a 57× cut; worst-policy
P_double 0.0000 with uncapped exact 4.5e−05). The "bounded fee" hypothesis
measured TRUE for even-money and FALSE as a universal frame: T2 dies in a
SINK-low-take (0.244/0.163 at t ≤ 0.02, every cap) / SAFE-high-take
(0.0608 at its best cell) pincer; T3 fails SINK in all 12 cells
(0.148–0.346 — the parent's wall reproduced in the fee frame) and SAFE in
all 12 (0.275–1.000). Residual gaps: T2 SAFE 0.0608 vs 0.05; T3 SINK
0.1480 vs 0.10; T1 gap CLOSED. Cap rider: c=5 is load-bearing (RG wipes
0.116–1.000 at c ≥ 25 — the parent's MAXBET rider transposes intact).
Agreement gate max pooled deviation 0.78 pp vs the 1.0 pp band (19/210
per-leg readings over 1.0 pp, max ≈ 2.8 per-leg SE, disclosed); t=0
control = 1/3 exactly (closed form ≡ independent elimination); Wald
prize-fairness passed on every control leg; 1,620 traced replications
replayed exactly through the independently written twin kernel; twin
decision evaluators agree.

Slice boundary this cycle (the V015–V024 precedent): this session carries
the INTAKE 023 and VERDICT 025 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). The tail at append was VERDICT 024 (PROPOSAL 022 @
6c7e278) — origin/main re-checked immediately before the append, numbering
unaffected, +2 offset preserved (P023 → V025). No @codex step — suspended
per the outbox codex-line escalation @ dedc12e. Born-red card and complete
flip land in one push (the V018–V024 choreography).

## Run command

```
python3 sims/verdict-025-ticket-envelope/ticket_envelope_sim.py
```

## 💡 Session idea

When a pre-registered agreement gate compares a capped MC process against
an UNCAPPED closed form, reconcile the two QUANTITIES at intake time, not
at debug time: here the 4,000-round grinder cap holds back 22 pp of
doubling mass at t=0 (1/3 → 0.1123), so a naive gate reading would have
failed on model mismatch with a bug-free kernel. The portable rule: for
every analytic pin, write down WHAT STOPPED PROCESS it describes; if the
MC stops earlier (cap, censoring, bankruptcy), add the exact same-capped
quantity to the analytic arm (a finite-horizon absorption DP is ~15 lines
and deterministic) and gate against THAT, keeping the uncapped form as a
pure-math pin with the gap reported. The same discipline caught nothing
here only because it was applied before the pinned run — the fixture
discloses it as an intake decision, which is where it belongs.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-024-keep-margins-noise.md`: complete and
honest; its exports are adopted here directly. (1) The one-push born-red
choreography is followed verbatim. (2) Fixtures-before-runner, including
hand-derived pins WITH derivations committed before code — reused (two
pins: the MC-chase seven-round loss-streak wipe consuming exactly 100
draws; the jackpot three-round double under the tight cap); its
recompute-the-pin-mechanically rule was applied by hand-checking both pin
walks against the kernel spec before committing them. (3) Its
draw-count-sentinel discipline (exactly one uniform per event makes
stream-position accounting exact integer arithmetic) — reused directly:
one rng.random() per ticket, fresh-Random advance sentinels closing at
1,214,568,503 + 605,734,597 uniforms. (4) Its twin-evaluator and
trace-replay patterns — reused (an independently written dict-state twin
kernel replaying 1,620 traced replications exactly; two decision
evaluators, one exact-integer, one Fractions). (5) Its
smoke-test-the-self-checks-on-a-throwaway-seed practice — followed before
any pinned-seed run.

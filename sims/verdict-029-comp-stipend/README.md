# verdict-029 · comp-stipend

Can a comp/stipend line — the LAST of the three non-odds levers VERDICT 022
routed after rejecting the odds lever (rake-only PvP priced free by its own
rake ≡ edge identity; entry-fee priced by VERDICT 025, reject) — buy FUN
back at the sink-firm take, or close the tiered shape's SAFE near-miss,
without any swept policy INCLUDING a per-design farmer family extracting
positive expected session value from the house (the new pre-registered
MINT band)? Runs ON VERDICT 025's measured surviving substrate,
cell-for-cell: this is the program's first three-generation chained verdict
line (V022 → V025 → here), every generation sharing bands and cell
addresses. Answers idea-engine PROPOSAL 027 (control/outbox.md
2026-07-13T06:04:37Z, idea
`ideas/superbot/casino-comp-stipend-envelope-2026-07-13.md`, landed via
idea-engine PR #294, main `3978df1`) — the ORDER 004 rule-3 GAME-MECHANICS
rotation slot, round 3. Fully hermetic per the PROPOSAL 017–026 precedent:
every fixture is a pinned constant committed with the sim, zero
repo/network reads in the verdict session; both parents' anchor constants
are quoted verbatim in `fixtures.json` from their committed files @
`5e356ed`.

Model: B₀ = 1,000 integer chips, F = 10, per-round ticket cap c = 5 FIXED
(both parents measured the tight cap load-bearing); exact integer
centi-unit arithmetic (1 cu = 0.1 chip) makes every comp amount in the
grid an exact integer. Shapes T1 double-up / T2 tiered (T3 jackpot
EXCLUDED BY CITATION of V025's measured walls + comp monotonicity,
spot-asserted on one reporting cell); takes t ∈ {0.05, 0.10} + t=0 control
reporting-only. Comp designs: D1 qualified stipend σ·B₀ at session end iff
handle ≥ B₀; D2 handle rebate σ·F per ticket, continuous, session cap
2σ·B₀; D3 loss rebate ρ·(B₀ − final)⁺ — D1/D2 over σ ∈ {0.02, 0.05, 0.10,
0.20}, D3 over ρ ∈ {0.2, 0.4, 0.6, 0.8}. 48 decision cells + 4 σ=0
baseline cells that must reproduce V025's committed rows. Policies
R1/R5/RG/MC and profiles CASUAL/GRINDER/COMPULSIVE verbatim from V025 with
comp counted in final wealth (grinder stop targets shift with the comp).
FARMER family per design: D1 wash-qualifier, D2 cap-chaser, D3 12-variant
optimal-stopping grid — the MINT attack. Bands: FUN ≥ 0.25 / SAFE ≤ 0.05 /
SINK ≤ 0.10 inherited verbatim BY DESIGN + MINT ≤ 0 (weak; the σ = t
knife-edge marked boundary). Arm A exact: comp-shifted binomial/DP FUN for
all 52 cells with the σ=0 Fractions equal to V022/V025's committed values
by EXACT rational equality, exact casual-R1 wipe and E[net incl. comp],
the D1≡D2 and D3≡baseline FUN identities, the (σ−t)·B₀ farmer pump line,
an exact banded-Fraction stopper DP on T1 (b=1 variants cross-checked
against the gambler's-ruin closed form), V025's three-derivation grinder
ruin machinery, t=0 P_double = 1/3. Arm S seeded MC gated at 1.0 pp
(probabilities, pooled per the pre-disclosed SE arithmetic) and 4·SE
(EVs). Ruling REJECT (no rescue of C1 = (T1, 0.10) and none of C2 = (T2,
0.05), checked FIRST) / APPROVE (≥ 2 consecutive clean sizes at C1,
stability-reproduced) / NULL per the decision rule registered in the idea
file before any code existed.

## Run (one command)

```
python3 sims/verdict-029-comp-stipend/comp_stipend_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — the only randomness is
`random.Random(20260752)` (primary) / `random.Random(20260753)` (stability,
half M) / `random.Random(20260754)` (reporting: t=0 control, compulsive,
T3 monotonicity spot cell, aggregated-draw spot check part A) /
`random.Random(20260755)` (aux: 8× gate re-measures + the aggregation
twin), each consumed in the pinned loop order (shape T1→T2, t ascending,
baseline block first then D1→D2→D3 with sizes ascending, policy
R1/R5/RG/MC each casual-then-grinder, farmer legs per the fixtures, the
ρ-invariant D3 stopper block last per (shape, t), replications sequential,
exactly one `rng.random()` per ticket). No network, no git, no wall clock,
no `hash()`. stdout and `results.json` are byte-identical across process
runs (verified by external `diff` of two complete runs, cpython-3.11).
Progress goes to stderr only.

## Files

- `comp_stipend_sim.py` — stdlib-only driver: exact Arm A (comp-shifted
  binomial + bigint DP convolution + banded-Fraction stopper DP + ruin
  closed form/elimination/capped DP), the seeded MC arm with an
  independently written twin kernel, twin decision evaluators, gates,
  anchors, reporting legs.
- `fixtures.json` — the pre-registration, committed BEFORE the runner:
  every constant verbatim from the idea file, 18 disclosed intake-time
  decisions (the σ = t boundary rule, MINT exact-where-covered, stopper
  ρ-invariance, the pre-run gate-calibration SE arithmetic), both parents'
  quoted anchor constants, five hand-derived pins with full derivations.
- `results.json` — full four-band tables (primary + stability), signature
  table, house-net table, rescue summaries, gates + breaches + 8× aux
  re-measures, anchors, reporting legs, ruling.
- `REPORT.md` — the verdict report (validity gate + ruling +
  recommendation).

## Verdict

See `REPORT.md` and the `## VERDICT 029` entry in `control/outbox.md`.

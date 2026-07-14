# VERDICT 071 — REPORT — noisy reciprocity: TFT vs the complete memory-one field under execution noise (INTAKE 060)

**Class: REJECT** (pre-registered rules applied in order: REJECT → INVALID →
APPROVE → NULL; REJECT checked FIRST fires on all four conjuncts).

Source: idea-engine `## PROPOSAL 060 · 2026-07-14T05:55:31Z · status: sim-ready`
(idea-engine PR #404 @ main 0d307cc; idea doc
`ideas/fleet/noisy-reciprocity-tft-collapse-2026-07-14.md`). Fully hermetic:
every fixture constant pinned in the PROPOSAL 060 block / idea doc, copied
verbatim into the committed `fixtures.json`; the runner reads only that file;
zero repo/network reads at verdict time. The drafter's disclosed prototype
landing was re-derived from scratch with ZERO trust and compared NEVER gated.

## Reproducibility

- `SELF-CHECKS: 54 passed, 0 failed`, exit 0, ~4 s/run, stdlib-only, hermetic
  (reads only its own `fixtures.json`), CPython 3.11 pinned and asserted.
- Byte-identical across two full process runs by external `diff` + sha256:
  `run-stdout.txt` = `105edaf4b2659a5a0b416d8eecf3d4cb072190f64f246c35cf8bdffa9c169e6c`,
  `results.json` = `00b718d6a2f05a7b018b2bfd20af1bf6d4c640393873d1382a6fc1838d5d3383`.
- Seeds: 20261377 main / 20261378 stability / 20261379 presentation — the ONLY
  three RNGs constructed (asserted, pinned order); aux 20261380 NEVER read
  (asserted against the constructed-seeds registry).
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run. Fixtures committed BEFORE the runner (git trail: fixtures
  ebff9a6 precede the runner commit).
- Every decision number is a seedless exact `fractions.Fraction`; the seeded
  Arm-R legs are REPORTING-ONLY and carry no statistical gate (their only
  gates: the 2T-per-game draw sentinel, exact at 1,088,000 + 272,000 calls,
  and byte reproducibility) — joint gate pass probability 1 for a correct
  implementation, as registered.

## Decision conjuncts (registered order, REJECT first — all four FIRE)

1. **Gap:** score(WSLS) − score(TFT) at ε = 1/100 =
   `9345083308624553/19013690936000000` ≈ 0.491492 ≥ 2/5 exact.
   (score(TFT) = 66320495249/30396000000 ≈ 2.181882; score(WSLS) =
   152492158669156561/57041072808000000 ≈ 2.673375.)
2. **Echo identity:** v(TFT,TFT) = 9/4 EXACTLY at every grid ε
   {1/1000, 1/100, 1/20, 1/10} — and the F2 gate separately proves the
   TFT-vs-TFT stationary law is (1/4, 1/4, 1/4, 1/4) at every grid ε. The
   collapse is ε-INDEPENDENT: one error per thousand costs the same 25% of the
   cooperation surplus as one in ten.
3. **Rank inversion:** rank(TFT) strictly worse than rank(WSLS) at EVERY grid
   ε — dense ranks 9 vs 5 at all four ε (see Anomaly 1: the drafter disclosed
   10 vs 5 in competition-rank terms; the relational conjunct is identical
   under both conventions).
4. **WSLS self-play floor:** v(WSLS,WSLS) at ε = 1/100 = `737773/250000` =
   2.951092 ≥ 14/5. Grid: 187188187/62500000 ≈ 2.99501 (1/1000) ·
   737773/250000 (1/100) · 5553/2000 = 2.7765 (1/20) · 1301/500 = 2.602
   (1/10) — the registered 3 − O(ε) shape.

APPROVE was arithmetically foreclosed (mutually exclusive rank conjunct);
ALLD tops every noisy table (rank 1 at all four grid ε, score 597/200 = 2.985
at ε = 1/100) — a statement about uniform complete fields, not an equilibrium
claim (registered boundary).

## Gates (all green)

- **F1** field & solve identities: 16 rules re-enumerated as all of {0,1}⁴,
  named indices TFT = 10 (1,0,1,0), WSLS = 9 (1,0,0,1), ALLC = 15, ALLD = 0;
  PD preconditions T > R > P > S and 2R > T + S asserted; all 1,024 grid
  stationary solves: entries ≥ 0, Σπ = 1 exact, residual πP − π = 0 exact.
- **F2** echo theorem: uniform stationary at TFT-TFT, every grid ε, exact.
- **F3** closed-form anchors at every grid ε, exact; pinned references at
  ε = 1/100 reproduced: 29899/10000 · 10299/10000 · 49401/10000.
- **F4** transpose conservation: v(i,j) row-accounting = column accounting of
  the transposed solve, all 256 ordered pairs, every grid ε, exact.
- **F5** ε = 1/2 degeneracy: all 256 pairs uniform stationary, every value
  9/4 exactly.
- **F6** battery: Arm B (independently-written Cramer/adjugate) exact-equal on
  every Arm-A v(i,j) at every grid ε; ε = 0 orbit hand anchors v₀(TFT,ALLD) = 1,
  v₀(WSLS,ALLD) = 1/2, v₀(TFT,TFT) = v₀(WSLS,WSLS) = 3 all reproduced; twin
  decision evaluators (evaluator 2 recomputes scores/ranks from a fresh Arm-B
  pass) agree on the token REJECT/REJECT; draw sentinels exact; aux seed never
  read; byte-identical double run; CPython minor pinned.

## Anomalies (first-class findings)

1. **Dense-vs-competition rank (drafter disclosure mismatch, ruling-neutral).**
   The registered rank convention is DENSE ("dense; exact-Fraction
   comparisons" — idea doc, Pinned model). Under it rank(TFT) = 9 at every
   grid ε, not the drafter's disclosed 10: rules 3 = (0,0,1,1) and
   12 = (1,1,0,0) tie at exactly 9/4 — coincidentally the echo value — above
   TFT at every grid ε, and dense ranking counts the tied value once where
   competition ranking counts it twice. Every disclosed EXACT quantity
   (scores, gap, all v(i,j) spot values, orbit gap 1/12) reproduced
   digit-for-digit; only the rank RENDERING differs. No decision clause reads
   the absolute rank number except APPROVE's rank(TFT) = 1, false under both
   conventions; the strict/weak inequalities are convention-invariant here
   (WSLS rank 5 either way). Registered instrument applied as registered;
   disclosure mismatch reported, not smoothed over.
2. **Arm-R mixing-time finding (registered as a named finding, not a ruling).**
   The finite-horizon main leg (T = 4,000, ε = 1/100) deviates from the exact
   stationary value by up to 37359/37250 ≈ 1.0029 payoff units — pair
   (4, 12) = ((0,1,0,0) vs (1,1,0,0)), column seat; stability leg (T = 1,000)
   worse at 609/500 = 1.218. Mechanism: rule 12 repeats its OWN last executed
   move regardless of the opponent, so its behavior regime only switches via
   its own trembles (rate ε) — the chain is metastable with relaxation time
   ~1/ε = 100 rounds, and a 4,000-round horizon sees only ~40 regime switches.
   Exactly the pre-registered reason Arm R carries no statistical gate.

## Reporting legs (ungated)

- **Gap-vs-ε curve:** 0.521570 (1/1000) → 0.491492 (1/100) → 0.373757 (1/20)
  → 0.258117 (1/10); already BELOW 2/5 at ε = 1/20 and 1/10 — one decision-cell
  step right lands margin-straddle NULL, as the registration disclosed. ε = 0
  orbit gap = 1/12 ≈ 0.083 — the WSLS margin is noise-BORN.
- **Singular perturbation exhibit:** v(TFT,TFT) = 3 at the ε = 0 orbit vs
  exactly 9/4 for every grid ε > 0 — the discontinuity at ε = 0 is the
  sharpest statement of the echo tax.
- **vs-ALLD column (retaliation's real virtue):** TFT 1 vs WSLS 1/2 at ε = 0;
  TFT 510001/500000 vs WSLS 107/200 at ε = 1/100 — TFT still beats WSLS
  against pure defection even as its self-play collapses.
- **Nice subfield (c_CC = 1, restricted round-robin, 1/8 weights):** at
  ε = 1/100 WSLS ranks 1 and Grim-shaped (1,0,0,0) ranks 2; TFT ranks 6 of 8 —
  the folk claim fails even among nice rules under noise.
- **Presentation order:** seed 20261379 read by the Arm-R presentation
  shuffle only.

## Boundaries (as registered)

Execution trembles, not misperception (a different kernel — named follow-up);
the uniform COMPLETE field with self-play (the honest strategy-space reading
of "the best"; ALLD's table-top is not an equilibrium claim —
replicator/ecological dynamics on this same exact table is the named
follow-up); long-run average payoff (irreducible chains, start-independent;
discounting re-admits first-move effects — named follow-up); deterministic
memory-one rules only (mixed/zero-determinant strategies — named follow-up).

## Transferable correction (pre-registered REJECT consequence, verbatim-faithful)

1. A strict mirror rule pays a permanent 25% cooperation tax at ANY nonzero
   error rate — ε-independent; lowering the error rate does not shrink it.
2. Repair beats retaliation under noise: add a WSLS-shaped "after a bad round,
   change something" clause; do not chase a lower ε. Transfer surface:
   anywhere the fleet codifies counterparty-mirroring under fallible
   observation (retry/backoff handshakes, respond-in-kind review/trust rules,
   any echo-the-counterparty protocol). Routing is the manager's per Q-0260 —
   this repo edits no other repo; nothing here builds, publishes, or spends.

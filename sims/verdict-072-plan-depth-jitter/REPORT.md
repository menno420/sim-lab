# VERDICT 072 — REPORT — plan-depth refill jitter: the Q-0164 "DEPTH >= the cadence" bar under the marker-reset-to-latest convention (INTAKE 061)

**Class: REJECT** (pre-registered rules applied in order: REJECT → INVALID →
APPROVE → NULL; REJECT checked FIRST fires on all three conjuncts).

Source: idea-engine `## PROPOSAL 061 · 2026-07-14T06:33:02Z · status: sim-ready`
(idea-engine PR #408 @ main 02ea4ce; idea doc
`ideas/superbot/plan-depth-refill-jitter-2026-07-14.md`; where the doc and
the block differ, the block wins — no disagreement found). Fully hermetic:
every fixture constant pinned in the PROPOSAL 061 block / idea doc, copied
verbatim into the committed `fixtures.json`; the runner reads only that
file; zero repo/network reads at verdict time. The drafter's disclosed
prototype landing was re-derived from scratch with ZERO trust and compared
NEVER gated.

## Reproducibility

- `SELF-CHECKS: 37 passed, 0 failed`, exit 0, ~18 s/run, stdlib-only,
  hermetic (reads only its own `fixtures.json`), CPython 3.11 pinned and
  asserted.
- Byte-identical across two full process runs by external `diff` + sha256:
  `run-stdout.txt` = `973e0382e129a8da985c2b4d00adf1b51fc03523d3a83735fbdbf4781ed1f936`,
  `results.json` = `9b6e37bd90a9e7c53212e3c8b41c7bf837518fa7c33558cc46999aa6d8e0cee6`.
- Seeds: 20261381 main / 20261382 stability / 20261383 presentation — the
  ONLY three RNGs constructed (asserted, pinned order); aux 20261384 NEVER
  read (asserted against the constructed-seeds registry).
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run. Fixtures committed BEFORE the runner (git trail: fixtures
  b87d985 precede the runner commit).
- Every decision number is a seedless exact `fractions.Fraction`; the seeded
  Arm-R legs are REPORTING-ONLY and carry no statistical gate (their only
  gates: the 1 + N + ΣW draw sentinel, exact at 3,100,002 main + 619,998
  stability calls, and byte reproducibility) — joint gate pass probability 1
  for a correct implementation, as registered.

## Decision conjuncts (registered order, REJECT first — all three FIRE)

1. **Dry rate:** p_dry(S = 30, q = 9/10, L0) =
   `1101510756549069125820660830403305561487141/6250000000000000000000000000000000000000000`
   ≈ 0.176242 ≥ 1/20 exact (clears the line by 3.52×). The committed
   depth-30 bar dries in more than a sixth of refill cycles at the pinned
   jitter.
2. **Safe depth:** S*(9/10, L0) = 39 = cadence + 9 ≥ 33, by exact scan over
   S ∈ [0, 60]; published bracket p_dry(38) ≈ 0.018095085 > 1/100 >
   p_dry(39) ≈ 0.008070362. The honest 1%-safe depth is cadence + lateness
   headroom (max L0 lateness = 12; 39 ≈ 30 + max-lag at the pinned mix).
3. **Dry-span fraction:** E[drained span]/30 =
   `69538814667382134710773264045511718415683/2500000000000000000000000000000000000000000`
   ≈ 0.027816 ≥ 1/50 exact (the thinnest clause, 1.39× over its line, as
   the registration disclosed). Expected drained span ≈ 0.834466 PRs/cycle
   at the decision cell.

APPROVE was arithmetically foreclosed (mutually exclusive on every clause).
Falsifiability behaved as registered: the PROMPT mix HOLDS the committed bar
(p_dry(30) ≈ 0.009538011 < 1/100, S*(PROMPT) = 30 exactly — the committed
rule is exactly right when passes land promptly), and the q = 3/5 column
lands APPROVE-side (p_dry(30, 3/5, L0) ≈ 0.002367 < 1/100 — a docs-heavy
merge mix dissolves the fragility).

## Gates (all green)

- **F1** model & mechanism identities: all three lag pmfs sum to 1 exactly;
  window pmfs sum to 1; binomial rows sum to 1 at every in-play window ×
  every grid q; the window closed form W = 30 − ℓ_prev + ℓ_cur reproduced
  EXACTLY by a direct event-walk of the verbatim committed trigger
  arithmetic (`latest // 30 > marker // 30`, marker := landing count) over
  every lag pair at two marker bases; mean-window conservation
  Σ P(pair)·W = 30 exact on all three mixes.
- **F2** the forgiveness theorem: p_dry(S = 30) = 0 EXACTLY under every
  constant lag c ∈ {0, 1, 3, 6, 12} at every grid q, both arms — ANY steady
  lateness is exactly forgiven by the reset-to-latest marker convention.
- **F3** the q = 1 identity: p_dry(30, q = 1, mix) = P(ℓ_cur > ℓ_prev)
  exactly — L0: 19/50, PROMPT: 1/4, HEAVY: 25/64, all matching the pinned
  references.
- **F4** the committed-incident anchor: at the old horizon S = 9 with
  constant lag (W = 30), E[drained span] =
  400000000000000006053440257869/20000000000000000000000000000
  ≈ 20.0000000003 ∈ [18, 22] at q = 9/10, and = 21 exactly at q = 1 — the
  harvested "drained the queue ~20 PRs before each refill" retrodicted from
  first principles.
- **F5** hand world (K = 4, S = 2, q = 1/2, lag uniform {0, 1}): windows
  {3, 4, 5} w.p. {1/4, 1/2, 1/4}, tails {1/8, 5/16, 1/2}, p_dry = 5/16 —
  all reproduced exactly, both arms, trigger walk included.
- **F6** battery: Arm B (independently-written queue-level DP event-walk)
  exact-equal on every published cell — all 84 surface cells × 3 metrics,
  all 12 scan-bracket cell pairs, the full 3 × 61 decision-q scan columns,
  the F2/F4/F5 cells; twin decision evaluators (evaluator 2 recomputes
  p_dry/S*/span-fraction from a fresh Arm-B pass) agree on the token
  REJECT/REJECT; draw sentinels exact; aux seed never read; byte-identical
  double run; CPython minor pinned.

## Anomalies (first-class findings)

1. **"Per dry cycle" wording (drafter disclosure mislabel, ruling-neutral).**
   The PROPOSAL 061 block discloses "dry consuming-arrivals ≈ 0.751 per dry
   cycle"; the computed 0.751019198 is the UNCONDITIONAL per-cycle
   expectation E[max(0, Bin(W, q) − S)] (the idea doc's own "per-cycle
   dry consuming-arrivals ≈ 0.751" wording is correct). Conditional on a dry
   cycle the expected stranded arrivals are 8202042300415/1924773766366 ≈
   4.261302 — the average dry cycle strands over FOUR plan slices' worth of
   dispatch fires, not "most of one" (the idea doc's parenthetical gloss).
   No decision clause reads this quantity; reported, not smoothed over.
2. None other. Every other drafter-disclosed value reproduced from scratch:
   the decision-cell p_dry digit-for-digit at 43 numerator digits, S* = 39
   with both brackets, span fraction 0.027816, PROMPT 0.009538 / S* 30,
   HEAVY S* 50, q = 3/5 cell 0.002367, S = 9 dry share 0.9999993 and span
   ≈ 20.0, S = 20 dry share 0.909, E[W] = 30 — see
   `drafter_comparison_never_gated` in results.json.

## Reporting legs (ungated)

- **Arm R mechanism trace** (literal counter/marker/trigger walk at the
  decision cell, reporting-only as registered): main leg (20261381,
  N = 100,000) p_dry_hat off the exact value by ≈ 0.00185, span-fraction
  off by ≈ 0.00036; stability leg (20261382, N = 20,000) p_dry off by
  ≈ 0.00136. Draw sentinels exact: 3,100,002 and 619,998 uniforms
  (= 1 + N + ΣW each). No drift finding — the trace sits on the exact law
  well within MC noise.
- **Safe-depth table (q = 9/10):** S*(L0) = 39, S*(PROMPT) = 30,
  S*(HEAVY) = 50; at q = 1: S*(L0) = 42 (full 12-cell table with brackets
  in results.json).
- **Old committed worlds:** S = 9 dries in ≈ 99.99993% of cycles (expected
  drained span ≈ 20.0 — the Q-0164 incident); the pre-Q-0134 row S = 20
  still dries in ≈ 90.89% of cycles.
- **Dry arrivals:** ≈ 0.751 per cycle / ≈ 4.261 per dry cycle at the
  decision cell (see Anomaly 1).
- **Presentation order:** seed 20261383 read by the stdout
  presentation-shuffled surface listing only.

## Boundaries (as registered)

The lag mix is INVENTED-pinned-disclosed, two-sided (PROMPT holds the bar,
HEAVY breaks it worse: S* = 50) — the free measured replacement is named:
the marker residue N mod 30 committed in every pass record IS the realized
lateness ledger. Consumption is i.i.d. Bernoulli (burst correlation fattens
the tail REJECT-ward, stated never simulated). Merged-PR time (PR-number
gaps shorten real windows — APPROVE-ward for dryness, the checker's own
caveat). Dry = the committed degraded state (unplanned dispatch fires + the
⚠️ PLAN BACKLOG THIN escalation), never an outage — Q-0172 self-promotion
is the committed fallback. Single-band lag regime only (support < 30): the
ROUTINE_PAT-lapse ≥ 1-band stall class is excluded by construction, named
follow-up. APPLICATION GUARD: the verdict conditions on the committed
constants @ 50481b7 (STEP = 30, the ~30-PRs bar, the reset-to-latest
convention) — a retuned STEP, changed reset convention, or stock-triggered
refill means re-run, not reuse.

## Transferable law (pre-registered REJECT consequence, verbatim-faithful)

"Depth = cadence" is safe against STEADY lateness and unsafe against
GROWING lateness: the marker-reset-to-latest convention cancels constant
lag EXACTLY (F2, an unstated virtue now provable — do not "fix" it into a
crossing-reset that would break the forgiveness) and conserves mean cadence
exactly (E[W] = 30 on every mix); dryness at depth = cadence is precisely
P(lateness grew) at q = 1. The fix is headroom (1%-safe depth = 39 ≈
cadence + max lateness at the pinned mix) or measurement (read the free
marker-residue ledger), never a faster scheduler. Transfer surface: every
count-or-cadence-triggered refill loop in the fleet (idea-engine's ORDER
003 never-dry duty, manager wake-chain queues, venture kill-clock
checkpoints). Routing is the manager's per Q-0260 — this repo edits no
other repo; nothing here builds, publishes, or spends.

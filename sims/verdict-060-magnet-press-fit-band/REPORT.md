# REPORT — VERDICT 060: the magnet press-fit band (PROPOSAL 049)

**Ruling: reject** — per the pre-registered rule, evaluated IN ORDER, REJECT
FIRST, on Arm A's exact Fractions.

- **REJECT (checked FIRST) FIRES:** `FAIL(15) = 145/861 ≈ 0.168409 > 1/10`
  (margin over the band: `145/861 − 1/10 = 589/8610 ≈ 0.0684`). Across the
  pinned printer population the shipped `magnet_fit = 0.15` default misses
  the PRESS band in roughly one print in six — the fit line's "a firm
  press-fit on most printers" claim retires, and the honest instruction is
  the repo's own calibrate-first doctrine (print the tolerance coin, put
  YOUR row's number in `magnet_fit`).
- INVALID gate not reached for the ruling but evaluated: all seven control
  gates PASS (below) — the ruling is issued on healthy controls.
- APPROVE / NULL not reached.

Sharpening (a) — the default errs toward UNSEATABLE, the EXPENSIVE direction:
`UNSEAT(15) = 125/861 ≈ 0.145` vs `DROP(15) = 20/861 ≈ 0.023`. The repo's own
"a drop of glue fixes it" rescues a loose magnet but nothing un-cracks a
brittle one, so the glue-fallback view `FAIL_glue(15) = 125/861 ≈ 0.145`
barely improves on `FAIL(15)` while `FAIL_glue(5) = 20/861 ≈ 0.023` collapses.
Sharpening (b) — even the grid-best cell `F = 10` fails at `40/287 ≈ 0.139`:
at the pinned population width NO universal default is honest, which is
precisely the coin project's own doctrine.

## The question and the model (registered, hermetic)

Does the shipped diametral interference default land the as-printed joint in
the PRESS band? All lengths integer hundredths of a mm (cmm), DIAMETRAL.
Population: `H ~ U{0..40}` (systematic hole undersize, center = the coin
exemplar's `H₀ = ρ·S = 20`), `η ~ U{−10..+10}` (per-print noise),
`m ~ U{−5..+5}` (magnet diameter error), independent;
`I(F) = F + H + m − η`; DROPS-OUT iff `I < 10`, PRESS iff `10 ≤ I ≤ 50`,
UNSEATABLE iff `I > 50`; metrics as exact Fractions over the
`41 × 11 × 21 = 9,471`-cell equiprobable lattice.

## Arm A — exact Fractions (DECISION arm, seedless)

| F (cmm) | DROP | UNSEAT | FAIL | FAIL float |
|---------|------|--------|------|------------|
| 5 | 125/861 | 20/861 | 145/861 | 0.168409 |
| 10 | 20/287 | 20/287 | 40/287 | 0.139373 |
| **15 (shipped)** | **20/861** | **125/861** | **145/861** | **0.168409** |
| 20 | 5/1353 | 335/1353 | 340/1353 | 0.251293 |
| 25 | 0 | 15/41 | 15/41 | 0.365854 |
| 30 | 0 | 20/41 | 20/41 | 0.487805 |

`min_F FAIL = 40/287` at `F = 10`. `FAIL_glue(F) = UNSEAT(F)` — the column
above. Two in-process Arm-A computations produced identical rationals; the
two full process runs are byte-identical (below).

Per-H conditional `FAIL(15 | H)` (which printers the default fails): zero for
`H ∈ {10..20}` (the calibrated middle), rising to `5/21 ≈ 0.238` at `H = 0`
(loose printers → DROP) and `5/7 ≈ 0.714` at `H = 40` (tight printers →
UNSEAT); the full 41-point curve is in `results.json` / `run-stdout.txt`.

## Controls gate (INVALID if any fails) — all PASS

- Zero-noise identity (seed 20261334, `η ≡ 0, m ≡ 0, H ≡ 20`): PRESS with
  probability EXACTLY 1 at every grid F in BOTH arms (exact identity — Arm A
  Fraction 1; Arm B 20,000/20,000 at every cell). PASS.
- Monotonicity theorems: DROP non-increasing and UNSEAT non-decreasing in F,
  on Arm A's exact table AND on Arm B's common-random-numbers counts. PASS.
- Arm-B agreement on every grid cell. PASS (table below).

## Arm B — seeded MC validation (seed 20261333, N = 200,000, CRN across all six F)

Pinned draw order H → m → η; gate per cell `|FAIL̂ − FAIL| ≤ 1/100` absolute
(exact Fraction comparison) AND `≤ 4·se`, `se = √(p_A(1−p_A)/N)`.

| F | FAIL̂ | exact | \|dev\| | 4·se | result |
|---|-------|-------|--------|------|--------|
| 5 | 0.168745 | 0.168409 | 0.000336 | 0.003347 | PASS |
| 10 | 0.139705 | 0.139373 | 0.000332 | 0.003098 | PASS |
| 15 | 0.168475 | 0.168409 | 0.000066 | 0.003347 | PASS |
| 20 | 0.250430 | 0.251293 | 0.000863 | 0.003880 | PASS |
| 25 | 0.366275 | 0.365854 | 0.000421 | 0.004308 | PASS |
| 30 | 0.487645 | 0.487805 | 0.000160 | 0.004471 | PASS |

## Stability leg (seed 20261336, N = 20,000)

`FAIL̂(15) = 3367/20000 = 0.168350` — the ruling class (reject) reproduces
through BOTH twin independently-written evaluators (one Fraction-based, one
pure-integer cross-multiplication; they agree on the provisional class, the
stability class, and the final verdict). PASS.

## Sensitivity worlds (seed 20261335, N = 20,000 each, REPORTING-ONLY — never flip the decision)

| world | FAIL(15) exact | float | reject-edge side | straddle |
|-------|----------------|-------|------------------|----------|
| H narrow {10..30} | 20/441 | 0.045351 | at-or-below | **yes** |
| H wide {−10..50} | 440/1281 | 0.343482 | above | no |
| η narrow {−5..+5} | 675/4961 | 0.136061 | above | no |
| η wide {−20..+20} | 455/1681 | 0.270672 | above | no |
| m degenerate {0} | 45/287 | 0.156794 | above | no |
| m wide {−10..+10} | 3565/18081 | 0.197168 | above | no |
| I_hold = 5 | 470/3157 | 0.148876 | above | no |
| I_hold = 15 | 185/861 | 0.214866 | above | no |
| I_seat = 40 | 335/861 | 0.389082 | above | no |
| I_seat = 60 | 40/861 | 0.046458 | at-or-below | **yes** |

Every world's MC confirmation passed on all six cells. The two straddles are
the registration's own disclosed falsifiability exhibit: the narrow-population
and `I_seat = 60` worlds land `≈ 0.045–0.046`, inside the APPROVE/NULL region
— REJECT is a property of the pinned population width, and the rule would
rule differently at nearby pins. Reporting-only: the ruling rides rule 1,
which fired first; no straddle axis is in play.

## Remedy-direction inversion flag (reporting-only, decidable by inspection, NEVER gated)

Line-83 geometry `pocket_d = magnet_d - magnet_fit` means RAISING
`magnet_fit` makes the pocket SMALLER (tighter) — yet both shipped remedy
texts point the dial the other way ("Won't go in? Raise it (e.g. 0.25)" /
"Drops out? Lower it"; the README repeats it). Each remedy as written makes
its failure WORSE. Routes lane-side as a one-line doc fix per Q-0260 — this
repo never edits curious-research files.

## Drafter reference comparison (reporting-only, never gated)

The from-scratch re-derivation reproduces the idea doc's disclosed hand check
EXACTLY on all eleven disclosed quantities (FAIL at all six F; the DROP/UNSEAT
splits at F = 5, 10, 15) — no drafter arithmetic error found. The disclosed
sensitivity approximations (`≈ 0.045` narrow-H, `≈ 0.046` I_seat = 60) also
match the exact values `20/441` and `40/861`.

## Reproduction

```
python3 sims/verdict-060-magnet-press-fit-band/magnet_fit_sim.py
```

One command, no flags, stdlib-only, hermetic (reads only its own
`fixtures.json`), CPython 3.11 pinned and asserted, ~1.2 s/run. 43
self-checks, 0 failed, exit 0. Seeds 20261333–336 are the ONLY four RNGs
constructed (asserted, pinned order), strictly above the P048/V059 high-water
20261332 — new registry high-water 20261336. Per-leg draw sentinels exact:
headline 600,000 / zero-noise control 60,000 / sensitivity 600,000 /
stability 60,000. stdout + `results.json` byte-identical across two full
process runs by external sha256 — no wall-clock in any output:

- `run-stdout.txt` sha256 `1c69ce85f8bedad7207e4ee8a7bf776a5349b338b255d17f484cd90e2f0b2141`
- `results.json` sha256 `3991657e86abda01971ef90c14bd0d1e225168b1c9f27e8b5c5f5098a45a9500`

## Limits

Model-true under the registered frame, not a bench measurement: the H span,
η, m, I_hold, I_seat widths are INVENTED-but-pinned (no bench datapoint for
the magnet tool exists anywhere in the fleet — the scad has never been
rendered, by its own header); every one carries a registered sensitivity
pair, and the sweeps bracket scale, not shape. `ρ = 1/2` (the hole's share of
the coin pair's offset) is a disclosed CHOICE bracketed by the H pair; the
coin calibrates printed-on-printed while this joint is
printed-on-ground-steel, which is why only the hole's share enters.
Independence of H, m, η is an assumption — slicer/firmware hole compensation
is the named most-likely-to-flip alternative (shifts the center down, trading
UNSEAT for DROP; the wide-H leg brackets it, and it lands REJECT-side at
0.343 anyway). The `4·se` Arm-B tolerance is float arithmetic by
registration; every decision comparison is an exact Fraction or pure-integer
cross-multiplication. The cheapest live probe stands as pre-priced: ONE
tolerance coin + ONE magnet cup on the owner's printer plus the repo's own
hand-fit test pins H and both band edges for the one printer that matters
first.

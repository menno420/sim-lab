# REPORT — VERDICT 059: Parrondo's paradox at a conservative discrete pin (PROPOSAL 048)

**Ruling: approve** — per the pre-registered rule, evaluated IN ORDER, REJECT
FIRST, on Arm A's exact Fractions.

- **REJECT (checked FIRST) does NOT fire:** `D_mix = 26673/4429850 ≈ +0.006021 > 0`
  — the paradox manifests at the conservative pin.
- **INVALID gate does NOT fire:** both isolated-loss preconditions hold —
  `D_A = −1/50 = −0.0200 < 0` (Game A losing) and
  `D_B = −1529/87950 ≈ −0.017385 < 0` (Game B losing under its own stationary
  law). The premise "two LOSING games" is live, not vacuous.
- **APPROVE fires:** `D_mix = 26673/4429850 ≥ 1/1000` (margin over the band:
  `22243190/4429850000 ≈ 0.005021`, ≈ 6.02× the material threshold) AND the
  seed-20261332 stability leg reproduces both the sign
  (`D̂ = +0.008090 > 0`) and the `≥ 1/1000` margin
  (`1618/200000 ≥ 1/1000`, exact Fraction comparison) AND all four Arm-B legs
  land within `4·se` of Arm A.
- NULL not reached.

Two individually-losing games DO combine into a winner at `EPS = 1/100` —
twice the textbook bias — and the margin is material (≈ 0.60%/step, ≈ 6× the
registered `1/1000` band). But the pin sits close to the cliff: the
reporting-only sweep shows the paradox is already DEAD at the very next
registered lattice point (`EPS = 3/200` → `D_mix ≈ −0.00366`).

## Arm A — exact rationals (DECISION arm, seedless)

| quantity | exact Fraction | float |
|----------|----------------|-------|
| `D_A` (pure A) | `−1/50` | −0.020000 |
| `D_B` (pure B) | `−1529/87950` | −0.017385 |
| `D_mix` (random 1/2–1/2) | `26673/4429850` | +0.006021 |

Stationary residue distributions (the ratchet mechanism, reporting-only):

- `π_B = (673/1759, 1633/10554, 4883/10554) ≈ (0.3826, 0.1547, 0.4627)` —
  Game B alone parks **38.3%** of its time in the bad residue 0 (uniform
  would be 33.3%): the dynamics funnel it into its own bad state.
- `π_mix = (30529/88597, 1186/4663, 35534/88597) ≈ (0.3446, 0.2544, 0.4011)`
  — mixing in Game A reshuffles occupancy: bad-state time drops to **34.5%**,
  the good coins are visited more, and the drift flips sign.

Both Arm-A computations in-process produced identical rationals; the two full
process runs are byte-identical (below).

## Arm B — seeded MC validation (never decision-bearing beyond the validity conjunct)

`N = 200,000` per leg, direct capital simulation (`capital mod 3` branching,
pinned draw order, exact draw sentinels: mixed legs 400,000 draws, pure legs
200,000 draws).

| leg | seed | D̂ | Arm A exact | \|dev\| | 4·se | result |
|-----|------|----|-------------|--------|------|--------|
| mixed headline | 20261329 | +0.006420 | +0.006021 | 0.000399 | 0.008944 | PASS |
| pure-A control | 20261330 | −0.017640 | −0.020000 | 0.002360 | 0.008943 | PASS |
| pure-B control | 20261331 | −0.015660 | −0.017385 | 0.001725 | 0.008943 | PASS |
| stability | 20261332 | +0.008090 | +0.006021 | 0.002069 | 0.008944 | PASS |

Stability leg: sign reproduced AND `1618/200000 ≥ 1/1000` — PASS. Both
losing-control legs confirm their preconditions empirically with the correct
sign.

## Reporting-only side pins (never gate the ruling)

**Critical-EPS sweep** — where the paradox dies:

| EPS | D_mix (exact) | float | sign |
|-----|---------------|-------|------|
| 1/100 | 26673/4429850 | +0.006021 | **positive** |
| 3/200 | −8109/2214800 | −0.003661 | negative |
| 1/50 | −9851/738275 | −0.013343 | negative |
| 1/40 | −51/2215 | −0.023025 | negative |
| 1/25 | −115404/2216425 | −0.052068 | negative |

The critical boundary lies in `(1/100, 3/200)`: the registered pin is the
LAST surviving point of the registered lattice. The robustness margin is
thin — a 50% increase in the bias kills the paradox.

**Periodic `[A,A,B,B]` comparator** (12-state phase×residue product chain):
`D = 59892253498512/12578166446889025 ≈ +0.004762` — positive too, so the
effect is not an artifact of the random mixing rule (random 1/2–1/2 beats
this periodic pattern at this pin, 0.006021 vs 0.004762).

**Drafter reference comparison** (reporting-only, never gated): the sim's
from-scratch re-derivation reproduces the idea doc's disclosed hand check
EXACTLY on all five quantities (`D_A`, `D_B`, `D_mix`, `π_B`, `π_mix`) — no
drafter arithmetic error found.

## Reproduction

```
python3 sims/verdict-059-parrondo-lattice/parrondo_sim.py
```

One command, no flags, stdlib-only, hermetic (reads only its own
`fixtures.json`), CPython 3.11 pinned and asserted, ~0.2 s/run. 346
self-checks, 0 failed, exit 0. Seeds 20261329–332 are the ONLY four RNGs
constructed (asserted, pinned order), strictly above the V058 high-water
20261328 — new registry high-water 20261332. stdout + `results.json`
byte-identical across two full process runs by external diff — no wall-clock
in any output:

- `run-stdout.txt` sha256 `879874c01a44541fc43932564a16f10b1b67441efdba6d985050b733adb66f26`
- `results.json` sha256 `fce31e076ff0c41216bd0c762890ad203894531389d476a138a0ebc13195cac4`

## Limits

Model-true under the registered frame: the ruling is on LONG-RUN drift (the
renewal rate) of the pinned Harmer–Abbott structure (`M = 3`, coin triple
`(1/2, 1/10, 3/4)` shifted by `EPS`); finite-capital ruin, variance, and
first-passage behavior are out of scope by registration. `EPS = 1/100` is a
pinned CHOICE — the bands quantify only over this pin, and the sweep
discloses the cliff at `3/200`. The `4·se` Arm-B tolerance is a float
computation (registered as such); every decision comparison is an exact
Fraction or pure-integer cross-multiplication.

# verdict-101 · berkson-admission-collider

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 088
(`## PROPOSAL 088 · 2026-07-16 · status: sim-ready`, registered spec
`berkson-admission-collider-2026-07-16`). P088 → V101 under the constant +13
PROPOSAL↔VERDICT offset (the P087 → V100 precedent).

The head prices a causal-inference folk belief: "the novel work we ship is less rigorous
and the rigorous work is less novel, so there's a real tradeoff." The claim is that this
apparent tradeoff is **Berkson's paradox** — a pure selection artifact. Two INDEPENDENT
latent axes, novelty `N` and rigor `R`, each iid `Normal(0,1)` drawn from SEPARATE PRNG
streams, so `corr(N,R) = 0` in the population BY CONSTRUCTION. Admission is a DISJUNCTIVE
collider gate — admit iff `N ≥ t OR R ≥ t` — and conditioning on that common effect of two
independent causes opens a spurious NEGATIVE correlation among admitted items: a low-novelty
admit must have been carried by rigor, and vice versa, so low-on-one pairs with high-on-the-
other. The artifact STRENGTHENS as admission tightens (a dose-response), and a SINGLE-gate
control (admit on `N` alone) induces ZERO correlation — isolating the disjunction as the sole
cause.

On a pinned world (n = 2000 items/run, seeds S = [1,2,3,4,5]) each seed draws
`N = [random.Random(seed).gauss(0,1) …]` and `R = [random.Random(seed+10000).gauss(0,1) …]`
from two separate streams (the +10 000 offset guarantees no shared draws). OR-gate
thresholds are calibrated so the marginal admit rate hits target `T`: with independent axes
the OR admit rate is `1 − (1−p)²`, so `p = 1 − √(1−T)` and `t = Φ⁻¹(1−p) = Φ⁻¹(√(1−T))`.
Levels `T ∈ {0.50, 0.25, 0.10}` (reference `T = 0.25`); the single-gate control uses
`a = Φ⁻¹(1−0.25) = Φ⁻¹(0.75) = 0.674490`. `Φ⁻¹` is Acklam's stdlib rational approximation
(no numpy/scipy) and Pearson `r` is pure stdlib. P088 pre-registered an APPROVE rule
requiring ALL four gates R1–R4. The measured run APPROVES: `ρ_full` pooled mean +0.000251
(R1), `ρ_OR@25` pooled mean −0.587329 clearing −0.45 by 20.97σ (R2), a strictly monotone
dose-response −0.457816 (50%) > −0.587329 (25%) > −0.685281 (10%) with adjacent separations
14.34σ / 8.92σ (R3), and a single-gate control at −0.013478 inside the null band and 43.35σ
from the OR effect (R4). All numbers reproduce the proposal's disclosed dry-sim from an
INDEPENDENT re-implementation — VERDICT **APPROVE**, first failing gate None.

## Run (one command)

```
python3 berkson_admission_collider_sim.py
```

Exit 0 iff every self-check passes (10/10) AND the twin evaluators agree AND the achieved
admit rates are valid. Deterministic: `results.json` and `run-stdout.txt` are byte-identical
across process runs — no wall clock, no network, no git at run time. Stdlib only, CPython 3.
The RNG is two `random.Random` instances per seed over the in-file seed constants
S = [1,2,3,4,5], one for each axis; the +10 000 offset on the R stream is what makes the two
axes independent by construction.

## Structure — two gates + twin evaluators

- **OR-collider gate** — admit iff `N ≥ t OR R ≥ t` at the three calibrated thresholds
  `t(50%) = 0.544952`, `t(25%) = 1.107798`, `t(10%) = 1.632219`. The admitted set is the
  L-shaped union of two half-planes with the low-low corner carved out; the scatter over that
  L tilts down-right, so `ρ_admit` goes negative even though the population `ρ` is zero. This
  is the head's effect (R2) and dose-response (R3).
- **Single-gate control** — admit iff `N ≥ a` ALONE (`a = 0.674490`, matched to the same
  ≈25% marginal admit rate). Selecting on `N` alone says nothing about the independent `R`, so
  `ρ_single ≈ 0`. This is the falsifier (R4): if the single gate ALSO anticorrelated, the
  "disjunctive collider" mechanism claim would be false → REJECT.
- **Φ⁻¹ (Acklam)** — inverse standard-normal CDF via the rational approximation, verified
  against `Φ⁻¹(0.975)=1.959964`, `Φ⁻¹(0.75)=0.674490`, `Φ⁻¹(0.8660254)=1.107798` to 6dp; the
  four calibrated thresholds are re-verified to 6dp each run.
- **Twin evaluators** — an if-chain scorer and an independently transcribed table-driven
  scorer agree on the ruling token AND the first-failing gate over the measured gate outcomes
  — APPROVE/None both. A divergence fails the run (exit ≠ 0).

## Decision rule (pre-registered, from P088)

**APPROVE iff R1 AND R2 AND R3 AND R4**, the rule firing in order R1→R2→R3→R4.

- **R1 null anchor:** `|pooled mean(ρ_full)| ≤ 0.03` AND `|mean| + 3·SE ≤ 0.03` (≥3σ INSIDE
  the null band). Verifies the population is the stable zero-correlation regime.
- **R2 effect @ T=0.25:** pooled `mean(ρ_OR) + 3·SE ≤ −0.45` (clears the −0.45 anticorrelation
  floor by ≥3σ).
- **R3 dose-response:** `mean ρ_OR` at 50% > 25% > 10% (strictly more negative as admission
  tightens), each adjacent pair separated by `|mean_a − mean_b| / √(SE_a² + SE_b²) ≥ 3`.
- **R4 mechanism isolation:** single-gate pooled `|mean(ρ_single)| ≤ 0.03` on the POOLED-MEAN
  reading, AND `|mean_OR@25 − mean_single| / √(SE_OR25² + SE_single²) ≥ 3`.

**Disclosed correction (from the spec).** R4 is registered on the pooled-MEAN reading, NOT
R1's stricter ≥3σ-inside test. The single-gate control estimates a quantity that is exactly
zero, but with ≈500 admitted items/seed the per-seed Pearson noise is ≈0.045, so the pooled 3σ
envelope (`|mean|+3·SE = 0.047985`) pokes just past 0.03 — expected and disclosed, NOT applied
to R4. The decisive R4 clause is the 43.35σ separation from the OR effect.

- **REJECT** — R4 single-gate control ITSELF anticorrelates (fails the band), OR R1 anchor
  unstable, OR R3 non-monotone dose-response.
- **NULL** — R2 sub-threshold (the effect is real but doesn't clear −0.45 by ≥3σ): a finalized
  finding, not a re-run.
- **INVALID** — non-deterministic (the two process runs are not byte-identical), achieved
  admit rates miss targets (`|achieved − T| > 0.02`), or shared-stream `ρ_full ≠ 0`.

`SE = σ/√5` with `σ` = sample SD (ddof=1) across the 5 per-seed ρ. Full grammar and the
pinned world in `fixtures.json`.

## Layout

- `fixtures.json` — the pinned world (n, seeds, +10 000 offset, levels, reference T), the
  pre-registered gates and decision rule, the source proposal header, the four calibrated
  thresholds (+ their 6dp expectations), and the seed-1 reference-stringency (25% OR-gate)
  admitted-subset size (537) with the first-20 admitted (N,R) pairs full-precision via `repr`
  (the committed fixture, re-verified each run).
- `berkson_admission_collider_sim.py` — the single runner (`build_fixture` path + self-check
  `main`).
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs (byte-identical
  across a double run).
- `REPORT.md` — the verdict report (per-seed + pooled ρ table, σ margins, sha256 digests of
  the double run).

**VERDICT: APPROVE** (first failing gate None) — 10/10 self-checks, exit 0, byte-identical
double run, twin evaluators agree APPROVE/None.

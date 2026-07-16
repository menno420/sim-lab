# verdict-093 · cycle-following-coupling-lever

The joint-vs-marginal gap of success events coupled through one random
permutation's cycle skeleton. Answers idea-engine PROPOSAL 080
(`## PROPOSAL 080 · 2026-07-16T02:41:50Z · status: sim-ready`, idea
`ideas/fleet/cycle-following-coupling-lever-2026-07-16.md` — the round-16
COMPLETELY-UNRELATED rotation closer, the sixteenth fleet-external domain:
correlation design under shared randomness): with 2n players hunting their
own numbers in 2n boxes filled by ONE uniform permutation, is the folk
belief "marginals multiply into the joint; a strategy that moves no
marginal cannot move the group" priced exactly wrong? Five structure
theorems, re-derived from scratch: the LEVER (joint pointer success =
1 − Σ_{k=b+1}^{m} 1/k exactly for b ≥ n — ≈ 0.3118 at m = 100 vs the
independent product's 2⁻¹⁰⁰), MARGINAL INVARIANCE (every player exactly
b/m always), CONCENTRATION + FLOOR (≈ 72.66 of 100 fail together; P_n >
1 − ln 2 forever, rationally certified), the below-n BREAKDOWN of the
harmonic shortcut (exact inclusion-exclusion corrections), and the
ADVERSARY with its TWO REPAIRS (conjugation = cycle-type-frozen no-op
{720, 0, 720}; one-sided remap = full restoration 276/720 ×3).

## Run (one command)

```
python3 sims/verdict-093-cycle-following-coupling-lever/cycle_following_coupling_lever_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: stdout and `results.json`
are byte-identical across process runs (no wall clock, no paths, no
network, no git at run time). Stdlib only — this is a pure-math head (kin:
the P028/P032/P048/P060/P072/P076 exact-counting family); no vendor tree,
no third-party import anywhere. CPython 3.11 pinned and asserted (Arms A/B
are platform-independent exact arithmetic; only the reporting-only Arm R
and the presentation shuffle touch the pinned minor's `random` module).

## Layout

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  080 block / idea file, committed BEFORE the runner: the world and
  strategy pins, the three m = 6 adversary arrangements, the F3 census
  anchors, the typed contacts C1–C4, the Arm-R draw-order grammar with
  seeds 20261714–717 and both registered preview triples, and the
  pre-registered decision rule. Sim-chosen realizations (the decimal
  display convention, the ln-2 bracket depth K = 60, the m = 100
  adversarial witness rotation, the presentation-shuffle target) are
  disclosed as vacancy-derived fixtures, never match claims.
- `cycle_following_coupling_lever_sim.py` — the three-arm runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

## Arms

- **Arm A** — seedless exact closed forms (DECISION-bearing): the harmonic
  law 1 − Σ_{k=b+1}^{m} 1/k, the per-length law m!/k, the marginal law
  b/m, the below-n corrections m!/50 and m!/32, the decrement and
  alternating identities, the rational ln-2 bracket (Σ 1/(k·2ᵏ) + tail
  bound). Pure Fraction/integer arithmetic.
- **Arm B** — independently-written brute enumerations with their own
  cycle walker and bookkeeping: full permutation loops at m ∈ {4, 6, 8}
  (24 / 720 / 40,320), fixed-element cycle-length tables, the 720-σ
  one-sided-remap and conjugation loops on all three pinned arrangements,
  the same-set and independent-sets pencil enumerations — plus the
  cycle-type PARTITION census at m ∈ {8, 10} (the third counting method).
  Tied to Arm A through the typed must-equal contacts: **C1** the
  three-method counting triangle (10 / 276 / 14,736 / 1,285,920), **C2**
  per-length == (m−1)! summing to m!, **C3** repair censuses across ALL
  THREE arrangements (276 ×3; conjugation {720, 0, 720}), **C4** the
  below-n corrections (+10!/50 and +8!/32).
- **Arm R** — seeded random episodes, REPORTING-ONLY (no statistical
  gate): m = 100, one Fisher–Yates permutation per episode under the
  REGISTERED draw-order grammar (exactly m − 1 = 99 `randrange` draws,
  i = 99..1, one `random.Random` per seed). Seeds 20261714 (N = 20,000)
  and 20261715 (N = 8,000) with registered preview triples; presentation
  shuffle 20261716 (presentation legs only); aux 20261717 reserved and
  never read; draw-count sentinel exactly 99N.

Decision rule (registered order, evaluated by two independently-written
evaluators over an ENUMERATED boolean input set): REJECT → INVALID →
APPROVE → NULL, REJECT evaluated FIRST. Full grammar in `fixtures.json`.

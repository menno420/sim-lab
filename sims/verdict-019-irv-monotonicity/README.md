# verdict-019 · irv-monotonicity

How often does raising the winner make it lose? Answers idea-engine
PROPOSAL 017 (control/outbox.md 2026-07-13T00:59:58Z, idea
`ideas/fleet/irv-monotonicity-close-races-2026-07-13.md` @ `efc78ae`, landed
via idea-engine PR #281) — the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain
rotation slot's first head (social choice theory; fully hermetic by design:
zero repo/network reads, every fixture is integer combinatorics the sim
constructs itself). Under the pinned 3-candidate IRV rule (plurality-loser
elimination, pairwise final on full ballots, exact ties excluded and counted),
what fraction of elections exhibit an upward monotonicity violation (∃ X ≠ W,
t ∈ {X≻W≻Z, X≻Z≻W}, 1 ≤ k ≤ count(t) such that converting k ballots of t to
W≻X≻Z dethrones winner W) — measured as V_all and V_close (close := round-1
elimination margin ≤ 5% of n) in BOTH Arm E (exhaustive IAC — exact seedless
fractions) and Arm S (seeded IC Monte Carlo) — landing APPROVE / REJECT / NULL
per the decision rule registered before any code existed?

## Run (one command)

```
python3 sims/verdict-019-irv-monotonicity/irv_monotonicity_sim.py
```

Exit 0 iff all 19,494 self-checks pass. Deterministic — the only randomness is
`random.Random(<pinned seed>)` in a pinned loop order (Arm S; Arm E is
seedless by construction), no network, no git, no wall clock, no `hash()`.
stdout and `results.json` are byte-identical across process runs (verified by
external `diff` of three complete runs, cpython-3.11). Runtime ~18 s.

## Files

- `irv_monotonicity_sim.py` — stdlib-only driver: the pinned IRV evaluator
  (incremental-sums fast path), the exhaustive upward-violation search, Arm E
  full composition enumeration (n=25: C(30,5)=142,506 profiles; n=13: 8,568),
  Arm S seeded IC (n=99, M=200,000, seed 20260713; n=1,001, M=20,000, seed
  20260714), the exact-integer decision rule, 19,494 self-checks (independent
  dict/string re-implementation of BOTH the evaluator and the violation
  search, two full tiny-n enumerations incl. even-n pairwise-tie paths,
  hand-derived pinned elections, delta-table proofs, IAC candidate-symmetry
  exactness, RNG-stream reproduction from a fresh `Random(seed)`).
- `fixtures.json` — the pre-registration, committed BEFORE results: {n, M,
  seed} per arm, band constants (verbatim from the idea file), the pinned IRV
  rule / violation definition / close definition / tie handling, the decision
  rule and its consequences, and the two hand-derived pin elections with
  their full derivations.
- `results.json` — committed run output: all four legs {V_all, V_close, tie
  fraction, per-(X,t) breakdown}, decision detail, sensitivity flags, ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  019 ruling).

## Verdict (summary — full report in REPORT.md)

**null (pre-registered)** — the two standard neutral voter models land on
OPPOSITE sides of the pre-registered bands, so by the rule committed before
any code ran, NO ruling issues and the model-dependence itself is the citable
finding:

- **Arm E (exhaustive IAC, n=25 — exact, seedless):** V_close = 984/20,880 =
  **0.0471** (< 0.05, the REJECT side) · V_all = 1,464/130,716 = **0.0112**.
- **Arm S (seeded IC, n=99, M=200,000):** V_close = 16,583/98,983 =
  **0.1675** (≥ 0.10, the APPROVE side) · V_all = **0.1106**.
- The NULL is robust, not knife-edge: for APPROVE, Arm E would need V_close
  ≥ 0.10 (it measures 0.047 — 2.1× away); for REJECT, Arm S would need
  V_close < 0.05 (it measures 0.168 — 3.4× away).
- Size legs (sensitivity, cannot flip the decision): S-n1001 sits on the same
  side of every band as S-n99 (V_close 0.1232, V_all 0.1215); E-n13 is
  degenerate BOTH ways and flagged — its close set is empty by construction
  and its V_all is exactly 0 (upward violations are analytically IMPOSSIBLE
  at n=13; the sim's zero is a theorem, not sampling).
- Consequence (pre-registered): neither camp's soundbite may be cited as
  settled — "≪5% even when close" holds under IAC at n=25 and "double digits
  when it matters" holds under IC at n=99+, so any citation must name its
  voter model.

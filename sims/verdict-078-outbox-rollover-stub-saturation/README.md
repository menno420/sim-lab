# verdict-078 — outbox rollover stub saturation (INTAKE 065)

Prices idea-engine PROPOSAL 065's folk claim where it lives: "a
threshold-triggered archive roll keeps a live append-only file bounded
forever." In the pinned world (live file = header H0 + roll receipts +
pointer stubs + full blocks, all exact integer bytes; constants measured from
the fleet's own outbox rollover convention and pinned in the proposal), each
roll converts evicted b-byte blocks into s-byte stubs that never leave and
appends its own permanent h_r-byte receipt — so the post-roll floor rises
monotonically, roll spacing decays to thrash, and the live file has a
computable saturation wall N*. Judged against pre-registered bands at the
decision cell (P-STUB, T = 204800, s = 530, b = 16000, W = 2, h_r = 1000,
H0 = 500): REJECT-first (N*_stub ≤ 300 AND ≥ 8 thrash rolls with spacing ≤ 2
AND N*_range ≤ 4 × N*_stub while P-COMPACT holds a constant floor over
100,000 appends), APPROVE (N*_stub ≥ 500 AND every one of the first 20
spacings ≥ 4), NULL otherwise on named axes, INVALID on any F1–F6 gate
failure. Three hand-proved structure theorems ride as gates: FLOOR LAW +
roll-timing invariance, RECEIPT-FREE INVARIANCE (wall = ceil((T − H0)/s),
b-invariant — block-size discipline buys zero wall), COMPACT BOUNDEDNESS
(receipt-superseding range policy pins the floor at a constant forever).
Fully hermetic: the runner reads ONLY `fixtures.json` (committed before the
runner); zero repo/network reads at verdict time.

## Run

```
python3 sims/verdict-078-outbox-rollover-stub-saturation/rollover_stub_saturation_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). Stdlib-only. Every decision number is a seedless exact
integer; the only seeded arm (R) is reporting-only with NO statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 065
  block / idea doc (H0 = 500; h_r = 1000; the T grid {102400, 204800, 409600}
  with decision cell 204800; the s grid {265, 530, 1060} with decision cell
  530; the b grid {8000, 16000, 24000} with decision cell 16000; the W grid
  {0, 2, 8} with decision cell 2; the three policies P-STUB / P-RANGE /
  P-COMPACT; the roll-every-25 alternate timing schedule; the decision
  constants {300, 8, 2, 4×, 500, 4-of-first-20}; the F2–F5 anchors; Arm-R mix
  and replication counts; seeds 20261567–570), plus fixture-level conventions
  C1–C11 and the drafter's disclosed landing (compared, never gated) —
  committed BEFORE the runner existed. The F3 first-spacing expression slip
  is pre-identified there as anomaly A1.
- `rollover_stub_saturation_sim.py` — three-arm runner: Arm A seedless exact
  integer recurrence over the full grid (decision-bearing), Arm B
  independently-written literal byte-ledger simulator (exact-equal on every
  published number; second decision evaluator), Arm R seeded size-mix
  reporting-only walls.
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, wall tables, theorem verifications, gates, anomalies,
  reporting legs, boundaries, the pre-registered consequence.

## Ruling

See REPORT.md (written from the accepted run; the ruling token is issued by
the twin evaluators per the pre-registered order REJECT → INVALID → APPROVE
→ NULL).

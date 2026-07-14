# verdict-073 — owner-queue attention order (INTAKE 062)

Prices venture-lab's derived owner queue where it lives: the committed
presentation of `docs/publishing/OWNER-QUEUE.md` @ 68d57bb (decisions first —
"each with a bolded default so 'agree' is a one-word reply" — then the 44
click-run publish sequences in document order, 262 unchecked owner clicks, 16
hard-gated) as an owner-attention sequencing policy against the classical
alternatives — at idea-engine PROPOSAL 062's pinned model (5 policies DOC /
SPT / LPT / LAZY-DOC / LAZY-SPT × 2 decision-layer accountings BATCHED = 1 /
PER-ITEM = 19; metrics L_π(t), TTF, T22, MEAN, V_γ exact; γ grid {49/50,
99/100, 199/200}, decision cell 99/100). Fully hermetic: the runner reads
ONLY `fixtures.json` (committed before the runner); zero repo/network reads.

## Run

```
python3 sims/verdict-073-owner-queue-attention-order/owner_queue_attention_order_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). ~18 s/run, stdlib-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 062
  block / idea doc (the 44 name+count+gate rows with the 152/110/262/16/19
  identities, the 5 policy definitions, both accountings, the γ grid, the
  band constants, the sitting pmf, the F4 hand world, seeds 20261385–388),
  plus the fixture-level choices C1–C12 disclosed BEFORE the runner existed.
- `owner_queue_attention_order_sim.py` — three-arm runner: Arm A seedless
  exact integer prefix sums + `fractions.Fraction` V_γ (decision-bearing);
  Arm B independently-written tick-by-tick event-walk twin (exact-equal on
  every published number, powers the second decision evaluator); Arm R
  seeded REPORTING-ONLY owner-sitting traces on the pinned pmf {3: 1/2,
  8: 3/10, 21: 1/5} (main 20261385 at N = 100,000/policy, stability 20261386
  at N = 20,000, presentation shuffle 20261387; aux 20261388 NEVER read,
  asserted).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, per-conjunct results in registered order, theorems,
  reporting legs, boundaries.

## Ruling

**APPROVE** — all five pre-registered conjuncts hold at exact rationals
through the queue's own committed batch door: BATCHED gapMEAN = 72/11 ≈ 6.55
≤ 8 (MEAN(DOC) = 2835/22 vs best SPT 2691/22), ratioV(99/100) ≈ 1.0681 <
11/10, TTF 7 ≤ 2 × 4 — AND the batch door is load-bearing: forgoing the
one-reply "go with defaults" path at the SAME order costs +18 mean
interactions exactly and 25/7 ≈ 3.57× time-to-first-title (PER-ITEM gapMEAN
= 188/11 ≈ 17.09 ≥ 15, TTF 25 ≥ 4 × 5). The committed decisions-first +
document order is attention-near-optimal only THROUGH its batch reading —
the one-word reply is the load-bearing half of the design, not a
convenience. Disclosed live edge behaved as registered: the γ = 49/50
impatience leg lands ratioV ≈ 1.1341 ≥ 11/10 (reporting-only, named — one
attention-span step would cross the REJECT line), LPT anchors the worst
sort at 1624/11 ≈ 147.6, and the V020-exclusion leg re-lands every decision
clause identically.

# VERDICT 188 — the pie-rule opening trap (reproduce PROPOSAL 175)

## Probe report

Factual reproduction record for `ideas/superbot-games/pie_rule_opening_trap.py`
(idea-engine PROPOSAL 175, PR #665) copied byte-identical into sim-lab and run under
SEED=20260717. Every value below is the MEASURED value from this session's run
(`run-stdout.txt`), not a target restatement. Idea-engine reference read at main
`6dd9f3d`. Report generated 2026-07-19T16:17:40Z.

📊 Model: Claude

### 1. Does the verifier copy match the idea-engine source byte-for-byte?

MEASURED — YES. `diff ../idea-engine/ideas/superbot-games/pie_rule_opening_trap.py
sims/verdict-188-pie-rule-opening-trap/pie_rule_opening_trap.py` returned no output,
diff exit 0.

| Artifact | sha256 | git blob |
|----------|--------|----------|
| idea-engine source | `7e89f6908d835cb5d9c72de6c149926ac61b20043fd537d300c21827f12f4e39` | `ace21553a02343a058ed7f0a26bd58a05cd15daf` |
| sim-lab copy | `7e89f6908d835cb5d9c72de6c149926ac61b20043fd537d300c21827f12f4e39` | `ace21553a02343a058ed7f0a26bd58a05cd15daf` |

Both hashes equal the source exactly. Byte-identity confirmed.

### 2. Does the results-dict digest reproduce byte-exact?

MEASURED — YES, MATCH. Printed line:
`Results-JSON sha256: 72950442cc7509423256f28470c2281c9f79de3b601611b9feb931d083e8cb08`.
Disclosed digest:
`72950442cc7509423256f28470c2281c9f79de3b601611b9feb931d083e8cb08`.
Character-for-character identical — MATCH.

### 3. Is the run deterministic across invocations?

MEASURED — YES. Two separate `python3 pie_rule_opening_trap.py` invocations (both exit 0)
under `SEED=20260717` produced byte-identical stdout: cross-invocation
`diff run-stdout.txt run2.txt` exit 0. The verifier's own in-process double-run guard
(`main()` runs `run()` twice and `assert c1 == c2`, i.e. byte-identical compact-canonical
serializations) passed without triggering "in-process nondeterminism". Deterministic across
invocations and in-process.

### 4. Is the SEED honestly pinned?

MEASURED — YES. SEED=20260717 is a module-level in-source constant. Both invocations were
run with `SEED=20260717` exported into the environment; the printed digest is identical to
the disclosed value that was produced without any env override, confirming the env var is
inert (the file imports no `os` and reads no env var — each gate seeds its own
`random.Random(SEED + k)`). Determinism rests on the in-source seed alone.

### 5. Do all three gates pass in order with |z| ≥ 3.0?

MEASURED — YES, all three pass in order G1 → G2 → G3; `all_pass=true`,
`first_failing_gate=null`. Z_GATE=3.0; every measured |z| far exceeds it.

| Gate | Description | Metric | Measured | Pass rule |
|------|-------------|--------|----------|-----------|
| G1 | edge exists, NO rule (greedy-strongest, no swap) | win_rate | 0.900505 | > 0.5 by ≥ 3σ |
| G1 | opening_f = 0.9 | z_vs_half | 598.381968 | z ≥ 3.0 → pass true |
| G2 | the trap: naive-strong UNDER the swap rule | win_rate | 0.10111 | < 0.5 by ≥ 3σ |
| G2 | opening_f = 0.9 | z_vs_half | −591.72081 | z ≤ −3.0 → pass true |
| G3 | robustness, shifted catalogue: balanced win rate | opt_rate (opt_f=0.5) | 0.50116 | within 2pp of 0.5 |
| G3 | naive-strong win rate | naive_rate (naive_f=0.95) | 0.04946 | — |
| G3 | balanced − naive gap | gap_mean | 0.4517 | > 0 by ≥ 3σ |
| G3 | | z_gap | 370.907761 | z_gap ≥ 3.0 → pass true |

`opt_within_2pct_of_fair=true`, `all_pass=true`, `first_failing_gate=null`. No discrepancy
beyond float-rounding on any field.

### 6. Is the mechanism sound, not a strawman?

MEASURED — YES. Under the pie / swap rule the second player may take over the first
player's position instead of replying, so the first player's realized win probability from
an opening o is `min(f, 1 − f)`, where f is the mover's no-swap win probability from that
opening. The responder swaps whenever f > 0.5, so any advantage the opener builds is
handed straight to the responder. The realized-win maximizer is therefore f = 0.5 (a fair
game), and opening with the strongest, highest-f move is exactly the worst choice.

- G1 (200k games) shows a genuine first-move edge with NO rule: the greedy-strongest
  opening f=0.9 wins 90.0505% (z=598.38).
- G2 turns the swap rule on with the SAME naive greedy-strongest opening: realized win rate
  inverts to 10.111% (z=−591.72) — below fair by hundreds of sigma. The responder simply
  swaps into the 0.9-side, leaving the opener with 1 − 0.9 = 0.1.
- G3 (shifted catalogue 0.50/0.65/0.78/0.88/0.95) shows the fix is real, not a closed-form
  artifact: balanced play (opt_f=0.5) realizes 0.50116 — a fair game, within 2pp of 0.5 —
  and strictly dominates naive-strong play (naive_f=0.95 → 0.04946) by gap 0.4517
  (z_gap=370.91). Balanced dominates AND restores fairness.

### 7. Does grounding document the specific head?

MEASURED — live. WebFetch to https://en.wikipedia.org/wiki/Pie_rule resolved live this
session. The page (a) describes the swap / take-over mechanic and (b) supports the
"don't make the first move too strong" prescription:

> "The second player must select one of two options: Letting the move stand or Switching
> places."

> "The first player will choose a move neither too strong nor too weak, and the second
> player will have to decide whether switching places is worth the first-move advantage."

The second quote is a direct textual anchor for the head's prescription: the opener aims
for a balanced (neither too strong nor too weak) move precisely because a too-strong move
invites the swap. Current page revision oldid `1200819498` (last edited 2024-01-30
09:13 UTC). The idea doc should pin the source as
`https://en.wikipedia.org/wiki/Pie_rule@1200819498` (oldid pin) when it lands.

### 8. Real game phenomenon or textbook toy?

Real phenomenon. The pie / swap rule is a standard balancing mechanism in combinatorial
board games (Hex and others) used precisely to neutralize the first-move advantage: it
forces the opener to pick a near-balanced move because any strong opening is taken over by
the responder. The verifier's `min(f, 1 − f)` payoff and the G2 inversion quantify exactly
that documented incentive.

## Ruling

APPROVE. The digest reproduces EXACTLY
(`72950442cc7509423256f28470c2281c9f79de3b601611b9feb931d083e8cb08` MATCH), the copy is
byte-identical (diff exit 0, file sha256 `7e89f690…f12f4e39`, git blob `ace21553…5cd15daf`,
both equal to source), the run is deterministic (cross-invocation diff exit 0 plus the
in-process double-run assert passing), and all three gates PASS in order on the proposal's
own pre-registered thresholds (G1 z=598.38, G2 z=−591.72, G3 z_gap=370.91; `all_pass=true`,
`first_failing_gate=null`), with grounding live (Wikipedia "Pie rule" oldid 1200819498, swap
mechanic and balanced-opening prescription both quoted). On this clean reproduction the
verdict high-water advances V187 → V188 (union-max, no regress).

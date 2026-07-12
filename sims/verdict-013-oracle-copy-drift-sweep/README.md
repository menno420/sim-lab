# verdict-013 · oracle-copy-drift-sweep

Spec sweep for a candidate `tools/check_copy_drift.py` (superbot-next). Answers
idea-engine PROPOSAL 011 (control/outbox.md @ `6d9e80ec`, idea
`ideas/superbot-next/oracle-copy-punctuation-drift-sweep-2026-07-12.md`): which
(user-copy enumeration grammar × match-normalization tier) cell maximizes true
drift catches at near-zero false positives on the real corpora
(superbot-next@`af985c17` `sb/` literals vs superbot@`1ecc2113` `disbot/` copy),
and does the winning cell's true-catch count justify a red-gating checker over
a one-line fix?

## Run (one command)

```
python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py
```

Exit 0 iff all 1490 self-checks pass. Deterministic — the ONLY RNG is the
planted-drift injector, seeded `20260712` (committed constant); audit samples
are fixed strides over sorted pair lists; stdout and `results.json` are
byte-identical across re-runs (verified warm AND from a cold fetch). First run
fetches the two pinned corpora into `./corpora/` (gitignored) via shallow
`git fetch origin <sha>`; SHA-pinning makes the cache a transport detail, not
an input degree of freedom. Runtime ~20 s warm, ~25 s cold (plus network for
the two shallow fetches).

## Files

- `copy_drift_sweep.py` — checker prototype (AST extraction → normalization →
  pairing) + the full 60-cell sweep (6 enumeration grammars × 5 normalization
  tiers × 2 gating/pairing rules) + seeded planted-drift layer (punct / case /
  whitespace / wording mutations with hand-derived per-tier expectations) +
  1490 self-checks (pins, tier/grammar/gating monotonicity invariants, label
  coverage, the tournament.py:153 catch-and-miss matrix, frontier claims,
  in-process determinism).
- `labels.json` — the hand audit: every judgment-call pair the union of cells
  surfaces (89 pairs), classified true-drift / intentional-change / false-pair
  with per-pair reasons; 217 further pairs auto-classified by the one
  mechanically-derivable rule (rebuild literal byte-verbatim elsewhere in the
  oracle pool).
- `results.json` — committed run output: full 60-cell table with audited TC/FP,
  per-pair detail with sites on both sides, planted recall per cell, the
  tournament-instance evidence block, the winning cell.
- `REPORT.md` — the finalizable verdict report (validity gate + machine-readable
  winning spec + paste-ready VERDICT 013 outbox entry).

## Verdict (summary — full report in REPORT.md)

**reject — one-line fix wins.** The FP-free frontier (g5-msg | t3-case |
r-noexact, and equally g3-refusal) catches exactly **1 true drift** on the real
tree: the motivating `sb/domain/rps/tournament.py:153` "You're already
registered." vs oracle "You're already registered!". Whole-tree true drift is 3
pairs total (the tournament pair + two double-space setting hints reachable
only through the all-literals grammar at 38+ audited FPs). One catch at zero FP
does not justify a red-gating checker — the probe's own §4(e) decision rule.
The winning spec is recorded machine-readably in REPORT.md should the class
recur.

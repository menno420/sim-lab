# verdict-015 · heartbeat-contradiction-linter

Detector-cell sweep for the heartbeat intra-file contradiction question.
Answers idea-engine PROPOSAL 013 (control/outbox.md 2026-07-12T22:04:42Z,
idea `ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md` @ `0a9bfc8d`,
landed via idea-engine PR #275): over the committed revisions of idea-engine
`control/status.md` (`fc0bab6` → `0cfe15e`), which (fact-key extraction
grammar × disposition-vocabulary normalization × comparison scope) cell
catches the known live intra-file contradiction at `c77563c` (line 3 "STILL
ENABLED and LEFT ARMED deliberately" vs line 9 "being DISMANTLED with the
chat archive", same failsafe trigger) plus planted disposition-flip
contradictions, at near-zero false positives (the `e66c78a`
quotation-negation carry must NOT flag) — and does the winning cell's TC/FP
profile justify a kit advisory contradiction linter alongside the
single-home grammar rule, or the rule alone?

## Run (one command)

```
python3 sims/verdict-015-heartbeat-contradiction-linter/heartbeat_contradiction_sweep.py
```

Exit 0 iff all 229 self-checks pass. Deterministic — no RNG anywhere (plants
are ENUMERATED: first eligible statement, fixed templates), no network, no
wall clock; the corpus is 23 sha256-pinned fixture files. stdout and
`results.json` are byte-identical across process runs (verified by external
`diff` of two full runs). Runtime <1 s.

## Files

- `heartbeat_contradiction_sweep.py` — stdlib-only sweep: 27 cells
  (3 grammars × 3 normalizations × 3 scopes) over the real corpus + 44
  enumerated planted disposition flips (22 explicit-id P1 + 22 alias-only P2,
  the real specimen's shape), label-based scoring against the committed
  archetype table, 229 self-checks.
- `corpus/` — the 23 committed revisions of idea-engine `control/status.md`,
  `fc0bab6` → `0cfe15e` endpoints inclusive, extracted from a FULL-history
  clone (a shallow clone mis-follows this file — see labels.json) and
  sha256-pinned.
- `labels.json` — the audit ledger: corpus manifest with commit SHAs and
  fixture hashes, the specimen and hard-FP pins, the hand-audited
  ground-truth table (30 real revision×entity contradictions with verbatim
  up-evidence), the pair-label archetype patterns with reasons, vocabulary
  and grid justifications, count reconciliation, and gaps G1–G5.
- `results.json` — committed run output: full 27-cell table with per-cell
  flagged lines, winner, misses, self-check tally.
- `REPORT.md` — the finalizable verdict report (validity gate + paste-ready
  VERDICT 015 outbox entry).

## Verdict (summary — full report in REPORT.md)

**approve — ship BOTH halves: the single-home grammar rule AND the kit
advisory contradiction linter, spec'd as the winning cell.** Headline
corpus finding first: the proposal's premise ("one known live contradiction,
21 clean revisions") is UNDERCOUNTED ×30 — the carried ⚑ paragraph "being
DISMANTLED with the chat archive" contradicts the phase line's
live/armed/standing declaration about the SAME failsafe trigger in ALL 21
session-1-era revisions (plus the pacemaker chain in 9 of them): 30 real
intra-file contradictions from ONE carry+update seam, standing unnoticed for
~19.7 hours until the close-out probe pinned the `c77563c` instance. Winner:
**g3-id+alias × n3-attrib+quote-excl × s3-cross-block** — catches the pinned
specimen AND all 30/30 ground-truth instances at ZERO false-positive flags
across all 23 revisions (`e66c78a`'s quotation-negation carry correctly
un-flagged; so is its NEW-enabled/OLD-deleted distinct-id pair), planted
recall 44/44 (P1 1.00, P2 1.00). The grammar axis is load-bearing exactly as
the probe suspected: id-only and id+PR grammars catch NOTHING real (0/30 —
the carry side of every real contradiction names the routine by noun phrase,
never by id), and the naive co-occurrence baseline flags the `e66c78a` fix
itself. Honest cost: pair-level precision at the flag site is 0.52 (37
artifact pairs ride along on keys that are genuinely contradicted) — fine
for an always-exit-0 ADVISORY, disqualifying for a red gate.

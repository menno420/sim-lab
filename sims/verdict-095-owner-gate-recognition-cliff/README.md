# verdict-095 · owner-gate-recognition-cliff

The exact recognition census of the venture-lab owner-gate parser pair.
Answers idea-engine PROPOSAL 082
(`## PROPOSAL 082 · 2026-07-16T08:44:56Z · status: sim-ready`, idea
`ideas/venture-lab/owner-gate-recognition-cliff-2026-07-16.md` — the
round-17 VENTURE rotation slot, products half): the kit's own sold
fail-safe sentence (GOTCHAS.md #4 verbatim: "a stray checkbox edit (agents
reflow markdown all the time) can only ever RE-QUEUE an owner action,
never silently drop one") is priced on the claim's own shipped parser
(both copies, verbatim-identical recognition predicate at the grounding
HEAD). The sentence is TRUE on its own disposition 2×2 (registered as R1 —
zero silent cells) and INVERTED everywhere else: recognition is an
unguarded four-way conjunction (⚑-first-after-lstrip ∧ literal
`**Owner:**` ∧ `^- \[[ xX]\]\s+` shape ∧ flush-left position), and on the
registered 26-cell single-edit mutation grid over the pinned canonical
gate file, EXACTLY 18 cells land SILENT-LOSSY — every one with lint 0 AND
manual 0, because every lint error class fires only AFTER recognition (the
lint-downstream law). The cascade cells are the sharpest: the three silent
edits that hit the DONE row each land done 0 · armed 0 · lint 0 — one
character disarms both kill-clock checkpoints of a live launch (once-live
arming, registered directly on the no-DONE control corpus as parsed 2 /
armed 0). Granularity inversion: breaking the FILE (heading demote) is
guarded; breaking a ROW is silent. The repair fork is priced in-model: a
conservation lint counting a LOOSER net the deriver does not use catches
18/18 silent cells + 2 of the 3 alarmed-lossy with 0 false positives on
all three corpora, missing only the one semantic-regrade cell (disclosed
open).

## Run (one command)

```
python3 sims/verdict-095-owner-gate-recognition-cliff/owner_gate_recognition_cliff_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: stdout and `results.json`
are byte-identical across process runs (no wall clock, no paths, no
network, no git at run time). Stdlib only — this is a shipped-parser
deterministic-replay head (nearest method kin: P081/V094's replay of a
shipped mechanism against its own comfort comment, with the
true-sentence-survives move); the model replays FIVE pinned source
behaviors (recognition predicate, row shape, fold rule, checked-only
case-sensitive DONE disposition, gate-section + once-live arming) read
from ~340 lines of parser source across two copies at the grounding HEAD —
the source-semantics NULL axis prices exactly that. CPython 3.11 pinned
and asserted (Arms A/B are seedless exact parsing and integer counting;
only reporting-only Arm R and the presentation shuffle touch the pinned
minor's `random` module).

## Layout

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  082 block / idea file, committed BEFORE the runner: the five pinned
  behaviors, corpus C0 + the C1/C2 variant rules, the 14 operators × named
  targets = 26 cells, the F3 census anchors (baseline tuples, class totals
  {18, 3, 4, 1}, the SILENT-LOSSY list with cell coordinates, the key-cell
  tuples, the 2×2 row, the cascade triple, the once-live pair, the repair
  census), the typed contacts C1–C4, the Arm-R draw-order grammar with
  seeds 20261722–725 and both registered preview censuses + class-stream
  digests, and the pre-registered decision rule. Sim-chosen realizations
  (the corpus WHAT wording, target-line resolution, the 2×2 realization on
  r1, the digest procedure, salt logging, the presentation target) are
  disclosed as vacancy-derived fixtures, never match claims.
- `owner_gate_recognition_cliff_sim.py` — the single three-arm runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

## Arms

- **Arm A** — regex-faithful replay of the five pinned behaviors plus the
  strict lint (every error class conditioned on recognition) and the
  conservation-lint repair arm. Seedless, DECISION-bearing: every decision
  number is an exact parse census over the registered finite grid.
- **Arm B** — INDEPENDENTLY-WRITTEN character-level twin: no row regexes —
  per-character line classification plus an explicit index fold walk over
  parallel state/text lists. Tied to Arm A through the typed must-equal
  contacts: **C1** the three baseline tuples, **C2** all 26 grid cells +
  all four 2×2 cells (full observable tuple, merged/vanished accounting
  included), **C3** the twin decision evaluators agree on the ruling token
  over an ENUMERATED 64-row boolean input set, **C4** Arm R per-trace
  A == B with draw counters exactly 3N and the registered class-stream
  digests reproduced.
- **Arm R** — seeded random cells, REPORTING-ONLY (no statistical gate):
  per trace EXACTLY 3 `rng.randint` draws in registered order (corpus ∈
  [0,2], grid cell ∈ [1,26], salt ∈ [1,1000] drawn-and-logged), one
  `random.Random` per seed; INAPPLICABLE and NO-EDIT counted honestly as
  their own classes. Seeds 20261722 (N = 20,000, digest `e8d8812b3f9c`)
  and 20261723 (N = 8,000, digest `fc2709073718`); presentation shuffle
  20261724 (presentation leg only); aux 20261725 reserved and never read.

Decision rule (registered order, evaluated by two independently-written
evaluators over an ENUMERATED boolean input set): REJECT → INVALID →
APPROVE → NULL, REJECT evaluated FIRST. Full grammar in `fixtures.json`.

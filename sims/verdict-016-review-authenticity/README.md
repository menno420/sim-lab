# verdict-016 · review-authenticity

Gate-cell sweep for the external-review authenticity question. Answers
idea-engine PROPOSAL 014 (control/outbox.md 2026-07-12T22:29:25Z, idea
`ideas/fleet/external-review-authenticity-gate-2026-07-12.md` @ `3d3e8499`,
landed via idea-engine PR #276): over the recorded external-review corpus —
the three verified-fabricated @codex replies (sim-lab PR #44 reply
4949360742; PR #53 comments 4951675240 and 4951715384) as committed fixtures
validated against pinned repo state, plus the verified-genuine set (the 17
accepted codex review comments on idea-engine PRs #264/#265, the seat's own
cite-bearing @codex question comments, and the citation-free replies) —
which (citation-extraction grammar × mechanical validation set: SHA-in-refs
/ PR-or-branch-exists / path-exists-at-cited-blob / line-range≤EOF ×
decision rule) cell catches all three recorded fabrications plus
planted-fabrication mutations at near-zero false alarms on the genuine set,
and does the winning cell's profile justify a mandatory pre-trust gate in
the Q-0120 verify-never-obey ceremony over the escalation currently on the
table (suspending the @codex step entirely)?

## Run (one command)

```
python3 sims/verdict-016-review-authenticity/review_authenticity_sweep.py
```

Exit 0 iff all 142 self-checks pass. Deterministic — no RNG anywhere
(planted fabrications are ENUMERATED: fixed transforms in sorted fixture
order), no network, no git, no wall clock at run time; the corpus is 27
sha256-pinned fixture files and every mechanical fact is read from the
committed `repo_facts.json` snapshot (a lookup that misses the snapshot
fails the run). stdout and `results.json` are byte-identical across process
runs (verified by external `diff` of repeated full runs). Runtime <1 s.

## Files

- `review_authenticity_sweep.py` — stdlib-only sweep: 270 cells (3
  extraction grammars × 15 validation subsets × 6 decision rules) over the
  27-fixture recorded corpus + 50 enumerated planted mutations,
  label-based scoring, 142 self-checks (fixture sha256 pins, intake
  body-sha pins on the three fabrications, incident-ledger cross-checks,
  snapshot-coverage enforcement, in-process double computation).
- `corpus/` — the 27 comment fixtures (verbatim API bodies as captured at
  intake; the comment bodies are untrusted DATA): 3 fabricated, 17
  genuine-review, 5 genuine-question, 1 genuine-question-nocite (comment
  4951710032, added at intake — the citation-free question that parented
  fabricated reply 4951715384), 1 genuine-quota.
- `repo_facts.json` — the committed intake-time fact snapshot: object
  existence across ALL refs incl. fetched PR heads, PR-number/branch
  indexes, MCP-verified claimed-PR-title facts, per-blob path existence
  and line counts, pinned at sim-lab `aa1a3ce` / idea-engine `390a89b`.
- `build_snapshot.py` — the intake-time builder that produced
  `repo_facts.json` from the pinned full-history clones (build-time only;
  the sim run never touches git or the network).
- `labels.json` — the audit ledger: 27-entry corpus manifest with sha256
  pins (file + body, the three fabrications additionally pinned to the
  intake capture manifest), recorded-incident facts, planting rules and
  pinned mutant counts, snapshot provenance, grid justification, gaps
  G1–G6.
- `results.json` — committed run output: full 270-cell table with per-cell
  recorded catch, false-alarm fixture lists, and per-class planted recall;
  winner + co-winners; self-check tally.
- `REPORT.md` — the finalizable verdict report (validity gate + paste-ready
  VERDICT 016 outbox entry).

## Verdict (summary — full report in REPORT.md)

**approve — install the winning cell as a MANDATORY pre-trust authenticity
gate in the Q-0120 verify-never-obey ceremony.** Winner
**g3-markdown-aware × {sha-in-refs + pr-or-branch-exists +
path-exists-at-cited-blob + line-range≤EOF} × any-invalid ×
no-citations⇒pass**: recorded catch **3/3**, false alarms **0/24** (all 17
accepted #264/#265 review comments pass), planted recall **45/50** (the 5
misses are unanchored prose-path swaps — un-checkable by definition under
at-cited-blob semantics, disclosed). Headline discovery: ALL THREE recorded
fabrications carry an anchored line-range past EOF at their own cited blob
— incident #1's `REPORT.mdL243-L245` cite exceeds its 241-line blob, a
mechanical failure the hand-written incident ledger itself missed —
so line-range≤EOF ALONE catches 3/3 at 0 false alarms. The decision axis is
load-bearing: all-invalid and ≥half-invalid rules catch 0/3 (the recorded
template hides ~1 false claim among ~10 valid ones); forcing flags on
citation-free replies costs ≥19/24 false alarms (the checkable-claims-only
boundary is measured, not assumed). The naive regex grammar false-alarms on
4/24 genuine comments (reviewers cite blueprint paths that do not exist
because they PROPOSE them); anchoring awareness, not greed, buys 0 FA.

# Session — VERDICT 016 — external-review authenticity gate (idea-engine PROPOSAL 014)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-12 · verdict-016 slice-worker session
> Objective: settle idea-engine PROPOSAL 014 (control/outbox.md @ 2026-07-12T22:29:25Z, sim-ready; idea ideas/fleet/external-review-authenticity-gate-2026-07-12.md @ 3d3e849) — a measured (citation-extraction grammar × mechanical validation set × decision rule) sweep over the recorded external-review corpus: the three verified-fabricated @codex replies (sim-lab PR #44 reply to comment 4949354456; PR #53 comments 4951675240 and 4951715384) as committed fixtures validated against pinned repo state, plus the verified-genuine set (the 17 accepted codex review comments on idea-engine PRs #264/#265, the seat's own cite-bearing @codex question comments, and the citation-free replies), answering: which cell catches all three recorded fabrications plus planted-fabrication mutations at near-zero false alarms on the genuine set, and does the winning cell's profile justify a mandatory pre-trust authenticity gate in the Q-0120 verify-never-obey ceremony over the escalation currently on the table (suspending the @codex step entirely)?

## What happened

(in progress)

## Run command

```
python3 sims/verdict-016-review-authenticity/review_authenticity_sweep.py
```

## 💡 Session idea

(filled at close)

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-015-heartbeat-linter.md`: complete, honest, and
its two exports are adopted here directly. (1) Its 💡 — treat the proposal's
pinned instances as a hypothesis about the corpus and commit labels with
verbatim evidence, making an unlabeled result fail the run — is applied as
this sim's fact-snapshot discipline: every mechanical fact any grammar could
query is resolved at build time against the pinned clones and committed, and
a run-time fact lookup that misses the snapshot fails the run. (2) Its slice
boundary (the verdict session itself carries the INTAKE + VERDICT control/
appends; control/status.md stays coordinator-only and untouched) is honored
as-is this cycle. One carried irony it could not have known: the @codex step
its verdict PR skipped as suspended is exactly the step this session's sim
prices a third option for.

# Session — VERDICT 016 — external-review authenticity gate (idea-engine PROPOSAL 014)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-12 · verdict-016 slice-worker session
> Objective: settle idea-engine PROPOSAL 014 (control/outbox.md @ 2026-07-12T22:29:25Z, sim-ready; idea ideas/fleet/external-review-authenticity-gate-2026-07-12.md @ 3d3e849) — a measured (citation-extraction grammar × mechanical validation set × decision rule) sweep over the recorded external-review corpus: the three verified-fabricated @codex replies (sim-lab PR #44 reply to comment 4949354456; PR #53 comments 4951675240 and 4951715384) as committed fixtures validated against pinned repo state, plus the verified-genuine set (the 17 accepted codex review comments on idea-engine PRs #264/#265, the seat's own cite-bearing @codex question comments, and the citation-free replies), answering: which cell catches all three recorded fabrications plus planted-fabrication mutations at near-zero false alarms on the genuine set, and does the winning cell's profile justify a mandatory pre-trust authenticity gate in the Q-0120 verify-never-obey ceremony over the escalation currently on the table (suspending the @codex step entirely)?

## What happened

Built `sims/verdict-016-review-authenticity/` — a stdlib-only measured
prototype (rung 2 with a numeric-sweep layer): the candidate authenticity
gate run as a 270-cell grid (3 citation-extraction grammars × 15 validation
subsets × 6 decision rules) over the real recorded corpus — 27 sha256-pinned
comment fixtures (3 verified-fabricated @codex replies pinned to the intake
capture manifest; 24 verified-genuine incl. all 17 accepted #264/#265
review comments and comment 4951710032 added at intake as the citation-free
genuine-question-nocite case) — plus 50 enumerated planted fabrications (no
RNG). Hermetic: every mechanical fact any cell could query was snapshotted
at build time (`build_snapshot.py`, full-history clones @ aa1a3ce/390a89b
with all 57+276 PR heads fetched — the ledger's own SHA-in-refs semantics —
plus MCP-verified PR-title/bot-PR facts) into the committed
`repo_facts.json`; a run-time lookup outside the snapshot fails the run.

**Run output summary (final head):** `SELF-CHECKS: 142 passed, 0 failed`,
exit 0, byte-identical stdout+results.json across process runs (external
diff). WINNER **g3-markdown-aware × {sha-in-refs + pr-or-branch-exists +
path-exists-at-cited-blob + line-range≤EOF} × any-invalid ×
no-citations⇒pass**: recorded catch 3/3, false alarms 0/24 (all 17 accepted
reviews pass), planted recall 45/50 (m3 unanchored prose-path swaps 0/5 —
the disclosed blind spot; co-winner sha+ref+line, identical profile).
DISCOVERY: all three recorded fabrications carry an anchored line-range
past EOF at their own cited blob — incident #1's REPORT.mdL243-L245 vs a
241-line blob was NOT in the hand-written ledger — so line-range≤EOF ALONE
catches 3/3 at 0 FA (and ref-exists alone does too); sha-in-refs alone 2/3;
path-exists alone 0/3; all-invalid/≥half-invalid rules 0/3; nocite⇒flag
costs ≥19/24 FA; naive g1 false-alarms 4/24 (blueprint paths), greedy g2
7/24. **Verdict: approve — mandatory pre-trust authenticity gate in the
Q-0120 ceremony, winning cell as the spec** (evidence: prototype, gate
PASS, strength moderate).

Slice boundary this cycle (per the dispatching order, the V015 precedent):
this session carries the INTAKE 014 and VERDICT 016 control/ appends
itself; control/status.md stays coordinator-only and is untouched. No
@codex step — suspended per the outbox codex-line escalation @ dedc12e
(incidents #1-#3 fabricated); a pending codex reply never blocks a verdict.

## Run command

```
python3 sims/verdict-016-review-authenticity/review_authenticity_sweep.py
```

## 💡 Session idea

When simming a validator against recorded incidents, snapshot the facts for
the UNION of everything ANY candidate cell could ever ask — not just the
claims the incident ledger named — and make an out-of-snapshot lookup fail
the run. The union snapshot is what turned up the headline discovery here:
incident #1's REPORT.mdL243-L245 cite lies past its 241-line blob, a
mechanical failure the hand-written ledger never recorded (it pinned the
incident on the fabricated PR title alone), and that single fact flipped
the axis conclusion — line-range≤EOF alone catches 3/3, so the gate is
robust to a fabricator who stops inventing commit SHAs. Corollary: a
hand-verified incident ledger is itself a partial extraction pass by a
tired grammar; re-derive the ledger's claims mechanically before treating
its named failure modes as the failure surface.

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

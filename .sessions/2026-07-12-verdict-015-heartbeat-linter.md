# Session — VERDICT 015 — heartbeat contradiction linter (idea-engine PROPOSAL 013)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-12 · verdict-015 slice-worker session
> Objective: settle idea-engine PROPOSAL 013 (control/outbox.md @ 2026-07-12T22:04:42Z, sim-ready; idea ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md @ 0a9bfc8) — a measured detector-cell sweep over the real committed revisions of idea-engine control/status.md (fc0bab6 → 0cfe15e), answering: which (fact-key extraction grammar × disposition-vocabulary normalization × comparison scope) cell catches the known live intra-file contradiction at c77563c plus planted disposition-flip contradictions at near-zero false positives on the other clean revisions (the e66c78a quotation-negation carry must NOT flag) — and does the winning cell's TC/FP profile justify a kit advisory contradiction linter alongside the single-home grammar rule, or the single-home rule alone?

## What happened

Built `sims/verdict-015-heartbeat-contradiction-linter/` — a stdlib-only
measured prototype (rung 2 with a numeric-sweep layer): the candidate
detector engine run as a 27-cell grid (3 fact-key grammars × 3
disposition normalizations × 3 comparison scopes) over the real committed
corpus (all 23 revisions of idea-engine control/status.md, fc0bab6 →
0cfe15e inclusive, sha256-pinned fixtures from a FULL-history clone — a
shallow clone mis-follows this file, recorded in labels.json along with the
proposal's 22-vs-23 count reconciliation: git-exclusive vs
endpoint-inclusive range) plus 44 enumerated planted disposition flips
(22 explicit-id + 22 alias-only, the real specimen's shape; no RNG).

**Run output summary (final head):** `SELF-CHECKS: 229 passed, 0 failed`,
exit 0, byte-identical stdout+results.json across two process runs
(external diff). HEADLINE: the proposal's "one known live contradiction"
premise is UNDERCOUNTED x30 — the carried ⚑ "being DISMANTLED with the
chat archive" paragraph contradicts the phase line's live/armed/standing
declaration about the SAME trig_01T83 failsafe in ALL 21 session-1-era
revisions (+ the pacemaker chain in 9 of them): 30 hand-audited real
intra-file contradictions from ONE carry+update seam, unnoticed ~19.7h,
ended exactly by e66c78a's ad-hoc single-home fix. Winner cell
**g3-id+alias × n3-attrib+quote-excl × s3-cross-block**: pinned specimen
caught + 30/30 instances at 0 FP flags on all 23 revisions, e66c78a's
quotation-negation carry correctly un-flagged, planted recall 44/44.
Id-only grammars catch 0/30 (the carry names routines by noun phrase,
never id — the grammar axis is load-bearing); the naive co-occurrence
baseline flags the fix itself; pair-level precision at the flag site is
0.52 (advisory-grade, not red-gate-grade). **Verdict: approve — ship BOTH
halves (single-home rule + kit advisory linter, spec in REPORT.md)**
(evidence: prototype, gate PASS, strength moderate).

Slice boundary this cycle (per the dispatching order, changed from the
V014 division of labor): this session carries the INTAKE 013 and VERDICT
015 control/ appends itself; control/status.md stays coordinator-only and
is untouched. No @codex step — suspended per the outbox codex-line
escalation @ dedc12e (incidents #1-#3 fabricated).

## Run command

```
python3 sims/verdict-015-heartbeat-contradiction-linter/heartbeat_contradiction_sweep.py
```

## 💡 Session idea

When a sim's question pins "the one known instance" of a failure class,
treat that pin as a HYPOTHESIS about the corpus, not a fact: run the
candidate detector's most sensitive cell FIRST as a census, hand-label
everything it raises, and only then score the grid against the labeled
ground truth. This session's census overturned the premise (1 known
contradiction turned out to be 30 instances of one carried paragraph) and
the discovery flipped the evidence weight of the whole verdict — the
strongest argument for the linter was found BY the linter, and a sweep
that had trusted the proposal's clean/dirty split would have scored 29
true catches as false positives and wrongly ruled "FP floor too high,
rule only". Corollary worth keeping: an "FP" tally on real prose is only
as honest as its label provenance — commit the labels with verbatim
quoted evidence and make an unlabeled flag fail the run.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-014-routine-cadence.md`: complete and honest —
its slice boundary note ("control/ appends are deliberately LEFT TO THE
COORDINATOR") documented a division of labor that this cycle's dispatch order
has explicitly changed (this session carries the INTAKE and outbox appends
itself, status.md heartbeat still coordinator-only), which is exactly why
cards should state the boundary they honored rather than assume it is
standing law. Its 💡 (debug the hand-derivation first; commit the corrected
arithmetic as a comment next to the check) is adopted verbatim in this sim's
self-check style.

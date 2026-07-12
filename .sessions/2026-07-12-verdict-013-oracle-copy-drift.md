# Session — VERDICT 013 — oracle-copy drift sweep (idea-engine PROPOSAL 011)

> **Status:** `complete`
> 📊 Model: fable-5 · 2026-07-12 · verdict-013 slice-worker session
> Objective: settle idea-engine PROPOSAL 011 (control/outbox.md @ 6d9e80ec7fbb4f64541b929a6a10f85207400252) — sweep (user-copy enumeration grammar × match-normalization tier × gating rule) over the two pinned real corpora (superbot-next@af985c17 `sb/` literals vs superbot@1ecc2113 `disbot/` copy), measure per-cell true catches vs false positives + planted-drift recall, verify the motivating `sb/domain/rps/tournament.py:153` drift is caught by the winning cell, and rule whether the winning cell's true-catch count justifies a red-gating `tools/check_copy_drift.py` over a one-line fix.

## What happened

Built `sims/verdict-013-oracle-copy-drift-sweep/` — a working checker prototype
(AST extraction → normalization → oracle-pool pairing) swept over 60 cells
(6 enumeration grammars × 5 normalization tiers × 2 gating/pairing rules) on
both pinned real corpora, plus a seeded planted-drift layer (punct / case /
whitespace / wording mutations with hand-derived per-tier expectations, sole
RNG seed `20260712`, committed constant). Corpora fetch-on-run at pinned SHAs
into a gitignored cache (verdict-012's exact mechanism). Every judgment-call
pair the union of cells surfaces was hand-audited by reading both-side
contexts (89 pairs, committed as `labels.json` with per-pair reasons); 217
further pairs auto-classified by the one mechanically-derivable rule (rebuild
literal byte-verbatim elsewhere in the oracle pool).

**Run output summary (final head):** `SELF-CHECKS: 1490 passed, 0 failed`,
exit 0; stdout AND results.json byte-identical across re-runs, verified warm
AND from a cold cache (corpora deleted, runner refetched both pins).
Headline: the FP-free frontier (g5-msg | t3-case | r-noexact — identical at
g3-refusal and t2-punct, 8 cells) catches exactly **1 true drift**, and it IS
the motivating `sb/domain/rps/tournament.py:153` "You're already registered."
vs oracle "You're already registered!" (sites self-checked:
`disbot/utils/tournaments.py:44` + `disbot/views/rps/registration.py:49`).
Whole-tree true drift is 3 pairs; the other 2 (double-space setting hints)
are reachable only via the all-literals grammar at 38–68 audited FPs. Probe
grammar (a) verbatim-comment-adjacency MISSES the motivating instance (marker
7 lines away); the fuzzy wording tier is FP-positive everywhere it adds
flags. **Verdict: reject — one-line fix wins** (probe §4(e)'s own decision
rule; evidence: prototype, gate PASS, strength moderate-strong) — full ruling,
machine-readable winning spec, and paste-ready VERDICT 013 outbox entry at the
end of the sim's REPORT.md.

Slice boundary honored: control/ appends (INTAKE 011, VERDICT 013 outbox
entry, status.md heartbeat) are deliberately LEFT TO THE COORDINATOR — this
session touched only `sims/verdict-013-oracle-copy-drift-sweep/` and this
card, and the PR is parked READY, never merged by this worker. Do not merge —
coordinator lands this PR.

## Run command

```
python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py
```

## 💡 Session idea

A reject needs its abstractions to bias TOWARD the thing being rejected: every
simplification in this harness (literal-level pairing, whole-pool fragment
matching, snapshot oracle) inflates catch counts, never deflates them — so
"even the most generous reading finds 1 fundable catch" is the strong form of
the reject. Pattern to reuse for verdict sims whose likely answer is "don't
build it": pick the modeling shortcuts that help the OTHER side.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-012-doc-cite-checker.md`: clean and complete —
its "💡 Session idea" (audit the loosest variant's flag superset once, prove
subset monotonicity, every stricter cell inherits classified counts for free;
auto-classify only the mechanically derivable) was adopted wholesale here and
carried the 60-cell audit at 89 hand labels. Its codex-disposition commit
(reply REJECTED after tree verification, Q-0120 verify-never-obey) is the
template this verdict's coordinator should apply to the pending @codex reply.
Nothing to fix; the OA-002 usage-cap wall it recorded still stands.

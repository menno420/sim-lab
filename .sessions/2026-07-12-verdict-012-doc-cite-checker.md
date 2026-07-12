# Session — VERDICT 012 — doc-cite-checker spec sweep (idea-engine PROPOSAL 010)

> **Status:** `complete`
> 📊 Model: fable-5 · 2026-07-12 · verdict-012 slice-worker session
> Objective: settle idea-engine PROPOSAL 010 (control/outbox.md @ a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5) — sweep the cite-rule ladder (a file-exists / b +line-range / c +identifier-near-lines) × cite-grammar variants × doc-tree-scope variants over the two pinned real corpora (superbot-next@2c62a099, superbot@b2b7fe0c), measure true catches vs false positives per variant, verify the known WorkflowResult/`disbot/core/contracts.py:48-52` fabrication is caught, and rule ONE spec (grammar regex + scope + gating) for the superbot-next `tools/check_doc_cites.py` build.

## What happened

Built `sims/verdict-012-doc-cite-checker-spec/` — a working checker prototype
(extract → resolve → judge) swept over 36 variants per corpus (3 grammars ×
fence-skip on/off × 2 scopes × 3 resolution policies × rule ladder a/b/c), plus a
10-cite planted synthetic corpus with hand-derived per-variant expectations.
Corpora fetch-on-run at pinned SHAs into a gitignored cache. Every rule-a and
rule-b flag pair of the audit variant on BOTH corpora was hand-audited by reading
its context against the tree (78 + 45 unique pairs, committed as `labels.json`
with per-pair reasons); rule-c was sampled at a stated fixed stride (15 of 543).

**Run output summary (final head):** `SELF-CHECKS: 453 passed, 0 failed`, exit 0;
two consecutive runs byte-identical (stdout AND results.json, diff-verified); no
RNG anywhere. Headline: superbot-next has 0 rule-a/0 rule-b flags (0 FP) at
g3-strict-guard + fence-skip + all-md + exact-or-unique-suffix + FOREIGN_ROOTS
skip — red-gate defensible on the target tree; superbot's best cell is 14 TC /
14 FP (no clean red there: 7 deliberate absent-path correction notes + 6
tests/-prefix cross-repo collisions + 1 foreign workflow file); rule-b is
warn-grade (16/29 audited FP = ≤2-line EOF boundary noise); rule-c dead (1/15
sampled precision). Fabrication class: `disbot/core/contracts.py` verified ABSENT
@ b2b7fe0 (real analogue `disbot/services/lifecycle/contracts.py` EXISTS); all 7
surviving cite instances flagged by all three grammars — all are correction
notes, hence the ruling's inline waiver token. **Verdict: approve** (evidence:
prototype, gate PASS, strength moderate-strong) — full ruling + paste-ready
VERDICT 012 outbox entry at the end of the sim's REPORT.md.

Slice boundary honored: control/ appends (INTAKE 012, VERDICT 012 outbox entry,
status.md heartbeat) are deliberately LEFT TO THE COORDINATOR — this session
touched only `sims/verdict-012-doc-cite-checker-spec/` and this card, and the PR
is parked open (never merged by this worker).

## Run command

```
python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py
```

## 💡 Session idea

Ground-truth labels are the sim: for checker-spec sweeps, the machine part
(flag counts per variant) is cheap — the EVIDENCE is the committed, per-pair
audited `labels.json` that turns counts into true-catch/false-positive columns.
Pattern to reuse: audit the loosest variant's flag superset once, prove every
stricter variant is a subset (monotonicity self-checks), and every cell of the
grid inherits classified counts for free. Also: auto-classify only what is
mechanically derivable (suffix-resolvable relative paths), never the judgment
calls.

## ⟲ Previous-session review

Prior card `2026-07-11-closeout.md`: the close-out that archived the lane — it
brought durable state current (current-state ledger, PLATFORM-LIMITS walls,
docs/retro archive-ready note), verified 0 open PRs/issues, and predicted exactly
this: anything new re-opens the lane through the intake queue. This session does
that re-open — PROPOSAL 010 arrived `sim-ready` on idea-engine's outbox after the
archive, so the lane wakes for VERDICT 012 intake as the close-out card's model
anticipated. Clean card, nothing to fix; the one carried-forward open item (PR #38
@codex reply, OA-002 usage cap) remains an owner-action, untouched here.

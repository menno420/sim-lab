# Session — VERDICT 012 — doc-cite-checker spec sweep (idea-engine PROPOSAL 010)

> **Status:** `in-progress`
> 📊 Model: fable-5 · 2026-07-12 · verdict-012 slice-worker session
> Objective: settle idea-engine PROPOSAL 010 (control/outbox.md @ a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5) — sweep the cite-rule ladder (a file-exists / b +line-range / c +identifier-near-lines) × cite-grammar variants × doc-tree-scope variants over the two pinned real corpora (superbot-next@2c62a099, superbot@b2b7fe0c), measure true catches vs false positives per variant, verify the known WorkflowResult/`disbot/core/contracts.py:48-52` fabrication is caught, and rule ONE spec (grammar regex + scope + gating) for the superbot-next `tools/check_doc_cites.py` build.

## What happened

(in progress)

Note on slice boundary: control/ appends (INTAKE 012, VERDICT 012 outbox entry,
status.md heartbeat) are deliberately LEFT TO THE COORDINATOR — this slice-worker
session touches only `sims/verdict-012-doc-cite-checker-spec/` and this card. The
paste-ready VERDICT 012 outbox entry is at the end of the sim's REPORT.md.

## Run command

```
python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py
```

## 💡 Session idea

(pending close-out)

## ⟲ Previous-session review

Prior card `2026-07-11-closeout.md`: the close-out that archived the lane — it
brought durable state current (current-state ledger, PLATFORM-LIMITS walls,
docs/retro archive-ready note), verified 0 open PRs/issues, and predicted exactly
this: anything new re-opens the lane through the intake queue. This session does
that re-open — PROPOSAL 010 arrived `sim-ready` on idea-engine's outbox after the
archive, so the lane wakes for VERDICT 012 intake as the close-out card's model
anticipated. Clean card, nothing to fix; the one carried-forward open item (PR #38
@codex reply, OA-002 usage cap) remains an owner-action, untouched here.

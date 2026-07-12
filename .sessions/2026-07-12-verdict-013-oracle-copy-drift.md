# Session — VERDICT 013 — oracle-copy drift sweep (idea-engine PROPOSAL 011)

> **Status:** `in-progress`
> 📊 Model: fable-5 · 2026-07-12 · verdict-013 slice-worker session
> Objective: settle idea-engine PROPOSAL 011 (control/outbox.md @ 6d9e80ec7fbb4f64541b929a6a10f85207400252) — sweep (user-copy enumeration grammar × match-normalization tier × gating rule) over the two pinned real corpora (superbot-next@af985c17 `sb/` literals vs superbot@1ecc2113 `disbot/` copy), measure per-cell true catches vs false positives + planted-drift recall, verify the motivating `sb/domain/rps/tournament.py:153` drift is caught by the winning cell, and rule whether the winning cell's true-catch count justifies a red-gating `tools/check_copy_drift.py` over a one-line fix.

## What happened

(born-red heartbeat — sim commit, run evidence, and close-out follow in this PR)

Slice boundary: this session touches ONLY `sims/verdict-013-oracle-copy-drift-sweep/`
and this card. control/ appends (INTAKE 011, VERDICT 013 outbox entry, status.md
heartbeat) are deliberately left to the coordinator. Do not merge — coordinator
lands this PR.

## Run command

```
python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py
```

## 💡 Session idea

(pending close-out)

## ⟲ Previous-session review

(pending close-out)

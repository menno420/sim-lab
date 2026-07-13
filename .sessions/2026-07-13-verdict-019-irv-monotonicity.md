# Session — VERDICT 019 — IRV monotonicity in close races (idea-engine PROPOSAL 017)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-019 slice-worker session
> Objective: settle idea-engine PROPOSAL 017 (control/outbox.md @ 2026-07-13T00:59:58Z, sim-ready; idea ideas/fleet/irv-monotonicity-close-races-2026-07-13.md @ efc78ae, landed via idea-engine PR #281, main `80baad5`) — the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain rotation slot's first head (domain: social choice theory, 3-candidate instant-runoff voting). Build the fully hermetic pre-registered sim: under the pinned IRV rule (plurality-loser elimination, pairwise final, exact ties excluded and counted), measure the upward monotonicity violation fraction — V_all (all non-tied elections) and V_close (round-1 elimination margin ≤ 5% of n) — in BOTH Arm E (exhaustive IAC: all compositions at n=25, anchor n=13 — exact fractions, seedless) and Arm S (seeded IC: n=99, M=200,000, seed 20260713 primary; n=1,001, M=20,000, seed 20260714 size leg), then issue exactly ONE of APPROVE (V_close ≥ 0.10 AND V_all ≥ 0.01 in both arms) / REJECT (V_close < 0.05 in both) / NULL (anything else — model-dependence is the citable finding) per the decision rule registered BEFORE any code existed, with the lower-bound caveat (single-type uplift) and the CPython minor version pinned.

## What happened

(in progress — close-out written at session end)

## Run command

```
python3 sims/verdict-019-irv-monotonicity/irv_monotonicity_sim.py
```

## 💡 Session idea

(in progress)

## ⟲ Previous-session review

(in progress)

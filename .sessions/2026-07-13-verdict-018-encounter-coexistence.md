# Session — VERDICT 018 — encounter coexistence: cooldown-namespace contract sweep (idea-engine PROPOSAL 016)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-018 slice-worker session
> Objective: settle idea-engine PROPOSAL 016 (control/outbox.md @ 2026-07-13T00:37:54Z, sim-ready; idea ideas/superbot/encounter-coexistence-cooldown-contract-2026-07-13.md @ 3ddaea8, landed via idea-engine PR #279) — compose the two verdicted player models (VERDICT 001 channel-activity tiers + paced-spam farmer; VERDICT 008 grid playstyles) into single-player joint profiles (chat-only and grid-only regression legs FIRST, each reproducing its verdict's solo headline rates, then mixed-casual, mixed-deep, and a cross-surface arbitrage farmer) and sweep the cooldown-namespace contract — (a) per-source clocks at the pinned defaults (CHAT_ACTIVITY 900 s / GRID_ROAM 600 s), (b) one shared per-player clock c ∈ {600, 900} s, (c) per-source clocks plus a combined per-player hourly cap K ∈ {4, 6, 8} — scoring every cell against BOTH verdicts' pinned shapes simultaneously, bounding the combined per-player interruption rate at the stricter solo ceiling (Q-0087), and measuring whether cross-surface cooldown arbitrage buys the farmer a combined encounter-rate yield materially above the honest mixed profiles' — ending in ONE recommended contract row (cooldown namespace + combined-rate guardrail + which pinned defaults survive vs re-pin) for the shared engine before the first consumer build fixes it by accident.

## What happened

(in progress — build subtree `sims/verdict-018-encounter-coexistence/`)

## Run command

```
python3 sims/verdict-018-encounter-coexistence/encounter_coexistence_sim.py
```

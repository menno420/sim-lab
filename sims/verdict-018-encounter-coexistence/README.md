# verdict-018 · encounter-coexistence

Cooldown-namespace contract sweep for the shared encounter engine. Answers
idea-engine PROPOSAL 016 (control/outbox.md 2026-07-13T00:37:54Z, idea
`ideas/superbot/encounter-coexistence-cooldown-contract-2026-07-13.md` @
`3ddaea8`, landed via idea-engine PR #279): composing the two verdicted
player models — VERDICT 001's channel-activity tiers + paced-spam farmer and
VERDICT 008's grid playstyles — into single-player joint profiles, which
cooldown-namespace contract — (a) per-source clocks at the pinned defaults
(CHAT_ACTIVITY 900 s / GRID_ROAM 600 s), (b) one shared per-player clock
c ∈ {600, 900} s, (c) per-source clocks plus a combined per-player hourly cap
K ∈ {4, 6, 8} — keeps BOTH verdicts' pinned shapes simultaneously true while
bounding the combined per-player interruption rate at the stricter solo
ceiling (4/hr, the Q-0087 bound), and does cross-surface cooldown arbitrage
buy the farmer a combined yield materially above the honest mixed profiles'?

## Run (one command)

```
python3 sims/verdict-018-encounter-coexistence/encounter_coexistence_sim.py
```

Exit 0 iff all 1500 self-checks pass. Deterministic — fixed seeds only (the
parents' own SEEDS; the seeded streams ARE the two committed trace models),
no unseeded RNG, no network, no git, no wall clock, no `hash()`. stdout and
`results.json` are byte-identical across process runs (verified by external
`diff` of three complete runs). Runtime < 1 s.

## Files

- `encounter_coexistence_sim.py` — stdlib-only driver: vendored V001 channel
  machine + vendored V008 roll gate (semantics proven equal by regression +
  composition self-checks, never imported — the layout contract), the
  contract state machine (per-source / shared / capped), the merged
  two-surface event stream, 6 contract cells × 3 joint profiles × 5 seeds at
  8 h, the committed scoring P1–P6 and winner rule, 1500 self-checks.
- `grid.json` — the committed inputs: contract cells, joint profiles, solo
  anchors, the P1–P6 decision rule, ARB_RATIO_MAX = 2.0 (V008's 1.86
  farmer-vs-honest precedent rounded up), the winner rule — committed BEFORE
  results existed.
- `fixtures/games_shared_encounter_interface.py` — byte-copy of the shared
  seam, superbot-games `games/shared/encounter/interface.py` @ `64b3371`
  (zero cooldown/rate surface — the premise).
- `fixtures/MANIFEST.json` — sha256 pins: the seam fixture AND both parent
  sim files (a silent parent edit fails this sim loudly); premise pins
  (superbot `cdb2680` live / `0f991a8` proposal — docs-only delta, window
  OPEN).
- `results.json` — committed run output: regression legs, solo anchors, all
  6 cells × 3 profiles, scores, passing cells, winner.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  018 recommendation).

## Verdict (summary — full report in REPORT.md)

**approve** — the contract row exists and is measured:

- **Pure per-source clocks (a) — the accident whichever build lands first
  would install — FAIL:** honest mixed players are fine (distortion 0.0000;
  mixed-deep combined 3.275/hr < 4), but the cross-surface arbitrage farmer
  reaches **8.875 combined encounters/hr** (chat pinned at 4.000 + grid
  4.875), **2.71×** the best honest mixed profile — the channel neither solo
  sim could see is real, not negligible.
- **Shared clock cells:** c=600 FAILS (arb 5.15/hr > 4); c=900 PASSES the
  bound but re-pins V008's GRID_ROAM 600 s default to 900 s and costs the
  honest mixed-deep player 0.975/hr (grid 2.95 → 2.20) — dominated.
- **WINNER (committed rule): C-cap-4** — per-source clocks at BOTH verdicts'
  pinned defaults + a combined per-player cap of 4 encounters per sliding
  3600 s. Both parents' default sets survive unchanged; the arbitrage farmer
  pins to exactly 4.000/hr (ratio 1.391, below both parents' own solo farmer
  ratios); measured honest cost: the mixed-deep player loses 0.400/hr
  (combined 3.275 → 2.875, a 12.2% clip) — the disclosed price of the
  Q-0087 stricter-ceiling bound. K is the owner's judgment knob: K=6 zeroes
  the honest cost but concedes the farmer 6/hr (above the stricter ceiling)
  and so FAILS the committed bound.

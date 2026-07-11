# VERDICT 008 — mining-grid per-action encounter tuning sweep

Numeric simulation (method ladder rung 1) settling the depth-gating / anti-farm RATE
economics of the grid-mine per-action encounter mechanic for `menno420/superbot`.

- **Source idea:** idea-engine `control/outbox.md` **PROPOSAL 008** (2026-07-11T12:16:30Z),
  pinned `68f45743d4cab7eab5f863f2918e4fb7d9c1c196`; idea entry
  `ideas/superbot/mining-grid-encounters-2026-07-10.md` @ `977662f2d84d1b29d51fbc4121f2e467afcc6a94`;
  canonical superbot `docs/ideas/mining-grid-encounters-2026-06-22.md` @ `e1090dbcfdf63ffd955399dc2325b9ad1a2f8c8d`.
- **Sister precedent:** `sims/intake-003-wild-encounter-spawn-tuning` (VERDICT 001) — same
  shape, self-check density, and no-earn-rate caveat.
- **Run (one command, deterministic, stdlib-only, exit 0 iff self-checks pass):**
  ```
  python3 sims/verdict-008-mining-grid-encounters/mining_grid_encounter_sim.py
  ```
- **Wider-variation robustness pass** (post-verdict addendum — adversarially stress-tests the
  anti-farm cooldown cap against bot-speed / boundary-timing / AFK grinders + wider param edges;
  verdict unchanged; 811 self-checks, exit 0 iff clean):
  ```
  python3 sims/verdict-008-mining-grid-encounters/robustness_wide.py
  ```
- **What it models:** a single player's 1-hour grid-mine traversal. Each mine action, at a grid
  depth, may roll a LIVE per-action encounter — it fires iff `depth >= threshold` AND off the
  per-PLAYER cooldown AND `u < chance` (one live encounter per player; resolved instantly for
  rate-accounting). Three STYLIZED playstyles (modeled, not telemetry): casual roamer (shallow),
  deep-runner (honest deep player), `!fastmine` grinder (adversarial optimal farmer parked deep).
  CRN reuses each `(playstyle, seed)` action+roll schedule across every cell.
- **Sweep:** threshold ∈ {5,10,15,20} × chance ∈ {0.01,0.02,0.05,0.10} × cooldown ∈ {60,300,600,900}s
  = 64 cells × 3 playstyles × **seeds [11,23,42,101,2027]**, plus an 8h robustness pass.
  **7723 self-checks** (gating, cooldown cap, one-live, monotonic-in-chance, sanity, determinism,
  2 expect_reject negatives).
- **Files:** `mining_grid_encounter_sim.py` (model + sweep + 7723 self-checks) · `REPORT.md`
  (the validity-gate answers + the verdict) · this README.
- **Verdict:** `needs-more-evidence` · evidence `simulation` · **gate PASS**. SETTLED
  analytically (RATE terms): gating is structural (0 encounters above threshold); the per-PLAYER
  cooldown caps encounters at `3600/cooldown` enc/hr for EVERYONE incl. the `!fastmine` grinder
  (grinder-vs-honest ratio bounded and shrinking toward ~1.15 as chance rises; the grinder's
  rolls-per-encounter is 2–4× the honest player's, so reward-per-action collapses). UNSETTLED and
  COUPLED: the loot faucet's ABSOLUTE VALUE (no live fishing/mining earn-rate baseline exists →
  loot values provisional) and the owner-vague "rare-but-present" target — farm-unprofitability is
  settled in RATE terms, not VALUE terms.
- **Recommended launch defaults:** threshold=15 (or 20 for a provably-silent surface), chance=0.02,
  cooldown=600s; guardrails: per-PLAYER (not per-cell) cooldown, one live encounter per player,
  audited-seam resolution (`economy_service`/`update_mining_item`/`game_xp` via `mining_workflow`
  RS02). Ship with the telemetry list in REPORT.md so the loot-value + shape gaps close on live data.

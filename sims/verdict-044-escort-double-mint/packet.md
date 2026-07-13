# SIM-REQUEST packet — dnd-escort-double-mint (verbatim copy)

PACKET PIN: menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94 (main HEAD of blobless clone, 2026-07-13T10:55Z; matches the sibling pin used by VERDICT 042).
Source: `control/outbox.md` @ 57f69be, lines 186–221.

Verbatim:

```
## SIM-REQUEST · dnd-escort-double-mint · 2026-07-13

**Requested by:** games seat (D&D finalization — audited `choose` seam + CLI)
**For:** owner / lab balance sim
**Status:** `open`

The D&D finalization wired the audited `choose` write boundary
(`services/dnd_workflow.py`) over the pure bounded-menu resolver and ran a
play-review while driving it. One economy finding surfaced that the seam
**cannot** resolve without inventing a balance number (which it does not do) — it
is a balance/owner call, so it is filed here rather than patched or capped:

- **Escort-bundle DOUBLE-MINT — one traversal mints `safe_passage` 2×.** The
  `escort_step` effect completes the single-objective `safe_passage` ESCORT
  bundle and mints the tier-capped reward in ONE step
  (`games/dnd/core/effects.py` `_escort_step`: `offer → accept → apply_event →
  grant_rewards`, minting `catalog.TIER_CAPS[RewardTier.I]`). But the scene
  catalog wires `escort_step` to **two** different options on a single arc
  (`games/dnd/data/scenes.py`): `advance_escort` on `waystation_road`
  (`next_scene_id="waystation_gate"`) AND `signal_escort` on `treeline_watch`
  (`next_scene_id=None`). A single traversal — `waystation_road ·
  advance_escort` (mint #1 → gate) → `waystation_gate · circle_to_treeline`
  (narrate → treeline) → `treeline_watch · signal_escort` (mint #2 → end) —
  therefore completes the `safe_passage` bundle **twice** and mints its reward
  **2×** in one escort. (The seam folds each mint honestly — the running totals
  double — and the two mints are visible as two `reward:*` audit rows.)

**Ask:** decide whether one escort completing `safe_passage` twice (and minting
2×) is intended, or whether the arc should mint the escort bundle at most once.
This is a balance/design question — a sim/owner call, NOT a seam fix. **Meanwhile
every D&D value stays VERBATIM** — no number was invented tonight; the seam folds
exactly the engine's tier-capped bundle and the two effect wirings are the
catalog's, unchanged. The seam does **not** cap the second mint (capping would be
an invented balance number).
```

# Session — VERDICT 042 — Mining economy tuning: descend-gate shape + faucet/sink gap vs the Forge ladder (idea-engine ORDER 006 SIM-REQUEST 4)

> **Status:** `complete`
> 📊 Model: Claude (Fable family) · 2026-07-13 · verdict-042 slice-worker session
> Objective: serve idea-engine ORDER 006 SIM-REQUEST 4 (control/inbox.md @ 8218d66, fm ORDER 044 relay, Q-0264 fan-in batch 2; requesting seat **superbot-games**): MINING-ECONOMY-TUNING — (a) surface descend-gate shape (fresh player with only an iron pickaxe has `max_accessible_depth == 0`; torch `depth_access=1` / lantern `=2`; `games/mining/core/world.py` + `equipment.py`) and (b) faucet/sink gap (base roll 1–2 ore/dig at 1–3 coin values vs iron sword 60 coins in `market.GEAR_SHOP` and Forge I 3,000 coins + 25 iron + 15 stone / Forge II 8,000 + 20 gold + 10 iron in `structures._FORGE_BUILD_LADDER`). Packet: superbot-games `control/outbox.md` § "SIM-REQUEST · mining-economy-tuning · 2026-07-13", pinned @ `menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94`. Method: V038's discipline — byte-copied engine modules with sha256 MANIFEST, fixtures.json pre-registration committed BEFORE the runner, B0 validity gate reproducing every packet-pinned constant exactly before any probe counts, exact-arithmetic primary legs (Fractions, zero decision-bearing RNG) + seeded engine-driven Monte Carlo validation legs (seeds 20260792–20260797, strictly above the dispatch-named 20260791 high-water), byte-identical re-run check. Build subtree `sims/verdict-042-mining-economy/`. Siblings VERDICT 040 (ship-it bundle) and 041 (cookbooks) reserved; this slice is 042 with intake id simreq-006. Worker session — no control/status.md or control/inbox.md writes anywhere; superbot-games and idea-engine untouched.

## What happened

Built `sims/verdict-042-mining-economy/` — a rung-1 NUMERIC SIMULATION driving
the byte-copied superbot-games mining core directly (13 files under
`engine/games/mining/core/`, the FULL import closure — zero stubs — sha256
MANIFEST re-verified before import at pin 57f69be3). fixtures.json (B0
anchors, four play profiles + the NP-1 natural-progression composite, four
acceptance bands in engine-native digs/actions, a NULL-first mechanical
decision rule, and closed-form predictions) committed BEFORE the runner
(git trail: dc69428 precedes 1173cfd). Every decision-bearing number is
exact Fraction arithmetic over engine constants read live; the four seeded
MC legs + the GRID-1 engine-exact grid leg are validation-only.

**Run output:** `SELF-CHECKS: 67 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two clean-shell runs by external diff
(sha256 stdout `1acf51d8…`, results `29e369ac…`). **B0 VALID** — every
packet constant exact (gate 0/1/2, BASE_ROLL_MAX 2, sell values 1/2/3/4/6/12,
sword 60, Forge 3000+{25 iron,15 stone} / 8000+{20 gold,10 iron}). Every
pre-registered closed-form prediction confirmed exactly (32/7, 64/21, 85/22,
106/23, 1.59, the amount-inertness, 22.4).

**Ruling: approve — RATIFY every packet-pinned constant.** Gate (a): G0
worst-case DETERMINISTIC 5 actions / 10 s (chop-craft path); alternatives
buy ≤ 4 actions and delete the light-slot teaching beat — BAND-GATE ratifies
with 4× headroom. Faucet/sink (b): exact 4.571–7.328 coins/dig by depth →
1,646–2,638 coins/h at the engine's own 360 digs/h throttle; NP-1 iron sword
@ ~17 digs, Forge I @ 438.6 digs ≈ 1.09 h, Forge II @ 1,550.8 digs ≈ 4.17 h
— all bands ratify; materials never bind. Three registered reporting flags:
(1) pickaxe + iron pickaxe are amount-INERT (E[amount] 3/2 = bare hands)
under BASE_ROLL_MAX=2 + round() — the 2026-06-22 base-roll cut silently
zeroed the bottom half of the tool ladder; (2) boosters price energy at
0.8 coins/dig < the faucet everywhere → the throttle is profitably
bypassable ×5 (Forge I ≈ 15.8 min boosted); (3) the packet's "~22 coins per
8 digs" reconstructs exactly as the stone/bronze/iron-only undercount —
the true faucet is ~1.6–1.7× higher.

Landed: INTAKE simreq-006 + VERDICT 042 appended to `control/outbox.md`
(append-only; simreq-005 reserved for the in-flight cookbooks sibling).
Sequence: branched off ed2abe2 with V038 at the tail; VERDICT 040 landed
mid-slice @ fc3a5e6 (PR #88) and origin/main was merged INTO this branch
(never rebased), tail re-verified immediately before the append; VERDICT 041
stays reserved/in-flight — this slice took 042 per dispatch, no renumber.
`python3 bootstrap.py check --strict` exit 0. Known walls met as documented:
Write-tool refusal on REPORT.md handled via bash heredoc (the V038 pattern,
zero work lost); one self-inflicted cleanup — engine `__pycache__` briefly
committed, removed by amend before push.

## 💡 Session idea

When a balance packet quotes a soft aggregate ("~22 coins per 8 digs")
alongside hard pinned constants, register a RECONSTRUCTION leg that
searches for the arithmetic that produces the soft number — not just a
comparison against the true value. Here the reconstruction (stone/bronze/
iron-only average × 1.5 × 8 = 22.4) identified exactly WHICH ores the
requesting seat forgot, turning "your estimate is low" into "you dropped
silver/gold/diamond from the value average" — a finding the seat can act on
(fix its play-review arithmetic) rather than merely accept. The portable
rule: a wrong number's DERIVATION is more valuable evidence than its error
size, and on a finite constant table the derivation is usually recoverable
by enumeration.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-040-shipit-bundle-pricing.md`: complete and
honest; exports adopted. (1) Its seed-buffer discipline (register above the
visible high-water with margin for in-flight siblings) was inherited
directly: this head's 20260792–97 were registered per the dispatch-named
20260791 high-water and V040's mid-slice 20260880 draw collided with
nothing. (2) Its disclosed pre-registration correction (a reporting pin
caught by the runner's own self-check) reinforced this head's choice to put
every closed-form prediction INSIDE the self-check battery — all confirmed
on first run, so the discipline cost nothing and would have caught a slip.
(3) Its intake-time provenance finding (the sourceless $64 anchor) has a
sibling here: the packet's Forge-ladder self-correction and its soft
faucet estimate were both classified at intake (anchor vs reporting leg)
before any code existed — the classification held through the run.

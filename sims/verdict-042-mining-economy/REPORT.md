# VERDICT 042 — mining-economy-tuning (descend gate + faucet/sink vs the Forge ladder)

> **Status:** `finalized` · 2026-07-13 · rung 1 NUMERIC SIMULATION · exact
> arithmetic (zero decision-bearing RNG) + seeded engine-driven MC validation
> legs · engine byte-copied @ `menno420/superbot-games 57f69be34785afb427d608b207e7369025166e94`

Serves **idea-engine ORDER 006 SIM-REQUEST 4** (`control/inbox.md @ 8218d66`,
fm ORDER 044 relay, Q-0264 fan-in batch 2), requesting seat **superbot-games**.
Order text, verbatim:

> (4) MINING-ECONOMY-TUNING — (a) surface descend-gate shape: a fresh player
> with only an iron pickaxe has max_accessible_depth==0 and cannot descend
> until a torch (depth_access=1) / lantern (=2) is equipped
> (games/mining/core/world.py + equipment.py); (b) faucet/sink gap: base roll
> 1–2 ore/dig at 1–3 coin values vs iron sword 60 coins (market.GEAR_SHOP) and
> Forge I 3,000 coins + 25 iron + 15 stone / Forge II 8,000 + 20 gold + 10 iron
> (structures._FORGE_BUILD_LADDER);

Packet: superbot-games `control/outbox.md` § "SIM-REQUEST · mining-economy-tuning
· 2026-07-13" (status: open) @ the pin. The packet carries an inline
self-correction on the Forge ladder; the corrected values (Forge I 3,000 +
25 iron + 15 stone; Forge II 8,000 + 20 gold + 10 iron) match ORDER 006 item 4
and the source, and are the B0 anchors.

**One command:** `python3 sims/verdict-042-mining-economy/mining_economy_sim.py`
(exit 0; `SELF-CHECKS: 67 passed, 0 failed`; stdout + `results.json`
byte-identical across two clean-shell runs — sha256 stdout `1acf51d8…`,
results `29e369ac…`).

## RULING: **approve — RATIFY every packet-pinned constant** (per the pre-registered rule)

All four registered acceptance bands land in their ratify ranges. The
"steep faucet/sink gap" premise dissolves once (i) the full six-ore value
table and (ii) the engine's own sim-pinned 360-digs/hour energy throttle are
priced. Three flags ride along (reporting legs, registered as unable to flip
the ruling): a genuinely broken bottom of the pickaxe ladder, a profitable
booster bypass of the energy throttle, and the packet's faucet arithmetic
understating by ~1.6–1.7×.

## B0 validity gate — PASS (every packet number exact, engine-driven)

- `compute_stats({"tool": "iron pickaxe"})` → `depth_access == 0`,
  `world.max_accessible_depth == 0`, `can_descend(0, ·) == False` ✓
- torch `depth_access == 1` (max depth 1), lantern `== 2` (max depth 2) ✓
- `rewards.BASE_ROLL_MAX == 2`; roll support {1, 2} at multiplier 1.0 ✓
- sell values stone 1 / bronze 2 / iron 3 (+ auxiliary silver 4 / gold 6 /
  diamond 12, the packet's own comment) ✓
- `GEAR_SHOP["iron sword"] == 60` ✓
- `_FORGE_BUILD_LADDER == (3000 + {iron:25, stone:15}, 8000 + {gold:20, iron:10})` ✓

## Probe (a) — descend gate: **RATIFY the current shape**

Fresh player, iron pickaxe only, exact measurements:

| arm | worst-case (deterministic) | expected |
|---|---|---|
| **G0 current, chop-craft path** (chop → 2 wood → craft torch → equip → descend) | **5 actions / 10 s** | E[chops] = 4/3 → E[actions] = 13/3 ≈ 4.33 |
| G0 current, dig-sell-buy path (dig to 10 coins → buy torch) | 14 actions (worst 10 digs) | E[digs] = 2.985 (p50 3 · p90 5 · p99 6) |
| G1 pickaxe grants depth 1 | 1 action / 2 s | — |
| G2 torch at 5 coins / 1 wood | 4 actions | E[digs to 5] = 1.90 |

BAND-GATE (ratify iff worst deterministic ≤ 20 actions and ≤ 2 min): G0 passes
at **5 actions / 10 s** — the gate is a seconds-scale progression beat that
teaches the light slot, not a wall. G1 would buy 4 actions and delete the
torch teaching beat (the lantern would still gate Deep); G2 buys ≤ 1 action.
Neither is worth the design surface it burns. The seam's enforcement
(block + record nothing) is correct behaviour against a correctly-shaped gate.

## Probe (b) — faucet vs sink ladder: **RATIFY 60 / 3,000 / 8,000**

Exact per-dig faucet (Fraction arithmetic over live engine constants; iron
pickaxe; grid-average cells per GRID-1, validated ≤ 0.3% by seeded engine MC):

| profile | E[coins/dig] | coins/h @ engine throttle (360 digs/h) |
|---|---|---|
| P0 fresh floor (d0, NORMAL cells) | 32/7 ≈ **4.571** | 1,646 |
| P1 surface roamer (d0) | 848/175 ≈ **4.846** | 1,745 |
| P2 cavern roamer (d1, torch) | 2703/440 ≈ **6.143** | 2,212 |
| P3 deep roamer (d2, lantern) | 8427/1150 ≈ **7.328** | 2,638 |

Natural-progression composite NP-1 (buy torch 10 → lantern 40 → iron sword 60
→ Forge I → Forge II; withheld forge materials priced at sell value +90/+150
coins; fluid expectation accounting per fixtures):

| milestone | cumulative digs | wall-clock (sustained model) | band | verdict |
|---|---|---|---|---|
| torch | 2.2 | ~4 s | — | — |
| lantern | 8.7 | ~17 s | — | — |
| iron sword | 16.9 (P1 standalone: E = 13.31, p50 13 · p90 18 · p99 21) | ~34 s | [10, 200] digs | **RATIFY** (near low edge — flagged) |
| Forge I | **438.6** | **1.09 h** | [200, 2200] digs | **RATIFY** |
| Forge II | **1,550.8** | **4.17 h** | [500, 4400] digs | **RATIFY** |

Materials never bind — coins are the binding resource everywhere: at the
Forge I milestone the player holds E ≈ 181 iron (needs 25) and ≈ 62 stone
(needs 15); at Forge II E ≈ 426 gold (needs 20). The ore-and-coin faucet is
one faucet: the ladder prices in coins and the materials arrive for free on
the way.

## Flags (reporting legs — registered as unable to flip the ruling)

1. **TOOL-LADDER — the bottom two pickaxe tiers are amount-inert.** Under
   `BASE_ROLL_MAX = 2` + `round()`, E[amount] is **3/2 for bare hands, the
   25-coin pickaxe (×1.13) AND the 60-coin iron pickaxe (×1.25)** —
   `round(1·1.25)=1`, `round(2·1.25)=2` (banker's rounding), identical to no
   tool. Gold (×1.375 → E 2) and diamond (×1.5 → E 5/2) do pay. The
   `rewards.py` docstring claim "a better tool still pays" is measured FALSE
   for the pickaxe and iron pickaxe: the 2026-06-22 rebalance (1–3 → 1–2
   base roll) silently zeroed the bottom half of the tool ladder. Candidate
   row for the seat (not ordered): give the low tiers a fractional-carry or
   probabilistic bonus (e.g. `floor(r·m) + bernoulli(frac)`), or re-derive
   `TOOL_POWER_GAIN` against the 1–2 roll — needs its own registered sim.
2. **FAUCET-BYPASS — boosters beat the throttle at a profit.** Ration
   (20 coins → 25 energy) and energy drink (40 → 50) both price energy at
   **0.8 coins/dig**, below the faucet at every depth (4.57–7.33). A
   booster-chugging active player runs ~1,800 digs/h at the 2 s interaction
   floor, netting ≈ 11,750 coins/h at depth 2 — **Forge I in ≈ 15.8 min,
   Forge II ≈ 41.6 min more** (vs 1.09 h / 4.17 h throttled). The 360/h
   energy throttle is therefore a pacing suggestion, not a cap, for anyone
   who buys food. If the seat wants the throttle to bind, the booster price
   must exceed the marginal dig value (> ~7.3 coins/dig-equivalent at depth
   2, i.e. ration > ~183 coins or smaller restore); flagged, not ordered —
   the current shape may be intended ("a coin sink that lets an active
   player dig past the passive rate" is the shop's own comment).
3. **PACKET-ARITHMETIC — the request's faucet estimate is a floor.** The
   packet's "~22 coins per 8 digs" reconstructs exactly as the
   stone/bronze/iron-only value average (28/15 × 1.5 amount × 8 = 22.4/8);
   the true surface faucet including silver/gold/diamond is 36.6 (P0) –
   38.8 (P1) per 8 digs, ~1.6–1.7× higher. The "steep gap" impression came
   partly from this undercount.

## The probe battery (the 8 questions, per the ORDER 005/006 "evidence per your 8-question battery" lineage)

1. **What is this really?** A correctly-shaped seconds-scale descend gate
   plus a faucet/sink ladder whose pacing is already coherent under the
   engine's own 360-digs/h throttle — Forge I ≈ 1.1 h, Forge II ≈ 4.2 h of
   sustained play — with one genuinely broken constant interaction (the
   amount-inert bottom pickaxe tiers) hiding under a "faucet too weak"
   impression fed by undercounted arithmetic.
2. **What is the possibility space?** Gate: three arms measured (grant-on-
   pickaxe, cheaper torch, unchanged) — all within 4 actions of each other,
   so the space is design taste, not economics. Faucet/sink: the three named
   sink constants (60/3,000/8,000), the roll cap, the tool gain, and the
   booster price — swept or priced here; only the last two show anomalies.
3. **Most advanced capability by the simplest implementation?** RATIFY —
   zero constant changes ship this verdict. The one candidate worth a
   follow-up sim is low-tier pickaxe feltness (one rounding-rule change or
   one re-derived gain constant).
4. **What breaks it?** For the ratify ruling: a workflow layer that prices
   non-dig actions in energy (INT-2 flip axis) could stretch NP-1 times —
   but by at most the action counts measured here (≤ 20 non-dig actions to
   Forge I, noise vs 439 digs). For the game: booster-funded play collapses
   sink pacing ×4–6 (flag 2).
5. **What does it unlock?** The seat can close its SIM-REQUEST with the gate
   and ladder ratified and a numeric basis for the two real tuning
   questions it didn't know it had (tool-ladder feltness, booster pricing).
   Cross-verdict: this is the first absolute coins/hour baseline for the
   mining lane — V001/V008/V018/V022/V025/V029's walled "no live earn-rate
   baseline" caveat now has an engine-pinned number to anchor against
   (4.57–7.33 coins/dig · 360 digs/h sustained, boosted ceiling ~11,750/h).
6. **What does it depend on?** The pin 57f69be3 (any retune re-runs the one
   command); GRID-1 (i.i.d. cell draws — validated against the engine's own
   deterministic grid at ≤ 1% abs); INT-1/INT-2 interaction-pacing
   assumptions (burst timings only; sustained numbers are engine-pinned);
   fluid expectation accounting on the two forge legs (±1-dig-scale
   overshoot error at 400+ digs, immaterial).
7. **Which lane should build it?** Nothing to build for the ratify. The two
   flagged candidate rows belong to superbot-games (its constants, its
   registered-sim discipline per the fishing lane's own "never hand-edit a
   weight" rule). Nothing for sim-lab.
8. **Smallest shippable slice?** Close the SIM-REQUEST as ratified (zero
   diffs); optionally file the two candidate rows as new SIM-REQUESTs with
   this sim's tables as the packet.

## What it did NOT settle

- **Fun.** Engine-economic pacing under registered greedy profiles, not
  human-perceived progression feel or retention.
- **The workflow layer.** The pure core has no energy price on non-dig
  actions and no per-action latency; INT-1 (2 s floor) and INT-2 (non-dig
  actions free) are registered assumptions with named flip axes. Sustained
  times are engine-pinned regardless.
- **Multiplayer/market dynamics.** Solo faucet vs solo sink; no player
  trade, no price discovery.
- **The two flagged candidate rows** (tool-ladder feltness fix; booster
  price) — priced, not designed; each needs its own registered sim before a
  constant changes (the V017/V038 discipline).
- **Dynamite, encounters, exploration outcomes** — off the packet's named
  constants; the faucet here is the dig/roll path the packet pinned.

## The validity gate (all five, honestly)

1. **COMPARABLE TO LIVE?** The sim drives the byte-copied engine's own
   functions (`compute_stats`/`max_accessible_depth`/`roll_mine_loot`/
   `apply_cell_to_loot`/`mine_multiplier`, shop/ladder constants read live)
   at the pinned sha. Abstracted away: the Discord workflow layer (INT-1/
   INT-2, flip axes named — affects burst seconds, never the engine-pinned
   sustained times or any band edge), roaming (GRID-1, validated ≤ 1% abs
   against the engine's deterministic grid), and fluid accounting on the two
   long forge legs (±1-dig overshoot vs 400+ digs). No remaining gap moves
   any measurement toward a band edge by more than noise.
2. **UNCORRUPTED?** 67 self-checks, 0 failed, exit 0. B0 reproduced every
   packet constant exactly BEFORE any probe counted. All closed-form
   predictions registered in fixtures.json pre-run confirmed exactly
   (32/7, 64/21, 85/22, 106/23, 1.59, amount-inertness, 22.4). Four seeded
   engine-MC legs agree with the exact numbers at ≤ 0.30% relative (gate
   1%). No cherry-picking: every registered arm and band reported, including
   the near-edge sword number and the two seeds the fixtures did not
   enumerate (GRID-1 legs — disclosed in results.json).
3. **ROBUST?** The ruling is band-medial everywhere that matters: Forge I
   438.6 digs sits 2.2× above the low edge and 5× below the high; Forge II
   1,550.8 similarly. The one near-edge number (sword E 13.3 vs low edge 10)
   is flagged; moving it below the edge flips BAND-SWORD to "sink too
   cheap", which per the registered rule would recommend RAISING the 60 —
   the opposite of the packet's worry — and still not the packet's "gap"
   ruling. Gate worst-case (5 actions) has 4× headroom to its band.
4. **REPRODUCIBLE?** One command, stdlib-only, hermetic (reads only its own
   subtree). stdout + results.json byte-identical across two clean-shell
   runs (external diff; sha256 recorded above). Exact rationals platform-
   independent; MC legs fixed-seed (20260792–20260797, all above the fleet
   high-water 20260791).
5. **LIMITS?** Everything under "What it did NOT settle"; the bands are
   registered judgment lines (full tables ship, a re-drawn line re-reads
   without re-running); "actions" are pure-core actions, not UI round-trips.

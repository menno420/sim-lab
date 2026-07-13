# REPORT — fishing economy tuning: per-species sell/reward curve + fishing progression curve (idea-engine ORDER 006 item 5, seat superbot-games)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 006 · 2026-07-13T09:02Z.
> Packet read READ-ONLY at `menno420/superbot-games` @
> `57f69be34785afb427d608b207e7369025166e94` (blob-filtered clone; sha256
> MANIFEST of every byte-copied file in `fixtures/MANIFEST.json`).
> Run: `python3 sims/verdict-043-fishing-economy/fishing_economy_sim.py`

Binding spec, verbatim (ORDER 006 `do:`, SUPERBOT-GAMES BALANCE item 5):

> (5) FISHING-ECONOMY-TUNING — (a) pin a per-species sell/reward curve (a catch
> grants NO XP/currency today — games/fishing/inventory/adapter.py
> catch_to_grant leaves ProgressionDelta empty; key the curve on species.py
> size_rank/rarity_weight); (b) pin a fishing progression curve (no
> fishing-owned skill/level axis). Fishing is IN-REPO sim-pinned: re-run
> games/fishing/sim/catch_sim.py under new targets per
> docs/design/fishing-catch-skeleton.md §5 — never hand-edit a weight;

## Method

Rung 1 numeric simulation driving the packet's OWN pinned harness: the whole
fishing module closure was byte-copied at the packet sha (`fixtures/`,
sha256-manifested) and `catch_sim.run()` was driven ONLY through its public
entry point per skeleton §5 — **zero edits to any weight or constant**. The
candidate sell/XP curves are a pure exact-`Fraction` fold over the sim's
output distributions (the "new targets" the order names). Pre-registration
(`fixtures.json` — candidate curves, mining-faucet parity grounding, bands
A1–A5 / P1–P3, mechanical decision rule, seeds) was committed BEFORE the
runner (git-trail ordered).

**B0 validity gate (all PASS before any tuning arm ran):**
`catch_to_grant(Catch(...)).progression == ProgressionDelta()` for every
species, with the packet-quoted docstring verbatim in the copied adapter;
the species table exactly minnow 1/50.0 · bass 2/30.0 · pike 3/15.0 ·
legend_carp 4/5.0 (`MAX_SIZE_RANK` 4); `Catch` fields exactly
`(species_id, size)`; `CAST_COST` 2, `DIG_COST` 1, `REGEN_SECONDS` 10,
`MAX_ENERGY` 60, `BASE_ROLL_MAX` 2, the depth-0 ore weights and the ore sell
values 1/2/3/4/6/12 as quoted.

**The parity frame.** Fishing casts debit the SAME energy engine mining digs
from (`catch.py`: "fishing shares the one energy economy"), so the comparable
unit is **coins per energy**. Mining fresh depth-0 (the fresh player is
depth-locked per ORDER 006 item 4a): E[value/ore] = 64/21, E[ore/dig] = 3/2 →
**32/7 ≈ 4.571 coins/energy** (≈ 1,645.7 coins/hour sustained at 360
energy/h). Mining ceiling proxy (diamond tool ×1.5 at depth 4): **755/56 ≈
13.482 coins/energy**. Design cue honoured (`catch.py` verbatim: "Kept modest
— fishing is a slower, calmer faucet than digging"): the parity band centers
at-or-below 1.0×, never above.

## Results (main leg = packet §5 protocol, 48,000 casts/tier; every §5 anchor reproduced exactly)

**(a) Sell curve — APPROVED constants.** Inverse-rarity family
`sell = round(c·50/rarity_weight)` (the mining house style: "commonness is
the inverse of worth"); the pre-registered calibration rule mechanically
picked **c = 8**, matching the registered candidate:

| species | size_rank | rarity_weight | **sell (coins)** |
|---|---|---|---|
| minnow | 1 | 50.0 | **8** |
| bass | 2 | 30.0 | **13** |
| pike | 3 | 15.0 | **27** |
| legend_carp | 4 | 5.0 | **80** |

Coins/energy per (spot, tier), exact: fresh@dock **141427/32000 ≈ 4.4196**
(0.967× mining parity — A1 band [3.8857, 4.8] PASS); gear gradient strict at
every spot (A2 PASS; e.g. dock 4.42 < 5.57 < 7.73); ceiling max =
master@deep_water **10.199 ≤ 13.482** (A3 PASS — fishing's best case stays
under mining's own diamond-tool depth-4 ceiling, so the shared energy pool
stays allocation-stable); place gradient tide_pool < dock < deep_water at
every tier (A4 PASS; fresh: 3.79 < 4.42 < 5.66 — the stingy rare biome pays
per energy); integers strictly increasing in size_rank (A5 PASS).
Semantics: these are per-fish **sell prices for the future market/sell leg**
(the mining-parity shape — ore mints nothing at dig; the numbers are the
future fish `ItemDef.value` rows via the documented
`items.register_fish_species` injection point); `catch_to_grant.currency`
stays 0 at catch time.

**(b) Progression curve — APPROVED constants.** Per catch:
`ProgressionDelta.game_xp = size_rank` (1/2/3/4 — the magnitude the adapter
already relays as `ItemMeta.value`); `global_xp` 0 (quest-owned per the
exploration TIER_CAPS pattern); level ladder `xp_to_next(L) = 50·L`
(cumulative 25·L·(L−1)); milestone levels 10 and 25 (mirrors mining
`titles.py` veteran/legend). **Stat-neutral by construction**: levels grant
no fishing_power/bite_luck, so the pinned gear caps (6/3) and every §5 sim
bound stay untouched — no re-tuning, no pay-to-win drift. Bands: first
level-up inside two full energy bursts fresh@dock (two-burst XP 57.47 ≥ 50,
P1 PASS); XP/h strictly increasing with gear at every spot (P2 PASS); level
25 sustained master@deep_water ≈ **47.0 h** ∈ [24, 120] (P3 PASS — the V038
idle-scale long tail; V038's award-20 sat at ≈39 h).

**Robustness leg** (400 fresh cast-seeds `range(20260881, 20261281)`, all
above the fleet high-water 20260880; new high-water **20261280**): every band
reproduces its main-leg verdict (fresh@dock cpe 4.4177, L25 47.18 h).

**Gates:** 59 self-checks, 0 failed, exit 0; twin coins/energy evaluators
agree on all 18 (spot, tier) cells across both legs; all 20 §5 published
anchors reproduced (9 bite rates, 3 fresh bite counts, 4 dock-fresh species
shares, 3 aggregate bite rates, mean energy exactly 2); mining hand-pins
(64/21, 32/7, 151/28, 755/56) reproduced from the copied source; XP-ladder
identity checked; stdout + results.json **byte-identical across two full
process runs** by external diff (sha256 stdout `acc11b4a…`, results
`d51bb11b…`); ~4.3 s/run, stdlib-only, hermetic (reads only its own
fixtures.json + fixtures/).

## Ruling

**APPROVE-WITH-CONSTANTS** (pre-registered rule: both arms passed all bands
on the main leg and reproduced on the robustness leg). Recommend the manager
relay to superbot-games: wire the sell table {minnow 8, bass 13, pike 27,
legend_carp 80} as the fish sell/reward curve and the progression curve
{game_xp = size_rank per catch; xp_to_next(L) = 50·L; milestones L10/L25,
stat-neutral} — the seam quotes both VERBATIM per the packet's own ask.

## Validity gate (what would flip this)

- A different parity target (e.g. "fishing should out-earn mining deep play")
  re-runs the same committed fold at a re-registered band — table lookup on
  the shipped 18-cell grid, no new sim needed for modest moves.
- Making levels grant stats (G3) voids the stat-neutrality premise and
  RE-OPENS the pinned §5 bounds — that change needs its own sim.
- A sellable-AND-cookable fish (G4: "cooked fish" refills the shared energy
  bar) opens a coins↔energy loop this verdict did not model — named follow-up
  axis; wire the sell leg to NOT double-pay a cooked fish without a sim.
- New species rows / spot rows re-run the fold unchanged (the curve is a
  formula keyed on the data tables, not a hand list).
- Live earn-rate telemetry (G1 — the standing fleet gap) supersedes the
  model-true engine arithmetic wherever they disagree.

## The 8-question probe battery (idea-engine README.md § "The probe battery (v0 — the core method)" @ 8218d66)

1. **What is this really?** An empty-faucet fill-in: fishing has outcomes but
   no economy; the ask is the missing constants, grounded so the shared
   energy pool stays coherent.
2. **Possibility space?** Any (sell curve × XP curve) pair; the binding
   constraint is the shared energy economy — coins/energy parity with mining
   is the only anchor that exists in source today.
3. **Most advanced capability by simplest implementation?** A 4-row sell
   table + a 2-constant XP ladder, both pure data in the existing injection
   points — no new mechanics, no resolver change, no weight edits.
4. **What breaks it?** Stat-granting levels (re-opens §5 bounds); the
   cook-vs-sell loop (G4); a steeper curve (c ≥ 9 breaches the calmer-faucet
   band; registered as ineligible by the calibration rule).
5. **What does it unlock?** The seam's sell/buy leg (audited coin faucet
   parity with mining's), fishing titles/milestones, and the fish ItemDef
   rows the mining port left an injection point for.
6. **What does it depend on?** The pinned species/spot tables and §5 bounds
   (unchanged); the shared energy engine constants; a future sell action in
   the workflow layer (G2 — does not exist yet).
7. **Which lane builds it?** superbot-games (the requesting seat): data rows
   + adapter fill-in + one workflow action; sim-lab owns only the evidence.
8. **Smallest shippable slice?** The sell table alone (fish ItemDef rows via
   `items.register_fish_species` + a sell action quoting `market.sell_price`)
   — the XP axis can follow independently; both sets of constants are pinned
   here.

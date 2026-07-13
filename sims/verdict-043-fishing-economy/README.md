# verdict-043 · fishing-economy-tuning

Serves **idea-engine ORDER 006 SUPERBOT-GAMES BALANCE item 5**
(control/inbox.md @ 8218d66; requesting seat **superbot-games**): pin (a) a
per-species sell/reward curve keyed on `species.py` size_rank/rarity_weight
and (b) a fishing progression curve. Packet read READ-ONLY at
menno420/superbot-games @ `57f69be34785afb427d608b207e7369025166e94`.

Fully hermetic and §5-faithful: the pinned fishing module closure is
byte-copied under `fixtures/` (sha256 `MANIFEST.json` at the packet sha) and
the packet's own `catch_sim.run()` is driven ONLY through its public entry
point — **zero weight edits**; the curves are an exact-`Fraction` fold over
the sim's output. Pre-registration (`fixtures.json`: candidate curves, bands
A1–A5/P1–P3, mechanical decision rule, seeds) committed BEFORE the runner.

**Ruling: APPROVE-WITH-CONSTANTS.** Sell curve (coins, inverse-rarity house
style, c=8): **minnow 8 · bass 13 · pike 27 · legend_carp 80** — fresh@dock
4.4196 coins/energy = 0.967× the mining fresh depth-0 parity anchor 32/7;
ceiling 10.199 ≤ mining's own 755/56 ≈ 13.482. Progression: **game_xp =
size_rank per catch; xp_to_next(L) = 50·L (cumulative 25·L·(L−1));
milestones L10/L25; stat-neutral** (pinned §5 bounds untouched). 59
self-checks 0 failed; byte-identical double run; robustness leg seeds
20260881–20261280 (above fleet high-water 20260880, new high-water 20261280).

Run: `python3 sims/verdict-043-fishing-economy/fishing_economy_sim.py`

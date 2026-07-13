# verdict-046-mining-booster-bypass

> **Status:** `finalized` — VERDICT 046 (INTAKE 035), idea-engine PROPOSAL 035
> ("mining booster bypass / throttle seal", game-mechanics round 5, requesting
> lane routing per Q-0264; consumer seat **superbot-games**).

Balance sim for V042's own reporting-only flag: rations (20 coins → 25 energy)
and energy drinks (40 → 50) price energy at 4/5 coins per dig — below the
faucet at every committed depth row — so the 360/h energy throttle (the mining
lane's only pacing control) is a coin-profitable ×4.45 bypass. This head
sweeps the committed-shape seal levers: booster-admission cap C ∈ {60, 75,
100, 125} effective energy/window × semantics ∈ {sliding-3600 s, fixed-hour}
(8 decision cells), with REPRICE (excluded by registered arithmetic
11325/896 vs 48/7) and HYBRID riding reporting-only, against three
pre-registered bands (SEAL 5/4 · REFILL · PACE 0.8×).

- **Run:** `python3 sims/verdict-046-mining-booster-bypass/booster_bypass_sim.py`
  (stdlib-only, hermetic — reads only its own fixtures.json + engine/ —
  exit 0, stdout + results.json byte-identical across two full process runs,
  cpython-3.11 pinned, ~65 s)
- **Engine:** `engine/games/mining/core/` — the parent VERDICT 042's own
  committed subtree byte-copied (13 files @
  `menno420/superbot-games 57f69be34785afb427d608b207e7369025166e94`, sha256
  per file in `engine/MANIFEST.json`, re-verified before import; ZERO fresh
  clones — the V043/V028 byte-reuse precedent)
- **Pre-registration:** `fixtures.json` — parent anchors machine-read from the
  committed `sims/verdict-042-mining-economy/{results,fixtures}.json` +
  V043's 755/56 hand-pin at build time, never transcribed; bands, cells,
  policies, seeds (20261281–84, above fleet high-water 20261280), decision
  rule (REJECT → APPROVE → NULL) committed BEFORE the runner; one disclosed
  pre-run amendment (gate tolerances) before any execution
- **Results:** `results.json` + `run-stdout.txt` (raw), `REPORT.md`
- **Ruling:** **null** (pre-registered single-cell outcome) — C=60 is the ONLY
  decision cell passing SEAL+REFILL+PACE, in BOTH semantics; C=75 fails PACE
  under the measured ladder front-load premium (Forge I 0.7789 vs the 0.8
  band; the sustained-rate closed form predicted 0.8329). The two-cells rule
  (P031) refuses a single-point band. Named live probe: shop telemetry.

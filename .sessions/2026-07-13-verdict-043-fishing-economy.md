# Session — VERDICT 043 — fishing economy tuning: per-species sell/reward curve + fishing progression curve (idea-engine ORDER 006 SUPERBOT-GAMES BALANCE item 5, requesting seat superbot-games)

> **Status:** complete
> 📊 Model: Claude Fable (family-level) · 2026-07-13 · verdict-043 slice-worker session
> Objective: serve item 5 of idea-engine `control/inbox.md` ORDER 006 @ 8218d66 — "(5) FISHING-ECONOMY-TUNING — (a) pin a per-species sell/reward curve (a catch grants NO XP/currency today — games/fishing/inventory/adapter.py catch_to_grant leaves ProgressionDelta empty; key the curve on species.py size_rank/rarity_weight); (b) pin a fishing progression curve (no fishing-owned skill/level axis). Fishing is IN-REPO sim-pinned: re-run games/fishing/sim/catch_sim.py under new targets per docs/design/fishing-catch-skeleton.md §5 — never hand-edit a weight;". Packet read READ-ONLY at menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94 (blob-filtered clone; the sibling pin 5aec110 superseded at this read). Build `sims/verdict-043-fishing-economy/`: byte-copy the pinned fishing modules incl. `games/fishing/sim/catch_sim.py` (sha256 MANIFEST at the packet sha), B0 validity gate (catch_to_grant empty ProgressionDelta + the species.py size_rank/rarity_weight table as quoted), pre-registered fixtures.json (candidate sell curve keyed on size_rank × rarity_weight grounded against the mining faucet coins/energy scale, progression-curve proposal, acceptance bands, explicit decision rule) committed BEFORE the tuned runs; drive catch_sim.run() only through its own entry points per skeleton §5 — zero weight edits; any fresh seeds strictly above fleet high-water 20260880; final configuration run twice, byte-identical by external diff. Land INTAKE simreq-007 + VERDICT 043 in `control/outbox.md` (append-only; VERDICT 041 (cookbooks) + VERDICT 042 (mining) RESERVED by sibling slices at dispatch). Worker session — no control/status.md or control/inbox.md writes anywhere; superbot-games and idea-engine untouched.

## What happened

Built `sims/verdict-043-fishing-economy/` — the packet's OWN pinned harness
(`games/fishing/sim/catch_sim.py`) byte-copied with its full 23-file module
closure (sha256 `fixtures/MANIFEST.json` at packet sha 57f69be) and driven
ONLY through its public entry point `run(seeds=…)` per skeleton §5 — zero
weight/constant edits anywhere; the candidate sell/XP curves are an
exact-`Fraction` fold over the sim's output distributions. Pre-registration
`fixtures.json` (B0 gate, mining-parity grounding verbatim at path@SHA,
candidate curves, bands A1–A5/P1–P3, mechanical decision rule, seeds)
committed BEFORE the runner (git trail: 9ce3b77 precedes 33a6b8e).

**B0 VALID** (all four gates exact before any tuning arm): catch_to_grant
empty ProgressionDelta for every species + the packet-quoted docstring
verbatim; species table minnow 1/50.0 · bass 2/30.0 · pike 3/15.0 ·
legend_carp 4/5.0; Catch = (species_id, size); CAST_COST 2 / DIG_COST 1 /
REGEN_SECONDS 10 / MAX_ENERGY 60 / BASE_ROLL_MAX 2 / ore values 1–12.

**Run:** `SELF-CHECKS: 59 passed, 0 failed`, exit 0; all 20 §5 published
anchors reproduced exactly on the main leg (the §5 protocol, seeds 0–399,
48,000 casts/tier); robustness leg on 400 fresh cast-seeds 20260881–20261280
(above fleet high-water 20260880 → new high-water 20261280) reproduces every
band; stdout + results.json byte-identical across two full process runs by
external diff (sha256 stdout acc11b4a…, results d51bb11b…).

**Ruling: approve-with-constants.** (a) Sell curve {minnow 8, bass 13,
pike 27, legend_carp 80} coins — fresh@dock 4.4196 coins/energy = 0.967× the
mining fresh depth-0 parity anchor 32/7 (V042's 4.571 coins/dig matches
independently); ceiling 10.199 ≤ 755/56. (b) Progression: game_xp =
size_rank per catch; xp_to_next(L) = 50·L; milestones L10/L25; stat-neutral
(pinned §5 bounds untouched). Landed INTAKE simreq-007 + VERDICT 043 in
`control/outbox.md` (append-only; V041 cookbooks reserved by the in-flight
sibling, V042 mining landed mid-slice @ 48dd6a6, origin/main merged INTO
this branch, never rebased). `bootstrap.py check --strict` exit 0.
PR: https://github.com/menno420/sim-lab/pull/90 (READY; merge-on-green owns
the merge — zero agent merge calls). Worker session — no control/status.md
or control/inbox.md writes anywhere; superbot-games and idea-engine
untouched.

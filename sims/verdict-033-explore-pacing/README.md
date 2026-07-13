# verdict-033 · EXPLORE_ACTION pacing & the quest currency faucet (V018's excluded third trigger, priced)

Can the THIRD encounter trigger (EXPLORE_ACTION quest beats) ride VERDICT
018's committed contract row — per-source clocks + the mandatory combined
per-player cap K=4 per sliding 3600 s — and at which per-source cooldown
c_E, jointly with B (beats per completion) and the admission↔progress
COUPLING (gated vs free)? Plus the mint axis no rate-terms parent could
carry: the quest bundle's per-completion currency is a committed in-tree
integer (TIER_CAPS ≤ GLOBAL_MAX = (20, 120, 50) @ superbot-games
`5aec110`), so per-player currency/hr is computed in ABSOLUTE native units
for the first time. Answers idea-engine PROPOSAL 031 (control/outbox.md
2026-07-13T07:49:09Z, idea
`ideas/superbot-games/explore-action-pacing-quest-mint-2026-07-13.md`,
landed via idea-engine PR #299, main `6daf5ea`) — the ORDER 003
GAME-MECHANICS rotation slot, round 4, following the encounter family's own
excluded-trigger thread (V018: "EXPLORE_ACTION inherits this rule by
contract, not by this sweep"). Fully hermetic: every fixture a pinned
constant committed with the sim; zero repo/network reads at run time.

Model: one player, THREE surfaces, one merged event stream, 8 h window.
Chat = the V001 machine verbatim, grid = the V008 gate verbatim (both
vendored via V018, sha256-pinned, regression-anchored to all 15 published
parent numbers); explore = quest-beat attempts (Poisson r_E/hr honest,
paced 5 s saturating farmer) requesting EXPLORE_ACTION admission against
(c_E clock AND the shared K-window). Gated coupling: admitted beats advance
the quest; free: every attempt advances, encounters fire only when
admitted. Sweep c_E ∈ {0, 300, 600, 900} s × B ∈ {3, 5, 8} ×
{gated, free} at K=4 (24 decision cells); K=6 reporting-only. Bands
committed before the runner: FLOW (≥ 80% of the analytic ceiling), FAIR
(mixed-triple-deep keeps chat+grid ≥ 2.375/hr and ≥ 1 beat/hr), MINT
(farmer ≤ 2.0× honest currency/hr).

Decision (registered order, REJECT first): REJECT iff in GATED coupling at
K=4 NO c_E passes all three bands in ≥ 2 of 3 B values. **Result: REJECT —
0 of 24 decision cells pass all three bands; FAIR is the binding axis in
every cell (the third surface clips V018's honest mixed-deep player from
its committed 2.875/hr to 1.188–1.688/hr, 2.4–3.4× the registered 0.5/hr
materiality allowance), stability-reproduced.** The pre-registered
consequence ships: EXPLORE_ACTION encounters join the K-window, but quest
PROGRESS must not be admission-gated — free coupling is the contract line,
quest pacing stays at the lane's own per-completion host gate, and the
free-coupling mint table (farmer 6,000 currency/hr absolute vs honest
93.75) quantifies why that host gate is load-bearing.

## Run (one command)

```
python3 sims/verdict-033-explore-pacing/explore_pacing_sim.py
```

Exit 0 iff all self-checks pass (25,843). Deterministic: byte-identical
stdout + `results.json` across two process runs by external diff,
cpython-3.11 pinned and asserted. No network, no git, no wall clock. ~5 s.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the decision rule with its evaluation order, the V018 anchor
  set + sha256 pins on all seven chained machinery files, 8 intake-time
  decisions (committed BEFORE the runner; one pre-runner amendment scoped
  the farmer-saturation gate analytically — git history is the trail).
- `explore_pacing_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).

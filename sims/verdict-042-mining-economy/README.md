# verdict-042-mining-economy

> **Status:** `finalized` — VERDICT 042 (intake simreq-006), idea-engine ORDER 006
> SIM-REQUEST 4, requesting seat **superbot-games**.

Balance sim for the superbot-games mining economy: (a) the surface descend
gate (light-gated `depth_access`) and (b) the faucet/sink gap (dig roll vs
iron sword 60 / Forge I 3,000 / Forge II 8,000).

- **Run:** `python3 sims/verdict-042-mining-economy/mining_economy_sim.py`
  (stdlib-only, hermetic, exit 0, byte-identical re-runs)
- **Engine:** `engine/games/mining/core/` — 13 files byte-copied from
  `menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94`
  (sha256 per file: `engine/MANIFEST.json`, re-verified before import;
  zero stubs — the copied set is the full import closure)
- **Pre-registration:** `fixtures.json` (profiles, bands, decision rule,
  closed-form predictions, seed policy) — committed before the runner
- **Results:** `results.json` + `run-stdout.txt` (raw), `REPORT.md`
  (ruling, tables, 8-question battery, validity gate)
- **Ruling:** approve — RATIFY every packet-pinned constant; three flags
  (amount-inert bottom pickaxe tiers; profitable booster bypass of the
  360/h throttle; packet faucet arithmetic ~1.6–1.7× low)

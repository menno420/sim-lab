# verdict-045-exploration-bands

> **Status:** `finalized` — VERDICT 045 (intake simreq-009), idea-engine ORDER 006
> SIM-REQUEST 7, requesting seat **superbot-games**.

Balance sim for the superbot-games exploration lane: (a) reconcile the quest
catalog `TIER_CAPS` (tier I 5/25/10 · II 10/60/25 · III 20/120/50, conservative
placeholders per D-0008) against the superbot Q-0087 dual-track bands; (b)
ratify/tune the survival Medium/Hard gradient (Medium 50/15s/1, Hard 40/20s/1;
Easy ≡ the shipped mining bar per D-0004).

- **Run:** `python3 sims/verdict-045-exploration-bands/exploration_bands_sim.py`
  (stdlib-only, hermetic, exit 0, byte-identical re-runs; ZERO decision-bearing
  RNG — the only RNG anywhere is the packet harness's own internal DetRng
  spacing jitter, packet-owned constants, no registry seeds drawn)
- **B0 gate (standalone):** `python3 sims/verdict-045-exploration-bands/b0_check.py`
  — re-derives every quoted TIER_CAPS / difficulty / energy constant from the
  byte-copied modules and fails loudly (exit 1) on any mismatch
- **Engine:** `engine/games/` — 13 files byte-copied from
  `menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94`
  (sha256 per file: `engine/MANIFEST.json`, re-verified before import;
  zero stubs — the copied set is the full import closure incl. the packet's
  own survival sim harness `games/exploration/survival/sim.py`)
- **Q-0087 evidence:** quoted verbatim in `fixtures.json` from
  `menno420/superbot @ 6d8148808e7965f61cd85625798252fe32e1a409` — KEY FACT:
  Q-0087 is a dual-track PHILOSOPHY + sim METHODOLOGY; its "bands" are three
  FUTURE P0-harness output curves; NO numeric band constants exist upstream
  (D-0008: reconciliation waits on the upstream artifact)
- **Pre-registration:** `fixtures.json` (band definitions, play profiles,
  decision rules, closed-form predictions) — committed before the runner
- **Results:** `results.json` + `run-stdout.txt` (raw), `REPORT.md`
  (ruling, tables, 8-question battery, validity gate)
- **Ruling:** (a) RATIFY-AS-PLACEHOLDERS + honest NULL on the numeric band
  import (no upstream constants exist at the pin); (b) RATIFY the Medium/Hard
  gradient (sustained 360/240/180 actions/hr, casual play provably never
  energy-blocked on any difficulty)

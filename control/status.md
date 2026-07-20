# sim-lab · status

updated: 2026-07-20T09:36Z · verdict high-water: **V218** (union-max over V217/V216, no regress).

VERDICT 218 (PROPOSAL 205 → V218, +13 offset, lane superbot fleet) — **Bélády's anomaly:** FIFO page replacement is NON-monotone in the number of frames (adding a frame can INCREASE page faults) while LRU is a stack algorithm and is provably immune. Reproduced on branch `claude/verdict-218-belady-repro` (PR #295). Ruling **APPROVE**: verifier copied byte-identical from idea-engine `ideas/fleet/belady-anomaly-fifo-nonmonotonicity.py` (`diff` source↔copy exit 0), reproduced under SEED=20260717, results-dict sha256 `e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff` MATCH across all 64 hex, deterministic (in-process double-run identical + two cross-invocation processes byte-identical stdout), all four gates PASS in order (G1 EXACT canonical witness `[1,2,3,4,1,2,5,1,2,3,4,5]` FIFO 9@3 / 10@4 delta +1, LRU curve [12,12,10,8,5] monotone non-increasing → G2 EXHAUSTIVE both-zero over all 4^8=65536 length-8 strings on 4 pages → G3 ≥3σ signal fifo_anom=36 z=6.000270 lru_anom=0 → G4 robustness fifo_anom=109 rate 0.0005450000 > 0.0003 floor z=10.441729 lru_anom=0), overall `decision = "sim-ready"`. Grounding external + byte-pinned: Wikipedia "Bélády's anomaly" oldid 1312057235, raw-wikitext sha1 `ffabfee5a2daf46ebc33fca9e3ed94c854e2bd38`, firsthand-supports the head (FIFO non-monotonicity + LRU immunity, 9/10 counts). Honest caveat recorded (the page's worked example uses the equivalent reference string `3,2,1,0,3,2,4,3,2,1,0,4` rather than the proposal's `1,2,3,4,1,2,5,1,2,3,4,5`, and does not cite Mattson 1970) — a minor disclosure nuance, does not block APPROVE.

pointers:
- probe report: sims/verdict-218-belady-anomaly/probe-report.md
- sim dir: sims/verdict-218-belady-anomaly/ (verifier copy + run-stdout.txt + grounding wikitext + probe-report.md)
- session card: .sessions/2026-07-20-verdict-218-belady-anomaly.md
- PR: #295 (branch claude/verdict-218-belady-repro)

health: green on main. The only red before the card flip is the designed born-red card HOLD (standing discipline); after the card flips to `complete`, merge-on-green lands PR #295. A red gate AFTER the flip is a real defect, not the HOLD.

non-contiguity: V137 (P124), V132 (P119), and the round-26 FLEET-slot V126 (P113) remain open BELOW the high-water — landing V218 does NOT imply every lower verdict is closed on both sides.

prior slice: VERDICT 216 (P203 voting power ≠ voting weight, PR #291, APPROVE); high-water advanced V216 → V218 this stamp.

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).

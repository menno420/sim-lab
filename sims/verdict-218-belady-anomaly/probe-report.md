# VERDICT 218 — Bélády's anomaly: FIFO page replacement is NON-monotone in the number of frames — more frames can mean MORE faults; on the canonical string [1,2,3,4,1,2,5,1,2,3,4,5] FIFO faults 9@3 frames but 10@4 frames (delta +1), while LRU is a stack algorithm and is provably immune — reproduce PROPOSAL 205

- **Slice:** VERDICT 218 · PROPOSAL 205 (P205 → V218, +13 offset, lane superbot fleet)
- **Source proposal:** idea-engine PROPOSAL 205 — **Bélády's anomaly.** A demand-paged cache
  under FIFO page replacement is NON-monotone in the number of frames: adding a frame can
  INCREASE the number of page faults. On the canonical reference string
  `[1,2,3,4,1,2,5,1,2,3,4,5]` FIFO faults EXACTLY 9 with 3 frames but EXACTLY 10 with 4
  frames (anomaly_delta = +1). LRU is a **stack algorithm** (Mattson, Gecsei, Slutz & Traiger
  1970): the resident set at m frames is always a subset of the resident set at m+1 frames, so
  adding a frame can never increase LRU faults — LRU is provably immune.
- **Verifier (source):** idea-engine `ideas/fleet/belady-anomaly-fifo-nonmonotonicity.py`
- **Reproduced by:** sim-lab session 2026-07-20-verdict-218, branch
  `claude/verdict-218-belady-repro` (built off origin/main `ca9a0ce`); verdict PR #295. The
  P205 claim already landed on the control lane (#294).
- **Timestamp (date -u):** 2026-07-20T09:33Z
- **SEED:** 20260717 · stdlib-only (`json`, `hashlib`, `math`, `random`, `collections.deque`).
  G3 consumes `random.Random(SEED)`; G4 consumes `random.Random(20260718)`.

## 📊 Model: Claude · high effort · verdict-reproduction

## Ruling: pending coordinator sign-off

This probe reproduces the disclosed digest byte-for-byte (full-64 exact), determinism holds
both in-process and across invocations, and all four gates PASS in their stated directions.
No final APPROVE/REJECT ruling is written here — the ruling is left to be finalized under
coordinator sign-off (a later worker flips the card).

## Head

A demand-paged cache serving a reference string under FIFO page replacement evicts the
oldest-INSERTED page on a miss. FIFO is NOT a stack algorithm: increasing the frame count can
change which pages are resident in a way that is NOT a superset of the smaller-cache resident
set, so a page that would have been a hit at m frames can become a miss at m+1 frames. On the
canonical string `[1,2,3,4,1,2,5,1,2,3,4,5]` this manifests as FIFO faulting 9 times at 3
frames but 10 times at 4 frames — MORE memory, MORE faults (anomaly_delta = +1). LRU, by
contrast, evicts the least-recently-USED page and IS a stack (inclusion) algorithm: the
resident set at m frames is a subset of the resident set at m+1 frames at every prefix, so
adding a frame can never turn a hit into a miss — LRU faults are monotone non-increasing in
frames and LRU is never anomalous. The verifier certifies this four ways: G1 the EXACT
canonical 9/10 witness plus LRU monotone curve, G2 an EXHAUSTIVE both-zero enumeration over
all 4^8 length-8 strings on 4 pages, G3 a ≥3σ signal at scale (A=6, L=16), G4 a robustness /
regime-shift signal (A=7, L=20).

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` → **exit 0**
  (byte-for-byte identical; source `ideas/fleet/belady-anomaly-fifo-nonmonotonicity.py`).
  Both files sha256 `343bfb407e87c1f2c1039d0af3618ba676b70f75de31202d9befbd59a2d215fe`.
- **Ran under SEED = 20260717**, full stdout captured to `run-stdout.txt`, process **exit 0**
  (`decision: sim-ready`, all gates true).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`; whole-dict, no self-field, stdout-only):**
  - disclosed (PROPOSAL 205): `e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff`
  - reproduced (this run):    `e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality;
    `grep -oE '[0-9a-f]{64}'` yields a single unique 64-hex token of length 64; no
    truncation). The verifier PRINTS this digest (`results_sha256: …`).

## Determinism

- **In-process:** `main()` calls `compute()` TWICE and `assert`s the two compact-canonical
  serializations are equal (`NON-DETERMINISTIC: in-process double-run diverged` otherwise).
  This run printed `in_process_double_run: IDENTICAL` — the assert held, no divergence.
- **Separate cross-invocation:** two independent `python3` invocations produced
  **byte-identical stdout** (`diff run-stdout.txt run-stdout-2.txt` → **exit 0**), both
  printing `results_sha256: e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff`.
- Two seeded RNGs (`random.Random(20260717)` for G3, `random.Random(20260718)` for G4) plus
  the deterministic exhaustive G1/G2, so the whole-dict sha256 is a reproducible determinism
  digest with no self-field.

## Gate evaluation (against PROPOSAL 205's OWN criteria, in order — each read in ITS direction)

Gate polarity is mixed, so each is read in its own direction. **G1 is an EXACT gate** (integer
fault-count equality — no sampling, self-certifying). **G2 is an EXHAUSTIVE EXACT gate** (both
anomaly counts must be EXACTLY 0 over all 65536 strings — any nonzero FAILS). **G3 is a ≥3σ
SIGNAL gate** (a LARGE z is the PASS — opposite polarity to G2). **G4 is a ROBUSTNESS gate**
with a two-legged PASS (rate ABOVE the 0.0003 floor AND z ≥ 3 under a regime shift, LRU still 0).

- **G1 — EXACT canonical witness (`[1,2,3,4,1,2,5,1,2,3,4,5]`; DIRECTION: exact integer
  equality; PASS iff FIFO delta>0 AND LRU monotone non-increasing):**
  - `fifo_3 = 9`, `fifo_4 = 10`, `anomaly_delta = +1` (>0).
  - `lru_curve_frames_1_to_5 = [12, 12, 10, 8, 5]` — monotone non-increasing
    (`lru_monotone_non_increasing = true`). **PASS.**
- **G2 — EXHAUSTIVE EXACTLY-TRUE (all A=4 length-8 strings, total = 4^8 = 65536, frames_max=4;
  DIRECTION: both exactly 0):**
  - `fifo_anomalous = 0` AND `lru_anomalous = 0`. Exhaustive enumeration matches the
    closed-form prediction — LRU immune by the stack property, FIFO cannot be
    Bélády-anomalous with ≤4 distinct pages (pinning the anomaly threshold above 4 pages; the
    classic minimal FIFO anomaly needs 5 pages, length 12). **PASS.**
- **G3 — ≥3σ SIGNAL (N=200000, A=6, L=16, frames_max=6, `random.Random(SEED)`; DIRECTION:
  z ≥ 3, lru_anom == 0):**
  - `fifo_anom = 36`, `p_fifo = 0.0001800000`, `z = 6.000270` (≥ 3.0), `lru_anom = 0`. The
    z clears 3σ because the LRU comparator is provably exactly 0, so even a rare-but-nonzero
    FIFO rate is hugely significant against zero. **PASS.**
- **G4 — ROBUSTNESS / regime-shift (N=200000, A=7, L=20, frames_max=7, `random.Random(20260718)`;
  DIRECTION: rate > 0.0003 floor AND z ≥ 3, lru_anom == 0):**
  - `fifo_anom = 109`, `fifo_rate = 0.0005450000` (> floor `0.0003000000`), `z = 10.441729`
    (≥ 3.0), `lru_anom = 0`. The FIFO anomaly persists above the floor across the regime shift
    while LRU is invariantly 0. **PASS.**

**Overall decision field:** `decision = "sim-ready"` (all of G1/G2/G3/G4 = true).

## Grounding

- **Source:** Wikipedia "Bélády's anomaly" oldid **1312057235** (raw wikitext).
- **Byte-pin:** raw-wikitext sha1 **`ffabfee5a2daf46ebc33fca9e3ed94c854e2bd38`** (confirmed in
  hex, 40 hex chars).
- **Firsthand support (YES):** the page firsthand supports FIFO non-monotonicity (Bélády's
  anomaly — adding a frame can increase FIFO page faults) and LRU immunity (LRU as a stack
  algorithm does not suffer the anomaly), and corroborates the 9/10 fault counts.
- **Honest caveats (recorded):**
  - The page's worked example uses reference string `3,2,1,0,3,2,4,3,2,1,0,4` rather than the
    proposal's equivalent `1,2,3,4,1,2,5,1,2,3,4,5` (a relabelling of the same anomaly
    structure — 5 distinct pages, length 12, delta +1).
  - The page does NOT cite Mattson 1970 (the stack-algorithm result the proposal attributes
    the LRU-immunity to Mattson, Gecsei, Slutz & Traiger 1970); that attribution is the
    proposal's, not the grounding page's.

## Ruling evidence summary

Digest matches full-64 exact
(`e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff`, printed `results_sha256:`
line, single unique 64-hex token of length 64, no truncation); verifier byte-identical (`diff`
source↔copy exit 0, both files sha256
`343bfb407e87c1f2c1039d0af3618ba676b70f75de31202d9befbd59a2d215fe`, source
`ideas/fleet/belady-anomaly-fifo-nonmonotonicity.py`); deterministic (in-process double-run
IDENTICAL via assert AND two cross-invocation processes byte-identical stdout, `diff` exit 0).
All four gates hold in their stated directions: **G1** EXACT (fifo_3=9, fifo_4=10, delta +1,
LRU curve [12,12,10,8,5] monotone non-increasing); **G2** EXHAUSTIVE (fifo_anomalous=0 AND
lru_anomalous=0 over all 65536 strings); **G3** ≥3σ signal (fifo_anom=36, z=6.000270 ≥3,
lru_anom=0); **G4** robustness (fifo_anom=109, rate 0.0005450000 > 0.0003 floor, z=10.441729
≥3, lru_anom=0); overall `decision = "sim-ready"`. Grounding is byte-pinned (Wikipedia
"Bélády's anomaly" oldid 1312057235, raw-wikitext sha1
`ffabfee5a2daf46ebc33fca9e3ed94c854e2bd38`) and firsthand-supports the head (FIFO
non-monotonicity + LRU immunity, 9/10 counts), with honest caveats (worked-example uses the
equivalent `3,2,1,0,3,2,4,3,2,1,0,4` string; does not cite Mattson 1970) that do not block.
**Ruling: pending coordinator sign-off.** (Run stdout: `run-stdout.txt`.)

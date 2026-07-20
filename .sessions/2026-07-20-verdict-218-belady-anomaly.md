# VERDICT 218 — Bélády's anomaly: FIFO page replacement is NON-monotone in the number of frames — giving the cache MORE memory can make it fault MORE. On the canonical reference string [1,2,3,4,1,2,5,1,2,3,4,5] FIFO faults 9 times at 3 frames but 10 times at 4 frames (delta +1), while LRU is a STACK algorithm (Mattson, Gecsei, Slutz & Traiger 1970) and is provably immune — adding a frame can never increase LRU faults, so LRU is never anomalous — reproduce PROPOSAL 205

> **Status:** complete

📊 Model: Claude · high effort · verdict-reproduction

started: 2026-07-20T09:29:54Z

💓 Heartbeat: round-slot FLEET P205 → V218 (+13) reproduction on branch
`claude/verdict-218-belady-repro`; sim dir `sims/verdict-218-belady-anomaly/`
(byte-identical verifier copy + reproduction stdout + grounding wikitext + probe-report),
digest target full-64 `e5c3517c…3bf7bff`, four gates evaluated in order (G1 EXACT canonical
witness FIFO 9@3 / 10@4 delta +1 with LRU monotone non-increasing; G2 EXHAUSTIVE all
4^8=65536 length-8 strings on 4 pages, FIFO_anomalous==0 AND LRU_anomalous==0; G3 ≥3σ SIGNAL
N=200000 A=6 L=16; G4 ROBUSTNESS regime-shift N=200000 A=7 L=20 above 0.0003 floor),
determinism in-process double-run + two cross-invocation processes byte-identical, grounding
byte-pinned (Wikipedia oldid 1312057235, raw-wikitext sha1
`ffabfee5a2daf46ebc33fca9e3ed94c854e2bd38`). Born-red HOLD armed on this first card commit;
released later by a deliberate `complete` flip in a separate worker. PR born-red until then.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so
the substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It
flips to `complete` as the deliberate LAST commit — only after the sim dir (byte-identical
verifier copy + reproduction stdout + grounding wikitext + probe-report), the digest match
(full-64 exact `e5c3517c…3bf7bff`), the in-order G1/G2/G3/G4 gate evaluation (all PASS), the
determinism check (in-process double-run identical AND two cross-invocation processes
byte-identical), and the grounding check have ALL landed — that flip clears the HOLD and
releases merge-on-green. NO merge API calls are made from this session; CI + the landing
automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 205 (P205 → V218, +13 offset, lane superbot fleet): **Bélády's anomaly.**
A demand-paged cache under FIFO page replacement is NON-monotone in the number of frames —
adding a frame can INCREASE the number of page faults. On the canonical reference string
`[1,2,3,4,1,2,5,1,2,3,4,5]` FIFO faults EXACTLY 9 times with 3 frames but EXACTLY 10 times
with 4 frames (anomaly_delta = +1). LRU, by contrast, is a **stack algorithm** (Mattson,
Gecsei, Slutz & Traiger 1970): the resident set at m frames is always a subset of the
resident set at m+1 frames, so adding a frame can never increase LRU faults — LRU is provably
immune to the anomaly. Copies the disclosed verifier
`ideas/fleet/belady-anomaly-fifo-nonmonotonicity.py` byte-identical into
`sims/verdict-218-belady-anomaly/`, reproduces the results-dict sha256, confirms determinism,
and evaluates the four gates in order against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0), stdlib-only (`json`, `hashlib`,
  `math`, `random`, `collections.deque`), SEED = 20260717. G3 uses `random.Random(SEED)`;
  G4 uses `random.Random(20260718)`.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results
  dict's own sha256 IS the digest (`json.dumps(d, sort_keys=True, separators=(",",":"))`);
  target `e5c3517c9d3408bc76941be37b820d0216fcbe0fb00c2cffaf1d8bf763bf7bff` matched across all
  64 hex chars, identical across two fresh cross-invocation runs.
- Gates (in order, against the proposal's OWN criteria — read each in ITS direction):
  - **G1 EXACT canonical witness (`[1,2,3,4,1,2,5,1,2,3,4,5]`; direction: exact integer
    equality)** — FIFO faults == 9 at 3 frames and == 10 at 4 frames, anomaly_delta = +1
    (>0); AND LRU faults on the SAME string are monotone non-increasing across frames 1..5.
    PASS iff FIFO delta>0 AND LRU monotone non-increasing.
  - **G2 EXHAUSTIVE EXACTLY-TRUE (all A=4 length-8 strings, 4^8=65536, frames 1..4;
    direction: both exactly 0)** — FIFO_anomalous == 0 AND LRU_anomalous == 0. Exhaustive
    enumeration matches the closed-form prediction — LRU is immune by the stack property, and
    FIFO cannot be Bélády-anomalous with ≤4 distinct pages, pinning the anomaly threshold
    above 4 pages (the classic minimal FIFO anomaly needs 5 pages, length 12).
  - **G3 ≥3σ SIGNAL (N=200000 random strings, A=6, L=16, frames 1..6, `random.Random(SEED)`;
    direction: z ≥ 3)** — two-proportion one-sided z-test H0 p_fifo==p_lru vs p_fifo>p_lru.
    z clears 3σ because the comparator LRU is provably exactly 0. LRU anomaly count must be 0.
  - **G4 ROBUSTNESS / regime-shift (N=200000 random strings, A=7, L=20, frames 1..7,
    `random.Random(20260718)`; direction: rate above floor AND z ≥ 3)** — FIFO anomaly rate
    stays above floor 0.0003 AND the shifted-regime two-proportion z (FIFO vs LRU=0) ≥ 3,
    while LRU stays exactly 0.
- Grounding: Wikipedia "Bélády's anomaly" oldid 1312057235, raw-wikitext sha1
  `ffabfee5a2daf46ebc33fca9e3ed94c854e2bd38` (byte-pinned). Caveat: the page firsthand
  supports FIFO non-monotonicity and LRU immunity and corroborates the 9/10 counts, but its
  worked example uses reference string `3,2,1,0,3,2,4,3,2,1,0,4` rather than the proposal's
  equivalent `1,2,3,4,1,2,5,1,2,3,4,5`, and does not cite Mattson 1970.

## ⟲ Previous-session review

Previous-session review: VERDICT 217 (hat-check invariance — for a uniform random permutation
of n items the number of fixed points has mean EXACTLY 1 for every n≥1 and variance EXACTLY 1
for every n≥2; the derangement probability D_n/n! → 1/e ≈ 0.3679; the whole fixed-point count
converges to Poisson(1), PROPOSAL 204 → V217) landed complete with a full-64 digest MATCH
(`7b99e650…46dfb0`) and all four gates PASS via the born-red HOLD choreography — `in-progress`
first commit, deliberate `complete` flip last. Its carry-forward was GATE-POLARITY discipline:
read each gate in ITS OWN direction — V217's G1 was an EXACT `Fraction`/exhaustive gate (any
mismatch FAILS), G2 a ≥3σ FLOOR gate with a two-sided consistency leg, G3 an AGREEMENT gate (a
SMALL cross-scale range is the PASS), G4 a GOODNESS-OF-FIT gate (a SMALL χ² is the PASS). V218
re-tunes that mix AGAIN: G1 is an EXACT gate (integer fault counts 9@3 / 10@4, delta +1, LRU
monotone — self-certifying, no sampling); G2 is an EXHAUSTIVE EXACT gate (both anomaly counts
must be EXACTLY 0 over all 65536 strings — a single nonzero FAILS); G3 is a ≥3σ SIGNAL gate (a
LARGE z is the PASS — the opposite polarity of G2, and note the significance comes from the
provably-zero LRU comparator, not a large absolute FIFO rate); G4 is a ROBUSTNESS gate with a
two-legged PASS (a FIFO rate ABOVE the 0.0003 floor AND z ≥ 3 under a regime shift, with LRU
still exactly 0). The load-bearing evidence is the EXACT G1/G2 block (the canonical 9/10
witness plus the exhaustive both-zero enumeration), with G3/G4 corroborating the anomaly's
persistence at scale. Standing non-contiguity persists: V137 (P124), V132 (P119), and the
round-26 FLEET-slot V126 (P113) remain open BELOW the high-water; landing V218 does not imply
every lower verdict is closed.

## 💡 Session idea

The asymmetry between FIFO and LRU is not two separate facts but ONE structural distinction:
LRU is a **stack (inclusion) algorithm** and FIFO is not. A cheap orthogonal extension that
reuses `lru_faults`/`fifo_faults` verbatim would ADD a deterministic "stack-inclusion gate":
for the canonical string (and a handful of exhaustive short strings) reconstruct the actual
RESIDENT SET at each frame count m and assert directly that `resident_LRU(m) ⊆ resident_LRU(m+1)`
at every prefix position — the Mattson inclusion property itself — while exhibiting at least
one prefix where `resident_FIFO(m) ⊄ resident_FIFO(m+1)`. This turns the anomaly gates
(counts of anomalous strings) into a witness of the ROOT CAUSE (the inclusion property holds
for LRU and is violated by FIFO), from which non-anomaly of LRU is a corollary rather than an
observed count. The digest-bearing results dict and the four shipped gates stay byte-identical;
only a sibling exact stack-inclusion gate is added.

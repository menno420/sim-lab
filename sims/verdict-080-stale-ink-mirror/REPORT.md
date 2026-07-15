# VERDICT 080 — the stale-ink mirror (idea-engine PROPOSAL 067) — REPORT

## Ruling

**NULL — registered axes n4 + n3** (per the pre-registered rule applied in
the registered order REJECT → INVALID → APPROVE → NULL; both
independently-written decision evaluators agree NULL/NULL on the same axes;
every decision number is an exact integer or exact rational).

The REJECT — the drafter's predicted landing — does **not** fire, twice
over:

- **R3 fails — the two-morning decode theorem (T3b) is FALSE as
  registered.** The registered claim ("the 12 consecutive-value pairs are
  pairwise distinct, so any unclamped consecutive pair of dawn readings pins
  (base, phase) uniquely") fails at **every one of the 24,360** unclamped
  consecutive-pair cases over the full achievable (base, phase) grid:
  candidate histogram {2: 1160, 3: 3828, 4: 6264, 5: 5800, 6: 7308} — and
  at every one of the 506 such cases on the committed world's own 20 cells
  ({2: 27, 3: 100, 4: 113, 5: 100, 6: 166}). Canonical counterexample:
  TALLOW, true (base, phase) = (7, 0), day 5, readings (9, 10) — **six**
  indistinguishable in-grid worlds {(7,0), (8,11), (9,10), (10,9), (11,8),
  (12,7)} produce exactly those two mornings, all clamp-free. The algebra
  error is precise: the 12 tri-value pairs ARE pairwise distinct (T3a,
  verified exact), but distinct tri pairs do not give reading-space
  identifiability — a base translation composes with a phase shift inside a
  diff-sign class (r1 − r0 = ±step only halves the phase residues; the six
  survivors each pair with a different base). This is the registered **n4**
  axis verbatim: theorem failure without gate failure.
- **n3 fires — the R2 collapse clause is world-fragile.** With R1 and R2
  both holding on the committed world, Arm R's 200-world census replicates
  R2 on only **56/200 = 0.28 < 1/2** (stability set, fresh 200 worlds:
  41/200 = 0.205; the first-20 slice of the main set: 5/20 — the drafter's
  own drafting census was 9/20, below 1/2 as well, disclosed at
  registration as the armed axis). Per fixture convention C11 the n3 axis
  is read as the registered carve-out of REJECT.

What DID hold — and stands as the citable exact findings inside the NULL:

- **R1 exact (the mirror and the photograph are real):** I(6) = **300/300**
  (den 300 ≥ 250), I(12) = **0/300**, E(12) = **0/360**, clamps included, on
  the committed world. The inversion staircase is perfect: I(a) = (0, 60,
  120, 180, 240)/240 for a = 1..5, 300/300 at a = 6, mirroring back to 0/240
  at a = 11 and 0/300 at a = 12. E sums a = 1..12: (669, 1131, 1596, 1838,
  2075, 2067, 2064, 1828, 1591, 1127, 664, 0). 53/600 impact-free cells sit
  at a clamp bound (C1 reading) and the census is still total. T1 and T2 are
  exact identities for all m.
- **R2 exact on the committed world:** SCRYER/ORACLE = 1278/1311 =
  **0.974828 ≥ 9/10** (1.0831× over the line — the drafter's 1.0194×
  knife-edge WIDENED under the registered-text scaffold). All three
  informed arms cross 300 gold by day 6 (the committed route's own proof
  does it in 13). SCRYER identifies 16/20 cells by day 30 — matching the
  drafter's disclosure, and now structurally explained by the T3b
  counterexample census (some cells never accumulate identifying variety).
- **Corrected decode law (the n4 finding, C12):** k consecutive unclamped
  mornings leave (histograms in results.json): k = 2 → 2–6 candidates
  (never 1), k = 3 → first uniques, k = 7 → always unique. And the lag-6
  MIRROR identity itself is the fastest decoder: base = (r_d + r_{d+6})/2
  exactly at all 18,624 unclamped anti-phase pairs (T2 corollary) — the
  drafter's headline lag is also the decode lag, two mornings six days
  apart, not two consecutive mornings.

## Gates — ALL GREEN (31 self-checks, 0 failed, exit 0)

- **F1** — base/phase re-derived from seed 0x5749434B match the registered
  tables (both arms); day-1 impact/shock-free price table matched; the
  (THORNBY, SALT) witness track (34, 34, 33, 31, 29, 27, 29, 31, 33, 34,
  34, 34) matched, base 33 / phase 6 confirmed.
- **F2** — T1 (photograph) and T2 (mirror) exact for all m, both arms; T3a
  (12-pair distinctness) exact; T3b measured by exhaustive twin-checked
  enumeration — FALSE, routed to n4 per the registered axis text and C7
  (the enumeration machinery is twin-gated; the theorem's truth value is a
  finding, not a control failure).
- **F3** — E sums and the I staircase exact; E(12) = 0 and I(6) = 300/300 as
  committed-world identities; the A-then-B round trip is net-0 exactly at
  all 547 cap-free clamp-free cells (the committed "hammering A/B in place
  always loses gold" comment is a disclosed micro-erratum, reporting-only).
- **F4** — hand world (2 towns × 1 good, step 1): E(1, 3, 6, 12) = (24, 56,
  72, 0), I = (0/16, 8/16, 20/20, 0/20) — pencil values, both arms.
- **F5** — drift_step 0 → E ≡ 0 and empty I census (ink never lies);
  E(12) = E(24) = E(36) = 0 exactly, both arms.
- **F6** — Arm B (literal day-walk, independently written: track-list
  triangle, walked price calendars, flat-dict engine, separately-coded
  planner) exact-equal on every published number including all four-arm
  censuses (both scaffolds, both deck rows), the E/I surfaces, the theorem
  censuses, and every Arm-R per-world row; twin decision evaluators agree
  NULL/NULL on axes [n3, n4]; SCRYER candidate sets never empty (C4);
  seed registry exactly [20261590, 20261591, 20261592], aux 20261593 never
  read (C8); stdout + results.json byte-identical across two full process
  runs; CPython 3.11 asserted.

## Reproducibility

One command, no flags:
`python3 sims/verdict-080-stale-ink-mirror/stale_ink_mirror_sim.py`.
Two full in-repo process runs externally diffed — byte-identical. sha256:
`run-stdout.txt`
`c49a2a1f67c10691a1623d18f10cb7fdbe8382195c507a0219e6af63f48f26de`,
`results.json`
`93da51deeadfdd60bb00021f056d3b6b6573144ba72cb785c11b8c6299725e55`.
~12 s/run on CPython 3.11.15, stdlib-only, hermetic (reads only its own
`fixtures.json`). Seeds constructed: 20261590 (Arm-R main), 20261591
(stability), 20261592 (presentation sample); aux 20261593 asserted never
read. This session allocated NO seeds of its own — the P067 drafter's
registered allocation is the session seed set (the V077–V079 precedent);
the 20261584–589 gap is the drafter's disclosed V079-buffer, unused.
Registration trail: born-red card f3d7676 → fixtures 6ad8134 → runner
1380d42 → accepted run (this commit). One disclosed pre-run correction: the
fixtures' DECIMAL rendering of the seed constant was a transcription slip
(1465009995 for hex 0x5749434B = 1464419147), caught by F1's own gate in a
scratchpad rehearsal and corrected in the runner commit BEFORE the committed
pipeline ever ran; the hex string was authoritative and unchanged. No
fix-forwards after the runner landed — the first complete in-repo run of
the committed pipeline is the accepted run.

## Headline tables (exact; full detail in results.json)

Four-arm census, registered-text scaffold (C2/C3), committed world:

| arm | decks ON | first ≥300 | decks OFF | first ≥300 |
|-----|----------|------------|-----------|------------|
| ORACLE | 1311 | day 6 | 1239 | day 6 |
| SCRYER | 1278 | day 6 | 1290 | day 6 |
| INKTRUTH | 900 | day 6 | 792 | day 6 |
| BLIND | 9 | never | 11 | never |

Decision ratio SCRYER/ORACLE (decks ON) = 1278/1311 ≈ **0.9748** ≥ 9/10;
decks-OFF ratio 1.0412 (below the registered 11/10 overshoot line — the
drafter's 1.209 decks-OFF overshoot anecdote does not reproduce). INKTRUTH
≫ BLIND everywhere: the REJECT that didn't fire was never against the
ledger having value.

Arm R (200 alternative worlds, decks ON, registered scaffold): R2 holds in
56/200 (main) / 41/200 (stability). Ordering census (main): O>S>I>B 83,
O>I>S>B 58, S>O>I>B 25, I>O>S>B 17, S>I>O>B 9, I>S>O>B 6, O>I>B>S 1,
O>S>B>I 1 — ORACLE first in 143/200, BLIND last in 198/200.

## Anomalies — first-class, never smoothed (C9)

Matches (6): the E sums, I(6), I(12), the 53/600 clamp census (C1 at-bound
reading), the day-6 informed crossing, SCRYER's 16/20 identification.

Mismatches (10), with diagnoses:

- **A1 — the four-arm table is systematically off by a reserve constant.**
  Disclosed ORACLE 1309/1237 (ON/OFF) and INKTRUTH 898 reproduce EXACTLY
  under reserve = toll·dist + **toll** (the drafter-evident scaffold, C10
  reporting row) — the registered text says toll·dist + **guard fee**. The
  drafting prototype evidently reserved one toll, not the fee. Decision
  numbers here ride the registered text (1311/1239/900); the ruling is
  scaffold-insensitive across both variants (ratio 0.9748 either way).
- **A2 — SCRYER 1201 (ON) / 1496 (OFF) and BLIND 0 do not reproduce** under
  any natural reading of the registered belief text tried (nearest natural
  reading, C4: 1276/1288 and 18 under the drafter-evident scaffold). The
  registered SCRYER prose underdetermines the unidentified-cell belief; the
  drafter's 0.9175 knife-edge and 1.209 decks-OFF overshoot are properties
  of their unregistered fallback, not of the world. Direction preserved
  (SCRYER ≈ ORACLE ≫ INKTRUTH ≫ BLIND ≈ ruin).
- **A3 — the T3b drafting verification cannot reproduce** ("T3 ... unique
  (base,phase) recovery from every unclamped consecutive pair over the full
  (base, phase) grid" was disclosed as verified at drafting): uniqueness
  fails at literally every case. The drafting enumeration evidently checked
  T3a only. This anomaly IS the n4 finding.
- **A4 — alt-world replication:** drafting 9/20 vs this run's 56/200
  (first-20 slice of the registered stream: 5/20) — levels differ with the
  SCRYER convention, but BOTH sit below 1/2: the drafter's own census
  corroborates n3.

## Boundaries (pre-registered, ride the verdict)

- **Planner boundary:** all gold numbers are properties of the shared
  greedy scaffold (held identical across arms; only the belief axis
  varies), plus — measured this session — of the belief-fallback
  convention the registration left open (A2). A full-DP upper bound is the
  named free follow-up.
- **Deck boundary:** contracts unused by all arms; rumor/hazard decks ON at
  the decision cell as shipped; decks-OFF row reported.
- **Impact boundary:** beliefs impact-free, execution impact-exact, shared.
- **Magnitude boundary:** the E/I surfaces and T1/T2 are theorem-backed;
  the gold gaps ride the committed seed's world, with the Arm-R census as
  the honesty row — and that row is exactly where the REJECT died (n3).
- **Intent boundary:** NULL does not say the game is bad. T1/T2/R1 stand:
  at the map's natural week-lag revisit the ledger lies deterministically,
  in a computable direction — that finding survives and is citable. What
  did NOT survive pre-registration is the two-morning-decode sentence (n4)
  and the world-robustness of the planner collapse (n3).
- **Version boundary:** the verdict conditions on Wickroad v0.4 @ c0c6882
  (re-verified firsthand this session). gba-homebrew moved to v0.5 (wider
  7-town map, 18ddd08) AFTER the registration pin — the legacy 5-town
  world init, tri12, seed and price law are unchanged there, but the wider
  map changes the natural round-trip lags; per the registered application
  guard, a de-periodized or re-seeded later cut means re-run, not reuse.

## Consequence (pre-registered NULL branch, verbatim-faithful)

Routing is the manager's per Q-0260 — this repo never edits gba-homebrew
files; nothing here builds, publishes, or spends. Per the registration:
"NULL → the named axis ships with its exact census as the citable number."

- **n4 census (citable):** the two-morning decode is FALSE — two unclamped
  consecutive mornings leave 2–6 indistinguishable worlds (full histogram
  in results.json); 7 consecutive mornings always decode; and the mirror
  identity itself decodes fastest: two mornings SIX days apart pin base
  exactly (base = (r_d + r_{d+6})/2, all 18,624 unclamped anti-phase
  pairs). The lane's hook sentence about stale ink survives longer than
  the drafter's replacement claim did: remembering a town for a week does
  NOT hand the player its books — it hands them a 6-way riddle whose
  fastest key is the mirror lag itself.
- **n3 census (citable):** per-world four-arm rows for all 200 + 200
  worlds in results.json; the SCRYER≈ORACLE collapse is a property of the
  shipped seed's world in ~1 world in 4, not of the law's generic worlds.
- **What survives for the lane (T1/T2/R1, exact):** lag-12 ink is a
  photograph, lag-6 ink is a perfect mirror (300/300, clamps included),
  and the flagship EMBERTON↔THORNBY round trip sits dead center in the
  certain-inversion band. The consequence menu the drafter pre-registered
  for REJECT ((a) per-run world seed; (b) co-prime per-good periods;
  (c) lean in and surface the decode) remains the natural menu for THESE
  survivors, but under a NULL it routes as information, not as a
  recommendation issued by this verdict; any re-registration should carry
  the corrected T3 and an n3-aware, fully-pinned scaffold.

Named follow-ups, none in scope: a fully-pinned re-registration of the
planner census (machine-readable scaffold constants — the V079 session
card's structured-disclosure idea, now with a measured failure mode); the
full-DP upper bound; the v0.5 wider-map re-run.

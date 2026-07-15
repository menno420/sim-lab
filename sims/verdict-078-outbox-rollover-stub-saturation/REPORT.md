# VERDICT 078 — outbox rollover stub saturation (idea-engine PROPOSAL 065) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT → INVALID → APPROVE → NULL; both independently-written decision
evaluators agree REJECT/REJECT; every decision number a seedless exact
integer):

- **N\*_stub = 233 ≤ 300** (1.29× under the line; the pipeline is at 64) —
  the committed mandatory-pointer-stub rollover saturates the live outbox at
  233 proposals: the roll fires and the file is STILL ≥ 204800.
- **Thrash is real: 18 pre-saturation rolls have spacing ≤ 2 ≥ 8** (2.25×
  over the line; collapse at roll 34, proposal 209 — rolls 34–51 all fire ≤ 2
  proposals apart, the last ten fire on EVERY append).
- **The obvious fix underdelivers: N\*_range = 671 ≤ 4 × 233 = 932** exact
  (multiplier 671/233 ≈ 2.88, 1.39× under the line) — because the roll
  RECEIPTS are a second tombstone family (24.77% of the wall mass) — **while
  P-COMPACT holds a CONSTANT floor** (34,030 = H0 + h_r + s + W·b, spacing
  constant 11) over the full 100,000-append walk. The wall is policy-born,
  not volume-born.

"Roll when big" is a counter, not a thermostat: every roll raises the floor
(F_1 = 39,330 → F_51 = 205,930, strictly monotone), the saturation floor
decomposes as stub 122,430 / receipts 51,000 / window 32,000 / header 500,
and block-size discipline buys zero wall (RECEIPT-FREE INVARIANCE: at
h_r = 0, W = 0 the wall is ceil((T − H0)/s) = 386 — identical across
b ∈ {8000, 16000, 24000}).

## Gates — ALL GREEN (33 self-checks, 0 failed, exit 0)

- **F1** — file size == sum of parts at every append (every one of the 243
  grid cells, Arm B's literal ledger); conservation appended == archived +
  live fulls at every roll, every cell; the spacing identity
  Δ_k = ceil((T − F_k)/b) re-derived by the event walk at the decision cell;
  the floor law verified at every roll under all three policy forms
  (P-STUB H0 + k·h_r + s·n_k + Σ window; P-RANGE s·k; P-COMPACT s + h_r
  constant).
- **F2** — (a) FLOOR LAW timing invariance: the roll-every-25 alternate
  schedule matches the closed form in (k, appends) at every roll, all three
  policies, exact; (b) RECEIPT-FREE INVARIANCE: wall = 386 =
  ceil((204800 − 500)/530), identical across the whole b grid; (c) COMPACT
  BOUNDEDNESS: floor constant 34,030 and spacing constant 11 over the
  100,000-append walk, both arms full length; MONOTONE THRASH (F_k strictly
  increasing, Δ_k non-increasing) at every P-STUB grid cell.
- **F3** — closed-form anchors, all hit exactly: N\*_stub = 233, K = 51,
  first spacing 13, first floor 39,330 = 500 + 1000 + 530·11 + 32000,
  collapse index 34, 18 thrash rolls, saturation floor 205,930 with
  composition 122,430 / 51,000 / 32,000 / 500, N\*_range = 671, P-COMPACT
  floor 34,030. (The anchor's inline derivation TEXT for the first spacing
  is anomaly A1 below — the VALUE is confirmed.)
- **F4** — hand world (T = 100, H0 = 10, h_r = 5, s = 2, b = 20, W = 1):
  N\* = 18, K = 8, spacings (5, 3, 3, 2, 2, 1, 1, 1), floors (43, 54, 65,
  74, 83, 90, 97, 104) — both arms, matching the pencil walk.
- **F5** — degeneracies: s = b = 16000 lands N\* = 13 (compaction reclaims
  nothing but the window); s = 0 AND h_r = 0 (true deletion) never saturates
  in 100,000 appends, floor constant 32,500 — both arms.
- **F6** — Arm B (literal byte-ledger, independently written) exact-equal on
  every Arm-A number across all 243 grid cells (walls, K, every floor entry,
  every spacing entry, every composition row; unbounded cells on the
  registered prefix, decision-cell P-COMPACT and true-deletion at full
  100,000-append length); twin decision evaluators agree REJECT/REJECT;
  Arm-R draw sentinels exact (one uniform per appended proposal — 2,274,645
  main + 454,597 stability draws == the summed walls); aux seed 20261570
  never read (constructor registry: [20261567, 20261568, 20261569]); stdout
  + results.json byte-identical across two full process runs; CPython 3.11
  asserted.

## Reproducibility

One command, no flags: `python3
sims/verdict-078-outbox-rollover-stub-saturation/rollover_stub_saturation_sim.py`.
Two full process runs externally diffed — byte-identical. sha256:
`run-stdout.txt`
`7bb7368eeedd4e95cf3d275611e8e95da4abcb63b16e519d263fd839a494af6a`,
`results.json`
`e74f959a2aead814ad6c80ad47944d8dd3cedb085f181e1c59d1882cb8992c17`.
~8 s/run on CPython 3.11.15, stdlib-only, hermetic (reads only its own
`fixtures.json`). Seeds constructed: 20261567 (main), 20261568 (stability),
20261569 (presentation shuffle — read by the shuffled stdout wall-table
listing only); 20261570 reserved, asserted never read. No fix-forwards —
the first complete run of the registered pipeline is the accepted run
(exit 0 on that run).

## Headline tables (exact integers; full grid in results.json)

N\*(W, b) under the committed P-STUB at T = 204800, s = 530:

| W \ b | 8000 | 16000 | 24000 |
|-------|------|-------|-------|
| 0     | 318  | 283   | 258   |
| 2     | 292  | 233   | 187   |
| 8     | 215  | 92    | 17    |

(The W = 8 / b = 24000 corner saturates at 17 proposals — a verdict-lag
stall at fat blocks eats the whole threshold in window mass.)

s grid at the decision cell: 265 → 369, 530 → 233, 1060 → 136. T grid:
102400 → 76, 204800 → 233, 409600 → 581 (N\* ≈ linear in T — raising the
threshold is pure postponement). Receipt-free invariant wall: 386 across the
entire b grid.

Falsifiability behaved exactly as registered: the T = 409600 cell lands
N\* = 581 ≥ 500 with all first-20 spacings ≥ 12 (one grid step up the
threshold lands APPROVE outright); the W = 0 / b = 8000 corner (318) and the
halved-stub cell (369) sit inside the (300, 500) straddle; and APPROVE at
the decision cell itself was arithmetically live until the stub grammar was
measured — a heading-only 150 B stub lands N\* = 504 ≥ 500 (the committed
heading+target+idea-URL stub at 530 B is what puts the wall inside pipeline
scale). The 200,000-decimal threshold reading lands 224 — immaterial to
every band, as disclosed.

Decision-cell spacing series (13, 11, 10, 10, 10, 9, … 2, 2, 1 × 10): the
first spacing is 13, the collapse to Δ ≤ 2 happens at roll 34 (proposal
209), and the last ten rolls fire on every single append.

## Arm R (seeded, REPORTING-ONLY — no statistical gate)

Under the pinned size mix {8000: 1/4, 16000: 1/2, 24000: 1/4} (mean exactly
16000): main leg (10,000 episodes) wall mean 227.4645 (exact 454929/2000),
min 213, median 228, max 245; stability leg (2,000) mean 227.2985. **Named
finding (mix drift, ruling-neutral):** 86.25% of mixed-size episodes
saturate BELOW the constant-size wall 233 (4.66% at, 9.09% above) — size
variability pulls the wall slightly REJECT-ward on average, and the whole
distribution (213–245) sits far inside the (300, 500) straddle band, so no
plausible size mix moves the ruling. Draw sentinels exact: one uniform per
appended proposal, per-episode draws == that episode's wall, both legs.

## Anomalies — first-class, never smoothed

**A1 (drafter derivation-text slip, ruling-neutral, value confirmed):** the
proposal/idea file writes "first spacing 13 = ceil((204800 − 32500)/16000)"
— the as-written expression evaluates to **11**, not 13 (asserted in-sim).
The event-walk-correct expression is ceil((204800 − 500)/16000) = 13
(spacing 1 runs from the empty file, header only — the hand world's own
first spacing 5 = ceil((100 − 10)/20) fixes the convention). The anchored
VALUE 13 is what the walk yields and what the rest of the disclosed landing
requires (N\* = 233 = 13 + Σ later spacings); no decision clause reads the
expression. Same family as V077's A1: a disclosed-landing channel mixing
exact values with an unchecked inline derivation.

**A2 (drafter approximation/rounding, ruling-neutral):** two disclosed
reporting values differ in the last digit from the exact re-derivation —
collapse proposal disclosed "≈ 208", exact **209** (the drafter's tilde
marks it approximate); stub share disclosed "59.4%", exact **59.4522%**
(truncation, not rounding — 59.5 at one decimal). All 12 other disclosed
comparison rows (the full W×b, s, and T wall tables, the 150 B-stub APPROVE
counterfactual 504, the 200,000-decimal reading 224, the T = 409600
first-20-spacings floor, receipt share 24.8, window share 15.5, multiplier
2.88, retrodicted floor 63,710, roll-2 forecast 11 fulls, wall date
2026-07-27) reproduced exactly.

## Reporting rows (never gated)

At the observed pipeline pace (63 proposal intervals over 4.43 days, the
pipeline at 64): the decision-cell wall dates to **2026-07-27** (exact days
remaining 74867/6300 ≈ 11.88) — a date, not a risk class. The model
retrodicts the live file's post-roll-1 floor at 63,710 vs the measured
154,629 B (the seven resident fulls and ~9.5 KB of un-modeled
ASK/ACK/CLOSE-OUT blocks account for the gap — disclosed F1 boundary; those
families only SHRINK real headroom, REJECT-ward) and forecasts roll 2 at 11
full blocks at trigger (the live file held 7 at the drafting HEAD).

## Boundaries (pre-registered, ride the verdict)

- **Size constancy** — real block/stub sizes vary; Arm R is the named
  measured companion (wall distribution 213–245 around 233); saturation is
  mass-driven, the floor law is exact per realized sizes.
- **Roll timing** — real rolls are order-fired, not threshold-fired; the
  FLOOR LAW is timing-invariant (F2a), so the wall is timing-robust — only
  the thrash cadence is model-conditional.
- **Traffic** — the model prices proposals only; ASK/ACK/REPORT blocks
  shrink real headroom, REJECT-ward, direction stated never simulated.
- **Window** — the newest-W convention; non-contiguous pending sets change
  which blocks wait, not the retained mass; W = 8 prices the stall
  direction.

## Consequence (pre-registered REJECT branch, verbatim-faithful)

The folk rule "a threshold-triggered archive roll keeps the live file
bounded forever" retires with numbers. Paste-ready structured choice to
fleet-manager (owner of `docs/conventions/outbox-rollover.md`),
recommendation first per Q-0263.2: **(a, recommended — one convention line,
zero migration, removes the wall entirely)** ONE RANGE STUB per roll (span +
archive pointer keeps content-stable numbering; the archive holds every
block byte-faithful) AND each roll's receipt SUPERSEDES the previous — the
floor pins at ≈ 34 KB forever (COMPACT BOUNDEDNESS, exact); (b) keep
per-block stubs and accept the counter — schedule the stub file's own
second-order roll before ≈ 80% of N\* (the same law recurses one level up);
(c) raise the threshold — pure postponement (76 / 233 / 581 across the T
grid, ≈ linear). On EVERY branch the archive layer is vindicated: dated
archive files absorb unbounded bytes by design — the wall lives only in the
live file's tombstone grammar. APPLICATION GUARD: the verdict conditions on
(1) the committed convention shape at the pin (per-block stubs + per-roll
live-resident receipts + terminal-blocks-only — a changed stub or receipt
grammar means re-run, not reuse) and (2) stub/receipt mass being live-file
resident (an archive-side numbering index changes the model). Transferable
law, one line: **compaction that leaves per-item tombstones has capacity
(T − H)/s, and compaction whose receipts live on the compacted surface has a
second wall behind the first — boundedness requires the tombstone AND
receipt grammars to be O(1) per roll, not O(items).** Routing is the
manager's per Q-0260; this repo edits no other repo.

# VERDICT 068 — REPORT — the paper lane's BEAT coin (INTAKE 057)

**Class: REJECT** (pre-registered rules applied in order: REJECT → INVALID →
APPROVE → NULL; REJECT checked FIRST fires on all four conjuncts).

Source: idea-engine `## PROPOSAL 057 · 2026-07-14T03:30:10Z · status: sim-ready`
(idea-engine PR #391 @ main 665dca9; idea doc
`ideas/trading-strategy/paper-lane-beat-coin-2026-07-14.md`). Protocol under
price: trading-strategy `docs/paper-lane-protocol.md` §7/§9 A5/A6 +
`src/trading_lab/config.py:60–61` @ `d857e50ad7bc32bed5b2999cce16b4bf8a37246e`.

## Reproducibility

- `SELF-CHECKS: 68 passed, 0 failed`, exit 0, ~22 s/run, stdlib-only, hermetic
  (reads only its own `fixtures.json`), CPython 3.11 pinned and asserted.
- Byte-identical across two full process runs by external sha256:
  `run-stdout.txt` = `9cfe2b083af9f1da64e38729a72ac4981ef88e183f78d579f88a5897685372c7`,
  `results.json` = `910e562c572dfa0cb126c350c2313b53f1eaf8f1b27db559ae66a4f22acfccd7`.
- Seeds: 20261365 headline / 20261366 stability / 20261367 reporting — the ONLY
  three RNGs constructed (asserted, pinned order); aux 20261368 NEVER
  constructed (never-construct hygiene, asserted).
- No fix-forwards: the first complete run of the registered pipeline is the
  accepted run.

## Per-conjunct results (registered order)

**(a) Identity gate — FIRES.** BEAT ⟺ R_F < 1 with ZERO exceptions over the
full enumerated lattice (F ∈ {6,12,24} × k ∈ 0..F × T ∈ {4,8,16} × j ∈ 0..T =
1395 points) under the multiplicative equal-cost accounting. The fixed-notional
dollar variant also lands zero exceptions and ZERO sign flips; its second-order
cost asymmetry is at most $1.896572 per cycle in margin (exact rational in
results.json) and never touches the indicator. Zero exact ties (101 is prime,
101 ∤ 100^F — asserted symbolically and checked exhaustively; §9 A5 never fires
in-world). **The trade's own P&L cancels exactly out of the committed verdict:
a window grades BEAT precisely when the market FELL over its cycle's flat
segment.**

**(b) The null coin is not conservative — FIRES.**
B(NULL, COMMITTED) = 1985628207794352919031012090343552/3552713678800500929355621337890625
≈ 0.558905 ≥ 13/25 = 0.52. Controls: B(NULL, ZERO) = 20656327/33554432 ≈
0.615607 exactly (F3 closed form — fair-EV world, ~62% null coin: pure
volatility drag); B(NULL, DOUBLE) ≈ 0.501206 (below the 13/25 edge — the
conjunct genuinely discriminates on drift, exactly as the falsifiability leg
promised). Win-rate and EV point in opposite directions: at the committed
drift the zero-skill trader BEATs 55.9% of windows while losing an expected
$54.33 per cycle to B&H (EV row, exact; $109.40 at DOUBLE drift; exactly $0.00
at ZERO drift).

**(c) Count powerlessness at the committed rate — FIRES.** The exact one-sided
Neyman–Pearson count test at n = 8 (the first-year closed-window floor), size
≤ 1/20 non-randomized, NULL vs SKILL (δ = 1/25) at the committed drift needs
critical count 8-of-8 (achieved size 0.009521) and posts power 0.040650 < 1/2.
B(SKILL, COMMITTED) ≈ 0.670089. Horizon rows: n = 16 → power 0.173, n = 34 →
0.270; n*₅₀ = 56 windows = 5.00 calendar years at the committed 17-in-18-months
rate; n*₈₀ = 124 windows = 11.07 years. Strong skill (δ = 2/25) still posts
power 0.121 at n = 8 — the conjunct is not an artifact of a weak alternative.

**(d) Arm S confirms — FIRES.** Seed 20261365, N = 200,000 cycles per decision
world (CRN across δ worlds at each drift), 50,000 8-window seasons for the
power row; BEAT evaluated through exact lattice tables built from the protocol
arithmetic of BOTH accountings (fixture C3). Every decision cell passes both
gate halves (|EST − EXACT| ≤ 1/100 absolute AND ≤ 4·SE): worst deviation
0.001170 (power row). Draw-count sentinels exact; twin evaluators (threshold
rule vs full protocol arithmetic) agree at every lattice point and every MC
cycle (0 mismatches). Stability leg (seed 20261366, N = 20,000 + 5,000
seasons) passes all gates and reproduces REJECT through both evaluators.

## Controls (all green)

F1 pmf/mean identities (mean cycle 45/2, implied 16.8 windows/18mo ∈ [15,19]);
F2 no-tie primality theorem + k*(F) = F/2 at F ∈ {6,12,24}; F3 zero-drift
closed form exact; F4 monotonicity (B non-increasing in drift, increasing in δ
at every drift; power non-decreasing in n and δ); F5 hand world F = 2
(k*(2) = 1, P(BEAT) = 1 − p² per drift world); sentinels; twin evaluators;
seed hygiene. Reporting legs (seed 20261367, ungated): the s ∈ {1/200, 1/50}
worlds preserve the identity (0 exceptions, 0 ties) AND leave the coin exactly
unchanged — k*(F) = F/2 at every registered s, so B(NULL, ·) is s-INVARIANT
across the pair (0.615607/0.558905/0.501206 at ZERO/COMMITTED/DOUBLE
identically): volatility scale moves the magnitude of R_F but not the
median-threshold up-count rule, so no registered decision conjunct sits near
an s edge (a first-class exact reporting finding). F-mix pairs move the coin
with flat-segment length exactly as vol drag predicts: short-heavy
B(NULL, COMMITTED) ≈ 0.580933, long-heavy ≈ 0.537470 — both still ≥ 13/25,
conjunct (b) robust across the registered mixes. Anti-skill (δ = −1/25,
the donchian-shaped direction) B ≈ 0.443783; strong skill (δ = 2/25) power at
n = 8 is 0.121364 < 1/2. Every reporting MC confirmation lands within noise
of its exact value (max deviation 0.007345 at N = 20,000).

## Drafter comparison (never gated)

Every disclosed exact value reproduced from scratch: B(NULL, COMMITTED) exact
fraction matches digit-for-digit; B(NULL, ZERO) = 20656327/33554432; critical
count 8; n*₅₀ = 56; n*₈₀ = 124; class REJECT.

## Boundaries (registered, direction stated)

- **i.i.d. two-point market:** the identity theorem is distribution-free (needs
  only §7's equal-costs structure and shared in-window fills); the coin LEVEL
  is model-bound — fat tails move it AWAY from 1/2 at equal drift (REJECT
  direction); autocorrelation is the named most-likely-to-flip alternative for
  conjunct (b), bracketed qualitatively, never simulated.
- **Skill parameterization:** δ is the general channel BY the identity (every
  long/flat rule's skill reaches the verdict only through its flat-segment
  tilt); the donchian-shaped anti-skill −1/25 leg rides as reporting.
- **Truncation:** open-window and late-commit-MISS effects shrink effective n
  or deflate BEATs — the REJECT direction; ignored in the decision arm.
- **Scope:** this verdict prices the GRAMMAR, never the strategy (the holdout
  is SPENT and untouched); promotion is §8 owner-gated and untouched; no
  real-money implication exists anywhere in the lane by construction.

## Consequence (pre-registered REJECT menu, routing the manager's per Q-0260)

Paste-ready three-line note for the lane: (i) every weekly aggregate
`k BEAT of n` line gains the measured null-coin companion — a BEAT majority is
the null EXPECTATION at AAPL-like drift (0.559 coin), not evidence, and a BEAT
minority is likewise not damning; (ii) the §8 promotion firewall gains its
measured basis — counts could not promote even in principle before n*₅₀ = 56
windows ≈ 5 years (vindicated, not violated); (iii) the free upgrade, named:
the ledger already commits every signal-side close and fill, so an EV-grade
companion column (the cycle dollar difference A6's charge actually prices) can
ride the existing rows at zero new data — adopting it is a lane/owner intent
call, never ruled here.

**Application guard (two conditions):** (1) conditions on §7's grammar, §9
A5/A6, and the 6 bps/side · $10,000-notional accounting as committed @
`d857e50` — materially amended protocol text means re-run, not reuse;
(2) conditions on the lane's forward dataset being empty-to-single-digit
(ledger at `paper-0001` WATCH) — once real closed windows exist in force,
re-base the coin on realized cycle structure.

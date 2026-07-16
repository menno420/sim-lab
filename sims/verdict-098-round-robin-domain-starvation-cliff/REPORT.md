# VERDICT 098 — REJECT — the "fair rotation is harmless underloaded" claim that fails its own low-load gate (P085, round-robin-domain-starvation-cliff)

**Ruling: REJECT** (first failing gate **R1**). The multi-domain starvation
phenomenon is REAL — R2 and R4 both PASS, confirming that a fixed round-robin (RR)
rotation starves the highest-arrival (deepest) backlog: at overload ρ=1.10 the
most-starved domain under RR is `fleet`, the highest-λ domain (mean q_d fleet 1011.968
vs venture 141.988, game 2.924, unrelated 0.836), and at criticality ρ=1.00 RR's
max backlog (1561.20) is more than 3× LQF's (109.20). But P085's pre-registered ACCEPT
rule requires ALL of R1–R4, and R1's low-load-harmlessness leg FAILS: at the registered
low anchor ρ=0.70 filler(RR)=0.33314 > filler(LQF)+0.02 = 0.32021. R3 ALSO fails
(ρ=0.70 Var[total_backlog] RR 7991.62 ≫ LQF 1.50). Root cause: RR grants each domain a
fixed 1/4 = 0.25 service share; fleet's arrival rate ρ·0.40 exceeds 0.25 once ρ > 0.625,
so at ρ=0.70 fleet is ALREADY unstable under RR — that makes RR waste more fillers than
LQF (breaking R1-low) and gives RR's total backlog a linear-growth trend (breaking R3,
which had claimed "RR smoother when underloaded"). The true harmless-load region is
ρ < 0.625, below the tested 0.70. Two of four gates fail → REJECT at first failing gate
R1 — per the pre-registered rule ACCEPT iff R1 AND R2 AND R3 AND R4, fired in order
R1→R2→R3→R4; both independently-written decision evaluators (an if-chain scorer and a
table-driven scorer) agree REJECT/R1 on the measured gate outcomes.

6 self-checks, 6 passed, 0 failed; exit 0 on the accepted run; < 1 s/run; hermetic —
CPython 3.11.15, stdlib only, zero repo/network reads at verdict time. The schedulers
share one arrival stream per round (RR and LQF see identical inputs), and the seed-1
first-50-round total_backlog traces for both schedulers are committed as the fixture and
re-verified each run. stdout + results.json byte-identical across two full in-repo
process runs by external diff + sha256:

- `results.json` sha256 `8fa99865b24c518e6187b7e25e264ed2059501610009e7b4995b77033bbbaca6`
- `run-stdout.txt` sha256 `a424def174b1c2718aec9ff47b6b9eaa22d353a033079423067d2a50eb6d1bf5`

## The decision clauses (all measured)

- **R1 crossover — FAIL (the first failing gate).** Two-legged. The LOW leg fails: at
  ρ=0.70 filler(RR)=0.33314 > filler(LQF)+0.02 = 0.30021+0.02 = 0.32021 — RR wastes
  MORE service on fillers than LQF even at the "harmless" low load, the opposite of the
  registered ≤ claim. The HIGH leg passes: at ρ=1.10 filler(RR)=0.11697 ≥
  filler(LQF)+0.10 = 0.00000+0.10 = 0.10000. A two-legged gate fails if either leg
  fails; R1 fails on its low leg, and it is the FIRST gate in the R1→R2→R3→R4 order, so
  it is the first-failing gate the ruling names.
- **R2 backlog divergence @ criticality — PASS.** At ρ=1.00 max_backlog(RR)=1561.20 ≥
  3 × max_backlog(LQF) = 3 × 109.20 = 327.60. RR's backlog diverges from LQF's at the
  critical load exactly as the head predicted — the starvation is real.
- **R3 low-load harmlessness — FAIL.** At ρ=0.70 Var[total_backlog](RR)=7991.62 >
  Var[total_backlog](LQF)=1.50. RR's total backlog is NOT smoother when underloaded; it
  carries a linear-growth trend because fleet is already unstable under RR's 0.25 share
  at ρ=0.70. This is the SECOND failing gate; R1 is reported because it fires first.
- **R4 starvation locality — PASS.** At ρ=1.10 under RR the argmax over mean q_d
  (window [500,10000)) is `fleet` (1011.968), well above venture (141.988), game
  (2.924), unrelated (0.836) — the most-starved domain is the highest-λ domain, exactly
  the deepest backlog the head names.
- **ACCEPT does not fire and is excluded.** ACCEPT would require ALL of R1–R4; R1 and
  R3 both fail, so ACCEPT is excluded and the rule returns REJECT at the first failing
  gate R1.

## Twin evaluators and agreement

Two independently-written decision evaluators score the SAME measured gate outcomes:

- **Evaluator A (if-chain):** applies R1→R2→R3→R4 as a short-circuit if-chain, returning
  the ruling token and the first gate whose predicate is False → **REJECT / R1**.
- **Evaluator B (table-driven):** an independently transcribed table of (gate,
  predicate, outcome) rows, scanned in the registered order for the first False → **REJECT / R1**.

Both agree on BOTH the ruling token (REJECT) AND the first-failing-gate reason (R1),
checked by the self-checks `twin_evaluators_agree_verdict` and
`twin_evaluators_agree_reason`. The seed-1 first-50-round total_backlog traces for both
schedulers match the committed fixture (`fixture_trace_matches_committed`), the metric
window is exactly T−W rounds (`window_n_is_T_minus_W`), the shared-arrival stream is
present and non-null (`shared_arrivals_specified_not_null`), and the R4 argmax domain is
a real domain (`r4_domain_is_a_real_domain`) — 6/6.

## Margin ledger (typed, per-load means over seeds S=[1,2,3,4,5], window [500,10000))

| ρ    | fill_RR | fill_LQF | maxbk_RR | maxbk_LQF | var_RR    | var_LQF  |
|------|---------|----------|----------|-----------|-----------|----------|
| 0.70 | 0.33314 | 0.30021  | 334.40   | 9.60      | 7991.62   | 1.50     |
| 0.90 | 0.21461 | 0.10114  | 1140.80  | 24.20     | 95381.80  | 16.77    |
| 1.00 | 0.15579 | 0.00558  | 1561.20  | 109.20    | 177413.57 | 756.45   |
| 1.10 | 0.11697 | 0.00000  | 2185.20  | 1010.20   | 349297.29 | 74472.73 |

- **R1 low-leg margin (the failing margin):** filler(RR)−[filler(LQF)+0.02] = 0.33314 −
  0.32021 = **+0.01293 > 0** → FAIL (the gate required ≤ 0).
- **R1 high-leg margin:** filler(RR)−[filler(LQF)+0.10] = 0.11697 − 0.10000 = **+0.01697
  ≥ 0** → PASS.
- **R2 margin:** max_backlog(RR) − 3·max_backlog(LQF) = 1561.20 − 327.60 = **+1233.60 ≥
  0** → PASS.
- **R3 margin:** Var(RR) − Var(LQF) = 7991.62 − 1.50 = **+7990.12 > 0** → FAIL (the gate
  required ≤ 0).
- **R4:** argmax_d mean(q_d) under RR at ρ=1.10 = **fleet** (1011.968) → PASS.

The crossover algebra: RR's per-domain share is 1/N = 1/4 = 0.25; fleet's arrival rate
is ρ·Λ_fleet = ρ·0.40, which crosses 0.25 at ρ = 0.25/0.40 = **0.625**. At the
registered low anchor ρ=0.70 > 0.625, fleet is already over its RR share and its queue
grows without bound — the source of both the R1-low filler waste and the R3 variance
blow-up.

## Falsifiability gates (were real)

- **Shared arrivals (else NULL):** RR and LQF are compared on ONE arrival stream per
  round applied to both queue copies — asserted present and non-null. Without it the
  comparison would be a scheduler-vs-input confound, and the run would route NULL.
- **Fixture trace pin:** the seed-1 first-50-round total_backlog traces for both
  schedulers are committed and re-derived each run — one misread of the serve/arrival
  order moves the traces and trips the check.
- **Window length:** metrics are over exactly [W,T) = [500,10000) = T−W rounds, asserted.
- **R4 domain validity:** the most-starved argmax is asserted to be one of the four real
  domains — a transcription slip in the per-domain accounting would trip it.

Any self-check failure would have blocked exit 0. The ACCEPT world was reachable (had
all four gates passed) and did not come live — two gates fail.

## Scope boundaries (stated, per the registration)

- **Anchor boundary:** the low-load gates R1-low and R3 are registered at ρ=0.70, which
  sits ABOVE the true RR-stability crossover ρ≈0.625 for the fleet domain — so the
  "harmless low load" the gates test is not actually harmless for this Λ. The REJECT is
  faithful to the registration as written; it does NOT claim RR is harmful at every low
  load, only at the anchor P085 chose.
- **Scheduler-pair boundary:** the ruling binds the RR-vs-LQF comparison on the pinned Λ,
  ρ set, and horizon. A weighted/deficit round-robin with per-domain share ∝ λ_d is a
  DIFFERENT scheduler not tested here; the head names it as the repair, not a measured
  result.
- **Estimator boundary:** filler rate, max backlog, and total-backlog variance are means
  over the five seeds S=[1,2,3,4,5] on the [500,10000) window; the claim is the
  gate-by-gate PASS/FAIL on those means, not a distributional/CI statement over an
  ensemble of seeds.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a fleet-internal scheduling head. The deliverable is a citable measured verdict
plus a transferable correction, fanned in to the fleet manager (Q-0264). Per the
proposal's pre-registered REJECT consequence, paste-ready and recommendation-first
(Q-0263.2): **(1, recommended)** if a rotation must guarantee low-load harmlessness,
use a WEIGHTED/DEFICIT round-robin with per-domain service share ∝ λ_d — a plain
fixed-share RR starves any domain whose arrival rate exceeds its 1/N share, and fleet
(λ=0.40) crosses the 1/4 share at ρ=0.625, below the tested 0.70; **(2)** do not
register a "harmless low-load" anchor above a domain's RR-capacity crossover
max_d(λ_d)·ρ vs 1/N — P085's ρ=0.70 anchor is above ρ≈0.625, which is exactly why R1-low
and R3 fail; **(3)** the starvation-locality result itself STANDS (R2+R4 pass): under
overload a fixed RR rotation starves the DEEPEST (highest-arrival) backlog, so any
throttle/dispatch surface that rotates lanes on a fixed share should expect the
highest-traffic lane to starve first. Transferable audit: every fleet dispatch surface
that hands each lane/domain a FIXED rotation share (review-queue round-robins, per-repo
CI schedulers, any "fair" turn-taking dispatcher) — "does any lane's arrival rate exceed
its 1/N rotation share, and if so is the rotation weighted to that rate?"

## Seeds

**V098 consumes NO seed-ledger block.** The seeds are the in-file constants
S=[1,2,3,4,5] (`random.Random(seed)`), a fixed local realization set that drives the
shared arrival streams — NOT a draw from the fleet seed ledger. The next free ledger
block stays **20261730**, untouched (inherited unchanged from the V097 baton). The
schedulers share one arrival stream per round so the seeds drive identical inputs to RR
and LQF; no seed touches the decision rule, which is a deterministic gate-by-gate
comparison of the seed-averaged metrics.

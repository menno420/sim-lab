# VERDICT 082 — the WIP-cap dryness floor (idea-engine PROPOSAL 069) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT -> INVALID -> APPROVE -> NULL; both independently-written decision
evaluators agree REJECT/REJECT; every decision number is an exact
rational). The drafter's disclosed landing reproduces from scratch on
every value — **zero anomalies** (8 disclosed rows checked, all match).

The committed pair — ORDER 004's "WIP cap 3, backpressure holds" and
ORDER 003's "the PROPOSAL->VERDICT pipeline is never dry" — is jointly
unsatisfiable as a stationary guarantee. At the decision cell (K = 3,
r_hat = 4492/3973, the seat's own measured BURST cadence — its
dryness-minimizing regime), all four REJECT clauses clear:

- **Headline dryness**: D(3, r_hat) = **62712728317/304425042745 ~
  0.206004** >= 1/10 (2.06x over the line). The committed cap misses the
  committed floor a FIFTH of the clock in the seat's own best regime.
- **Grid robustness**: D(3, r) >= 1/20 at every registered grid r; worst
  cell D(3, 2) = 1/15 ~ 0.0667 (1.33x), best-for-the-folk-claim cell
  D(3, 1/2) = 8/15 ~ 0.533.
- **Cap-lift**: D(12, r_hat) =
  15467594593367231354493402010382429975895121/
  465777524392350112207277258435652957975602941 ~ **0.033208** >= 1/40
  (1.33x). A 4x WIP raise still misses "never" by every reading.
- **Backpressure price**: B(3, r_hat) = **90639863488/304425042745 ~
  0.297741** >= 1/5 (1.49x). "Backpressure holds" is the same coin's
  other face — the drafter is cap-blocked (harvest-diverted) ~30% of the
  clock. (This also prices the softer ORDER 003 "drafted-or-in-flight"
  reading of the floor, per the registered DRY-definition boundary.)

## The three structure theorems — verified exact, none stated in the orders

- **T1 — impossibility** (F2a, every grid cell): D(K, r) = pi(0) > 0
  strictly for every finite K and every r, with the exact lower bound
  D >= (1/(K+1)) * min(1, r^-K). A WIP cap and a never-dry floor on the
  same buffer always leave positive dry mass — the two lived DRY events
  (idea-engine inbox:188, inbox:219) are the cap's own arithmetic firing
  on schedule, not anomalies.
- **T2 — monotone frontier** (F2b): D strictly decreasing in K along
  every r-row and in r along every K-column; the K->infinity frontier is
  max(0, 1 - r) exactly — approach checked at (K = 40, r = 1/2):
  D - (1 - r) ~ 2.27e-13, inside (0, 1e-10), never crossing. On the
  r < 1 side NO cap raise reaches below 1 - r: drafting speed is the only
  lever there. "Never dry" is purchasable only in the joint limit
  K->infinity AND r > 1 — a LIMIT, not a rule.
- **T3 — balanced knee** (F2c): at r = 1 the law is uniform, D = B =
  1/(K+1) and TH = K/(K+1)*mu exactly at every grid K; the committed
  K = 3 at parity is dry a quarter, blocked a quarter, running at 3/4 of
  the bottleneck; the marginal cap lift buys Delta-D(3->4) = 1/20 exactly.

**Swap symmetry** (F5, every grid cell): pi_j(K, r) = pi_{K-j}(K, 1/r)
exactly, so D(K, r) = B(K, 1/r) — one seat's dryness is the mirror
seat's backpressure; grid-end orderings strict (D(K, 1/2) > D(K, 2),
B(K, 1/2) < B(K, 2) at every K).

## The variance attribution — the exhibit that relocates the blame

Under DETERMINISTIC service at the same means, D_det(K, r) =
max(0, 1 - K*r/(1 + r)): at the decision cell **D_det(3, r_hat) = 0
exactly**, and the threshold is K_det(r_hat) = 2 — a clockwork cadence
satisfies the committed pair perfectly from K = 2 up. The entire 20.6%
tax is dispersion-born, not cap-born. Arm R's three service shapes at the
same pinned means bracket this live (reporting-only, main leg, 100,000
cycles): exponential D-hat = 0.20753 (beside the exact 0.20600),
deterministic D-hat = 0.0 exactly (beside D_det = 0), and the measured
burst-gap empirical mix D-hat = 0.00023 — a named finding: WITHIN the
burst regime the seat's own four-gap dispersion is far closer to
clockwork than to memoryless, so the pinned memoryless decision model is
conservative toward the folk claim's failure being even cheaper to fix
in-regime; the REJECT-ward dispersion lives ACROSS regimes (burst mean
1986.5 s vs lifetime mean 5839 s), where the lifetime anchor lands
D(3, r_life) = 59887990527825907/95189705338888425 ~ **0.629** — and both
lived DRY events in fact occurred in that day-pause regime.

## The K*(r, d) safe-cap table (reporting — the consequence menu's table)

min K with D(K, r) <= d, for d = 1/10, 1/20, 1/100:

| r          | 1/10        | 1/20        | 1/100       |
|------------|-------------|-------------|-------------|
| 1/2        | unreachable | unreachable | unreachable |
| 3/4        | unreachable | unreachable | unreachable |
| 1          | 9           | 19          | 99          |
| r_hat      | 6           | 10          | 21          |
| r2         | 5           | 7           | 12          |
| 2          | 3           | 4           | 6           |

"unreachable" is the T2 theorem (frontier 1 - r >= d), not a search
timeout. At the committed cap the seat would need K = 6 just to reach the
1/10 band at burst cadence; the deep-cap corner D(12, 2) = 1/8191 ~
0.00012 (verified exact) and D_det = 0 are the live APPROVE-side
witnesses — falsifiability was real on every clause, and the headline
clause dies one grid step away at r = 2 (D = 1/15 < 1/10).

## Surfaces

Full exact D/B/TH/E/W over K in {1, 2, 3, 4, 6, 12} x r in {1/2, 3/4, 1,
4492/3973, 40428/30847, 2} in `results.json` (Fractions + float
renderings). Decision-row extract, D(3, r): 8/15 · 64/175 · 1/4 ·
62712728317/304425042745 · 29352074455423/184314341266075 · 1/15.

## Gates — all green

- **F1** (chain identities, every grid cell): pi*Q = 0 residual exactly
  zero against Arm B's own generator; sum(pi) = 1; per-level detailed
  balance lambda*pi(j) = mu*pi(j+1); flow conservation
  lambda*(1 - pi(K)) = mu*(1 - pi(0)); E = 1 - D iff r >= 1 and
  E = 1 - B iff r <= 1.
- **F2** (the three theorems): T1 positivity + exact lower bound; T2
  strict monotonicity both axes + the frontier window at (40, 1/2); T3
  uniform law, D = B = 1/(K+1), TH = K/(K+1)*mu, Delta-D(3->4, 1) = 1/20.
- **F3** (census anchors, exact): D(3, r_hat) = 62712728317/304425042745
  with its 3973^3/(...) construction identity; B(3, r_hat) =
  90639863488/304425042745; D(3, r2) = 29352074455423/184314341266075;
  D(3, 1) = 1/4; D(3, 1/2) = 8/15; D(3, 2) = 1/15; the exact D(12, r_hat)
  rational pin; D_det(3, r_hat) = 0 with K_det = 2; r_hat = 4492/3973,
  r2 = 40428/30847, r_life = 150482/391243 all re-derived inside the
  runner from the pinned gap integers (burst 1622+2674+2263+1387 = 7946,
  S_d = 3973/2; night 30847/18; lifetime 391243/67; S_v = 2246).
- **F4** (hand worlds): K = 1 -> D = 1/(1 + r) at every grid r; K = 2,
  r = 2 -> pi = (1/7, 2/7, 4/7); K = 3, r = 1 -> the uniform quarter.
- **F5** (swap symmetry + grid-end orderings): above.
- **F6** (battery): Arm B reproduces every Arm-A number EXACTLY (pi and
  all five metrics at every grid cell); twin decision evaluators agree
  REJECT/REJECT; Arm-R draw-count sentinels exact (exponential legs
  200,000/39,998 draws = draft-starts + verdict-starts; deterministic
  legs 0; empirical legs 99,999/20,000 = draft-starts); aux seed
  20261613 never read (constructor registry = [20261610, 20261611,
  20261612] exactly); byte-identical double run; CPython 3.11 asserted.

**606 self-checks, 0 failed, exit 0, ~0.6 s/run.**

## Reproducibility

One command, no flags, stdlib-only, hermetic (reads only its own
`fixtures.json`). stdout + `results.json` byte-identical across two full
in-repo process runs by external diff + sha256:

- `run-stdout.txt`
  `732a99d0293055a316aba986b9ff50b335611d2ff15552aef128d6ad30bec146`
- `results.json`
  `9e5203ba0d1e8b3e9bb433bbc826feb6606481cf9b1f5bdf6606b68aef649b08`

CPython 3.11 pinned and asserted (Arms A/B are platform-independent exact
rationals; Arm R floats are pinned to the CPython minor). Seeds
20261610 (main) / 20261611 (stability) / 20261612 (presentation, row
order only) are the ONLY RNGs constructed; aux 20261613 reserved, never
read. Registry high-water after this slice: 20261613 (reserved; highest
READ 20261612; this verdict session allocated NO seeds of its own — the
drafter's registered set IS the session seed set, the V077-V081
precedent; the 20261604-609 gap stays the drafter's disclosed in-flight
buffer, unused).

## Anomalies

**NONE.** The drafter's disclosed landing reproduced from scratch on
every checked row (D(3, r_hat) exact, B(3, r_hat) exact, D(12, r_hat) at
stated precision, D_det = 0 exact, D(3, r_life) at stated precision,
D(12, 2) = 1/8191 exact, both disclosed margins 2.06x/1.49x at stated
precision). The registered anchor-fragility NULL axis stayed disarmed:
r_hat and r2 agree on the headline clause (D(3, r2) ~ 0.159 >= 1/10).

## Boundaries (registered; the decision rides the pinned chain and says so)

1. **Memoryless service is the pinned decision model** — both directions
   priced: the deterministic exhibit (D_det = 0) brackets APPROVE-ward;
   the committed cross-regime dispersion (burst/night/lifetime means
   1986.5/1714/5839 s) argues REJECT-ward. Arm R adds the measured
   nuance: the WITHIN-burst empirical shape is near-clockwork
   (D-hat ~ 0.0002), so the 20.6% headline is a memoryless-model price,
   while the lifetime-regime price (~0.63) dwarfs it — the lived DRY
   events came from regime-switching, exactly where the stationary
   single-regime model is weakest.
2. **The anchor is one committed verdict pair** — S_v = 2246 s is the
   only append->finalization pair echoed on idea-engine's own bus; the
   grid brackets r across [1/2, 2]; a bulk verdict-latency harvest is the
   named follow-up.
3. **Single-class single-server stations** — the 4 rotating lanes ride
   one class; multi-class and verdict-side batching are named follow-ups
   (T1 is population-structure-free).
4. **Stationarity** — the long-run law, not the transient of a fresh
   pipe; both lived DRY events fell >= 3 days into continuous operation.

## Pre-registered consequence (routing is the manager's per Q-0260)

REJECT -> the paste-ready structured choice, recommendation first per
Q-0263.2: **(a, recommended)** keep cap 3, RESTATE the floor as a priced
SLA — replace "never dry" with "stationary dryness <= d at the measured
cadence" using the K*(r, d) table above, and reclassify dry events inside
the priced band as arithmetic (no escalation work), outside it as signal;
**(b)** buy dryness with VARIANCE, not WIP — steady the drafting cadence
toward clockwork at the same mean (the exact D_det law prices this as
fully curative at K >= 2, where T2 proves no affordable cap raise is; the
Arm-R burst-gap trace says the seat already runs near-clockwork INSIDE a
burst — the variance to kill is cross-regime); **(c)** raise the cap only
on the r > 1 side and only with the table in hand (0.206 -> 0.033 for a
4x raise; for r < 1 the frontier max(0, 1 - r) makes drafting speed the
only lever). Owner/lane intent call, never ruled here. Named follow-ups,
none in scope: multi-lane multi-class extension; verdict-side batching;
the bulk verdict-latency harvest; the transient dryness of a
freshly-filled pipe.

# VERDICT 047 — the 37% rule off its home objective: the exact cardinal price of look-then-leap's folk cutoff

> **Ruling:** `approve` — per the pre-registered rules applied IN ORDER:
> REJECT (checked FIRST) does not fire — ΔV(N) exceeds 1/50 at five of the
> six swept N (only N=5's 1/60 sits under the line); APPROVE fires — ΔV(N) ≥
> 1/20 AND B(N) ≥ 3/20 at every decision cell N ∈ {50, 100, 200}, all
> comparisons exact Fraction. The objective fork is first-order: the 37% rule
> is a rank-obsession tax at scale.
>
> Intake: **036** (idea-engine PROPOSAL 036, PR #313; claim PR #314) ·
> Fully hermetic + fully exact: zero RNG, zero seeds (fleet high-water
> 20261284 unchanged), zero floats in computation, zero repo/network reads ·
> 151 self-checks, 0 failed · stdout + results.json byte-identical across two
> full process runs by external diff · ~1.4 s, stdlib-only.

## The question (registered)

The secretary problem's popularized "37% rule" — observe the first ~37% of N
candidates, then take the first running record — is THE popular algorithm for
sequential choice, sold on a real theorem: for P(select the single best), the
~N/e cutoff is optimal (reproduced here as an ANCHOR, never a band). What the
popularization never prices is that almost no real chooser holds that
objective: a hirer's payoff is the QUALITY of who they get. This head
measures, in the rule's OWN frame and family (N known, no recall, i.i.d.
U[0,1] values in uniform random arrival order; cutoff rules CR(r), r ∈
{1..N−1}; MUST-CHOOSE decision-binding, WALK-AWAY reporting-only; the rank-k
candidate worth (N+1−k)/(N+1) exactly):

- **ΔV(N)** = E_must[V](r*_V) − E_must[V](r_folk) — the folk cutoff's exact
  cardinal regret against the best cutoff in its own family, r_folk(N) =
  clamp(⌊(37N+50)/100⌋, 1, N−1);
- **B(N)** = P(bottom-half hire | CR(r_folk), must-choose, forced-last leg
  included), bottom-half := overall rank ≥ ⌊N/2⌋+1;

over N ∈ {5, 10, 20, 50, 100, 200} — the full 379-cell (N, r) census × 2
objectives × 2 conventions, every number an exact rational.

**Decision rule (fixtures.json, committed BEFORE the runner; evaluated in
this order; bands disjoint by construction 1/50 < 1/20):** REJECT iff ΔV(N) ≤
1/50 at EVERY swept N (checked FIRST) → APPROVE iff ΔV(N) ≥ 1/20 AND B(N) ≥
3/20 at every N ∈ {50, 100, 200} → NULL (anything else, a legitimate
finalized outcome).

## Validity

Two structurally independent arms, equal by EXACT RATIONAL EQUALITY on every
(N, r, objective, convention) cell: **Arm A** (the analytic closed forms —
P_best(r,N) = (r/N)·Σ_{j=r}^{N−1} 1/j; E_must[V] = ½(1 + r/(r+1) − r/N);
E_walk[V] = ½ + r/(2(r+1)) − r/(2N) − r/(2(N+1))) and **Arm B** (independent
combinatorial rank census: the joint (selected position, selected overall
rank) distribution by direct finite counting — acceptance mass
[r/(j−1)]·(1/N)·C(N−k, j−1)/C(N−1, j−1) plus the take-at-N legs, no
integrals, no values; P_best off the rank-1 row, E[V] via
Σ_k P(rank k)·(N+1−k)/(N+1)). **Census gate** (algorithm-free third arm):
full permutation enumeration at N ∈ {5, 6, 7} (120/720/5040 orders), both
objectives, both conventions, the full selected-rank distribution at every r
— equal to BOTH arms exactly.

All gates green (any failure = run INVALID): the classic anchors
P_best(1,3) = 1/2, N=4: r*=1 @ 11/24, N=5: r*=2 @ 13/30; the convention
identity E_must − E_walk = r/(2(N+1)) on every cell, both sides independently
computed (and separately on Arm A's closed forms); the never-leap identities
P(take last | must) = r/(N−1) and P(end empty | walk) = r/N; rank-distribution
sums (1 must-choose, 1 − r/N walk-away); P(rank 1) identical across
conventions; E_must[V](N−1, N) = ½ per N; ⌊N/e⌋ floor agreement under both
endpoints of the rational bracket 271828182845/10¹¹ < e < 271828182846/10¹¹.
**151 self-checks, 0 failed, exit 0.** Byte-identical stdout + results.json
across two separate full process runs (external diff) — by construction: zero
RNG, zero floats (display decimals are exact decimal strings by integer long
division). No fix-forwards: the first accepted run is the registered
pipeline's first complete run (one pre-run correction while writing the
runner: the arm/census table loop initially built tables only for the grid
∪ {3,4} and crashed at the census Ns {6,7} before any output — a KeyError,
not a measurement change).

## The measured tables (must-choose; exact rationals in results.json)

| N | r_folk | r*_V (ties) | r*_R (ties) | ΔV exact | ΔV | B exact | B |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 2 | 1 | 2 | 1/60 | 0.0167 | 1/3 | 0.3333 |
| 10 | 4 | 2 | 3 | 1/30 | 0.0333 | 281/1260 | 0.2230 |
| 20 | 7 | {3, 4} | 7 | 3/80 | 0.0375 | 720919/3912480 | 0.1843 |
| 50 | 19 | 6 | 18 | 117/1400 | 0.0836 | 3720341542979195807/19189130057250753600 | 0.1939 |
| 100 | 37 | 9 | 37 | 49/475 | 0.1032 | (exact in results.json) | 0.1869 |
| 200 | 74 | 13 | 73 | 1037/8400 | 0.1235 | (exact in results.json) | 0.1859 |

E_must[V] at r*_V vs r_folk: 13/20 vs 19/30 (N=5) · 11/15 vs 7/10 (N=10) ·
4/5 vs 61/80 (N=20) · 152/175 vs 157/200 (N=50) · 181/200 vs 3047/3800
(N=100) · 2609/2800 vs 97/120 (N=200). The value-optimal cutoff tracks the
√N − 1 calculus prediction exactly: r*_V = 1, 2, {3,4}, 6, 9, 13 vs
⌊√N⌋ − 1 = 1, 2, 3, 6, 9, 13.

**Ruling application (exact comparisons, registered order):**

1. REJECT — ΔV ≤ 1/50 at EVERY N? 1/60 ≤ 1/50 (N=5) but 1/30 > 1/50 (N=10),
   3/80 > 1/50 (N=20), 117/1400 > 1/50 (N=50), 49/475 > 1/50 (N=100),
   1037/8400 > 1/50 (N=200) → **does not fire**.
2. APPROVE — at N ∈ {50, 100, 200}: ΔV = 117/1400, 49/475, 1037/8400, each ≥
   1/20; B ≈ 0.19387, 0.18686, 0.18592 (exact rationals in results.json),
   each ≥ 3/20 → **fires**.

**RULING: APPROVE.**

## Reporting-only legs (cannot flip the decision; did not)

- **The fork is in the OBJECTIVE, not the folk rule's arithmetic:** the folk
  cutoff's own-objective shortfall P_best(r*_R) − P_best(r_folk) is 0 EXACTLY
  at N ∈ {5, 20, 100} (r_folk = r*_R there, as the registration predicted)
  and ≤ 0.0005 elsewhere (11/25200 at N=10; ≈ 0.00032 at N=50; ≈ 7×10⁻⁶ at
  N=200). Meanwhile ΔR(N) = P_best(r*_R) − P_best(r*_V) — what a
  value-optimizer concedes on the classic objective — grows 0.0167 → 0.1894
  across the grid: the two objectives genuinely part ways.
- **The downside shape:** take-last @ r_folk = r/(N−1) ≈ 0.37–0.5 (1/2, 4/9,
  7/19, 19/49, 37/99, 74/199); selected-rank quartiles at r_folk are bimodal —
  at N=100: {1, 2, 34} (median hire = 2nd-best, 75th percentile rank 34, and
  an 18.7% bottom-half tail) vs r*_V's {2, 4, 9}: the early leap trades the
  jackpot for never being handed a lottery ticket on the last candidate.
- **Walk-away frontier** (convention flip visible, never decision-entangled):
  argmax_r E_walk = 1, 1, 2, 4, 6, 9 with E_walk* = 17/30, 36/55, 103/140,
  2093/2550, 61429/70700, 24257/26800; end-empty @ r_folk = r/N = 2/5 … 37/100.
- **⌊N/e⌋ variant:** r_e = 1, 3, 7, 18, 36, 73 (floor agreement gated under
  both bracket endpoints); ΔV_evar = 0, 1/120, 3/80, 249/3325, 729/7400,
  627/5180 — the variant does not rescue the cardinal regret at scale.
- **The classic story on its home objective is intact:** P_best(r_folk, N) −
  1/e ∈ (0.0654…, 0.0304…, 0.0163…, 0.0061…, 0.0032…, 0.0016…) via the
  rational bracket — converging on 1/e from above, exactly as the theorem says.

## Liveness disclosure vs measurement

The drafting closed forms predicted ΔV ≈ {0.017, 0.033, 0.0375, 0.084,
0.103, 0.123} — the measured exact values match all six (1/60, 1/30, 3/80,
117/1400, 49/475, 1037/8400). The genuinely open number B(N) was
MC-bracketed near 0.19 vs the 3/20 band at drafting; measured exactly:
0.19387 / 0.18686 / 0.18592 at the decision cells — inside the bracket, and
clearing the band with 3.6–4.4 pp of margin (not knife-edge). The registered
expected landing (APPROVE) is the landing.

## Model basis, lower bound, and limits (registered scope)

Every number is CONDITIONAL on the rule's own canonical frame: known N, no
recall, cutoff family CR(r), uniform values (the neutral cardinal choice) —
this head prices the folk rule against its OWN family. The optimal cardinal
policy is a threshold rule OUTSIDE the cutoff family, so **every regret
measured here is a LOWER bound on the cost against full optimality**. The
single most-likely-to-flip alternative is the VALUE DISTRIBUTION — heavy
tails (superstar markets) reward late leaping and shrink ΔV — named as the
follow-up head with both arms' machinery reusable; unknown/random N, recall,
interview costs, and non-cutoff policies are out of the registered scope by
design. The decision is pinned to must-choose; the walk-away frontier ships
reporting-only. Bands quantify only over the swept grid; the one judgment
call (are 1/20 and 3/20 the right materiality lines?) is pinned by
pre-registration — a reader may dispute the bands, never the measured numbers.

## What a reader does differently (pre-registered APPROVE consequence)

The 37% rule may no longer be cited as "the optimal strategy" for sequential
choice UNQUALIFIED — it is optimal only for the all-or-nothing best-pick
objective. Anyone whose payoff is the hire's QUALITY (nearly every popular
application: hiring, apartments, dating) should leap far earlier — the
measured r*_V(N) ≈ √N − 1 curve ships (1, 2, {3,4}, 6, 9, 13 over the grid).
Every future fleet citation of the rule carries the objective caveat plus the
downside table (forced-last rate r/(N−1) ≈ 37%, bottom-half rate ≈ 19%).

**Run:** `python3 sims/verdict-047-37-rule/secretary_37_sim.py` — stdlib-only,
hermetic, no flags. Raw outputs: `run-stdout.txt`, `results.json` (exact
fractions as "num/den" strings + display decimals, full 379-row frontier).

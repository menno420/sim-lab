# VERDICT 093 — REJECT — the 50/50 crowd that wins a third of the time (P080, cycle-following coupling lever)

**Ruling: REJECT** (the independence multiplication is wrong as doctrine
wherever trials share a randomness source: the joint is a DESIGN VARIABLE
the marginals do not constrain — a coupling exists that lifts the group
from 2⁻¹⁰⁰ to ≈ 0.3118 while provably moving no marginal; the lift is
floored above 1 − ln 2 forever; failures concentrate instead of thinning;
and of the two folk repairs, one is a conjugation no-op and the other a
full restoration, distinguishable only by composition algebra) — per the
pre-registered rule applied in the registered order REJECT → INVALID →
APPROVE → NULL (REJECT evaluated FIRST and fires on all four clauses
R1–R4; twin independently-written decision evaluators agree REJECT/REJECT
over an ENUMERATED boolean input set; every decision number a seedless
exact integer census or Fraction identity).

61 self-checks, 61 passed, 0 failed; exit 0 on the accepted run (the
first complete in-repo run of the committed pipeline — rehearsed to green
on untracked outputs before the runner commit: 60/61 on the first
rehearsal run with ONE rehearsal fix, a fixture-string comparison against
a parenthetical-bearing disclosed value — comparison plumbing only, no
decision value touched; 61/61 on the second rehearsal run; zero
fix-forwards after the runner landed); ≈ 2.6 s/run; hermetic — pure-math
head, stdlib only, no vendor tree, zero repo/network reads at verdict
time (kin: the P028/P032/P048/P060/P072/P076 exact-counting family).
CPython 3.11 pinned and asserted (Arms A/B are platform-independent exact
arithmetic; only reporting-only Arm R and the presentation shuffle touch
the pinned minor's `random` module). stdout + results.json byte-identical
across two full in-repo process runs by external diff + sha256:

- `results.json` sha256 `d6783470d69becd5e5b3ab7568b42c14bcd72494ce85ac88dbf9ff8167827c8f`
- `run-stdout.txt` sha256 `4ca48a520d6d982cd38ffed9cdd8a9e34eb67ca8a99317abc10bb9b89dd732bf`

**Anomaly census (structured by disclosure coverage, the V087–V092
convention): 54 compared-and-matched, 0 mismatched, 6 vacant.** Every
registered numeral in the P080 registration — decision AND reporting —
reproduced exactly from scratch: the joint censuses 10 / 276 / 14,736
(brute) and 1,285,920 (partition == 10!·893/2520), the below-n cells
632,736 = 560,160 + 72,576 (= 10!/50) and 5,916 = 4,656 + 1,260 (= 8!/32),
P₁..P₅ = 1/2, 5/12, 23/60, 307/840, 893/2520, the per-length law 180/144/
120 = 6!/k, the marginals 240/360/480 of 720 with the (m−1)!-per-length
law at m ∈ {4, 6, 8}, the headline P₅₀ = 0.3118278207 (exact 41/41-digit
fraction), the ratio 3.953 × 10²⁹ and the poles 2⁻¹⁰⁰ ≈ 7.889 × 10⁻³¹ /
same-set 0, the concentration value 50/T₅₀ ≈ 72.6562, the five budget
rows (0.4062346943 / 0.4924928953 / 0.7139781129 / 0.8951930852 / 99/100
exactly), the decrement identity for n = 1..199, the floor gap 0.0049750,
the repair censuses 276/720 on ALL THREE arrangements, the conjugation
censuses {720, 0, 720}, the adversarial 6-cycle zero, the factorial
counts 24 / 720 / 40,320, both Arm-R preview triples ((6,131, 13,869,
1,007,767) and (2,455, 5,545, 403,116)) with draw counts exactly
1,980,000 / 792,000 and the disclosed trace mean 72.6633, and the pencil
worlds (m = 2 lever 1/2 vs 1/4; the independent product 81/1296 = (1/2)⁴;
b = m → 1; b = m − 1 → 1 − 1/m). The six honest vacancies (sim-chosen
realizations of shape-registered slots, disclosed in fixtures.json,
ledgered as vacancy-derived disclosures — never match claims): the
decimal display convention (round-half-up on the exact Fraction at the
registered precision), the ln-2 bracket depth K = 60, the "forever" route
through the alternating-series identity, the m = 100 adversarial witness
realization (the rotation), the presentation-shuffle target, and the
m = 4 independent-sets enumeration frame.

## The decision clauses (all exact)

- **R1 — THE LEVER (fires).** Joint pointer success == 1 − Σ_{k=b+1}^{m}
  1/k exactly for b ≥ n: the C1 three-method counting triangle agrees at
  every enumerated size — brute censuses 10 / 276 / 14,736 at m ∈ {4, 6,
  8}, partition census == brute at (8, 4), partition census 1,285,920 ==
  10!·893/2520 at m = 10. Headline m = 100: P₅₀ = 0.3118278207 (exact
  41/41-digit fraction) vs the independent-random-sets pole of exactly
  2⁻¹⁰⁰ ≈ 7.889 × 10⁻³¹ — a lift of exactly P₅₀·2¹⁰⁰ ≈ 3.953 × 10²⁹ —
  and the same-set pole of exactly 0 (pigeonhole, enumerated).
- **R2 — MARGINAL INVARIANCE (fires).** The cycle length of a fixed
  element is uniform — exactly (m−1)! permutations per length at every
  enumerated m — so every player's own success at budget b is exactly
  b/m at every (m, b) enumerated (240/360/480 of 720 at m = 6). The
  entire 10²⁹ lift is pure dependence: 1/2 before, 1/2 after.
- **R3 — CONCENTRATION + FLOOR (fires).** E[# failing | joint failure] =
  50/T₅₀ ≈ 72.6562 of 100 (exact Fraction; the survivors are exactly the
  short-cycle members). P_n strictly decreasing with decrement exactly
  1/((2n+1)(2n+2)) for n = 1..199, and P_n > 1 − ln 2 certified: T₅₀ <
  S₆₀ < ln 2 < S₆₀ + 1/(61·2⁶⁰) (the rational bracket inside its own
  tail bound; width < 10⁻¹⁹), gap = ln 2 − T₅₀ = 0.0049750 at 7 places
  from both bracket ends.
- **R4 — THE REPAIRS (fires).** The adversarial 2n-cycle zeroes the
  deterministic pointer — on the pinned 6-cycle all 6 players fail at
  once (and the m = 100 rotation witness fails all 100). The folk
  "relabel the boxes" repair is a conjugation σ⁻¹πσ and preserves cycle
  type: censuses {720, 0, 720} over all 720 σ on identity / 6-cycle /
  3+3 — the 6-cycle stays lost forever. The one-sided remap (start at
  σ(i), read content c as σ(c) — effective permutation π∘σ) restores
  EXACTLY 276/720 == the uniform census against every pinned
  arrangement. The pair differs only in WHICH SIDE of the composition
  the shared randomness enters.
- **APPROVE (does not fire, and is arithmetically excluded):** the
  pointer census equals the 2⁻ᵐ product census at NO enumerated m
  (276/720 vs 720/2⁶/720 at m = 6) and no enumerated marginal moved off
  b/m — checked honestly; the pre-registered rule fired REJECT on the
  computed inputs.

## Twin arms and contacts

Arm A (seedless exact closed forms: the harmonic law, m!/k, b/m, the
correction terms, the identities, the bracket) and Arm B
(independently-written brute enumerations with their own cycle walker
and bookkeeping, plus the cycle-type partition census as the third
counting method) are tied through the four typed must-equal contacts:
**C1** the counting triangle (brute == m!·P_{m/2} at m ∈ {4, 6, 8};
partition == brute at (8, 4); partition == 10!·893/2520 at (10, 5)),
**C2** per-length == (m−1)! each, summing to m! (m ∈ {4, 6, 8}), **C3**
one-sided remap == 276 for ALL THREE arrangements and conjugation ==
{720, 0, 720}, **C4** true census == naive + 10!/50 at (10, 4) and
naive + 8!/32 at (8, 3) (the (8, 3) cell additionally brute-confirmed).
Arm R (seeds 20261714/20261715, REPORTING-ONLY, no statistical gate)
reproduced both registered preview triples exactly under the registered
draw-order grammar, with the 99N draw-count sentinel asserted
(1,980,000 / 792,000) and in-process double-run determinism verified
per seed; presentation seed 20261716 read by the presentation leg only;
aux seed 20261717 never read.

## Margin ledger (typed — the V086 convention)

- **Exact-equality cells BY REGISTRATION (the head's own subject):** the
  C1 triangle (10 / 276 / 14,736 / 1,285,920), the marginal cells
  (exactly b/m — saturated by the uniform-cycle-length law, no room to
  move), the conjugation row {720, 0, 720} (frozen by cycle-type
  invariance — 0 and 720 are the two poles, no interior), the repair row
  276 == the uniform census (equality BY THE COMPOSITION THEOREM, not
  clearance), the correction identities +10!/50 and +8!/32.
- **The one strict inequality:** the floor P₅₀ > 1 − ln 2, certified
  with an explicit rational margin — gap bracket [S₆₀ − T₅₀, S₆₀ +
  1/(61·2⁶⁰) − T₅₀], both ends 0.0049750 at 7 places, bracket width
  < 10⁻¹⁹.
- **Separation of the excluded APPROVE:** 276/720 = 0.3833… vs the
  product census 1/2⁶ = 0.015625 — a 24.5× separation at the smallest
  enumerated headline cell; nowhere near margin 0.
- No UNregistered decision comparison sits at margin 0; every clause
  input is an exact integer equality, an exact Fraction identity, or the
  one rationally-certified strict inequality.

## Falsifiability (was real)

One moved marginal would have killed R2 (the uniform-cycle-length law
was gated by direct count at every enumerated m, never cited); either
repair census landing elsewhere would have killed R4 (a reader who
believes any shared relabeling defeats the adversary is refuted by the
0/720 conjugation row; a reader who believes NO randomization can help
is refuted by the 276/720 one-sided row — both sides priced); the
harmonic shortcut is genuinely FALSE below b = n and a naive value
reproducing as the true census would have been a real drafter regression
— the census-contact NULL axis existed for exactly that (measured: the
true censuses exceed naive by exactly 10!/50 and 8!/32, the registered
corrections). The APPROVE witness world (genuinely independent
per-player randomness, where the product law is CORRECT) is real and is
the head's own pinned baseline, not a straw man.

## Scope boundaries (stated, per the registration)

- **The shared-source boundary:** with genuinely independent per-player
  randomness the product law is CORRECT — the verdict binds joint
  estimates over SHARED sources only, and says so.
- **The strategy-class boundary:** pointer OPTIMALITY among all
  strategies is neither claimed nor gated (a named follow-up); the head
  prices the lever's existence and exact value.
- **The small-m boundary:** enumerations feed m-uniform theorems (the C1
  triangle and the m!/k law verified at every enumerated m) applied at
  m = 100 as exact Fraction identities, never extrapolations.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

Fleet-external head — no lane consumer; the deliverable is the rotation
lane's SIXTEENTH-domain coverage row plus the transferable joint-risk
correction, which ships in three lines per the registration: (1) never
multiply marginals into a joint without naming the coupling — with one
shared randomness source the joint is DESIGNABLE from 0 to ≈ 1/3 while
every marginal stays pinned at 1/2, so a chain estimate 0.99ᵏ over legs
that share a seed, a branch state, a container image, or a wake schedule
is an assumption about dependence, not arithmetic; (2) failure
CONCENTRATION is a design lever, not an accident — under the pointer
coupling the group fails in one lump (≈ 72.66 of 100 together), which is
exactly what shared-fate batching, all-or-nothing retries, and
blast-radius design engineer on purpose: if you must fail, fail together
and pay recovery once; (3) repairs against adversarial structure must be
ALGEBRA-CHECKED, not vibed — the two folk-indistinguishable
randomizations differ only in composition side, one a theorem-level
no-op (conjugation preserves cycle type), the other a full restoration
(one-sided composition is uniform against any arrangement). Named
follow-ups, none in scope: pointer optimality, k-of-m objectives,
non-uniform priors, the anti-coupling (hedging) direction.

## Seeds

Arm-R reporting-only: 20261714 (N = 20,000), 20261715 (N = 8,000) under
the registered draw-order grammar (one Fisher–Yates permutation per
episode, exactly 99 `randrange` draws, i = 99..1, one `random.Random`
per seed; draw-count sentinels asserted); presentation shuffle 20261716
(presentation leg only); aux 20261717 reserved and never read. Seeds
20261710–713 are P079/V092's registered set — untouched; the allocation
started at 20261714 per the P079 card's baton. No seed touches any
decision arm.

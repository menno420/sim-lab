# VERDICT 087 — REJECT — the bundle over a floorless PWYW (P074, bundle-PWYW floor lattice)

**Ruling: REJECT** — per the pre-registered rule applied in the registered
order REJECT → INVALID → APPROVE → NULL (REJECT evaluated FIRST and fires
on all three clauses; twin independently-written evaluators agree
REJECT/REJECT; every decision number an exact integer or Fraction).

712 self-checks, 712 passed, 0 failed; exit 0 on the accepted run;
~0.6 s/run; stdlib-only; hermetic (reads only its own fixtures.json);
CPython 3.11 pinned and asserted. stdout + results.json byte-identical
across two full in-repo process runs by external diff + sha256:

- `results.json` sha256 `cb330b1160eddb77938186025084b1e61a9e929ab9adfa380b8eab22c87e092a`
- `run-stdout.txt` sha256 `58677f9d35c7159ab3e0ae722a8496197aebf4e6fa0398fbbc744882024eb0ff`

**Anomaly census: EMPTY.** Every disclosed numeral in the P074
registration — decision AND reporting — reproduced exactly from scratch:
the full seven-row f-grid census (coherence, σ_ach, π, gap, Δ), the f\*
table {59→10, 64→15, 68→19}, the mirror cell π(1) = 9, the strict-
discount law {11, 19}, the seller/buyer fork (+951/100, −10), the five
V040 external anchors (nets 41879/50589/54944/58428 per mille, the +4/5
second-fee row, the retention bar 50589/54944, the nudge cost
Δ(19) = −7039/1000), the pencil world, and the degeneracies. The
drafter's NO-DERIVED-LITERALS claim survived a zero-trust re-derivation
intact. The registration disclosed NO seeded Arm-R counts (exact
expectations only), so the seeded traces print beside the expectations
with nothing to compare — the census ran honestly and found nothing to
pin.

## The decision clauses (all exact)

**R1 — INCOHERENCE AT THE DEFAULT (fires).** At the decision cell
(a, s, p, f) = (49, 19, 59, 0):

- the coherence window [a, a + f] collapses to the single point
  **{49} ∌ 59** — the lane's own no-undercut guard, formalized, excludes
  the committed price (Arm B's candidate-price scan over every cent
  returns exactly one coherent price: $49);
- the SAME committed triple carries **σ_adv = +9** (reproducing the
  committed FAQ number exactly) and **σ_ach = −10** simultaneously —
  the advertised $9 discount is a $10 strategic surcharge over the
  achievable separate path (49 + 0 vs 59), ratio 10/9 over the copy's
  own number.

**R2 — THE ANCHOR-FAMILY LATTICE (fires).** f\*(p) = p − a with unit
slope maps V040's committed anchor family exactly:

- **59 (ratified) → f\* = 10** — strictly above half the suggested
  price, ratio **20/19** exactly;
- **64 (parked) → f\* = 15**;
- **68 (banned) → f\* = 19 = s EXACTLY** — the registered margin-0
  contact, gated as a two-sided must-equal: V040's banned anchor coheres
  only when the floor equals the suggested price, i.e. only when the
  PWYW knob is dead ink (an independent lattice re-derivation of V040's
  "never $68", which V040 reached via the $0-discount rationale).

**R3 — REPAIR THRESHOLDS (fires).** f = 10 restores weak coherence with
**σ_ach = 0 exactly**; a strict achievable discount of $d requires
**f ≥ 10 + d** (checked at d ∈ {1, 9} → {11, 19} by closed form AND by
Arm B's upward floor scan); the committed "$9" on the achievable basis
requires **f = 19 = s** — PWYW extinct. A live PWYW knob and the
committed copy are jointly satisfiable ONLY on a stated vs-suggested
basis.

APPROVE's witnesses were live and did not fire at the decision cell
(59 ∉ {49}, σ_ach = −10 < 0) — but the branch is genuinely live:
**every f ≥ 10 grid cell lands the APPROVE clauses** ([10, 15, 19]
verified), so a committed floor ≥ $10 anywhere in the packet flips the
ruling to coherent-as-shipped (re-run with the measured f, by table
lookup). No NULL axis triggered: the basis-reading fork stays a named
honest reading (on the vs-suggested basis the copy is TRUE — the gap
table s − f ships with this verdict either way), no granularity flip
(thresholds re-scanned at 1-cent and 99-cent quanta shift by less than
one quantum: {1000, 1500, 1900} → {1089, 1584, 1980} cents, integer-
dollar thresholds intact), no theorem failure, no twin disagreement.

## The full lattice surface (p = 59, exact)

| f | coherent | σ_ach | π | gap = s − f | Δ (seller) |
|---|---|---|---|---|---|
| 0 (decision) | no | **−10** | **10** | **19** | **+951/100 (+$9.51)** |
| 1 (mirror) | no | −9 | **9 = σ_adv** | 18 | 8639/1000 |
| 3 (sibling's floor) | no | −7 | **7** | 16 | 6897/1000 |
| 5 | no | −5 | 5 | 14 | 1031/200 |
| 10 (repair) | yes | **0** | 0 | 9 | 4/5 |
| 15 | yes | 5 | 0 | 4 | −711/200 |
| 19 = s | yes | **9 = σ_adv** | 0 | **0** | **−7039/1000 (V040's nudge cost)** |

Reporting sharpenings, verbatim from the registered landing and
re-derived: the sibling photo-packs' ONE committed floor ($3,
OWNER-QUEUE.md:84) would NOT save this lattice — a **$7 premium**
remains, so the repair needs a NEW committed value, not a copied one;
the only f-independent genuine saving anywhere in the system is
**β = $0.80** — the saved second fixed fee — and it accrues to the
SELLER ("saves $9 and one checkout" prices the checkout at $0.80, to
the other party); at f = 1 the strategic premium is exactly **$9** —
the copy's own number mirrored across the lattice.

## Margin ledger (C5, TYPED — the V086 💡 applied)

| row | type | value | status |
|---|---|---|---|
| σ_adv = copy number 9 | must-equal | 9 = 9 | green |
| σ_ach(0) = −(p − a) | must-equal | −10 = −10 | green |
| f\*(68) = s | must-equal | 19 = 19 (the registered margin-0 contact) | green |
| π(1) = σ_adv | must-equal | 9 = 9 (mirror) | green |
| σ_ach(10) = 0 | must-equal | 0 = 0 (repair threshold) | green |
| f(d = 9) = s | must-equal | 19 = 19 | green |
| Δ(19) = −7039/1000 | must-equal | external V040 anchor | green |
| f\*(59) − s/2 | must-clear | +1/2 (ratio **20/19**, the thin strict clause) | green |
| π(0) vs σ_adv | must-clear | ratio **10/9** (the other thin clause) | green |
| incoherence margins f ∈ {0,1,3,5} | must-clear | +10, +9, +7, +5 | green |
| coherence margins f ∈ {15,19} | must-clear | +5, +9 | green |

Gate: no UNregistered decision comparison sits at margin 0 — green.
Robustness note (reporting-only, never a decision code path): the R1
incoherence-at-default clause is arithmetically independent of the
f\*(68) = s margin-0 cell — the ruling's core finding (the committed
price is excluded at the floorless default) does not rest on the
registered knife-edge; the contact is the bonus re-derivation of V040's
ban.

## Gates

- **F1 — model identities + external anchors**: green. σ_adv = 9
  reproduces the committed copy number; the five V040 contacts
  reproduce EXACTLY in both arms (Fractions and integer milli-dollars):
  net(49) = 41879/1000, net(59) = 50589/1000, net(64) = 54944/1000,
  net(68) = 58428/1000, the +$0.80 both-separate-at-suggested row = 4/5,
  the retention bar net(59)/net(64) = 50589/54944 verbatim, and
  Δ(19) = −7039/1000; the w\* = f\* identity holds at p − a = 10.
- **F2 — the three structure theorems**: green at every cell. T1
  gap = s − f exactly across the full 7 × 3 grid AND all 105
  perturbed-(a, p) control worlds (a ∈ {3, 29, 49} × p ∈ {4, 39, 59,
  64, 68} × the full f grid, both arms) — the independence claim
  survived its designed kill. T2 window/threshold laws exact everywhere
  (window at f = 0 is {49} by candidate scan; windows [a, a + f]
  contiguous at every f). T3 the affine invariant Δ = α(p − a − f) + β
  verified at every (α, β) ∈ {871/1000, 1/2, 9/10} × {0, 4/5, 2} grid
  pair × every cell; simultaneous-strict seller-gain/buyer-loss at
  every f < 10; the β-residue f-independent at every f.
- **F3 — census anchors**: green, all verbatim — the seven-row table,
  f\* table, mirror cell, Δ(0) = 951/100, the strict-discount values
  {11, 19}, the sibling-$3 $7-premium cell.
- **F4 — the hand world**: green. (a, s, p) = (3, 2, 4), f = 0: w\* = 1,
  f\* = 1, gap = 2 = s, window = {3} (empty of discounts), π = 1 — all
  by pencil, matching both arms; Arm B's cent-scan lands w\* = 100
  cents exactly.
- **F5 — degeneracies and controls**: green. f = s → gap 0, coherent,
  σ_ach = σ_adv = 9 (the world the committed copy implicitly assumes);
  p = a = 49 → coherent at EVERY f with π = 0, and the only coherent
  price at f = 0 (the lane's guard sentence as arithmetic); p = a + s =
  68 → f\* = s (the banned-anchor contact); granularity non-flipping at
  1-cent and 99-cent quanta; APPROVE/R1 mutual exclusivity verified on
  every grid cell (C12).
- **F6 — battery**: green. Arm B reproduces every Arm-A number exactly
  (coherence flags, σ_ach, π, gap in cents; Δ in milli-dollars; f\* and
  w\* by scan; σ_adv by direct subtraction) — 105 twin rows + scans;
  twin decision evaluators agree REJECT/REJECT on their own arms'
  numbers; Arm-R draw-count sentinels (50,000 and 20,000 uniforms
  counted and asserted); presentation seed 20261662 read by the
  presentation leg only; aux seed 20261663 never read (constructor
  registry `[20261660, 20261661, 20261662]`); byte-identical double
  run.

## Arm R (reporting-only, no statistical gate)

| trace | pmf | seed | episodes | bundle-take | exact | mean outlay | exact |
|---|---|---|---|---|---|---|---|
| main | FLOOR-HEAVY {0: 3/5, 10: 1/5, 19: 1/5} | 20261660 | 50,000 | 20,002 (10001/25000) | 2/5 | 132501/2500 ≈ 53.0004 | 53 |
| stability | SUGGESTED-ANCHORED {19: 3/5, 10: 1/5, 0: 1/5} | 20261661 | 20,000 | 16,111 (16111/20000) | 4/5 | 114111/2000 ≈ 57.0555 | 57 |

Both seeded traces sit beside their exact expectations (no gate rides
them; the registration disclosed no seeded counts). The two pmfs
bracket the floor-heavy and suggested-anchored worlds — the lattice
prices PATHS and the copy's checkable truth, never buyer psychology.

## Falsifiability (was real)

- **Every f ≥ 10 cell**: the APPROVE clauses verifiably fire at
  f ∈ {10, 15, 19} — if the packet HAD committed a floor ≥ $10 (or the
  ⚑D click ships one), the ruling flips to coherent-as-shipped with the
  measured f deciding by table lookup.
- **The basis-reading fork**: on the vs-suggested reading the committed
  "saves $9" is TRUE as stated — the pre-registered NULL axis; this
  verdict ships the exact gap table s − f either way, so the repair is
  one clarifying phrase, not a scolding.
- **T1 perturbation worlds**: the independence claim would die on any
  world where the gap moves with a or p — 105 control cells checked in
  both arms, zero movement.

## Model boundary (declared, the P024 discipline)

The decision layer is model-FREE window/path arithmetic on committed
constants (what a buyer CAN pay, what the copy claims, what the lane's
own guard demands) — no demand model, no conversion, no market size
(V040's G1 territory, untouched: anchor-per-retention there,
lattice-per-both-buyer here). The only model content: (i) the affine
fee reading — V040's own committed reading, reproduced to five external
anchors, and T3 is proved across an (α, β) family, so fee imprecision
moves nothing (decision clauses never ride the fee layer); (ii) the
Arm-R pmfs — invented-but-pinned, REPORTING-ONLY. Boundaries stated:
strategic-buyer (real PWYW buyers overpay floors routinely — the REJECT
clause rides the committed COPY's checkable truth and the lane's own
coherence guard, never a behavioral prediction), platform quanta
(sub-dollar minimum-price quanta pre-checked non-flipping; named
follow-up), copy-reading (the vs-suggested reading is honest and is the
NULL axis, not a defeated strawman). The named live measurement is
free: any measured floor or PWYW payment distribution re-runs the
committed lattice functions at zero marginal cost.

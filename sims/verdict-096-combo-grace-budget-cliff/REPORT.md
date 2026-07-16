# VERDICT 096 — REJECT — the grace window that hides one shared budget (P083, combo-grace-budget-cliff)

**Ruling: REJECT** (the forgiving-streak grace contract — "any action within
the grace window is safe: miss the ideal beat by up to G and your streak
survives; you only ever lose the multiplier on a REAL miss, an action later
than G" — is wrong as doctrine the moment the grace is funded by ONE shared
budget rather than re-judged per action. On the pinned budget automaton
(P=10, G=3, B0=Bmax=10, R=1, M=25; break BEFORE the update at `B−ℓ<0` OR
`ℓ>G`, else `B ← min(Bmax, B−ℓ+R·[ℓ≤0])`), every steady within-grace lateness
breaks the streak at a finite, history-determined step `break_step = ⌊B0/ℓ⌋+1`
— ℓ=1→11, ℓ=2→6, ℓ=3→4 — and the break is SILENT under the strict
miss-contract because no single action ever exceeded G. The forgiveness
inversion is the sharpest cut: the silently wiped multiplier `= break_step−1 =
⌊B0/ℓ⌋ = {10,5,3}` is strictly DECREASING in ℓ, so the player who leans
LIGHTEST on grace each action (ℓ=1) rides the longest streak and loses the
MOST — 10 of M=25, more than 3× the ℓ=3 player. The contract is TRUE on its
own two cells (ℓ=0 replenishes to the cap and survives forever; ℓ>G is an
immediate real miss at step 1) and INVERTED on the shared budget it never
names) — per the pre-registered rule applied in the registered order REJECT →
INVALID → APPROVE → NULL (REJECT evaluated FIRST and fires on all four clauses
R1–R4; twin independently-written decision evaluators agree REJECT/REJECT over
an ENUMERATED 64-row boolean input set; every decision number a seedless exact
integer census over the registered finite grid, JOINT pass probability 1 for a
correct implementation).

35 self-checks, 35 passed, 0 failed; exit 0 on the accepted run (the first
complete in-repo run of the committed pipeline reproduced the drafter's
disclosed 35/35 exactly — no rehearsal fixes, no fix-forwards); < 1 s/run;
hermetic — deterministic-automaton exact-census head, stdlib only, zero
repo/network reads at verdict time (the model pins the budget automaton from
the idea file's integer constants and re-derives every census cell from
scratch with an independently-shaped twin; the model-semantics NULL axis
priced the `< 0` boundary and the break-before-update order exactly, and did
not fire). CPython 3.11 pinned and asserted (the decision arms are seedless
integer arithmetic, platform-independent; only reporting-only Arm R and the
presentation shuffle touch the pinned minor's `random` module). stdout +
results.json byte-identical across two full in-repo process runs by external
diff + sha256:

- `results.json` sha256 `413f4d55b71f5e9f9a71e3090db42268a44201bb22e9bc81cc5a979526c5cf03`
- `run-stdout.txt` sha256 `a0c9ed623167a603078b9d822a3be78c40ca0885d8fd1547daae4fc475cbbfc1`

**Anomaly census: every registered numeral in the P083 registration —
decision AND reporting — reproduced exactly from scratch, 0 mismatched.** The
steady break-step map {ℓ=0:∞, ℓ=1:11, ℓ=2:6, ℓ=3:4, ℓ=4:1(miss)}, the
multiplier-loss map {10,5,3} (= break_step−1 = ⌊B0/ℓ⌋, strictly decreasing),
the repair-(a) warning map {ℓ=1:10, ℓ=2:5, ℓ=3:3} with the ℓ=0 zero, the
repair-(b) break map {ℓ=1:∞, ℓ=2:10, ℓ=3:5}, both closed-form contacts C1/C2,
and Arm R — both preview censuses (SURVIVE 4,595 · SILENT-BREAK 11,427 ·
REAL-MISS 3,978 @ 20261726; 1,844 / 4,534 / 1,622 @ 20261727), both registered
class-stream digests (`3bfa073726f7`, `6f857d0afcf4`), and both draw sentinels
(60,000 / 24,000). The honest vacancies (sim-chosen realizations of
shape-registered slots, disclosed in fixtures.json before the runner, never
match claims): the decision-arm horizon (1000 actions, safely beyond every
finite break step), the class-stream digest procedure (see the note below),
the salt-logging realization (sum + first 5 per seed), and the
presentation-shuffle target (the stdout census-table display order).

> **Digest-procedure disclosure (vacancy-derived, load-bearing).** The
> registered class-stream digest is a function of the concatenated FIRST
> CHARACTER of each trace's class label — SURVIVE and SILENT-BREAK both begin
> with `S`, REAL-MISS with `R` — so the digest is a survive-vs-real-miss
> position stream and does NOT by itself separate SURVIVE from SILENT-BREAK.
> That split is asserted SEPARATELY and exactly by the per-seed census counts
> (SURVIVE 4,595 vs SILENT-BREAK 11,427 @ 20261726), which reproduced on the
> nose. Digest and census are therefore two independent witnesses of the same
> Arm-R stream: the census fixes the three-way class split, the digest fixes
> the per-trace ordering of real misses. Both reproduced.

## The decision clauses (all exact)

- **R1 — THE FOLK BELIEF MADE PRECISE (fires; checked, not assumed).** The
  steady census over ℓ ∈ {0,1,2,3} lands `{ℓ=0 survives; ℓ=1,2,3 break at
  11, 6, 4}` — NOT "all within-grace survive" — with the ℓ > G control (ℓ=4)
  breaking at step 1, the true real miss the contract does describe. The two
  cells where the contract is TRUE (the ℓ=0 survivor, the ℓ>G real miss) are
  registered as prominently as the silent breaks (F5), so the head cannot be
  read as a straw man.
- **R2 — THE CLIFF POSITION (fires).** The steady sim `break_step` equals the
  closed form `⌊B0/ℓ⌋ + 1` exactly across the pinned grid ℓ ∈ {1,2,3}:
  `[11, 6, 4] == [11, 6, 4]` (contact C1). An independently-shaped twin
  (Arm B, a full-trajectory budget walk with no early return) agrees on every
  steady pattern.
- **R3 — THE FORGIVENESS INVERSION (fires).** The silently wiped multiplier
  `= break_step − 1 = ⌊B0/ℓ⌋ = {10, 5, 3}` is strictly DECREASING in ℓ
  (10 > 5 > 3), max at ℓ = 1 (10 of M = 25, and the cap never binds since all
  losses < 25). Per action, being ℓ = 3 late "feels" three times riskier than
  ℓ = 1; at the STREAK level it is the exact opposite — the lightest habitual
  lateness is the most expensive habit, and nothing in the per-action grace
  test tells the player so.
- **R4 — THE PRICED REPAIRS (fires).** Repair (a), a one-shot grace-low
  warning firing when the NEXT action would break (`B_after − ℓ < 0`), fires
  exactly ONCE per streak at `break_step − 1` (ℓ=1→10, ℓ=2→5, ℓ=3→3) and
  ZERO times on the ℓ=0 survivor cohort — the legibility the silent break
  lacks, zero false positives. Repair (b), replenish-on-within-grace at
  R'=1, makes ℓ=1 survive (net change −1+1 = 0 — the folk belief made true
  for the lightest habit) and moves ℓ=2 → step 10, ℓ=3 → step 5, each equal
  to its closed form `⌊(B0−ℓ)/(ℓ−1)⌋ + 2` (contact C2) — a strict extension
  over the baseline that closes the ℓ=1 gap entirely but only DEFERS the rest.
- **APPROVE (does not fire, and is arithmetically excluded):** APPROVE
  requires every steady within-grace pattern ℓ ∈ {1,2,3} to survive to the
  horizon; the ℓ=1 cell breaks at step 11 (B0=10 is exhausted after 10 unit
  spends — F4a, pencil). Mutually exclusive with REJECT, as registered.

## Twin arms and contacts

Arm A (the pinned stepwise automaton — break-before-update, replenish-only-
on-clean, checked-first miss; DECISION-bearing, seedless) and Arm B (an
INDEPENDENTLY-shaped twin: a full-trajectory budget WALK over an explicit
per-step trajectory with no early-return closed form) are tied through the
typed must-equal contacts: **C1** steady sim `break_step == ⌊B0/ℓ⌋ + 1` for
ℓ ∈ {1,2,3}; **C2** repair-(b) sim `break_step == ⌊(B0−ℓ)/(ℓ−1)⌋ + 2` for
ℓ ∈ {2,3} with ℓ=1 surviving; the twin-machine contact (Arm B == Arm A on all
five steady patterns and on every Arm-R trace of both seeds); and the
twin-evaluator contact (two independently-written decision evaluators — an
if-chain and a table-driven scorer — agree on the ruling token over the
ENUMERATED 64-row boolean input set, REJECT/REJECT on the measured inputs).
Presentation seed 20261728 read by the presentation leg only (the census-table
display order), after every decision leg finished; aux seed 20261729 never
read.

## Margin ledger (typed)

- **Exact-equality cells BY REGISTRATION (the head's own subject):** the
  break-step map {11, 6, 4, 1}, the loss map {10, 5, 3}, the repair-(a)
  warning map {10, 5, 3} with the ℓ=0 zero, the repair-(b) map {∞, 10, 5},
  both closed forms C1/C2, both Arm-R censuses, both class-stream digests, and
  both 3N draw sentinels. All integer censuses or exact string equality — no
  tolerance anywhere.
- **The one strict inequality:** the forgiveness inversion (loss strictly
  decreasing in ℓ) carries margin ≥ 2 at every adjacent pair (10 → 5 → 3).
- **The margin-0 boundary, registered AS margin-0:** the budget test
  `B − ℓ < 0` (strict `<`, not `≤`) — reading it as `≤` would move every break
  step by one; the model-semantics NULL priced exactly that, and the sim
  re-derived the `<` boundary from the pinned clause. No unregistered decision
  comparison sits at margin 0.

## Falsifiability (was real)

The model-semantics axis was live: the transition is PINNED, not executed
against a shipped system, and one misread of the break-before-update order or
the `< 0` boundary moves every break step together. The sim re-derived all of
them from the pinned semantics with an independently-shaped twin (Arm B exists
because a stepwise automaton is exactly where an update-order or boundary
misread hides), and every census landed on the registered values, including
both Arm-R class-stream digests. The APPROVE world was one boundary misread
away (had the ℓ=1 cell survived, APPROVE's condition would have come live); it
did not — ℓ=1 breaks at 11. A single moved census would have killed its clause
and the registered rule would have issued INVALID or the honest NULL; none
moved.

## Scope boundaries (stated, per the registration)

- **The model-semantics boundary:** the ruling binds the pinned automaton as
  registered (the transition, the `< 0` boundary, the break-before-update
  order, the replenish-only-on-clean rule), not a shipped combo system.
- **The design-transfer boundary:** the lane ships NO combo/streak multiplier
  at the grounding HEAD (superbot-games @ 5db902a3 — `grep` returns only
  weight/yield/mine multipliers, never a streak system). The head transfers
  the STRUCTURE of the shipped shared-budget pace surface
  `games/mining/core/energy.py` (`MAX_ENERGY`/`REGEN_SECONDS`/`RESTORE_VALUES`,
  settle-on-read from a `(value, timestamp)` pair) onto a proposed multiplier
  surface, and the design-transfer NULL axis prices an unsound transfer — it
  did not fire (the transfer is a faithful model of a per-action-faced shared
  budget). The production color (the "shared budget instead of a per-dig
  cooldown" 2026-06-22 balance choice) is cited as color, never a fixture.
- **The witness-space boundary:** the steady-lateness family is the folk
  belief's OWN case ("I'm always a little late") — a witness family, not a
  measure over all input sequences. The decision claim is existential and
  exact on the registered grid; prevalence rides only the reporting-only
  Arm R and is stated as such (SILENT-BREAK ≈ 57% of random within-window
  players @ 20261726).

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

Verdict consumer: superbot-games — the lane owns the pacing/throttle economy
this head models (the shipped shared-budget precedent
`games/mining/core/energy.py`) and would own the combo/streak multiplier this
head prices as a DESIGN surface. Per the proposal's pre-registered REJECT
consequence, paste-ready structured choice, recommendation first (Q-0263.2):
**(a, recommended)** design the combo multiplier with the budget MADE LEGIBLE
— carry the grace budget as an explicit settled `(value, timestamp)`-style
surface (the energy.py pattern the lane already ships and unit-tests) AND fire
the grace-low warning of repair (a): zero new steady-state cost, one-shot per
streak at break_step−1, zero false positives on the clean cohort, closing the
exact silent-break gap the strict miss-contract leaves — the player sees the
cliff coming instead of watching a 10× multiplier vanish on a "safe" action.
**(b)** replenish-on-within-grace (repair b, R'=1) — makes the lightest habit
(ℓ=1) truly survive-forever as the tooltip promises, at the price of one
changed constant and a still-silent (merely deferred) break for ℓ ≥ 2; pairs
with (a) rather than replacing it. **(c)** status quo + document — ship the
shared-budget combo but AMEND the tooltip/balance doc to state the budget
explicitly ("your grace is a shared reserve that refills only on an on-time
action"), so the folk belief is never sold. Known co-consumers: the mining
energy surface (`energy.py` — the same shared-budget-behind-a-per-action-face
pattern, already legible via settle-on-read; the transfer runs BOTH ways), the
two in-repo pacing heads (explore action-pacing → P031, mining booster
throttle → P035 — each prices a DIFFERENT dial on the same throttle economy),
and — the transferable audit — every fleet mechanic that presents a SHARED
budget behind a PER-ACTION test (rate limits, cooldown pools, retry budgets):
a per-action "am I under the limit?" check is silent on cumulative-budget
depletion, and the fix is to surface the budget, not to re-judge the action.

## Seeds

Arm-R reporting-only: 20261726 (N = 20,000, digest `3bfa073726f7`) and
20261727 (N = 8,000, digest `6f857d0afcf4`) under the registered draw-order
grammar (per trace exactly 3 `randint` draws in order lateness ℓ ∈ [0,4],
horizon cap ∈ [5,50], salt ∈ [1,1000] drawn-and-logged; one `random.Random`
per seed; draw-count sentinels asserted at exactly 3N: 60,000 / 24,000);
presentation shuffle 20261728 (presentation leg only); aux 20261729 reserved
and never read. Seeds 20261722–725 are P082/V095's registered set — untouched;
the allocation started at 20261726 per the V095 heartbeat baton, and the next
free block starts at **20261730**. No seed touches any decision arm.

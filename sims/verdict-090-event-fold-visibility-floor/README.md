# verdict-090 — the event-fold visibility floor (INTAKE 077)

Prices idea-engine PROPOSAL 077 exactly where it lives: superbot-idle's
`docs/design/timed-events-scoping.md` @ `884aeae` (status `plan`, nothing
built) commits BOTH the piecewise-exact seventh-factor event fold
`rate = base_rate * count * upgrade_pct * prestige_pct * milestone_pct *
theme_pct * event_pct // 10_000_000_000` with its graduation identity
AND the § 1a promise that the world runs "visibly richer during the
window, for idlers and actives alike, in the exact T6 proportion" — on a
committed catalog where all 18 packs ship tier-1 `base_rate: 1`. Exact
integer arithmetic makes the pair **jointly unsatisfiable**. Five exact
structure theorems carry the verdict, every one re-derived from scratch
here: **T1 — the DEAD BAND**: the canonical start cell (pre-floor
product exactly 10^8, rate exactly 1/s) pays ZERO extra for EVERY
integer event pct 101..199 (**99/99 dead**); the first paying multiplier
is exactly **×2.00** (E = 200, a registered margin-0 contact, rate
1 → 2); one upgrade is still dead at ×1.5 (1.25·1.5 = 1.875 → 1) and the
first paying neighbour needs upgrade + two milestones (1.375·1.5 =
2.0625 → 2). **T2 — the CENSUS**: over the committed 214,500-cell
lattice (214,496 alive; the 4 zero-rate theme-90 artifacts enumerated by
name), alive-but-event-dead cells number **4,151 / 675 / 56 / 14 / 0**
across ×1.10/×1.25/×1.50/×1.75/×2.00 (the ×2.00 zero certified:
floor(2r) ≥ 2·floor(r) > floor(r) for r ≥ 1), and **zero** dead cells
have rate ≥ 20. **T3 — the QUANTIZATION JACKPOT**: realized/nominal
maxes at exactly **20/11** at ×1.10 (witness (1,1,0,2,8,110): a +10%
window delivered as +100%) and mins at 10/11 (the dead start cell); the
staircase envelope `floor(R·E/100) ≤ RE ≤ ceil((R+1)·E/100) − 1` holds
on every alive cell with BOTH edges attained at every grid E — a +10%
event at rate 1 is NEVER +10%. **T4 — the REPAIR FORK**, each arm priced
and each breaking a different committed sentence: (a) V038's min-delta
floor overshoots by the SAME 20/11; (b) the milli-ledger (G = 1000)
zeroes the census (certificate ≥ 99; canonical minimum exactly 100) at
the price of the doc's own § 3 "state_version stays 2" promise; (c) a
rate-floor R\* = 20 caps deviation at exactly **1/22** but concedes the
start state. **T5 — the TRUE SENTENCE confirmed**: piecewise closed-form
credit == the 1-second tick loop, byte-equal, on the pencil calendars —
the doc's exactness sentence survives; only its proportionality sentence
dies. All decision arithmetic is seedless exact integers/Fractions
(REJECT checked first). The runner is hermetic — it reads ONLY
`fixtures.json` (committed before the runner); every COMMITTED external
constant was re-verified firsthand at superbot-idle `884aeae` BEFORE the
fixture was written.

## Run

```
python3 sims/verdict-090-event-fold-visibility-floor/event_fold_visibility_floor_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~15 s (the Arm-B
Fraction walk is the heaviest leg). Every decision number is an exact
integer or Fraction; the seeded Arm R carries no statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 077 block / idea file (the committed fold + graduation
  identity, the 25/10/5 percents, the {1×18, 5×17} base-rate multiset,
  the lattice + caps, the E grid + T1's all-E sweep, the three repair
  arms, the F3 census anchors, the pencil worlds, the four typed
  must-equal contacts, the REGISTERED Arm-R draw-order grammar with
  seeds 20261690–693 and the disclosed previews, the decision rule, the
  typed margin-ledger cells). Sim-chosen values disclosed as vacancies:
  the four pencil-calendar cells (registered by count only) and the
  alt-fold named control's value.
- `event_fold_visibility_floor_sim.py` — the three-arm runner
  (A seedless pure-integer lattice census / B independently-written
  Fraction classifier + closed-form envelope twin / R seeded
  reporting-only window traces under the registered grammar).
- `results.json` — canonical machine-readable outputs (sorted keys, no
  timestamps): the full census rows, the envelope with per-E edge-hit
  counts, the ratio extremes per E, the repair-arm prices, the pencil
  worlds, the controls (theme-100 sub-lattice, cap-bump, alt-fold), the
  typed contacts, the margin ledger, the structured anomaly census, the
  seed registry.
- `run-stdout.txt` — the accepted run's stdout.
- `REPORT.md` — the ruling against the pre-registered bands, the
  numbers, the margin ledger, falsifiability, and the consequence
  hand-off.

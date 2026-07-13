# REPORT — idle economy FEEL sim: superbot-idle SIM-001's three ASKs, measured (ORDER 005 SIM-REQUEST 2)

> **Status:** `finalized` — the evidence behind VERDICT 038 (conditional).
> Source: idea-engine `control/inbox.md` ORDER 005 · 2026-07-13T07:51:32Z · SIM-REQUEST 2
> (fm ORDER 043 relay, Q-0264 fan-in; requesting seat **superbot-idle**).
> Packet: superbot-idle `control/outbox.md` § SIM-001 economy-FEEL cluster + `docs/design/`
> @ `d992c5688e802b28d11c0ec6c835fa54a87149ec`.
> Registered spec: `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)"
> (scenarios S1/S2/S3, outputs O1–O6, criteria A1–A10, verdict semantics).

## METHOD LABEL: `simulation`

NUMERIC SIMULATION (method-ladder rung 1). Deterministic, integer-exact, stdlib-only,
hermetic (reads only its own fixtures), NO RNG anywhere — zero seeds drawn, the fleet
seed-registry high-water 20260775 (V037) untouched; determinism is proven by
byte-identical re-run (external diff of stdout + results.json across two full process
runs: sha256 stdout `76b9ce28f33c…`, results `c91c82ede48d…`), ~23 s per run on
CPython 3.11 (recorded, not asserted — the engine is exact big-int arithmetic,
platform-independent by construction). Pre-registration `fixtures.json` (anchors, arms,
bands, rules, 13 intake-time decisions) committed BEFORE the runner; ONE disclosed
amendment (A7 anchor mapping, below); git history is the trail.

## PREMISE (verified at run time, pinned into the fixtures)

- `fixtures/idle_engine/` + `fixtures/tools/simulate.py` are byte-for-byte copies of
  `menno420/superbot-idle` @ `d992c568`, sha256-manifest-verified before any import.
  The entire economy surface is byte-identical to V017's fixture pin `c753bc8` (only
  `render.py`, outside the surface, differs) — so V006/V017 published numbers must
  reproduce, and they do (B0).
- The driver never reimplements the registered spec: the repo's own committed SIM-001
  harness is imported through the V006/V017 synthetic-package-anchor accommodation
  (the byte-identical `__init__.py` is never EXECUTED) and its `run_report(full)` /
  `simulate_s2` / `simulate_s3` produce every baseline and arm number. The single
  driver-level variant (seed-count arm; the vendored world hard-codes count 1) is
  equivalence-GATED against the vendored `simulate_s3` at C=1 (exact purchase + reset
  trail match) before any C>1 cell is trusted.
- NO generator purchase path exists at `d992c568` (self-checked: `purchase_upgrade` /
  `purchase_upgrades` are the only purchase functions) — every generator-dependent
  probe is an HONEST NULL by premise (see the V017 chain, below).

## What the sim MODELS

The registered SIM-001 world exactly: one `tier1` generator (base_rate 1/s, count
fixed 1), the `boost1` ladder priced by `build_upgrade_spec`, one prestige track per
`build_prestige_spec`, the pinned PROVISIONAL table {60, 115/100, 25, 100000, 100000,
10}, horizon 14 simulated days, S1 idle-only / S2 check-in N ∈ {0.25, 2, 8, 24} h /
S3 optimal speedrun, greedy buy-when-affordable, prestige-iff-eligible, all AMB-1..11
literal readings inherited from the committed harness verbatim. Arm legs change
exactly ONE constant each (registered exact-integer arms), everything else pinned.

## What it SETTLED (the load-bearing numbers)

**B0 — baseline validity: VALID.** Every hard anchor reproduced EXACTLY from the
byte-copied engine: first three boost1 costs **60/69/79**; rate-by-level L0–L5
**[1,1,1,1,2,2]**; S3 first prestige **t = 12573 s** (3.49 h); run-2 duration
**11536 s** (ratio 11536/12573 → **0.9175**); O6 20-reset final ratio 1398/1447 →
**0.9661**; committed-harness criteria **A1–A9 PASS, A10 FAIL** (strict reading);
V006 cross-pins A1 60 s · A2 12 · A4 100000 s · A5 21600 s · durations 12573/11536/10475
· A8 gap 1215 s · O6 awards all 1 · 9-of-12 early purchases inert. The packet's one
"~" number landed exact: S3 reaches **80,796 resets** in 14 days (soft anchor ±100, hit
dead-on). Disclosed amendment 1: V006's published A7 pin (6,16) is the harness's
INCLUSIVE AMB-4 auxiliary — reproduced exactly on that reading; the strictly-before
gate values are (13,30); both readings clear A7's ≥ 2 band, nothing decision-bearing
moved.

**ASK 1 — first-upgrade no-op: CONFIRMED-INERT** (registered rule: first felt purchase
≥ 2 AND inert early spend ≥ 50%). With count 1 / base_rate 1 the fold is
rate(L) = (100+25L)//100 = 1 + L//4 (self-checked per level against the real engine):
a purchase is FELT only at levels 4, 8, 12, … — **the first THREE purchases (60+69+79
= 208 primary) buy nothing felt; the first felt purchase is #4**; **9 of the first 12
purchases are inert = 69.5% of early spend**; over the full first run (13 purchases to
level 13) the felt share is **3/13 ≈ 23.1%** and 74.6% of all run-1 spend is
felt-inert. Tuning arms (all measured, full table in results.json): minimal
purchase-1-felt values are **EFFECT_PERCENT = 100** (25→100), **base_rate = 4**,
**seed count = 4**; growth is a confirmed NON-lever for feltness. **No axis is
viable**: E = 100 breaks A3+A6 (first prestige 3378 s, ratio 29.6×), base_rate 4
breaks A3+A4 (4180 s, crossing 25000 s), count 4 breaks A1+A3+A4 — every constant big
enough to make purchase 1 felt destroys the registered pacing bands. The registered
fallback therefore fires: **the packet's own third option, a min-visible-delta floor
in the effect fold, is the only lever that can fix feltness without re-deriving the
whole table** — an engine change, routed as the design recommendation with the
inertness table as sizing input. (Softer measured note: E = 34 keeps all screens green
and moves the first felt purchase from #4 to #3 — a palliative, not a fix.)

**ASK 2 — weak prestige payoff: CONFIRMED** (registered rule: run-2 speedup ≤ 10% AND
awards flat at 1 AND speedup shrinking). The payoff curve across the 20-reset O6
ladder: r₂ = 0.9175 (**8.25% faster after a 3.49 h grind**), every award exactly 1,
marginal relative bonus falling 10/100 → 10/290, per-reset speedup decaying 8.25% →
3.39% (r₂₀ = 1398/1447 = 0.9661); time-to-award-K: award 2 at 24109 s, award 5 at
53167 s, award 10 at 89817 s, award 20 at 140253 s ≈ 39 h. Lever arms (one constant
each, 20-reset ladders): divisor 50000 changes NOTHING (award still 1 — isqrt floors
it away); divisor 25000 → award 2, r₂ = 0.8331; divisor 10000 → award 3, r₂ = 0.7680;
bonus 25 → r₂ = 10066/12573 = **0.8006**; bonus 50 → r₂ = 0.6588. Registered
mechanical rule (felt band r₂ ≤ 0.85 inside T9's [0.5, 1.0], smallest change
magnitude): **recommended lever = PRESTIGE_BONUS_PERCENT 10 → 25** (run 2 becomes
19.9% faster; T9 band intact; awards stay flat 1 so the award-flation axis is
untouched; every arm keeps the A10 trend rising and the super-geometric flag false).

**ASK 3 — A10 ruling: TREND-PASS; graduation: GRADUATE-WITH-REWORDING** (registered
rule, wiggle band 1/50 registered at 2× the packet's own on-record wiggle). The strict
literal gate fails with **6 violations** (ratio drops at k = 3, 9, 11, 13, 15, 19 of
0.0095 / 0.0030 / 0.0166 / 0.0135 / 0.0035 / 0.0014 — max **740545/44635132 ≈ 0.0166**,
inside the 0.02 band, honestly noted at 83% of it); the TREND rises 0.9175 → 0.9661
toward 1 and the harness's own super-geometric flag is False. Ruling: **A10's strict
wording trips on integer-floor wiggles, not on the failure mode it registers against**
(sub-exponential stacking holds). Graduation: A1–A9 PASS + TREND-PASS ⇒ **graduate the
PROVISIONAL table → SIM-PINNED conditional on re-registering A10 in trend form in the
same PR** (proposed wording in fixtures.json `a10_trend_wording_proposed`; final text
is the requesting seat's to register). Auxiliary, as the packet flagged: optimal play
reaches exactly **80,796 resets** in 14 days (late resets shrink to seconds) — a v2
cap/cooldown criterion is recommended as a NEW registered target, not folded into A10.

**FEEL probes (ORDER 005's framing, registered metrics with bands):**
- **F1 session pacing — PASS**: median gap between early-session purchases 70 s, max
  93 s (band ≤ 120 s, the doc's own "a purchase every minute or two"); worst mid-run
  gap 1215 s = 9.66% of the run (band < 25%).
- **F2 meaningful-choice cadence — FAIL**: felt-purchase share of run 1 = 3/13 ≈
  **23.1%** vs the registered ≥ 50% line — the quantified form of ASK 1's complaint:
  pacing of purchases is fine, but three of four purchases are felt-noise.
- **F3 idle-vs-active balance — PASS**: active advantage 100000/12573 ≈ 7.95× (band
  4–12×); return-visit bursts ≥ 2 levels on both readings (strict minima 13/30,
  inclusive 6/16).

## The probe battery (v0 — the 8 questions, per ORDER 005 "evidence per your 8-question battery")

1. **What is this really?** A pacing engine whose integer rate-floor fold makes the
   FIRST felt reward arrive at purchase 4 and whose prestige loop pays 8.25% per
   3.5 h — timing criteria all green, felt-reward cadence measurably broken (23.1%).
2. **What is the possibility space?** Four feltness axes (effect %, base rate, seed
   count, min-visible-delta floor) × two payoff levers (bonus %, award divisor) — all
   swept here as exact arms; plus the not-yet-built generator tier (V017's row).
3. **Most advanced capability by the simplest implementation?** For payoff: ONE
   constant, PRESTIGE_BONUS_PERCENT 25, makes run 2 19.9% faster with zero side
   effects on A-criteria trends. For feltness: no constant works — the simplest real
   fix is the engine-side min-visible-delta floor.
4. **What breaks it?** Any feltness constant big enough to work (E=100/B=4/C=4)
   breaks A3/A4/A6 pacing; strict-literal A10 wording breaks on integer-floor
   wiggles (≤ 0.0166) forever — no parameter change fixes a wording bug.
5. **What does it unlock?** Graduation of the seven-parameter table PROVISIONAL →
   SIM-PINNED (blocked only by A10's wording), and the E#52 generator cost-curve
   build (with V017's priced row).
6. **What does it depend on?** The pinned engine surface @ d992c568 (byte-identical
   to V017's pin); the committed harness's AMB readings; re-registration happening
   doc+engine same-PR per economy-v1.md's own verdict semantics.
7. **Which lane should build it?** superbot-idle (requesting seat) — doc re-wording
   + any constant re-registration; the min-visible-delta floor is an idle_engine
   change on the same lane. Nothing for sim-lab to build.
8. **Smallest shippable slice?** Re-register A10 in trend form (doc-only, zero
   parameter change) and graduate the table — everything else (bonus 25, delta
   floor, v2 reset cap) ships as separately-registerable rows with this verdict's
   measured tables as evidence.

## What it did NOT settle

- FELT-threshold values for a min-visible-delta floor (engine mechanic does not
  exist; sizing input = the inertness table, but the mechanic's own sim must follow
  its build — same discipline as V017's A11 row).
- Anything generator-dependent: NO purchase path at the pin ⇒ honest NULL. T10/A11
  stay exactly V017's conditional row (C2 = 900, R2 = 5, T10 = 1948 s in the 15–45 min
  band). This verdict + V017 jointly feed fm owner-queue E#52.
- Human perception: "felt" here = integer rate delta > 0, the only player-visible
  rate the engine exposes. A UI that displays fractional rates would change what
  "felt" means without changing the engine (named flip axis).
- The ASK-2 lever choice beyond the registered candidates (e.g. changing the award
  SHAPE away from isqrt) — out of registered scope; the curve tables ship as evidence.
- Long-horizon meta-pacing beyond 20 resets (the registered O6 basis); the 80,796-
  reset auxiliary signal is reported, its cap criterion deliberately routed as NEW.

## The validity gate (all five, quoted verbatim from README § "The validity gate")

1. **COMPARABLE TO LIVE?** — The sim IS the registered live contract: the repo's own
   committed harness, byte-copied, driving the byte-copied engine at the pinned
   commit; scenario policies are the spec's own. What the model abstracts away: human
   perception (felt = integer rate delta — disclosed, with the UI flip axis named)
   and milestones (the committed harness's own scope; milestone_percent neutral at
   100 — matches the registered world). No remaining gap could flip a conclusion
   that is itself about the engine's integer arithmetic.
2. **UNCORRUPTED?** — 77 self-checks, 0 failed, exit 0. B0 reproduced EVERY packet
   number and every V006 cross-pin exactly BEFORE any ruling ran (the drift-isolation
   discipline); the driver's one scenario variant is equivalence-gated at C=1; the
   closed-form fold predictions (E ≥ 100, B ≥ 4, C ≥ 4) were registered before the
   run and confirmed by measurement; no seeded luck is possible (zero RNG — bit
   identity is the reproducibility form); no cherry-picking: every registered arm is
   reported including the arms that came out against expectations (divisor 50000 =
   no-op) and the near-band violation (0.0166 vs 0.02). One anchor MAPPING amendment
   disclosed in fixtures.json + here.
3. **ROBUST?** — Not knife-edge where it rules: ASK 1's confirmation has 3 inert
   purchases of 3 (the packet's regime) and 69.5% ≥ 50% with 19.5 pp margin; ASK 2's
   bar is met at 8.25% vs 10% and the recommended arm clears the felt band by 4.9 pp;
   the verdict-level CONDITIONAL survives any single ASK-1/ASK-2 flip (they gate no
   registered criterion). The one narrow number is ASK 3's max wiggle 0.0166 vs the
   0.02 band (83% of it) — flagged: a future retune should re-run the ladder, and the
   proposed trend wording carries the band explicitly so a re-drawn band re-reads.
4. **REPRODUCIBLE?** — One command, no flags, stdlib-only, hermetic; committed code +
   fixtures; stdout and results.json byte-identical across two full process runs by
   external diff (sha256 pinned above); byte-identity holds BY CONSTRUCTION (integer
   engine, zero RNG/floats in decisions — floats appear only as display approximations
   beside exact fractions).
5. **LIMITS?** — This evidence shows the ENGINE's felt economics at the pin under the
   registered greedy policies; it does not show human-perceived fun, retention, or
   anything about the unbuilt generator tier (honest NULL); the ≥ 50% F2 line and the
   r₂ ≤ 0.85 felt band are registered judgment lines shipped with full tables so a
   re-drawn line re-reads, never re-runs; arm screening covers A1/A2/A3/A4/A6 (D5,
   disclosed) — any adopted row must re-run the full committed harness before
   re-registration (the V017 guardrail).

**Gate: PASS.**

## Outcome

**VERDICT 038: `conditional`** — per the pre-registered mapping, evaluated in the
registered REJECT-first order: REJECT (any A1–A9 FAIL or material A10 break) — does
not fire, A1–A9 all PASS and every strict violation is inside the wiggle band;
APPROVE (A1–A10 strict all-PASS) — does not fire, the strict A10 gate fails;
CONDITIONAL fires: **graduate the PROVISIONAL table → SIM-PINNED conditional on
re-registering A10 in trend form (doc change, same PR, zero parameter changes)**,
with the three ASK rulings (CONFIRMED-INERT / CONFIRMED-WEAK / TREND-PASS) and the
measured lever tables (bonus 25 recommended; min-visible-delta floor routed; v2
reset-cap criterion proposed) shipped to the requesting seat as re-registration
candidates. Run: `python3 sims/verdict-038-idle-economy-feel/idle_economy_feel_sim.py`.

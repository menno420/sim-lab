# REPORT — exploration reward bands: TIER_CAPS vs Q-0087 dual-track bands + survival Medium/Hard gradient (idea-engine ORDER 006 item 7, seat superbot-games)

> **Live verdict** (not an exemplar). Binding spec quoted verbatim below from
> `menno420/idea-engine` `control/inbox.md` @
> `8218d6630f53633461d993d9a3caa4ad54ab251d`, ORDER 006 · 2026-07-13T09:02Z.
> Packet read READ-ONLY at `menno420/superbot-games` @
> `57f69be34785afb427d608b207e7369025166e94` (13 files byte-copied, sha256
> per file in `engine/MANIFEST.json`) and `menno420/superbot` @
> `6d8148808e7965f61cd85625798252fe32e1a409` (Q-0087 evidence docs,
> sha256-pinned in `fixtures.json`).
> Run: `python3 sims/verdict-045-exploration-bands/exploration_bands_sim.py`
> (B0 standalone: `python3 sims/verdict-045-exploration-bands/b0_check.py`)

Binding spec, verbatim (ORDER 006 `do:`, SUPERBOT-GAMES BALANCE item 7):

> (7) EXPLORATION-REWARD-BANDS — (a) reconcile games/exploration/quest/catalog.py
> TIER_CAPS (tier I 5/25/10 · II 10/60/25 · III 20/120/50, conservative
> placeholders per D-0008) against the real superbot Q-0087 dual-track bands;
> (b) ratify/tune the survival Medium/Hard gradient
> (games/exploration/survival/difficulty.py: Medium 50/15s/1, Hard 40/20s/1;
> Easy is byte-identical to the mining bar per D-0004).

## The premise finding that shapes (a)

**Q-0087 carries NO numeric band constants.** Verified against superbot @
6d81488 (router entry lines 3518–3542 + the survival design doc's D0/P0
sections): Q-0087 is a dual-track *philosophy* (casual track owns capability;
grind track owns prestige/surplus, never mandatory) plus an approved sim
*methodology* — the "bands" are the survival **P0 harness's future sim-output
pinned tests** (three curves: casual progress/day · grinder surplus per extra
hour · the capability-gap "mandatory-feel" metric). superbot-games' own
D-0008 says the same: reconciliation waits on that upstream ARTIFACT, not the
owner. So "import the real constants" is impossible at this pin — the honest
deliverable is: score TIER_CAPS against the band **definitions** and the
already-verdicted V018/V033 contracts, ship the tables the future P0 bands
will score by lookup, and declare the numeric import an explicit NULL. This
expectation was **registered in fixtures.json before the runner existed**.

## Method

Rung 1 numeric simulation, exact/NO-RNG: every decision-bearing number is
integer/`Fraction` arithmetic over the byte-copied pinned modules, or produced
by the packet's OWN survival harness (`games/exploration/survival/sim.py`)
driven through its public `run()` entry point — zero edits to any constant.
**B0 validity gate first** (`b0_check.py`, 28 checks + replicated in-process):
sha256 manifest re-verified, then TIER_CAPS / GLOBAL_MAX / TUNABLES / mining
bar / RewardBundle field semantics / tier semantics all re-derived from source
and compared to the order's quoted values — any mismatch fails loudly (exit 1).
Pre-registration (`fixtures.json` — Q-0087 band definitions verbatim,
V018/V033 contract anchors, play profiles, bands S1–S4 / C1a–C3 / GB0–GB5,
decision rules in evaluation order, closed-form predictions, gaps G1–G5) was
committed BEFORE the runner (git trail: registration `8c64ed5` precedes runner
`9737207`). ZERO registry seed draws — fleet high-water **20261280 untouched**
(the only RNG anywhere is the packet harness's own internal DetRng spacing
jitter over its `__main__`-default `seeds=range(400)`, packet-owned protocol
constants per the V043 precedent; its own docstring + our sweep prove the
jitter never changes any outcome).

**B0: VALID** — all 28 standalone + replicated checks pass: TIER_CAPS exactly
I (5,25,10) · II (10,60,25) · III (20,120,50) with `capability=None` on every
bundle; GLOBAL_MAX (20,120,50); TUNABLES Easy (60,10,1) · Medium (50,15,1) ·
Hard (40,20,1); **Easy ≡ mining bar BY IMPORT** (`max_energy=energy.MAX_ENERGY,
regen_seconds=energy.REGEN_SECONDS, cost=energy.DIG_COST` in source — D-0004's
identity is drift-proof by construction); RewardBundle = (global_xp, game_xp,
currency, capability); tiers I casual / II standard / III prestige.

## Results (a) — TIER_CAPS vs the Q-0087 band definitions

**Structural (all exact, all PASS):** S1 every tier ≤ GLOBAL_MAX
component-wise; S2 strict monotone I < II < III on all three components; S3
GLOBAL_MAX == TIER_CAPS[III] exactly (the ceiling binds, no slack); S4 the
V033 contract re-derives exactly from these caps — gated-farmer ceiling
`Fraction(floor(4·8/3), 8) × 25 = 125/4 = 31.25` currency/hr (tier II) and
`125/2 = 62.50` (tier III), matching V033's published table; V033's measured
honest ceiling 30.31 ≤ 31.25; farmer/honest = 1.031 ≤ ARB_RATIO_MAX 2.0.

**Band-definition checks (all exact, all PASS):**

- **Curve 1 — casual progress/day.** Registered casual profiles at V033's
  honest r_E = 12 beats/hr: CAS-A (15 min/day) = exactly 1 tier-I
  completion/day → **(5 global_xp, 25 game_xp, 10 currency) per day**, weekly
  (35, 175, 70); CAS-B (10 min/day) = 4 completions/week → (20, 100, 40).
  Strictly positive on every component (C1a) and a casual WEEK out-earns the
  single largest possible grant on the capability axis: 35 ≥ 20 = GLOBAL_MAX
  global_xp, CAS-B 20 ≥ 20 (C1b). The casual day costs 3 energy ≤ Hard's
  burst 40 — no difficulty ever gates it (C1c, couples (a) to (b)).
- **Curve 2 — grinder surplus/hour.** REAL: honest ceiling 30.31 currency/hr
  (V033) vs the casual 10/day — surplus table shipped at h ∈ {1,2,4,8} h/day.
  "Diminishing" is NOT scorable from flat per-completion caps — it is the
  host gate's / P0 harness's property (part of the registered NULL, G2).
- **Curve 3 — capability-gap "mandatory-feel".** The purchase channel is
  structurally closed: capability-per-currency across tiers = 1/2, 2/5, 2/5 —
  non-increasing (C2), grind-tier play never converts currency to capability
  at a premium; no bundle grants capability and tier-III unlocks are play-only
  per the catalog docstring (C3). The weekly gap TABLE ships
  (ratio = 7·h·g·global_xp[tier]/35; at tier III exactly 4·h·g — e.g. the
  V033 gated-farmer frame g=1.25, h=4 gives 20×): the BAND on it is exactly
  the upstream P0 artifact — reported, not ruled.

**Ruling (a): RATIFY-AS-PLACEHOLDERS + HONEST NULL on the numeric band
import** (RULE-A3, the registered expectation): keep `TIER_CAPS`/`GLOBAL_MAX`
exactly as pinned — the D-0005/D-0008 mechanism unchanged, `catalog.py` the
single source of truth — and re-open reconciliation when superbot's survival
P0 harness ships its pinned bands, scored against the shipped capability-gap
table by lookup. No cap adjustment is warranted by any check that is
computable today.

## Results (b) — survival Medium/Hard gradient

**Leg B1 (the packet's own harness, `run(seeds=range(400))`):** reproduces the
repo's own pinned bands EXACTLY and matches every closed-form prediction —

| difficulty | cap/regen/cost | burst | sustained/hr | casual/day | grind 8h | gap |
|---|---|---|---|---|---|---|
| easy (≡ mining bar) | 60/10s/1 | 60 | **360** | 30 | 2940 | 98.0 |
| medium | 50/15s/1 | 50 | **240** | 30 | 1970 | 65.7 |
| hard | 40/20s/1 | 40 | **180** | 30 | 1480 | 49.3 |

**Leg B2 (registered profile sweep on the byte-copied engine, NO RNG):**

| profile | easy | medium | hard |
|---|---|---|---|
| P-CAS-10 (20 att) | 20/20 · 0 refused | 20/20 · 0 | 20/20 · 0 |
| P-CAS-15 (30 att) | 30/30 · 0 | 30/30 · 0 | 30/30 · 0 |
| P-REG-60 (180 att) | 180/180 · 0 | 180/180 · 0 | 180/180 · 0 |
| P-GRD-240 (1440 att) | 1440 · 0.000 | 1009 · **0.299** | 759 · **0.473** |
| P-SAT-480 (5760 att) | 2939 · 0.490 | 1969 · 0.658 | 1479 · 0.743 |

(cells: completed · refusal fraction; every count within the registered ±1
closed-form band, most exact.)

- **GB2 casual immunity PASS** — zero refusals for casual AND regular
  profiles on ALL difficulties: the gradient taxes only saturating play (the
  D0 dual-track core: difficulty never gates casual capability).
- **GB3 orders PASS** — completed strictly decreasing E>M>H, refusal/attrition
  strictly increasing E<M<H on both saturating profiles (Easy exactly 0 at
  the 360/hr press rate).
- **GB4 magnitude PASS** — sustained ratios exactly **M/E = 2/3, H/E = 1/2,
  H/M = 3/4**, inside the registered ratify bands [0.55,0.80] / [0.40,0.60] /
  [0.60,0.90]; the 8-h saturated ratios (0.670 / 0.503) sit within ±0.005 of
  them — the opening burst does not distort the long-run gradient.
- **GB5 quest loop never bound PASS** — V033's honest 12 beats/hr costs 12
  energy/hr vs Hard's sustained 180/hr: **15× headroom**; exact crossover
  shipped: energy binds quest throughput only above 3600/regen_seconds
  beats/hr (360/240/180).

**Ruling (b): RATIFY** (RULE-B3): keep Medium 50/15s/1 and Hard 40/20s/1
exactly as pinned; Easy stays the by-import mining-bar identity (D-0004).

**Gates:** 93 self-checks, 0 failed, exit 0; stdout + results.json
**byte-identical across two full process runs** by external diff (sha256
stdout `8b3f6921…`, results `ba914ecc…`); < 1 s/run, stdlib-only, hermetic
(reads only its own fixtures.json + engine/).

## Validity gate (what would flip this)

- **The upstream P0 artifact landing** (the registered NULL's unlock): once
  superbot's survival P0 harness ships numeric bands, score the committed
  capability-gap and surplus tables against them by lookup — a table row
  outside a pinned band re-opens the specific cap with the arithmetic already
  in hand; no re-sim needed for the comparison itself.
- **A pinned host gate g**: every grinder-side ceiling here is per-g or under
  the V033 gated frame; a committed g value collapses the tables to single
  columns (lookup, not re-run).
- **A seam that prices quest beats at ≠ 1 bounded action** (G5) re-runs GB5
  by the shipped crossover formula.
- **Changing TIER_CAPS or TUNABLES upstream** re-runs the whole sim unchanged
  (one command); the repo's own `tests/test_survival_sim.py` re-pins the
  harness numbers in CI exactly as this sim reproduces them.
- **Live telemetry** (G3, the standing fleet gap) supersedes model-true
  arithmetic wherever they disagree.

## The 8-question probe battery (idea-engine README.md § "The probe battery (v0 — the core method)" @ 8218d66)

1. **What is this really?** A reconciliation ask whose reconciliation TARGET
   does not exist yet: the real deliverable is proving the placeholders are
   safe to keep (they are) and building the instrument the future target
   scores against (the tables), plus a straightforward gradient ratify.
2. **Possibility space?** For (a): ratify / re-size any of 9 cap integers /
   NULL; for (b): ratify / re-derive regen-vs-cap gradient. The binding
   constraints are the D0 hard rule (capability never behind grind-hours),
   V018's K=4 window, V033's host-gate carve-out, and D-0004's by-import
   anchor.
3. **Most advanced capability by simplest implementation?** Zero code
   changes: both surfaces ratify exactly as pinned; the new artifacts are
   evidence tables, not constants — nothing for the seat to wire.
4. **What breaks it?** The P0 artifact landing with bands the tables violate
   (then the specific failing cap re-opens with arithmetic in hand); a
   committed host gate g > ~1.25/hr at tier III widening the capability gap;
   a beat-cost seam change (GB5 formula re-run).
5. **What does it unlock?** Closes the last open superbot-games item of
   ORDER 006 batch 2; gives the exploration lane a verdicted statement that
   its caps satisfy every Q-0087 property computable today; hands the future
   P0 harness a pre-built scoring table.
6. **What does it depend on?** The pinned catalog/difficulty/energy modules
   (byte-copied, manifest-verified); V018's C-cap-4 row and V033's ruling
   (quoted contract anchors); D-0004/D-0008 (both honoured, neither
   re-opened).
7. **Which lane builds it?** Nothing to build in superbot-games (double
   ratify). The named upstream dependency belongs to superbot (the survival
   P0 harness — D-0008's artifact); sim-lab owns only the evidence.
8. **Smallest shippable slice?** This verdict itself: both constants sets
   stay VERBATIM (exactly what the requesting seat's SIM-REQUEST asked —
   "no number was invented"); the capability-gap table travels with the
   verdict for the P0 build to consume.

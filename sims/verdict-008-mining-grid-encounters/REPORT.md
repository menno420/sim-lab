# REPORT — VERDICT 008 / PROPOSAL 008: mining-grid per-action encounter tuning

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> **Source idea:** idea-engine `control/outbox.md` **PROPOSAL 008** (2026-07-11T12:16:30Z,
> `status: sim-ready`) @ `68f45743d4cab7eab5f863f2918e4fb7d9c1c196` (idea entry
> `ideas/superbot/mining-grid-encounters-2026-07-10.md` @
> `977662f2d84d1b29d51fbc4121f2e467afcc6a94`; canonical superbot
> `docs/ideas/mining-grid-encounters-2026-06-22.md` @ `e1090dbcfdf63ffd955399dc2325b9ad1a2f8c8d`).
> **Sister precedent:** `sims/intake-003-wild-encounter-spawn-tuning` (VERDICT 001) — this
> report mirrors its shape, self-check density, and no-earn-rate caveat. **Sim:**
> `mining_grid_encounter_sim.py` (this subtree). **Run:**
> `python3 sims/verdict-008-mining-grid-encounters/mining_grid_encounter_sim.py`
> (deterministic, stdlib-only, 5 seeds, exit 0 iff all **7723** self-checks pass).

---

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — "seeded, deterministic, parameter-swept"). The
encounter dynamics are fully modelable as a per-action roll (`u < chance`) gated by a depth
threshold and a per-player cooldown over seeded playstyle traces, so this sits on rung 1, the
cheapest-adequate rung and the direct analogue of the settled VERDICT 001 spawn-tuning sim.
This label fills the outbox `evidence: simulation`. **One axis of the source claim is NOT
sim-able and is declared out of scope below** — the loot faucet's ABSOLUTE value (no live
fishing/mining earn-rate baseline exists) — which is why the verdict is
`needs-more-evidence`, not `approve`.

## What the sim MODELS

A single player's grid-mine traversal over a 1-hour active-play window (3600s), 5 seeds,
stdlib-only. Each mine **action** carries a timestamp and a grid **depth**; each action at
**eligible** depth may roll a **live per-action encounter**.

- **Per-action live roll** — the owner ruled the roll is live per-action, NOT a
  per-`(seed,x,y,z)`-cell deterministic hash, so every action draws a fresh uniform
  `u ∈ [0,1)`. An action **fires** iff `depth >= threshold` **and** `(now − last_fire) >=
  cooldown` **and** `u < chance`.
- **Guardrails baked into the model** (per the source ruling): a **per-PLAYER cooldown**
  (not per-cell) and **at most one live encounter per player at a time**. The encounter is
  modelled as **resolved instantly** for rate-accounting, so the one-live invariant reduces
  to the cooldown gate (self-checked: no two fires within `cooldown`).
- **Three STYLIZED playstyle traces** (MODELED, not measured from live telemetry — a
  disclosed abstraction; real player depth distributions are unknown):
  - **casual roamer** — slow ~30s/action (jittered), shallow mean-reverting depth walk mostly
    in [0,12] with rare deeper forays; mostly BELOW typical thresholds.
  - **deep-runner** — the HONEST deep player, steady ~12s/action, depth ramps up and parks
    deep (~22–38); most actions eligible.
  - **`!fastmine` grinder** — the ADVERSARIAL/optimal farmer, fast ~3s/action (the shipped
    `!fastmine` cadence), immediately parks at an optimal eligible depth (30, deeper than every
    swept threshold) so EVERY action can roll — the optimal roll-farming strategy, not naive
    play.
- **CRN** — mirroring VERDICT 001's `_HONEST_CACHE` (via the vendored `CrnCache`), the action
  schedule `(t, depth)` AND the per-action `u` are generated ONCE per `(playstyle, seed,
  horizon)` and REUSED across every one of the 64 parameter cells. A cell only changes
  `(threshold, chance, cooldown)`; this keeps the sweep CRN-clean and **monotonic in chance**
  (proven and asserted).

Sweep grids: threshold ∈ {5, 10, 15, 20}; chance ∈ {0.01, 0.02, 0.05, 0.10}; cooldown ∈ {60,
300, 600, 900}s = **64 cells × 3 playstyles × 5 seeds**, plus an **8-hour robustness pass**.
Every headline number is mean (± population sd) over 5 seeds. **7723 self-checks** tie the
simulated rates to analytic caps and abort (exit 1) on any violation. Vendored harness helpers
(`SEEDS`, `mean_sd`, `CrnCache`, `sweep`, `SelfCheck`, `determinism_check`) are copied inline —
the sim never imports the harness at runtime (the layout contract).

## What it SETTLED (the load-bearing claims — in RATE terms, analytically)

**(1) GATING is structural.** Zero encounters are ever recorded at `depth < threshold`, on
every one of the 64 cells × 3 playstyles × 5 seeds (self-check-enforced). At threshold=20 the
casual roamer records **0.00 enc/hr** on every chance/cooldown — the surface is provably calm;
at threshold=15 casual sits at **~0.20 enc/hr** (a rare deep foray occasionally crossing 15 —
those encounters are legitimately at depth ≥ 15, not a gating leak).

**(2) The per-PLAYER cooldown analytically CAPS yield at `3600/cooldown` enc/hr for EVERYONE,
including the optimal grinder — this is the load-bearing anti-farm result.** Fires are ≥
`cooldown` apart, so at most `3600/cooldown` fit an hour regardless of action rate. The
`!fastmine` grinder — parked deep, mining every 3s, rolling on **all 1200** actions — **pins
exactly to the cap at high chance**: at cooldown=600s (cap 6.00) the grinder reaches
`3.60 / 5.20 / 5.80 / 6.00` enc/hr for chance `0.01 / 0.02 / 0.05 / 0.10` and **cannot exceed
6.00** no matter how fast it mines. Self-check-enforced on **every** cell (`enc/hr ≤
3600/cooldown`).

**(3) Farm-unprofitability in RATE terms: the grinder-vs-honest ratio is bounded and SHRINKS as
chance rises, while the grinder's rolls-per-encounter (reward-per-action) collapses.** At
cooldown=600s the grinder-vs-honest yield ratio runs `2.25 → 1.86 → 1.45 → 1.15` as chance
climbs `0.01 → 0.10` — because at a binding cooldown the honest deep-runner (`1.60 → 5.20`
enc/hr) rises toward the same ceiling, so the grinder cannot pull away. Meanwhile the grinder
pays far more effort per reward: at the recommended set it burns **232 eligible rolls per
encounter vs the honest player's 104** (≈2.2×), and at cooldown=900s the gap widens to
**320 vs 123** (≈2.6×). So per-action rolling is farm-**unprofitable in rate terms**: the
grinder's marginal encounters-per-action collapse and its rate advantage is capped near 1–2×
and self-limiting.

**(4) A recommended default set exists** (argued from the full sweep, not cherry-picked — see
the candidate table in stdout): **threshold=15, chance=0.02, cooldown=600s**. Its numbers
(mean ± sd over 5 seeds): casual **0.20 ± 0.40** enc/hr (calm surface); deep-runner
**2.80 ± 0.40** enc/hr — rare-but-present and **comfortably below the 6.00/hr cap**; grinder
**5.20 ± 0.40** enc/hr — cooldown-bounded; grinder-vs-honest ratio **1.86**; rolls-per-encounter
honest **104** vs grinder **232**; faucet **0.43 encounter-loot events per 100 mine actions**
(≈232 mine actions per encounter for the grinder, ≈107 for the honest player). If the owner
wants the surface provably *silent* rather than ~0.2/hr, **threshold=20 hard-zeros casual**
(0.00 enc/hr) at a small cost to the deep-runner (2.60 vs 2.80) — offered as the stricter
alternative.

> **HONESTY on "rare-but-present":** the owner's intent is **qualitative** — there is **NO
> pre-registered numeric target** for what "rare-but-present" means. This report therefore does
> **NOT** invent a numeric bound and then declare it "passed." The 2.80 enc/hr figure is
> reported *as a number the manager can judge against the qualitative intent*, and this vagueness
> is a headline (see gate 1) that pushes the *shape* half of the claim toward
> needs-more-evidence.

## What it did NOT settle

- **The loot faucet's ABSOLUTE value / whether the capped rate is "profitable" — UNMEASURABLE
  here (the headline negative).** No live earn-rate baseline exists. **Restated verbatim from
  VERDICT 001:** *"no live fishing/mining earn-rate baseline exists, so loot values stay
  provisional and the slice must log the same named telemetry."* The sim reports the faucet
  value-agnostically — `faucet% = (encounters/actions) × R` where `R = V_encounter / V_mine_here`
  is the UNPINNED loot-value ratio — and reports `actions/encounter` so the manager can back out
  the tolerable `R` for any target faucet%. Without live loot values, the RATE-half result
  (farming is rate-bounded) cannot be converted into a VALUE-half result (farming is *worthless*).
- **THE TWO HALVES COUPLE — say it plainly:** farm-unprofitability is **settled in RATE terms**
  (the cooldown caps enc/hr; the grinder gains no rate edge and wastes 2–4× the actions) but
  **NOT settled in VALUE terms** (a capped-6/hr faucet could still be lucrative if `V_encounter`
  is large). The rate result is robust and analytic; the value result is un-modelled for lack of
  a baseline. A build can ship the *mechanic* with the defaults below, but its loot *economics*
  is unsettled until the named telemetry lands.
- **The "rare-but-present" numeric target** — owner-vague (above); this report will not
  manufacture one.
- **Real player depth distributions, cadence, and AFK.** The three traces are STYLIZED
  (modeled), not measured; the deep-runner's park band (22–38) and the `!fastmine` 3s cadence are
  assumed, and no AFK / session-churn is modeled.
- **Combat fast-follow / the encounter-resolution content itself** — out of scope (the shared
  resolution engine is VERDICT 001's; duplicate-guard: whichever build lands first fixes it).
- **Multi-player interaction** — single-player model (per-player cooldown is the guardrail, so
  the single-player cap IS the per-player guarantee).

---

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the
conclusion;"**
Partially, and the gaps are **unequal across the two halves**. The abstractions: STYLIZED depth
profiles (not telemetry), an assumed `!fastmine` 3s cadence, no AFK, **loot VALUES entirely
absent**, and an unknown real-player depth distribution. Whether a gap flips the conclusion
splits cleanly: **(a) the cooldown CAP is analytic** — `enc/hr ≤ 3600/cooldown` holds by the
firing rule for ANY trace shape (self-checked on all 64 cells and again at 8h), so no trace-realism
gap can flip the farm-**rate**-resistance result; it is robust to the stylized traces. **(b) The
shape / "rare-but-present" judgment depends on trace realism** — the deep-runner's 2.80 enc/hr
rides on the assumed park band and cadence, and "rare-but-present" has no numeric target, so this
half is explicitly **flagged**, not asserted robust. **(c) The loot-value half explicitly CANNOT
be settled here** — it is not merely a gap, it is un-modelled for lack of a live baseline. So a
gap *can* move the shape/value halves (already routed to needs-more-evidence) but *cannot* move
the analytic rate-cap.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical
stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong — the strongest gate here. *Bugs:* **7723 self-checks**, 0 failed, ending on
`sys.exit(sc.report())` (exit 0 iff clean). They assert, on **every** cell/playstyle/seed:
**GATING** (0 fires below threshold), the **COOLDOWN CAP** (`enc/hr ≤ 3600/cooldown` — the
anti-farm invariant, printed alongside each block), and **ONE-LIVE** (consecutive fires ≥
cooldown apart); plus **MONOTONIC-in-chance** (encounters non-decreasing as chance rises, which
CRN guarantees — proven in the sim docstring by a greedy-earliest-fire argument), a **SANITY**
check (`!fastmine` eligible-actions ≥ deep-runner eligible-actions on every threshold/seed), and
**2 `expect_reject` negatives** (a `cooldown ≤ 0` cell — whose cap would be infinite — and a
`chance > 1` cell MUST be rejected; a validator that failed open would be a hole). *Seeded luck:*
5 fixed seeds with common-random-numbers across the whole sweep; headline sd is small and
reported (e.g. recommended deep-runner 2.80 ± 0.40 enc/hr). *Cherry-picking:* the **FULL 64-cell
sweep** is printed (enc/hr per playstyle, blocked by cooldown, threshold × chance), plus the full
ratio/rolls-per-encounter and loot-faucet tables — the recommended point is argued from a printed
candidate-comparison table, not selected as a best cell. **No self-check fired to expose a hidden
coupling** (unlike VERDICT 001, where a false invariant fired): all 7723 pass. The rate-vs-value
coupling reported above is a **structural disclosure**, not a caught bug.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes on the load-bearing (rate) result, conditionally on the estimate-dependent (shape) one. The
cooldown cap and gating are *analytic* and are re-verified at the grid edges (threshold 5↔20,
chance 0.01↔0.10, cooldown 60↔900) by self-check — they cannot be an artifact of one operating
point. The sim additionally re-runs the **entire sweep at an 8-hour window** (the ROBUSTNESS PASS
block): the per-hour cap and gating are re-asserted on all 64 cells at 8h and hold, and the
recommended-set numbers are stable (casual 0.05, deep-runner 2.95, grinder 4.88 enc/hr;
grinder-vs-honest ratio 1.65 — the grinder's rate advantage does not grow with the longer
horizon). The one conclusion NOT robust to its inputs is the deep-runner "rare-but-present"
figure, which depends on the STYLIZED park band/cadence and on an owner-vague target — flagged,
not asserted robust.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. Code committed and public; ONE documented command
(`python3 sims/verdict-008-mining-grid-encounters/mining_grid_encounter_sim.py`); stdlib-only; 5
fixed seeds; no `hash()`/no wall-clock (PYTHONHASHSEED-independent). The **whole 64-cell sweep is
run twice with the CRN cache cleared between and asserted byte-identical** (`determinism_check`),
and the run exits 0 only when all self-checks pass. Runs in < 1 s.

**5. "LIMITS? what this evidence does NOT show."**
It does **not** show the loot faucet's absolute value or whether the capped 6/hr is "profitable"
(no earn-rate baseline — unmeasurable here), does not use real player depth telemetry (STYLIZED
traces), does not validate the real `!fastmine` cadence, does not model AFK/churn or multi-player
interaction, and treats combat fast-follow and the encounter-resolution content as out of scope.
It answers "which `(threshold, chance, cooldown)` gates encounters by depth and bounds the farm
**RATE**," NOT "is the encounter loot economy balanced in **VALUE**."

---

## EVIDENCE STRENGTH: **moderate** — gate PASS (rate-half settled; shape+value halves routed on)

Reproducibility and the gating/cooldown-cap robustness are strong (self-check-enforced across
7723 checks, analytic and rate-independent, deterministic, re-verified at 8h). But STYLIZED
(un-telemetered) traces, an owner-vague "rare-but-present" target, and the entirely-absent loot
baseline keep it short of **strong**. Well above **hypothesis-only** (it clears gates 2–4 solidly
and the analytic part of 1).

Under the README rule — "A result that fails the gate is a hypothesis, not evidence" — the sim
**PASSES** the gate for the claims it covers (gating; the per-player cooldown cap; the bounded,
self-limiting grinder-vs-honest rate ratio; the collapsing reward-per-action). The loot-value
sub-question is **out of scope** (unmeasurable without live telemetry), and the "rare-but-present"
target is **owner-vague** — neither is a *failed* claim, but together they are why the overall
**verdict is `needs-more-evidence`**, not `approve`: the mechanic can ship with the defaults
below, but its loot *economics* and its shape *acceptance* are unsettled until the named
telemetry lands.

---

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** `needs-more-evidence`. The gating + interruption-rate-bounding + farm-RATE-
  resistance half is **settled analytically**; the loot-faucet-VALUE half and the "rare-but-
  present" shape target are **unsettled** (they couple — farm-unprofitability is settled in RATE
  terms, not VALUE terms). Both prongs of PROPOSAL 008's `done-when` are answered: a recommended
  default set AND the exact telemetry the smallest slice must log.
- **Ruling (what would settle it):** launch a smallest slice logging the named telemetry below,
  then recompute the faucet in VALUE terms against the real `mine_here` earn rate and validate
  the deep-runner depth/cadence traces against real players; that closes the value half and pins
  the shape target.
- **Target:** `menno420/superbot` (hub) — grid navigator `views/mining/grid_mine_view.py`;
  audited `mining_workflow` (RS02/Q-0071); seams `economy_service` / `update_mining_item` /
  `game_xp`. Co-consumer: the Q-0186 wild-encounters / Encounters-cog build (shared
  encounter-resolution engine, VERDICT 001 sim-pinned defaults) — duplicate-guard: same
  resolution engine as VERDICT 001, whichever build lands first fixes it.
- **Recommended launch defaults:** `threshold = 15` (or `20` for a provably-silent surface),
  `chance = 0.02`, `cooldown = 600s` (per-player). At these: casual ~0.2/hr, deep-runner
  ~2.8/hr (below the 6/hr cap), grinder ~5.2/hr (cooldown-bounded), grinder-vs-honest ratio ~1.86
  and shrinking with chance, grinder rolls-per-encounter ~2.2× the honest player's.
- **Guardrails (carry into the ORDER):** **per-PLAYER cooldown (NOT per-cell)** — the load-
  bearing cap; **one live encounter per player**; **audited-seam resolution** through
  `economy_service` / `update_mining_item` / `game_xp` via `mining_workflow` RS02 (Q-0071);
  treat loot **VALUES as PROVISIONAL** — do not scale them until the telemetry yields a
  faucet-in-value ratio.
- **Telemetry the smallest slice MUST log (to close the coupled value + shape gaps):**
  per-action **encounter fire rate per playstyle band**; **per-player cooldown-hit rate**;
  **encounter-loot coin value vs `mine_here` coin value** (the missing baseline — without it the
  faucet% cannot be computed); and the **depth distribution of real players** (to validate the
  STYLIZED traces and pin the "rare-but-present" target).
- **Codex review:** reply: pending.

<!-- Outbox verdict-grammar block (README), emitted on finalization — DRAFT, coordinator finalizes:
## VERDICT 008 · <ISO8601> · status: finalized
target: menno420/superbot
idea: idea-engine control/outbox.md PROPOSAL 008 @ 68f45743d4cab7eab5f863f2918e4fb7d9c1c196 (idea ideas/superbot/mining-grid-encounters-2026-07-10.md @ 977662f2d84d1b29d51fbc4121f2e467afcc6a94; canonical superbot docs/ideas/mining-grid-encounters-2026-06-22.md @ e1090dbcfdf63ffd955399dc2325b9ad1a2f8c8d)
verdict: needs-more-evidence
evidence: simulation
report: sims/verdict-008-mining-grid-encounters/ · run: python3 sims/verdict-008-mining-grid-encounters/mining_grid_encounter_sim.py
recommendation: gating is structural + the per-player cooldown analytically caps encounters at 3600/cooldown enc/hr for EVERYONE incl. the !fastmine grinder (grinder-vs-honest RATE ratio bounded and shrinking toward ~1.15 as chance rises; grinder rolls-per-encounter 2-4x the honest player's -> reward-per-action collapses). Recommended defaults threshold=15 (or 20 for a silent surface), chance=0.02, cooldown=600s. UNSETTLED and COUPLED: the loot faucet's ABSOLUTE VALUE (no live earn-rate baseline -> loot values provisional) and the owner-vague "rare-but-present" target -> farm-unprofitability is settled in RATE terms, not VALUE terms. Ship the mechanic with per-PLAYER (not per-cell) cooldown + one-live-encounter + audited-seam resolution (economy_service/update_mining_item/game_xp via mining_workflow RS02); log the named telemetry (per-action fire rate per playstyle band, per-player cooldown-hit rate, encounter-loot vs mine_here coin value, real-player depth distribution) to close the value+shape gaps.
codex: PR #<n> comment · reply: pending
gate: PASS
-->

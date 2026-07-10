# REPORT — VERDICT 004 / PROPOSAL 004: explore-hub federated-world GLOBAL XP balance

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> **Source idea:** `menno420/superbot docs/ideas/explore-hub-federated-world-2026-06-19.md`
> @ `fd638e3c0693687a62093aa6bd75954e238fa58d`; routed as idea-engine `control/outbox.md`
> PROPOSAL 004, pinned `cd7251ec30950d12d29e65c57d843864387d0aec`. **Sim:**
> `federated_xp_balance_sim.py` (this subtree). **Run:**
> `python3 sims/verdict-004-explore-hub-xp-balance/federated_xp_balance_sim.py`
> (deterministic, stdlib-only, 5 seeds, exit 0 iff all 4469 self-checks pass).

---

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — "seeded, deterministic, parameter-swept"). The
federated-XP dynamics reduce to a leveling curve, a trickle-fed global pool, a two-way split
of an effect budget (rate vs. power), and a seeded per-session earn process — all fully
modelable — so this sits on rung 1, the cheapest-adequate rung and the direct analogue of the
settled `intake-003` precedent. This label fills the outbox `evidence: simulation`. **The
load-bearing result is a CONSTRUCTION argument** (phi=0 ⇒ zero substitution, zero gate, at
every swept magnitude), which the sim demonstrates and self-checks exactly; the recommended
MAGNITUDE is a hypothesis pending live data, which is why the verdict is
`needs-more-evidence`, not `approve`.

## What the sim MODELS

A single player climbing a NEW game from zero to the L_BASE "core-loop comfortable" level,
5 seeds, stdlib-only. Named functions/params (see the sim):

- **Per-game leveling** — `xp_for_level(L) = 60.0 * L**1.6`, inverse `level_from_xp`;
  `L_BASE = 10` (time-to-baseline target), `L_MASTER = 50` (mastery ceiling).
- **Per-game competence** — `pg_competence(L) = (min(L,50)/50)**0.8`, normalized so
  `pg_competence(L_MASTER) = 1.0`.
- **Global pool / veteran career** — a veteran played `n_prior` games each to `L_vet`; a
  trickle `t` of that prior XP flows into a shared pool: `global_pool = t · n_prior ·
  xp_for_level(L_vet)`. `GLOBAL_CAP_XP = 6208.8` is DERIVED so a MODERATE veteran (3 games,
  L_vet=25) at t=0.10 sits at `global_frac = 0.5`. `global_frac = min(1, global_pool/CAP)`.
- **Global boost mechanism (the crux)** — the effect budget `e` is split by a mechanism
  fraction `phi`: `rate_effect = e·(1−phi)` multiplies earn RATE only (accelerator, the
  xp-gain/stamina style); `power_effect = e·phi` adds flat in-game COMPETENCE (the
  luck-as-gear/carry-as-dominance style). `earn_multiplier = 1 + min(BOOST_CAP=0.60,
  rate_effect·global_frac)`; `global_competence = min(GCOMP_CAP=0.60, power_effect·
  global_frac)`; `effective_competence(L) = pg_competence(L) + global_competence`.
- **Session loop (common random numbers)** — ONE per-session earn-noise sequence per seed,
  `Normal(1, 0.15)` clipped to >0.05, is reused for the veteran and the fresh player, so the
  ONLY difference between them is `earn_multiplier` (variance reduction). `sessions_to_baseline`
  = first session whose cumulative XP ≥ `xp_for_level(L_BASE)`.

Metrics per cell (mean±pstdev over seeds): **CSA** cold-start advantage = `(t_fresh −
t_vet)/t_fresh` (fresh uses `global_frac=0`); **MSI** = a global-MAXED game-NOVICE's
`effective_competence(L_BASE, gf=1)` ÷ a true master's `pg_competence(L_MASTER)=1`;
**gate_risk_band** = `global_competence(1.0)`, the width of a global-only content band.
Sweep grids: trickle `t ∈ {0.02,0.05,0.10,0.20,0.40}`; effect `e ∈
{0.05,0.10,0.20,0.35,0.50}`; mechanism `phi ∈ {0,0.25,0.50,1.0}`; veteran depth `(n_prior,
L_vet) ∈ {(1,15),(3,25),(6,40)}` = **300 cells × 5 seeds**. **4469 self-checks** tie the
simulated numbers to the analytic mechanism and abort (exit 1) on any violation.

## What it SETTLED (the load-bearing claims)

**(1) MECHANISM dominates the risk — "accelerator, never gate" holds BY CONSTRUCTION at
phi=0.** When the whole effect budget is spent on earn-RATE (phi=0), the substitution term
`global_competence(1.0)` and the `gate_risk_band` are **0.000 for EVERY swept e and every t**
(mechanism-sweep table, phi=0 row all zeros). A global-maxed but game-novice player's MSI is
then exactly `pg_competence(L_BASE) = 0.276` — identical for all e — i.e. the global pool
adds NOTHING to in-game competence and opens NO content band. This is an identity, not a
tuned point, and is asserted exactly on every cell. Meanwhile CSA still scales with e, t, and
veteran depth (below), so the accelerator is real without ever being a gate or a substitute.

**(2) Cold-start acceleration scales with e, trickle, and veteran depth (a free UX dial).**
At phi=0, moderate veteran, CSA rises from 0.000 (e=0.05, t=0.02) to 0.333 (e=0.50,
t≥0.20). The recommended default **phi=0, e=0.20, t=0.10** gives moderate-veteran CSA =
**0.091 ± 0.014** (`earn_multiplier = 1.10`) — right at the 0.10 "measurable" line — while
deeper veterans clear it comfortably (deep-vet CSA at e=0.20, t=0.10 = **0.167**; at e=0.35 =
0.258). The trickle saturates: t=0.20 and t=0.40 give identical moderate-vet CSA because
`global_frac` has already hit 1.0 and the earn term is `BOOST_CAP`-limited. So magnitude is a
dial: raise e or t to buy more cold-start help, bounded by `BOOST_CAP`.

**(3) Any phi>0 turns global level into a substitute AND a gate, monotonically.** At the
worst swept cell (**phi=1.0, e=0.50**) a global-maxed novice reaches MSI = **0.776** (nearly
a master's competence with zero in-game mastery) and opens a `gate_risk_band` of **0.500** —
content placed in (1.0, 1.5] is reachable ONLY with global level, i.e. a hard gate. Both
`global_competence` and the band are monotone nondecreasing in phi and in e (self-checked).
The safe-region decision table (moderate depth, all 100 (t,e,phi) cells) shows **9 GATE-FREE
PASS cells — all at phi=0**; the 8 additional cells that pass the *loose* `<0.15` band
tolerance all sit at phi=0.25 and carry a small but NONZERO band (0.05–0.125), so under the
strict "never gate" contract only the phi=0 column is truly safe.

## What it did NOT settle (negatives as headlines)

- **The exact earn-shape curves are family-level stand-ins, not the shipped catalogue.**
  `BASE_SESSION_XP=100` and `xp_for_level = 60·L**1.6` stand in for the shipped
  mining/fishing/GAME_ENCOUNTERS earn shapes; the *magnitude* numbers (CSA, sessions-to-
  baseline) ride on that abstraction. The STRUCTURAL phi=0 result does NOT (see the gate).
- **Session-length distribution is assumed** — one abstract "session" = `BASE_SESSION_XP`
  earn units × noise; real sessions vary in length and the per-session variance is a guess
  (`NOISE_CV=0.15`).
- **The organic efficiency→power conversion is unmodeled.** A player who earns faster (rate
  boost) will, over time, convert that into higher in-game level and thus real power — a
  *secondary* substitution channel the sim does not capture. The phi=0 guarantee is about the
  DIRECT mechanism only; it says nothing about players out-leveling faster because they earn
  faster (which is the intended, contract-compatible effect, but its magnitude is unmeasured).
- **"Measurable / feels-good" effect magnitude needs live data.** Whether CSA≈0.09–0.17
  reads to a player as "a noticeable head start" versus "invisible" is a UX question no
  offline sim can answer; the 0.10 line here is this report's stipulation, not a measured
  threshold.

---

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the
conclusion;"**
Split, and the split is the whole point. The LOAD-BEARING conclusion (phi=0 ⇒ zero
substitution, zero gate, at every magnitude) is a CONSTRUCTION argument: `global_competence =
min(cap, e·phi·gf)` is identically 0 whenever phi=0, independent of the earn shape, the
session model, `GLOBAL_CAP_XP`, or the noise — so NO abstraction gap can flip it (this is why
it self-checks to exact 0.000 on all cells). What the model DOES abstract away — the shipped
earn curves, session-length distribution, and the secondary efficiency→power conversion — bears
ONLY on the MAGNITUDE conclusions (CSA numbers, the exact measurable line), and those gaps can
and likely do move the recommended `e`/`t`. Honest residual risk: the recommended magnitude
(e≈0.20) is where the abstraction is load-bearing and could be wrong; the structural
recommendation (phi=0) is where it cannot.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical
stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. *Bugs:* **4469 self-checks** tie every simulated number to the analytic mechanism —
`earn_multiplier ≥ 1` and `== 1` exactly iff there is no acceleration; `t_vet ≤ t_fresh` on
every cell/seed; CSA ∈ [0,1); the analytic tie `t_vet ≈ t_fresh/earn_multiplier` within noise
on every cell/seed; `phi=0 ⇒ global_competence==0 ∧ MSI==pg_competence(L_BASE) ∧
gate_risk_band==0` asserted EXACTLY; monotonicity of CSA in e and of the band in phi and e;
`global_frac ∈ [0,1]`; `pg_competence` monotone with `pg_competence(L_MASTER)==1` — across all
300 grid cells. *Seeded luck:* 5 fixed seeds with common-random-numbers (veteran and fresh
share one noise sequence); the run is byte-identical across repeats (determinism self-test).
*Cherry-picking:* the FULL 300-cell sweep is printed — the CSA (t×e) table, the mechanism
(phi×e) table, the depth×e table, and the entire 100-row (t,e,phi) decision table with
PASS/FAIL — the recommendation is argued from the whole grid, not a selected cell.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes for the structural claim, conditionally for the magnitude. The phi=0 result is verified at
every edge of every axis (t 0.02↔0.40, e 0.05↔0.50, all three veteran depths) — it is 0 by
construction, so edges cannot break it. The MAGNITUDE result is robust in *direction* (CSA
monotone up in e, t, depth; saturating at `BOOST_CAP`) but its *level* is not robust to the
abstracted earn shape. Edge behaviour is sane: a shallow vet at t=0.10 gets near-zero CSA
(global_frac 0.074) while a deep vet saturates at global_frac 1.0 — the accelerator neither
vanishes for everyone nor runs away.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong — the strongest gate. Code committed and public; ONE documented command
(`python3 sims/verdict-004-explore-hub-xp-balance/federated_xp_balance_sim.py`); stdlib-only
(`random`, `statistics`, `collections`); 5 fixed seeds; no `hash()`, no wall-clock
(PYTHONHASHSEED-independent). Two consecutive runs were verified byte-identical, and the run
exits 0 only when all 4469 self-checks pass.

**5. "LIMITS? what this evidence does NOT show."**
It does not show the real cold-start magnitude on the shipped earn curves (family-level
stand-ins here), does not model session-length distribution or the secondary efficiency→power
conversion, and cannot say whether the modeled CSA "feels" like a head start (a UX question).
It answers "which MECHANISM keeps a global pool an accelerator and never a gate/substitute
(phi=0, structurally) and how magnitude scales with (e, t, depth)," NOT "what exact (e, t)
players should get" — that needs the telemetry below.

---

## EVIDENCE STRENGTH: **moderate** (structural claim **strong**; magnitude **hypothesis**)

Two-tier. The STRUCTURAL claim — rate-only global skills (phi=0) cannot substitute for mastery
or gate content at ANY swept magnitude — is **strong**: it is a construction argument,
self-checked to exact 0 on all 300 cells, deterministic and reproducible, and robust to every
abstraction the sim makes (gate 1's load-bearing gap does not touch it). The MAGNITUDE
recommendation (e≈0.20, t≈0.10 giving CSA≈0.09 at moderate depth) is a **hypothesis**: it
rides on family-level earn shapes and an assumed session model, so it clears gates 2–4 but is
explicitly weak on gate 1's COMPARABLE-TO-LIVE for the numbers.

Under the README rule — "A result that fails the gate is a hypothesis, not evidence" — the sim
**PASSES** the gate for the structural claim (no gate fails; it is settled by construction) and
therefore counts as evidence for the phi=0 invariant. The magnitude is carried as an explicit
hypothesis, NOT a failed claim — which is why the overall **verdict is `needs-more-evidence`**,
not `approve`: ship the phi=0 mechanism as the invariant now; confirm the magnitude on live
telemetry.

---

## VERDICT & recommendation (for the fleet manager to route)

**Verdict: `needs-more-evidence`.** The mechanism half is settled (phi=0 is a structural
"accelerator-never-gate" guarantee); the magnitude half needs live data. Both prongs of
PROPOSAL 004's `done-when` are answered: a recommended safe default AND the exact telemetry the
smallest slice must log.

**Target:** `menno420/superbot` — explore-hub plan **PR 2 owner gate**; seams `game_xp`,
`economy_service`, `world_registry` #1156.

**Recommended default:** global skills as **RATE/efficiency multipliers (phi = 0)** — this is
the load-bearing invariant, not a dial — effect budget **e ≈ 0.20**, trickle **t ≈ 0.10**,
hard **BOOST_CAP ≈ 0.25**, and **content thresholds set ≤ the pure-per-game max (1.0), never
inside a global-only band**.

**Guardrails (ship all):**
- Ship the **phi=0 mechanism constraint as the invariant** (global skills may only multiply
  earn RATE / efficiency — stamina, xp-gain, movement — never add flat in-game power/competence);
  keep the effect MAGNITUDE (e, t, BOOST_CAP) a tunable.
- Enforce **content thresholds ≤ pure-per-game max**: no unlock may require global level (any
  content reachable only via the global pool is a contract violation).
- Treat the recommended e/t as PROVISIONAL — tune on the telemetry below, not by feel.

**Telemetry PR 2's plumbing slice MUST log (to close the magnitude gap):**
- per-session **earn amount + source game**;
- **session length**;
- **`global_frac` at each new-game start**;
- **sessions/time-to-baseline (L_BASE)** in each new game;
- **per-game-level vs global-level at every content-unlock event** (to detect any content
  reached with sub-baseline per-game level — the gate-violation tripwire);
- **trickle inflow rate per game**.

**Out of scope (owner-reserved design questions — NOT settled here and not for this sim to
decide):** hub shape, survival overlay, docking topology, and cross-game identity.

**Codex review:** _placeholder — the coordinator will post the `@codex` review comment (one
specific question, on the final PR head); reply disposition to be recorded in the outbox
verdict._

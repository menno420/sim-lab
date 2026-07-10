# REPORT — INTAKE 003 / PROPOSAL 003: wild-encounter activity-spawning tuning

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> **Source idea:** `menno420/superbot docs/ideas/wild-encounters-activity-spawning-2026-06-20.md`
> @ `fd638e3c0693687a62093aa6bd75954e238fa58d`; routed as idea-engine `control/outbox.md`
> PROPOSAL 003 (2026-07-10T20:10:06Z), pinned
> `d70a31126f5d2ce318449ab85f018e62e39e3831`. **Sim:** `wild_encounter_spawn_sim.py` (this
> subtree). **Run:** `python3 sims/intake-003-wild-encounter-spawn-tuning/wild_encounter_spawn_sim.py`
> (deterministic, stdlib-only, 5 seeds, exit 0 iff all 946 self-checks pass).

---

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — "seeded, deterministic, parameter-swept"). The
spawn/claim dynamics are fully modelable as a debounced counter + a threshold + a claim/cooldown
process over seeded message traces, so this sits on rung 1, the cheapest-adequate rung and the
closest analogue to the settled `gen3_deployment_sim` precedent. This label fills the outbox
`evidence: simulation`. **One axis of the source claim is NOT sim-able and is declared out of
scope below** (reward inflation vs. fishing/mining — no live baseline exists); that does not
change the rung of the evidence that WAS produced, but it is why the verdict is
`needs-more-evidence`, not `approve`.

## What the sim MODELS

A single opted-in channel over an 8-hour active window, 5 seeds, stdlib-only:

- **Honest traffic** — Poisson message arrivals at a per-tier rate (EST), author uniform over
  N users (EST). One honest trace per (tier, seed) is REUSED across every parameter set (common
  random numbers → a fair, variance-reduced comparison). Tiers: `low` 0.5 msg/min / 3 users;
  `med` 3 msg/min / 8 users; `high` 15 msg/min / 25 users.
- **Debounced counter** — a message increments the counter only if it lands `>= debounce`
  seconds after the previous COUNTED message; the counter accrues ONLY while no spawn is live
  (the conservative "no banking during a live spawn" design — the accrue-during-live variant is
  a stated LIMIT).
- **Spawn** — at `counter >= threshold` a spawn goes live (embed + Claim); counter resets to 0;
  **one live spawn per channel** (no new spawn accrues while one is live). Unclaimed spawns
  expire after `SPAWN_TTL = 300s`.
- **Claim** — the first later message whose author is off **per-claimer cooldown** claims the
  live spawn; that author goes on cooldown for `cooldown` seconds; the spawn clears and accrual
  resumes.
- **Adversarial farmer** — a single account (id −1) paced at a chosen inter-message gap,
  optionally amid honest high traffic, claiming every spawn its cooldown permits.

Sweep grids: threshold ∈ {12, 24, 36, 48}; debounce ∈ {5, 10, 20, 30, 60}s; cooldown ∈ {60,
300, 900, 1800}s. Every headline number is mean over 5 seeds. **946 self-checks** tie the
simulated rates to analytic caps and abort (exit 1) on any violation.

## What it SETTLED (the load-bearing claims)

**(1) A recommended default set keeps spawns rare-but-visible in every tier.** Operationalizing
"rare-but-visible" as roughly 0.5–6 spawns per active-hour in all three tiers (the source gives
no numeric target — this band is this report's explicit definition), the set **threshold=24,
debounce=30s** lands at **0.93 / 3.00 / 4.38 spawns per active-hour** for low / med / high — all
inside the band, with ~30 real messages per spawn. It anchors the only number in the source (the
research report's "~24 messages" anecdote).

**(2) The debounce×threshold product sets a traffic-independent spawn CEILING.** Because the
counter can increment at most once per `debounce`, spawns are bounded by `3600/((threshold−1)·
debounce)` per hour regardless of how busy the channel is — **5.22 spawns/hr** at (24, 30s). This
is why the `high` tier (15 msg/min) lands at 4.38/hr instead of running away: the sweep shows
that dropping debounce to 5–10s lets high traffic hit **10–33 spawns/hr** (spawn-spam), while
debounce=30–60s holds it to 2–5/hr. The ceiling is enforced by self-check on every one of the
60 (tier×threshold×debounce) grid cells.

**(3) Paced-spam farming is hard-bounded, and fast spam is worthless.** Any single account's
claim rate is capped at `min(spawn ceiling, 3600/cooldown)` — **4.00 claims/hr** at (24, 30s,
900s), traffic-independent and self-check-enforced. The plateau table shows a lone farmer pacing
4× *faster* than debounce (gap 7.5s, 3840 messages) gets the SAME 4.00 claims/hr as pacing at
debounce (gap 30s, 960 messages) — reward-per-message falls 4× (0.0083 vs 0.0333). So the only
non-wasteful farm is: pace at ~debounce, send **≥24 spam messages per reward**, and accept the
per-cooldown cap. In busy traffic the farmer additionally loses the claim race to denser honest
messages (0% share in the high-tier run) — see the LIMIT on that result below.

## What it did NOT settle

- **Reward inflation vs. fishing/mining earn rates — UNMEASURABLE here.** No earn-rate baseline
  exists in the source (fishing v1 shipped superbot #1033–#1041 with no published rate; the probe
  report says so explicitly: "No earn-rate baseline exists to check a new source against — not
  measured"). The sim reports only the ABSOLUTE mint: **~6.8 / 24.0 / 35.0 claims per 8h window**
  (low/med/high) at the recommended set. The RATIO to fishing/mining cannot be computed without
  their earn-rate telemetry. This is the headline negative result.
- **Whether the capped-4/hr farm is "profitable"** in coin terms — needs a reward valuation
  (coin/item value) the sim does not have. The sim bounds the *quantity* a farmer can mint, not
  its *worth*.
- **The reflex-bot farmer.** Claims are modeled as message-driven (an account only claims when it
  sends a message), so a listener-bot that clicks the instant a spawn appears is NOT modeled; the
  "0% farmer share in high traffic" is therefore optimistic. Against such a bot the binding
  guarantee is the analytic per-account cooldown cap (still 4/hr at cd=900), NOT the 0%.
- **Absolute traffic** — the three tiers are EST, not measured; the `low`-tier visibility
  (0.93/hr) rides on the 0.5 msg/min estimate.
- **The accrue-during-live-spawn variant, multi-channel/guild effects, content-quality/spam
  detection, and claim atomicity** (an engineering constraint per Q-0071, not a tuning unknown).

---

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the
conclusion;"**
Partially, and the gaps are unequal across the conclusions. The spawn-frequency and anti-farm
CEILING results are driven by the counting mechanics (debounce, threshold, one-live-spawn) which
are modeled faithfully and whose caps are *analytic and traffic-independent* — no plausible
traffic gap flips them. The gaps that CAN move a conclusion are: (a) the EST traffic tiers, which
set the `low`-tier visibility number (0.93/hr) — a slower real channel could push `low` below the
"visible" band; and (b) the message-driven claim model, which makes the "farmer 0% share in busy
channels" optimistic (a reflex-bot is not modeled). Neither gap touches the load-bearing per-
account cap (4/hr). The reward-inflation axis is not merely a gap — it is un-modeled for lack of
a baseline (see gate 5).

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical
stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong — the strongest gate here. *Bugs:* **946 self-checks** tie every simulated rate to its
analytic cap (spawns ≤ ceiling on all 60 grid cells; farmer claims ≤ per-account cap on every
cooldown; counter ≤ threshold; claims ≤ spawns) and abort on violation — and a self-check
already earned its keep: an early assertion asserting "spawn count is invariant to cooldown"
FIRED, correctly exposing a real second-order coupling (a faster claim clears the live spawn
sooner, so accrual resumes sooner); the false invariant was removed and the coupling is disclosed
here, not hidden. *Seeded luck:* 5 fixed seeds with common-random-numbers across the sweep; the
run is byte-identical across repeats (determinism self-test). *Cherry-picking:* the FULL 4×5
sweep is reported per tier (spawns/hr AND messages/spawn), plus the full cooldown grid — the
recommended point is argued from the whole table, not selected as the best cell.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes on the load-bearing results, conditionally on the estimate-dependent one. The spawn ceiling
and the farmer cap are *analytic and traffic-independent*, verified across the entire sweep and
at the edges (threshold 12↔48, debounce 5↔60, cooldown 60↔1800) by self-check — they cannot be an
artifact of one operating point. The recommended (24, 30, 900) sits comfortably inside the
visibility band in all three tiers. The one conclusion NOT robust to its inputs is `low`-tier
visibility, which depends on the EST 0.5 msg/min rate — flagged, not asserted as robust.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. Code committed and public; ONE documented command
(`python3 sims/intake-003-wild-encounter-spawn-tuning/wild_encounter_spawn_sim.py`); stdlib-only;
5 fixed seeds; no `hash()`/no wall-clock (PYTHONHASHSEED-independent). Two consecutive runs were
verified byte-identical, and the run exits 0 only when all self-checks pass.

**5. "LIMITS? what this evidence does NOT show."**
It does not show reward inflation vs. fishing/mining (no baseline — unmeasurable here), does not
price whether capped farming is worth the spam effort, does not model a reflex-claim bot, uses
EST traffic tiers rather than measured ones, models a single channel with the "no banking during
a live spawn" design, and ignores content-quality/spam detection and claim atomicity. It answers
"which (threshold, debounce, cooldown) keeps spawns rare-but-visible and bounds farming," NOT
"does the reward economy stay balanced."

---

## EVIDENCE STRENGTH: **moderate**

Reproducibility and the anti-farm/ceiling robustness are strong (self-check-enforced, traffic-
independent, deterministic), and a self-check caught a real modeling error before it could
mislead. But EST traffic tiers, the message-driven claim model (optimistic on reflex-bots), and
the entirely-absent reward baseline keep it short of **strong**. Well above **hypothesis-only**
(it clears gates 2–4 solidly and most of 1).

Under the README rule — "A result that fails the gate is a hypothesis, not evidence" — the sim
**PASSES** the gate for the claims it covers (spawn frequency per tier; the spawn ceiling; the
per-account farm cap; the fast-spam plateau). The reward-inflation sub-question is **out of
scope** (unmeasurable without live telemetry), not a failed claim — which is why the overall
**verdict is `needs-more-evidence`**, not `approve`: the mechanic can ship with the defaults
below, but its reward *economics* is unsettled until the named telemetry lands.

---

## VERDICT & recommendation (for the fleet manager to route)

**Verdict: `needs-more-evidence`.** The spawn-tuning/anti-farm half is settled; the reward-
economics half is unmeasurable without live data. Both prongs of PROPOSAL 003's `done-when` are
answered: a recommended default set AND the exact telemetry the smallest slice must log.

**Target:** `menno420/superbot` (hub) — Encounters cog; seams `economy_service`,
`game_xp(GAME_ENCOUNTERS)`, fishing/mining catalogue, `world_registry` #1156 (Q-0186 Lane A).

**Recommended launch defaults:** `threshold = 24 messages`, `debounce = 30s`, `cooldown = 900s`.

**Guardrails (ship all):**
- one-live-spawn-per-channel (bounds mint and prevents pile-ups);
- off-by-default + per-channel opt-in + channel allow-list (source anti-pattern);
- per-claimer cooldown enforced server-side AT the Claim callback, so a reflex-bot is still
  capped at 4 claims/hr (the sim does not model reflex-bots — enforce the cap in code);
- atomic exactly-once claim through the audited `*_workflow` seam (Q-0071);
- treat reward VALUES (coins/item rarity) as PROVISIONAL — do not scale them until the telemetry
  below yields a reward-inflation ratio.

**Telemetry the smallest slice MUST log (to close the reward-economics gap):**
- per spawn: `channel_id, spawn_ts, messages_counted_since_last_spawn, distinct_active_users_in_window`;
- per claim: `claim_ts, time_to_claim_ms, claimer_id, claimer_claims_prev_24h, reward_item_id, reward_coins`;
- per channel/day: `total_encounter_coins_minted, total_items_minted, distinct_claimers`;
- **the missing baseline:** `fishing+mining coins & items earned per active user per day` over the
  SAME window — without this the reward-inflation ratio cannot be computed.
- This enables, on live data: validating the EST traffic tiers against real messages/spawn;
  recomputing farmer-vs-honest with real claim timing; and finally computing
  `encounter_mint ÷ fishing_mining_earn`.

**Codex review:** posted on the verdict PR head (one specific question on the message-driven
claim model vs. the analytic cooldown cap); reply disposition recorded in the outbox verdict.

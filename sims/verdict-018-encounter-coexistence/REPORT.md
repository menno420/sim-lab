# REPORT — encounter coexistence: cooldown-namespace contract sweep (PROPOSAL 016)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 016** ·
> 2026-07-13T00:37:54Z · status: sim-ready (idea
> `ideas/superbot/encounter-coexistence-cooldown-contract-2026-07-13.md` @ `3ddaea8`,
> landed via idea-engine PR #279, main `d1d1b6b`).
> Parents composed: **VERDICT 001** (`sims/intake-003-wild-encounter-spawn-tuning/`,
> CHAT_ACTIVITY) and **VERDICT 008** (`sims/verdict-008-mining-grid-encounters/`,
> GRID_ROAM) — both sha256-pinned in `fixtures/MANIFEST.json` and re-verified before
> any leg runs. Shared seam: superbot-games `games/shared/encounter/interface.py` @
> `64b3371` (fixture byte-copy — zero cooldown/rate surface).
> Run: `python3 sims/verdict-018-encounter-coexistence/encounter_coexistence_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic,
parameter-swept): the pipeline's first **interaction-term verdict**. Both
surfaces' dynamics were already modeled and verdicted separately; the only new
object is the cross-surface admission rule (the contract), which is a small
deterministic state machine over the parents' own committed trace models —
composed, never re-invented. This label fills the outbox `evidence: simulation`.
The reward-VALUE axis is NOT sim-able and is declared out of scope below (the
parents' wall, restated verbatim, not re-attempted).

## PREMISE (verified live this session — the VERDICT 017 discipline)

The proposal pinned superbot `0f991a8` with the window OPEN. At intake the live
HEAD had moved to `cdb2680` — the delta `0f991a8..cdb2680` is **docs-only**
(3 files, 360 insertions, zero code: an owner direct-order pack, a
current-state note, a session card). A fresh tree scan at `cdb2680` confirms:
no Encounters cog, no activity-spawn engine, no grid-encounter slice;
`disbot/utils/mining/grid.py` still rules "v1 = free movement, NO encounters";
the only encounter code is the pure creature-game catch roll. superbot-games
live HEAD still equals the proposal's pin `64b3371`, and grep over the seam
interface for cooldown/rate/throttle/debounce still returns nothing. **The
window is OPEN and the premise HOLDS** — the namespace is still nobody's
decision; this verdict supplies it before build order does.

## What the sim MODELS

One player, two surfaces, one merged event stream, 8 h window, 5 seeds
(the parents' own SEEDS), stdlib-only:

- **Chat surface** — the VERDICT 001 channel machine, vendor-copied semantics:
  Poisson honest traffic per tier, debounced counter (24 × 30 s), one live
  spawn per channel, TTL 300 s, first off-cooldown message claims. The JOINT
  player is author 0 in the med-tier channel (honest profiles) or the lone
  paced farmer in its own channel (the V001 antifarm leg). Every OTHER author
  keeps the plain V001 900 s per-claimer clock — chat-only players, for whom
  all swept contracts are identical (disclosed).
- **Grid surface** — the VERDICT 008 per-action gate, vendor-copied semantics:
  CRN traces of (t, depth, u); an action fires iff depth ≥ 15 AND the contract
  admits AND u < 0.02.
- **The contract under sweep** (the joint player's cross-surface admission
  rule): **(a)** per-source clocks at the pinned defaults (chat 900 s from the
  player's last chat claim, grid 600 s from the last grid fire);
  **(b)** shared(c): any encounter on either surface blocks BOTH for c ∈
  {600, 900} s; **(c)** cap(K): per-source clocks AND fewer than K ∈ {4, 6, 8}
  combined encounters in the sliding (t−3600 s, t] window.
- **Joint profiles** (the interleave bracket, per the proposal): mixed-casual
  (med chat + casual roamer), mixed-deep (med chat + deep-runner), and the
  **cross-surface arbitrage farmer** (paced-spam chat farmer + `!fastmine`
  grinder, both running in parallel — each surface's cooldown dead time filled
  with the other surface's actions).
- **Regression legs FIRST** (self-check-enforced, the VERDICT 017 baseline
  discipline): the vendored chat model reproduces VERDICT 001's published
  **0.93 / 3.00 / 4.38 spawns per active-hour** and the **4.00 claims/hr**
  farmer cap; the vendored grid model reproduces VERDICT 008's
  **0.20 / 2.80 / 5.20 enc/hr** (1 h) and **0.05 / 2.95 / 4.88** (8 h) —
  each formatted exactly as the parent formatted it. Composition identities:
  the joint machine with one surface empty equals the parent machine
  event-for-event (asserted per seed, both directions).

Scoring per cell (P1–P6, committed in `grid.json` before results): wild shape
in-band, structural grid gating + solo caps, the chat per-claimer cap, the
**combined bound ≤ 4/hr** (the stricter solo ceiling, min(4, 6) — the Q-0087
never-mandatory bound the proposal names), no-material-arbitrage
(ARB_RATIO_MAX = 2.0, committed from V008's accepted 1.86 farmer-vs-honest
precedent), and no-rate-inflation vs same-horizon solo legs. **1500
self-checks** tie every cell to its analytic ceiling and abort on violation.

## What it SETTLED (the load-bearing claims — in RATE terms)

**(1) For HONEST players, coexistence under per-source clocks is negligible —
measured, with bounds.** Under contract (a) the honest mixed profiles are
identical to their solo legs (distortion 0.0000/hr): mixed-casual
0.325 chat + 0.050 grid = 0.375 combined/hr; mixed-deep 0.325 + 2.950 =
**3.275 combined/hr — under the 4/hr stricter ceiling**. Honest cross-surface
play never approaches either clock's cap, so the clocks never interact. The
proposal's negligible-effects branch is TRUE for honest players.

**(2) The cross-surface arbitrage channel is real and material — the
negligible-effects branch FAILS for the farmer, so pure per-source clocks are
rejected.** The arbitrage farmer under (a) reaches **8.875 combined
encounters/hr** (chat pinned at its verdicted 4.000 cap + grid 4.875,
i.e. 88.75% of the analytic 4+6 = 10/hr ceiling), **2.71×** the best honest
mixed profile — above the committed 2.0 materiality bound and 2.2× the
stricter solo ceiling. Both parents' farm-unprofitability proofs hold
per-surface (chat exactly 4.000, grid 4.875 ≤ 6 — self-checked); the runaway
is purely the composition, the channel neither solo sim could see.

**(3) Shared clocks either fail the bound or buy it by re-pinning a parent
default and taxing honest players.** c=600: the farmer alternates surfaces
every 600 s → **5.15 combined/hr > 4** (FAIL P4); analytic note: for a
chat-ONLY player a 600 s shared clock also admits up to 6 claims/hr,
silently re-pinning V001's verdicted 4/hr per-claimer cap upward. c=900:
passes every criterion (farmer exactly 4.000/hr) but re-pins V008's GRID_ROAM
600 s → 900 s and costs the honest mixed-deep player **0.975/hr** (grid
2.95 → 2.20, chat 0.325 → 0.100) — the largest honest tax of any passing
cell, for no additional protection.

**(4) The winner (committed rule, mechanical): C-cap-4 — per-source clocks at
BOTH verdicts' pinned defaults PLUS a combined per-player cap of 4 encounters
per sliding 3600 s.** Both parents' default sets survive unchanged
(preserves-pinned-defaults = true). The arbitrage farmer pins to **exactly
4.000 combined/hr** (the cap binds: mean 132.2 chat + 101.2 grid cap-blocks
per 8 h run), ratio **1.391** — below V008's own accepted solo ratio (1.86).
Measured honest cost, disclosed: the mixed-deep player loses **0.400/hr**
(combined 3.275 → 2.875, a 12.2% clip; grid 2.950 → 2.675, chat
0.325 → 0.200); mixed-casual is untouched (0.375/hr, never near the cap).
Combined mint share under the winner: mixed-deep 93.1% grid / 6.9% chat;
arb-farmer 56.2% grid / 43.8% chat (RATE terms only).

**(5) K is the owner's judgment knob, priced.** K=6 zeroes the honest cost
(distortion 0.0000 — mixed-deep keeps its full 3.275/hr) but concedes the
farmer 6.00 combined/hr, above the stricter solo ceiling → FAILS the
committed P4 bound (and K=8 fails P4 AND P5 at 7.85/hr, ratio 2.40). If the
owner ever relaxes the Q-0087 reading from min(4, 6) to something looser,
K=6 is the measured next notch — the proposal explicitly carves this cap
parameter to the owner; the committed rule recommends K=4.

## What it did NOT settle

- **Reward VALUE — the parents' wall, restated verbatim:** "no live
  fishing/mining earn-rate baseline exists, so loot values stay provisional
  and the slice must log the same named telemetry." Every mint number above
  is RATE/fraction-only; whether 4/hr combined is *lucrative* is unmeasurable
  until the parents' named earn-rate baseline telemetry lands.
- **Real interleaving.** How much a real player mixes chat and mining is
  unknown; mixed-casual / mixed-deep / arbitrage-optimal BRACKET it, and the
  conclusions are reported as the bracket, not a point. The honest-cost figure
  (0.400/hr at K=4) rides on the stylized mixed-deep interleave.
- **The third trigger.** EXPLORE_ACTION (superbot-games quest beats) inherits
  the namespace rule + combined cap BY CONTRACT, not by this sweep — its
  pacing is lane-pinned; adding it to the combined window is the build's
  contract obligation, not a measured cell here.
- **Multi-channel chat.** The chat surface is V001's single opted-in channel;
  a player claiming across many channels multiplies the CHAT side only if the
  build scopes the chat clock per-channel — the row below scopes ALL clocks
  per-player, which the combined cap enforces regardless.
- **Reflex-claim bots and real traffic tiers** — the parents' own disclosed
  limits, inherited unchanged (the per-account caps are the binding guarantee,
  and they are what the contract row enforces).

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The two surface models are the parents' own verdicted fixtures, reproduced
exactly (regression legs) — any gap they carry is the gap two finalized
verdicts already carry. New abstractions: the interleave bracket (honest
profiles are stylized; the ARBITRAGE result cannot be flipped by it — the
farmer profile is the optimizing adversary, and its 8.875/hr rides on both
parents' committed adversary traces) and instant encounter resolution (a live
resolution that occupies the player would LOWER all rates — conservative).
The winner's honest-cost number (0.400/hr) IS interleave-sensitive — flagged,
not asserted robust. No plausible gap un-fails (a): its failure is
analytic-backed (two independent clocks admit 4+6/hr by construction).

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **1500 self-checks, 0 failed**, exit-coded: sha256 manifest pins on
the seam fixture AND both parent files verified before any leg; exact
regression to ALL ten published parent numbers; composition identities to
both parent machines per seed; structural gating (0 grid fires below depth);
per-cell analytic combined ceilings; per-source clock spacing / shared-clock
spacing audits; an **independent sliding-window re-audit** of the cap cells
(recomputed without the deque); 3 expect_reject negatives (a contract that
fails open must reject); full-sweep determinism with CRN caches cleared.
Seeds: the parents' 5, CRN-cached. Cherry-picking: the FULL 6 × 3 table is
printed and committed, failures scored first-class; the winner comes from the
rule committed in `grid.json` before results existed.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The rejection of (a) is margin-free: 8.875/hr vs a 4.0 bound (2.2×) and 2.71
vs a 2.0 ratio bound — no seed, tolerance, or profile tweak closes that. The
winner's PASS is not knife-edge on the farmer side (it pins to the cap
exactly, by construction — the cap is analytic) but its honest cost is a
frontier trade: K=4 costs mixed-deep 12.2%, K=6 costs 0% and fails the bound
— there is no swept K that does both, and the report says so rather than
smoothing it. B-shared-900 passing confirms the bound is achievable two ways;
the winner dominates it on every committed axis (defaults survive, less than
half the honest cost, same farmer ceiling).

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, fixed seeds, no network / git /
wall clock / hash(); stdout AND `results.json` byte-identical across THREE
complete process runs by external `diff`; in-process full-sweep determinism
check with caches cleared. Runtime < 1 s.

**5. "LIMITS? what this evidence does NOT show."**
It does not show reward VALUE (no earn-rate baseline — the parents' wall,
restated, not moved); does not measure real interleaving (bracketed); does
not sweep EXPLORE_ACTION (inherits by contract); does not model multi-channel
chat, reflex bots, or resolution content; and the sliding-window cap's
server-side implementation (per-player, across all triggers, atomic with the
claim/fire) is an engineering obligation the row states, not a thing this sim
can prove about unwritten code.

## EVIDENCE STRENGTH: **moderate** — gate PASS

Gates 2 and 4 are strong (exact parent regression, 1500 checks, byte-identity
across runs); gate 3 is decisive for the rejection of (a) and honest about
the winner's K trade-off; gate 1 carries the interleave bracket, disclosed.
Short of strong because the honest-cost figure is interleave-model-dependent
and the profiles are stylized (the parents' own limitation, inherited). Well
above hypothesis-only. Under the README rule the sim **PASSES** the gate for
every claim it makes; the VALUE half was never in scope.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `approve`** — the proposal's approve-consequence: ONE measured
  contract row for the shared engine, handed BEFORE the first consumer build
  fixes the namespace by accident. (The alternative branch — "coexistence
  effects negligible, proceed solo-tuned" — is measured FALSE for the
  adversary: 8.875/hr, 2.71× honest; and TRUE for honest players, which is
  exactly why the row can keep both parents' defaults.)
- **THE CONTRACT ROW (for superbot-games' CONTRACT.md slice and the Q-0186
  Encounters-cog build):**
  - **Namespace: PER-SOURCE clocks, keyed (player_id, trigger)** — each
    trigger keeps its own verdicted cooldown: CHAT_ACTIVITY 900 s per-claimer
    (VERDICT 001), GRID_ROAM 600 s per-player (VERDICT 008). **Both verdicts'
    pinned default sets survive coexistence unchanged — nothing re-pins.**
  - **Combined-rate guardrail (MANDATORY, the row's second half): at most
    K = 4 encounters per player per sliding 3600 s across ALL triggers**
    (the stricter solo ceiling, the Q-0087 never-mandatory bound). Enforced
    server-side at the same point the per-source clock is checked, atomic
    with the claim/fire (the parents' reflex-bot guardrail, extended to the
    combined window). Without it, per-source clocks alone hand a
    cross-surface farmer 8.875/hr — 2.2× the bound.
  - **EXPLORE_ACTION inherits this rule by contract, not by this sweep:**
    per-source clock lane-pinned as its own balance sim rules; its fires
    count into the SAME combined K-window.
  - **K is the owner's carved judgment knob, priced:** K=4 costs the honest
    mixed-deep player a measured 0.400/hr (12.2% clip); K=6 zeroes that cost
    but concedes 6/hr combined (above the stricter ceiling — fails the
    committed bound). Recommended K=4; re-run this sim on any K or clock
    retune (one command, < 1 s).
- **Runner-up, honestly characterized:** B-shared-900 (one shared 900 s
  clock) also bounds the farmer at 4.000/hr but re-pins V008's 600 s default
  and costs honest mixed-deep 0.975/hr — dominated by the winner on every
  committed axis. B-shared-600 and K ∈ {6, 8} fail the committed bound
  (5.15 / 6.00 / 7.85 combined/hr).
- **Telemetry (the parents' named lists EXTEND, the wall stays walled):** per
  player per day combined_encounters_all_surfaces (+ per-trigger breakdown);
  per encounter: trigger namespace + cooldown state at fire (per-source
  remaining, combined-window count); per player per day cooldown_block_events
  split own-clock vs combined-cap; combined encounter-mint share vs each
  surface's solo mint — in RATE/fraction terms, because (verbatim) "no live
  fishing/mining earn-rate baseline exists, so loot values stay provisional
  and the slice must log the same named telemetry."
- **Not re-opened:** both parents' in-band solo defaults (24 / 30 s / 900 s;
  15 / 0.02 / 600 s) — no coexistence cell named a breach of either solo
  shape, so nothing re-pins (P6 held everywhere; the only honest-rate
  movements are DROPS under the cap/shared cells, disclosed above).
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015/V016/V017 slice boundary, with header timestamps from
live `date -u` at append time. -->

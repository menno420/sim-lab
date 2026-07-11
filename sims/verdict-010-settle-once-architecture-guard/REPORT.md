# REPORT — settle-once-architecture-guard (VERDICT 010)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: PROPOSAL 009 @ `menno420/idea-engine` `control/outbox.md` `05601ba3ef751e794b610b2dbc84fe8a30398dd0` (status: sim-ready).
> Canonical idea doc: `menno420/superbot` `docs/ideas/settle-once-architecture-guard-2026-06-24.md` @ `8214200aa0c00dda4156748617c9482dadc4277a`.
> Corpus reconstructed from superbot @ `1eeedb03b8a29992e438544e5e3c0e1ef51d35b0` / superbot-next @ `4024624d3258aa982bac466acb16a51b17bbc6df` + incident docs (BUG-0013 bug-book; PRs #1444 / #1445 / #1781; superbot-next #133).
> Run: `python3 sims/verdict-010-settle-once-architecture-guard/settle_once_sim.py`

## METHOD LABEL: NUMERIC SIMULATION / reconstruction (rung 1–2)

The class is a concurrency invariant (a terminal effect that must fire exactly once), so its dynamics are fully modelable: each instance is reconstructed as a minimal replayable check-then-act race, and each candidate guard is a minimal enforcement layer swept over EVERY order-preserving interleaving. Deterministic and RNG-free — the interleaving sweep is exhaustive, not sampled, so it is stronger than multi-seed stability. This is the cheapest adequate evidence: the catch/miss of a guard is a structural fact (does the fence have something to fence, and does the static checker force it), not a live-timing measurement.

## What it MODELS

A settlement site runs a terminal effect (payout / result-post / record-write) that must happen exactly once per match. A **double-settlement** = the terminal runs twice. Two duplication paths reach it (timeout-races-final, double-event, two-racing-stands, retry); each is modeled as two attempts doing a non-atomic check-then-act over shared state. Without an atomic fence, the interleaving `[A.read, B.read, A.act, B.act]` lets both act → double. A guard makes the claim / consume / flag a single indivisible compare-and-set, so exactly one attempt wins across every interleaving.

The six instances, by **leg type** (the load-bearing discriminator):

| # | instance | repo · path | leg | why the double fired |
|---|---|---|---|---|
| 1 | BUG-0013 challenge-view timeout | superbot · `disbot/cogs/deathmatch_cog.py:_ChallengeView.on_timeout` | no_row | 30s timer never `stop()`ed, `on_timeout` had no `_resolved` guard → re-posts terminal |
| 2 | RPS PvP result-embed (#1444) | superbot · `disbot/views/rps/pvp_play.py:_resolve` | no_row | money leg idempotent; the DOUBLE was the result-embed post |
| 3 | deathmatch bot-duel (#1444) | superbot · `disbot/views/games/deathmatch_panel.py:_finish` | no_row | bespoke `is_over` boolean; `_finish` reachable from `on_timeout` |
| 4 | blackjack PvP (#1445) | superbot · `disbot/views/blackjack/pvp_view.py:_resolve_pvp` | escrow | module-level settle; `pop(key, None)` didn't short-circuit on missing key |
| 5 | Gate-V Arm-D W/L double-write (#1781) | superbot · `disbot/cogs/deathmatch_cog.py:_DuelView → update_deathmatch` | no_row | wager escrow idempotent; the gap was the un-guarded W/L leaderboard record-write |
| 6 | #133 tournament consolation | superbot-next · `sb/domain/blackjack/ops.py:_record_tournament_payout` | no_row | free/consolation leg has NO escrow rows to consume → two racing final stands re-pay |

Three candidate contracts (from the proposal, plus the roots-fix variant the proposal's own question implies):

- **(a) caller-side atomic claim** — superbot's Rule 6 shape / `SettleOnceMixin.claim_settlement()`. Fences every leg-type (claims regardless of rows), but is **opt-in**: caught only where a static checker forces the claim. As shipped, `scripts/check_consistency.py:1151` registers the rule with `roots=("views/","services/")`.
- **(a)+roots-fix** — the same, with `cogs/` added to the scanned roots (the one-line widening).
- **(b) row-consumption alone** — superbot-next's D-0042 `once()` fence + FOR-UPDATE deletion count. Intrinsic to the payout query (can't be forgotten), but structurally can only fence legs that HAVE consumable rows.
- **(c) row-consumption + mandated check-and-set for no-row legs** — the #133 fix generalized: escrow legs settle by atomic row-delete; no-row legs settle by an atomic check-and-set on a dedicated settle-flag row (the winning delete pays, the loser deletes zero rows).

## What it SETTLED (the load-bearing claims)

**The catch matrix** (rows=contracts, cols=instances; PREV=prevented-statically, RUN=caught-at-runtime, MISS=missed):

```
contract                                          1     2     3     4     5     6    catch  miss
(a) caller-side atomic claim                      MISS  PREV  PREV  PREV  MISS  MISS   3/6    3
(a)+roots-fix (cogs/ added)                       PREV  PREV  PREV  PREV  PREV  MISS   5/6    1
(b) row-consumption alone                         MISS  MISS  MISS  RUN   MISS  MISS   1/6    5
(c) row-consumption + check-and-set no-row legs   PREV  PREV  PREV  RUN   PREV  PREV   6/6    0   ← winner
```

1. **(c) is the only contract that catches the full corpus** — 6/6, 0 missed. Its invariant: *every money-moving op leg must settle exactly once, enforced by EITHER atomic consumption of ≥1 escrow row OR, for a leg with no consumable escrow row, an atomic check-and-set on a dedicated settle-flag row; the terminal effect runs only for the atomic winner.*
2. **(b) row-consumption alone misses 5/6** — it fences only the one escrow leg (instance 4); every no-row leg (result-posts 1/2/3, the W/L record-write 5, the #133 consolation 6) has nothing to consume. This is not a seed artifact: the miss holds across all interleavings and the retry-3 variant. #133 is the live proof — the free/consolation leg (`sb/domain/blackjack/ops.py:587-589`: "the free branch has no escrow rows to consume") breached D-0042 exactly here.
3. **(a) caller-side claim is opt-in, so its coverage = its static scope.** As shipped (`roots=("views/","services/")`) it prevents the three views/ instances but MISSES the two cogs/ instances and the cross-tree #133 → 3/6. The corpus is dominated by no-row terminals, which (a) *can* fence at runtime if present — but the incidents recurred precisely because the claim was omitted where the checker didn't force it.
4. **The registry-roots drift changes instance-5's row, and it is STILL LIVE.** Measured on superbot @1eeedb0: the Rule 6 *registration* at `scripts/check_consistency.py:1151` passes `roots=("views/","services/")`, while the rule function's docstring + default arg (`:984`, `:1007`) claim `views/ + services/ + cogs/` (the "2026-07-07 widening"). The #1781 widening reached the docstring/default but NOT the registration tuple that governs the scan — so cogs/ is silently excluded today, and 8 cogs/ guard-adopters sit outside the scanned roots (`rg SettleOnceMixin|claim_settlement|rearm_settlement disbot/` → 8 lines in cogs/). Adding `cogs/` flips instances 1 and 5 from MISS → PREV → **(a)+roots-fix = 5/6** (still misses cross-tree #133). This is the evidence for superbot's lane-side one-liner: `check_consistency.py:1151` `roots += ("cogs/",)`.

**False-positive column (mandatory — a guard that blocks legit settlements "catches" everything trivially):**

- Legit SINGLE settlement runs exactly once under (a), (c), and (b)-on-escrow — no false positive.
- **(b) strictly enforced false-positives a legit no-row settle**: a mandated "≥1 row consumed" rejects a valid free-consolation payout (which has zero rows) → 0 terminals. So (b) both misses doubles AND cannot express legit no-row settlements.
- **(a) and (c) both need explicit re-arm to avoid false-positiving legit MULTI-STAGE settlement**: a naive single-claim/single-flag blocks the second legitimate stage (tournament semifinal → final) → 1 of 2 legit terminals. `rearm_settlement()` (the #1781 sibling find — RPS `check_tournament_progress` semifinal free-reward race) clears the flag between stages → 2 of 2. This is the winner's one mandatory guardrail.

**Variant / generalization sweep:** the catch/miss outcome is invariant across the exhaustive interleaving set (6 orderings for 2 attempts, 90 for retry-3), across attempt-reordering, and across the retry-3 duplication variant. Fences give exactly-once in ALL interleavings for supported legs; the no-guard baseline doubles in ≥1 interleaving for every instance. (b)'s miss on no-row legs is structural in every interleaving.

**Recommended build spec (for superbot-next, warn-first per Q-0105):** a `tools/check_*` script over the K7 op grammar (D-0010) that requires every money-moving op leg to declare one of `{consumes ≥1 escrow row, check-and-set on a settle-flag row}`; a leg that does neither is a WARN. The static rule's scope must enumerate EVERY money-moving root (do not repeat the cogs/ drift), and the flag primitive must expose explicit re-arm for legitimate multi-stage settlement. superbot-next already ships the seam (22 `tools/check_*` scripts) but none enforce settle-once today; the #133 fix (`tournament_flag.clear_active()` atomic DELETE-and-count + `state.settled` render twin) is the reference implementation of the no-row leg fence.

## What it did NOT settle

- **The LIVE false-positive count from actually running the checkers** (the proposal's literal ask) is **NOT MEASURED** — faithfully executing superbot's `check_consistency.py` AST rule or a superbot-next `check_*` over K7 legs needs their parser/config, not grep. The grep figures reported are enforcement-surface proxies, not checker output (the disbot/ 99-match `_resolve|_finish|...` count is an over-count from name collisions — an upper bound, not a site count). "Not measured" beats invention.
- Whether contract (c)'s static rule, once built, parses every real op leg correctly — a build-and-measure task for the superbot-next lane.
- Absolute concurrency probabilities in the live async runtime — the model proves double-settlement is *possible* across all interleavings, not its live *rate*.
- Any settlement site outside the six documented instances — the corpus is those six only; the 7th related find (RPS semifinal free-reward race) is used only as evidence for the re-arm guardrail, not as a corpus member.

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

The model abstracts away the real DB, async runtime, and Discord view lifecycle. What it captures faithfully is the *structural* determinant of catch/miss: leg-type (escrow vs no-row) × fence-mechanism × static-enforcement scope. Because catch/miss is structural (does the fence have something to fence; does the checker force it), not a timing outcome, abstracting the real scheduler cannot flip it — the exhaustive interleaving sweep already covers every ordering a real scheduler could produce for the modeled check-then-act. The one gap that COULD flip a cell is leg-type misclassification (a "no-row" leg that actually has consumable rows, or vice versa); this is mitigated by grounding each leg-type in the incident code (#133 "no escrow rows to consume" `ops.py:587-589`; the Gate-V gap is a leaderboard record-write via `update_deathmatch`, not an escrow consume). The registry-roots scope is a measured code fact (`check_consistency.py:1151`), not a modeling assumption.

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

72 self-checks pass, 0 fail. The battery caught a real model bug before finalization: the escrow leg initially seeded `rows = n_attempts`, letting each racer consume its own row — the `rowconsume/escrow` exactly-once check fired (got 2, want 1) and the model was corrected to a single shared escrow pot. No seeded luck: the model is RNG-free and the interleaving sweep is EXHAUSTIVE (6 orderings for 2 attempts, 90 for retry-3), stronger than sampling; seed-invariance across `SEEDS=[11,23,42,101,2027]` is asserted and trivial (no RNG). No cherry-picking: the FULL 4×6 matrix is reported, not the winner's row, and the false-positive column is mandatory.

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

Yes. The catch/miss outcome is invariant across every interleaving, across attempt-reordering, and across the retry-3 duplication variant. Fences give exactly-once in ALL interleavings for supported legs; the no-guard baseline doubles in ≥1 interleaving for every instance; (b)'s structural miss on no-row legs holds in every interleaving. The winner (c) survives all variants at 0 missed.

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Committed. One command: `python3 sims/verdict-010-settle-once-architecture-guard/settle_once_sim.py`. Byte-identical results across re-run (determinism self-check). Exit 0 iff all 72 self-checks pass.

**5. LIMITS?** *"what this evidence does NOT show"*

See "What it did NOT settle" — the live checker false-positive count is not measured (grep proxies only, an over-count upper bound); the built (c) checker's real-leg parse fidelity is unproven; absolute live concurrency rates are out of scope; the corpus is the six documented instances only. This evidence settles which guard CONTRACT is complete over the known class and its variants; it does not settle the checker's implementation on the live trees.

## EVIDENCE STRENGTH: moderate-strong — gate PASS

Passes all five gate questions. Strong on UNCORRUPTED (72 self-checks, one real bug caught), ROBUST (exhaustive sweep), and REPRODUCIBLE (one command, byte-identical). Bounded on COMPARABLE (structural model, not live runtime) and on the unmeasured live false-positive count — both honestly labelled, neither flips the contract choice.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** approve — build the settle-once guard; adopt contract **(c)**.
- **Target:** superbot-next (owns the `tools/check_*` CI seam, the K7 op grammar D-0010, the D-0042 wager-lane discipline). Lane-side one-liner for superbot: `scripts/check_consistency.py:1151` `roots += ("cogs/",)` (fix the still-live registry-roots drift so Rule 6 scans the cog layer where `_DuelView` and the leaderboard sinks live).
- **Recommended implementation:** contract (c) — invariant: every money-moving op leg settles exactly once via `{atomic consume ≥1 escrow row}` OR `{atomic check-and-set on a settle-flag row}`; static rule (warn-first, Q-0105): a `tools/check_*` over the K7 op grammar requiring one of the two fences on every money-moving leg.
- **Named changes / guardrails:** (1) the static rule's scope must enumerate EVERY money-moving root — the cogs/ drift is the failure mode to avoid; (2) the settle-flag primitive must expose explicit re-arm (`rearm_settlement`) for legitimate multi-stage settlement, else it false-positives tournament progression; (3) reference implementation is the #133 fix (`tournament_flag.clear_active()` + `state.settled`).
- **Codex review:** reply: pending (OA-002 Codex usage-capped).

<!-- Outbox verdict-grammar block (emitted to control/outbox.md on finalization):
VERDICT 010 · <ISO8601> · status: finalized
target: superbot-next (build the tools/check_* settle-once fence); superbot (lane-side one-liner: check_consistency.py:1151 roots += cogs/)
idea: PROPOSAL 009 @ idea-engine 05601ba3ef751e794b610b2dbc84fe8a30398dd0
verdict: approve
evidence: simulation
report: sims/verdict-010-settle-once-architecture-guard/ · run: python3 sims/verdict-010-settle-once-architecture-guard/settle_once_sim.py
recommendation: adopt contract (c) row-consumption + mandated check-and-set for no-row legs (6/6, 0 missed, 0 false-positive given re-arm); (b) alone misses 5/6; (a) opt-in misses cogs/ + cross-tree
codex: PR #<n> comment · pending
gate: PASS
-->

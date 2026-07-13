# Session — VERDICT 018 — encounter coexistence: cooldown-namespace contract sweep (idea-engine PROPOSAL 016)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-018 slice-worker session
> Objective: settle idea-engine PROPOSAL 016 (control/outbox.md @ 2026-07-13T00:37:54Z, sim-ready; idea ideas/superbot/encounter-coexistence-cooldown-contract-2026-07-13.md @ 3ddaea8, landed via idea-engine PR #279) — compose the two verdicted player models (VERDICT 001 channel-activity tiers + paced-spam farmer; VERDICT 008 grid playstyles) into single-player joint profiles (chat-only and grid-only regression legs FIRST, each reproducing its verdict's solo headline rates, then mixed-casual, mixed-deep, and a cross-surface arbitrage farmer) and sweep the cooldown-namespace contract — (a) per-source clocks at the pinned defaults (CHAT_ACTIVITY 900 s / GRID_ROAM 600 s), (b) one shared per-player clock c ∈ {600, 900} s, (c) per-source clocks plus a combined per-player hourly cap K ∈ {4, 6, 8} — scoring every cell against BOTH verdicts' pinned shapes simultaneously, bounding the combined per-player interruption rate at the stricter solo ceiling (Q-0087), and measuring whether cross-surface cooldown arbitrage buys the farmer a combined encounter-rate yield materially above the honest mixed profiles' — ending in ONE recommended contract row (cooldown namespace + combined-rate guardrail + which pinned defaults survive vs re-pin) for the shared engine before the first consumer build fixes it by accident.

## What happened

Built `sims/verdict-018-encounter-coexistence/` — a stdlib-only NUMERIC
SIMULATION (rung 1), the pipeline's first interaction-term verdict: the two
verdicted trace models vendor-copied (parent sim files sha256-pinned,
re-verified before any leg) and composed through a cross-surface contract
state machine over one merged event stream. Premise verified live at intake:
superbot HEAD moved 0f991a8 → cdb2680 on a docs-only delta (3 files, 360
insertions, zero code) — no Encounters cog, no spawn engine, no
grid-encounter slice anywhere in the tree; superbot-games seam unchanged @
64b3371 with zero cooldown/rate surface. The coexistence window is OPEN; the
premise HOLDS.

**Run output summary:** `SELF-CHECKS: 1500 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across three process runs (external
diff), < 1 s. Regression legs all EXACT (V001 0.93/3.00/4.38 spawns/hr +
farmer 4.00 claims/hr; V008 0.20/2.80/5.20 enc/hr @1 h and 0.05/2.95/4.88
@8 h) plus per-seed composition identities to both parent machines. Honest
coexistence under per-source clocks: negligible (distortion 0.0000/hr;
mixed-deep 3.275 combined/hr < the 4/hr stricter ceiling). The arbitrage
channel: REAL — 8.875 combined/hr under pure per-source (2.71× honest), each
surface's own cap intact; the runaway is purely the composition. **Verdict:
approve** (evidence: simulation, gate PASS, strength moderate) — the contract
row: per-source namespace keyed (player_id, trigger) at BOTH parents' pinned
defaults + MANDATORY combined per-player cap K=4 per sliding 3600 s
(winner C-cap-4 by the grid.json rule committed before results; farmer pins
to exactly 4.000/hr, ratio 1.391; honest cost disclosed 0.400/hr on
mixed-deep). Runner-up B-shared-900 dominated. K carved to the owner, priced.

Slice boundary this cycle (the V015/V016/V017 precedent): this session
carries the INTAKE 016 and VERDICT 018 control/ appends itself;
control/status.md stays coordinator-only and is untouched; control/inbox.md
untouched (manager-order file). No @codex step — suspended per the outbox
codex-line escalation @ dedc12e. No claim file — the V017 session filed none;
precedent mirrored.

## Run command

```
python3 sims/verdict-018-encounter-coexistence/encounter_coexistence_sim.py
```

## 💡 Session idea

When two finalized verdicts share a seam, the cheapest next verdict is the
INTERACTION TERM run on their own committed fixtures: this sweep re-invented
nothing — it vendor-copied two parent trace models, proved byte-fidelity by
exact regression to every published headline number plus per-seed
composition identities (joint machine with one surface empty == the parent
machine event-for-event), and then the only genuinely new code was the
~60-line contract state machine actually under test. That fidelity floor is
what let a 6-cell sweep settle a 2.5× design fork in under a second: the
expensive thing was never the simulation, it was trusting the composition —
and regression + composition identities buy that trust mechanically. Rule of
thumb for future intakes: if a proposal names two committed sims as parents,
budget the sim as (vendored parents + identity checks + the new seam only),
and treat any urge to re-model a parent as scope creep.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-017-t10-cost-curve.md`: complete, honest, and
its exports are adopted here directly. (1) Its baseline-leg discipline (B0
must reproduce the prior verdict EXACTLY before any new cell counts) is this
sim's regression-legs-first rule, extended to TWO parents and hardened with
composition identities. (2) Its 💡 (sweep the mechanic's SHAPE, not just its
numbers) maps here as the contract FAMILY axis (per-source / shared / capped)
— and again the shape axis was the decisive one: no K value inside family (a)
exists, the family itself was the fork. (3) Its slice boundary (the verdict
session carries the INTAKE + VERDICT appends; status.md coordinator-only,
inbox untouched) is honored as-is. One deviation, disclosed: 017 pushed
born-red then flipped complete in a follow-up commit on the same PR; this
session lands born-red card and complete flip in one push (first commit is
still the in-progress card) because `bootstrap.py check --strict` fails on an
in-progress newest card and the strict-gate-before-every-push rule binds
harder than the two-push choreography.

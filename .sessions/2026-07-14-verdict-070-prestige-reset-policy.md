# Session — VERDICT 070 — Prestige reset-policy optimality: does superbot-idle's committed "optimal-play" greedy reset loop survive the milestone fold the engine now ships? (idea-engine PROPOSAL 059, ORDER 003 GAME-MECHANICS rotation slot, round 11)

> **Status:** complete
> 📊 Model: fable-family · 2026-07-14 · verdict-070 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 059 (`## PROPOSAL 059 · 2026-07-14T05:19:21Z · status: sim-ready`, landed via idea-engine PR #402 → main 99ce912; reservation this slice: idea-engine claim file `control/claims/claude-verdict-070-prestige-reset-policy.md` landed via idea-engine PR #403 → main db5074e; numbering INTAKE = proposal number, PROPOSAL 059 → VERDICT 070 per the established +11 offset map P050→V061 … P058→V069) — price the policy-optimality of superbot-idle's committed greedy reset loop at the HEAD multiplier fold (source pin superbot-idle @ `5ddd5a230d4a6504c06b52805cba5dc8b3276b44`): a pre-registered, fully deterministic 15-policy grid at the SIM-PINNED constants {60, 115/100, 25, 100000, 100000, 10} + milestone ladders {10^3/10^5/10^7, 1/5/25, +5%}, exact integer arithmetic throughout, horizon H = 1,209,600 s (H/2 reporting leg), policy family Π = never · fixed-m (m ∈ {1,2,4,9,16,25,100}; fixed-1 IS the committed greedy policy) · hybrid-k (one patient 10^7 run at the first reset boundary with P ≥ k, k ∈ {0,100,1000,10000}) · cooldown-τ (τ ∈ {60,300,3600} — the lane's flagged cap, priced), boundary order pinned credit → award milestones → buy-while-affordable → award → reset check → award. Twin-arm: Arm A seedless exact event scheduling (decision), Arm B independently-written per-second evaluator (must reproduce every total EXACTLY), Arm R seeded REPORTING-ONLY probes (seed 20261373: 12 hybrid triggers randrange(1,60001) + 6 cooldowns randrange(30,7201); stability 20261374: 4+2; presentation shuffle 20261375; aux 20261376 NEVER read). Decision rule pre-registered, applied IN ORDER: REJECT FIRST (∃ π ∈ Π \ {fixed-1}: 100·total(π) ≥ 101·total(fixed-1), exact big-int, both arms) → INVALID (F1 engine-fold identities · F2 V038 cross-pins · F3 milestones-OFF contrast monotonicity · F4 conservation · F5 hand world · F6 battery — report, no ruling) → APPROVE (∀ π: 100·total(π) ≤ 99·total(fixed-1) AND total(fixed-1) ≥ 2·total(never)) → NULL (parity-straddle / mechanism-miss / horizon-conditional / surviving twin disagreement — named axes). Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT via hybrid-1000. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-070-prestige-reset-policy/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 059 + VERDICT 070 appended to sim-lab `control/outbox.md` only). This card held the substrate gate red deliberately until this final flip (the born-red discipline — that red was the ONLY red on this branch).

## What happened

Built `sims/verdict-070-prestige-reset-policy/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 059 block / idea doc @
idea-engine 99ce912; fixture-level choices C1–C9 — the strictly-before-H
horizon-boundary convention, the event set, the hybrid trigger semantics,
the argmax-beater mechanism-miss parse, the sentinel/shuffle/aux
conventions, the reset-series hash serialization, exact-integer
serialization, every-boundary conservation, the both-arms REJECT parse —
all disclosed IN the fixture BEFORE the runner existed). Git trail (PR
#131): 90be6e7 (born-red card) → 76bae2f (fixtures) → 861ee9d (runner
prestige_reset_policy_sim.py + accepted run: results.json, run-stdout.txt,
README.md, REPORT.md) → 38a0bef (INTAKE 059 + VERDICT 070 ledger) → this
flip. Reservation: idea-engine claim PR #403 (claim-first) + born-red card
first commit + PR #131 READY; `VERDICT 070`/`INTAKE 059` grepped clean at
session start (09782df) and re-grepped clean at 49833d0 immediately before
the ledger append (main moved mid-session on PR #130, a manager inbox
relay only; origin/main merged INTO this branch, never rebased).

**Run:** `SELF-CHECKS: 72 passed, 0 failed`, exit 0, ~67 s/run; stdout +
results.json byte-identical across two full process runs by external
sha256 (run-stdout 0292219965..., results 732246f0...); CPython 3.11
pinned, asserted; seeds 20261373/74/75 the ONLY RNGs constructed (pinned
order), aux 20261376 never read (asserted); randrange sentinels exact at
12+6 and 4+2; twin evaluators exact-equal on EVERY total of EVERY leg
(ON@H, OFF@H, ON@H/2, all 24 Arm-R probes); F1–F6 all green.

**Ruling: REJECT** — the registered clause fires with an ≈ 8× margin over
its line: hybrid-1000 (one patient 10^7 run at P ≥ 1000, then greedy)
totals 27,411,200,535 vs greedy's 25,386,048,335 = 1.079774× ≥ 101/100;
hybrid-10000 a second cell above the line (1.058479). Attribution holds:
the same beater LOSES with milestones OFF (0.978933) — the beat is exactly
the lifetime-3 (+5% forever) rung the greedy loop can never earn and
tools/simulate.py folds zero of. The grind half of the docstring claim is
simultaneously CONFIRMED: greedy = 1024.97× never-reset — the committed
SCHEDULE is what fails, not reset-and-grow. Falsifiability behaved as
registered (hybrid-100 below parity at 0.983833; hybrid-0 collapses;
every fixed-m ≥ 2 and cooldown loses); the beater clears the line at H/2
too (1.037531). All 15 drafter-disclosed totals reproduced from scratch
digit-for-digit (never gated). Named anomalies, first-class: (1) the
disclosed F2 ±1 is now diagnosed EXACTLY — a greedy-OFF reset lands
exactly at t = H = 1,209,600, and the pinned convention (C1) excludes it
(80,795) while the vendored harness's t+dt>horizon convention includes it
(80,796); (2) the cooldown price is strongly horizon-dependent —
cooldown-60 is 0.994643× greedy at H/2 but 0.600232× at H; (3)
hybrid-10000 at H/2 equals greedy EXACTLY (the detour never fires by day
7); (4) late-game cadence bottoms at 2 s/reset in the shipped fold
(day-14 bin 43,200) and the Π-best keeps the same late cadence — the
beater banks lifetime-3, it does not fix the spam.

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-069-rubric-weight-robustness.md`): V069's
closing observation — that the V068/V069 card structure (git-trail
sentence, run block, per-conjunct ruling block) "is becoming the de-facto
verdict-card template and could be promoted to one" — held for a third
consecutive session: this card reused the structure unchanged and the only
friction was self-imposed prose length, which is evidence the promotion to
a committed template (with the section headings fixed and the prose
budgeted) is now cheaper than the next reuse.

💡 **Session idea (genuine, this session):** the H/2 reporting leg exposed
a pricing trap the headline table hides — a policy cap's cost is strongly
HORIZON-DEPENDENT (cooldown-60 = 0.9946× greedy at 7 days but 0.6002× at
14; meanwhile hybrid-10000 = exactly 1.0× at 7 days and 1.0585× at 14).
Candidate instrument rule for any future policy-price or cap-price table:
every price ships as a (H/2, H) PAIR with a one-line monotonicity
direction, because a cap that looks free at the evaluation horizon can be
ruinous at a longer one and vice versa — and the pair costs one extra
column, not one extra sim (the H/2 leg already exists in the standing
battery).

📊 Model: fable-family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).

# Session — VERDICT 066 — Badge saturation: is the mineverse achievement catalog's Coin Magnate line (`COIN_MAGNATE_THRESHOLD = 10_000`) a wealth badge or an account-age badge under the hub's own committed daily faucet? (idea-engine PROPOSAL 055, ORDER 003 GAME-MECHANICS rotation slot, round 10)

> **Status:** complete
> 📊 Model: Claude Fable (family) · 2026-07-14 · verdict-066 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 055 (`## PROPOSAL 055 · 2026-07-14T02:25:10Z · status: sim-ready`, landed via idea-engine PR #385 → main 18f31718b20cb1c5f3fad6cb2767babe124c691a; numbering INTAKE = proposal number, PROPOSAL 055 → VERDICT 066 per the established P050→V061 / P051→V062 / P052→V063 / P053→V064 offset map, P054→V065 in flight on PR #123) — price the World flagship's showcase wealth badge, `COIN_MAGNATE_THRESHOLD = 10_000` (`server/views.py::earned_achievements` @ superbot-mineverse `b983291cd9fc4b0d037a25a139c7ef5991e1236f`, both calibration comments quoted verbatim in the fixture), against the hub's committed daily faucet `_DAILY_TIERS` @ superbot `34775943da081dd0a1dc7cf858efc0889726fcf6` (six integer-uniform tiers, weights/100, E[!daily] = 169201/100 exact, one claim per `_DAILY_COOLDOWN = 86400` s), on the shared wallet the read contract wires the badge to (`coins` "mutated only by `economy_service`", docs/mining-data-contract.md @ b983291), per the idea doc `ideas/superbot-mineverse/badge-saturation-coin-magnate-2026-07-14.md` @ idea-engine main 18f3171. Pinned player model (invented-but-pinned, every width a grid axis or disclosed pin): fresh wallet 0; per day claim w.p. p then spend floor(σ·claim) same day (net = claim − floor(σ·claim), savings never spent — direction stated); T = first day wallet ≥ 10,000; season H = 90 days; grid p ∈ {1, 1/2, 1/4, 1/10} × σ ∈ {0, 1/2, 9/10} with DECISION world σ = 1/2; σ ∈ {0, 9/10} and H ∈ {30, 180} reporting-only; non-daily faucets excluded (understates income — REJECT-robust, direction stated). Arm A = DECISION (seedless exact absorbing DP over integer wallet states 0..9999, ≥ 10,000 absorbing, run-decomposed prefix-sum transitions, every P(T ≤ n) an exact Fraction over denominator (2·10^6)^n — p on 20, pmf on 10^5; alone decision-bearing). Arm S = robustness (seeded MC N = 20,000/decision-cell, `random.Random(20261357)`, pinned draw order: claim-Bernoulli then tier-then-uniform value exactly as `economy_helpers._pick_daily` draws it — `random.choices` tier pick then a uniform integer; agreement ≤ 1/100 absolute on every decision P(T ≤ 90) cell AND ≥ 4·SE headroom on every firing cell). Stability seed 20261358 (N = 10,000) must reproduce the ruling through twin independently-written evaluators; reporting seed 20261359 (the σ ∈ {0, 9/10} worlds, the H ∈ {30, 180} pair, badge-share curves S(d) in E[!daily] units, the CV-of-T age-concentration mark at (p = 1, σ = 0), the C* threshold menu — exact minimal C keeping P(T ≤ 90) ≤ 1/2 per cell plus the committed threshold re-expressed at {20,000, 50,000, 100,000} — the other six badges' exact static sample-calibration rows, the deep_diver contract-cap saturation note); aux seed 20261360 NEVER read. Decision rule pre-registered, applied IN ORDER: REJECT FIRST ("age badge": Arm A EXACT at σ = 1/2 posts P(T ≤ 90) ≥ 19/20 at ≥ 3 of 4 claim-rate cells AND median T ≤ 14 days at the full-engagement (p = 1, σ = 0) cell AND every firing cell confirms in Arm S within 1/100 with ≥ 4·SE headroom) → APPROVE ("the calibration holds": at σ = 1/2, P(T ≤ 90) ≤ 1/2 at ≥ 2 of 4 cells AND ≥ 19/20 at ≤ 1 cell, both arms, stability reproduced) → NULL (anything else — three named axes: band-straddle with the C* menu row as knob, concentration-miss with knob H, arm disagreement). Gates F1–F5 + mechanical (draw-count sentinels, twin evaluators, two-process byte identity by external sha256, CPython minor pinned, aux seed never read) — run invalid on any failure. Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT at σ = 1/2 with P(T ≤ 90) = 1.000000 / 1.000000 / 0.986615 / 0.205567 across p = 1, 1/2, 1/4, 1/10 and full-engagement median 7; the p = 1/10 cell the surviving discriminator; the σ = 9/10 world the named flip (only p = 1 fires). Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-066-badge-saturation/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 055 + VERDICT 066 appended to sim-lab `control/outbox.md` only; nothing echoed to idea-engine). Reservation this slice: idea-engine claim file `control/claims/` for INTAKE 055 + VERDICT 066 merged via idea-engine PR #386 BEFORE this session; this born-red card is the first commit on `claude/verdict-066-badge-saturation` and the PR opens READY immediately after. This card holds the substrate gate red deliberately until the final flip (the born-red discipline — that red is the ONLY acceptable red on this branch).

## What happened

Built `sims/verdict-066-badge-saturation/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 055 block / idea doc @
idea-engine main 18f3171; both calibration comments and the
shared-wallet contract line quoted verbatim at the pins; the disclosed
fixture-level choices — Bernoulli/value-draw conventions, full-horizon
trajectory shape + exact draw sentinels, exact-variance SE convention,
reporting N = 10,000, the C* binomial-mixture machinery with its exact
absorbing-arm cross-check, the median convention, the cpython-3.11
pin — all pinned in the fixture BEFORE the runner). Git trail (PR #124):
839a413 (born-red card) -> 987adfb (fixtures) -> b1a31be (runner
badge_saturation_sim.py + accepted run: results.json, run-stdout.txt,
README.md, REPORT.md) -> merge of origin/main (V065 landed mid-session
via PR #123; both slices kept, this block stayed 066) -> d397b68
(INTAKE 055 + VERDICT 066 ledger) -> this flip. Reservation disclosure:
the idea-engine claim file for INTAKE 055 + VERDICT 066 merged via
idea-engine PR #386 BEFORE this session branched (the claim-first
ritual, the V065 pattern); `VERDICT 066`/`INTAKE 055` grepped clean at
session start (135ae4e, 02:51:46Z) and re-grepped clean at 626d16e
immediately before the ledger append.

**Run:** `SELF-CHECKS: 166 passed, 0 failed`, exit 0, ~1m41s/run;
stdout + results.json byte-identical across two full process runs by
external sha256 (run-stdout d11c2530..., results 3a037d0d...); CPython
3.11 pinned, asserted. Gates all green: F1 anchor exact (E = 169201/100,
weights 100, per-value table re-derived); F2 crossing identities exact
(0, 1/2500, certainty-at-20; P(T<=3) = 0 at sigma = 1/2); F3 all seven
hit lists reproduce the calibration comments exactly; F4 monotonicity
exact in n, p, sigma, C; F5 degenerate transform + mass conservation
every day of every cell; the binomial-mixture day-90 wallet law equals
the absorbing arm at C = 10,000 on every decision cell (exact Fraction
equality); draw sentinels exact (7,200,000 / 3,330,986 headline); twin
evaluators agree on headline AND stability; aux seed 20261360 never
constructed, never read.

**Ruling: REJECT** (checked FIRST, fires on all three conjuncts):
P(T <= 90) at sigma = 1/2 = 1 exactly / 1 - eps / 0.986615 / 0.205567
over p = 1, 1/2, 1/4, 1/10 (3 of 4 >= 19/20), full-engagement median
T = 7 <= 14 (E[T] = 6.66, CV = 0.263 — the age-badge concentration
mark), every firing cell confirmed in Arm S (worst |dev| 0.000265,
worst finite headroom 44.7·SE). Stability (seed 20261358) reproduces
through both twin evaluators. Every drafter-disclosed value reproduced
from scratch EXACTLY (both sigma rows, both medians). The C* menu
ships: 76,043 / 37,916 / 18,823 / 7,362 per archetype (44.9 / 22.4 /
11.1 / 4.4 expected dailies). Three first-class anomalies: A1 the
registration's Common-row per-value numerator is a denominator slip
(9/10^5 written, 9/10^4 exact — convicted by the registration's own
weights-sum-100 + E-exact conjuncts); A2 the outbox idea: blob pin
4df5043 is pre-squash, absent from main history (HEAD copy verified
constant-identical); A3 superbot's _daily_weights streak-luck shift is
excluded by the registered base-weight streak-0 floor (REJECT-robust
direction, named by the registration itself).

Walls: one new, disclosed — the worker harness's Write tool refused to
create REPORT.md by filename pattern ("Subagents should return findings
as text, not write report files"), so REPORT.md rode a shell heredoc
alongside the ledger append (the standing V054+ heredoc classification;
fixtures, runner, README, and this card went through Write normally).
One dirt rescue: a `.substrate/guard-fires.jsonl` working-tree
modification appeared after the mid-session merge of origin/main —
restored locally, never staged, never pushed. ASK-003 observation: the
post-merge `bootstrap.py check --strict` printed "all checks passed"
WITHOUT re-flagging this card's still-in-progress born-red HOLD (the
pre-merge run had flagged it); consistent with the known mtime-keyed
check staleness — disclosed here, and the CI substrate-gate remains the
arbiter on the PR. `control/inbox.md`, both status heartbeats, and
idea-engine's outbox untouched. Session-card markers: `**Status:**`
complete, 💡 below, previous-session review below, `📊 Model:`
family-level. PR: https://github.com/menno420/sim-lab/pull/124 (READY;
merge-on-green owns the merge — zero agent merge/arm calls).

## 💡 Session idea

When the sim's state variable is MONOTONE, register the unabsorbed
terminal law as the cross-structure — it is simultaneously a stronger
correctness check and a free reporting deliverable. Proof case from this
slice: net daily income is strictly positive under every registered
sigma (min net = 50 at sigma = 9/10), so the wallet never decreases and
P(T <= 90 | threshold C) = P(W_90 >= C) for EVERY C at once. That one
identity did double duty: (1) the registered absorbing DP
(day-by-day absorption at 10,000) and an independently-decomposed exact
law (W_90 = S_K, K ~ Binomial(90, p) claims-count mixture — different
recursion, different denominators, different code path) had to agree as
exact Fractions on every decision cell, which is a strictly stronger
independence class than twin evaluators (two DECOMPOSITIONS of the
model, not two codings of one comparison); and (2) the same day-90 law
priced the ENTIRE C* threshold menu and the {20k, 50k, 100k}
re-expression by suffix sums — the headline consequence deliverable —
at one extra pass instead of one absorbing DP per candidate threshold
(a ~17x bisection saving per cell). Kin, deduped (grep .sessions/ +
outbox for "cross-structure", "brute-force", "monotone"): V064's
1024-outcome enumeration and V063's inclusion-exclusion-vs-enumeration
are the same GENUS (independent second structure must equal the
decision arm); the new species is picking the second structure so it is
also a consequence-menu generator — the check pays for the report.
One-line guard for future registrations: if the state is monotone,
pre-register "unabsorbed terminal law == absorbing law at the committed
threshold, exact" as a named gate and hang the threshold menu off it.
Anchors: badge_saturation_sim.py `mixture_tails` + the cross-structure
checks; REPORT.md § C* threshold menu; fixtures.json
`cstar_menu.machinery_note`.

## ⟲ Previous-session review

VERDICT 064 (healthcheck blind window, PR #122) is the reviewed
predecessor (V065 landed mid-session in parallel and is only touched
here as a merge fact). V064's 💡 — require drafter disclosures to be
exact rationals and machine-check every re-stated closed form at
drafting — reads VALIDATED from here with a sharpened species: P055's
drafter disclosed ten values exactly and every one reproduced to the
digit (the V064 pattern holding), while the one registration defect
this session found (A1) lived in exactly the place V064's rule
predicts — a hand-transcribed DERIVED table (the per-value numerators)
rather than a disclosed decision number, and the registration's own
redundant conjuncts (weights sum 100, E exact) are what convicted it.
The five-line drafting harness V064 proposed would have caught A1
before registration. Its craft transferred verbatim and cheaply: the
born-red -> fixtures -> runner git trail, the twin evaluators, the
exact-variance SE convention, plain-vocabulary stability classes
("REJECT", keeping the ledger grammar closed — its own nit against
V063, honored here), and the literal five-validity-gate REPORT closing.
One honest divergence back: V064 proved aux-seed hygiene by
CONSTRUCTING the aux RNG and asserting zero draws; this slice proved it
by NEVER CONSTRUCTING it (a recording factory whose log is asserted
equal to the three registered constructions) — absence from the
construction log is a simpler and strictly stronger invariant than a
zero draw-counter, and it matches P055's "never read" grammar; worth
adopting as the default unless a registration explicitly pins
"constructed last, 0 draws".

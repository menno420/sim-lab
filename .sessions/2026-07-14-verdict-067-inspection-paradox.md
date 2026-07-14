# Session — VERDICT 067 — The inspection paradox at equal means: does the folk rule "mean headway μ ⇒ expected wait μ/2" survive random incidence on a deliberately consumer-relevant equal-mean schedule grid, or does headway variability inflate every real wait by the size-bias factor 1 + CV²? (idea-engine PROPOSAL 056, ORDER 003 COMPLETELY-UNRELATED rotation slot, round 10 closer)

> **Status:** complete
> 📊 Model: Claude Fable (Claude 5 family) · 2026-07-14 · verdict-067 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 056 (`## PROPOSAL 056 · 2026-07-14T02:52:22Z · status: sim-ready`, landed via idea-engine PR #387 → main adc641fe33c479d74ff60b0614725477058c53a8; reservation this slice: idea-engine claim file `control/claims/claude-verdict-067-inspection-paradox.md` landed via idea-engine PR #388 → main 3ae82cb; numbering INTAKE = proposal number, PROPOSAL 056 → VERDICT 067 per the established +11 offset map P050→V061 / P051→V062 / P052→V063 / P053→V064, V065/V066 in flight on PRs #123/#124) — price the folk rule "a service averaging one arrival every μ minutes means a random arriver waits μ/2" against the exact random-incidence law ρ = E[W]/(μ/2) = E[X²]/E[X]² = 1 + CV², per the idea doc `ideas/fleet/inspection-paradox-wait-inflation-2026-07-14.md` @ idea-engine ae0e038. Pinned model: i.i.d. integer-minute headways X, mean EXACTLY μ = 10 per cell; passenger lands uniformly at random over a long window (random incidence), waits W = time to next arrival, continuous-uniform position within the containing gap; five committed equal-mean schedules — CLOCKWORK X ≡ 10 (control), JITTER X ∈ {8, 12} w.p. 1/2, SPREAD X uniform on {5..15}, MEMORYLESS X geometric on {1, 2, …} q = 1/10, BUNCHED X ∈ {2 w.p. 4/5, 42 w.p. 1/5}; variances {0, 4, 10, 90, 256}; exact laws E[W] = E[X²]/(2E[X]), E[L] = E[X²]/E[X], P(W > w) = E[(X − w)⁺]/E[X]; exceedance grid w ∈ {5, 8, 10, 15}. Arm A = DECISION (seedless exact `fractions.Fraction` moment arithmetic, geometric via closed forms cross-checked against exact rational partial sums to K = 500 plus exact tail formulas, alone decision-bearing); Arm S = confirmation (seed 20261361: per stochastic cell a K = 100,000-interval renewal trajectory, pinned draw order cells JITTER → SPREAD → MEMORYLESS → BUNCHED, all intervals before any landing, geometric as count-of-Bernoulli(q)-trials no float log, N = 200,000 uniform landings with bisect waits and containing-gap lengths; agreement gate |mean_S − E_A|/E_A ≤ 1/100 AND ≤ 4·SE on E[W] AND on P(W > 10) per cell); stability leg seed 20261362 (K = 20,000, N = 50,000, ruling reproduced through twin independently-written decision evaluators); reporting leg seed 20261363 (median/P90 wait rows, never decision-bearing); aux seed 20261364 reserved, NEVER read by any decision number. Decision rule pre-registered, applied IN ORDER: REJECT FIRST (ρ(BUNCHED) ≥ 2 AND ρ ≥ 11/10 in ≥ 3 of the 4 stochastic cells AND Arm S confirms within the agreement gate on every stochastic cell) → INVALID (F1 pmf re-derivation / F2 size-bias identities / F3 CLOCKWORK degenerate / F4 monotonicity / F5 hand identities / Arm-S gate failing — report, no ruling) → APPROVE (ρ ≤ 21/20 at EVERY stochastic cell AND the seed-20261362 stability leg reproduces through twin evaluators) → NULL (band-straddle / dispersion-sensitivity / arm disagreement — named axes, never a re-run request). Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT at ρ = 26/25 / 11/10 / 19/10 / 89/25 across JITTER/SPREAD/MEMORYLESS/BUNCHED, BUNCHED E[W] = 89/5 = 17.8 min vs folk 5, SPREAD exactly ON the 11/10 edge, JITTER genuinely APPROVE-side. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-067-inspection-paradox/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 056 + VERDICT 067 appended to sim-lab `control/outbox.md` only). This card holds the substrate gate red deliberately until the final flip (the born-red discipline — that red is the ONLY acceptable red on this branch).

## What happened

Built `sims/verdict-067-inspection-paradox/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 056 block / idea doc @
idea-engine adc641f; the disclosed fixture-level choices — single RNG
stream per leg with the per-cell intervals-before-landings reading of
"all intervals before any landing", uniform-only draw maps, the
exact-variance SE convention sqrt(Var_exact/N) with
Var(W) = E[X^3]/(3E[X]) - E[W]^2, the literal both-halves-on-both-metrics
agreement-gate parse, reporting-leg K = 20,000 / N = 50,000, the twin
evaluators, the CPython 3.11 pin — all pinned in the fixture BEFORE the
runner) committed before the runner. Git trail (PR #125): 6479f99
(born-red card) -> fb96ee8 (fixtures) -> 5e55c25 (runner
inspection_paradox_sim.py + accepted run: results.json, run-stdout.txt,
README.md, REPORT.md) -> 119ace3 (merge of origin/main after V065 #123
and V066 #124 landed mid-session in parallel lanes — merged IN, never
rebased; their files untouched) -> dfb9809 (INTAKE 056 + VERDICT 067
ledger) -> this flip. Reservation: idea-engine claim PR #388 (merged
03:04:21Z) + born-red card first commit + PR #125 READY;
`VERDICT 067`/`INTAKE 056` grepped clean at session start (135ae4e) and
re-grepped clean at a277c9d immediately before the ledger append.

**Run:** `SELF-CHECKS: 83 passed, 0 failed`, exit 0, ~35 s/run; stdout +
results.json byte-identical across two full process runs by external
sha256 (run-stdout 8f1c00f5..., results 75407460...); CPython 3.11
pinned, asserted; seeds 20261361/62/63 the ONLY RNGs constructed
(never-construct aux hygiene, the V066 pattern), aux 20261364 never
read; draw sentinels exact (K, or T = 997,056 for the headline
MEMORYLESS cell; N landings per cell per leg). F1-F5 control gates all
green; twin evaluators agree on headline and stability.

**Ruling: INVALID** (controls branch — report, no ruling). REJECT,
checked FIRST, fails on its THIRD conjunct only: the science conjuncts
hold exactly in Arm A (rho(BUNCHED) = 89/25 = 3.56 >= 2; rho >= 11/10
in 3 of 4 stochastic cells, SPREAD exactly ON the 11/10 edge), but the
Arm-S agreement gate breaches on SPREAD P(W>10) — est 0.134625 vs exact
3/22, relative dev 0.01275 > 1/100 while only 2.27*SE (the 4*SE half
passes). The INVALID branch's "gate failing on any cell" then fires.
Findings, first-class: A1 the registered relative-1/100 gate half is
under-powered by construction (bands 1.49/1.78/3.27 sigma at headline
N, 0.75/0.89/1.63 sigma at stability N — a PERFECT sim passes both legs
with prob ~0.24; INVALID was the modal outcome); A2 the gate sentence
admits a "respectively" parse under which every cell passes and REJECT
would fire — class is parse-dependent, stricter parse adopted and
fixture-pinned pre-run; A3 the stream-reading pin makes the class
seed-lottery-dependent. Stability leg (20261362) lands INVALID through
both twin evaluators (its own gate breaches on JITTER) — reproduces the
headline class. Drafter comparison (never gated): EVERY disclosed exact
value reproduced from scratch — rho {1, 26/25, 11/10, 19/10, 89/25},
BUNCHED E[W] = 89/5 = 17.8 vs folk 5, rider share 21/25, P(W>10) =
16/25; the disclosed REJECT is blocked purely by the gate artifact, not
by any drafter arithmetic error.

Walls: none new. The Write tool refused the REPORT.md filename — rode
the standing shell-heredoc fallback (the V054-V066 classification), as
did the ledger append. Disclosed: after the mid-session merge of main,
LOCAL `bootstrap.py check --strict` went false-GREEN on this branch
while this card still said in-progress (the ASK-003 mtime quirk
validated the newer merged V065 card instead of this one); the born-red
hold rode CI, not the local check, for the final pre-flip push.
`control/inbox.md`, both status heartbeats, and idea-engine's outbox
untouched. PR: https://github.com/menno420/sim-lab/pull/125 (READY;
merge-on-green owns the merge — zero agent merge/arm calls).

## 💡 Session idea

A pre-registered MC agreement gate is itself a statistical instrument
and must be POWER-CHECKED at drafting against its own registered N —
exact-rational disclosure discipline (V064's rule) cannot catch this
defect class because it is value-free: every number in PROPOSAL 056 is
a correct exact Fraction, yet the gate's relative-1/100 half spans only
1.49/1.78/3.27 sigma on three of four cells at the registered
N = 200,000 (0.75/0.89/1.63 sigma at the stability N), so a PERFECT
implementation draws INVALID with probability ~0.76 across the two legs
— the registration pre-committed to a coin flip and this session's seed
lost it honestly. The five-line stdlib drafting check: for every gated
(metric, cell, N), band_width_in_SE = min(rel_tol*value, abs_tol) /
sqrt(Var/N); require >= the gate's own SE multiplier (here 4), else
widen the tolerance or drop the cell to reporting. Corollary with
teeth: a confirmation-arm gate conjunct nested inside REJECT/APPROVE
silently makes SEED NOISE decision-bearing exactly when it is
under-powered — if the science conjuncts are exact-arm-only (they are
here), the gate belongs in INVALID alone, not inside REJECT, so noise
can block a ruling but never masquerade as one axis of it. Kin, deduped
(grep .sessions/ + outbox for "under-powered", "power", "gate width",
"SE units"): V061's 💡 priced an UNDERPOWERED stability conjunct (noise
problem, remedy = size N); V064's an INCONSISTENT symbolic disclosure
(convention problem, remedy = exact rationals); V066's a
hand-transcribed derived table (transcription problem, remedy = machine
re-derivation); this prices an UNDER-POWERED decision gate (design
problem, remedy = SE-units power row at drafting) — same genus
(registration machinery gets less scrutiny than decision numbers),
fourth distinct species, and the first where the defect is invisible to
every prior guard because no disclosed VALUE is wrong. Anchors:
REPORT.md § First-class findings A1/A2; results.json per-cell gate
sub-booleans; fixtures.json `agreement_gate_literal`.

## ⟲ Previous-session review

VERDICT 066 (badge saturation, PR #124) is the direct predecessor (it
and V065 landed mid-session here as merge facts). Its aux-seed
divergence — prove hygiene by NEVER CONSTRUCTING the aux RNG and
asserting the construction log, rather than constructing it and
asserting zero draws — transferred verbatim into this slice
(RNG_REGISTRY == [20261361, 20261362, 20261363], aux 20261364 absent by
construction) and is the better default, as its card argued. Its 💡
(register the monotone unabsorbed terminal law as cross-structure +
consequence menu) did not apply here — no monotone state; this slice's
second structures were closed forms vs partial-sum-plus-exact-tail —
which is itself a useful boundary datum: the V066 guard is
domain-conditional, not universal craft. One honest gap back: V066's
card (like V064's before it) validates the "exact disclosures
reproduce" drafting rule, and P056 SATISFIES that rule completely while
still carrying the defect that decided this verdict — its gate's
statistical power. The drafting harness both cards propose polices
values; it needs the SE-units power row this session's 💡 specifies,
or the next drafter can again pre-register a coin flip with every
number exact.

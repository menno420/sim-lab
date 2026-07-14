# Session — VERDICT 069 — Rubric weight-robustness: is the fresh venture-lab 7-concept batch's band partition (best/borderline/no-build, weights 35/20/15/15/15, bands 3.0/3.5) an artifact of a few percent of a judgment-call weight vector? (idea-engine PROPOSAL 058, ORDER 003 VENTURE rotation slot, round 11, PRODUCTS half)

> **Status:** complete
> 📊 Model: fable-family · 2026-07-14 · verdict-069 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 058 (`## PROPOSAL 058 · 2026-07-14T04:10:35Z · status: sim-ready`, landed via idea-engine PR #395 → main 76aca1e; reservation this slice: idea-engine claim file `control/claims/claude-verdict-069-rubric-weight-robustness.md` riding idea-engine PR #397; numbering INTAKE = proposal number, PROPOSAL 058 → VERDICT 069 per the established +11 offset map P050→V061 … P057→V068) — price the weight-robustness of the band partition induced by venture-lab's shipped rubric (weights w0 = (7/20, 1/5, 3/20, 3/20, 3/20) exact; bands no-build t < 3, borderline 3 ≤ t ≤ 7/2, best t > 7/2) over the published 7 × 5 per-criterion score table (venture-lab docs/products/ideas-2026-07-13-night.md @ a9e202d, quoted verbatim in the PROPOSAL 058 block / idea doc): (i) each concept's EXACT critical jitter radius x*_i via linear-fractional 32-vertex arithmetic (seedless fractions.Fraction, alone decision-bearing for the x* clauses), (ii) the flip probability p(x) per radius x ∈ {1/50, 1/20, 1/10, 1/5}, decision cell x = 1/10, via seeded MC (Arm S main seed 20261369, N = 100,000/radius, 5 uniforms per draw in criterion order; stability seed 20261370, N = 20,000/radius; cross-seed agreement gate 1/50 absolute per radius), plus reporting-only Dirichlet worlds (seed 20261371, κ ∈ {100, 400}, N = 20,000 each), aux seed 20261372 reserved and NEVER read. Decision rule pre-registered, applied IN ORDER: REJECT FIRST (p̂(1/10) main ≥ 1/10 AND x*_1 ≤ 1/20 AND x*_6 ≤ 1/20) → INVALID (F1 identity · F2 critical-radius self-consistency ±1/1000 · F3 zero-flip at 1/50 · F4 containment 1e-9 · F5 hand world · F6 battery · cross-seed gate — report, no ruling) → APPROVE (p̂(1/10) ≤ 1/20 AND all seven x* > 1/20) → NULL (p-straddle / arms-split / mechanism-conditional / surviving arm disagreement — named axes). Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT on all three conjuncts — x* = (1/27, 9/37, 1/3, 7/41, 1/11, 1/47, 1/5), p̂(1/10) ≈ 0.225 (throwaway seed 999). Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-069-rubric-weight-robustness/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 058 + VERDICT 069 appended to sim-lab `control/outbox.md` only). This card holds the substrate gate red deliberately until the final flip (the born-red discipline — that red is the ONLY acceptable red on this branch).

## What happened

Built `sims/verdict-069-rubric-weight-robustness/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 058 block / idea doc @
idea-engine 76aca1e; fixture-level choices C1–C7 — the one-core-random()-call
per u_j sentinel convention, the float band evaluation with edge-hit counter,
the 32-pattern × both-edges x* min, the stability-reproduces parse, the
Dirichlet call sentinel, the F4 uniform-legs scope, repr serialization — all
disclosed IN the fixture BEFORE the runner existed). Git trail (PR #128):
7ccf2fe (born-red card) → 26a0df4 (fixtures) → c05f415 (runner
rubric_weight_robustness_sim.py + accepted run: results.json, run-stdout.txt,
README.md, REPORT.md) → 20a7ed9 (INTAKE 058 + VERDICT 069 ledger) → this
flip. Reservation: idea-engine claim PR #397 (claim-first) + born-red card
first commit + PR #128 READY; `VERDICT 069`/`INTAKE 058` grepped clean at
session start (b155cd1) and re-grepped clean at 31be00d immediately before
the ledger append (main moved mid-session on a status.md heartbeat only;
origin/main merged INTO this branch, never rebased). The harvest pin
venture-lab docs/products/ideas-2026-07-13-night.md blob aa09f12 @ a9e202d
was independently re-verified at intake via GitHub MCP get_file_contents at
the pinned commit SHA (venture-lab added to session scope via add_repo for
that one read); the verdict sim itself read none of it.

**Run:** `SELF-CHECKS: 64 passed, 0 failed`, exit 0, ~2.5 s/run; stdout +
results.json byte-identical across two full process runs by external sha256
(run-stdout 208a85da..., results ea0cffc2...); CPython 3.11 pinned, asserted;
seeds 20261369/70/71 the ONLY RNGs constructed (pinned order), aux 20261372
never read (asserted); core-random() sentinels exact at 5·N per uniform
(seed, radius) leg; twin evaluators agree on headline AND stability; F1–F6 +
cross-seed gates all green.

**Ruling: REJECT** — all three pre-registered conjuncts fire. (1) p̂(1/10) =
0.224550 ≥ 1/10 on the main leg (≈ 94 SD above the edge). (2) exact x*_1 =
1/27 ≈ ±3.70% ≤ 1/20 — the sole above-band concept (141/40 = 3.525) loses
"best available" inside ±3.7% of weight jitter. (3) exact x*_6 = 1/47 ≈
±2.13% ≤ 1/20 — the borderline floor exits through the 3.0 no-build edge.
Full exact table 1/27 · 9/37 · 1/3 · 7/41 · 1/11 · 1/47 · 1/5 — every
drafter-disclosed Fraction reproduced digit-for-digit, never gated. The
registered falsifiability margins behaved as disclosed: p̂(1/20) = 0.060070
below the 1/10 line (one grid step tighter would have landed p-straddle
NULL), five of seven concepts tolerate ≥ ±9%. Reporting: Dirichlet worlds
flip MORE than the uniform box (κ=100: 0.4379, κ=400: 0.33885) —
mechanism-conditional NULL axis not triggered, direction REJECT-ward; 0
exact-edge hits anywhere.

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-068-paper-lane-beat-coin.md`): V068's card
closed with a candidate kit lint — "flag any pre-registered comparator whose
two sides share a common multiplicative factor" — and this session is quiet
evidence for its cousin on the gate side: V068 (and V067 before it) put the
gate-power arithmetic INSIDE the registration, and P058 inherited that
discipline explicitly ("the V067 lesson, applied": every tolerance absolute,
the only stochastic gate SD-sized at its registered N, F3 made deterministic
by exact arithmetic). Result measured here: zero gate artifacts, first
complete run accepted, the class landed on the science. The V068 card's
structure (git-trail sentence, run block, per-conjunct ruling block) was
reused essentially unchanged — it is becoming the de-facto verdict-card
template and could be promoted to one.

💡 **Session idea (genuine, this session):** the attribution table exposed a
structural fact the flip PROBABILITY alone hides: at the decision radius the
flip event coincided EXACTLY with concept 6's band change (22,455 of 22,455
flips moved concept 6; concept 1's region sat entirely inside it in-sample),
so the batch-level p(x) is really a one-concept statistic near its decision
threshold. Candidate instrument rule for any weighted-rubric robustness
audit: alongside p(x), report the CONDITIONAL flip decomposition
P(flip driven only by argmin-x* concept) — when it is ≈ 1, the honest
headline is "one row is knife-edge", not "the partition is fragile", and the
cheap fix is re-scoring that one row rather than re-cutting the bands. Zero
extra draws needed — the attribution counts already exist.

📊 Model: fable-family (self-reported by this session's harness; family-level
name only per the standing attribution doctrine).

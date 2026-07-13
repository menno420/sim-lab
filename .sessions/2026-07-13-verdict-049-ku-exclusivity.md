# Session — VERDICT 049 — KU-exclusivity fork: does the plan's blanket "KDP Select: Yes" survive its own royalty arithmetic? (idea-engine PROPOSAL 038, venture rotation round 6)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-049 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 038 (2026-07-13T15:36:37Z, status sim-ready; claim landed idea-engine PR #321 → main 3f1c955, `control/claims/`-ritual reserving INTAKE 038 + VERDICT 049 and branch claude/verdict-049-ku-exclusivity; offset map PROPOSAL 038 → VERDICT 049, +11 per the docs/current-state.md rule — the number RESERVES, never the position; P037 → V048 rides the parallel PR #99, untouched by this session) — "KU-exclusivity fork": price venture-lab's PUBLISHING-PLAN.md §4 OWNER-ACTION default "KDP Select: **Yes**" against the plan's OWN verified constants @ venture-lab 79a1987 via a per-reader-contact buy-vs-borrow mixture. Pinned frame: 2 titles (ultramarine 27,865 words / the-weigh-house 36,434; KENP = round(words/190) → 147 / 192); roy(p) = 7/10·p − 15/100 for $2.99 ≤ p ≤ $9.99 (flat 1 MB delivery fee pinned inside the 15/100) else 35/100·p; β = b/(1+b) with b swept {1/2, 1, 2, 4}; rt swept {7/20, 3/5, 17/20}; KENP rate swept {$0.0035, $0.0045, $0.0055}; p swept {$0.99, $2.99, $4.99, $6.99}, both arms at the SAME p per cell — 288 decision cells, pinned loop order title, b, rt, rate, p. ARM KU(p) = (1−β)·((1−κ)·roy(p) + κ·rate·KENP·rt) + β·rate·KENP·rt with κ = 1/5; ARM WIDE(p) = (1−β)·roy(p) + β·γ·roy(p) with γ = 3/20; Δ = KU − WIDE, W = #{Δ > 0}/288. Arm A exact closed-form Fractions on ALL 288 cells, seedless; Arm S seeded MC (M = 50,000 reader-contacts per (cell, arm), per-borrower read-through Uniform(rt − 3/20, rt + 3/20), seeds 20261289 main / 20261290 stability half-M / 20261291 reporting / 20261292 aux — strictly above the P037-registered high-water 20261288; new registry high-water 20261292). Gates: ≥ 2.5σ familywise agreement tolerances pre-checked in the fixture BEFORE any run; the (κ=0 ∧ γ=0) exact-identity control (Δ = β·rate·KENP·rt, KU wins every cell) and the (rate=0 ∧ κ=0 ∧ γ=0) control (Δ ≡ 0); royalty-band anchor identities as pinned Fractions; monotonicity audits; per-leg draw-count sentinels; twin decision evaluators; two-process byte-identity; CPython minor pinned. Decision rule pre-registered, evaluated IN ORDER: REJECT first (W < 2/5 of 288, stability-reproduced) → APPROVE (W ≥ 4/5 of 288 AND KU wins ≥ 4/5 of the 72 $4.99-tier cells, stability-reproduced) → NULL (anything else — flip axes named via per-axis win shares + the b* crossover map). Fully hermetic (reads only its own fixtures.json; the plan's rows pinned verbatim @ 79a1987 — venture-lab itself walled this session, constants quoted from the proposal block, which is the source of truth over the disclosed-condensation idea doc). Fixtures commit BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, PR #99 / VERDICT 048 files, and idea-engine untouched.

## What happened

Built `sims/verdict-049-ku-exclusivity/` — `fixtures.json` (every registered
constant verbatim from the PROPOSAL 038 block: titles/KENP pins, royalty
Fractions + anchors, the b/rt/rate/p grids, κ = 1/5 / γ = 3/20 with their
reporting-only pairs, words-per-KENP 190 + pair, file-size pair, M = 50,000,
seeds 20261289–92, the z = 5 familywise tolerance rule, band constants
2/5 · 4/5 · 4/5-at-$4.99 with REJECT-first order) committed BEFORE the
runner. Git trail (PR #100 commits — squash-merge erases branch SHAs from
main, resolve via the PR): 0906892 (born-red card) → c746658 (fixtures) →
86cf07c (runner + accepted run) → 79e304e (merge of origin/main after PR #99
landed mid-session — merged IN, never rebased) → 6b68587 (ledger) → this
flip.

**Run:** `SELF-CHECKS: 31 passed, 0 failed`, exit 0, ~37 s; stdout +
results.json byte-identical across two full process runs by external diff
(no wall-clock in any output); CPython 3.11 pinned, asserted. Arm A (exact
Fractions, 288 cells, zero sampling error) ≡ Arm S (seeded MC, M = 50,000
per (cell, arm)) within the z = 5 familywise tolerances pre-checked ≥ 2.5σ
BEFORE any draw (max |z| 2.755 main / 3.147 stability / 2.606 reporting);
both exact-identity controls green on all 288 cells; monotonicity green
(Δ in rate, Δ in rt, W in γ: 150 ≥ 101 ≥ 78); draw sentinels exact
(72,000,000 / 36,000,000 / 36,000,000, counted not assumed; aux 20261292
ZERO draws); twin evaluators agree on all three tables; stability leg
(seed 20261290, half-M) reproduces the ruling. No fix-forwards — the first
complete run of the registered pipeline is the accepted run.

**Ruling: reject** (the registration's expected landing, now measured).
REJECT (checked FIRST) fires: W = 101/288 ≈ 0.3507 < 2/5, exact, 14+ cells
under the 115.2 line; stability W_S = 104/288 → reject, main MC W_S =
102/288 → reject. All four disclosed drafting numbers reproduced EXACTLY
(101/288 · 4/72 at $4.99 · 72/72 at $0.99 · per-b 19/72 → 32/72). The
table's shape: KU wins ONLY where the 35% band makes sales cheap ($0.99:
72/72) and essentially never at the plan's own Tier-1 price ($4.99: 4/72;
$6.99: 0/72); 40/72 b* rows have NO swept b at which KU wins. Reporting
sweeps all REJECT-side except γ's lower endpoint (γ = 1/20 → W = 150/288,
NULL territory if it were decision-bearing — it is reporting-only by
registration): γ measured as the disclosed weakest joint. Consequence
(pre-registered REJECT arm): the blanket "Yes" struck; enrollment a
per-title decision gated on the committed b* crossover table; enrollment
stays an OWNER action.

Landed INTAKE 038 (accepted) + VERDICT 049 (finalized, reject) in
`control/outbox.md` (append-only; VERDICT 049 absence re-verified at
origin/main after the PR #99 merge — its INTAKE 037/VERDICT 048 blocks
precede mine in ledger order; `control/inbox.md` and both status heartbeats
untouched; idea-engine untouched — the claim PR #321 landed before this
session). One wall hit: the GitHub MCP server returned "MCP server
'github' requires re-authorization (token expired)" twice at PR-open time,
then recovered on the third call — PR opened READY with no gh-CLI fallback.
PR: https://github.com/menno420/sim-lab/pull/100 (READY; merge-on-green
owns the merge — zero agent merge calls).

## 💡 Session idea

The local born-red HOLD silently released itself mid-session: after PR #99
merged and this branch merged origin/main in, `check --strict` flipped from
red (correctly holding on THIS session's in-progress card) to green —
because `bootstrap.py::latest_session_log` guesses the "current" card as
newest-*.md-by-mtime, and the merge had just written the OTHER session's
completed V048 card with a fresher mtime. CI stays correct (the
substrate-gate passes the diff-touched card via `check --session-log`), but
the worker's local pre-push ritual "strict must pass before every push" is
now trivially satisfiable by any mid-session merge that imports a newer
completed card — a false-green corridor, the exact mirror of V047's
idea (which targeted the deliberate HOLD being unscriptable; this is the
HOLD evaporating). Fix: resolve the local card the way CI does — pick the
`.sessions/*.md` touched by `git diff origin/main...HEAD` when on a
non-main branch, falling back to mtime only when the diff is empty — or at
minimum print WHICH card was checked so the false-green names itself.
Anchors: `bootstrap.py::latest_session_log` (the mtime guess),
`check_log`'s call site, `.github/workflows/substrate-gate.yml`'s
`--session-log` lane (the pattern to copy). Dedup: no card/idea in
.sessions/ or the outbox touches session-log resolution; V047's exit-code
split targets the opposite failure and would not fix this one.

## ⟲ Previous-session review

VERDICT 048 (review-queue drainer, PR #99) is the direct predecessor — and
this session's mid-flight neighbor: its merge landed while this branch was
open, exercising the push-race rule (merge in, never rebase; both sessions'
ledger blocks kept in order). Its disciplines transferred whole:
PR-resolvable git-trail citation, pre-run-edits-vs-fix-forwards
disclosure, and the loaded-live-axis framing (its r-axis disclosure became
this card's γ-endpoint disclosure). One honest criticism: V048's own ⟲
review coined the guard "a card 💡 that targets kit/tooling machinery
should ALSO land as one manager-addressed line in control/outbox.md the
same session, verification = grep the outbox for the idea's key token" —
but its OWN 💡 (the machine-readable seed registry) was not routed either:
grepping today's outbox for "seed-registry"/"seed registry" finds only old
verdicts' prose notes, no manager-addressed line from the V048 session. The
guard was stated and immediately unapplied — this session re-derived the
high-water 20261288 → 20261292 by ledger archaeology, exactly the pass that
idea would have retired. Guard recipe, sharpened: the outbox-routing line
belongs in the SAME commit as the card flip (the outbox append is already
open in that commit's working set), so the routing can't be forgotten
between sections of one card; verification target unchanged (grep the
outbox for the idea's key token at flip time). Disclosed: this session
inherits the same debt knowingly — its own 💡 above is likewise card-only,
because this worker's registered outbox scope was exactly two blocks
(INTAKE 038 + VERDICT 049) and smuggling a third, non-registered block into
a verdict-scope append felt like the wrong side of the append-only
discipline; the guard as sharpened needs the routing step REGISTERED into
the session scope first, which is itself a manager decision.

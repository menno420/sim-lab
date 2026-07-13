# Session — VERDICT 051 — Schelling segregation tipping: does a 30%-minority-content preference still self-sort on a deliberately conservative dynamics? (idea-engine PROPOSAL 040, unrelated-domain rotation round 6)

> **Status:** `complete`
> 📊 Model: fable-family · 2026-07-13 · verdict-051 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 040 (2026-07-13T17:19:39Z, status sim-ready; claim landed via idea-engine PR #327, `control/claims/`-ritual reserving INTAKE 040 + VERDICT 051 and branch claude/verdict-051-schelling-tipping; offset map PROPOSAL 040 → VERDICT 051, +11 per the docs/current-state.md rule — the number RESERVES, never the position; P039 → V050 rides a parallel live session, untouched by this session) — "Schelling segregation tipping at the integration-compatible threshold": measure whether an agent population content as a 30% local minority (τ = 3/10) still self-sorts into strong global segregation under the pinned CONSERVATIVE frame. Pinned frame (every constant verbatim from the PROPOSAL 040 block, the source of truth): 40×40 TORUS (1,600 cells, row-major), exactly 720 A / 720 B / 160 vacant (45/45/10, conservation recounted every sweep); Moore-8 with wraparound; satisfaction = like-fraction among OCCUPIED neighbors ≥ τ tested in exact integers as like·τ_den ≥ τ_num·occ, zero-occupied-neighbors ⇒ SATISFIED; init = the pinned 1,600-entry label list [720 A, 720 B, 160 vacant] under one rng.shuffle; dynamics = live random-serial sweeps (per sweep: shuffle the ascending occupied-cell list, each agent evaluates against the LIVE grid, an unsatisfied agent relocates to a uniformly random vacant cell — ascending vacancy list, index by rng.randrange — vacating immediately); termination = fixation (a zero-relocation sweep, independently re-certified) or cap 500 sweeps, cap-terminated runs CAP-CENSORED for decision purposes; RNG = one stdlib random.Random(seed) per leg, pinned draw order (init shuffle → per-sweep order shuffle → one randrange per relocation), draw-count sentinels. Metric: s(τ) = per-run exact-Fraction mean over agents with ≥ 1 occupied neighbor of like/occ at termination; decision number = MEDIAN of M = 32 main-leg runs at τ = 3/10 (mean of the 16th/17th order statistics, exact rational). Legs: seed 20261297 main (full τ grid {1/8, 1/4, 3/10, 3/8, 1/2, 5/8, 3/4}, M = 32, every cell but τ = 3/10 reporting-only) / 20261298 stability (decision cell, M = 16, must reproduce any APPROVE) / 20261299 reporting (vacancy pair {1/20, 1/5} → 760/760/80 and 640/640/320, plus the N = 25 cell 281/281/63, each M = 16, reporting-only — CANNOT flip the decision) / 20261300 aux (reserved, NEVER drawn). Gates, run invalid on any failure: the pinned 4×4 hand fixture (wrap + neighborhood arithmetic); the τ = 0 control leg (EXACTLY zero relocations, every run's initial-placement s inside [47/100, 53/100]); per-sweep conservation 720/720/160; independent fixation re-certification by a separately written satisfaction scan; monotonicity audit (reporting, flagged loudly); per-leg draw-count sentinels; twin independently-written decision evaluators; stdout + results.json byte-identical across two process runs; CPython minor pinned. Decision rule pre-registered, evaluated IN ORDER, both bands carrying the validity conjunct "AND fewer than 1/4 of the 32 decision-cell runs are cap-censored": REJECT first (median s(3/10) < 11/20) → APPROVE (median ≥ 7/10 AND the seed-20261298 stability leg reproduces the same ruling under the identical rule) → NULL (anything else — binding axis named from the pre-registered four: band straddle [11/20, 7/10), non-convergence, stability non-reproduction, vacancy-sensitivity flip; cheapest live probe pre-priced: the τ = 3/10 cell alone at cap 2,000 on aux seed 20261300). Fully hermetic: zero repo/network reads by the runner — fixtures.json constructed from the pinned constants and committed BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, the parallel VERDICT 050 session's files/claims/number, and idea-engine's outbox untouched.

## What happened

Built `sims/verdict-051-schelling-tipping/` — `fixtures.json` (every
registered constant verbatim from the PROPOSAL 040 block: grid/counts, the
τ grid as exact rationals, satisfaction rule + vacuous-satisfaction
convention, sweep cap 500, M = 32/16, seeds 20261297–300, bands
11/20 · 7/10 with REJECT-first order and the < 1/4-cap-censored validity
conjunct, baseline band [47/100, 53/100], the vacancy pair + N = 25 cells,
and the 4×4 hand fixture with its 16 hand-computed occ/like values —
derived by hand at fixture-commit time, before the runner existed)
committed BEFORE the runner. Git trail (PR #102 commits — squash-merge
erases branch SHAs from main, resolve via the PR): 4db256b (born-red card)
→ 9898785 (fixtures) → 55bb9b4 (runner + accepted run) → 0d7c778 (merge of
origin/main after PR #101 / VERDICT 050 landed mid-session — merged IN,
never rebased) → 4214193 (ledger) → this flip.

**Run:** `SELF-CHECKS: 32 passed, 0 failed`, exit 0, ~17 s; stdout +
results.json byte-identical across two full process runs by external diff
(no wall-clock in any output); CPython 3.11 pinned, asserted. Gates all
green: 4×4 hand fixture verified by the engine AND the independently
written satisfaction scan; τ = 0 control (main seed, M = 32) made EXACTLY
zero relocations with every initial-placement s inside [47/100, 53/100]
(measured 0.4837–0.5115 — the well-mixed baseline measured, not assumed);
per-sweep conservation 720/720/160 at all 9,315 sweep ends; all 320
fixations independently re-certified; draw sentinels exact per leg
(randranges ≡ relocations, shuffles ≡ runs + sweeps; aux 20261300 ZERO
draws); twin decision evaluators (Fraction vs pure-integer) agree. No
fix-forwards — the first complete run of the registered pipeline is the
accepted run.

**Ruling: approve.** REJECT (checked FIRST) does not fire: median s(3/10)
= 90871/120960 ≈ 0.7512, not < 11/20, validity conjunct PASS (0/32
cap-censored — every run in all 320 across all legs FIXATED; the four
pre-registered NULL shapes stayed empty and the aux-seed probe was never
needed). APPROVE fires: median ≥ 7/10 exactly, all 32 decision runs
individually ≥ 7/10 (worst 0.7143), stability leg reproduces (seed
20261298, median 21511/28800 ≈ 0.7469, 0/16 capped). The s(τ) curve is the
side pin: 0.51 → 0.57 → 0.75 → 0.76 → 0.87 → 0.98 → 1.00 across
{1/8 … 3/4} — the tipping knee sits between 1/4 and 3/10, exactly at the
showcase threshold; no vacancy flip (0.7529 / 0.7371 same side of both
bands); N = 25 agrees (0.7440). Landed INTAKE 040 (accepted) + VERDICT 051
(finalized, approve) in `control/outbox.md` (append-only; `## VERDICT 051`
collision-grepped at origin/main bec5505 at session start and re-grepped
after the mid-session merge of 1889181 — none). `control/inbox.md`, both
status heartbeats, VERDICT 050 files, and idea-engine's outbox untouched;
claim rode idea-engine PR #327 (merged → main ee4fb76). No walls hit;
@codex suspended per dedc12e — `codex: none this cycle`. PR:
https://github.com/menno420/sim-lab/pull/102 (READY; merge-on-green owns
the merge — zero agent merge calls).

## 💡 Session idea

`.substrate/guard-fires.jsonl` is a TRACKED shared-append file that every
session's local `check` writes to (this session's born-red strict run
appended a session-log line to it mid-flight, unprompted) — which makes it
exactly the merge-conflict machine the claims README documents: the
measured claim-layout sim (superbot `tools/sim/claim_layout_sim.py`) put
shared-append files at ~98% conflict under concurrent sessions, and this
repo now routinely runs two parallel verdict slices (V048∥V049, V049∥V050,
V050∥V051). The only reason V050∥V051 didn't conflict here is that V050's
session happened not to commit its guard-fires lines — the hazard is
armed, not hypothetical. Fix, mirroring the one-file-per-claim lesson the
kit already ratified: shard the log per session
(`.substrate/guard-fires/<card-slug>.jsonl`) or untrack it (gitignore +
local-only), keeping `check`'s writer unchanged either way. Anchors:
`bootstrap.py`'s guard-fire append site (grep `guard-fires`), the claims
README's measured ~98% shared-append conflict rate, this card's git trail
(the flip commit carries the appended line as evidence). Dedup: grep of
.sessions/, control/outbox.md, and docs/ for "guard-fires" at flip time —
zero hits anywhere; the V048/V049/V050 idea lineage targets session-log
resolution and seed registries, never the guard-fire log.

## ⟲ Previous-session review

VERDICT 050 (Gloamline survival ceiling, PR #101) is the direct
predecessor and this session's mid-flight neighbor — its merge landed
while this branch was open, exercising the push-race rule (merged IN,
never rebased; both sessions' ledger blocks kept in order, numbers stable
throughout). Its disciplines transferred whole: fixtures-before-runner
with PR-resolvable citations, the collision-grep-at-append ritual, and the
development-edits-vs-fix-forwards disclosure line. The material finding:
V050's ⟲ reviewed V049's 💡 (the mtime false-green corridor — a
mid-session merge importing a newer COMPLETED card trivially satisfies the
local strict HOLD) and reported it "still live and still unguarded" while
noting V050 itself "simply never entered" the corridor. THIS session
entered it, and it fired exactly as V049 predicted: after the PR #101
merge, local `check --strict` flipped green by validating V050's
just-imported completed card (fresher mtime) while this session's own card
still said in-progress — verbatim output "session log
.sessions/2026-07-13-verdict-050-gloamline-survival-ceiling.md complete."
CI stayed correct (substrate-gate checks the diff-touched card), but the
local pre-push ritual was trivially satisfiable for the rest of the
session — the corridor is now a REPRODUCED defect with a live citation,
not a described risk, which is exactly the escalation V049's fix sketch
(resolve the card the way CI does, via `git diff origin/main...HEAD`)
needs to stop being three-cards-deep card-only debt.

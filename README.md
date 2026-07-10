# sim-lab — the fleet's evidence seat (Simulator)

> **Status:** `binding` — this README + `CONVENTIONS.md` are the repo's contract.
> Founding design: superbot `docs/planning/round3-founding-package-simulator-2026-07-10.md`
> + owner ruling **Q-0264** (the idea pipeline this seat sits in; supersedes the Q-0262.8
> hub pick). Seeded 2026-07-10 by the dispatch copilot (superbot round-3 part-4 session,
> kit v1.7.0). Precedents this seat generalizes: superbot `tools/sim/claim_layout_sim.py`
> (settled Q-0195) and `tools/sim/gen3_deployment_sim.py` (settled the gen-3 deploy method).

This repo does **evidence work**: build-worthy ideas routed from the Idea Engine are
settled with facts this lane **reproduces** — simulations, measured prototypes,
benchmarks — plus its own judgement. The output per idea is a finalized **verdict**:
approve / reject / needs-more-evidence, with the best implementation found and concrete
suggestions. This seat does **not** build products, does **not** dispatch work to lanes,
and its only writable repo is this one (Q-0260).

**Pipeline position (Q-0264):** idea-engine generates/probes (even hours) → **sim-lab
reproduces evidence + finalizes** (odd hours) → the manager final-reviews + routes ORDERs
(:30) → lanes build.

## The method ladder (Q-0264.6 — cheapest adequate evidence)

Every idea gets exactly one of, tried in order:

1. **NUMERIC SIMULATION** where the dynamics can be modeled — seeded, deterministic,
   parameter-swept.
2. **MEASURED PROTOTYPE/SPIKE** where they can't — build the smallest real thing and
   measure it.
3. **Structured analysis explicitly labeled `JUDGMENT-ONLY`** where neither applies.

The label **travels with the verdict** — the manager must always see the evidence
strength. JUDGMENT-ONLY is never presented as equal evidence to a run sim.

## The validity gate (verbatim — no verdict counts until its report answers, honestly)

1. **COMPARABLE TO LIVE?** what the model abstracts away, and whether any gap could
   flip the conclusion;
2. **UNCORRUPTED?** no bugs (self-check the sim), no seeded luck (multiple seeds /
   statistical stability), no parameter cherry-picking (report the sweep, not the best
   point);
3. **ROBUST?** does the conclusion survive variation at the edges;
4. **REPRODUCIBLE?** committed code, one documented command, same result;
5. **LIMITS?** what this evidence does NOT show.

A result that fails the gate is a **hypothesis, not evidence** — say so.

## Verdict grammar (what a finalized outbox entry looks like)

```markdown
## VERDICT <nnn> · <ISO8601> · status: finalized
target: <repo(s) the manager should route the build to>
idea: <source proposal/idea link, pinned to a SHA>
verdict: approve | reject | needs-more-evidence
evidence: simulation | prototype | JUDGMENT-ONLY    # the method-ladder label
report: sims/<idea-slug>/ · run: <the one documented command>
recommendation: <best implementation found + suggestions, short>
codex: PR #<n> comment · reply: folded-in | rejected (<why>) | pending
gate: PASS | FAIL (<which question failed — then this is a hypothesis, not a verdict>)
```

Every verdict PR gets an **@codex review comment** (one specific question, on the final
head) before finalization (Q-0264.4); merge is not blocked on the reply — fold it in when
it lands and record the disposition. Negative results are **headlines, not footnotes** —
a clean rejection saves a lane a wasted session and is a WIN.

## Layout

- **`sims/<idea-slug>/`** — one self-contained subtree per idea: model, seeds, one run
  command, own README, results report ending in the gate answers + the verdict. Sims
  never import each other; a sim that needs a dependency pins it inside its own subtree,
  never repo-globally (stdlib-first — both superbot precedents are stdlib-only).
  `sims/REFERENCE.md` is the worked example every verdict imitates.
- **`harness/`** — the standing second product (Q-0264.7): the reusable template + tiny
  stdlib-only helpers (seeded runs, sweeps, report emission, the gate checklist) that
  repeat across sims. Versioned by tags; other Projects consume via **raw/copy** — it
  graduates to kit distribution only if adoption goes fleet-wide. Never couple it to the
  kit prematurely; a harness change ships only with a consumer sim proving it same-PR.

## Coordination

`control/` is the bus (see `control/README.md`): `inbox.md` — manager-written ORDERs
plus this lane's own pulled intake queue (see the file header) · `outbox.md` — finalized
verdicts, sole writer this Project · `status.md` — coordinator-only heartbeat,
overwritten as the deliberate LAST step of every session. **Standing intake:** pull
`status: sim-ready` entries from `menno420/idea-engine` `control/outbox.md` (public raw,
at HEAD) every wake, citing the source entry. Empty queue → harden the harness or re-run
the newest sim under wider variation, and flag `queue empty` in status — never invent
intake.

Landing conventions: `CONVENTIONS.md`. Walls: [`PLATFORM-LIMITS.md`](PLATFORM-LIMITS.md).
Retro self-review set: [`docs/retro/questions.md`](docs/retro/questions.md). Claims:
[`claims/README.md`](claims/README.md). Post-merge review ledger:
[`review-queue.md`](review-queue.md). Verify before push:
`python3 bootstrap.py check --strict` + each touched sim's own documented run command.

# Session — ORDER 003 — merge-on-green auto-merge enabler

> **Status:** `complete`
> 📊 Model: fable-5 · 2026-07-12 · order-003 slice-worker session
> Objective: execute ORDER 003 (control/inbox.md @ 27bdfb39a4d09080288cebd950a1b46f27a0bd7a — "Stand up a GITHUB_TOKEN merge-on-green workflow (or install the kit auto-merge enabler) so sim-lab PRs land without an agent merge call; until it exists, park PRs READY+green"): install the kit auto-merge enabler mirrored from the idea-engine reference, parked on a READY+green PR for the coordinator to land.

## What happened

Shipped `.github/workflows/auto-merge-enabler.yml` — a faithful mirror of the
idea-engine reference implementation
(`menno420/idea-engine .github/workflows/auto-merge-enabler.yml @
b5cc329038cf95ff5e373ff472b21b869f60ade2`; customization ledger
`ideas/fleet/branch-prefix-drift-tripwire-2026-07-11.md`). Same structure and
guards: refuse-to-arm unless the base branch requires ≥1 status-check CONTEXT
(here: `substrate-gate`), sleep-15 fresh re-read of the `do-not-automerge`
label (stale-payload race), skip-arming while the PR's own in-diff session
card is still `in-progress` (arm only once the branch is FINAL; re-arms on
`synchronize` when the card flips `complete`), then
`gh pr merge --auto --squash` with a `Head-ref:` provenance line in the squash
body. Token: `secrets.ROUTINE_PAT || secrets.GITHUB_TOKEN`.

Host adaptation (the one deliberate divergence): the job-level branch-prefix
allowlist uses THIS repo's empirical prefixes surveyed from PR heads #1–#49
(`claude/`, `control/`, `sim/`, `harness/`, `closeout/`, `verdict-`,
`intake-`, `heartbeat-`, `finalize-`, `order-`) plus `fix/` from the
reference list — copying idea-engine's list verbatim would have matched
almost none of sim-lab's real branches, the exact silent-no-op class the
reference's own tripwire ledger documents (its PR #54 incident).

**The bootstrap problem, explicitly:** PR 1 (this branch,
`fix/order-003-merge-on-green`) cannot land itself via the enabler it ships.
It is parked READY+green per the ORDER and per this card's born-red status —
the in-progress-card guard refuses to arm while this card says
`in-progress`, and no agent enables auto-merge on it by hand. The
coordinator lands PR 1 (and flips this card `complete` at close-out). Note:
on `pull_request` events GitHub runs the workflow from the PR's merge ref,
so the enabler DOES execute on PR 1 itself — the born-red card guard is
what keeps it from self-arming. **PR 2 provides the done-when evidence**: the
first subsequent matching-prefix PR that lands with zero agent merge calls,
cited in `control/status.md` per the ORDER's done-when.

## Run command

```
python3 bootstrap.py check --strict
```

## 💡 Session idea

Left for the close-out (coordinator): candidate — the empirical
prefix-allowlist survey (PR heads → startsWith list) is a hand step here;
idea-engine's `--branch-prefix-drift` preflight tripwire is the standing
version and could be mirrored into this repo's check seam the day the
allowlist first drifts.

## ⟲ Previous-session review

Prior card `2026-07-12-verdict-013-oracle-copy-drift.md`: clean and complete
(previous-session review, verdict reject with FP-free-frontier evidence,
slice boundary honored — control/ appends left to the coordinator, PR parked
READY). Its "park READY, coordinator lands" discipline is exactly the shape
this ORDER 003 slice retires for future PRs: after the enabler is on main,
matching-prefix READY PRs arm themselves and merge on green with no agent
merge call. Nothing to fix.

## Close-out

PR 1 (#50) merged to main @ `e11ed40d713f1c1f6a8a41bf478f60371e777811` —
the enabler is live. This card flip is PR 2 (`fix/order-003-evidence`), the
done-when observation run: opened READY, no agent merge call, expected to be
landed by the auto-merge-enabler itself.

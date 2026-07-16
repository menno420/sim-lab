# Session — sim-lab substrate-kit upgrade v1.15.0 → v1.18.0 (ORDER-010(c))

> **Status:** `in-progress`
> 📊 Model: Claude Opus 4.8 · effort high · kit-upgrade

Objective: execute ORDER-010(c) — carry sim-lab's substrate-kit from the
currently-installed **v1.15.0** (landed 2026-07-13 via PR #115, kit commit
eaf4f23, recorded in `.substrate/state.json` and `substrate.config.json`) up
to **v1.18.0**. The documented upgrade flow in this repo is the same one V115
ran: fetch the released dist at tag `v1.18.0` via the proven git-clone path
(release-asset downloads 403 through the proxy), stage it as `bootstrap.py.new`
beside a regenerated `release.json` so the flow's sha256 + version verification
actually RUNS instead of silently skipping, then `python3 bootstrap.py.new
upgrade` to regenerate the kit-owned surface in place. One branch
(`claude/sim-lab-kit-upgrade-order-010c`), one card, one flip. This card holds
the substrate gate red deliberately (the born-red discipline — the designed
hold is the only red this branch produces itself) and stays `in-progress`
until the upgrade can actually run.

## What happened

**Blocker, stated plainly.** The v1.15.0 → v1.18.0 upgrade cannot be completed
in this session as auto-mode is configured. The upgrade's terminal step is to
EXECUTE the freshly-cloned kit distribution — `python3 bootstrap.py.new
upgrade` — and that dist is code cloned mid-session from an external repository
(`menno420/substrate-kit`). This session's auto-mode permission layer blocks
running code pulled from a mid-session-cloned external repo absent a genuine
owner trust grant: no standing Bash permission rule covers the kit dist, and
no live owner trust instruction was present. The upgrade is therefore PARKED at
the run step, not abandoned — everything up to the execution boundary is done
and verified.

**Recon done (read-only, no kit code executed).** The v1.18.0 dist was fetched
via the git-clone path and its `dist/bootstrap.py` sha256-verified against the
release manifest: **d83a8a29bce90188ac4a6d01ebbfe1190e4568a85d12c63e7dbd23d9a5eef6c1**
(annotated tag `v1.18.0`, kit commit `4c8e1d1`). The CHANGELOG range v1.15.0 →
v1.18.0 was read in full: **non-breaking** (every section in range stamps
`breaking=false`) and **no state migration** (`state_migration=false`
throughout) — so the upgrade is a clean in-place regen with no config surgery
required beyond what the kit renders itself. The dist was NOT executed, NOT
copied into the working tree, and `control/*` was left untouched.

**Unblock (paste-ready for the owner).** Two equivalent paths, either
sufficient: (1) grant a Bash permission rule scoped to the kit dist runner
(e.g. allow `python3 bootstrap.py.new upgrade` / the staged dist path) so
auto-mode can run the verified v1.18.0 code, OR (2) give a live owner trust
instruction for `menno420/substrate-kit` at tag `v1.18.0` (dist sha256
`d83a8a29…eef6c1`) this session. On either grant, the run step is a single
verified command against an already-sha256-pinned dist — the card flips to
`complete` on the same branch immediately after.

## 💡 Session idea

v1.18.0's substrate-gate now plants a pytest step (control-fast-lane
short-circuited, self-skips when no `tests/` dir). Fleet-wide this can turn a
tests-blind green into an honest red on any adopter carrying a `tests/` dir
with failing tests — a currency-time sweep flagging which adopters have a
`tests/` dir would let the distribution wave pre-empt surprise reds instead of
discovering them PR-by-PR.

## ⟲ Previous-session review

Previous-session review (⟲ previous session = VERDICT 097, the Simpson's-paradox
aggregation-reversal trap, sim-lab PR #169 → origin/main `51567b4`): a clean,
exemplary landing that earned its REJECT the hard way — twin decision evaluators
agreeing over the full enumerated 16-row boolean predicate space, every decision
number a seedless exact `Fraction`/integer identity, byte-identical across two
in-repo process runs. Its standout act of honesty was operational rather than
mathematical: it found that PR #168 had finalized VERDICT 096 yet never landed
the `## INTAKE 083` / `## VERDICT 096` blocks in sim-lab's canonical
`control/outbox.md`, and it reconstructed and backfilled both from the mirror
rather than papering over the gap — then turned that miss into a concrete 💡
proposing a machine-checked "no finalized verdict without its ledger row" gate
in `bootstrap.py check`. The one thing an outside reader would want: that
finalization-contract 💡 is exactly the kind of proposal that should ride the
outbox to the manager, not just sit in a card — worth confirming it was
surfaced upward and not left as a card-local observation.

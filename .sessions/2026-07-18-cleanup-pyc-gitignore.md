# CLEANUP — remove swept-in Python bytecode (__pycache__/*.pyc) from the tree and add a repo-root .gitignore so compiled artifacts can never sweep back in

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · review/verify

Born in-progress as this session's FIRST commit (born-red HOLD); it holds `substrate-gate` red until the removal + `.gitignore` land and the close-out is written — the flip to `complete` is the deliberate LAST step, not part of this opening commit.

## GROUNDING
Verified at HEAD, not assumed. Branch `claude/cleanup-pyc-gitignore` off origin/main HEAD `7d71fbec9fd35e0151345cf69703e5593903b653` (VERDICT 123, #196). `git ls-files | grep -E '__pycache__|\.pyc$'` reports 34 tracked compiled-bytecode files — one stray in `sims/verdict-123-discount-depth-breakeven/__pycache__/discount_breakeven_trap.cpython-311.pyc`, one in `sims/verdict-029-comp-stipend/__pycache__/`, and 32 under the two `sims/verdict-075-*` / `sims/verdict-076-*` fishing/mining fixture trees. No repo-root `.gitignore` exists (`test -f .gitignore` → absent), so nothing prevented the sweep. These are build outputs — deterministic, regenerated on any `python3` run — never source; committing them is pure noise and invites cross-platform diff churn. Scope is exactly: `git rm` every tracked `__pycache__`/`*.pyc` path + add a repo-root `.gitignore` covering `__pycache__/` and `*.pyc`. No sim source, fixture `.py`, or verdict artifact (results.json / run-stdout.txt) is touched.

## Objective
Remove all 34 tracked Python-bytecode files from the tree and add a repo-root `.gitignore` so `__pycache__/` and `*.pyc` can never be committed again. Confirm `git ls-files | grep -E '__pycache__|\.pyc$'` returns empty and `python3 bootstrap.py check --strict` exits 0 after the change.

## What happened
`git rm` removed all 34 tracked bytecode files (the `sims/verdict-123-discount-depth-breakeven/__pycache__/*.pyc` stray plus the verdict-029 and verdict-075/076 fixture `__pycache__` trees); a new repo-root `.gitignore` was added with `__pycache__/` and `*.pyc` (plus the common `*.pyo`/`*.pyd` siblings) so the sweep cannot recur. Post-change `git ls-files | grep -E '__pycache__|\.pyc$'` is empty and `python3 bootstrap.py check --strict` exits 0. No source, fixture, or verdict artifact was modified — bytecode-only removal.

## ⟲ Previous-session review
The prior loop landed VERDICT 123 (P110 → V123, the discount-depth breakeven trap) via sim-lab PR #196 @ `7d71fbec` (merge-on-green after the born-red card flip), which is exactly the merge that swept the `sims/verdict-123-discount-depth-breakeven/__pycache__/discount_breakeven_trap.cpython-311.pyc` stray into the tree — the verifier was executed in-place to reproduce the digest and the compiled output rode along because no `.gitignore` guarded against it. This cleanup closes that recurrence class repo-wide, not just for V123: the same absence of a root `.gitignore` is why the older verdict-029 and verdict-075/076 fixture bytecode is also tracked. Guard recipe for the next session: the `.gitignore` added here is the durable fix — if new `*.pyc` ever reappear under `git ls-files`, check that the root `.gitignore` still carries `__pycache__/` and `*.pyc` before re-removing, since a lost ignore rule is the only way they return.

## 💡 Session idea
A one-line CI tripwire would make this cleanup self-enforcing instead of periodic: a `substrate-gate` advisory that fails (or warns) when `git ls-files | grep -E '__pycache__|\.pyc$'` is non-empty turns "an agent notices and sweeps stray bytecode" into "the gate refuses the commit that introduces it." The same pattern generalizes to any never-commit build output (`.DS_Store`, editor swap files, coverage dumps) — a single tracked-artifact denylist checked at gate time is strictly cheaper than the recurring manual prune, and it converts a `.gitignore` (which only stops *new* adds by cooperating clients) into an enforced invariant that also catches an artifact added with `git add -f` or by a client that ignores the ignore file.

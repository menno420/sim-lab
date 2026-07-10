# harness/

Reusable structure extracted from the first five verdict sims so the next
verdict is cheaper than the last. **Stdlib-only Python + markdown templates.**

Sims stay self-contained (the layout contract): they never import the harness
at runtime. This directory is a **copy source** -- vendor-copy the pieces you
need into `sims/<slug>/`. Releases are git-tagged (`harness-vX.Y.Z`); consume a
pinned tag via raw/copy.

## What's here

| file | what | provenance |
|---|---|---|
| `simharness.py` | seeded-run + sweep + self-check + frozen-run helpers | see per-symbol docstrings |
| `REPORT_TEMPLATE.md` | 8-section REPORT skeleton + 5 verbatim gate questions + verdict grammar | all five REPORTs, `sims/REFERENCE.md` |
| `selftest.py` | consumer proof: exercises every helper, exit 0 | -- |

### `simharness.py` symbols
- `SEEDS = [11, 23, 42, 101, 2027]` -- the standard multi-seed set. *intake-002/003, verdict-004.*
- `mean_sd(xs)` -> `(mean, pstdev)`. *intake-003, verdict-004 (byte-identical).*
- `CrnCache` -- Common-Random-Numbers cache (variance reduction). *intake-003 `_HONEST_CACHE`, verdict-004 `_NOISE`.*
- `sweep(grid, run)` -- full cartesian grid, whole table (anti-cherry-pick). *intake-002, intake-003, verdict-004.*
- `SelfCheck` -- pass-counter battery: `check` / `expect_reject` / `expect_ok` / `in_set` / `report`, raising `SELF-CHECK FAILED: ...`, terminal `SELF-CHECKS: n passed, 0 failed`. *all five.*
- `determinism_check` (run-twice) / `determinism_bytes` (canonical JSON). *intake-003, verdict-004 / verdict-005.*
- `load_frozen_runs`, `modal`, `agreement_rate` -- frozen-run analyze pattern (live layer -> frozen JSON -> deterministic analyzer). *intake-001, verdict-005.*

## Start a new verdict from this
1. `mkdir sims/<idea-slug>/`; copy `REPORT_TEMPLATE.md` -> `sims/<slug>/REPORT.md`.
2. Vendor-copy the helpers you need from `simharness.py`. Numeric sim: `SEEDS`, `mean_sd`, `CrnCache`, `sweep`, `SelfCheck`, `determinism_check`. Frozen-run prototype: `load_frozen_runs`, `modal`, `agreement_rate`, `SelfCheck`, `determinism_bytes`.
3. End the sim on `sys.exit(sc.report())` -- exit 0 iff every self-check passes.
4. One documented run command in the sim's README; fill the five gate answers honestly.

## The one rule
A harness change ships **only with a consumer proving it in the same PR**. This
extraction ships with `selftest.py` as its consumer; the first real sim consumer
vendor-copies on the next verdict.

## Self-test
```
python3 harness/selftest.py
```
Exit 0 iff every helper behaves as the source sims relied on.

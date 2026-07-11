# owner-001 — superbot-next (NEW) vs superbot (OLD): settings / command / UX surface

Deterministic, self-checked, stdlib-only analysis comparing the settings,
command, and panel/UX surface of **superbot-next** against **superbot**, from
static inventories committed under `data/`.

## Run

```
python3 sims/owner-001-superbot-next-settings-ux/settings_ux_sim.py
```

Exits 0 on success, prints `SELF-CHECKS: n passed, 0 failed`, prints
`determinism: byte-identical on re-run`, and writes `results.json` (canonical,
`sort_keys`) next to the script. The analysis runs twice internally and asserts
the two `results` are byte-identical, so the run is its own reproducibility
check.

## Inputs (committed, so the sim is reproducible from data alone)

`data/next/*` and `data/old/*` are verbatim copies of machine-readable
inventories extracted from the two repos. Per-version files:

- `settings.json` — `{name, subsystem, type, default, scope, set_where,
  set_ref, read_where:[file:line…], notes}` — NEW 125, OLD 118.
- `commands.json` — `{name, subsystem, kind, ref, opens_panel}` — NEW 367,
  OLD 484 (raw entries, incl. prefix/slash duplicates of the same name).
- `panels.json`  — `{panel, subsystem, ref, widgets:[…], opened_by,
  buttons:[label->action…]}` — NEW 165, OLD 29.

## Pinned source SHAs

- superbot-next (NEW): `168ef8080347905766893fd92ae3be1ec2ebbc4c` (main)
- superbot     (OLD): `9f46cb7840cb2216a012002fe27feb342d45f480` (main)

## What it computes

1. **Inventory diff** — kept/added/removed/moved settings (by exact name);
   rename CANDIDATES (flagged, never asserted); command deltas (raw + distinct)
   with per-subsystem breakdown. Partition invariants self-checked.
2. **Redundancy** — dead settings (no reader), display-only settings (read only
   at a `panels.py` render site), duplicate-effect groups (identical read-site
   sets), subordinate pairs (read-set strict subset of a master toggle).
3. **Combinability** — structural co-read collapse (measured, robust) plus a
   seeded config-space demonstration (SUPPORTING; an explicitly-declared
   read-site-activation MODEL, not executed branch logic).
4. **Reachability** — a directed graph (commands → panels → settings) with
   BFS `steps_to_reach` per setting, discoverability from the top-level
   `/settings` entry, path multiplicity, consistency across matched settings,
   and a one-setting-per-subsystem task battery.
5. **UX delta** — signed OLD→NEW deltas per proxy metric; regressions named.

See `REPORT.md` for the filled numeric sections, the five-question validity
gate answered honestly, the model's stated limits, and the draft verdict.
The harness helpers used (`SEEDS`, `mean_sd`, `sweep`, `SelfCheck`,
`determinism_bytes`) are vendor-copied into the script — the sim never imports
the harness at runtime.

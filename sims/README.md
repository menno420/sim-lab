# sims/ — one idea, one subtree

> **Status:** `binding` (structure). Each `sims/<idea-slug>/` is self-contained: model,
> seeds, ONE documented run command, own README, and a results report that ends in the
> five validity-gate answers + the verdict + the best-implementation recommendation
> (grammar: repo `README.md`). Seeded/deterministic; sweep reported, not cherry-picked.
> Sims never import each other; a sim may vendor-copy from `harness/`; a dependency is
> pinned inside the sim's own subtree, never repo-globally.

`REFERENCE.md` (written at coordinator boot, step 2 of the founding package §2) is the
worked example every later verdict imitates — the verdict grammar applied to superbot's
`tools/sim/gen3_deployment_sim.py` precedent.

*(no sims yet — the first is the Idea Engine's PROPOSAL 001, waiting in its outbox)*

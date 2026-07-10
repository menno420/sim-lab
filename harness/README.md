# harness/ — the reusable sim harness (standing second product, Q-0264.7)

> **Status:** `skeleton` — extract what REPEATS across sims, never speculate ahead of a
> second consumer. Target contents: a sim template + tiny stdlib-only helpers (seeded
> runs, parameter sweeps, report emission, the validity-gate checklist as a fill-in
> section). Versioned by git tags; other Projects consume via **raw/copy** — never as an
> install dependency. It graduates to kit distribution only if adoption goes fleet-wide
> (substrate-kit §6 pattern) — do not couple to the kit prematurely. A harness change
> ships only with a consumer sim proving it in the same PR.

*(empty at seed — first extraction comes from the first two sims, or from the two
superbot precedents if the queue is empty: `tools/sim/claim_layout_sim.py` +
`tools/sim/gen3_deployment_sim.py`, read via public raw)*

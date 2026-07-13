# verdict-035 · Assign-at-merge, priced — the merge-queue re-validation tax

Does the routed Option-3 assign-at-merge build survive its own operational
price? VERDICT 023 (idea-engine PROPOSAL 021) REJECTED the shipped Option-1
checker as sufficient and routed the Option-3 build while stating verbatim
"nothing here prices Option 3's build cost" — its P3 was a FREE oracle
(number assigned at the merge instant, durations exactly W+V). Any REAL
assign-at-merge mechanism serializes migration-bearing merges through the
shared sequence and pays a re-validation V_q at the head of that line: an
M/D/1 queue with its own arithmetic (rho = lambda*V_q, Pollaczek-Khinchine
waiting, a hard ceiling at rho -> 1). This sim prices that queue per cell
against the parent's committed P1 residual. Answers idea-engine PROPOSAL 033
(control/outbox.md 2026-07-13T08:43:05Z, idea
`ideas/superbot/assign-at-merge-queue-tax-2026-07-13.md`, landed via
idea-engine PR #303, main `11c5a1f`) — the standing ORDER 003 FLEET-BACKLOGS
rotation slot, round 5, round 2's own verdict-opened thread (the successor
move P023<-V022 / P026<-V024 / P029<-V027 / P030<-V020 applied to the fleet
slot's superbot line for the first time).

Frame (inherited from P021/V023 verbatim): Poisson migration-bearing PRs
lambda in {1, 4, 12}/day; develop W = 8 h; validate V in {0.25, 2, 24} h;
H = 2,000 h, warm-up 200 h, M = 40. Policy P3Q: after validation a PR enters
a FIFO queue for the shared migration sequence; one PR served at a time;
service = one deterministic re-validation V_q; number assigned at merge —
zero renumbers by construction, MEASURED as exactly zero on every leg (the
V023 P3-control discipline). Decision cells: the FIVE treadmill cells V023's
REJECT bound. WIN(cell, V_q) := Arm-A-exact W + V + lambda*V_q^2/(2(1-rho))
+ V_q <= the cell's committed P1 mean AND rho < 0.9 (the pre-registered
stability exclusion; its only decision-grid member is lam12 x V_q = 2,
rho = 1.0 exactly). V_q*(cell) = the largest winning V_q in {0.1, 0.5, 2} h.

Dual arms: Arm A exact seedless M/D/1 closed forms (the decision arm — the
ruling rides exact-Fraction arithmetic against the committed anchors, quoted
verbatim from `sims/verdict-023-renumber-treadmill/results.json` @ `c7340ae`;
HEAD byte-identical and the parent's committed runner re-run once out-of-sim,
results.json byte-identical — the V031 precedent). Arm S seeded event-driven
MC of the whole queue (seeds 20260768 main / 20260769 stability half-M /
20260770 reporting / 20260771 aux, strictly above the P031 high-water
20260767), familywise-calibrated ~3.5-sigma gates (the V027/V031 lesson),
Little's law + busy-fraction identities, M/M/1 jitter leg, draw-count
sentinels, twin queue engines, twin decision evaluators, and the V_q = 0
control leg reproducing the committed P3 means {8.25, 10.0, 32.0} EXACTLY.

Decision (registered order, REJECT first): REJECT iff V_q* exists in <= 2 of
5 treadmill cells; APPROVE iff V_q* >= 2 h in >= 4 of 5, stability-reproduced;
NULL otherwise — the per-cell V_q* frontier table IS the citable pin.
**Measured ruling: NULL** — a winning V_q exists in ALL 5/5 treadmill cells
(REJECT misses), but V_q* >= 2 h in only 2/5 (APPROVE misses): the frontier
is real and binding on the lambda axis (the rho ceiling excludes lam12 x 2 h)
and the V = 2 same-day-review column (only ~1.42 h of headroom).

## Run (one command)

```
python3 sims/verdict-035-assign-at-merge-tax/assign_merge_tax_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: pinned seeds, pinned loop
order, no network, no git, no wall clock; reads only its own fixtures.json.
Progress to stderr only. stdout + results.json byte-identical across two
process runs (external diff). CPython 3.11 pinned and asserted. ~2.5 s.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file / the parent's committed results.json, the decision rule with its
  evaluation order, the familywise SE arithmetic with pre-run worked examples
  and the pinned breach protocol, and twelve intake-time decisions (committed
  BEFORE the runner — git history is the trail).
- `assign_merge_tax_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).

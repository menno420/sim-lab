# verdict-083 — the sample-window front-matter toll (INTAKE 070)

Prices idea-engine PROPOSAL 070's unpriced committed convention where it
lives: the assembly order of front matter in venture-lab's produced books
(title, copyright, dedication, TOC, content note — default: everything up
front) against the retail sample window it silently spends. A
Look-Inside-style sample is modeled as what the head literally claims: a
BUDGET of B = ceil(alpha * (F + S)) display units counted from byte one,
which the artifact's own front matter F spends before the story's S units
start; a browsing reader survives each unit with probability q (geometric
attrition) and converts iff k* hook story-units are read INSIDE the
budget: C = q^(F + k*) * 1[F + k* <= B]. Four committed formats at their
measured lengths @ venture-lab `520bdfc` (NOVELLA 27,890 w -> 112
screens; EPISODE 8,809 w -> 36 screens; PB15 30 story pages; PB12 24
story pages), assembly policies prose F in {1..4} screens / picture book
F in {2,3,4} pages, grids alpha in {1/20, 1/10, 1/5} x q in {4/5, 9/10,
19/20, 49/50} x k* in {2,3,5} screens / {1,2} spreads, decision cell
(alpha = 1/10, q = 19/20, k* = 3 screens / 1 spread). Judged against
pre-registered bands, REJECT-first (FRONT-LOADED F = 4 cliffs C = 0 on
>= 3 of 4 committed formats AND the NOVELLA toll C(F=1)/C(F=4) >= 11/10),
then INVALID, then APPROVE (zero cliffs AND toll <= 21/20), then NULL on
named axes. The runner is hermetic — it reads ONLY `fixtures.json`
(committed before the runner); zero repo/network reads at verdict time;
the MEASURED fixture constants were re-verified firsthand at venture-lab
`520bdfc` before the fixture was written.

## Run

```
python3 sims/verdict-083-sample-window-front-matter-toll/sample_window_toll_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, < 1 s. Every
decision number is an exact rational; the only seeded arm (R) is
reporting-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  070 block / idea file (the budget/conversion model, the four committed
  formats with their measured constants, the alpha x q x k* grids and
  decision cell, the T3 two-point mixture, the G6 census anchors
  including toll 8000/6859 and the 3-of-4 cliff census, the G5 hand
  worlds, Arm-R parameters {100,000 main / 20,000 stability traces at 3
  cells}, seeds 20261620-623), plus fixture-level conventions C1-C11 —
  committed BEFORE the runner existed.
- `sample_window_toll_sim.py` — three-arm runner: Arm A seedless closed
  form (exact Fractions; decision-bearing), Arm B INDEPENDENTLY-WRITTEN
  brute unit-walk enumeration twin (walks the truncated artifact unit by
  unit, multiplying survival and counting story units to the hook — never
  via the closed form; second decision evaluator recomputes from Arm B
  alone), Arm R seeded reader-trace MC at the three surviving
  decision-grid cells (main 20261620, stability 20261621, presentation
  20261622, aux 20261623 NEVER read).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the exact conversion/toll/cliff/S* surfaces, the
  three theorem verifications (T1 exponential toll, T2 viability cliff +
  S* law, T3 mixture log-convexity), the margin-0 knife-edge ledger, the
  hand worlds, the twin-arm and byte-identity notes, and the Arm-R traces
  beside the exact values.

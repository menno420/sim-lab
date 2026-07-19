# VERDICT 187 — the IRR speed trap (reproduce PROPOSAL 174)

## Probe report

Factual reproduction record for `ideas/venture-lab/irr_speed_trap.py` (idea-engine
PROPOSAL 174, PR #664) copied byte-identical into sim-lab and run under SEED=20260717.
Every value below is the MEASURED value from this session's run (`run-stdout.txt`),
not a target restatement. Idea-engine reference read at main `34e3776`.

### 1. Does the verifier copy match the idea-engine source byte-for-byte?

MEASURED — YES. `diff ../ie-ro/ideas/venture-lab/irr_speed_trap.py
sims/verdict-187-irr-speed-trap/irr_speed_trap.py` returned no output, diff exit 0.
Sim-copy file sha256 `13ecd4b4e0b220a4f48d366d39b8d89b6a3943aa746b87cb5057f9cd6e1b0547`,
git blob `3fb977e630e04108072c8a6402653bf16e93067a` — both equal the disclosed
reference hashes exactly. Byte-identity confirmed.

### 2. Does the results-dict digest reproduce byte-exact?

MEASURED — YES, MATCH. Printed line:
`Results-JSON sha256 552e98a09fd8f8c069156ab40d35dca2049671702e5e11f8d40a52fba3f2736f`.
Disclosed digest: `552e98a09fd8f8c069156ab40d35dca2049671702e5e11f8d40a52fba3f2736f`.
Character-for-character identical — MATCH.

### 3. Is the run deterministic across invocations?

MEASURED — YES. Two separate `python3 irr_speed_trap.py` invocations (both exit 0)
produced byte-identical stdout: `diff run-stdout.txt run2.txt` exit 0. The verifier's
own in-process double-run assert (`compute()` run twice, `assert a == b`) reports
`double_run_identical=true` in the output. Deterministic across invocations and in-process.

### 4. Is the SEED honestly pinned?

MEASURED — YES. SEED=20260717 is a module-level in-source constant. Both invocations
were run with `SEED=20260717` exported into the environment; the printed digest is
identical to the disclosed value that was produced without any env override, confirming
the env var is inert (the file imports no `os` and reads no env var). Timing/value
determinism rests on the in-source seed alone.

### 5. Do all three gates pass in order with z ≥ 3.0?

MEASURED — YES, all three pass in order G1 → G2 → G3; `all_pass=true`,
`first_failing_gate=null`. All z-values far exceed the Z_GATE=3.0 threshold and each
reproduces the proposal target within float rounding.

| Gate | Metric | Measured | Proposal target |
|------|--------|----------|-----------------|
| G1 | mean IRR gap | 0.147747 | 0.147747 |
| G1 | z | 789.30361 | ≈789.30 |
| G1 | inversion fraction | 0.99506 | ≈0.99506 |
| G1 | pass | true | true |
| G2 | mean delta-IRR | 0.013764 | +0.013764 |
| G2 | delta-IRR z | 756.063137 | ≈756.06 |
| G2 | mean delta-MOIC | -0.146102 | −0.146102 |
| G2 | delta-MOIC z | -1093.342507 | ≈−1093.34 |
| G2 | pass | true | true |
| G3 | mean IRR gap | 0.032235 | 0.032235 |
| G3 | z | 251.423783 | ≈251.42 |
| G3 | inversion fraction | 0.8858 | ≈0.8858 |
| G3 | pass | true | true |

No discrepancy beyond float-rounding on any field. `double_run_identical=true`,
`all_pass=true`, `first_failing_gate=null`.

### 6. Is the mechanism sound, not a strawman?

MEASURED — YES. IRR conflates the SPEED of cash flows with their MAGNITUDE.
G1 (200k bullet pairs) shows the fast low-MOIC fund out-IRRs the slow high-MOIC fund
in 99.506% of pairs (mean gap +0.147747) purely from the shorter clock T. G2 charges
the subscription line's compounded interest ((1+c)^τ−1) against the LP distribution:
mean delta-MOIC is strictly negative (−0.146102, z=−1093.34, LP receives FEWER dollars)
while mean delta-IRR is strictly positive (+0.013764, z=756.06, reported IRR RISES) —
higher IRR with fewer dollars is measured, not assumed, moving on the T→T−τ timing alone.
G3 reproduces the inversion (+0.032235, 88.58%) under a shifted, staged J-curve
distribution solved by bisection, so the effect is not an artifact of the bullet closed form.

### 7. Does grounding document the specific head?

MEASURED — live HTTP 200. `curl` to
https://en.wikipedia.org/wiki/Internal_rate_of_return returned HTTP 200 this session.
The durable anchor — the reinvestment-at-IRR text — is present: grepping the fetched
page for `reinvest[a-z]*` returned multiple hits (`reinvestment`, `reinvested`). This
matches the proposer honesty note that the durable anchor is the reinvestment text plus
the M^(1/T)−1 algebra, not a verbatim heading string (markup interleaves the words).

### 8. Real venture phenomenon or textbook toy?

Real phenomenon. LP league tables rank managers on realised IRR, and subscription
(capital-call) credit lines are widely used to defer LP draws and lift reported IRR.
The head — ranking on IRR rewards SPEED over DOLLARS, with DPI/MOIC/TVPI the honest
dollars metric — is a documented practice, and the G2 subscription-line result quantifies
it: the metric moves on timing alone even as the LP nets fewer dollars.

## Ruling

APPROVE. The digest reproduces EXACTLY
(`552e98a09fd8f8c069156ab40d35dca2049671702e5e11f8d40a52fba3f2736f` MATCH), the copy is
byte-identical (diff exit 0, file sha256 `13ecd4b4…6e1b0547`, git blob `3fb977e6…3067a`),
the run is deterministic (two-invocation diff exit 0 plus in-process `double_run_identical=true`),
and all three gates PASS in order on the proposal's own pre-registered thresholds
(G1 z=789.30, G2 delta-IRR z=756.06 / delta-MOIC z=−1093.34, G3 z=251.42; `all_pass=true`,
`first_failing_gate=null`), with grounding live (HTTP 200, reinvestment text present).
On this clean reproduction the verdict high-water advances V186 → V187 (union-max, no regress).

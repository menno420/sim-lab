# VERDICT 189 — the giant-component phase transition (reproduce PROPOSAL 176)

## Probe report

Factual reproduction record for `ideas/fleet/giant_component_threshold.py`
(idea-engine PROPOSAL 176, PR #668) copied byte-identical into sim-lab and run under
SEED=20260717. Every value below is the MEASURED value from this session's run
(`run-stdout.txt`), not a target restatement. Idea-engine reference read at main
`8cfa363` (merge SHA `8cfa36367c859f54dc04cc996a369c86edd27ed8`). Report generated
2026-07-19T16:56:26Z.

📊 Model: Claude

### 1. Does the verifier copy match the idea-engine source byte-for-byte?

MEASURED — YES. `diff ../idea-engine/ideas/fleet/giant_component_threshold.py
sims/verdict-189-giant-component-transition/giant_component_threshold.py` returned no output,
diff exit 0.

| Artifact | sha256 | git blob |
|----------|--------|----------|
| idea-engine source | `c05dfc968d857921bf20ce400a7e8277b64eed16abbf08c7ef1dee28463ad9b2` | `2e4026b882de13b3677a4c424b8d51946205d6e7` |
| sim-lab copy | `c05dfc968d857921bf20ce400a7e8277b64eed16abbf08c7ef1dee28463ad9b2` | `2e4026b882de13b3677a4c424b8d51946205d6e7` |

Both hashes equal the source exactly. Byte-identity confirmed. Source pin: idea-engine
PROPOSAL 176, PR #668, merge SHA `8cfa36367c859f54dc04cc996a369c86edd27ed8`.

### 2. Does the results-dict digest reproduce byte-exact?

MEASURED — YES, MATCH. Printed line:
`Results-JSON sha256: 14875022bef41594dbc8d19bd2960724d2f86f6dedcadf1b339f228915469537`.
Disclosed digest:
`14875022bef41594dbc8d19bd2960724d2f86f6dedcadf1b339f228915469537`.
Character-for-character identical — MATCH.

### 3. Is the run deterministic across invocations?

MEASURED — YES. Two separate `python3 giant_component_threshold.py` invocations (both exit 0)
produced byte-identical stdout: cross-invocation `diff` exit 0. The verifier's own in-process
double-run guard (`main()` runs `compute()` twice and asserts byte-identical
compact-canonical `json.dumps(..., sort_keys=True, separators=(",",":"))` serializations)
passed without triggering nondeterminism. Deterministic across invocations and in-process.
SEED=20260717, trials=40, z_gate=3.0.

### 4. Is the SEED honestly pinned?

MEASURED — YES. SEED=20260717 is a module-level in-source constant. The file imports no `os`
and reads no env var; a single `random.Random(SEED)` stream is drawn in a fixed condition
order, so any `SEED` env export is inert and the printed digest is produced by the in-source
seed alone.

### 5. Do all three gates pass in order with z ≥ 3.0?

MEASURED — YES, all three pass in order G1 → G2 → G3; `all_pass=true`,
`first_failing_gate=null`. Z_GATE=3.0; every measured z far exceeds it.

| Gate | Description | Metric | Measured | Pass rule |
|------|-------------|--------|----------|-----------|
| G1 | existence: giant appears above, absent below | sup_mean (n=4000, c=1.4) | 0.507138 | ≥ 0.30 |
| G1 | | sub_mean (n=4000, c=0.7) | 0.008025 | ≤ 0.08 |
| G1 | | z of difference | 263.375801 | z ≥ 3.0 → pass true |
| G2 | robustness (4× scale shift) | sup_mean (n=16000, c=1.4) | 0.511348 | ≥ 0.30 |
| G2 | size-invariance | size_gap | 0.004211 | ≤ 0.05 |
| G2 | subcritical shrinks with n | sub 0.008025 → 0.002861 | sub_shrinks true | m_sub2 < m_sub1 |
| G2 | | z_vs_floor | 204.254546 | z ≥ 3.0 → pass true |
| G3 | sharpness / placebo | jump_near (frac 1.1 − frac 0.9) | 0.159642 | — |
| G3 | | jump_far (frac 0.7 − frac 0.5) | 0.001612 | — |
| G3 | growth concentrated at c ≈ 1 | z of jump difference | 33.80426 | z ≥ 3.0 → pass true |

`all_pass=true`, `first_failing_gate=null`. No discrepancy beyond float-rounding on any field.

### 6. Is the supercritical giant fraction genuinely intensive (size-invariant), or a finite-n artifact?

MEASURED — intensive. The c=1.4 fraction is 0.507138 at n=4000 and 0.511348 at n=16000
(gap 0.004211 ≤ 0.05), i.e. size-invariant across a 4× scale shift, while the c=0.7
subcritical fraction shrinks 0.008025 → 0.002861 (order log n / n → 0) over the same shift.
The giant is a constant fraction of the graph; the subcritical clusters are not.

### 7. Does the measured supercritical fraction match the mean-field fixed point ρ = 1 − exp(−c·ρ)?

MEASURED — YES. The giant emerges at the critical average degree c = 1; the surviving
fraction solves the mean-field fixed point ρ = 1 − exp(−c·ρ), which has a positive root
ρ > 0 only for c > 1. At c = 1.4 that root is ρ(1.4) ≈ 0.516. The measured supercritical
fraction climbs with n toward that asymptote — sup 0.507138 (n=4000) → 0.511348 (n=16000) —
consistent with finite-size approach to ρ(1.4) ≈ 0.516 from below.

### 8. Does grounding document the specific c = 1 threshold head?

MEASURED — live, HTTP 200. Grounding
`https://en.wikipedia.org/wiki/Giant_component@66da05b62033927be39802f77888c6408fdee263`
(pinned content hash) confirms the durable anchor: a giant component emerges at the phase
transition where the average degree c crosses 1 (the exact c = 1 head), and the surviving
fraction obeys P_∞ = 1 − exp(−⟨k⟩·P_∞) — the ρ = 1 − exp(−c·ρ) fixed point the verifier
anchors to.

### Dedup vs P105

Distinct from the P105 functional-graph head (a random mapping where every node has
out-degree exactly 1). This is G(n, m) Erdős–Rényi with variable Poisson degree and a
threshold at c = 1 — a different random-graph ensemble and a different mechanism (branching
criticality on a variable-degree graph, not the fixed out-degree-1 structure of a functional
graph).

### Math sanity

The giant component emerges at c = 1: exploring a node's component reaches on average c new
nodes per step, so exploration dies out (components of order log n) for c < 1 and survives to
coalesce into a single giant for c > 1. The surviving-fraction fixed point ρ = 1 − exp(−c·ρ)
has ρ = 0 as its only root for c ≤ 1 and a unique positive root ρ > 0 for c > 1; at c = 1.4
that root is ρ(1.4) ≈ 0.516. The finite-size supercritical measurements (0.507 at n=4000 →
0.511 at n=16000) climb toward that asymptotic value, exactly as expected for approach to the
thermodynamic limit from below. This is the bond-percolation universality class on the
complete graph.

**Recommendation: APPROVE — PROPOSAL 176 reproduces exactly; disclosed digest matches, determinism holds, all three pre-registered gates pass.**

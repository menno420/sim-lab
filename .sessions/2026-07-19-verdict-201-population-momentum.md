# VERDICT 201 — Population momentum (reproduce PROPOSAL 188)

> **Status:** `complete`

📊 Model: opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-19T23:41:12Z
flipped: 2026-07-19T23:50:36Z

## 💡 What this verdict does

Reproduces PROPOSAL 188 (idea-engine, round-44 UNRELATED slot): a growing population (NRR 1.5) whose fertility drops instantly to exact replacement (NRR 1.0) keeps growing for roughly a generation, ending ~29% larger, purely because the young age structure inherited from the prior growth regime still carries a reproductive surplus. Leslie-matrix renewal; the deterministic momentum M_det = 1.291976.

## Method

Copy the committed verifier `ideas/fleet/population_momentum.py` from idea-engine byte-identically into `sims/verdict-201-population-momentum/`, run under SEED=20260717 (in-source), confirm the in-process double-run and a separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest `fb74854ebd92a08fe48770136cf4e5645b47176394d1b04a70c2a0cc6ef36f33`, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 200 (Glicko RD order-sensitivity, reproduce PROPOSAL 187) landed on main, ruled APPROVE — no carryover defects.

## Result

Verifier copied byte-identically from idea-engine @0b77ba0 (`diff` exit 0; file sha256 `6f0f7485232a2109197419bb890978ed972accef541965475c43a7237220c21d`, git blob `1d5599fada651332edc99515fa736fcfee1da0f9`). Ran under the in-source SEED=20260717: two independent invocations produced byte-identical stdout (`diff` exit 0) and the in-process double-run assert held. Results-dict sha256 `fb74854ebd92a08fe48770136cf4e5645b47176394d1b04a70c2a0cc6ef36f33` MATCHES the disclosed PROPOSAL 188 digest across all 64 hex (byte-grep count 1, no truncation). Gates in order: G1 momentum-real PASS (mean_M 1.291456, z=1246.791124), G2 age-structure null contrast PASS (mean_M_null 1.000409 within the 0.02 band, z_contrast=949.016224), G3 delayed-childbearing robustness PASS (mean_M_shift 1.219339, z=1115.580283); deterministic_momentum M_det=1.291976; all_pass=true. Grounding `https://en.wikipedia.org/wiki/Population_momentum` resolves live (HTTP 200) and supports the head verbatim ("a population will continue to grow even if the fertility rate declines"); the conventional Keyfitz (1971) origin attribution is absent from that page and is honestly disclosed by the proposer as unverified-from-source — a historical-citation caveat that does not gate, the mechanism being Leslie-matrix-exact. Full run stdout: `run-stdout.txt`; detail: `probe-report.md`.

## Ruling

**APPROVE.** The population-momentum head reproduces exactly: a growing population (NRR 1.5) whose fertility drops instantly to exact replacement (NRR 1.0) keeps growing for roughly a generation and ends 29.2% larger (deterministic M_det=1.291976; stochastic mean_M 1.291456), driven solely by the young age structure inherited from the prior growth regime — the pre-reproductive bulge has not yet had its replacement-level children, so births exceed deaths until it ages through the childbearing years. All three of the proposal's own gates pass in order, the null contrast isolates age structure as the sole cause (a replacement-regime stationary structure stays flat at 1.000409), and the disclosed results-dict digest matches to the byte. The Keyfitz historical-citation caveat is disclosed and does not affect the mechanism, which is Leslie-matrix-exact.

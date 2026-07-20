# VERDICT 202 — Ski-rental keep-warm break-even (reproduce PROPOSAL 189)

> **Status:** complete

📊 Model: opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-20T00:44:31Z
flipped: 2026-07-20T00:47:02Z

## 💡 What this verdict does

Reproduces PROPOSAL 189 (idea-engine, `ideas/fleet/ski_rental_keep_warm.py`): the classic ski-rental break-even applied to a keep-warm-vs-cold decision. When idle gaps are long the break-even (rent-then-buy) policy beats always keep-warm; when gaps are short it beats always-cold; and a matched-cost exponential-idle regime recovers the randomized competitive ratio e/(e-1) ≈ 1.58. Deterministic break-even worst case approaches ~2× (ratio-of-means ~1.9× at the tested buy cost). Disclosed results-dict digest `0a0464162b20350c6d07104fed5bf62f1578021be85c0ecba18b4b07a3964c2b`.

## Method

Copy the committed verifier `ideas/fleet/ski_rental_keep_warm.py` from idea-engine byte-identically into `sims/verdict-202-ski-rental-keep-warm/`, run under SEED=20260717 (in-source), confirm the in-process double-run and a separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 201 (Population momentum, reproduce PROPOSAL 188) landed on main, ruled APPROVE — no carryover defects.

## Result

Verifier copied byte-identically from idea-engine @27d5f4e (`diff` exit 0; file sha256 `e670dafdb3ef4388a827ae2659cff8eb7844f586404674540d102be5fbd5b158`, git blob `cf5840bb0b277e7fb4f129544ddfcd6729369e1d` — identical to the source blob). Ran under the in-source SEED=20260717: two independent invocations produced byte-identical stdout (`diff` exit 0) and the in-process double-run assert held; exit 0. Results-dict sha256 `0a0464162b20350c6d07104fed5bf62f1578021be85c0ecba18b4b07a3964c2b` MATCHES the disclosed PROPOSAL 189 digest across all 64 hex (byte-grep count 1, no truncation); an independent JSON-canonical recompute reproduces the same digest. Gates in order: G1 g1_long_idle_warm_blowup PASS (z=306.250137, ratio_be=1.903787<2, ratio_warm=5.522566>2), G2 g2_short_idle_cold_blowup PASS (z=1524.124639, ratio_be=1.033101<2, ratio_cold=5.030524>2), G3 g3_matched_constant_and_shift PASS (ratio_be_match=1.579541 vs e/(e-1)=1.581977 → rel_err=0.00154<0.02, ratio_be_hyper=1.601131<2, z_hyper=124.186516≥3); all_pass=true. Grounding `https://en.wikipedia.org/wiki/Ski_rental_problem` resolves live (HTTP 200) and supports the break-even rule ("rent for 9 days and buy on the morning of day 10") and the randomized e/(e-1) ≈ 1.58 bound ("expected cost is at most e/(e-1) ≈ 1.58 times ... No randomized algorithm can do better"). The proposer's deterministic-worst-case framing as a ratio-of-means ~1.9× (approaching 2× as b→∞) rather than the literal "2-competitive" phrase is honestly disclosed and FAIR. Full run stdout: `run-stdout.txt`; detail: `probe-report.md`.

## Ruling

**APPROVE.** The ski-rental keep-warm break-even head reproduces exactly: the break-even (rent-then-buy) policy beats always keep-warm under long idle (ratio_be 1.90 vs ratio_warm 5.52) and beats always-cold under short idle (ratio_be 1.03 vs ratio_cold 5.03), and the matched-cost exponential-idle regime recovers the randomized competitive ratio e/(e-1)=1.581977 to within 0.15% (ratio_be_match 1.579541). All three of the proposal's own gates pass their criteria in order, the disclosed results-dict digest matches to the byte (with an independent recompute confirming it), and determinism holds across the in-process double-run and a separate cross-invocation. The deterministic-2 framing caveat is disclosed and fair; the mechanism is exact.

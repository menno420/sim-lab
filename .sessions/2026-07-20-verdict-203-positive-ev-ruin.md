# VERDICT 203 — positive-EV ruin (ergodicity): a +EV repeated bet ruins the typical investor (reproduce PROPOSAL 190)

> **Status:** in-progress

📊 Model: opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-20T01:24:23Z
flipped: —

Born-red HOLD: this card is the VERDICT 203 slice's FIRST commit, born `in-progress` so the PR is red until the deliberate `complete` flip after the byte-identical reproduction, digest match, gate evaluation, grounding, and `python3 bootstrap.py check --strict` all land. Flipping to `complete` is the deliberate LAST commit.

## 💡 What this verdict does

Reproduces PROPOSAL 190 (idea-engine, `ideas/venture-lab/positive-ev-time-average-ruin.py`): ergodicity economics / the Peters coin. A repeated multiplicative bet with strictly positive expected value — heads ×1.5 / tails ×0.6, each p=0.5, ensemble expected multiplier 1.05 (+5% EV) — drives the TYPICAL investor toward ruin, because the TIME-AVERAGE (geometric) growth is negative (√0.9 = 0.9486832981, −5.27%/round). Over P=20000 paths × T=100 rounds the ensemble mean final wealth rises to ~55.60 (positive EV, carried by a vanishing lucky tail) yet the median collapses to ~0.00515 and 86.23% of paths finish below their starting stake. Disclosed results-dict digest `8d04b241d3589e2e49337c087da623d73c47dbe84074eaf5596bfa39db3c5336`.

## Method

Copy the committed verifier byte-identically from idea-engine @45ad3eb into `sims/verdict-203-positive-ev-ruin/`, run under the in-source SEED=20260717, confirm the in-process double-run and a separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest (exact-string byte-grep, no truncation), and evaluate the proposal's own G1→G2→G3→G4 gates in order (≥3σ + robustness).

## previous-session review

Prior verdict card: VERDICT 202 (Ski-rental keep-warm break-even, reproduce PROPOSAL 189) landed on main, ruled APPROVE — no carryover defects. DIGEST-POSTURE carry-forward honored (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY, P127+ compact-canonical twist — verified against this script's text, not assumed); SEED pinned 20260717. Non-contiguity note: idea-engine's outbox mirror ledger still shows V201 as its latest VERDICT block (the V202 mirror to idea-engine is pending) while sim-lab has V202 landed (main HEAD 067bcfa) — union-max verdict high-water across the system is V202; V203 supersedes it.

## Result

Verifier copied byte-identically from idea-engine @45ad3eb (`diff` source↔copy exit 0; file sha256 `94d90595d7ab5e93ba7c0d235933cc0ca5c6d321dca055e4fbb239e5a24e777e`, git blob `2915195f628a7a13c99905a0cfa145424645a4ec` — identical to the source blob). Ran under the in-source SEED=20260717: the in-process double-run assert held (`double_run_identical=true`) and a separate cross-invocation produced byte-identical stdout (`diff` exit 0); exit 0. Results-dict sha256 `8d04b241d3589e2e49337c087da623d73c47dbe84074eaf5596bfa39db3c5336` MATCHES the disclosed PROPOSAL 190 digest across all 64 hex (exact-string byte-grep count 1, no truncation); an independent JSON-canonical recompute reproduces the same 64 hex. Gates in order (all measured z reproduce the disclosed value to the last digit): G1 time-avg-growth<0 (base) PASS (mean_time_avg_growth −0.0527741776, z=163.2077618449); G2 arithmetic-EV>0 (base) PASS (mean_per_round_simple_return 0.04990775, z=156.8448905713); G3 majority-ruined (base) PASS (frac_below_start 0.8623>0.5, z=102.4739147296); G4 robustness/shift world U=1.6/D=0.55 PASS (all three signs preserved: mean_time_avg_growth −0.0632973382 z=169.6825537139, mean_per_round_simple_return 0.075609 z=203.6710827592, frac_below_start 0.8627 z=102.5870518145); all_pass=true, first_failing_gate=null. Grounding: the raw-file-at-SHA pin (`raw.githubusercontent.com/elemer1/elemer1.github.io/def46918…/…The Barrier that Moved.md`) resolves live HTTP 200 and carries the claim verbatim ("multiply your wealth by 1.5 … by 0.6", "½ × 1.5 + ½ × 0.6 = 1.05", "1.5 × 0.6 = 0.9 … costs you ten percent", "eighty-six percent … less than they started … median … 0.0051"); the REST route ALSO resolved HTTP 200 this session (real commit dated 2026-06-05), so the disclosed "REST 403 → raw fetch" caveat is FAIR and conservative. Wikipedia "Ergodicity economics" corroborates (HTTP 200): heads +50% / tails −40%, E[x]=1.05x, "over time, with probability one, wealth decreases by about 5% per round". Full stdout: `run-stdout.txt`; detail: `probe-report.md`.

## Ruling

**APPROVE (clean).** The positive-EV-ruin / ergodicity head reproduces exactly: a strictly positive per-round arithmetic EV (+5%) coexists with a strictly negative time-average (geometric) growth (−5.27%/round), so the ensemble mean final wealth rises (~55.60, a vanishing lucky tail) while the median collapses (~0.00515) and 86.23% of paths finish below start. All four of the proposal's own gates pass their criteria in order with z-scores reproduced to the last digit, the disclosed results-dict digest matches to the byte (independent recompute confirming), determinism holds across the in-process double-run and a separate cross-invocation, and the grounding pin resolves via both raw-file-at-SHA and REST with Wikipedia corroboration. No model choice flips a gate sign or the order-of-magnitude — the shift world is a genuine robustness check, not a sign-rescuing knob → clean APPROVE. The disclosed REST-403 → raw-fetch caveat is fair.

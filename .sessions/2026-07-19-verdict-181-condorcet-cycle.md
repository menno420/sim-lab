# VERDICT 181 — Condorcet's voting-cycle paradox (reproduce PROPOSAL 168)

Reproduces idea-engine PROPOSAL 168 (Condorcet's voting-cycle paradox): transitive individual preferences compose into an intransitive collective majority, so a majority can prefer A over B, B over C, and C over A at once. Under impartial culture a random three-candidate electorate has no Condorcet winner roughly 8.7% of the time, and that rate rises with candidate count. The proposal's verifier `ideas/fleet/condorcet_voting_cycle.py` (idea-engine `11bb533`) is copied byte-identically into `sims/verdict-181-condorcet-cycle/condorcet_voting_cycle.py` and re-run under `SEED=20260717` with an in-process double-run plus a separate cross-invocation, both required byte-identical, against the disclosed results-dict sha256 `70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe`.

> **Status:** `complete`
> 📊 Model: Claude Opus · high effort · verdict-reproduction

**Born-red HOLD.** This card lands `in-progress` on the first commit so the substrate-gate born-red check holds the PR red until the reproduction is in. It flips to `complete` on the last commit — after the verifier copy, run stdout, and probe report are committed and the `control/status.md` heartbeat is written. This hold is the only legitimate red on this PR; any other gate failure is a real defect.

## Objective
Confirm that the PROPOSAL 168 verifier reproduces byte-identically in sim-lab under seed control, that its disclosed results-dict digest matches, and that its own gates (G1 cycles-exist, G2a documented-rate match, G2b monotone-in-candidates, G3 robustness-under-tilt) pass on their stated criteria.

## GROUNDING (verified at HEAD)
- Verifier source: idea-engine `ideas/fleet/condorcet_voting_cycle.py` @ `11bb533` — file sha256 `259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def`, git blob `f349dfa78e4c6a1012858d4fc0aab95daa678578`.
- Disclosed results-dict digest to reproduce: `70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe`.
- Documented-rate anchor: impartial-culture probability of no Condorcet winner ≈ 8.7% for three candidates at large electorates. Grounding: https://en.wikipedia.org/wiki/Condorcet_paradox@1360635422 · fetched 2026-07-19
- Seed: `SEED=20260717`; gate threshold `Z_GATE=3.0`.

## Constraints honored
- Stdlib-only Python 3 (hashlib, json, math, random); no third-party imports.
- Verifier copied byte-identically (`diff` exit 0); no edits to logic.
- Determinism: fixed seed; in-process double-run and cross-invocation both byte-identical.
- sim-lab records the reproduction only; no deploy.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3
- G1 head cycles-exist: three-candidate majority cycle rate significantly above zero — expect z_vs_zero ≈ +61.46 (m=3, n=101, rate ≈ 0.0863).
- G2a documented-rate match: measured three-candidate rate close to the documented ≈ 8.7% — expect |z_vs_documented| ≈ 0.44 (< 3, a closeness anchor).
- G2b monotone-in-candidates: no-winner rate strictly rising across m = 3 < 4 < 5 < 7 — expect step-z ≈ 19.39 / 11.95 / 18.63, each ≥ 3.
- G3 robustness-under-tilt: cycles persist under a Plackett–Luce popularity tilt — expect z_vs_zero ≈ +21.33 (rate ≈ 0.0223 > 0).

## Probe questions (independent-audit checklist)
**1.** Does `diff` between the sim-lab copy and idea-engine `ideas/fleet/condorcet_voting_cycle.py` @ `11bb533` exit 0?
**2.** Does the in-process double-run assert byte-identical results, and does a separate second invocation reproduce the same `Results-JSON sha256`?
**3.** Does that printed digest equal the disclosed `70de2ab4…`?
**4.** Is G1's cycles-exist z well above the `Z_GATE=3.0` threshold?
**5.** Is G2a a closeness anchor (|z_vs_documented| < 3) with the measured rate near 8.7%, rather than a far-from-zero anchor?
**6.** Is G2b strictly monotone in candidate count with each step-z ≥ 3?
**7.** Does G3 keep the cycle rate above zero under the popularity tilt?

## Outcome
**APPROVE.** The verifier reproduces byte-identically (`diff` exit 0; file sha256 `259b1e35c06798b9f5f1f254dfab06ce9ee496223f240371bfaa274de60a5def`, git blob `f349dfa78e4c6a1012858d4fc0aab95daa678578`), is deterministic in-process and across a separate invocation, and prints the disclosed results-dict digest `70de2ab46cf482130fa35b051f579d72215efa757dfcf7b5f60e56d85fc08fbe` (MATCH). All four gates pass on the proposal's own criteria: G1 cycles-exist z_vs_zero = +61.46 (m=3 rate 0.086275); G2a documented-rate match |z_vs_documented| = 0.44 (measured 0.086275 vs the ≈ 8.7% anchor); G2b monotone-in-candidates step-z 19.39 / 11.95 / 18.63 (rates 0.0867 → 0.1789 → 0.2479 → 0.3685 across m = 3 < 4 < 5 < 7); G3 robustness-under-tilt z_vs_zero = +21.33 (rate 0.02225 > 0). `all_pass = true`, no failing gate.

## ⟲ Previous-session review
VERDICT 180 (MMR/Elo rating deflation, PROPOSAL 167, sim-lab #254) landed APPROVE with a byte-identical verifier copy and a matching digest; its card and probe-report format are the template this card follows. main was green at HEAD before this card's born-red hold.

## 💡 Session idea
The G2a "documented-rate match" gate is a closeness anchor (|z| < 3), the inverse of the usual far-from-zero gate — a reusable pattern for any proposal whose claim is "reproduces a known published constant" rather than "beats the null". Worth codifying in the verdict-verifier skill so future documented-value reproductions state up front which anchor direction each gate uses.

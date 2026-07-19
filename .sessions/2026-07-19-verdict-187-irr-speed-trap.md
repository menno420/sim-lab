# VERDICT 187 — the IRR speed trap (reproduce PROPOSAL 174)

A venture fund's internal rate of return (IRR) is NOT monotone in the dollars it returns to LPs: because IRR is a time-normalised rate (for a bullet fund, r = M^(1/T)−1), a lower-MOIC fund that distributes FAST out-IRRs a higher-MOIC fund that distributes SLOW, so ranking funds on IRR systematically selects the one that hands LPs LESS cash. The load-bearing companion is the subscription (capital-call) credit line: delaying the LP capital call to t=τ shortens the IRR clock (T → T−τ) and raises the reported IRR even though the LP, net of line interest ((1+c)^τ−1), receives FEWER dollars — the metric moves on timing alone, not on value created. DPI / MOIC / TVPI answer the dollars question; IRR does not. This card reproduces the round-41 VENTURE verifier and rules on it. **This card is provisional — work in-progress.**

> **Status:** `complete`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD:** this card lands `in-progress` on its first commit to hold the PR red under the substrate-gate, and flips to `complete` on the last commit once the reproduction below is recorded (sim directory, run-stdout, probe report in place and the heartbeat stamped). Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective

Reproduce `ideas/venture-lab/irr_speed_trap.py` (idea-engine, PROPOSAL 174) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered z-gates (G1 → G2 → G3) against the proposal's own pre-registered criteria, verify grounding live, and rule. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)

- Verifier sim copy (intended): `sims/verdict-187-irr-speed-trap/irr_speed_trap.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/venture-lab/irr_speed_trap.py` @ idea-engine main `34e3776` (PROPOSAL 174, PR #664). Reference file sha256 `13ecd4b4e0b220a4f48d366d39b8d89b6a3943aa746b87cb5057f9cd6e1b0547`, git blob `3fb977e630e04108072c8a6402653bf16e93067a` (read at HEAD; sim-copy match to be reconfirmed at copy time).
- Offset authority: PROPOSAL 174 → VERDICT 187 (+13), round-41 VENTURE slot (P172→V185, P173→V186, next slot in the ladder).
- Pinned world constants (from the verifier, not invented): SEED=20260717 (in-source, env-inert) · Z_GATE=3.0 · TRIALS=200000 (G1, G2) · TRIALS_G3=40000. Bullet IRR closed form M^(1/T)−1; G3 IRR by 120-step bisection on NPV. G1 bullet pairs: slow-rich M_s~U[2.0,3.0], T_s~U[9,13]; fast-poor M_f~U[1.15,1.40], T_f~U[0.8,1.6] (M_f<M_s always). G2 subscription line: M~U[2.0,3.0], T~U[9,13], call delay τ~U[1.0,3.0], line rate c~U[0.04,0.10], ic=(1+c)^τ−1, MOIC_line=M−ic, IRR_line=(M−ic)^(1/(T−τ))−1. G3 staged J-curve: slow-rich calls −0.5 at t=0 and −0.5 at t=1, bullet distribution M_s~U[2.2,3.2] at T_s~U[12,16]; fast-poor same staged calls, M_f~U[1.20,1.45] split in equal thirds at d0, d0+1, d0+2 with d0~U[2.0,2.5]. All constants to be taken verbatim from the committed verifier.
- Domain reference: Internal rate of return — https://en.wikipedia.org/wiki/Internal_rate_of_return (reinvestment-at-IRR assumption + NPV-vs-IRR duration/scale ranking conflict). Proposer honesty note carried forward: durable anchor is the reinvestment text + the M^(1/T)−1 algebra, not a verbatim heading string (markup interleaves the words). Live HTTP 200 to be reconfirmed this session — TBD.
- Disclosed digest: results-dict sha256 `552e98a09fd8f8c069156ab40d35dca2049671702e5e11f8d40a52fba3f2736f` (from PROPOSAL 174 gate criteria). Reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 is the digest (floats rounded 6 dp before hashing); printed to stdout, nothing written to disk. `main()` runs `compute()` twice, asserts `a == b`, canonicalizes, prints indent=2 dump, then `double_run_identical=true`, `all_pass=…`, `first_failing_gate=…`, and the `Results-JSON sha256 …` line.

## Constraints honored

Stdlib-only (`json`, `math`, `hashlib`, `random`); Python 3; no network and no disk writes by the verifier. SEED pinned in-source (`SEED = 20260717`); the file does not import `os` and reads no env var (env override expected inert). Verifier to be copied byte-identically (diff exit 0); no edits. Gates evaluated against the proposal's own pre-registered thresholds, not re-invented. Determinism to be confirmed across two separate invocations plus the in-process double-run assert.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — speed beats magnitude (bullet): over 200k matched pairs the fast-low-MOIC fund's IRR exceeds the slow-high-MOIC fund's; pass = (mean IRR gap / se ≥ 3.0) and (mean gap > 0). Proposal targets: mean IRR gap 0.147747, z≈789.30, inversion fraction ≈99.506%. Measured value TBD.
- G2 — subscription line: higher IRR, fewer LP dollars: delaying the capital call raises LP IRR while LP MOIC strictly falls; pass = (delta-IRR z ≥ 3.0) and (mean delta-MOIC < 0) and (|delta-MOIC z| ≥ 3.0). Proposal targets: mean delta-IRR +0.013764 (z≈756.06), mean delta-MOIC −0.146102 (z≈−1093.34). Measured value TBD.
- G3 — robustness under shifted, staged (J-curve) distribution: staged two-year calls, longer horizons, early spread distributions solved by bisection; the fast fund's IRR still exceeds the slow fund's; pass = (mean gap / se ≥ 3.0) and (mean gap > 0). Proposal targets: mean IRR gap 0.032235, z≈251.42, inversion fraction ≈88.58%. Measured value TBD.
- all_pass = G1 AND G2 AND G3 (proposal reports **true**; to be reproduced). Measured TBD.

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Target: diff exit 0; reference file sha256 `13ecd4b4…6e1b0547`, git blob `3fb977e6…3067a`. Sim-copy hashes TBD.
2. Does the results-dict digest reproduce byte-exact? Target: printed `Results-JSON sha256 552e98a0…b3f2736f` == disclosed. Reproduction TBD.
3. Is the run deterministic across invocations? Target: two separate `python3` runs byte-identical (diff exit 0) plus the in-process `assert a == b` double-run equality. Reproduction TBD.
4. Is the SEED honestly pinned? SEED=20260717 is a module-level source constant; the file imports no `os` and reads no env var — to be confirmed against the committed verifier.
5. Do all three gates pass in order with z ≥ 3.0? Target: G1 ≈789.30, G2 delta-IRR ≈756.06 / delta-MOIC |z|≈1093.34, G3 ≈251.42; all_pass=true, no failing gate. Measured TBD.
6. Is the mechanism sound, not a strawman? IRR conflates the SPEED of cash flows with their MAGNITUDE; G2 charges the line's compounded interest (1+c)^τ−1 against the LP distribution, so MOIC strictly falls while IRR rises purely from the shortened T→T−τ clock — higher IRR with fewer dollars is measured, not assumed. To be confirmed from the numbers.
7. Does grounding document the specific head? Wikipedia IRR page documents the reinvestment-at-IRR assumption and the NPV-vs-IRR duration/scale ranking conflict; the durable anchor is the reinvestment text + the M^(1/T)−1 algebra (heading not verbatim-grep-able due to markup interleave), the subscription-line inflation cited as documented practice. Live HTTP 200 recheck TBD.
8. Real venture phenomenon or textbook toy? LP league tables rank managers on realised IRR and capital-call lines are widely used to defer draws and lift reported IRR — the head is that this rewards speed over dollars, with DPI/MOIC the honest dollars metric. To be affirmed in Outcome.

## Outcome

Reproduced clean. Measured results below.

- **Verifier byte-identity:** copied byte-identically from the idea-engine reference — `diff` exit 0; sim-copy file sha256 `13ecd4b4e0b220a4f48d366d39b8d89b6a3943aa746b87cb5057f9cd6e1b0547`, git blob `3fb977e630e04108072c8a6402653bf16e93067a` (both match the idea-engine reference).
- **Determinism:** two separate invocations byte-identical (cross-invocation `diff` exit 0) plus the in-process `double_run_identical=true`.
- **Digest:** printed `Results-JSON sha256 552e98a09fd8f8c069156ab40d35dca2049671702e5e11f8d40a52fba3f2736f` == disclosed → **MATCH (exact)**.
- **Gates in order (measured vs proposal target):** G1 — mean IRR gap 0.147747, z=789.30361, inversion 0.99506 (target 0.147747 / ≈789.30 / ≈99.506%); G2 — delta-IRR mean +0.013764 z=756.063137, delta-MOIC mean −0.146102 z=−1093.342507 (target +0.013764/≈756.06, −0.146102/≈−1093.34); G3 — mean gap 0.032235 z=251.423783 inversion 0.8858 (target 0.032235/≈251.42/≈88.58%). `all_pass=true`, `first_failing_gate=null`. Every field matches to the printed precision.
- **Illustrative point:** fast-poor fund IRR 0.191138 vs slow-rich 0.091493 — the smaller-but-faster fund out-IRRs the larger-but-slower one.
- **Grounding:** Wikipedia "Internal rate of return" live HTTP 200; reinvestment text present (reinvestment/reinvested returned by grep).
- **Reproduction record paths:** `sims/verdict-187-irr-speed-trap/{irr_speed_trap.py, run-stdout.txt, probe-report.md}`.

**Ruling: APPROVE.** The digest reproduced exactly and all three gates pass on the proposal's own thresholds; the algebra (IRR = MOIC^(1/T)−1 decreasing in horizon T at fixed MOIC; a subscription line shortens T→T−τ) is textbook-sound and the mechanism is measured, not assumed. The verdict high-water advances V186 → V187 (union-max, no regress).

## ⟲ Previous-session review

VERDICT 186 (decorrelated jitter backoff, reproduce PROPOSAL 173, round-41 FLEET slot) landed APPROVE at sim-lab #260 (merge 70e28a6): results-dict digest `efea8579…e2f8` MATCH, verifier byte-identical (file sha256 `b7614fbb…d6a2d42d`, git blob `2d67b408…d73bac`), all three gates PASS (G1 z=4350.28, G2 z=244.46, G3 z=11.84) on the proposal's own thresholds, with the grounding non-durability honestly disclosed. The same reproduce-then-rule discipline carries here. This card continues the loop at the next slot (P174 → V187, +13) and, on its flip to `complete`, advances the verdict high-water V186 → V187 by union-max; no regression.

## 💡 Session idea

The G1/G2 bands are bullet idealisations and G3 already relaxes to a staged J-curve; a follow-up could sweep the call-delay τ and the line rate c continuously and plot the reported-IRR lift against the LP MOIC loss — turning the single subscription-line result into a dose-response frontier (more delay / higher line rate → wider IRR-vs-dollars wedge). It would make concrete, over realistic facility terms, exactly how many basis points of headline IRR a fund can manufacture per dollar of LP cash foregone — the honest cost of the metric game.

**Recommendation: APPROVE PROPOSAL 174 (the IRR speed trap). Reproduced byte-identical at SEED=20260717 with the disclosed digest `552e98a0…b3f2736f` matching EXACTLY and G1/G2/G3 all passing on the proposal's own thresholds; the verdict high-water advances V186 → V187 (union-max, no regress below whatever is already there).**

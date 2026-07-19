# VERDICT 189 — the giant-component phase transition (reproduce PROPOSAL 176)

In a random graph on n nodes formed by adding m = round(c·n/2) uniformly random edges (average degree ≈ c), the fraction of nodes in the LARGEST connected component is NOT a smooth function of c: it stays a vanishing fraction (order log n / n) for c < 1 and jumps to a constant fraction ρ(c) > 0 the instant c crosses 1. The folk belief — "connectivity accretes gradually; twice the edges, twice the largest cluster; nothing special about one edge per node" — is wrong twice over: nothing macroscopic exists below the threshold, and above it a constant fraction appears abruptly rather than accreting linearly. The mechanism is branching-process criticality: exploring a node's component reaches on average c new nodes per step, so exploration dies out (components order log n) when c < 1 and survives to coalesce into a single giant when c > 1, with ρ solving the mean-field fixed point ρ = 1 − exp(−c·ρ) (ρ(1.4) ≈ 0.51). This is the bond-percolation universality class on the complete graph. This card reproduces the round-42 UNRELATED verifier and rules on it. **This card is provisional — work in-progress.**

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD:** this card lands `in-progress` on its first commit to hold the PR red under the substrate-gate, and flips to `complete` on the last commit once the reproduction below is recorded (sim directory, run-stdout, probe report in place and the heartbeat stamped). Red until the flip is the HOLD, not a defect. Contents below are provisional until the reproduction lands.

## Objective

Reproduce `ideas/fleet/giant_component_threshold.py` (idea-engine, PROPOSAL 176) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered z-gates (G1 → G2 → G3) against the proposal's own pre-registered criteria, verify grounding live, and rule. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)

- Verifier sim copy (intended): `sims/verdict-189-giant-component-transition/giant_component_threshold.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/fleet/giant_component_threshold.py` @ idea-engine main `8cfa363` (PROPOSAL 176, PR #668, merge SHA `8cfa36367c859f54dc04cc996a369c86edd27ed8`). Reference file sha256 `c05dfc968d857921bf20ce400a7e8277b64eed16abbf08c7ef1dee28463ad9b2`, git blob `2e4026b882de13b3677a4c424b8d51946205d6e7` (read at HEAD; sim-copy match to be reconfirmed at copy time).
- Offset authority: PROPOSAL 176 → VERDICT 189 (+13), round-42 UNRELATED slot (P173→V186, P174→V187, P175→V188, next slot in the ladder).
- Pinned world constants (from the verifier, not invented): SEED=20260717 (in-source, env-inert) · Z_GATE=3.0 · TRIALS=40 i.i.d. random graphs per condition. Sizes n1=4000, n2=16000 (a 4× scale shift for the robustness gate). Average degrees probed c ∈ {0.5, 0.7, 0.9, 1.1, 1.4}. A graph G(n, m) has m = round(c·n/2) edges, each a uniform random ordered pair (self-loops skipped, multi-edges permitted — asymptotically equivalent to G(n, p = c/n)); connectivity by union-find (DSU, union-by-size + path halving); the per-graph statistic is largest_component_size / n; per condition mean and standard error over 40 trials. A single `random.Random(SEED)` stream is drawn in a fixed condition order: sub(n1,0.7), sup(n1,1.4), sub(n2,0.7), sup(n2,1.4), then c=0.5, 0.9, 1.1 at n2. Mean-field anchor ρ = 1 − exp(−c·ρ) ⇒ ρ(1.4) ≈ 0.51. All constants to be taken verbatim from the committed verifier.
- Domain reference: Erdős–Rényi random-graph evolution — the giant component emerges at the critical average degree c = 1 — https://en.wikipedia.org/wiki/Giant_component (grounding pinned at content hash `66da05b62033927be39802f77888c6408fdee263`, permalink oldid 1340194064: https://en.wikipedia.org/w/index.php?title=Giant_component&oldid=1340194064; proposal fetched 2026-07-19T16:36:37Z, HTTP 200). Durable anchor is the emergence of a giant component at the phase transition where expected degree crosses 1 (the exact c = 1 head) and the ρ = 1 − exp(−c·ρ) fixed point, not a verbatim heading string. Live HTTP 200 to be reconfirmed this session — TBD.
- Disclosed digest: results-dict sha256 `14875022bef41594dbc8d19bd2960724d2f86f6dedcadf1b339f228915469537` (from PROPOSAL 176 gate criteria). Reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the results dict carries no digest field; `main()` runs `compute()` twice in-process, asserts byte-identical compact-canonical (`json.dumps(..., sort_keys=True, separators=(",",":"))`) serializations, prints the pretty (`indent=2, sort_keys=True`) dump, then the line `Results-JSON sha256: <hex>` computed over the compact-canonical form. Floats are rounded to 6 dp (`r6`) inside the dict before hashing. `all_pass` and `first_failing_gate` are FIELDS of the printed dict, not separate stdout lines. Nothing is written to disk.

## Constraints honored

Stdlib-only (`hashlib`, `json`, `math`, `random`); Python 3; no network and no disk writes by the verifier. SEED pinned in-source (`SEED = 20260717`); the file does not import `os` and reads no env var (env override expected inert). Verifier to be copied byte-identically (diff exit 0); no edits. Gates evaluated against the proposal's own pre-registered thresholds, not re-invented. Determinism to be confirmed across two separate invocations plus the in-process double-run assert (`canonical(r_a) == canonical(r_b)`).

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — existence: the giant appears above threshold and is absent below. pass = (sup_mean(c=1.4, n=4000) ≥ 0.30) and (sub_mean(c=0.7, n=4000) ≤ 0.08) and (z of the difference ≥ 3.0). Proposal targets: sup_mean 0.507138, sub_mean 0.008025, z 263.375801. Measured TBD.
- G2 — robustness (4× scale shift): at n=16000 the supercritical giant fraction stays ≥ 0.30 and is size-invariant while the subcritical fraction shrinks with n. pass = (sup_mean(n=16000) ≥ 0.30) and (z_vs_floor vs the 0.30 floor ≥ 3.0) and (|sup_mean(n=16000) − sup_mean(n=4000)| ≤ 0.05) and (sub_mean shrinks: m_sub2 < m_sub1). Proposal targets: sup_mean_n16000 0.511348, z_vs_floor 204.254546, size_gap 0.004211, sub 0.008025 → 0.002861. Measured TBD.
- G3 — sharpness / placebo: growth is concentrated at c ≈ 1, rejecting the smooth-linear-growth null. pass = ((jump_near − jump_far) ≥ 0.05) and (z of the jump difference ≥ 3.0) and (all sub-threshold fractions ≤ 0.15). Proposal targets: jump_near = frac(1.1) − frac(0.9) = 0.169817 − 0.010175 = 0.159642; jump_far = frac(0.7) − frac(0.5) = 0.002861 − 0.001248 = 0.001612; z 33.80426. Measured TBD.
- all_pass = G1 AND G2 AND G3 (proposal reports **true**; to be reproduced). `first_failing_gate` names the earliest failure (proposal reports **null**). Measured TBD.

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Target: diff exit 0; reference file sha256 `c05dfc96…463ad9b2`, git blob `2e4026b8…205d6e7`. Sim-copy hashes TBD.
2. Does the results-dict digest reproduce byte-exact? Target: printed `Results-JSON sha256: 14875022…15469537` == disclosed. Reproduction TBD.
3. Is the run deterministic across invocations? Target: two separate `python3` runs byte-identical (diff exit 0) plus the in-process `assert canonical(r_a) == canonical(r_b)` double-run equality. Reproduction TBD.
4. Is the SEED honestly pinned? SEED=20260717 is a module-level source constant; the file imports no `os` and reads no env var — to be confirmed against the committed verifier.
5. Do all three gates pass in order with z ≥ 3.0? Target: G1 z=263.375801, G2 z_vs_floor=204.254546, G3 z=33.80426; all_pass=true, first_failing_gate=null. Measured TBD.
6. Is the supercritical giant fraction genuinely intensive (size-invariant), or a finite-n artifact? Target: c=1.4 fraction 0.507138 (n=4000) vs 0.511348 (n=16000), gap 0.004211 ≤ 0.05, while the c=0.7 subcritical fraction shrinks 0.008025 → 0.002861 (order log n / n → 0). To be confirmed from the numbers.
7. Does the measured ρ(1.4) match the mean-field fixed point ρ = 1 − exp(−c·ρ)? Target: solving ρ = 1 − exp(−1.4ρ) gives ρ ≈ 0.51, matching the measured 0.511348 (n=16000) within ~0.002. To be confirmed.
8. Does grounding document the specific c=1 threshold head? Wikipedia "Giant component" documents the emergence of a giant component at the phase transition where expected degree crosses 1 — the exact c = 1 head — and the ρ = 1 − exp(−c·ρ) fixed point; the durable anchor is that transition, not a verbatim heading string. Live HTTP 200 recheck TBD.

## Outcome

Pending reproduction — this born-red card holds the PR red until the run lands. Measured results, digest match, gate evaluation, grounding recheck, and the reproduction record paths (`sims/verdict-189-giant-component-transition/{giant_component_threshold.py, run-stdout.txt, probe-report.md}`) will be recorded here on the flip to `complete`, and the verdict high-water advances V188 → V189 (union-max, no regress) on APPROVE.

## ⟲ Previous-session review

VERDICT 188 (the pie-rule opening trap, reproduce PROPOSAL 175, round-41 GAME slot) landed APPROVE at sim-lab #262 (merge ec7a0b9): results-dict digest `72950442…d083e8cb08` MATCH, verifier byte-identical (file sha256 `7e89f690…f12f4e39`, git blob `ace21553…5cd15daf`), all three gates PASS (G1 win_rate 0.900505 z=+598.38, G2 win_rate 0.10111 z=−591.72, G3 gap_mean 0.4517 z_gap=+370.91) on the proposal's own thresholds. The same reproduce-then-rule discipline carries here. This card continues the loop at the next slot (P176 → V189, +13) and, on its flip to `complete`, advances the verdict high-water V188 → V189 by union-max; no regression.

## 💡 Session idea

The giant-component head is a pure threshold — nothing macroscopic below c=1, a constant fraction above — and the sim already probes five average degrees. A follow-up could sweep c on a fine grid straddling 1 (e.g. c ∈ [0.85, 1.15] in steps of 0.01) at two or three sizes and fit the finite-size scaling of the largest-component fraction: the crossing point of the size-indexed curves locates the critical c, and the width of the transition window should narrow as n^(−1/3) (the known critical-window exponent). That turns the single sharp-jump result into a measured critical exponent — a stronger, quantitative confirmation that the transition is a genuine second-order phase change and not just a steep-but-smooth curve, and it makes concrete the "worst place to provision is exactly c=1" design warning by showing the fluctuation blow-up at the critical point.

**Recommendation (provisional, pending reproduction): reproduce PROPOSAL 176 (the giant-component phase transition) byte-identical at SEED=20260717 and confirm the disclosed digest `14875022…15469537` matches EXACTLY with G1/G2/G3 all passing on the proposal's own thresholds; on a clean reproduction the ruling is APPROVE and the verdict high-water advances V188 → V189 (union-max, no regress below whatever is already there). Verdict rendered in Outcome once the run is in.**

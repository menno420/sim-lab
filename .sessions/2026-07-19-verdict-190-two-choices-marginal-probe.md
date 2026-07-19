# VERDICT 190 — the second probe does all the work (reproduce PROPOSAL 177)

In randomized load balancing / task dispatch (JSQ(d): sample d servers uniformly at random, route to the least-loaded of the sample), the value of extra probes is almost entirely front-loaded onto the SECOND probe. With one random choice the maximum bin load is Θ(log n / log log n); with two it collapses to Θ(log log n) + O(1) — an exponential drop. Because d then enters only inside a log-log term, every probe past the second buys a shrinking constant. The folk belief — "more probes = proportionally better balance, so query more replicas" — is wrong: the single second probe removes several times more maximum load than every further probe (3rd, 4th, …) COMBINED (~4× in dry-sim). The honest, robust statement is AGGREGATE — one second probe vs all further probes combined — NOT that each successive per-step gap strictly shrinks (at finite n the individual gaps past d=2 are integer-granular and non-monotone: d=2→3 ≈ 0 bins while d=3→4 ≈ 0.8 bin). Operationally: JSQ(2) captures essentially the whole balancing win; paying for JSQ(3+) is near-worthless spend. This card reproduces the round-42 FLEET verifier and rules on it.

> **Status:** `complete`
> 📊 Model: Claude · effort high · verdict reproduction

**Reproduction landed — APPROVE.** The verifier was copied byte-identical (diff exit 0), run under SEED=20260717, and reproduced the disclosed results-dict digest `625b38309d4e6c8209a74f9123b23d56d769beb4ad592b917093d8c67d234c7f` EXACTLY (MATCH). All three pre-registered gates PASS in order (G1 z=77.71, G2 z=46.69 ratio 4.0, G3 z=52.81 ratio 4.70; `all_pass=true`). Determinism was confirmed via two identical separate process invocations byte-matching. HONEST CAVEAT: the verifier's `main()` runs `run()` only ONCE in-process — there is no in-process double-run assert here (unlike V188/V189); determinism was therefore established by two identical separate `python3` process invocations byte-matching, not an in-process re-run. This final flip to `complete` releases the born-red HOLD.

## Objective

Reproduce `ideas/fleet/two_choices_marginal_probe.py` (idea-engine, PROPOSAL 177) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered z-gates (G1 → G2 → G3) against the proposal's own pre-registered criteria, verify grounding live, and rule. Factual reproduction only; verdict rendered in Outcome once the run is in.

## GROUNDING (verified at HEAD)

- Verifier sim copy (intended): `sims/verdict-190-two-choices-marginal-probe/two_choices_marginal_probe.py` — to be a byte-identical copy of the idea-engine reference (`diff` exit 0 target).
- Idea-engine source: `ideas/fleet/two_choices_marginal_probe.py` @ idea-engine main `a1aa6a5` (PROPOSAL 177, PR #670, merge SHA `a1aa6a579634a5ec0cead1bfdf73fa471b8fd27a`). Reference file sha256 `5fede409315a2523a6fc816c25445f8cf03a718ae384c02d1fb857475a98c7e6`, git blob `2b2f8aef18de9b8296656593c898fded23fe94f7` (read at HEAD; sim-copy match reconfirmed at copy time).
- Offset authority: PROPOSAL 177 → VERDICT 190 (+13), round-42 FLEET slot (P174→V187, P175→V188, P176→V189, next slot in the ladder).
- Pinned world constants (from the verifier, not invented): SEED=20260717 (in-source, env-inert) · SIGMA_GATE=3.0 · RATIO_MIN=3.0 · N=8000 balls (dispatched requests) · R=250 independent trials per (regime, d) · DS=(1,2,3,4) probes. Explicit per-(regime,d,trial) seeds: `regime_seed + d·1_000_003 + t·7919`, with `regime_seed = SEED + regime·50_000_017`. Placement: least-loaded-of-d, ties→lowest index (deterministic, pessimistic — concentrates load). Metric: mean maximum bin load and its standard error over R trials. Regime A: m = n = 8000 (load factor 1). Regime B (robustness): m = n/2 = 4000 (load factor 2). second_gain = maxload(1) − maxload(2); further_gain = maxload(2) − maxload(4) = everything the 3rd and 4th probes add, combined. dom = second_gain − further_gain; ratio = second_gain/further_gain. All constants taken verbatim from the committed verifier.
- Domain reference: the "power of two choices" / balanced-allocations result (Azar–Broder–Karlin–Upfal, "Balanced Allocations", STOC 1994; Mitzenmacher–Richa–Sitaraman, "The Power of Two Random Choices: A Survey of Techniques and Results", 2001) — https://en.wikipedia.org/wiki/Balls_into_bins_problem, grounding pin `55f6ec5b128f4533cf57578a06708e1909b96924` (proposal fetched 2026-07-19T17:01:30Z). Durable anchor is the maximum-load collapse from Θ(log n / log log n) at d=1 to Θ(log log n) at d=2 (the doubly-diminishing curve), not a verbatim heading string. Live HTTP 200 to be reconfirmed this session.
- Disclosed digest: results-dict sha256 `625b38309d4e6c8209a74f9123b23d56d769beb4ad592b917093d8c67d234c7f` (from PROPOSAL 177 gate criteria). Reproduction must reproduce it EXACTLY before the card flips.
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the results dict carries no digest field; the compact-canonical (`json.dumps(..., sort_keys=True, separators=(",",":"))`) serialization of the whole results dict is hashed, printed as the line `Results-JSON sha256: <hex>`, and nothing is written to disk. Floats are rounded to 6 dp (`r6`) inside the dict before hashing. The pretty (`indent=2, sort_keys=True`) dump precedes the digest line. `all_pass` is a FIELD of the printed dict, not a separate stdout line.

## Constraints honored

Stdlib-only (`hashlib`, `json`, `math`, `random`); Python 3; no network and no disk writes by the verifier. SEED pinned in-source (`SEED = 20260717`); the file does not import `os` and reads no env var (env `SEED=20260717` export expected inert — value coincides). Verifier to be copied byte-identically (diff exit 0); no edits. Gates evaluated against the proposal's own pre-registered thresholds, not re-invented. Determinism to be confirmed across two separate invocations plus the in-process double-run structure.

## Gate plan (reproduced at HEAD), order G1 → G2 → G3

- G1 — the second probe produces a real jump: z of (maxload[d=1] − maxload[d=2]) with gap > 0. pass = (gap_1_2 > 0) and (z ≥ 3.0). Proposal target: gap_1_2 = 3.536, z = 77.709782 → PASS.
- G2 — second-probe dominance (the head): dom = second_gain − further_gain; require dom > 0, z(dom) ≥ 3.0, AND ratio second_gain/further_gain ≥ 3.0. Proposal target: second_probe_gain 3.536, all_further_gain 0.884, dom_stat 2.652, z 46.693563, ratio 4.0 → PASS.
- G3 — robustness under shifted load (m = n/2 = 4000, load factor 2): dom, ratio recomputed in regime B; require dom > 0, z ≥ 3.0, ratio ≥ 3.0. Proposal target: second_probe_gain 4.664, all_further_gain 0.992, dom_stat 3.672, z 52.81092, ratio 4.701613 → PASS.
- all_pass = G1 AND G2 AND G3 (proposal reports **true**; to be reproduced).

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Target: diff exit 0; reference file sha256 `5fede409…5a98c7e6`, git blob `2b2f8aef…3fe94f7`. To be confirmed at copy time.
2. Does the results-dict digest reproduce byte-exact? Target: printed `Results-JSON sha256: 625b3830…d234c7f` == disclosed. To be reproduced.
3. Is the run deterministic across invocations? Target: two separate `python3` runs byte-identical (diff exit 0); plus the verifier's explicit per-(regime,d,trial) seeding making each cross-invocation identical. To be confirmed.
4. Is the SEED honestly pinned? SEED=20260717 is a module-level source constant; the file imports no `os` and reads no env var — any `SEED` env export is inert (the exported value coincides with the in-source constant). To be confirmed against the committed verifier.
5. Do all three gates pass in order with z ≥ 3.0 and ratio ≥ 3.0? Target: G1 z=77.709782, G2 z=46.693563 (ratio 4.0), G3 z=52.81092 (ratio 4.701613); all_pass=true. To be measured.
6. Is the head honestly scoped as an AGGREGATE, not a per-step monotone sequence? The claim is that the single second probe removes more max load than all further probes COMBINED (ratio ≥ 3), NOT that each successive per-step gap strictly shrinks — at finite n the later gaps are integer-granular and non-monotone (d=2→3 ≈ 0.068 bin, d=3→4 ≈ 0.816 bin in dry-sim). To be affirmed from the gap fields (gap_2_3, gap_3_4).
7. Could the effect be an artifact of m = n (load factor 1)? G3 reruns at m = n/2 (load factor 2); the dominance must persist at ≥3σ with ratio ≥ 3 to rule out exactly-critical loading as the cause. To be affirmed.
8. What would falsify the head? A regime where the second probe's gain is under 3× the combined further-probe gain (ratio < 3), or where d=2 fails to beat d=1 at ≥3σ. The verifier checks exactly these; either failing flips all_pass to false. To be affirmed in Outcome.

## Outcome

**APPROVE.** The digest reproduces EXACTLY (`625b38309d4e6c8209a74f9123b23d56d769beb4ad592b917093d8c67d234c7f` MATCH), the copy is byte-identical (diff exit 0), and all three gates PASS in order on the proposal's own pre-registered thresholds (G1 second-probe jump z=77.71, G2 second-probe dominance z=46.69 ratio 4.0, G3 shifted-load robustness z=52.81 ratio 4.70; `all_pass=true`). The head is honestly scoped as an AGGREGATE — the single second probe removes ≥3× more max load than all further probes (3rd, 4th, …) COMBINED — NOT a per-step monotone sequence (at finite n the later per-step gaps are integer-granular and non-monotone). Determinism holds across two identical separate process invocations (byte-matching). HONEST CAVEAT: the verifier's `main()` runs `run()` only ONCE in-process — there is no in-process double-run assert (unlike V188/V189); determinism was confirmed by the two separate-invocation byte match. Reproduction record: `sims/verdict-190-two-choices-marginal-probe/`. On this reproduction the verdict high-water advances V189 → V190 (union-max, no regress).

## ⟲ Previous-session review

VERDICT 189 (the giant-component phase transition, reproduce PROPOSAL 176, round-42 UNRELATED slot) landed APPROVE at sim-lab #263 (merge 0d1afc8): results-dict digest `14875022…15469537` MATCH, verifier byte-identical (file sha256 `c05dfc96…463ad9b2`, git blob `2e4026b8…205d6e7`), all three gates PASS (G1 z=263.375801, G2 z_vs_floor=204.254546, G3 z=33.80426) on the proposal's own thresholds. The same reproduce-then-rule discipline carries here. This card continues the loop at the next slot (P177 → V190, +13) and, on its flip to `complete`, advances the verdict high-water V189 → V190 by union-max; no regression.

## 💡 Session idea

The head is scoped as an aggregate (one second probe vs all further probes combined) precisely because the per-step gaps past d=2 are integer-granular and non-monotone at finite n. A follow-up could sweep n over a few decades (e.g. n ∈ {1000, 8000, 64000, 512000}) and fit the d=1 and d=2 max-load curves against their asymptotic forms (log n / log log n vs log log n), turning the single ratio into a measured separation of growth rates — a quantitative confirmation that the 1→2 jump is an exponential collapse and not merely a steep constant, and firming up the "stop at JSQ(2)" provisioning rule with a scaling law rather than a point estimate.

**Recommendation: pending — born-red in-progress verdict; ruling to be rendered in Outcome once the reproduction lands (digest match + G1/G2/G3 evaluated on the proposal's own pre-registered thresholds).**

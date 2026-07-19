# VERDICT 186 — decorrelated jitter backoff (reproduce PROPOSAL 173)

After a shared failure, N clients retrying on PLAIN capped-exponential backoff stay phase-locked: they re-collide every window, so total retry work grows like N^2/2K against a server of capacity K. Adding FULL JITTER — drawing each retry uniformly inside the same backoff window — decorrelates the herd, spreading retries so collisions drop, with no change to the schedule's magnitude. This card reproduces the round-41 FLEET verifier and rules on it. **This card is provisional — work in-progress.**

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · verdict reproduction

**Born-red HOLD:** this card lands `in-progress` on its first commit to hold the PR red under the substrate-gate, and flips to `complete` on the last commit once the reproduction below is recorded.

## Objective

Reproduce `ideas/fleet/decorrelated_jitter_backoff.py` (idea-engine, PROPOSAL 173) byte-identical in sim-lab under SEED=20260717, confirm the disclosed results-dict sha256 reproduces byte-exact, evaluate the three ordered gates against the proposal's own criteria, verify grounding, and rule.

## GROUNDING (verified at HEAD)

- Verifier sim copy: `sims/verdict-186-decorrelated-jitter-backoff/decorrelated_jitter_backoff.py`
- Idea-engine source: `ideas/fleet/decorrelated_jitter_backoff.py` @ 10ef767 (PR #662 merge)
- Offset authority: PROPOSAL 173 -> VERDICT 186 (+13), round-41 FLEET slot
- Pinned world constants: SEED=20260717 (in-source, env-inert), N_CLIENTS=200, CAPACITY=10, BASE=1, CAP=64, TRIALS=400, SMEAR_MEAN=2.0, Z_GATE=3.0, REDUCTION_FLOOR=0.30
- Domain reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ (live HTTP 200; Full/Equal/no-jitter comparison + "reduced our call count by more than half")
- Disclosed digest: results-dict sha256 efea8579300ab0806132a48ea68cb8e9030105d8356b6fad51273fa8cb19e2f8
- DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (digest over the compact-canonical results dict, printed to stdout; nothing written to disk)

## Constraints honored

Stdlib-only (hashlib, heapq, json, random, statistics); no network and no disk writes by the verifier; SEED pinned in-source; verifier copied byte-identical (diff exit 0); determinism confirmed across two separate invocations.

## Gate plan (reproduced at HEAD), order G1 -> G2 -> G3

- G1 work reduction (tight Dirac herd): full-jitter mean total 784.51 vs deterministic no-jitter 2100 -> reduction fraction 0.626424 >= floor 0.30; z = 4350.282085 >= 3.0 -> PASS
- G2 thundering-herd flattening (tight herd): full-jitter post-herd peak 116.635 vs no-jitter N-K = 190; z = 244.458881 >= 3.0 -> PASS
- G3 robustness (over-dispersed geometric arrivals): paired diff 15.8175, se 1.335457, z = 11.844264 >= 3.0 -> PASS. Honest caveat: the absolute gap narrows (~2%) when arrivals are already dispersed — the win is largest when the herd is most synchronized.

## Probe questions (independent-audit checklist)

1. Does the verifier copy match the idea-engine source byte-for-byte? Yes — diff exit 0; file sha256 b7614fbb...d6a2d42d, git blob 2d67b408...d73bac.
2. Does the results-dict digest reproduce byte-exact? Yes — printed `Results-JSON sha256: efea8579...e2f8` == disclosed EXACT.
3. Is the run deterministic across invocations? Yes — two separate `python3` runs produced byte-identical stdout (diff exit 0); main() also asserts an in-process double-run equality.
4. Is the SEED honestly pinned? Yes — SEED=20260717 is a module-level source constant; the file does not import os and reads no env var.
5. Do all three gates pass in order with z >= 3.0? Yes — G1 4350.28, G2 244.46, G3 11.84; all_pass=true, no failing gate.
6. Is the mechanism sound, not a strawman? Yes — the no-jitter arm is standard capped-exponential backoff, not a deliberately weak baseline; deterministic backoff keeps a synchronized herd re-colliding (work ~N^2/2K), which full jitter breaks by spreading retries uniformly.
7. Does grounding document the specific head, not backoff in general? Yes — the AWS post runs the exact No-jitter/Full/Equal/Decorrelated comparison and reports "we've reduced our call count by more than half" (live HTTP 200).
8. Is the grounding byte-durable? No, and honestly disclosed — the AWS page serves per-request nonces so its content sha is not byte-stable; the doc records the fetch that documented the head and cites brooker.co.za + Wikipedia as backups. Audit note: those backups corroborate the general jitter mechanism but not the specific ">half" figure. Per the disclosed caveat this is not treated as a defect.

## Outcome

**APPROVE.** Reproduction: verifier copied byte-identical (diff exit 0; file sha256 b7614fbbd11c7bbf6daee5ebb10ac53102719eea81f2eba4069f7d53d6a2d42d, git blob 2d67b4083816917f87346b93a929d10de9d73bac). Determinism: two separate invocations byte-identical (diff exit 0); main() asserts in-process double-run equality. Digest: printed results-dict sha256 efea8579300ab0806132a48ea68cb8e9030105d8356b6fad51273fa8cb19e2f8 == disclosed EXACT (MATCH). Gates in order: G1 work_reduction z=4350.282085 PASS, G2 herd_flattening z=244.458881 PASS, G3 robust_shifted_arrivals z=11.844264 PASS; all_pass = true; first_failing_gate = null. Grounding: AWS Architecture Blog post verified live HTTP 200, supporting both the Full/Equal/no-jitter comparison and the "reduced our call count by more than half" head; the proposer honestly discloses the page is not byte-durable (per-request nonces) and cites brooker.co.za + Wikipedia as backups. Audit note (not a defect, per the disclosed caveat): the backups corroborate only the general jitter mechanism, not the specific ">half" figure — that quantitative head rests on the AWS post. **Ruling:** APPROVE. Verdict high-water ADVANCES V185 -> V186 (union-max, no regress).

## ⟲ Previous-session review

VERDICT 185 (Berkson's collider selection, PROPOSAL 172) landed clean at sim-lab #259 (merge 725ba33) with a byte-exact digest and live grounding — the same reproduce-then-rule discipline carried here.

## 💡 Session idea

The grounding-durability gap seen here — a quantitative head backed only by a non-byte-durable vendor source — recurs across proposals citing vendor blogs. Worth a small skill: when a pinned source is nonce-served, check the durable backups for the *specific* head, not just the general mechanism, and flag when they cover only the concept.

**Recommendation: APPROVE — reproduces byte-exact (digest efea8579... MATCH), all three gates pass, grounding head verified live at AWS (HTTP 200); non-durability honestly disclosed, backups cover the mechanism.**

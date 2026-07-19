# VERDICT 186 — probe report (reproduce PROPOSAL 173: decorrelated jitter backoff)

Independent-audit reproduction of idea-engine `ideas/fleet/decorrelated_jitter_backoff.py` under SEED=20260717.

## Reproduction facts
- Verifier copied byte-identical from idea-engine source: `diff` exit 0.
- File sha256: b7614fbbd11c7bbf6daee5ebb10ac53102719eea81f2eba4069f7d53d6a2d42d
- Git blob: 2d67b4083816917f87346b93a929d10de9d73bac
- Idea-engine source SHA: 10ef767 (PROPOSAL 173, PR #662 merge)
- Determinism: two separate `python3` invocations produced byte-identical stdout (diff exit 0); main() also asserts an in-process double-run equality on the compact-canonical JSON.
- Results-dict sha256 (printed to stdout): efea8579300ab0806132a48ea68cb8e9030105d8356b6fad51273fa8cb19e2f8 == disclosed EXACT (MATCH).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.
- SEED=20260717 is a module-level source constant (the file imports no os and reads no env var).

## Gates (order G1 -> G2 -> G3)
- G1 work_reduction_tight: full-jitter mean total 784.51 vs no-jitter 2100 -> reduction 0.626424 >= floor 0.30; z=4350.282085 -> PASS
- G2 herd_flattening_tight: full-jitter post-herd peak 116.635 vs no-jitter 190; z=244.458881 -> PASS
- G3 robust_shifted_arrivals: paired diff 15.8175, se 1.335457; z=11.844264 -> PASS
- all_pass = true; first_failing_gate = null.
- Honest caveat (proposer's own): under already-dispersed (over-dispersed geometric) arrivals the absolute gap narrows ~2%; the win is largest when the herd is most synchronized.

## Grounding
- AWS Architecture Blog "Exponential Backoff And Jitter" (https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/): live HTTP 200. Supports the No-jitter / Full / Equal / Decorrelated comparison and the head — verbatim: "we've reduced our call count by more than half" and "The no-jitter exponential backoff approach is the clear loser."
- Non-durability honestly disclosed by the proposer: the AWS page serves per-request nonces, so its content sha is not byte-stable; the doc pins the fetch and cites brooker.co.za + Wikipedia as backups.
- Audit note: the backups (brooker.co.za, en.wikipedia.org/wiki/Exponential_backoff) resolve live but corroborate only the general "jitter decorrelates the herd" mechanism — not the quantitative ">half" figure, which rests specifically on the AWS post. Per the disclosed caveat this is not treated as a defect; noted for the record.

## Ruling
APPROVE. Mechanism reproduces byte-exact, all three gates pass, and the grounding head is verified live at an authoritative source. Verdict high-water advances V185 -> V186 (+13; PROPOSAL 173 -> VERDICT 186).

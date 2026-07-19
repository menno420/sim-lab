# Probe report — VERDICT 192: Buchholz Swiss-tiebreak luck amplifier (PROPOSAL 179)

**Ruling: reproduction landed.** The committed verifier reproduced byte-identically and deterministically; the disclosed results-dict digest matches EXACT; all three ordered gates pass on the proposal's own thresholds. (The session card stays born-red/in-progress; this report records the reproduced evidence, the coordinator flips the card.)

## Source & reproduction
- Verifier source: idea-engine `ideas/superbot-games/swiss_buchholz_luck_amplifier.py` (git blob `0d4a4b1e804dbbafebabff46cf48dc4e8ba753eb`, 5407 bytes, stdlib-only: math, json, hashlib, random).
- Reproduction copy: `sims/verdict-192-buchholz-luck-amplifier/swiss_buchholz_luck_amplifier.py`.
- Byte-identity: `diff source copy` exit 0; copy sha256 `f41f270b465c905a5ba1cc2655e07fb7b21ad84eab2a9037bf0c01a03f5423f8`; git blob `0d4a4b1e804dbbafebabff46cf48dc4e8ba753eb`.
- Determinism: `main()` runs the simulation twice with `assert r1 == r2` (in-process double-run guard, source line 150); a separate second invocation is byte-identical (`diff run1 run2` exit 0). SEED=20260717 pinned at source; Z_GATE=3.0.

## Digest
- Reproduced results-dict sha256 (stdout): `0e591bb44f57f72fdff6536417a3ba009b74dfb9c07f2c41073bdbd9876c0fa8`.
- Proposal disclosure: `0e591bb44f57f72fdff6536417a3ba009b74dfb9c07f2c41073bdbd9876c0fa8`.
- **MATCH** (all 64 hex). Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — sha256 of compact-canonical `json.dumps(sort_keys=True, separators=(',',':'))`; no on-disk JSON.

## Gates (order G1 → G2 → G3, thresholds from the proposal)
| Gate | Claim | Statistic (measured) | Threshold | Result |
|------|-------|----------------------|-----------|--------|
| G1 | luck dominates (head) | base p_luck 0.804910, z_luck 511.920239 | p_luck ≥ 0.70, z_luck ≥ 3.0 | PASS |
| G2 | luck beats skill | base ratio 3.130521, z_diff 234.751939, gap 0.207511 | ratio ≥ 3.0, z_diff ≥ 3.0, gap ≥ 0.15 | PASS |
| G3 | robust under shifted field (σ=350, N=128, R=9) | shift p_luck 0.870756, z_diff 265.698695, gap 0.183947 | p_luck ≥ 0.70, z_diff ≥ 3.0, gap ≥ 0.10 | PASS |

`all_pass = true`. Base field: n=64, rounds=7, σ=200.0, n_tournaments=1200, n_pairs=442632, p_skill 0.597399. Shift field: n=128, rounds=9, σ=350.0, n_tournaments=400, n_pairs=548135, p_skill 0.686809, z_luck 818.237315.

## Ratio-compression caveat (disclosed, not a failure)
The base luck-to-skill signal ratio is 3.130521; under the shifted field it compresses to **1.984682**. This is expected and honestly disclosed: a wider skill spread (σ 200 → 350) makes own-skill more legible, so skill's own signal rises and the luck/skill ratio narrows. G3 is therefore **dominance-gated, NOT ratio-gated** — it requires shift p_luck ≥ 0.70, z_diff ≥ 3.0, and gap (p_luck − p_skill) ≥ 0.10, all of which hold (0.870756, 265.698695, 0.183947). Luck still dominates in the wider field; only the multiplicative ratio compresses. The shipped verifier's G3 matches the card's pre-registered G3 exactly — no plan-vs-verifier divergence.

## External grounding
Wikipedia "Swiss-system tournament" (`https://en.wikipedia.org/wiki/Swiss-system_tournament@1357112228`) — resolved live, HTTP 200. States: "If players remain tied, a tie-break score is used, such as the sum of all opponents' scores (Buchholz system)." Confirms Buchholz = sum of all opponents' scores — the strength-of-schedule tiebreak this head decomposes into luck (whom you happened to play) vs skill (how good you are).

## Probe answers
1. **Byte-identity?** YES — `diff` exit 0; copy sha256 `f41f270b…5423f8`, git blob `0d4a4b1e…53eb`, matching the idea-engine source.
2. **Deterministic?** YES — in-process double-run `assert r1 == r2` (line 150) holds; two cross-invocation runs print byte-identical stdout (`diff run1 run2` exit 0).
3. **Digest MATCH?** YES — reproduced `0e591bb4…c0fa8` equals the disclosed digest, all 64 hex, recomputed from the compact-canonical dict.
4. **G3 = pre-registered plan?** YES — shipped G3 gates dominance (p_luck ≥ 0.70, z_diff ≥ 3, gap ≥ 0.10), identical to the card's pre-registered G3; no divergence.
5. **Ratio compression disclosed?** YES — base 3.130521 → shift 1.984682 is stated as a caveat; G3 correctly gates dominance, not the ratio.
6. **G1 reproduces?** YES — base p_luck 0.804910 ≥ 0.70; z_luck 511.920239 ≥ 3.0.
7. **G2 reproduces?** YES — base ratio 3.130521 ≥ 3.0; z_diff 234.751939 ≥ 3.0; gap 0.207511 ≥ 0.15.
8. **Grounding live?** YES — HTTP 200; article supports Buchholz = sum of opponents' scores.

## Run
Full stdout committed at `run-stdout.txt`. Two invocations byte-identical; in-process double-run asserted equal.

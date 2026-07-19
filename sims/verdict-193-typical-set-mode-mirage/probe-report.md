# Probe report — VERDICT 193: typical-set "mode mirage" (PROPOSAL 180)

**Ruling: reproduction landed — APPROVE.** The committed verifier reproduced byte-identically and deterministically; the disclosed results-dict digest matches EXACT; all three ordered gates pass on the proposal's own thresholds. (The session card is born-red/in-progress on the first commit; this report records the reproduced evidence; the card flips to complete as the last commit.)

## Source & reproduction
- Verifier source: idea-engine `ideas/fleet/typical-set-mode-mirage-2026-07-19.py` (git blob `e7be486f260944e9d1b03f77ed2c07cd309c1cbe`, stdlib-only: random, math, json, hashlib, sys), pinned at idea-engine merge SHA `4a4b123` (PROPOSAL 180, #676).
- Reproduction copy: `sims/verdict-193-typical-set-mode-mirage/typical-set-mode-mirage-2026-07-19.py`.
- Byte-identity: `diff source copy` exit 0; copy sha256 `2af59b2b67bbaf0a9cdd30dbc2109346f1296027ab50b0229bf2b7f2bd804a60`; git blob `e7be486f260944e9d1b03f77ed2c07cd309c1cbe`.
- Determinism: `main()` runs the simulation twice with an in-process double-run assert; a separate second invocation is byte-identical (`diff run1 run2` exit 0). SEED=20260717 pinned in source; z_gate=3.0.

## Digest
- Reproduced results-dict sha256 (stdout): `1479479100edba6509b0275d31717a2f44b4504d6051023feffc5f13395b8c36`.
- Proposal disclosure: `1479479100edba6509b0275d31717a2f44b4504d6051023feffc5f13395b8c36`.
- **MATCH** (all 64 hex). Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — sha256 of the compact-canonical `json.dumps(sort_keys=True, separators=(',',':'))`; no on-disk JSON.

## Gates (order G1 → G2 → G3, thresholds from the proposal)
| Gate | Claim | Statistic (measured) | Threshold | Result |
|------|-------|----------------------|-----------|--------|
| G1 | typical concentration | mean ĥ 0.881064 vs H(0.7) 0.881291 (abs diff 0.000227), in-band 1.0 | abs(mean−H) ≤ 0.10 bits, in-band ≥ 0.99 | PASS |
| G2 | mode is a mirage (≥3σ) | z_sep 1308.854386, mode_count 0 of 4000 | z_sep ≥ 3.0, mode_count = 0 | PASS |
| G3 | robust under shift p=0.9 (≥3σ) | mean ĥ 0.468904 vs H(0.9) 0.468996 (abs diff 0.000092), in-band 0.999, z_sep 671.930225, mode_count 0 | abs(mean−H) ≤ 0.10, in-band ≥ 0.99, z_sep ≥ 3.0, mode_count = 0 | PASS |

`all_pass = true`. Base: p=0.7, n_symbols=1000, n_sequences=4000, H=0.881291, mode surprisal s=0.514573, se 0.00028. Shift: p=0.9, H=0.468996, mode surprisal s=0.152003, se 0.000472.

## Theory sanity-check
The mode (all-majority sequence) has probability p^n, but there is exactly ONE such sequence. The typical set holds ~2^{nH(p)} sequences each of probability ~2^{−nH(p)}, together carrying ≈all the mass. So an observation lands in the typical set (per-symbol surprisal ≈ H(p)) with probability →1 and never on the mode — even though the mode is the single most-probable sequence. At p=0.7 the observed surprisal 0.881064 bits exceeds the mode's 0.514573 bits by 1308.85σ; the sequence you see is each ~2^{n(H−s)} times LESS probable than the mode you never see. This is the generic case, not a large-deviation rarity.

## External grounding
Wikipedia "Asymptotic equipartition property" (`https://en.wikipedia.org/wiki/Asymptotic_equipartition_property@78b633eddfc34ed73d8a1a7250cc1ceb38bc1d52`) — resolved live, HTTP 200. Documents the AEP and the typical set fundamental to data compression — supporting the typical-set-vs-mode split this head decomposes.

## Probe answers
1. **Byte-identity?** YES — `diff` exit 0; copy sha256 `2af59b2b…804a60`, git blob `e7be486f…1cbe`, matching the idea-engine source.
2. **Deterministic?** YES — in-process double-run assert holds; two cross-invocation runs print byte-identical stdout (`diff` exit 0).
3. **Digest MATCH?** YES — reproduced `1479479100…8c36` equals the disclosed digest, all 64 hex, recomputed from the compact-canonical dict.
4. **G1 concentration?** YES — mean ĥ 0.881064 within 0.000227 of H(0.7) 0.881291; in-band 1.0 ≥ 0.99.
5. **Mode observed 0 times?** YES — base_mode_count 0 and shift_mode_count 0 of 4000 draws.
6. **z_sep ≥ 3σ at both p?** YES — 1308.854386 at p=0.7 and 671.930225 at p=0.9.
7. **Shift preserves concentration + mirage?** YES — mean ĥ 0.468904 vs H 0.468996, in-band 0.999, z_sep 671.93, mode 0.
8. **Grounding live?** YES — HTTP 200; the AEP page documents the typical set carrying ≈all the mass.

## Run
Full stdout committed at `run-stdout.txt`. Two invocations byte-identical; in-process double-run asserted equal.

**Recommendation: APPROVE — reproduce byte-identical, digest MATCH, G1 → G2 → G3 all PASS; land V193 and advance the verdict high-water V192 → V193.**

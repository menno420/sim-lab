# VERDICT 176 — mana-screw-deck-size — reproduction report

Clean-room reproduction of `ideas/superbot-games/mana_screw_deck_size.py`
(idea-engine PROPOSAL 163). All numbers below are measured in this session.

## Verifier provenance

- Source: `/home/user/idea-engine/ideas/superbot-games/mana_screw_deck_size.py`
- Copied to: `sims/verdict-176-mana-screw-deck-size/mana_screw_deck_size.py`
- Byte-identical to source: `diff` exit **0**
- `sha256sum`: `3eb604e18fa42fca7a085ed27211a301c119d93bf419d97754533f3f4d2f788d`
- `git hash-object` (blob): `3f3e60326432260c5fd5abe1c7e639af15b9aca2`

## Run posture

- SEED: **20260717** (a module constant `SEED`; not env/argv-driven)
- TRIALS = 400000 Monte-Carlo opening hands per regime
- Digest posture (as disclosed by the paired doc): WHOLE-DICT / NO-SELF-FIELD /
  STDOUT-ONLY — the ordered results dict does NOT contain its own hash; floats
  are `round()`-ed to 6 dp; the preimage is the compact canonical JSON
  `json.dumps(results, sort_keys=True, separators=(",",":"))` encoded UTF-8,
  hashed with sha256.

## Determinism

- In-process double run byte-identical: **True** (asserted by `main()`, which
  runs the pipeline twice and asserts the two canonical digests are equal).
- Cross-invocation (two separate `python3` processes): stdout `diff` exit **0**
  — BYTE-IDENTICAL.
- Both process invocations exited **0** (all_pass true).

## Results-dict digest

- Computed (verifier's own print): `1280ae6278b508f00d3737841768181288e7ed31f12a443d5982b5f03b898e33`
- Independently recomputed with the disclosed posture: `1280ae6278b508f00d3737841768181288e7ed31f12a443d5982b5f03b898e33`
- Disclosed value: `1280ae6278b508f00d3737841768181288e7ed31f12a443d5982b5f03b898e33`
- Verdict: **MATCH**

## Gates — measured statistics

### G1 — bigger deck more often off-curve at matched land fraction (rejects ratio-only null)
- offcurve_a_40card = **0.209482**
- offcurve_b_60card = **0.224975**
- diff_b_minus_a = **0.015493**
- se = **0.000922**
- z = **16.804944**
- pass = **true** (z >= 3.0, one-sided; bigger deck strictly more off-curve)

### G2 — measured variance ratio matches the closed-form FPC ratio (anchor / match gate)
- var_a_measured = **1.418017**
- var_b_measured = **1.504962**
- var_ratio_measured_b_over_a = **1.061314**
- fpc_ratio_closed_form = **1.061633**
- se_ratio = **0.003175**
- mean_a_check = **2.799585**, mean_b_check = **2.7988**
- z = **-0.100413**
- pass = **true** (this is a MATCH gate: pass condition is |z| < 3.0, i.e.
  measured ≈ closed form, NOT a directional z >= 3 gate)

### G3 — robust under shifted land fraction (p = 0.30, keep window [1,3])
- offcurve_a_40card = **0.167433**
- offcurve_b_60card = **0.181385**
- diff_b_minus_a = **0.013952**
- se = **0.000848**
- z = **16.44651**
- pass = **true**

### Decision
- all_pass = **true**, first_failing_gate = **null**

All three measured gate results match the doc's disclosed values exactly.

## Algebra sanity check (closed form)

Opening-hand land count is hypergeometric: draw n = 7 from a deck of N cards of
which `lands` are lands, at a matched land fraction p = lands/N = 0.40 so the
expected land count n·p = 2.8 is **equal** for both decks. The hypergeometric
variance is

    Var = n·p·(1−p)·(N−n)/(N−1),

where the finite-population correction FPC = (N−n)/(N−1) is the only term that
depends on deck SIZE at a matched fraction. At n = 7:

    N = 40 → FPC = 33/39 = 0.846154
    N = 60 → FPC = 53/59 = 0.898305

so 0.846154 < 0.898305 — the SMALLER (40-card) deck has strictly LOWER
opening-hand land-count variance despite the equal expected 2.8 lands, and the
variance ratio B/A is the FPC ratio 0.898305 / 0.846154 = **1.061633**. The
measured Monte-Carlo variance ratio **1.061314** agrees with this closed form
to ~3 decimals (|z| = 0.10, within Monte-Carlo error, G2). The equal means
(mean_a_check 2.799585, mean_b_check 2.7988 ≈ 2.8) confirm the fraction is
matched, so the consistency gap is driven by SIZE via the FPC, not by the land
ratio. G1 (bigger deck 0.224975 vs 0.209482 off-curve) and G3 under the shifted
fraction (0.181385 vs 0.167433) confirm the same SIGN.

## Grounding

- `curl -sS -o /dev/null -w "%{http_code}" https://en.wikipedia.org/wiki/Hypergeometric_distribution`
  → HTTP **200** (live, through the configured proxy).

## Verdict

Clean-room re-run reproduces the disclosed results-dict sha256, is
deterministic in-process and cross-invocation, and G1 ∧ G2 ∧ G3 all PASS on the
proposal's own criteria (all_pass = true) — G1/G3 directional at z ≈ +16.8 /
+16.4 and G2 the anchor match at |z| = 0.10 < 3. The measured numbers agree
with the hypergeometric FPC closed form.

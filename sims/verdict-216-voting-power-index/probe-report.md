# VERDICT 216 — voting power is not voting weight: under a weighted voting game [q; w_1..w_n] a voter's Banzhaf / Shapley–Shubik power is NOT proportional to its weight — reproduce PROPOSAL 203

- **Slice:** VERDICT 216 · PROPOSAL 203 (P203 → V216, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 203 — **voting power is not voting weight.** In a
  weighted voting game `[q; w_1..w_n]` a coalition `S` wins iff its total weight `≥ q`;
  voter `i` is a swing (critical) in a coalition iff removing `i` flips a win to a loss.
  The Banzhaf index normalizes swing counts; the Shapley–Shubik index normalizes pivotal
  shares over orderings. The head: a voter's power is NOT proportional to its weight — a
  larger-weight bloc can hold identical power to a smaller one, a positive-weight voter can
  be a DUMMY with zero power, and the two canonical indices can disagree
  (`ideas/superbot-games/voting-power-not-weight-2026-07-20.md`)
- **Verifier (source):** idea-engine
  `ideas/superbot-games/voting-power-not-weight-2026-07-20.py`
- **Reproduced by:** sim-lab session 2026-07-20-verdict-216, branch `claude/verdict-216`
  (built off origin/main `8261cb9`)
- **Timestamp (date -u):** 2026-07-20T08:26Z
- **SEED:** 20260717 · **Z_GATE:** 3.0 · stdlib-only (`hashlib`, `json`, `random`,
  `fractions`, `itertools`, `math`)

## Head

A weighted voting game `[q; w_1..w_n]`: coalition `S` wins iff `Σ_{i∈S} w_i ≥ q`. Voter `i`
is a **swing** (critical) in `S` (with `i ∉ S`) iff `S` loses but `S ∪ {i}` wins. The
**Banzhaf** power index normalizes each voter's swing count; the **Shapley–Shubik** index
normalizes each voter's pivotal share over all `n!` orderings. Both are computed EXACTLY
via `fractions.Fraction` by coalition enumeration; Banzhaf is cross-checked by an exact
weight generating-function DP. The head is that **power is not weight**: under
`[51; 50,49,1]` the 49-weight bloc has the SAME power as the 1-weight bloc (Banzhaf `1/5`
each, Shapley–Shubik `1/6` each) while the 50-weight bloc holds `3×` the Banzhaf power
(`3/5`); positive-weight DUMMIES (weight yet zero power) occur across the exhaustive n=4
enumeration; the two canonical indices disagree in a nonzero number of games; and over
larger seeded games the biggest bloc's Banzhaf power systematically exceeds its weight
share. The verifier certifies this four ways (G1 exact headline instance, G2 exact
exhaustive dummy/ratio enumeration, G3 exact index-disagreement enumeration, G4 seeded
≥3σ robustness).

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` →
  **exit 0** (byte-for-byte identical; source
  `ideas/superbot-games/voting-power-not-weight-2026-07-20.py`, 8423 bytes).
- **Ran under SEED=20260717, Z_GATE=3.0**, full stdout captured to `run-stdout.txt`,
  process **exit 0** (`all_pass = true`).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`; whole-dict, no self-field, stdout-only):**
  - disclosed (PROPOSAL 203): `660bb1e59107c98a1b10256d3dfa195346a02298cba9753a9aef3e2281ece254`
  - reproduced (this run):    `660bb1e59107c98a1b10256d3dfa195346a02298cba9753a9aef3e2281ece254`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality,
    single unique 64-hex token, no truncation). The verifier PRINTS this digest
    (`results_sha256: …` in `run-stdout.txt`).

## Determinism

- **In-process:** the verifier builds the results dict TWICE within one process
  (`build_results()` called twice) and exits 3 with `NON-DETERMINISTIC` if the two
  compact-canonical serializations diverge. This run did NOT exit 3 — the in-process
  double-run converged (identical).
- **Separate cross-invocation:** two independent `python3` invocations both printed
  `results_sha256: 660bb1e59107c98a1b10256d3dfa195346a02298cba9753a9aef3e2281ece254`
  (identical results-dict digest both times, byte-identical stdout).
- The only stochastic gate (G4) pins its stream off `random.Random(SEED)` with
  `SEED = 20260717`, so the whole-dict sha256 is a reproducible determinism digest with no
  self-field.

## Gate evaluation (against PROPOSAL 203's OWN criteria, in order)

Each gate is read in ITS OWN direction. **G1/G2/G3 are EXACT gates** (exact `Fraction`
equality / exact enumeration counts — no sampling, self-certifying). **G4 is a ROBUSTNESS
+ ≥3σ SIGNAL gate** (a LARGE z is the PASS — the large-voter premium must be significantly
positive). Reading G4 as an agreement gate would invert the PASS.

- **G1 — EXACT headline instance (DIRECTION: exact fraction equality):** `[51; 50,49,1]`
  (majority quota `q = 51`):
  - Banzhaf normalized index `= (3/5, 1/5, 1/5)` EXACT.
  - Shapley–Shubik normalized index `= (2/3, 1/6, 1/6)` EXACT.
  - The **49-weight bloc has IDENTICAL power to the 1-weight bloc under BOTH indices**
    (Banzhaf `1/5 == 1/5`, Shapley–Shubik `1/6 == 1/6`), while the 50-weight bloc holds
    `3×` the Banzhaf power (`3/5`). A one-unit weight difference (49 vs 1) buys ZERO power
    difference; a one-unit difference (50 vs 49) buys a `3×`/`4×` power jump — power is
    plainly not weight.
  - Banzhaf swing counts agree brute-vs-DP (`methods_agree = true` — closed-form
    generating-function DP `==` exhaustive enumeration). Independently brute-forced and
    confirmed off-verifier. **PASS.**
- **G2 — EXACT exhaustive n=4, weights 1..6 (DIRECTION: dummy_count > 0, methods agree
  all, max ratio > 1):** all `6^4 = 1296` games enumerated:
  - `dummy_count = 540` games contain a **positive-weight dummy** (a voter with weight yet
    ZERO swings ⇒ zero power); first witness `[1,1,1,4]` at `q = 4`.
  - `max_power_weight_ratio = 5/2` — the maximum (power-share / weight-share) strictly
    exceeds 1, attained at `[1,2,6,6]` (`q = 8`): power is not proportional to weight, and
    a bloc can carry `2.5×` its weight share in power.
  - `methods_agree_all = true` — brute swing counts `==` generating-function DP for ALL
    1296 games. Independently brute==DP confirmed. **PASS.**
- **G3 — EXACT exhaustive n=4 (DIRECTION: index_unequal_count > 0):** over the same 1296
  games the Banzhaf and Shapley–Shubik normalized vectors DIFFER in
  `index_unequal_count = 80` games — the two "canonical" power measures give materially
  different answers. `max_index_l1 = 1/10` (max L1 gap between the two normalized vectors),
  attained at `[1,1,1,3]` (`q = 4`). **PASS.**
- **G4 — ROBUSTNESS + ≥3σ (DIRECTION: mean > 0 AND z ≥ 3.0):** over a seeded sample of
  larger games (`n ∈ {5,6,7}`, `per_n = 1000`, weights `1..20`, `SEED = 20260717`), the
  top voter's Banzhaf power-share minus its weight-share has:
  - `sample = 3000`, `mean_power_minus_weight_share = +0.033793`, `sem = 0.001295`,
    `z = 26.104016` — strictly positive mean, `z ≥ 3.0` by a wide margin (a large-voter
    premium: the biggest bloc's power systematically exceeds its weight). **PASS.**

`all_pass = true` (`gates = {G1:true, G2:true, G3:true, G4:true}`).

## Grounding

- **Source:** Wikipedia "Banzhaf power index" oldid **1347671339** (raw wikitext).
- **Byte-pin:** raw-wikitext plain sha1 **`ec2eab5bed81ab8f7385fe3dfd4b758ae507b79e`** —
  matches the disclosed pin (`banzhaf-power-index-oldid-1347671339.wikitext` in the sim
  dir).
- **Content:** the article documents the phenomenon directly — (a) power is NOT the same as
  weight share; (b) voters with DIFFERENT weights can have EQUAL power; (c) the DUMMY voter
  (positive weight, zero power). The head's mechanism is squarely on-page.
- **Honest caveat (recorded):** the article's WORKED examples use DIFFERENT weight triples
  (`[6; 4,3,2,1]`, U.S. Electoral College votes, Nassau County) — NOT the exact
  `[50,49,1]` triple. So the specific 50-49-1 witness (49-bloc power `==` 1-bloc power)
  is **firsthand-computed** here, while the PHENOMENON it exhibits (power ≠ weight,
  equal-power-different-weights, dummies) is documented on-page. This caveat is FAIR and
  does **NOT** block APPROVE: the Banzhaf and Shapley–Shubik indices are exact,
  self-certifying combinatorial math (`fractions.Fraction`, no sampling in G1/G2/G3) — the
  `[50,49,1]` fractions can be verified by hand, and were independently brute-forced and
  confirmed off-verifier. External + byte-pinned grounding of the phenomenon — **STRONG**,
  with the honest firsthand-witness caveat.

## Ruling evidence summary

Digest matches full-64 exact
(`660bb1e59107c98a1b10256d3dfa195346a02298cba9753a9aef3e2281ece254`, printed
`results_sha256:` line, single unique 64-hex token, no truncation); verifier byte-identical
(`diff` source↔copy exit 0, source `ideas/superbot-games/voting-power-not-weight-2026-07-20.py`);
deterministic (in-process double-run converged — no exit 3 — AND two cross-invocation
processes both `660bb1e5…ece254`). All four gates hold in their stated directions:
**G1** EXACT `[51; 50,49,1]` Banzhaf `(3/5,1/5,1/5)` / Shapley–Shubik `(2/3,1/6,1/6)` with
49-bloc power `==` 1-bloc power under both indices and brute `==` DP; **G2** EXACT
exhaustive n=4 (540 positive-weight dummies, max power/weight ratio `5/2` at `[1,2,6,6]`,
brute `==` DP all 1296); **G3** EXACT exhaustive n=4 (Banzhaf `≠` Shapley–Shubik in 80
games, max L1 `1/10` at `[1,1,1,3]`); **G4** ROBUSTNESS + ≥3σ (large-voter premium mean
`+0.033793`, `z = 26.104016 ≥ 3.0`, sample 3000, SEED 20260717). Grounding is byte-pinned
(Wikipedia "Banzhaf power index" oldid 1347671339, raw-wikitext plain sha1
`ec2eab5bed81ab8f7385fe3dfd4b758ae507b79e`) and documents the phenomenon (power ≠ weight,
equal-power-different-weights, dummy voter), with an honest caveat that the on-page worked
examples use different weights so the `[50,49,1]` witness is firsthand — which does not
block, since the indices are self-certifying exact math. Reproduces the disclosed digest
byte-for-byte, all gates hold in direction, external grounding supports the head →
**APPROVE**. (Run stdout: `run-stdout.txt`.)

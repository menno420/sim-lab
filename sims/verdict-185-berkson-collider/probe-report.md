# VERDICT 185 — Berkson's collider selection · reproduction record

Reproduces **PROPOSAL 172** (Berkson's collider paradox) at the +13 offset. Factual reproduction of the idea-engine reference verifier; ruling in the session card.

## Verifier (byte-identical copy)
- Path: `sims/verdict-185-berkson-collider/berkson_collider_selection.py`
- `diff` against the idea-engine reference: **exit 0** (byte-identical)
- file sha256: `66c97ffdf0949c6fe75acb5644e791bb21220a25634e047acf5db8d8a5037bb3`
- git blob: `162dab4c24de82f1b5e1556c91525ee09868fdb3`
- Stdlib-only (`math`, `json`, `hashlib`, `random`, `sys`); Python 3. `SEED = 20260717` pinned in-source; the `SEED` env var is inert.

## Determinism
- Cross-invocation: two independent `SEED=20260717 python3 …` runs → `diff` of the two stdout captures **exit 0** (byte-identical).
- In-process: `main()` runs `run()` twice and asserts the two compact-canonical serializations are identical before printing (`assert _canon(r1) == _canon(r2)`), which held.

## Results-dict digest
- Posture: **whole-dict / no-self-field / stdout-only** — the results dict carries no digest field; the script canonicalizes with `json.dumps(d, sort_keys=True, separators=(",",":"))` and sha256s that.
- Script-printed digest: `42a47b8890316dd5d9da056f1598ad4e3b7472678ffb0e4d3a62c25cadc19e0b`
- Independently recomputed (parse printed JSON → re-canonicalize → sha256): `42a47b8890316dd5d9da056f1598ad4e3b7472678ffb0e4d3a62c25cadc19e0b`
- Disclosed expected: `42a47b8890316dd5d9da056f1598ad4e3b7472678ffb0e4d3a62c25cadc19e0b`
- **Result: EXACT MATCH** (three-way, all 64 hex).

## Gate outcomes (order G1 → G2 → G3)
- **G1 — collider-induced negative correlation (`G1_selected_negative`): PASS.** Gaussian top-10% selected mean r = `-0.710835` (std 0.021896), z = `+459.110893`. The elite within-group correlation is strictly negative at ≥3σ.
- **G2 — selection-induced reversal (`G2_selection_induced_reversal`): PASS.** Full-population mean r = `-1.7e-05` (≈ 0, control), selected-minus-population mean = `-0.710818`, z = `+454.654805`. Conditioning on the collider flips ~0 correlation to strongly negative.
- **G3 — robust under shifted marginals (`G3_robust_nonnormal`): PASS.** Uniform marginals r = `-0.49835`, z = `+305.311106`; exponential marginals r = `-0.738422`, z = `+531.488409`. Both strictly negative at ≥3σ — not Gaussian-specific.
- **Non-gated deepening:** tight top-2% mean r = `-0.796923` vs loose top-40% mean r = `-0.52506` (diff mean -0.271863, z = +110.99457) — tightening the cut deepens the negative correlation toward r → -1, the collider prediction.
- `all_pass = true`, `first_failing_gate = null`, exit 0. Config: n_per_trial 8000, trials 200, top_frac 0.1, tight_frac 0.02, loose_frac 0.4, z_gate 3.0, seed 20260717.

## Mechanism (confirmed from the numbers)
X and Y are independent in the population (population_mean_r ≈ -1.7e-05 ≈ 0), yet conditioning on X+Y above a threshold — a collider (X → S ← Y) — manufactures a strong negative correlation inside the selected set (-0.710835). The reproduction supports the collider-selection mechanism: the negative within-elite correlation is an artifact of the selection cut, not a population trade-off.

## Grounding
- https://en.wikipedia.org/wiki/Berkson%27s_paradox — live **HTTP 200**; page describes Berkson's paradox / collider selection bias ("two independent events become conditionally dependent given that at least one occurs"), matching the reproduced mechanism.

## Ruling
Digest EXACT MATCH, determinism holds, all three gates PASS in order on the proposal's own thresholds → **APPROVE**. Verdict high-water advances V184 → V185 (union-max, no regress).

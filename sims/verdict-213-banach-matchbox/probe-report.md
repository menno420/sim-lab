# VERDICT 213 — Banach's matchbox problem: residual-count pmf and asymptotic mean: reproduce PROPOSAL 200

- **Slice:** VERDICT 213 · PROPOSAL 200 (P200 → V213, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 200 — Banach's matchbox residual: the count `K` left in the non-empty pocket when the other is first found empty has pmf `P[K=k]=C(2N−k,N−k)(1/2)^(2N−k)` and mean `E[K] ~ 2√(N/π)−1` (`ideas/fleet/banach-matchbox-residual-2026-07-20.md`)
- **Verifier (source):** idea-engine `ideas/fleet/banach_matchbox_residual.py` (git blob `f08cb3b3be6e11f11cd5c7f85523356462b9ed4a`, origin/main `a9feab5`)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-213-banach-matchbox, HEAD-synced idea-engine `a9feab5` / sim-lab `56e1aab` (branch `claude/verdict-213`)
- **Timestamp (date -u):** 2026-07-20T06:29:50Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`) · Z_GATE=3.0

## Head

A mathematician carries two matchboxes, one in each pocket, each initially holding
`N` matches. Each time a match is needed a pocket is chosen by a **fair coin**
(prob 1/2 each) and one match removed; eventually a pocket is chosen and found
**empty**. `K` is the number of matches remaining in the OTHER box at that instant.
The claim: `K` has the exact probability mass function
`P[K = k] = C(2N−k, N−k)·(1/2)^(2N−k)`, equal by the `C(a,b)=C(a,a−b)` symmetry to
`C(2N−k, N)·2^−(2N−k)`, and its mean grows like the asymptotic
`E[K] ~ 2√(N/π) − 1`. The verifier certifies the pmf/expectation EXACTLY against an
independent dynamic program for `N ∈ {10, 50}`, corroborates the mean with a
2,000,000-trial Monte-Carlo simulation, and checks the asymptotic constant
`2/√π = 1.128379` is approached monotonically from above.

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` →
  **exit 0** (git blob `f08cb3b3be6e11f11cd5c7f85523356462b9ed4a` on both sides;
  `git hash-object` of the copy equals the source blob on idea-engine origin/main
  `a9feab5`).
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process
  **exit 0** (`all_pass = True`).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`):**
  - disclosed (PROPOSAL 200): `e162890959eba728cf83004508a213f3585009bcc8fbc6e8bebdab753c576f56`
  - reproduced (this run):    `e162890959eba728cf83004508a213f3585009bcc8fbc6e8bebdab753c576f56`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality,
    hex-char count = 64, no truncation). The verifier PRINTS this digest
    (`results_sha256=…`); an independent out-of-band recompute
    (`hashlib.sha256(canonical(build_results()).encode()).hexdigest()`) reproduces the
    same 64 hex, and two fresh cross-invocation runs are byte-identical — all agree.
- Digest posture: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the compact-canonical
  results dict's own sha256 IS the digest; it is not a field inside the dict.

## Determinism

- **In-process double-run** — `main()` builds the results twice and asserts the
  canonical serializations are identical, exiting non-zero on divergence; the guard
  holds, exit 0. The Monte-Carlo gate constructs a fresh `random.Random(SEED)` at
  entry, so the two builds draw the identical stream.
- **Separate cross-invocation** — two independent `python3` invocations produced
  byte-identical stdout, hence the identical results-dict sha256 `e162890…c576f56`.

## Exact-arithmetic self-certification (the load-bearing evidence)

The firsthand gate is not a statistical estimate. **G1** computes the pmf two
INDEPENDENT ways and checks they agree EXACTLY in `fractions.Fraction`: the
closed-form `P[K=k] = C(2N−k, N−k)·(1/2)^(2N−k)` versus a dynamic program over the
random-walk absorption, term by term, for `N ∈ {10, 50}`. For each `N` the gate
certifies `pmf_equal = true` (every mass term matches exactly), `sum_is_one = true`
(the exact `Fraction` pmf sums to exactly 1), and `ek_equal = true` (the closed-form
`E[K]` equals the DP `E[K]` exactly). The exact means are pure rationals —
`N=10`: `707825/262144 ≈ 2.700138`; `N=50`:
`1115296899859219265664919877185/158456325028528675187087900672 ≈ 7.038513` — with
no float anywhere in the certification path. These are self-certifying,
independently re-checkable identities; this is what makes the APPROVE clean, with the
G2/G3/G4 statistics corroborating rather than carrying the ruling.

## Gate evaluation (against PROPOSAL 200's OWN criteria, in order)

- **G1 — EXACT PMF / EXPECTATION (Fraction-exact; closed form == DP is the PASS):**
  for `N ∈ {10, 50}` the exact-`Fraction` pmf equals the dynamic-programming pmf term
  by term (`pmf_equal = true`), each pmf sums to exactly 1 (`sum_is_one = true`), and
  the closed-form `E[K]` equals the DP `E[K]` exactly (`ek_equal = true`):
  - `N=10` exact `E[K] = 707825/262144 ≈ 2.700138`,
  - `N=50` exact `E[K] = 1115296899859219265664919877185/158456325028528675187087900672 ≈ 7.038513`.
  `G1_exactly_true = true.` *(core proof — the firsthand exact-pmf identity)*
- **G2 — SIGNAL 3σ (wants a real, significant effect):** `z2 = 1839.497873 ≥ 3` —
  the measured effect is overwhelmingly significant, not sampling noise.
  `G2_signal_3sigma = true.`
- **G3 — SIM AGREEMENT (wants `|z| < 3`):** the 2,000,000-trial Monte-Carlo mean
  `sim_mean = 7.04112` (se `0.003828`) agrees with the exact `E[K]≈7.038513` for the
  head case `N=50`: `z3 = 0.681218`, `|z3| < 3`. The simulation confirms the exact
  closed form. `G3_agreement = true.`
- **G4 — ASYMPTOTIC ROBUSTNESS (wants monotone approach to the constant from
  above):** the ratios `(E[K]+1)/√N` for `N ∈ {10, 50, 200}` are
  `1.170086 → 1.136817 → 1.130493` — monotonically DECREASING and every one strictly
  exceeds `2/√π = 1.128379`, exactly the behaviour predicted by
  `E[K] ~ 2√(N/π) − 1` (so `(E[K]+1)/√N → 2/√π` from above).
  `G4_robustness = true.`

**all gates pass in order**, `all_pass = true`.

## Grounding

- **Source:** Wikipedia "Banach's matchbox problem" oldid **1356179739**, raw wikitext
  (`index.php?title=Banach%27s_matchbox_problem&oldid=1356179739&action=raw`,
  MediaWiki API).
- **Fetch:** revision RESOLVES (raw wikitext, **2819 bytes**); raw-wikitext sha1
  `2a9bfea32a4ea817258b2a97ef8366cbaf7e6ec3` — **EXACT MATCH** to the disclosed pin,
  confirmed THREE ways: local `sha1sum` of the raw wikitext byte stream, AND the
  MediaWiki API `rvprop=sha1` for the same oldid — all agree byte-for-byte.
- **Content:** the revision states the exact pmf
  `P[K=k] = C(2N−k, N−k)·(1/2)^(2N−k)` (equivalently `C(2N−k, N)·2^−(2N−k)` by
  symmetry) and the asymptotic mean `2√(N/π) − 1` — exactly the two facts the
  verifier reproduces (G1's exact pmf and G4's asymptotic constant). A disclosed
  stray-"r" typo is confined to the exact-expectation line; it does NOT touch the pmf
  or the asymptotic, is **fairly disclosed** in the reproduction, and is **non-fatal**
  to grounding. **STRONG external byte-pinned grounding** — the pin resolves, the
  sha1 is byte-exact across three independent checks, and the pinned article states
  both load-bearing facts.

## Ruling evidence summary

Digest matches full-64 exact (`e162890…c576f56`, printed `results_sha256=` +
independently recomputed + byte-identical across two cross-invocation runs, all agree,
64 hex no truncation); verifier byte-identical (`diff` exit 0, git blob
`f08cb3b3`); deterministic (in-process double-run guard holds, exit 0). The
load-bearing gate is firsthand exact: **G1** certifies the closed-form `Fraction` pmf
against an independent DP term-by-term for `N ∈ {10, 50}`, each pmf summing to exactly
1 and `E[K]` exact-equal (`N=10` `707825/262144`, `N=50`
`1115296899859219265664919877185/158456325028528675187087900672`). **G2** confirms the
effect is real (`z2 = 1839.50 ≥ 3`), **G3** confirms the 2,000,000-trial sim mean
`7.04112` agrees with the exact `E[K]≈7.038513` (`z3 = 0.681218`, `|z| < 3`), and
**G4** confirms the asymptotic constant is approached monotonically from above
(`(E[K]+1)/√N = 1.170086 → 1.136817 → 1.130493`, all `> 2/√π = 1.128379`). Grounding
resolves byte-exact (Wikipedia "Banach's matchbox problem" oldid 1356179739,
raw-wikitext sha1 `2a9bfea32a4ea817258b2a97ef8366cbaf7e6ec3`, three-way confirmed) and
states both the pmf and the asymptotic; the disclosed stray-"r" typo is confined to
the exact-expectation line and is non-fatal. Reproduces the disclosed digest
byte-for-byte, all four gates hold in their stated directions, strong byte-pinned
external grounding → **APPROVE**. Final ruling is the coordinator's: **APPROVE**.

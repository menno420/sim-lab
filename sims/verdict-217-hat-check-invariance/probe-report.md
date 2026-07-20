# VERDICT 217 — hat-check invariance: for a uniform random permutation of n items the number of fixed points has mean EXACTLY 1 for every n≥1 and variance EXACTLY 1 for every n≥2; the derangement probability D_n/n! → 1/e; the whole count → Poisson(1) — reproduce PROPOSAL 204

- **Slice:** VERDICT 217 · PROPOSAL 204 (P204 → V217, +13 offset, lane superbot fleet)
- **Source proposal:** idea-engine PROPOSAL 204 — **hat-check invariance.** A coat-check
  clerk returns n coats uniformly at random (a random permutation π). A patron is a *fixed
  point* iff π returns their own coat. The head is a triple invariance: (1) E[fixed points]
  == 1 for every n≥1 and Var == 1 for every n≥2; (2) P(full derangement) = D_n/n! =
  Σ_{k=0}^n (-1)^k/k! → 1/e ≈ 0.3679 (NOT "essentially never"); (3) the count → Poisson(1).
- **Verifier (source):** idea-engine `ideas/fleet/hat-check-fixed-points-invariance.py`
- **Source proposal PR / commit:** idea-engine **PR #757**, commit **`3b94678`**.
- **Reproduced by:** sim-lab session 2026-07-20-verdict-217, branch
  `claude/verdict-217-hat-check` (built off origin/main `d8c73fa`); claim landed on the
  control fast lane (#292), verdict PR #293.
- **Timestamp (date -u):** 2026-07-20T09:10Z
- **SEED:** 20260717 · stdlib-only (`json`, `hashlib`, `math`, `random`, `fractions`,
  `itertools`)

## Ruling recommendation: APPROVE

Digest reproduces byte-for-byte (full-64 exact), determinism holds both in-process and
across invocations, all four gates PASS in their stated directions and match the disclosed
dry-sim numbers to the digit, and the head is externally grounded (byte-pinned Wikipedia
revision) with an honest STATES-vs-PROVES caveat that does not block. The load-bearing
evidence — the G1 EXACT `Fraction` enumeration (E==1, Var==1, and three-way agreement of
the derangement counts) — is self-certifying combinatorial math, not sampling.

## Head

A weighted... no — a hat-check clerk returns n coats uniformly at random: a uniform random
permutation π of the patrons. Patron i is a **fixed point** iff `π(i) = i` (own coat back).
Let X = number of fixed points. By linearity of expectation each patron matches with
probability `1/n`, so `E[X] = n·(1/n) = 1` for EVERY n≥1; a second-moment computation gives
`Var[X] = 1` for every n≥2. The event X=0 (a full **derangement**, nobody's own coat) has
probability `D_n/n! = Σ_{k=0}^n (-1)^k/k!`, which converges to `1/e ≈ 0.3679` — so "the
clerk essentially never hands everyone the wrong coat" is FALSE; it happens roughly 37% of
the time regardless of crowd size. And the full distribution of X converges to Poisson(1).
The verifier certifies this four ways: G1 EXACT `Fraction` enumeration (n=1..8), G2 a ≥3σ
derangement-floor sample (n=200), G3 an n-invariance sweep (n∈{10,100,1000,2000}), G4 a
Poisson(1) goodness-of-fit (n=100).

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` → **exit 0**
  (byte-for-byte identical; source `ideas/fleet/hat-check-fixed-points-invariance.py`).
- **Ran under SEED = 20260717**, full stdout captured to `run-stdout.txt`, process
  **exit 0** (`decision: sim-ready`, all gates true).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`; whole-dict, no self-field, stdout-only):**
  - disclosed (PROPOSAL 204): `7b99e6504b7cfa776ce871b7756b2ff71ed5bcd025e9dd6134d0f8d8e246dfb0`
  - reproduced (this run):    `7b99e6504b7cfa776ce871b7756b2ff71ed5bcd025e9dd6134d0f8d8e246dfb0`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality;
    single unique 64-hex token in `run-stdout.txt`; no truncation). The verifier PRINTS
    this digest (`results_sha256: …`).

## Determinism

- **In-process:** `main()` calls `compute()` TWICE and `assert`s the two compact-canonical
  serializations are equal (`NON-DETERMINISTIC: in-process double-run diverged` otherwise).
  This run printed `in_process_double_run: IDENTICAL` — the assert held, in-process
  double-run identical.
- **Separate cross-invocation:** two independent `python3` invocations produced
  **byte-identical stdout** (`diff` of the two captures → exit 0), both printing
  `results_sha256: 7b99e6504b7cfa776ce871b7756b2ff71ed5bcd025e9dd6134d0f8d8e246dfb0`.
- One seeded RNG (`random.Random(20260717)`) is consumed in gate order G2 → G3 → G4, so the
  whole-dict sha256 is a reproducible determinism digest with no self-field.

## Gate evaluation (against PROPOSAL 204's OWN criteria, in order — each read in ITS direction)

Gate polarity is mixed, so each is read in its own direction. **G1 is an EXACT gate** (exact
`Fraction` identities / exact enumeration counts — no sampling, self-certifying). **G2 is a
≥3σ FLOOR gate with a two-sided consistency leg** (a LARGE z_floor is the PASS; the 1/e leg
needs a SMALL |z_inv_e|). **G3 is an AGREEMENT gate** (a SMALL cross-scale range is the
PASS). **G4 is a GOODNESS-OF-FIT gate** (a SMALL χ² below the critical value is the PASS).

- **G1 — EXACT (Fraction, exhaustive enumeration n=1..8; DIRECTION: every identity exact):**
  - `E[X] == 1` for all n≥1; `Var[X] == 1` for all n≥2 (and `Var == 0` at n=1).
  - Derangement count `D_n` computed THREE ways agrees with **zero tolerance**:
    brute-force enumeration (perms with 0 fixed points) `==` inclusion-exclusion
    `D_n = n!·Σ_{k=0}^n (-1)^k/k!` `==` recurrence `D_n = (n-1)(D_{n-1}+D_{n-2})`,
    `D_0=1, D_1=0`. **D_n table (n=0..8):**

    | n | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
    |---|---|---|---|---|---|---|---|---|---|
    | D_n | 1 | 0 | 1 | 2 | 9 | 44 | 265 | 1854 | 14833 |

    (brute == incexc == recurrence for every row; independently re-derived off-verifier
    with `fractions.Fraction` — all three agree, `E==1`/`Var==1` confirmed.) **PASS.**
- **G2 — ≥3σ derangement floor (n=200, M=80000; DIRECTION: one-sided up past the 0.30 folk
  floor AND |z| < 3 vs 1/e):**
  - `p_derange = 0.369875`, `z_floor = +40.937939` (clears the folk "essentially never"
    floor `0.30` by ~41σ — the derangement rate is emphatically NOT ~0), `inv_e =
    0.3678794412`, `z_inv_e = 1.169146` (empirical rate within 3σ of `1/e`). **PASS.**
- **G3 — n-invariance / robustness-shift (n∈{10,100,1000,2000}; DIRECTION: mean does NOT
  move with crowd size):**
  - means `{10: 1.004275, 100: 1.0002125, 1000: 1.000425, 2000: 0.9824}`, cross-scale
    `range = 0.021875 < 0.05`, every mean within 0.05 of 1. **PASS.**
- **G4 — Poisson(1) shape (n=100, M=80000, buckets k=0,1,2,3,≥4; DIRECTION: χ² < crit ⇒
  fit not rejected):**
  - Pearson `χ² = 1.36372 < 18.467` (df=4, α=0.001). Counts `[29316, 29462, 14767, 4954,
    1501]` vs expected `[29430.36, 29430.36, 14715.18, 4905.06, 1519.05]`. **PASS.**

**Independent off-verifier re-derivation:** G1 re-computed from scratch (`fractions`,
exhaustive `itertools.permutations`) — E==1/Var==1 and the three D_n methods all agree with
zero tolerance. G2 re-run with a fresh `Random(20260717)` reproduced `p_derange = 0.369875`,
`z_floor = 40.9379`, `z_inv_e = 1.1691` exactly (G2 is the first RNG consumer). G3/G4
re-evaluated fresh-seed confirm the PROPERTY in-direction (G3 range 0.007065 < 0.05; G4 χ²
1.555 < 18.467); the verifier's in-pipeline values (range 0.021875, χ² 1.36372) are the RNG
position after G2/G3 and match the disclosed dry-sim numbers exactly.

**Dry-sim match:** every gate value reproduced here (p_derange 0.369875, z_floor +40.937939,
z_inv_e 1.169146, G3 range 0.021875, χ² 1.36372) equals the disclosed dry-sim numbers to the
digit.

## Grounding

- **Source:** Wikipedia "Rencontres numbers" oldid **1340506236** (raw wikitext, MediaWiki
  API `action=query prop=revisions rvprop=content|sha1`).
- **Revision resolves:** YES (revids=1340506236 returns revid 1340506236).
- **Byte-pin:** raw-wikitext sha1 **`256b0417a6785bd9d1e50a6aa9766175ee329dc5`** — matches
  the disclosed pin AND the MediaWiki-API-reported `sha1` field exactly
  (`rencontres-numbers-oldid-1340506236.wikitext` in this sim dir).
- **Supporting statements present (YES):**
  - "For n ≥ 1, the expected number of fixed points is 1 (a fact that follows from linearity
    of expectation)." — present verbatim (wikitext:
    `For ''n''&nbsp;≥&nbsp;1, the [[expected value|expected]] number of fixed points is&nbsp;1 (a fact that follows from linearity of expectation).`).
  - Poisson(1): "the i-th moment of this probability distribution is the i-th moment of the
    Poisson distribution with expected value 1" and "the probability distribution of the
    number of fixed points … approaches the Poisson distribution with expected value 1."
  - 1/e derangement limit: `lim_{n→∞} D_{n,k}/n! = e^{-1}/k!` and `D_{n,m}/n! ≈ e^{-1}/m!`.
- **Honest caveat (recorded):** the page **STATES** the facts, the verifier **PROVES** them.
  The article documents E=1 (linearity), the Poisson(1) limit, and the `e^{-1}` derangement
  limit as prose/formulae; the verifier supplies the exact `Fraction` enumeration and the
  three-way D_n cross-check that constitute a proof-by-computation for n=1..8 plus the
  sampled ≥3σ / goodness-of-fit corroboration at scale. External + byte-pinned grounding of
  the head — **STRONG**, with the honest STATES-vs-PROVES caveat, which does **NOT** block
  APPROVE (G1 is self-certifying exact math verifiable by hand).

## Ruling evidence summary

Digest matches full-64 exact
(`7b99e6504b7cfa776ce871b7756b2ff71ed5bcd025e9dd6134d0f8d8e246dfb0`, printed
`results_sha256:` line, single unique 64-hex token, no truncation); verifier byte-identical
(`diff` source↔copy exit 0, source `ideas/fleet/hat-check-fixed-points-invariance.py`,
idea-engine PR #757 / commit `3b94678`); deterministic (in-process double-run IDENTICAL via
assert AND two cross-invocation processes byte-identical stdout). All four gates hold in
their stated directions and match the disclosed dry-sim numbers: **G1** EXACT (E==1 all
n≥1, Var==1 all n≥2, D_n brute==incexc==recurrence [1,0,1,2,9,44,265,1854,14833]); **G2**
p_derange 0.369875, z_floor +40.937939 ≥3σ over the 0.30 folk floor, z_inv_e 1.169146
within 3σ of 1/e; **G3** cross-scale range 0.021875 < 0.05; **G4** Pearson χ² 1.36372 <
18.467 (df=4, α=0.001). Grounding is byte-pinned (Wikipedia "Rencontres numbers" oldid
1340506236, raw-wikitext sha1 `256b0417a6785bd9d1e50a6aa9766175ee329dc5`, API sha1 matches)
and states the head (E=1 by linearity, Poisson(1), 1/e derangement limit), with an honest
STATES-vs-PROVES caveat that does not block. Reproduces the disclosed digest byte-for-byte,
all gates hold in direction and match dry-sim, external grounding supports the head →
**APPROVE**. (Run stdout: `run-stdout.txt`.)

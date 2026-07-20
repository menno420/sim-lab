# VERDICT 237 — Probe report (reproduces PROPOSAL 224)

> The number of labeled trees on the vertex set **{1..n}** is EXACTLY
> **T(n) = n^(n−2)** (n ≥ 2; T(1)=T(2)=1). The proof is the **Prufer bijection**:
> labeled trees on {1..n} correspond one-to-one with sequences in
> **{1..n}^(n−2)**. Encode by repeatedly removing the smallest-labeled leaf and
> recording its unique neighbor (length n−2); decode by the standard degree-count
> reconstruction. Since |{1..n}^(n−2)| = n^(n−2) and the map is a bijection,
> T(n) = n^(n−2). A uniformly random labeled tree is a uniformly random Prufer
> sequence, so a fixed vertex's appearance count is **Binomial(n−2, 1/n)** and
> **degree = appearances + 1**, giving the EXACT facts E[deg(v)] = 2(n−1)/n,
> **P(edge {i,j}) = 2/n**, and P(v is a leaf) = ((n−1)/n)^(n−2).

- **Slice:** Cayley's formula / Prufer bijection, P224 → V237 (+13 offset)
- **Branch:** `claude/v237-cayley-prufer`
- **Sim dir:** `sims/verdict-237-cayley-prufer/`
- **Source:** PROPOSAL 224 (Ideas Lab), Cayley's formula T(n)=n^(n−2) via the Prufer-sequence bijection
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of the committed
`sims/verdict-237-cayley-prufer/cayley-prufer.py` → scratch copy; `diff`
committed ↔ copy exit **0** (byte-identical, logic unaltered). Stdlib-only
(`hashlib`, `json`, `math`, `random`, `sys`, `itertools`, `fractions.Fraction`).
SEED = 20260717, Z_GATE = 3.0, N_MC = 200000, GRID = [2,3,4,5,6,7,8]. All EXACT
work (G1 brute counts, G2 roundtrip, G3 Fraction probabilities, G6 formula
rejections) uses integers and `fractions.Fraction`; the ONE `random.Random(SEED)`
is consumed sequentially across the Monte-Carlo gates in fixed order (G4 n=12 →
G5 MC n=6 → n=10 → n=20). G6's MC leg reuses the G4 n=12 empirical estimate, so
no extra RNG draw is consumed.

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256: 7e8dbff568cf62ab3e15ebdc1d9a7e893f024d10f4bd39b1630cbc444317ad1b
```

- Reproduced digest: `7e8dbff568cf62ab3e15ebdc1d9a7e893f024d10f4bd39b1630cbc444317ad1b`
  (length 64, no truncation, bit-exact). The committed `run-stdout.txt` carries
  the same digest.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-
  canonical results dict's own sha256 IS the digest; the dict carries no
  self-field hash. `canonical()` is
  `json.dumps(r, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`.
  All floats in the results dict are rounded to 6 decimals for byte-stable
  canonical JSON. Nothing is written to disk by the verifier.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice and asserts
  the canonical-JSON forms are byte-identical before printing the digest
  (`sys.exit(3)` on divergence; exit 0 here).
- **Cross-invocation:** a second separate process re-invocation produced a
  byte-identical stdout and `results_sha256`
  (`7e8dbff568cf62ab3e15ebdc1d9a7e893f024d10f4bd39b1630cbc444317ad1b`; `diff` of
  the two stdouts exit 0). The only RNG is a `random.Random(SEED)` seeded from
  the fixed SEED — no wall-clock or OS randomness.

## 4. Gates — six, all PASS in their own directions, teeth confirmed

| Gate | Direction | Observed | Pass |
|------|-----------|----------|------|
| **G1** exact Cayley identity | EQUALITY (integers) | brute counts n=2..6 = **1, 3, 16, 125, 1296** = n^(n−2) exactly | ✅ |
| **G2** exact bijection roundtrip | EQUALITY | n=5: **125** trees, encode→decode roundtrip exact for every tree, the **125** Prufer seqs = all 5³=125 distinct sequences (no collision) | ✅ |
| **G3** exact probabilities (Fraction) | EQUALITY | n=5: P(edge {1,2})=**2/5** (50/125), mean deg(1)=**8/5** (200/125), leaf prob=**64/125** | ✅ |
| **G4** MC agreement | AGREEMENT, \|z\| < 3 | n=12, 200 000 draws: P(edge)=0.166375 vs 1/6, z_edge=**−0.35**; E[deg1]=1.834915 vs 11/6, z_deg=**0.80931** | ✅ |
| **G5** robustness grid | AGREEMENT across grid | identity n=2..8 all match (n≤6 brute, n=7,8 Prufer-roundtrip 16807/262144); MC edge-prob z: n=6 **−2.36064**, n=10 **−0.905608**, n=20 **−1.557794**, all \|z\|<3 | ✅ |
| **G6** falsifiability | REJECTION (mismatch / large \|z\|) | n=4,5,6 counts ≠ n^(n−1),(n−1)!,2^(n−1) (unique match n^(n−2)); naive P=1/2 rejected z=**−298.403272**, naive P=1/n rejected z=**134.368033** | ✅ |

`all_pass=true`, `first_failing_gate=null`, N_MC=**200000** (no bump required —
G4/G5 MC realizations all landed within 3σ at this SEED).

**Teeth read per gate (each in its own direction):**
- **G1** is an exact integer identity: labeled trees are counted FIRSTHAND by
  enumerating every size-(n−1) subset of the C(n,2) candidate edges and testing
  tree-ness via union-find (acyclic ⇒ connected at n−1 edges). The counts
  1/3/16/125/1296 equal n^(n−2) to the integer; a wrong enumeration or a
  miscounted subset would break the equality. Direction correct.
- **G2** proves the bijection FIRSTHAND at n=5: every one of the 125 enumerated
  trees encodes to a Prufer sequence and decodes back to the SAME edge-set
  (roundtrip identity), AND the 125 produced sequences are exactly the 125
  elements of {1..5}³ — injective and surjective, no collision. This is the
  mechanism Cayley's formula rests on, not just the count.
- **G3** is an exact rational equality over the full n=5 enumeration: the edge-
  presence probability is Fraction(50,125)=**2/5**=2/n, the mean degree of vertex
  1 is Fraction(200,125)=**8/5**=2(n−1)/n, and the leaf probability is
  Fraction(64,125)=(4/5)³=((n−1)/n)^(n−2). No float appears; a wrong count yields
  a non-matching Fraction and fails.
- **G4** is a genuine independent stochastic estimate: 200 000 uniform Prufer
  draws at n=12, decoded, where the null P(edge)=1/6 and E[deg1]=11/6 are the
  firsthand claims; the pass is agreement within 3σ (z_edge=−0.35, z_deg=0.81). A
  broken decode or a wrong probability would shift the empirical mean off the null.
- **G5** repeats the EXACT identity across n=2..8 (n=7,8 via a Prufer roundtrip-
  consistency check: all 16807 / 262144 sequences decode to valid trees that
  re-encode to themselves, so the code is a bijection onto exactly n^(n−2)
  distinct trees) AND re-confirms P(edge)=2/n by independent MC at three further
  sizes (n=6,10,20), the largest |z| being 2.36 — all under 3σ.
- **G6** rejects concrete WRONG models at the opposite polarity: (a) for n=4,5,6
  the true counts differ (exact strict inequality) from the plausible-wrong
  n^(n−1), (n−1)!, and 2^(n−1) — only n^(n−2) matches; (b) the naive "each edge
  present independently w.p. 1/2" (P=1/2) is rejected by the n=12 MC at
  z=−298.4 (|z|≫6), and the naive P=1/n at z=+134.4 — the gate PASSES BECAUSE the
  wrong values are rejected, confirming G3/G4/G5 are not trivially passable.

## 5. Grounding

The result is the standard textbook Cayley's formula / Prufer bijection (Cayley
1889; Prufer 1918). The verifier proves it FIRSTHAND three independent ways:
(a) an exact union-find enumeration of all labeled trees for n=2..6 matching
n^(n−2); (b) an explicit encode/decode bijection at n=5 that roundtrips every
tree and covers all 125 sequences with no collision, plus a roundtrip-consistency
extension to n=7,8; and (c) a uniform-Prufer Monte-Carlo whose empirical edge
probability 2/n and mean degree 2(n−1)/n agree within 3σ while the naive 1/2 and
1/n alternatives are rejected at |z|≫6. The firsthand artifacts (the enumerator,
the encode/decode pair, SEED, the gate grids, and the digest) are off-page by
construction; the bijection and the formula are the cited framework.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256
full-64 EXACT match (bit-exact, no truncation); determinism holds on both the
in-process double-run and the separate cross-invocation legs; all six pre-
registered gates PASS each in its own direction — three exact identities (G1
brute-count Cayley identity, G2 bijection roundtrip, G3 Fraction probabilities),
two Monte-Carlo AGREEMENT gates within 3σ (G4 z_edge=−0.35 / z_deg=0.81, G5
max|z|=2.36 across n∈{6,10,20}), and one FALSIFIABILITY gate that rejects the
three wrong count-formulas and the naive edge probabilities (1/2 at z=−298.4, 1/n
at z=+134.4) at the opposite polarity. No qualification required.

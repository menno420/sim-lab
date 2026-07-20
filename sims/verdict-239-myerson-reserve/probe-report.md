# VERDICT 239 — Probe report (reproduces PROPOSAL 226)

> Sell one item to **n** bidders with valuations iid **Uniform[0,1]**. The
> Myerson revenue-maximizing mechanism is a **second-price auction with reserve
> r* = 1/2**, the SAME for every n, and its expected revenue is the exact
> rational **R*(n) = 2n/(n+1) − 1 + (1/2)^n/(n+1)**. Hence **R*(2) = 5/12**,
> strictly above the no-reserve second-price revenue **1/3** — an extra
> **1/12** of surplus captured by the reserve.

- **Slice:** Myerson optimal reserve, P226 → V239 (+13 offset)
- **Branch:** `claude/verdict-239-myerson-reserve`
- **Sim dir:** `sims/verdict-239-myerson-reserve/`
- **Source:** PROPOSAL 226 (Ideas Lab), Myerson optimal reserve r*=1/2 for iid Uniform[0,1] bidders, R*(n)=2n/(n+1)−1+(1/2)^n/(n+1)
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of the committed
`sims/verdict-239-myerson-reserve/myerson-optimal-reserve.py` → scratch copy;
`diff` committed ↔ copy exit **0** (byte-identical, logic unaltered). Stdlib-only
(`hashlib`, `json`, `random`, `fractions.Fraction`). SEED = 20260717,
Z_GATE = 3.0, N_MC = 200000, dyadic reserve GRID = {0, 1/8, …, 1}. All EXACT
work (G1 virtual value, G2 three-route agreement, G3 Fraction revenues, G6 grid
optimum) uses `fractions.Fraction`; the ONE `random.Random(SEED)` is consumed
sequentially across the Monte-Carlo gates in fixed order (G4/G7 paired n=2 →
G5 n=3). The head claim is the SAME reserve r*=1/2 for every n.

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256: b125afaf186e8d2430783b89af1a877193a65752db77884458485ced7ec918f0
```

- Reproduced digest: `b125afaf186e8d2430783b89af1a877193a65752db77884458485ced7ec918f0`
  (length 64, no truncation, bit-exact). The committed `run-stdout.txt` carries
  the same digest.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-
  canonical results dict's own sha256 IS the digest; the dict carries no
  self-field hash. `canonical()` is
  `json.dumps(r, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`.
  All floats in the results dict are stored via `repr()` for byte-stable
  canonical JSON. Nothing is written to disk by the verifier.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice
  (`build_results()` is a pure function of SEED and fixed params, holding no
  digest of itself) and asserts the canonical-JSON forms are byte-identical
  before printing the digest (`SystemExit(3)` on divergence; exit 0 here).
- **Cross-invocation:** a second separate process re-invocation produced a
  byte-identical stdout and `results_sha256`
  (`b125afaf186e8d2430783b89af1a877193a65752db77884458485ced7ec918f0`). The only
  RNG is a `random.Random(SEED)` seeded from the fixed SEED — no wall-clock or
  OS randomness. Python 3.11.15.

## 4. Gates — seven, all PASS in their own directions

| Gate | Direction | Rule | Result |
|------|-----------|------|--------|
| **G1** psi_zero_at_half | EQUALITY | psi(1/2)=2·(1/2)−1=0 exact (Fraction) | ✅ PASS |
| **G2** three_routes_agree | EQUALITY | R_closed == R_integral == R_decomp for n∈{1,2,3,4,5} (Fraction); Rstar = {1:1/4, 2:5/12, 3:17/32, 4:49/80, 5:43/64} | ✅ PASS |
| **G3** R2_5_12_gain_1_12 | EQUALITY | R*(2)=5/12, no-reserve=1/3, gain=1/12 (Fraction) | ✅ PASS |
| **G4** mc_n2_agrees | AGREEMENT, \|z\|<3 | MC revenue n=2 vs 5/12; observed z=−0.8222447505199753, mean=0.41619502469293446 | ✅ PASS |
| **G5** mc_n3_agrees | AGREEMENT, \|z\|<3 | MC revenue n=3 vs 17/32; observed z=1.8159190976017108, mean=0.5322036684628617 | ✅ PASS |
| **G6** grid_opt_at_half | ROBUSTNESS | exact R(n,r) maximized at r=1/2 on dyadic grid {0,1/8,…,1} for n∈{2,3,5} | ✅ PASS |
| **G7** reject_no_reserve | REJECTION | paired MC (n=2): E[rev(r=1/2)−rev(r=0)]>0 rejects "no reserve optimal"; observed z=175.43989743655857 (>10), mean gain=0.08350364087588037 | ✅ PASS |

`all_pass=true`, `first_failing_gate=null`, N_MC=**200000** — G4/G5 MC
realizations landed within 3σ at this SEED and G7's paired gain is rejected at
z≫10.

**Teeth read per gate (each in its own direction):**
- **G1** is an exact rational equality: the virtual value psi(v)=2v−1 vanishes
  at r*=1/2 by `Fraction` arithmetic; a wrong reserve would leave psi≠0.
- **G2** proves R*(n) FIRSTHAND three independent exact ways — the closed form,
  the virtual-surplus integral, and the sell-decomposition — agreeing as exact
  `Fraction`s for n∈{1,2,3,4,5}. A wrong revenue formula breaks the triple
  equality.
- **G3** is the headline exact rational: R*(2)=5/12, the no-reserve second-price
  revenue is 1/3, and the reserve gain is exactly 1/12. No float appears.
- **G4/G5** are genuine independent stochastic estimates: 200 000 draws each,
  n=2 and n=3, where the closed-form R*(n) is the null and the pass is agreement
  within 3σ (z=−0.822, z=1.816). A broken auction rule would shift the mean off
  the null.
- **G6** is an exact robustness sweep: on the dyadic reserve grid {0,1/8,…,1}
  the exact revenue R(n,r) is maximized at r=1/2 for n∈{2,3,5} — no grid reserve
  beats the claimed optimum.
- **G7** rejects the naive "no reserve is optimal" alternative at the opposite
  polarity: the paired Monte-Carlo (n=2) gives a strictly positive expected gain
  E[rev(r=1/2)−rev(r=0)] at z=175.4 (≫10), so the gate PASSES BECAUSE the wrong
  model is rejected — confirming G3/G4 are not trivially passable.

## 5. Grounding

Pin: `https://en.wikipedia.org/w/index.php?title=Regular_distribution_(economics)&oldid=1304906615@45d380f12e80c8a69f221ff09bd3eb34b44cfe05 · fetched 2026-07-20`

Caveat: "The pinned revision of Wikipedia's Regular distribution (economics)
article quotes the virtual-valuation formula w(v) = v − (1−F(v))/f(v) verbatim
(there written with symbol w rather than psi) and states the Myerson principle
that the optimal single-item auction is a Vickrey (second-price) auction
augmented with reserve prices to guarantee non-negative virtual valuations —
i.e. a reserve set where the virtual value is zero. The article lists the
uniform distribution only as an example of a regular distribution; it does not
specialize to Uniform[0,1], does not compute psi(v)=2v−1, and does not solve
psi(r*)=0. Accordingly the specific numbers used here — r*=1/2, R*(2)=5/12,
no-reserve revenue 1/3, and the 1/12 reserve gain — appear nowhere in the pinned
wikitext and are DERIVED independently from the general theory, not quoted from
the source."

The firsthand artifacts (the virtual value, the three exact revenue routes, the
dyadic grid sweep, SEED, and the digest) are off-page by construction; the
Myerson virtual-value / reserve framework is the cited framework.

## 6. Reproduce

```
cd sims/verdict-239-myerson-reserve && python3 myerson-optimal-reserve.py
```

Exit 0; prints the results dict and
`results_sha256: b125afaf186e8d2430783b89af1a877193a65752db77884458485ced7ec918f0`.

## 7. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256
full-64 EXACT match (bit-exact, no truncation); determinism holds on both the
in-process double-run and the separate cross-invocation legs; all seven pre-
registered gates PASS each in its own direction — three exact identities (G1
virtual value at r*, G2 three-route revenue agreement, G3 the 5/12 vs 1/3 /
1/12 rationals), two Monte-Carlo AGREEMENT gates within 3σ (G4 z=−0.822,
G5 z=1.816), one exact ROBUSTNESS grid optimum (G6 r=1/2 for n∈{2,3,5}), and one
REJECTION gate that rejects the naive no-reserve alternative at z=175.4. No
qualification required.

# VERDICT 236 — Probe report (reproduces PROPOSAL 223)

> In the infinitely-repeated symmetric Prisoner's Dilemma with stage payoffs
> **T > R > P > S**, the grim-trigger strategy (cooperate until any defection,
> then defect forever) sustains mutual cooperation as a subgame-perfect
> equilibrium **iff the discount factor delta satisfies delta >= delta\* where the
> EXACT threshold is delta\* = (T − R)/(T − P)**. By the one-shot-deviation
> principle V_C(delta) = R/(1−delta) and the best one-shot deviation is
> V_D(delta) = T + delta·P/(1−delta); indifference V_C = V_D reduces to
> R − T + delta·(T − P) = 0, so at delta = delta\* the incentive gap is EXACTLY
> zero. The continuation-probability reading gives a per-episode statistic
> D_i = (R − P)·H_i − (T − P) with E[D_i] = (R − P)/(1−delta) − (T − P), which is
> **0 exactly at delta = delta\*** because 1 − delta\* = (R − P)/(T − P).

- **Slice:** grim-trigger folk-theorem threshold, P223 → V236 (+13 offset)
- **Branch:** `claude/verdict-236-grim-trigger-folk-theorem`
- **Sim dir:** `sims/verdict-236-grim-trigger-folk-theorem/`
- **Source:** PROPOSAL 223 (Ideas Lab), grim-trigger folk-theorem threshold delta\* = (T−R)/(T−P)
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of the committed
`sims/verdict-236-grim-trigger-folk-theorem/grim-trigger-folk-theorem.py`
→ scratch copy; `diff` committed ↔ copy exit **0** (byte-identical, logic
unaltered). Stdlib-only (`hashlib`, `json`, `math`, `random`,
`fractions.Fraction`). SEED = 20260717, Z_GATE = 3.0, N_MC = 200000. All EXACT
work (G1/G2 and the theoretical E[D] values in G5/G6) uses `fractions.Fraction`;
the ONE `random.Random(SEED)` is consumed sequentially across the Monte-Carlo
gates in fixed order (G3 headline → G4 per grid tuple → G5 → G6).

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256: 7f00cea0bd40b2133ae9e91110c5112e8d5bf16bbcd90809a91911015215334f
```

- Reproduced digest: `7f00cea0bd40b2133ae9e91110c5112e8d5bf16bbcd90809a91911015215334f`
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
  byte-identical `results_sha256`
  (`7f00cea0bd40b2133ae9e91110c5112e8d5bf16bbcd90809a91911015215334f`). The only
  RNG is a `random.Random(SEED)` seeded from the fixed SEED — no wall-clock or OS
  randomness.

## 4. Gates — six, all PASS in their own directions, teeth confirmed

| Gate | Direction | Observed | Pass |
|------|-----------|----------|------|
| **G1** exact indifference | EQUALITY (Fraction) | headline (5,3,1,0): delta\*==**1/2** AND V_C−V_D==**0/1** exactly | ✅ |
| **G2** exact grid | EQUALITY (Fraction), 0<delta\*<1 | (5,3,1,0)→**1/2**, (5,4,1,0)→**1/4**, (5,2,1,0)→**3/4**, (9,8,1,0)→**1/8**; every gap==**0** | ✅ |
| **G3** MC agreement | AGREEMENT, \|z\| < 3 | 200 000 draws at delta\*=0.5, z=**1.404082** | ✅ |
| **G4** MC grid | AGREEMENT, every \|z\| < 3 | z = 1/2:**−1.150506**, 1/4:**0.654137**, 3/4:**0.630256**, 1/8:**−0.319587**; max\|z\|=**1.150506** | ✅ |
| **G5** falsify wrong formula | REJECTION, \|z\| > 6 | naive (T−R)/(T−S)=2/5=0.4, theory E[D]=**−2/3**, z_wrong=**−140.372466** | ✅ |
| **G6** falsify below-threshold | REJECTION, z < −6 | delta\*/2=0.25, theory E[D]=**−4/3**, z_below=**−448.661725** | ✅ |

`all_pass=true`, `first_failing_gate=null`, N_MC=**200000** (no bump required —
G3/G4 realizations all landed well within 3σ at this SEED).

**Teeth read per gate (each in its own direction):**
- **G1** is an exact rational equality: the threshold delta\*=(T−R)/(T−P) evaluates
  to Fraction(1,2) and the indifference gap V_C(delta\*)−V_D(delta\*) is EXACTLY
  Fraction(0). No float appears — a wrong threshold or wrong value equation would
  produce a non-zero Fraction and fail. Direction correct.
- **G2** re-runs the exact identity across four distinct payoff grids (delta\* ∈
  {1/2, 1/4, 3/4, 1/8}), each with 0 < delta\* < 1 and gap==0 — rules out a
  headline-only coincidence. Exact teeth.
- **G3** is a genuine independent stochastic estimate: 200 000 geometric-horizon
  episodes of D_i at the true threshold, where the null E[D]=0 is the firsthand
  claim; the pass is agreement within 3σ (z=1.404082). A broken horizon sampler
  or a wrong threshold would shift the mean off zero and diverge.
- **G4** repeats the AGREEMENT test at each grid tuple's own delta\* — the largest
  |z| over four tuples is 1.150506, all under 3σ. Independent of G3's headline
  draw (the shared RNG continues), so this is fresh evidence at three additional
  thresholds.
- **G5** constructs a concrete WRONG model — the plausible confusion of Sucker S
  for Punishment P, delta_wrong=(T−R)/(T−S)=2/5 — whose exact theoretical mean is
  −2/3 ≠ 0, and rejects it at z=−140.4 (|z|≫6), opposite polarity to G3/G4. This
  confirms G3/G4 are not trivially passable.
- **G6** rejects the "cooperation holds for all delta>0" claim by sampling below
  the threshold (delta\*/2=0.25), where the deviation is strictly profitable and
  the exact theoretical mean is −4/3 < 0; the one-sided z=−448.7 is far below −6.

## 5. Grounding

The result is a standard textbook folk-theorem / grim-trigger threshold
(one-shot-deviation principle; Friedman 1971; Mailath–Samuelson, *Repeated Games
and Reputations*). The verifier proves it FIRSTHAND two independent ways: (a) an
exact Fraction indifference identity yielding delta\*=(T−R)/(T−P) with a zero
incentive gap across four payoff grids, and (b) a continuation-probability
Monte-Carlo whose per-episode statistic D_i has mean exactly zero at delta\* and
strictly negative below it or under the wrong-Sucker formula. The firsthand
artifacts (the exact identity, the geometric-horizon sampler, SEED, the gate
grids, and the digest) are off-page by construction; the threshold formula itself
is the cited framework.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256
full-64 EXACT match (bit-exact, no truncation); determinism holds on both the
in-process double-run and the separate cross-invocation legs; all six pre-
registered gates PASS each in its own direction — two exact Fraction identities
(G1 headline, G2 four-grid) with a zero incentive gap, two Monte-Carlo AGREEMENT
gates within 3σ (G3 z=1.40, G4 max|z|=1.15), and two FALSIFIABILITY gates that
reject the wrong-Sucker formula (−2/3, z=−140.4) and the below-threshold claim
(−4/3, z=−448.7) at the opposite polarity. No qualification required.

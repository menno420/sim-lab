# VERDICT 230 — Probe report (reproduces PROPOSAL 217)

> On a consistent-hashing ring with n keys placed by an ideal uniform hash, the
> expected largest arc ("max gap") owned by any single node is exactly H_n/n
> (the n-th harmonic number over n), and by inclusion–exclusion the expected arc
> equals A(n) = Σ_k (−1)^(k+1) C(n,k) / (k·n) == H_n/n. The busiest node does NOT
> own a plain 1/n fraction — it owns ~ (ln n)/n, a factor of H_n ≈ ln n larger.

- **Slice:** round-52, P217 → V230 (+13 offset)
- **Branch:** `claude/verdict-230-sim`
- **Sim dir:** `sims/verdict-230-consistent-hashing-max-gap/`
- **Source:** PROPOSAL 217 (idea-engine `ideas/fleet/consistent-hashing-max-gap-harmonic-2026-07-20.md`)
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of `idea-engine/ideas/fleet/consistent-hashing-max-gap-harmonic.py`
→ `sims/verdict-230-consistent-hashing-max-gap/consistent-hashing-max-gap-harmonic.py`;
`diff` source ↔ copy exit **0** (byte-identical). Stdlib-only. SEED = 20260717.

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256=41394b56e4ebec3d14eb340fbfbd896db530d794fcea2ca495212948f74184ac
```

- Disclosed target: `41394b56e4ebec3d14eb340fbfbd896db530d794fcea2ca495212948f74184ac`
- Independently compared against the disclosed digest, exact 64-char string
  compare → **MATCH** (printed digest is exactly 64 hex chars; no truncation,
  bit-exact).
- Digest posture: WHOLE-DICT / STDOUT-ONLY — the compact-canonical results
  dict's own sha256 IS the digest; the dict carries no self-field hash.

## 3. Determinism — both legs hold

- **In-process double-run:** the verifier builds the results dict twice and
  prints `determinism_double_run=True` (digest equality asserted before exit 0).
- **Cross-invocation:** a second separate process re-invocation produced
  byte-identical stdout. No wall-clock or OS randomness.

## 4. Gates — five, all PASS in their own directions

| Gate | Direction | Observed | Pass |
|------|-----------|----------|------|
| **G1** identity (exact, Fraction) | A(n) = Σ(−1)^(k+1)C(n,k)/(k·n) == H_n/n exactly, n=2..12 | all n equal=true, n·A/H_n == 1/1; e.g. A(4)=**25/48**=H_4/4, A(8)=**761/2240**=H_8/8 | ✅ |
| **G2** enumeration, monotone convergence | n=4, target 25/48≈0.520833; abs_err strictly decreasing in m | m=8 **0.07797619** > m=12 **0.049621212** > m=16 **0.036217949** > m=20 **0.028521672** | ✅ |
| **G3** two-sided Monte-Carlo | small `|z|` is the pass (agreement, not extremity) | z(n=32)=**−1.258124**, z(n=64)=**−0.45513**, both `|z|`<3 | ✅ |
| **G4** shift-invariance | n·A/H_n == 1 exact all n; shifted-ring MC within 3σ | exact_ratio_one_all_n=true; L=**7.0** → z(32)=**0.933517**, z(64)=**−0.166919** within 3σ | ✅ |
| **G5** falsifiability | wrong models must be REJECTED | naive "busiest owns 1/n" REJECTED at z(n=32)=**1322.80024** (large z = correct falsification); broken alternating-sign accounting ≠ H_n/n, REJECTED | ✅ |

All five gates PASS in their pre-registered directions. G1 is an exact
`Fraction` identity (no float slack). G2's strict monotone decrease of the
enumeration error toward 25/48 is load-bearing convergence evidence. G3/G4 use
the two-sided convention where *small* z is the pass — the estimator agreeing
with H_n/n, not deviating from it. G5 is the falsifiability leg: the deliberately
wrong "1/n" model is rejected with a huge z (1322.80), and the sign-dropped
inclusion–exclusion accounting no longer equals H_n/n — both correctly rejected.
The verifier's own `sim_ready=true` and `both_wrong_models_rejected=true` agree.

## 5. Grounding — byte-pinned, sha1 match; HONEST caveat

- Source: Wikipedia "Consistent hashing", oldid **1362790808**, `action=raw`
  wikitext.
- Raw-wikitext sha1 = `04e4621d7d3ec6c945d65c66c583dde9eda80cef` = disclosed
  pinned sha1 → **MATCH**.
- **On-page** (confirmed present): virtual-nodes / variance-reduction discussion,
  and the "1/n fraction of BLOBs relocate" statement.
- **Off-page** (correctly absent, and the proposal says so): the E[max arc] =
  H_n/n identity is NOT on the page, and the H_n ≈ ln n factor is NOT on the
  page — every "log" on the page refers only to the O(log N) lookup cost, not to
  the max-gap magnitude.

### Grounding-accuracy assessment (per the V222 grounding-scrutiny lesson)

The proposal's caveat is **honest** — neither oversold nor undersold. It does
not oversell: it explicitly does NOT claim Wikipedia states the H_n/n max-gap
identity, and correctly notes the page's only motivation is the virtual-node /
variance-reduction and "1/n relocate" material. It does not undersell: it
acknowledges that motivation is genuinely on-page. The caveat cleanly separates
the **firsthand-proven** result (the H_n/n identity, proven here by exact
Fraction identity + enumeration + MC) from the **Wikipedia motivation** (why
consistent hashing cares about load balance at all). No mis-description of the
source, so no qualification is forced.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256
full-64 EXACT match (bit-exact); determinism holds on both the in-process
double-run and the separate cross-invocation legs; all five pre-registered gates
(G1 exact identity, G2 monotone enumeration convergence, G3 two-sided MC, G4
shift-invariance, G5 falsifiability) PASS in their own directions with the wrong
models correctly rejected; grounding sha1 matches the pinned revision with the
on-page motivation present and the off-page identity honestly disclosed as
firsthand-proven rather than cited. No qualification required.

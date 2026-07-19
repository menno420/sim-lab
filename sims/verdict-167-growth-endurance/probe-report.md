# VERDICT 167 — growth-endurance dominance: independent reproduction probe report

Reproduction of PROPOSAL 154 (round-36 VENTURE slot, P154 → V167, +13). All
numbers below are from THIS clean-room reproduction: the verifier was copied
byte-identical from the idea-engine source, run twice as separate processes,
and the digest recomputed over the script's own compact-canonical stdout
payload. Every claim cites the run-stdout numbers.

## Reproduction inputs (identity)

- **Source verifier:** idea-engine `ideas/venture-lab/growth_endurance_dominance.py`
  at idea-engine commit `5b511a295b2eb6427520329aac14c84baf607c3a`.
- **Copied to:** `sims/verdict-167-growth-endurance/growth_endurance_dominance.py`.
- **File sha256:** `b46479d49f74b8d5f1868e01e6b1fcdef0394cf67026bccd005e0f3e370d6ac8`
- **git blob (copy):** `e3b7da5b071f19127b003e4df365bc070e83d3ae`
- **git blob (idea-engine source):** `e3b7da5b071f19127b003e4df365bc070e83d3ae` (identical)
- **byte count:** 5019 · **line count:** 146
- **Byte-identity `diff` exit code:** `0` (copy is byte-identical to source).

## Pinned world (from source)

SEED=20260717, N=1500, TRIALS=300, HORIZON=12, DELTA=0.05, REL_NULL=0.10,
paired GROWTH-vs-ENDURANCE contrast on the SAME per-company draw, one
`random.Random(SEED)` stream drawn in fixed order.

## run-stdout.txt (verbatim, 3 lines)

```
{"G1_dominance_sign":{"frac_dominant":0.992229,"gap_mean":0.354025,"z":996.770037},"G2_relative_effect":{"null":0.1,"rel_mean":2.219712,"z":925.51319},"G3_shifted_robustness":{"frac_dominant":0.997938,"gap_mean":0.322362,"z":1107.766114},"all_pass":true,"config":{"DELTA":0.05,"HORIZON":12,"N":1500,"REL_NULL":0.1,"SEED":20260717,"TRIALS":300},"first_failing_gate":null,"mechanism":"growth-endurance-dominance","proposal":154}
sha256:5dccb475a6fde0ebd5c557b3baa393be8430b91902bbadedb7f5bd16754495bf
all_pass:True
```

---

## Probe 1 — Does the results-dict sha256 reproduce the disclosed digest EXACTLY (compact-canonical, cross-invocation + in-process assert)?

**YES — exact match.**

- **Reproduced digest:** `5dccb475a6fde0ebd5c557b3baa393be8430b91902bbadedb7f5bd16754495bf`
- **Disclosed digest:** `5dccb475a6fde0ebd5c557b3baa393be8430b91902bbadedb7f5bd16754495bf`
- Character-for-character equal.

The digest is computed by the script itself over the COMPACT-canonical
serialization (`json.dumps(..., sort_keys=True, separators=(",",":"))`) of the
whole results dict — the P127+ STDOUT-ONLY twist, distinct from any pretty
indent=2 dump. Determinism confirmed three ways:

- **Fresh cross-invocation double-run:** two separate `python3` processes
  (`run1.txt`, `run2.txt`), `diff run1.txt run2.txt` → exit `0` (byte-identical
  stdout across invocations).
- **In-process double-run assert:** the script computes a second independent
  build and asserts `digest == digest2`; both invocations exited `0` — the
  assertion did NOT fire.
- **No JSON written to disk** by the script; the compact payload is the digest
  preimage.

## Probe 2 — Is the verifier byte-identical to the P154 source (diff exit 0, sha256 / git blob / byte / line identity)?

**YES.**

- `diff SOURCE COPY` exit code: `0`.
- File sha256: `b46479d49f74b8d5f1868e01e6b1fcdef0394cf67026bccd005e0f3e370d6ac8`.
- git blob of copy `e3b7da5b071f19127b003e4df365bc070e83d3ae` equals git blob of
  the idea-engine source `e3b7da5b071f19127b003e4df365bc070e83d3ae` — Git's own
  content-hash confirms byte-identity independently of `diff`.
- byte count 5019 · line count 146.
- Source pinned at idea-engine commit
  `5b511a295b2eb6427520329aac14c84baf607c3a`, path
  `ideas/venture-lab/growth_endurance_dominance.py`.

## Probe 3 — Do all three gates PASS in order G1 → G2 → G3 with the disclosed statistics, all_pass=true, first_failing_gate=null, exit 0?

**YES — all three PASS in order; all_pass=true; first_failing_gate=null; exit 0.**

Pass rule: G1 z≥3 and gap_mean>0; G2 z≥3 and rel_mean≥0.10; G3 z≥3 and
gap_mean>0. z_gate = 3.0, one-sided.

| Gate | Reproduced numbers | Rule check | Result |
|------|--------------------|------------|--------|
| **G1 dominance-sign** | gap_mean=+0.354025, z=+996.770037, frac_dominant=0.992229 | z 996.77 ≥ 3 ✓ AND gap_mean 0.354025 > 0 ✓ | **PASS** |
| **G2 relative-effect** | rel_mean=+2.219712, z=+925.513190 (null=0.10) | z 925.51 ≥ 3 ✓ AND rel_mean 2.219712 ≥ 0.10 ✓ | **PASS** |
| **G3 shifted-robustness** | gap_mean=+0.322362, z=+1107.766114, frac_dominant=0.997938 | z 1107.77 ≥ 3 ✓ AND gap_mean 0.322362 > 0 ✓ | **PASS** |

Every reproduced statistic equals the disclosed value to the printed 6 dp.
`all_pass:True`, `first_failing_gate:null`, both process exits `0`.

## Probe 4 — Is the headline read correctly (growth dominates for growth-stage g0 > 1−r), NOT as "durability is always the safe default"?

**Read correctly as a GROWTH-STAGE dominance claim, not a universal one.**

Over HORIZON=12 the compounding GROWTH strategy (multiplicative at g0) beats the
ENDURANCE strategy (additive durability bought by raising retention r) on
terminal enterprise value for companies ABOVE the crossover g0 > 1−r. The
contrast is attributable to the STRATEGY alone because both strategies are
evaluated on the SAME per-company draw per trial (paired; one
`random.Random(SEED)` stream) — source `trial()` draws `g0, r` once and computes
both `sens_r` and `sens_g` from that shared draw (lines 68–74). Growth dominates
on ~99.2% of paired draws (G1 frac_dominant=0.992229); the remaining ~0.78% are
the low-growth crossover companies where endurance wins. The folk "durability is
the safe default" belief is the growth-stage inversion the head targets — and it
holds only above the crossover, not universally.

## Probe 5 — Is the model-basis caveat correctly weighed as CONSERVATIVE-DIRECTION / DISCLOSED-DESCRIPTIVE (clean APPROVE, not a defect)?

**Yes — disclosed-descriptive, conservative-direction; a clean APPROVE is warranted.**

The low-growth crossover band (companies below g0 > 1−r, where endurance wins —
the ~0.78% of the primary sample not dominated, frac_dominant=0.992229) is
DISCLOSED in the verifier source itself: docstring lines 9–10 state "Dominance
holds for growth-stage companies (g0 > 1−r); it crosses over for low-growth
companies -- disclosed." The declared choices — fixed HORIZON=12, DELTA=0.05
budget increment, paired same-company draw — none flips a gate SIGN or the
order-of-magnitude of the growth-stage dominance: all three gates pass at
z ≈ 926–1108σ with the correct positive sign. The caveat narrows scope; it does
not weaken any gate. No gate reads the low-growth regime as universal.

## Probe 6 — Could the sign be a seed fluke?

**No.** The paired-draw contrast clears G1 at z=+996.770037σ with
frac_dominant=0.992229 at the primary distribution; G2 at z=+925.513190σ vs the
0.10 REL_NULL; and the sign survives the shifted-distribution re-draw (G3
z=+1107.766114σ, frac_dominant=0.997938 — `draw_shift` lowers endurance and
raises headline growth, the case where reversal is most plausible). Effect sizes
this many sigma above the gate, surviving an adversarial re-draw of the company
distribution, and reproduced byte-identically across a fresh cross-invocation
double-run and the in-process digest assert, are not a seed fluke.

## Crossover honesty check (grounded in code)

The crossover IS disclosed in the verifier source: docstring lines 9–10 —
"Dominance holds for growth-stage companies (g0 > 1−r); it crosses over for
low-growth companies -- disclosed." The draw distributions make the crossover
reachable: `draw_base` (lines 44–47) samples g0 ~ lognormal(log 0.60, 0.40)
clamped to [0.15, 2.00] and r ~ normal(0.78, 0.06) clamped to [0.55, 0.93], so
1−r spans roughly [0.07, 0.45]. When a draw lands with low g0 (near the 0.15
floor) and low r (near 0.55, i.e. 1−r near 0.45), the company falls below the
crossover g0 < 1−r; there `sens_r > sens_g` fails and the company is not counted
dominant (source `trial()` increments `dom` only when `sens_r > sens_g`, lines
73–74). frac_dominant = 0.992229 < 1.0 is therefore fully consistent with — and
is the direct measurement of — the disclosed low-growth crossover: ~0.78% of the
1500 paired draws fall into the low-growth band where endurance wins. A
frac_dominant of exactly 1.0 would instead contradict the disclosed crossover.
The sub-unity fraction is the mechanism honestly reporting its own boundary, not
a defect.

# VERDICT 214 — Graham's multiprocessing timing anomaly: greedy list scheduling is non-monotone yet ≤ (2−1/m)·OPT — reproduce PROPOSAL 201

- **Slice:** VERDICT 214 · PROPOSAL 201 (P201 → V214, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 201 · 2026-07-20T06:44:16Z — Graham's multiprocessing timing anomaly: greedy non-preemptive LIST SCHEDULING of precedence-constrained jobs on `m` identical machines is NON-monotone — relaxing an input (adding a machine, shortening every job, or deleting a precedence edge) can each STRICTLY INCREASE the makespan, yet the greedy makespan is provably ≤ (2−1/m)·OPT (`ideas/fleet/graham-scheduling-anomaly-2026-07-20.md`)
- **Verifier (source):** idea-engine `ideas/fleet/graham_scheduling_anomaly.py` (git blob `1582301497d7cba387d7ef66388d16232375ca07`, sha256 `5091d785a043ff0d2c1280972e154febee7c39cedbf02e0a96865cc428b3e8f8`)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-214-graham-anomaly, branch `claude/verdict-214` (built off origin/main `75aab02`)
- **Timestamp (date -u):** 2026-07-20T07:14Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`)

## Head

Greedy non-preemptive **list scheduling** places precedence-constrained jobs on `m`
identical machines: whenever a machine is idle it starts the next ready job in a fixed
priority list. The claim: this scheduler is **non-monotone** — *relaxing* an input can
make the makespan *worse*. Three independent relaxations each demonstrate it: adding a
machine (`m → m+1`), shortening every job by 1, or deleting a precedence edge can each
STRICTLY INCREASE the makespan. Yet the greedy makespan is provably bounded:
`list ≤ (2 − 1/m)·OPT` (Graham 1969). The verifier certifies the (2−1/m) bound EXACTLY
in `fractions.Fraction` against a brute-force optimal makespan over 20000 small
instances, and demonstrates each of the three anomalies as a statistically significant
Monte-Carlo effect with a concrete integer witness for the add-a-machine case.

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` →
  **exit 0**. sha256 identical on both sides:
  `5091d785a043ff0d2c1280972e154febee7c39cedbf02e0a96865cc428b3e8f8`; sim-lab git blob
  `1582301497d7cba387d7ef66388d16232375ca07`.
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process
  **exit 0** (`all_pass = true`).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`; whole-dict, no self-field, stdout-only):**
  - disclosed (PROPOSAL 201): `2f81534216b6d8dee3d99446a0e451bde7cd64019d5f10b7de59a01921129eef`
  - reproduced (this run):    `2f81534216b6d8dee3d99446a0e451bde7cd64019d5f10b7de59a01921129eef`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality,
    hex-char count = 1 unique 64-hex token, no truncation). The verifier PRINTS this
    digest (`sha256 = …`); the printed `canonical_json` line reproduces the compact
    dict whose own sha256 is the digest.

## Determinism

- **Separate cross-invocation** — two independent `python3` invocations produced
  byte-identical stdout (`diff run-stdout.txt run-stdout-2.txt` → **exit 0**; both
  files sha256 `9b2817c182b7f4a10ea40d23a1ae40da45649a255073e807945e31ec77c11c69`),
  hence the identical results-dict digest
  `2f81534216b6d8dee3d99446a0e451bde7cd64019d5f10b7de59a01921129eef` both times.
- The verifier constructs a fresh `random.Random(SEED)` for each Monte-Carlo gate, so
  the stochastic streams are pinned; the digest is a `DETERMINISM DIGEST` printed as
  the whole-dict sha256 with no self-field.

## Gate evaluation (against PROPOSAL 201's OWN criteria, in order)

Each gate is read in ITS OWN direction. G1 and G2 are **SIGNAL** gates (a HIGH z is the
PASS — the anomaly is a real effect, not sampling noise); G3 is an **EXACT-BOUND** gate
(zero violations is the PASS, corroborated by a non-trivial count so the bound is not
vacuous).

- **G1 — SURPRISE: remove-one-edge (DIRECTION: HIGH z; want z1 ≥ 10):** over
  `N1 = 60000` eligible DAGs, deleting one precedence edge made the list-schedule
  makespan STRICTLY LARGER in `count = 5470` cases (`p̂ = 0.09116667`,
  `SE = 0.0011751263`), giving `z1 = 77.580315 ≥ 10`. **PASS.**
  - observed vs disclosed: count 5470/60000 vs 5470/60000 ✓ · z 77.580315 vs 77.58 ✓
- **G2 — ROBUSTNESS: two independent relaxations (DIRECTION: HIGH z each; want z ≥ 3),
  `N2 = 500000`:**
  - (i) ADD-A-MACHINE `list(m+1) > list(m)`: `count = 72`, `p̂ = 0.00014400`,
    `SE = 0.0000169693`, `z = 8.485892 ≥ 3`. **PASS.** (disclosed z 8.49 ✓)
  - (ii) SHORTEN-ALL `list(t−1) > list(t)`: `count = 85`, `p̂ = 0.00017000`,
    `SE = 0.0000184375`, `z = 9.220328 ≥ 3`. **PASS.** (disclosed z 9.22 ✓)
- **G3 — EXACTLY-TRUE: `list/opt ≤ (2m−1)/m = 2 − 1/m` (Fraction-exact; violations MUST
  be 0):** over `K = 20000` small instances, `violations = 0`, `max ratio observed =
  11/7 = 1.571429`, `instances with ratio > 1 (bound non-trivial) = 8122 > 0`.
  **PASS** (0 violations AND non-trivial > 0). Max-ratio witness `m=3, list=11, opt=7`.
  - observed vs disclosed: 0 violations / max ratio 11/7≈1.571429 / 8122 non-trivial vs
    0 violations / 11/7 / (non-trivial disclosed as present) ✓

`all_pass = true`.

## Add-a-machine witness (the 27 → 28 non-monotone instance)

The G2 stream's first add-a-machine anomaly (printed verbatim):

```
times = {0: 1, 1: 2, 2: 4, 3: 9, 4: 4, 5: 7, 6: 7, 7: 9, 8: 3, 9: 7}
prec  = {0: [], 1: [], 2: [0], 3: [1], 4: [0], 5: [0, 4], 6: [1, 2, 4], 7: [3, 4], 8: [], 9: [7]}
order = [4, 2, 6, 7, 1, 5, 8, 9, 3, 0]
makespan on m   = 2: 27
makespan on m+1 = 3: 28   <-- STRICTLY LARGER
```

Adding a third machine to this fixed job set / priority list makes the greedy schedule
finish at **28** instead of **27** — a concrete integer counterexample to the folk
intuition that more machines never hurt. Matches the disclosed `m=2 makespan 27 → m=3
makespan 28` witness exactly.

## Grounding

- **Source:** Wikipedia "List scheduling" oldid **1291511174**
  (`index.php?oldid=1291511174`, MediaWiki API `prop=revisions&rvprop=sha1|ids|timestamp`).
- **Fetch:** revision **RESOLVES** — title "List scheduling", revid 1291511174,
  timestamp 2025-05-21T18:02:13Z. Revision **sha1 `e2de39981e1fdc4d2daf8d7411f1f3dc0f32aaa2`**
  (starts `e2de3998`, as disclosed), returned by the MediaWiki API `rvprop=sha1`.
- **Content:** the article states the approximation bound "the makespan is at most
  2 − 1/m times the optimal makespan" and presents ALL THREE anomalies firsthand —
  *Anomaly 1* removing dependencies enlarges the makespan, *Anomaly 2* shortening all
  jobs enlarges the makespan, *Anomaly 3* adding a machine enlarges the makespan — with
  the (2−1/m) bound and the anomalies attributed to **Graham 1969**. This is exactly the
  mechanism the verifier reproduces (G1 remove-edge, G2 add-machine + shorten-all, G3
  the (2−1/m) bound).
- **Disclosed caveat (assessed FAIR):** the page does NOT use the literal inline phrase
  "Graham's anomaly". That is a naming caveat only — the page shows the SUBSTANCE and
  MECHANISM firsthand (the exact bound and all three anomalies, cited to Graham 1969),
  which is what the head asserts. The caveat is **fairly disclosed** and **non-fatal**:
  grounding is judged on whether the mechanism is on-page, and it is.

## Ruling evidence summary

Digest matches full-64 exact
(`2f81534216b6d8dee3d99446a0e451bde7cd64019d5f10b7de59a01921129eef`, printed
`sha256 =` line, single unique 64-hex token, no truncation); verifier byte-identical
(`diff` exit 0, git blob `1582301497d7cba387d7ef66388d16232375ca07`, sha256
`5091d785…`); deterministic (two cross-invocation runs byte-identical, stdout sha256
`9b2817c1…`, `diff` exit 0). All gates hold in their stated directions: **G1** remove-edge
SIGNAL `z1 = 77.580315 ≥ 10` (5470/60000), **G2** two SIGNAL relaxations add-machine
`z = 8.485892 ≥ 3` (72/500000) and shorten-all `z = 9.220328 ≥ 3` (85/500000), **G3**
EXACT (2−1/m) bound `0` violations over 20000 instances with max ratio `11/7 ≈ 1.571429`
and 8122 non-trivial instances. The add-a-machine witness confirms the non-monotone
head concretely: `m=2` makespan **27** → `m=3` makespan **28**. Grounding resolves
(Wikipedia "List scheduling" oldid 1291511174, sha1 `e2de3998…`) and states both the
(2−1/m) bound and all three anomalies, cited to Graham 1969; the missing literal phrase
"Graham's anomaly" is a fairly-disclosed naming caveat, non-fatal because the mechanism
is firsthand on-page. Reproduces the disclosed digest byte-for-byte, all gates hold in
direction, witness confirmed, external grounding supports the head → **APPROVE**.

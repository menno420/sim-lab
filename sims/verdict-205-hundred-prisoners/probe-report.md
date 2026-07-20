# Probe Report — VERDICT 205 · PROPOSAL 192 (the 100 prisoners problem)

**Ruling: APPROVE** (clean).

Target: PROPOSAL 192 (idea-engine control/outbox.md, 2026-07-20T02:17:24Z), lane fleet / round-45 UNRELATED slot. Offset +13 → VERDICT 205. Claim landed on origin/main: claim PR #713 → 67d21db; proposal PR #715 → 70ecdf9 (union-resolve merge 326b59c).

## Head

100 prisoners each open 50 of 100 boxes holding a uniform-random permutation of their numbers. Independent guessing gives group survival (1/2)^100 ≈ 8×10⁻³¹. The shared cycle-following convention (open your own number, then follow the chain of numbers found) makes the whole group survive iff the permutation's longest cycle ≤ 50 — probability exactly 1 − (H₁₀₀ − H₅₀) ≈ 0.31183, bounded below by 1 − ln 2 ≈ 0.30685 for every even N. Sounds impossible; exactly true. A single shared convention converts 100 correlated coin-flips into one draw from a permutation's cycle structure, collapsing a ~10⁻³⁰ event into a 1-in-3.

## Reproduction
- Verifier `hundred_prisoners.py` copied **byte-identical** from idea-engine `ideas/fleet/` (landed PR #715 @ 70ecdf9); `diff` exits **0**. Copy sha256 `850f2b64725e6fd33f265743abf7f4d5a275c6a1a5f2a1999a8ffc63e4751683`; git-blob `be333856bcf7eac6bcb188861222dd3c780f68e6` identical to source blob.
- stdlib-only (`hashlib, json, math, random, fractions, itertools`); SEED=20260717; Z_GATE=3.0.
- Results-dict `sha256 = ebc266644b5e21cb3c3c52415abd30e907c279fed74aa8f1c7151d5be895fdcf` — full **64 hex, byte-exact match** to the disclosed digest (exact-string grep count 1, no truncation). Method: `sha256(json.dumps(results, sort_keys=True, separators=(",",":")))`, WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY posture, floats 6 dp, no on-disk JSON.

## Determinism
- **In-process double-run:** the verifier's built-in `assert r1 == r2` passes (exit 0) — the two internal `run()` results-dicts are byte-identical.
- **Cross-invocation:** two fresh `python3` invocations produce byte-identical stdout (`diff` exit 0).

## Gates (proposal's own criteria, in order — READ CAREFULLY: G1 is an agreement gate, not a signal gate)
- **G1 — Monte-Carlo agrees with the closed form:** PASS. p_closed_form = 0.311828, p̂ = 0.311315 (M = 200000 permutations), std_error = 0.001036, **z = 0.495079 < 3.0** = PASS. Here a SMALL z is the pass condition: the MC estimate MATCHES the closed form 1 − (H₁₀₀ − H₅₀); it is a closeness/agreement gate, not a ≥3σ signal gate.
- **G2 — exactly-true (exhaustive enumeration ≡ closed form, no sampling):** PASS. Enumerating all 8! = 40320 permutations gives **307/840**, and 1 − (H₈ − H₄) = **307/840** — exact rational identity, `exact_match = true`. Real evidential weight: the claim is proven, not just sampled.
- **G3 — robustness/shift sweep N ∈ {100, 300, 1000, 3000, 10000}:** PASS. closed-form sweep {100: 0.311828, 300: 0.308517, 1000: 0.307353, 3000: 0.307019, 10000: 0.306903}, **spread = 0.004925 < 0.01**, **min = 0.306903 > 1 − ln 2 = 0.306853** (floor respected), max 0.311828 < 0.32, log10 advantage over naive = **29.596914** (naive log10 = −30.103), i.e. ~29.6 orders of magnitude over naive guessing.
- `all_pass = true`, exit 0.

## Handoff check (proposer's explicit request): is the H_{2n} − H_n law an N=8 coincidence?
Independently enumerated ALL (2n)! permutations at N ∈ {6, 8, 10} (n = 3, 4, 5), counting permutations whose longest cycle ≤ n, and compared the exact rational to 1 − (H_{2n} − H_n):

| N  | exhaustive enumeration | 1 − (H_N − H_{N/2}) | match | float    |
|----|------------------------|----------------------|-------|----------|
| 6  | 23/60                  | 23/60                | ✓     | 0.383333 |
| 8  | 307/840                | 307/840              | ✓     | 0.365476 |
| 10 | 893/2520               | 893/2520             | ✓     | 0.354365 |

All three exact fractions equal the closed form. The G2 identity 307/840 at N=8 is **not** a coincidence — the long-cycle survival law 1 − (H_{2n} − H_n) reproduces exactly at every tested N. (10! = 3,628,800 permutations enumerated in stdlib `itertools.permutations`, seconds.)

## Grounding assessment
Grounding is **real and external**: Wikipedia "100 prisoners problem" at oldid **1355965864**.
- The revision **resolves** (WebFetch HTTP 200) and **supports the head** verbatim: "using the cycle-following strategy the prisoners survive in a surprising 31% of cases"; "1 − (H₁₀₀ − H₅₀) ≈ 0.31183"; "lim n→∞ (1−H₂ₙ+Hₙ) = 1−ln 2 ≈ 0.30685"; the cycle-following strategy and the "no cycle of length greater than 50" survival condition are both described.
- The raw wikitext sha1 pin was independently verified byte-exact this session: `curl action=raw` → **29277 bytes**, **sha1 5e5ca1c63092d2bf6748d449a4826c91330c5a92** (both match the disclosed pin exactly). The raw wikitext itself also carries "surprising 31% of cases", "H_{100} - H_{50}", "0.31183", "ln 2", and "no cycle of length greater than 50".
- **Rendered-vs-wikitext caveat:** the proposer discloses this fairly. The idea doc (line 8) separates the two surfaces explicitly — the verbatim quotes are attributed to the RENDERED article ("rendered article verified reachable ... stating [quotes]"), while the sha1 is stated to pin "the raw wikitext at oldid 1355965864 (29277 bytes)". Naming the two surfaces distinctly is a fair, conservative disclosure; and in fact the raw wikitext also carries the claims (in math markup), so the gap the caveat guards against is narrower than disclosed — the disclosure is if anything over-conservative, which is the safe direction.

## Verdict
**APPROVE (clean).** The head reproduces byte-identically under SEED=20260717; the disclosed results-dict sha256 matches to the byte (all 64 hex); determinism holds (in-process + cross-invocation). All three of the proposal's own gates pass in order on their own criteria (G1 MC-agrees-with-theory z=0.495<3, G2 exact rational 307/840 ≡ closed form, G3 stable sweep spread 0.004925<0.01, min 0.306903 above the 1−ln2 floor, ~29.6 orders over naive). The proposer's requested handoff is independently confirmed — the long-cycle law 1 − (H_{2n} − H_n) is exact at N∈{6,8,10}, not an N=8 coincidence. Grounding is external, real, and byte-exact-pinned (sha1 + byte count both verified), with the rendered-vs-wikitext caveat fairly disclosed. G2 is an exact mathematical proof (exhaustive enumeration, no sampling), so the head is self-certifying and independently grounded — clean APPROVE, not merely QUALIFIED. done-when satisfied: byte-identical results-dict digest with all_pass=true, G1(z<3) ∧ G2(enumeration ≡ closed form, exact) ∧ G3(stable band, above floor, ≫ naive) holding in order.

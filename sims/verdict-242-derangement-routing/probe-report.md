# Probe report — VERDICT 242 staging (PROPOSAL 229, derangement routing → 1/e)

Staging the SEED=20260717 stdlib verifier for PROPOSAL 229 so VERDICT 242 (+13 offset, round-54 FLEET slot) can rule on it. Claim: routing N agents to N tasks by a uniformly-random permutation leaves NO agent on its home task with probability p_N = D_N/N! = Σ_{k=0}^{N} (−1)^k/k! → 1/e ≈ 0.367879, and this is NOT the naive independence estimate (1−1/N)^N.

- **Verifier:** `verify_229_derangement_routing.py` (byte-identical copy of idea-engine `ideas/fleet/verify_229_derangement_routing.py`; diff exit 0).
- **Reproduction:** `run-stdout.txt` (`python3 verify_229_derangement_routing.py`, exit 0).
- **Digest posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical results dict's own sha256 IS the digest (`json.dumps(r, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of itself. `main()` builds the results twice in-process, asserts byte-identical canonical JSON, then prints `results_sha256:`. Disclosed full-64 = `1f68c3d1cb6003f6ede1bc1d47e18f27a996bea9fa716f759d38fc2c3832365a` (exact 64-char compare, no truncation).
- **Determinism (SEED=20260717):** in-process double-run IDENTICAL AND a separate cross-invocation byte-identical (stdout sha256 `7f0b6c26e3b5950e6459088045a19a2634f239e63ef1573bad78a8e00fefc16f`). A single `random.Random(SEED)` is consumed once, in the Monte-Carlo pass, which feeds both G2 and G4.

## Method

Stdlib-only (`json`, `hashlib`, `math`, `random`, `fractions.Fraction`). Subfactorials via the recurrence D_n=(n−1)(D_{n−1}+D_{n−2}); exact ratios and the alternating sum as `Fraction`; the MC pass draws T=2,000,000 seeded Fisher–Yates permutations of {0..6} and counts fixed-point-free ones. No floats in the exact gates.

## Gates (each read in ITS OWN direction — against the proposal's OWN criteria)

- **G1 — EXACT identity, two routes** (direction: any n where the two routes disagree ⇒ FAIL): for n = 1..12, p_n = Fraction(D_n, n!) from the subfactorial recurrence EQUALS the alternating sum Σ(−1)^k/k! exactly. All 12 equal (e.g. p_7 = 103/280 = 1854/5040 both ways). **PASS.**
- **G2 — Monte-Carlo agreement** (direction: |z| ≥ 3 ⇒ FAIL): N=7, T=2,000,000; phat = 734929/2000000 = 0.3674645; z = (phat − p_7)/√(p_7(1−p_7)/T) = **−1.151504**, |z| < 3. **PASS.**
- **G3 — invariants / robustness** (direction: any exact identity fails ⇒ FAIL): the second recurrence D_n = n·D_{n−1} + (−1)^n holds exactly for n = 1..15; 0 < p_n < 1 for n = 2..15; and p_n straddles 1/e with the correct alternating sign (p_even > 1/e > p_odd, n = 2..12) against high-order rational bounds lo < 1/e < hi. **PASS.**
- **G4 — FALSIFIABILITY** (direction: PASS iff the wrong model is REJECTED at |z_naive| > 8 AND the exact model is accepted): the naive independence model q_7 = (6/7)^7 = 0.339917 is rejected on the SAME MC sample at z_naive = **82.246356** (> 8), while the exact model is accepted (|z| = 1.15 < 3). **PASS.**

`all_pass = true`, `first_failing_gate = null`.

## Grounding (byte-pinned, quoted vs derived — honest scope)

External: English Wikipedia "Derangement" oldid 1364530247, raw-wikitext sha1 `ba6f5759199b761a56d50342132212bbc99ed505` (27,877 bytes; API revision sha1 and a self-computed sha1 of the `action=raw` wikitext agree exactly). **Quoted (literally on the pinned revision):** the closed form D_n = n!·Σ(−1)^i/i!, both recurrences D_n=(n−1)(D_{n−1}+D_{n−2}) and D_n=n·D_{n−1}+(−1)^n, the nearest-integer fact D_n=[n!/e], the value D_7=1,854, and the limit lim D_n/n! = e^{−1} ≈ 0.367879 stated explicitly as "the limit of the probability that a randomly selected permutation … is a derangement." **Derived firsthand (NOT on the page):** the fleet-routing framing, the p_7 = 1854/5040 ratio written as a probability, the naive independence alternative (1−1/N)^N and its rejection, and every Monte-Carlo z-value. The page even names the hat-check framing; the caveat neither over- nor under-sells — the core identity/limit is quoted, the routing framing, numerics, and falsifier are firsthand.

## ⟲ Previous-session review

Carry-forward from the round-54 stagings (V238–V241): GATE-POLARITY discipline — read each gate in its own direction. G1 here is an EXACT two-route Fraction identity (equality is the pass, and it is computed two independent ways, not restated), G2 is a two-sided AGREEMENT gate (small |z| passes), G3 is an exact INVARIANT gate (any mismatch fails), and G4 is a FALSIFIABILITY gate where the naive independence model must be REJECTED at large |z_naive| (82.2). Also carries the V235/V238 GROUNDING-accuracy discipline: the pinned "Derangement" revision states the closed form and the 1/e derangement-probability limit literally, so the caveat honestly attributes those as quoted while claiming only the routing framing, the specific numerics, and the falsifier as firsthand — avoiding the QUALIFIED over-/under-claim seam.

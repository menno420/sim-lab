# Probe report — VERDICT 244 staging (PROPOSAL 231, Shapley value of the airport cost-sharing game)

Staging the SEED=20260717 stdlib verifier for PROPOSAL 231 so VERDICT 244 (+13 offset, round-54 GAME slot) can rule on it. Claim: for the airport cost-sharing (cooperative COST) game with characteristic function v(S)=max_{i∈S} c_i, the Shapley VALUE — the fair split of the grand runway cost v(N)=max c_i — is the Littlechild–Owen segment-equal-sharing allocation φ_j = Σ_{k=1}^{j}(c_(k)−c_(k−1))/(n−k+1) over the ascending-sorted costs (c_(0)=0), equivalently the average marginal contribution max(0, c_i − max_{j before i} c_j) over uniformly random join-orders, and this is NOT the naive equal split v(N)/n.

- **Verifier:** `verify_shapley_airport.py` (byte-identical copy of idea-engine `ideas/superbot-games/verify_shapley_airport.py`; diff exit 0; sha256 `0a4389a1a571a9d6a8f86de95a2a338fb3bb656f184e66b6c9ffa35e3415f7f0`).
- **Reproduction:** `run-stdout.txt` (`python3 verify_shapley_airport.py`, exit 0).
- **Digest posture:** WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical results dict's own sha256 IS the digest (`json.dumps(r, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of itself. `main()` builds the results twice in-process, asserts byte-identical canonical JSON, then prints `results_sha256:`. Disclosed full-64 = `9cbd3c4ec0026187cd64a20bbb79167209f071adbd9a21ecade0787b55d0f4f2` (exact 64-char compare, no truncation).
- **Determinism (SEED=20260717):** in-process double-run IDENTICAL AND a separate cross-invocation byte-identical. A single `random.Random(SEED)` is consumed once, in the Monte-Carlo pass over random join-orders, which feeds both G2 and G4.

## Method

Stdlib-only (`json`, `hashlib`, `math`, `random`, `fractions.Fraction`, `itertools.permutations`). The characteristic function is v(S)=max_{i∈S} c_i; the closed form shares each sorted runway segment c_(k)−c_(k−1) equally among the n−k+1 planes that still need it; the exact reference is the average marginal contribution over ALL n! orderings via `itertools.permutations`. The MC pass draws 200,000 seeded random join-orders and records the top (max-cost) player's marginal contribution. No floats in the exact gates.

## Gates (each read in ITS OWN direction — against the proposal's OWN criteria)

- **G1 — EXACT closed form == n! average** (direction: any player where the two routes disagree ⇒ FAIL): for costs (1,2,4,8) (n=4) and (1,2,4,8,16) (n=5), the segment closed form EQUALS the exact average over all n! orderings as `fractions.Fraction`, for every player. Main φ = (1/4, 7/12, 19/12, 67/12) both ways. **PASS.**
- **G2 — Monte-Carlo agreement** (direction: |z| ≥ 3 ⇒ FAIL): top player rank 3 (cost 8), 200,000 seeded random join-orders; sampled mean marginal = 5.57834 vs exact 67/12 ≈ 5.5833333; z = **−1.311312**, |z| < 3. **PASS.**
- **G3 — invariance (exact)** (direction: any exact identity fails ⇒ FAIL): efficiency — Σφ = 8/1 equals the grand cost v(N)=8 exactly; symmetry — on costs (2,5,5,9) the two equal-cost players (indices 1,2) receive exactly equal value, sym pair 3/2 == 3/2. **PASS.**
- **G4 — FALSIFIABILITY** (direction: PASS iff the wrong model is REJECTED at |z| > 6 AND the exact model is accepted): the naive equal split v(N)/n = 8/4 = 2/1 is rejected on the SAME MC sample at z = **939.716932** (> 6), while the exact model is accepted (|z| = 1.31 < 3). **PASS.**

`all_gates_pass = true`.

## Grounding (byte-pinned, quoted vs derived — honest scope)

Two external byte-pinned revisions. **Primary — English Wikipedia "Shapley value" oldid 1364397219**, raw-wikitext sha1 `c557fc821d4fab14d90c3f7434e1120e6e9cf020` (29,964 bytes; API revision sha1 and a self-computed sha1 of the `action=raw` wikitext agree exactly). **Quoted:** the average-marginal-contribution definition φ_i(v)=(1/|N|!)·Σ_R[v(P_i^R∪{i})−v(P_i^R)] and efficiency Σ_i φ_i(v)=v(N). **Secondary — English Wikipedia "Airport problem" oldid 1312709389**, raw-wikitext sha1 `cc179b50972d2bf70492e5099ad242273874258a` (3,339 bytes; API sha1 = self-computed sha1 exact match). **Quoted:** the segment-equal-sharing rule ("Divide the incremental cost … equally among … all but the smallest type … Continue thus until finally the incremental cost of the largest type … divided equally among … the largest aircraft type") and the identity "the resulting set of landing charges is the Shapley value for an appropriately defined game," with the Littlechild–Owen (1973) attribution. **Derived firsthand (NOT on either page):** the specific Shapley vectors for the committed cost profiles (the airport page tabulates a different worked example, costs 8,11,13,18), the naive equal-split falsifier v(N)/n and its rejection, every Monte-Carlo z-value, and the results_sha256. The core Shapley definition, efficiency, and the airport segment-sharing closed form are quoted; the specific allocations, numerics, and falsifier are firsthand — the citation neither over- nor under-sells.

## Dedup

The cooperative Shapley VALUE of a COST game — distinct from the already-built Shapley–Shubik power index (a simple VOTING game): different characteristic function (max-cost v(S)=max c_i vs pivotal-swing winning-coalition), different object (a cost-allocation vector vs a per-voter power number). No prior airport / cooperative-cost Shapley card in the ledger.

## ⟲ Previous-session review

Carry-forward from the round-54 stagings: GATE-POLARITY discipline — read each gate in its own direction. G1 here is an EXACT two-route Fraction identity (the closed form vs the n! enumeration — computed two independent ways, not restated); G2 is a two-sided AGREEMENT gate (small |z| passes); G3 is an exact INVARIANT gate (any efficiency/symmetry mismatch fails); and G4 is a FALSIFIABILITY gate where the naive equal split must be REJECTED at large |z| (939.7). Also carries the GROUNDING-accuracy discipline: the pinned Shapley_value and Airport_problem revisions state the average-marginal-contribution definition, efficiency, and the segment-equal-sharing closed form literally, so the caveat honestly attributes those as quoted while claiming only the specific cost-profile allocations, the numerics, and the falsifier as firsthand — avoiding the QUALIFIED over-/under-claim seam.

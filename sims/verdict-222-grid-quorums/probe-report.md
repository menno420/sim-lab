# VERDICT 222 — Grid quorums √N intersection (Maekawa): on a k×k grid of N=k² sites, each site's quorum is its row∪column (exactly 2k−1 sites). Any two such quorums ALWAYS intersect even though each is only O(√N) of the N sites — the Maekawa mutual-exclusion property. STRUCTURE, not size, buys it: random subsets of the same size 2k−1 are disjoint at a positive rate, while grid quorums are never disjoint — reproduce PROPOSAL 209

- **Slice:** sim-lab VERDICT 222 (reproduce and rule on PROPOSAL 209; P209 → V222, +13 offset; lane superbot-games)
- **Source proposal:** PROPOSAL 209 — grid quorums √N intersection / Maekawa (idea-engine)
- **Verifier (source):** `ideas/fleet/grid_quorum_sqrt_intersection.py` (idea-engine) — copied byte-identical into this sim dir as `grid_quorum_sqrt_intersection.py`
- **Reproduced by:** copy the verifier byte-identical (diff exit 0), run it, capture stdout, recompute the results-dict sha256 and confirm full-64 match; two cross-invocation runs byte-identical
- **Timestamp (date -u):** 2026-07-20T11:33:01Z
- **SEED:** 20260717 · **params:** k_main=6 (N_main=36, quorum_size_main=11), k_shift={4..10}, t_mc=2000000

## 📊 Model: Opus family · high effort · verdict-reproduction

## Ruling: QUALIFIED APPROVE

Fully reproduced. The results-dict sha256 `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f`
matches the disclosed PROPOSAL 209 digest across all 64 hex characters — printed by the verifier AND
independently recomputed here by re-canonicalizing the printed results dict (0 divergence), and
byte-identical across two separate invocations. The verifier was copied byte-identical (diff exit 0). All
five gates PASS each read in its own direction; the G1 leg is a self-certifying EXACT-Fraction identity
(`intersection_fraction == Fraction(1)`, not a tuned tolerance), and the G3 surprise crux isolates
STRUCTURE (not size) as the cause of the guarantee. The head is honestly scoped to the k×k grid row∪col
(Maekawa) quorums and is externally grounded to a sha1-pinned Wikipedia revision that directly states the
quorum-intersection / √N properties. **The ruling is QUALIFIED — not plain APPROVE — because the
DISCLOSED grounding caveat mis-describes the source** (it claims the article "describes the OPTIMAL √N
family via finite projective planes," which is factually wrong: the revision contains no projective-plane
content and no concrete construction at all). The mis-description is CORRECTED below; the correction
actually FAVORS the citation, so the head remains soundly grounded. **Ruling: QUALIFIED APPROVE.**

## Head

Grid quorums √N intersection (Maekawa). On a k×k grid of N=k² sites, assign each site the quorum
consisting of every site in its row and its column — a set of exactly 2k−1 sites (the row's k sites, the
column's k sites, minus the shared corner counted once). Any two such quorums Rᵢ, Rⱼ ALWAYS intersect:
row(i) crosses col(j) and row(j) crosses col(i), so two rows and two columns on a grid necessarily meet
and Rᵢ∩Rⱼ ≠ ∅ — never empty — even though each quorum is only O(√N) of the N sites (2k−1 = 2√N−1). This
is exactly the quorum-intersection property that makes Maekawa's √N mutual-exclusion algorithm correct: a
site needs permission from only its ~2√N quorum members rather than a simple majority ⌊N/2⌋+1, yet any
two sites' quorums overlap, so at most one can hold the intersection at a time. The load-bearing claim is
that STRUCTURE, not size, buys the intersection: a random subset of the SAME size 2k−1 drawn from the N
sites is disjoint from another at a positive rate (the hypergeometric rate C(N−m,m)/C(N,m)), while the
grid quorums are disjoint at EXACTLY zero. The exact intersection law is decided in exact Fraction
arithmetic over all C(N,2) quorum pairs, so the always-intersect identity is a theorem, not a tolerance.

## Reproduction

- Verifier copied byte-identical: `diff ideas/fleet/grid_quorum_sqrt_intersection.py sims/verdict-222-grid-quorums/grid_quorum_sqrt_intersection.py` → **exit 0**.
- results-dict sha256 posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))`, exact Fractions serialized as "num/den" strings, floats rounded to fixed dp, no self-referential sha field).
- Disclosed digest:              `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f`
- Reproduced (printed by run):   `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f`
- Independently recomputed:      `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f` — recomputed OUTSIDE the verifier by parsing the printed results dict from `run-stdout.txt`, re-serializing compact-canonical (`sort_keys=True, separators=(",",":")`), and hashing sha256 → identical across all 64 hex chars.
- **FULL-64 EXACT MATCH** (printed == independently-recomputed == disclosed target). The printed token is 64 hex chars, no truncation.
- Cross-invocation: two separate process invocations produced byte-identical whole files including the digest line (`diff` exit 0), so both printed the same 64-char digest.
- Full reproduction stdout: `run-stdout.txt`.

## Determinism

- In-process double-run: the verifier recomputes in-process and reports `in_process_double_run = "IDENTICAL"`; the run exited 0, so the in-process guard held.
- Cross-invocation: two separate process invocations → byte-identical whole files including the digest line, `diff` **exit 0**.
- G5 gate: `{in_process_double_run: "IDENTICAL", pass: true}`.

## Gate evaluation (against PROPOSAL 209's OWN criteria, in order — each read in ITS direction)

- **G1 — grid ALWAYS intersects** (main grid k=6, N=36; direction: exact-equality, Fraction, `intersection_fraction == Fraction(1)`). Every one of the `num_pairs = 630` grid-quorum pairs (`num_grid_quorums = 36`, one per site, each of size 2k−1 = 11) shares ≥ 1 site: `intersection_fraction = "1"`. Independently reconfirmed from scratch: the minimum overlap over all 630 pairs is 2 (two rows and two columns cross at two sites), so no pair is even close to disjoint. **intersection_fraction == Fraction(1) → PASS.** (Self-certifying: an exact-1 Fraction over an exhaustive pair enumeration is a theorem, not a tuned tolerance.)
- **G2 — Monte-Carlo agrees with the closed form** (M=2e6; direction: low |z| = AGREEMENT / convergence). The Monte-Carlo random-subset disjoint rate `mc_disjoint_rate = 0.0074515` agrees with the exact hypergeometric closed form `closed_form_disjoint_prob = C(25,11)/C(36,11) = 10925/1472562 = 0.007419042458` (`se_closed = 6.0679487e-05`): `z = 0.5349 < threshold 3.0`. The closed form was computed FIRST (feasibility probe), so the threshold is what the math meets, not fitted after. **z = 0.5349 < 3.0 → PASS.** (CONVERGENCE/AGREEMENT gate: a SMALL |z| is the PASS direction — the Monte-Carlo control lands on the exact rate.)
- **G3 — the surprise crux: same-size RANDOM subsets genuinely fail to always intersect** (direction: HIGH z = SURPRISE, ≥ 3σ above zero — STRUCTURE, not size, buys the guarantee). Random same-size-11 subsets are disjoint at a POSITIVE rate `mc_disjoint_rate = 0.0074515` (`mc_disjoint_hits = 14903` out of 2e6; `se_hat = 6.0811081e-05`): `z = 122.5352 ≥ threshold 3.0` versus the zero a "size alone forces intersection" story would predict. Independently reconfirmed: the grid disjoint-rate is EXACTLY 0 (from G1) while an equal-SIZE random control is disjoint at 0.007419 > 0 — so it is the grid's row∪col STRUCTURE, not the quorum SIZE 2k−1, that buys the intersection guarantee. **z = 122.5352 ≥ 3 → PASS.** (EFFECT/SURPRISE gate: a LARGE z is the PASS direction — this is THE CRUX of the head.)
- **G4 — SHIFT / robustness across k∈{4..10}** (direction: exact-equality across k — grid always intersects AND quorum beats majority AND size-ratio strictly decreasing). For every k in {4,5,6,7,8,9,10}: `grid_intersection_fraction = "1"` (`all_grid_intersection_exact_1 = true`); the quorum size 2k−1 is strictly below the simple majority ⌊k²/2⌋+1 (`all_quorum_beats_majority = true`) — e.g. k=6: quorum 11 < majority 19; k=10: quorum 19 < majority 51; and the size ratio (2k−1)/k² is strictly DECREASING 7/16 → 9/25 → 11/36 → 13/49 → 15/64 → 17/81 → 19/100 (`size_ratio_strictly_decreasing = true`), so the √N savings scale up with N. **all three hold → PASS.** (Exact-across-k gate: the always-intersect identity, the sub-majority quorum, and the widening savings are all exact.)
- **G5 — determinism** (direction: byte-identical). In-process double-run `IDENTICAL` AND two separate-invocation processes diff **exit 0**. **PASS.**

Overall: gates {G1:true, G2:true, G3:true, G4:true, G5:true}, `all_gates_pass: true`, no first-failing gate.

## Grounding

- External, sha1-pinned: Wikipedia "Maekawa's algorithm", oldid **1306919367** (revision timestamp 2025-08-20T12:53:12Z), raw-wikitext sha1 `894805bdbac0adce66d1e794c45925fa9b280e89`. **3-way match:** disclosed token == API-stored revision sha1 == independently computed sha1 — all three identical.
- Firsthand support for the CORE: the article DIRECTLY supports the head. It states the quorum-intersection property (Rᵢ ∩ Rⱼ ≠ ∅ for all i, j), the size bound |Rᵢ| ≥ √(N−1), the 3√N–6√N message complexity, and cites Maekawa's 1985 √N paper. This carries the head's intersection / O(√N) legs directly.
- **CAVEAT CORRECTION (the qualifier — the reason this ruling is QUALIFIED rather than plain APPROVE):** the DISCLOSED grounding caveat claims the article "describes the OPTIMAL √N family via finite projective planes." **This is FACTUALLY WRONG.** The pinned revision contains NO mention of projective planes and NO concrete construction at all — grep of the revision for `projective` / `plane` / `grid` / `finite` / `optimal` returns ZERO hits. The article states only the ABSTRACT quorum axioms (the intersection property and the √N size/message bounds), not any specific construction. **Net effect FAVORS the citation:** precisely because the article states the intersection/√N properties abstractly (as axioms any valid quorum family must satisfy), the plain 2k−1 grid row∪col quorums the verifier enumerates are a fully valid CONCRETE member of that abstract family — the head does not depend on the projective-plane construction the caveat wrongly attributes to the source. So the head is soundly grounded on the abstract intersection/√N axioms; the qualification is only that the disclosed grounding caveat mis-describes the source, and it is corrected here.

## Novelty

Distinct from every prior head. Search across `ideas/**` for Maekawa / quorum / grid-quorum / mutual-exclusion / √N-intersection returns nothing prior as a built head. Adjacent but distinct: majority/voting heads (this is a SUB-majority O(√N) quorum, not a majority set) and set-cover / intersecting-family heads (this pins the specific row∪col grid design and its structure-vs-size separation). No prior head computes the grid quorum-intersection law or the hypergeometric same-size disjoint-rate control.

## Ruling evidence summary

VERDICT 222 reproduces PROPOSAL 209 bit-exact: the verifier copied byte-identical (diff exit 0), the results-dict sha256 `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f` matches the disclosed digest across all 64 hex characters — printed AND independently recomputed outside the verifier (0 divergence), byte-identical across two separate invocations — and determinism holds (in-process double-run IDENTICAL AND two cross-invocation processes byte-identical, diff exit 0). All five pre-registered gates PASS each read in its own direction: G1's EXACT-Fraction always-intersect law (`intersection_fraction = "1"` over all 630 pairs at k=6, min overlap 2; self-certifying), G2's LOW-z agreement (mc_disjoint_rate 0.0074515 vs closed form 10925/1472562 = 0.007419042458, z=0.5349<3), G3's HIGH-z SURPRISE crux (random same-size-11 subsets disjoint at 0.0074515 = 14903/2e6 while grid disjoint-rate is EXACTLY 0, z=122.5352 — STRUCTURE not SIZE buys the intersection), G4's SHIFT sweep (k∈{4..10}: grid fraction=1 ∀k, quorum 2k−1 < majority ⌊k²/2⌋+1 ∀k, ratio (2k−1)/k² strictly decreasing 7/16→19/100), and G5's determinism. The head is externally grounded to a sha1-pinned Wikipedia revision (oldid 1306919367, wikitext sha1 `894805bdbac0adce66d1e794c45925fa9b280e89`, 3-way match) whose abstract intersection/√N axioms (Rᵢ∩Rⱼ≠∅, |Rᵢ|≥√(N−1), 3√N–6√N messages, cites Maekawa 1985) firsthand-support the head. The ruling is QUALIFIED because the DISCLOSED grounding caveat mis-describes the source — it claims the article "describes the OPTIMAL √N family via finite projective planes," but the revision has no projective-plane / concrete-construction content at all (grep → zero hits); the correction actually FAVORS the citation, since the abstract axioms make the plain 2k−1 grid a valid concrete member, so the head stays soundly grounded. The head is genuinely distinct from prior shipped heads. **Ruling: QUALIFIED APPROVE.**

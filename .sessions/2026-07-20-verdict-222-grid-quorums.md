# VERDICT 222 — Grid quorums √N intersection: on a k×k grid, assign each site the quorum row∪col (2k−1 sites). Any two such quorums ALWAYS intersect (share ≥ the row/col crossing sites) even though each is only O(√N) of the N=k² sites — the Maekawa mutual-exclusion property. STRUCTURE, not size, buys the intersection: random subsets of the same size 2k−1 are disjoint at a positive rate, while grid quorums are never disjoint. Reproduce PROPOSAL 209

> **Status:** complete

📊 Model: Opus family · high effort · verdict-reproduction

started: 2026-07-20T11:29:38Z

💓 Heartbeat: round-slot SUPERBOT-GAMES P209 → V222 (+13) reproduction on branch
`claude/verdict-222`; sim dir `sims/verdict-222-grid-quorums/` (byte-identical verifier copy +
reproduction stdout + probe-report), digest target full-64
`bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f` (printed AND independently
reproduced byte-identical, MATCH), five gates each in its own direction (G1 EXACT grid always intersects
intersection_fraction=Fraction(1) over all 630 pairs at k=6, min overlap=2; G2 LOW-z agreement
mc_disjoint_rate=0.0074515 vs closed form C(25,11)/C(36,11)=10925/1472562=0.007419042458 z=0.5349;
G3 HIGH-z surprise crux random same-size-11 subsets disjoint at 0.0074515 vs grid EXACTLY 0
z=122.5352; G4 SHIFT k∈{4..10} grid fraction=1 ∀k, quorum 2k−1 < majority ⌊k²/2⌋+1 ∀k, ratio
(2k−1)/k² strictly decreasing 7/16→19/100; G5 determinism in-process double-run IDENTICAL +
separate-invocation diff exit 0), grounding byte-pinned (Wikipedia "Maekawa's algorithm" oldid
1306919367, wikitext sha1 `894805bdbac0adce66d1e794c45925fa9b280e89`, 3-way match). QUALIFIED APPROVE:
the disclosed grounding caveat mis-describes the source (claims the article "describes the OPTIMAL √N
family via finite projective planes" — the revision has NO projective-plane / concrete-construction
content at all; grep projective/plane/grid/finite/optimal → zero hits) and is CORRECTED here; the head
stays soundly grounded via the article's abstract intersection/√N axioms (Rᵢ∩Rⱼ≠∅, |Rᵢ|≥√(N−1),
3√N–6√N messages, cites Maekawa 1985), of which the plain 2k−1 grid is a valid concrete member.
Born-red HOLD armed on the first card commit; released by the deliberate `complete` flip.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the substrate
born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the
deliberate LAST commit — only after the sim dir (byte-identical verifier copy + reproduction stdout +
probe-report), the digest match (full-64 exact
`bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f`, printed + independently reproduced),
the five-gate evaluation each in its own direction (all PASS), the determinism check (in-process
double-run guard held AND separate-invocation diff exit 0), and the grounding check (sha1 3-way match +
caveat correction) have ALL landed — that flip clears the HOLD and releases merge-on-green. NO merge API
calls are made from this session; CI + the landing automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 209 (P209 → V222, +13 offset, lane superbot-games): **grid quorums √N intersection
(Maekawa).** On a k×k grid of N=k² sites, assign each site the quorum consisting of every site in its
row and its column — a set of exactly 2k−1 sites (the row's k, the column's k, minus the shared corner).
Any two such quorums ALWAYS intersect: two rows and two columns on a grid must cross, so Rᵢ∩Rⱼ is never
empty even though each quorum is only O(√N) of the N sites. This is the quorum-intersection property that
makes Maekawa's √N mutual-exclusion algorithm correct. The crux is that STRUCTURE, not size, buys the
intersection: random subsets of the SAME size 2k−1 drawn from the N sites are disjoint at a positive
rate, while grid quorums are never disjoint. Copies the disclosed verifier
`ideas/fleet/grid_quorum_sqrt_intersection.py` (idea-engine) byte-identical into
`sims/verdict-222-grid-quorums/`, reproduces the results-dict sha256, confirms determinism, and evaluates
the five gates each in its own direction against the proposal's OWN criteria.

## Method

- Byte-identical verifier copy (diff source↔copy exit 0), stdlib-only (`hashlib`, `json`, `random`,
  `itertools`, `fractions.Fraction`, `math`). Grid size k=6 (N=36, quorum size 2k−1=11), all C(36,2)=630
  quorum pairs enumerated exactly; Monte-Carlo N_MC=2e6 for the random same-size-subset control.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own
  sha256 IS the digest; target `bbc54843f3693815f107f95df069c26d985a3799b2afe2c0f689a38e3659096f`.
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 grid ALWAYS intersects (exact, direction: intersection_fraction == Fraction(1))** — every one of
    the 630 grid-quorum pairs at k=6 shares ≥ 1 site (min overlap = 2). PASS iff
    `intersection_fraction == Fraction(1)`.
  - **G2 agreement with the closed form (direction: |z| small)** — the Monte-Carlo random-subset
    disjoint rate (0.0074515) agrees with the exact hypergeometric closed form
    C(25,11)/C(36,11) = 10925/1472562 = 0.007419042458: z = 0.5349 < 3. PASS iff |z| < 3.
  - **G3 SURPRISE crux (direction: |z| large ≥ 3σ vs zero)** — random same-size-11 subsets are disjoint
    at a POSITIVE rate 0.0074515 (14903/2e6) while grid quorums are disjoint at EXACTLY 0:
    z = 122.5352 ≥ 3. PASS iff z large (structure, not size, buys the intersection).
  - **G4 SHIFT k∈{4..10} (direction: fraction==1 ∀k AND quorum < majority ∀k AND ratio decreasing)** —
    grid intersection fraction = 1 for every k; quorum 2k−1 < simple majority ⌊k²/2⌋+1 for every k;
    the ratio (2k−1)/k² is strictly DECREASING 7/16 → 19/100. PASS iff all three hold.
  - **G5 determinism (direction: byte-identical)** — an in-process double run is IDENTICAL and two
    separate process invocations diff exit 0. PASS iff both hold.
- Grounding: Wikipedia "Maekawa's algorithm", oldid 1306919367 (2025-08-20T12:53:12Z), raw-wikitext sha1
  `894805bdbac0adce66d1e794c45925fa9b280e89` (3-way match: disclosed == API-stored == independently
  computed). The article DIRECTLY supports the head — states the quorum-intersection property Rᵢ∩Rⱼ≠∅,
  |Rᵢ|≥√(N−1), 3√N–6√N messages, and cites Maekawa's 1985 √N paper. **CAVEAT CORRECTION (the
  qualifier):** the disclosed caveat claims the article "describes the OPTIMAL √N family via finite
  projective planes" — this is FACTUALLY WRONG. The revision contains NO projective-plane content and NO
  concrete construction at all (grep projective/plane/grid/finite/optimal → zero hits); it states only
  the abstract quorum axioms. Net effect FAVORS the citation: because the article states the
  intersection/√N properties abstractly, the plain 2k−1 grid the verifier enumerates is a fully valid
  concrete member. The head is soundly grounded; the qualification is only that the disclosed grounding
  caveat mis-describes the source and is corrected here.

## ⟲ Previous-session review

Previous-session review: VERDICT 221 (Pólya urn reinforcement ends uniform — a rich-get-richer urn
started at 1 black + 1 white finishes EXACTLY uniform on the black-count and Beta(1,1)=Uniform(0,1) on
the share; shifting to (2,1) bends the finish to Beta(2,1), mean 2/3; PROPOSAL 208 → V221) landed
complete with a full-64 digest MATCH (`d566e380…aa68`) and all five gates PASS via the born-red HOLD
choreography. Its carry-forward was GATE-POLARITY discipline: read each gate in ITS OWN direction — an
exact-0 / exact-Fraction residual is a self-certifying theorem, a ≥3σ z is an EFFECT gate, a below-3
max-dev-z is a CONVERGENCE/AGREEMENT gate. V222 leans on that same discipline with a five-gate mix
spanning BOTH polarities in one slice: G1's exact `intersection_fraction == Fraction(1)` (a theorem —
the grid always intersects, any disjoint pair FAILS), G3's HIGH-z SURPRISE crux (z=122.5352 is a
large-effect PASS — random same-size subsets ARE sometimes disjoint while grid never is, so structure
not size buys the intersection), G2's LOW-z agreement (z=0.5349 is a small-|z| PASS — the Monte-Carlo
random-disjoint rate matches the hypergeometric closed form), and G4's SHIFT sweep. The load-bearing
evidence is the exact G1 identity plus the G3 surprise crux together: the grid's disjoint rate is
EXACTLY 0 while an equal-SIZE random control is disjoint at 0.0074 > 0, isolating STRUCTURE as the cause.
This verdict also carries a GROUNDING-caveat correction (below), the reason the ruling is QUALIFIED
rather than plain APPROVE. Standing non-contiguity persists: V137 (P124), V132 (P119), and the round-26
FLEET-slot V126 (P113) remain open BELOW the high-water; landing V222 does not imply every lower verdict
is closed.

## 💡 Session idea

The G3 crux — grid quorums NEVER disjoint while equal-size random subsets are disjoint at the
hypergeometric rate C(N−m,m)/C(N,m) — is one sampled point of a **structure-vs-size intersection dial**
that the exact machinery already almost computes. A cheap orthogonal extension that reuses the exact
pair-enumeration verbatim would add a deterministic **quorum-family sweep gate**: for a fixed N, compare
the intersection fraction of THREE same-size families — (a) the k×k grid row∪col quorums (fraction = 1,
size 2k−1), (b) a finite-projective-plane / Maekawa-optimal quorum set of order q where N=q²+q+1 (also
fraction = 1 but the strictly-smaller optimal size q+1 ≈ √N), and (c) the random same-size control
(fraction = 1 − hypergeometric-disjoint-rate < 1) — pinning in exact Fraction arithmetic that BOTH
structured families intersect always while the size-matched random family does not, AND that the
projective-plane quorum is strictly smaller than the grid's 2k−1 at matched N. That turns "grid always
intersects, random sometimes doesn't" from a single k=6 witness into a continuous statement that
intersection is a property of the COMBINATORIAL DESIGN, with the projective plane as the size-optimal
witness the mis-stated caveat gestured at. The digest-bearing dict and the five shipped gates stay
byte-identical; only a sibling exact family-sweep gate is added. (Guard recipe for a later session: the
anchor is the verifier's exact pair-enumeration over `itertools.combinations` of the quorum list — add a
`projective_plane_quorums(q)` builder beside the existing `grid_quorums(k)` and route both through the
same `intersection_fraction` reducer; the test target is `intersection_fraction == Fraction(1)` for both
structured families at a matched N=q²+q+1.)

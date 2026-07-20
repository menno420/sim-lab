# VERDICT 223 — Akerlof lemons market collapse: a market in which EVERY possible trade strictly benefits both buyer and seller can still collapse to a vanishing fraction of its potential volume — quality uncertainty ALONE, with no transaction cost and no irrationality, destroys nearly all the gains from trade. On a quality grid Q={1..N}, seller reservation q and rational buyer valuation βq (1<β<2, so βq>q for every q — every trade win–win), the only price a competitive buyer will pay attracts a self-selecting pool of the worst goods, so the equilibrium max trading price is p* = min(N, ⌊β/(2−β)⌋) = 3 of 1000 at β=3/2 and the destroyed gains-fraction D = 1 − p*(p*+1)/(N(N+1)) ≈ 0.999988 — reproduce PROPOSAL 210

- **Slice:** sim-lab VERDICT 223 (reproduce and rule on PROPOSAL 210; P210 → V223, +13 offset; lane venture-lab)
- **Source proposal:** PROPOSAL 210 — Akerlof lemons market collapse (idea-engine `ideas/venture-lab/lemons-market-collapse-2026-07-20.md`)
- **Verifier (source):** `ideas/venture-lab/lemons-market-collapse-2026-07-20.py` (idea-engine) — copied byte-identical into this sim dir as `lemons-market-collapse-2026-07-20.py`
- **Reproduced by:** copy the verifier byte-identical (diff exit 0), run it, capture stdout, recompute the results-dict sha256 and confirm full-64 match; two cross-invocation runs byte-identical
- **Timestamp (date -u):** 2026-07-20T12:00:50Z
- **SEED:** 20260717 · **battery:** β ∈ {11/10, 5/4, 4/3, 3/2, 5/3, 7/4, 9/5, 19/10}, N ∈ {50, 100, 500, 1000, 5000} · **pinned world:** β = 3/2, N = 1000 · **Monte-Carlo M:** 200000 · **z_gate:** 3.0
- **Stdlib-only:** `hashlib`, `json`, `math`, `random`, `fractions` — no third-party imports.

## 📊 Model: Opus family · high effort · verdict-reproduction

## Ruling: APPROVE

Fully reproduced. The results-dict sha256 `b0251b0aa024e235fa4991c005c1cd3deaa3a04f2fcd2e5d4e041e6e21237539`
matches the disclosed PROPOSAL 210 digest across all 64 hex characters — printed by the verifier AND
independently recomputed here by re-canonicalizing the printed results dict (0 divergence), and
byte-identical across two separate invocations. The verifier was copied byte-identical (diff exit 0). All
four gates PASS, each read in its own direction: G1 and G4 are self-certifying EXACT-`Fraction`
identities (the closed-form threshold ≡ an exhaustive scan; the destroyed fraction ≡ the explicit
surplus-ratio identity — theorems, not tuned tolerances), G2 is a HIGH-z surprise crux (z ≈ 4078, the
win–win market survives at ~0.3% — thousands of σ below the folk "at least half survives" null), and G3
is a persistence/SHIFT sweep (D monotone in N, exact residual 0, near-total collapse ≥ 0.99 even at the
shallowest β = 19/10 corner). The head is honestly scoped as the canonical Akerlof result (disclosed as
standard, not a novel discovery) with an exact discrete instantiation, and externally grounded to a
byte-pinned Wikipedia revision. The disclosed grounding caveat is accurate (checked below). **Ruling: APPROVE.**

## Head

Akerlof "Market for Lemons" adverse-selection collapse. On a discrete quality grid Q = {1,…,N} with
uniform prior, the seller reservation for quality q is q (a seller parts with the good only if the price
meets its own value) and a rational buyer values q at β·q with 1 < β < 2 — so β·q > q for every q > 0,
EVERY trade is strictly mutually beneficial, with no transaction cost and no irrationality. A competitive
buyer who cannot observe q will pay a single posted price p only up to the expected value of what that
price actually attracts, β·E[q | q offered at p]. The offered set at price p is S(p) = {q ≤ p} (offering
is self-selecting on hidden quality — the worse the pool, the wider it is at any given price), and with
the uniform grid E[q | S(p)] = (p+1)/2, so willingness holds iff p ≤ β·(p+1)/2. Rearranged,
p ≤ β/(2−β): the price grows like p while the quality it buys grows only like βp/2 < p for β < 2, so the
offered pool degrades as fast as the price climbs. The equilibrium max trading price is therefore
p* = min(N, ⌊β/(2−β)⌋), and only q ≤ p* changes hands. At β = 3/2, N = 1000 that is p* = 3 of 1000, and
the destroyed fraction of mutually-beneficial gains is D = 1 − p*(p*+1)/(N(N+1)) = 1 − 12/1001000 ≈
0.999988 — the market realizes ~0.3% of its potential volume. The collapse is driven by β's distance
below 2, not by N: p* is essentially a constant of β once N exceeds it, so as the grid grows the
surviving fraction p*/N → 0 and D → 1 — a larger, richer market DEEPENS the failure.

## Reproduction

- Verifier copied byte-identical: `diff ideas/venture-lab/lemons-market-collapse-2026-07-20.py sims/verdict-223-lemons-collapse/lemons-market-collapse-2026-07-20.py` → **exit 0**.
- results-dict sha256 posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))`, exact `Fraction`s serialized as "num/den" strings, floats rounded to a fixed 10 dp, no self-referential sha field), printed to stdout as `RESULTS_SHA256=<64hex>`.
- Disclosed digest:              `b0251b0aa024e235fa4991c005c1cd3deaa3a04f2fcd2e5d4e041e6e21237539`
- Reproduced (printed by run):   `b0251b0aa024e235fa4991c005c1cd3deaa3a04f2fcd2e5d4e041e6e21237539`
- Independently recomputed:      `b0251b0aa024e235fa4991c005c1cd3deaa3a04f2fcd2e5d4e041e6e21237539` — recomputed OUTSIDE the verifier by parsing the printed results dict from `run-stdout.txt`, re-serializing compact-canonical (`sort_keys=True, separators=(",",":")`), and hashing sha256 → identical across all 64 hex chars.
- **FULL-64 EXACT MATCH** (printed == independently-recomputed == disclosed target). The printed token is exactly 64 hex chars (`[0-9a-f]{64}`), no truncation.
- Cross-invocation: two separate process invocations produced byte-identical whole files including the digest line (`diff` exit 0), so both printed the same 64-char digest.
- Full reproduction stdout: `run-stdout.txt`.

## Determinism

- In-process double-run: the verifier computes the results dict twice in one process and asserts `canonical(r1) == canonical(r2)` before hashing (a fresh `random.Random(20260717)` is created at the start of each full run); the run prints `double_run_identical=true` and exits 0, so the in-process guard held.
- Cross-invocation: two separate `python3` invocations → byte-identical whole stdout including the digest line, `diff` **exit 0**.
- Determinism: **CONFIRMED** (in-process double-run guard held AND separate-invocation diff exit 0).

## Gate evaluation (against PROPOSAL 210's OWN criteria, each read in ITS direction)

Every gate was re-derived independently here in a fresh stdlib re-implementation (NOT importing the
verifier), and the numbers match the verifier's printed output exactly.

- **G1 — EXACT p\*** (direction: exact agreement, expect discrepancies = 0). Over the full 40-pair (β,N)
  battery, the closed form p*_closed = min(N, ⌊β/(2−β)⌋) equals the exhaustive `Fraction` scan p*_scan
  (scan p = 0..N with the exact willingness test p ≤ β·(p+1)/2, take the max willing p):
  **discrepancies = 0.** At the pinned world β = 3/2, N = 1000 both give **p\* = 3**. p* is a constant of
  β alone across every N: β = 11/10 → 1, 5/4 → 1, 4/3 → 2, 3/2 → 3, 5/3 → 5, 7/4 → 7, 9/5 → 9,
  19/10 → 19 (identical at N = 50, 100, 500, 1000, 5000). **PASS** (self-certifying: an exact-Fraction
  agreement over an exhaustive scan is a theorem, not a tuned tolerance).
- **G2 — SURPRISE** (direction: HIGH z ≥ 3.0). Monte-Carlo on the pinned world (β = 3/2, N = 1000),
  M = 200000 draws from `random.Random(20260717)`: **hits = 596**, realized-trade rate
  **r_hat = 0.00298** versus the exact predicted p*/N = 3/1000 = 0.003, se = 0.0001218835, against the
  folk-null strawman H0 = 0.5 ("a reasonable observer expects at least half a wholly win–win market to
  survive"): **z = 4077.8269869233** (≫ 3, direction HIGH). r_hat = 0.00298 ≪ 0.5. **PASS** (EFFECT /
  SURPRISE gate — a LARGE z is the PASS direction; this is THE CRUX: the win–win market survives at
  ~0.3%, ~4078σ below the folk expectation, an astronomically large z because the effect is structural,
  not marginal).
- **G3 — ROBUSTNESS / SHIFT** (direction: persistence — monotone + near-total collapse, residual 0).
  (i) For each β, D(β,N) is weakly increasing in N: **monotone = true**. (ii) Exact residual
  |D_measured − D_closed| = 0 everywhere (`Fraction` D via realized/potential GFT with the (β−1) factor
  carried explicitly ≡ the closed form): **residual_discrepancies = 0**. (iii) min over all β of
  D(β, N=5000) = **1250231/1250250 ≈ 0.9999848** at the corner **β = 19/10** (the shallowest collapse,
  largest p* = 19) ≥ 0.99 with wide margin. D(β = 3/2) row rising toward 1: D(50) = 423/425,
  D(100) = 2522/2525, D(500) = 20874/20875, D(1000) = 250247/250250, D(5000) = 2083749/2083750.
  **PASS** (persistence gate — near-total collapse survives even β = 1.9 once N is large).
- **G4 — EXACT identity** (direction: exact, expect discrepancies = 0). Across the battery, the
  destroyed-fraction closed form D = 1 − p*(p*+1)/(N(N+1)) equals 1 − (explicit Σ_{q≤p*} q)/(explicit
  Σ_{q≤N} q) via explicit integer summation: **discrepancies = 0.** **PASS** (self-certifying exact
  surplus-identity theorem — no sampling).

Overall: gates {G1: true, G2: true, G3: true, G4: true}, `all_pass = true`, `first_failing_gate = null`.

## Grounding

- External, byte-pinned: Wikipedia "The Market for Lemons", oldid **1358736918**, pinned by the MediaWiki
  revision sha1 `34c3ec139bfdd21dc2d0a30ddd895bade01f6a3c` (a 40-hex byte-pin of the exact revision, NOT
  a sha256). The article carries the adverse-selection / asymmetric-information / quality-uncertainty /
  market-collapse core.
- **Disclosed grounding caveat is ACCURATE (verbatim from the proposal):** *"Grounding is qualitative on
  the page; the threshold is ours. The Wikipedia article 'The Market for Lemons' describes the phenomenon
  and model qualitatively (adverse selection, asymmetric information, quality uncertainty, market
  collapse — all present verbatim in the fetched wikitext); our exact collapse threshold p* = ⌊β/(2−β)⌋
  and the destroyed-fraction closed form D = 1 − p*(p*+1)/(N(N+1)) are our own clean discrete
  instantiation, NOT lifted from the page. The external pin corroborates the mechanism; the firsthand
  witness is the verifier."* This caveat is honest and correct: the mechanism is externally grounded and
  the exact discrete threshold is transparently owned by the proposal, not attributed to the source. The
  proposal also correctly discloses that the pinned `34c3ec13…` is the MediaWiki revision sha1 (a
  byte-pin), not a sha256 of rendered markdown.
- Honestly scoped: the proposal discloses this is the CANONICAL Akerlof (1970) result, taught in every
  information-economics course — NOT a novel discovery; the contribution is the pinned, gate-verified
  exact discrete instantiation and the venture/markets framing, not the (standard, disclosed) mathematics.

## Novelty

Distinct from prior shipped heads. The proposal's author-time grep of `ideas/` for
lemons/adverse-selection/akerlof/market-for-lemons returned zero prior hits, and it is explicitly
distinguished from `ideas/venture-lab/partner-channel-margin-stacking` (double-marginalization — vertical
successive-monopoly under FULL information, a different failure) and `ideas/venture-lab/independent-screens-odds-ladder`
(P206 — screening / odds-multiplication, the REMEDY side of information asymmetry; screening separates
types, whereas this is market UNRAVELING because a single price cannot). Different mechanism, opposite
posture.

## Ruling evidence summary

VERDICT 223 reproduces PROPOSAL 210 bit-exact: the verifier copied byte-identical (diff exit 0), the
results-dict sha256 `b0251b0aa024e235fa4991c005c1cd3deaa3a04f2fcd2e5d4e041e6e21237539` matches the
disclosed digest across all 64 hex characters — printed AND independently recomputed outside the verifier
(0 divergence), byte-identical across two separate invocations — and determinism holds (in-process
double-run guard held AND two cross-invocation processes byte-identical, diff exit 0). All four
pre-registered gates PASS, each read in its own direction: G1's EXACT-`Fraction` threshold identity
(closed form ≡ exhaustive scan over all 40 (β,N) pairs, 0 discrepancies, p* = 3 at β = 3/2, N = 1000),
G2's HIGH-z SURPRISE crux (M = 200000, hits = 596, r_hat = 0.00298 vs predicted 3/1000, z = 4077.83 —
the win–win market survives at ~0.3%, ~4078σ below the folk 0.5 null), G3's persistence/SHIFT sweep
(D monotone in N, exact residual 0, min D(N=5000) = 0.9999848 ≥ 0.99 at the β = 19/10 corner), and G4's
EXACT surplus-identity (D closed form ≡ 1 − (Σ_{q≤p*} q)/(Σ_{q≤N} q), 0 discrepancies). The head is
externally grounded to a byte-pinned Wikipedia revision (oldid 1358736918, revision sha1
`34c3ec139bfdd21dc2d0a30ddd895bade01f6a3c`) whose adverse-selection / asymmetric-information /
quality-uncertainty / market-collapse core firsthand-supports the mechanism; the disclosed grounding
caveat (qualitative on the page, exact threshold owned by the proposal) is accurate. The head is honestly
scoped as the canonical Akerlof result with an exact discrete instantiation and is genuinely distinct
from prior shipped heads. **Ruling: APPROVE.**

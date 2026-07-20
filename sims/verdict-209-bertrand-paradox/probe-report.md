# VERDICT 209 — Bertrand's paradox (random chord): reproduce PROPOSAL 196

- **Slice:** VERDICT 209 · PROPOSAL 196 (P196 → V209, +13 offset)
- **Source proposal:** idea-engine `control/outbox.md` `## PROPOSAL 196 · 2026-07-20T04:12:00Z · status: sim-ready`
- **Verifier (source):** idea-engine `ideas/fleet/bertrand_paradox_chord.py` (landed origin/main squash `3f309a5`, PR #729)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-209, HEAD-synced idea-engine `3f309a5` / sim-lab `3380164`
- **Timestamp (date -u):** 2026-07-20T04:22:24Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`) · Z_GATE=3.0

## Head

Ask for the probability that a "random" chord of a unit circle is longer than the
side of the inscribed equilateral triangle (√3·R), and three equally natural
definitions of "random chord" give EXACTLY **1/3** (random endpoints), **1/2**
(random radial point), and **1/4** (random midpoint). The question is
underspecified, not hard: "uniformly at random" is undefined on a continuous
sample space until the sampling mechanism is pinned (Bertrand 1889). The
threshold perpendicular distance is d* = R/2 (chord = 2√(R²−d²) = √3·R ⟺ d = R/2).

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` → **exit 0**.
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process exit 0.
- **Results-dict sha256 (compact-canonical, `sort_keys=True, separators=(",",":")`):**
  `ab79371c9908f7b16f9478d41969e224eb4c95c19d237a2773df693173b5c3cb`
  — **EXACT MATCH** to the disclosed PROPOSAL 196 digest across all **64** hex
  characters (byte-for-byte string equality, hex-char count = 64, no truncation).
- **all_pass = true** (g1_pass, g2_pass, g3_pass all true).

## Determinism

- **In-process double-run** — `main()` runs `run()` twice and asserts `r1 == r2`
  (byte-identical results dict); assertion holds, exit 0.
- **Separate cross-invocation** — two independent Python invocations of `run()`
  produced the identical results-dict sha256
  `ab79371c…b5c3cb` = `ab79371c…b5c3cb` → **byte-identical**.

## Independent re-derivation of the three exact rationals (my own `fractions.Fraction`)

Not trusting the verifier's `exact_fractions()`, I re-derived from geometry:

- Threshold: `2√(1−d²) = √3` ⟹ `1 − d² = 3/4` ⟹ `d² = 1/4` ⟹ `d* = 1/2` (exact rational).
- **A random endpoints** — fix one endpoint, the other uniform on the circumference;
  the chord is long iff the angular gap φ ∈ (2π/3, 4π/3). Favourable arc measure
  `4π/3 − 2π/3 = 2π/3` over total `2π` (π cancels) → **(2/3)/2 = 1/3**.
- **B random radial point** — midpoint uniform on a radius, d ~ U[0,1]; long iff
  d < 1/2 → length[0,1/2]/length[0,1] = **1/2**.
- **C random midpoint in disk** — midpoint uniform over the disk area; long iff
  midpoint within radius 1/2 → area ratio (1/2)² = **1/4**.

`Fraction`-exact assertion `endpoints==1/3 and radial==1/2 and midpoint==1/4`
holds. The non-uniqueness is EXACT (π cancels in every mechanism), not a sampling
artifact. Cross-mechanism spread = 1/2 − 1/4 = **0.25**.

## Gate evaluation (against PROPOSAL 196's OWN criteria, in order)

- **G1 — AGREEMENT gate (Monte-Carlo agrees with the closed form; a SMALL z is the
  PASS condition, not a ≥3σ signal):** M=200000 draws/method at R=1.
  - endpoints: p̂=0.331715 vs p*=0.333333, se=0.001054, **z=1.535286 < 3 → PASS**
  - radial: p̂=0.499135 vs p*=0.5, se=0.001118, **z=0.773680 < 3 → PASS**
  - midpoint: p̂=0.248830 vs p*=0.25, se=0.000968, **z=1.208371 < 3 → PASS**
  - g1_pass = **true**. (z<3 is the intended pass; not flagged as a miss.)
- **G2 — EXACTLY-TRUE gate:** exact-rational geometry `Fraction` ≡ pre-registered
  closed form for all three (endpoints 1/3, radial 1/2, midpoint 1/4;
  `exact_match=true` each), corroborated by deterministic quadrature within
  GRID_TOL=1e-3 (endpoints 0.33333, radial 0.5, midpoint 0.249997; all agree).
  g2_pass = **true**.
- **G3 — robustness/scale-invariance gate:** quadrature sweep across R∈{1,2,5,10};
  within-method spread = {endpoints 0.0, radial 0.0, midpoint 0.0} (all < 0.01 →
  scale-invariant), AND cross-method spread of the exact answers = **0.25 > 0.08**
  (the three answers genuinely differ — the paradox is REAL). g3_pass = **true**.

**all_pass = true**, first failing gate = none.

## Grounding

- **Source:** Wikipedia "Bertrand paradox (probability)" oldid **1363409876**, raw
  wikitext (`action=raw`).
- **Fetch:** `HTTP 200`, byte length **13700** (exact), raw-wikitext sha1
  `884f5add3a888fef5d10c73dcd4d2bac5490f568` — **EXACT MATCH** to the disclosed pin.
- **Content:** the wikitext states all three method names and fractions verbatim:
  - "The 'random endpoints' method: … the probability … is {{sfrac|1|3}}."
  - "The 'random radial point' method: … the probability … is {{sfrac|1|2}}."
  - "The 'random midpoint' method: … the probability … is {{sfrac|1|4}}."
  - plus the inscribed equilateral triangle framing and the d*=R/2 (side bisects
    the radius) construction.
- **Disclosed caveat (honest):** the pin is on the RAW WIKITEXT BYTES, not rendered
  HTML, and the fractions appear as `{{sfrac|1|3}}` / `{{sfrac|1|2}}` / `{{sfrac|1|4}}`
  templates (not literal "1/3" glyphs). This is exactly what the raw fetch shows —
  the disclosure is accurate and conservative. The grounding **resolves**, **states
  the three method names + fractions**, and the **sha1 matches byte-exact**.

## Ruling evidence summary

Digest matches full-64 exact; verifier byte-identical (diff exit 0); deterministic
(in-process double-run + cross-invocation byte-identical); the three exact
rationals 1/3, 1/2, 1/4 independently re-derived in `fractions.Fraction`; G1
(agreement, all z<3) / G2 (exact rationals + quadrature) / G3 (scale-invariant,
cross-spread 0.25>0.08) all PASS in order; grounding resolves byte-exact and
states the head verbatim. G2 is an exact self-certifying identity and the head is
externally grounded byte-exact → a **clean APPROVE** posture. Final ruling is the
coordinator's.

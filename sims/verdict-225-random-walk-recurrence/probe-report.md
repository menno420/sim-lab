# VERDICT 225 — PROPOSAL 212 (Pólya recurrence: a drunk man finds home in 2D / a drunk bird may be lost forever in 3D)

**Ruling: APPROVE**

Reproduced byte-exact; all six pre-registered gates independently confirmed each in its own direction; grounding caveat honest.

Headline: adding a third axis flips certain return into probable never-return — the simple symmetric lattice walk returns to its origin with probability 1 in 2D (recurrent) but only ~0.3405 in 3D (transient).

## Reproduction
- Source verifier: idea-engine `ideas/fleet/random-walk-recurrence-dimension-2026-07-20.py`, copied byte-identical (`diff` source↔copy exit 0, `cmp` byte-identical) to `sims/verdict-225-random-walk-recurrence/`.
- SEED=20260717, stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions.Fraction`).
- `results_sha256 = 66ca292316986d8121a552e3c4c61557182d787b2e25cf54659a0130d0dede07` — FULL-64 EXACT match to the disclosed PROPOSAL 212 digest (64 hex chars, byte-grep `^[0-9a-f]{64}$` PASS, no truncation; printed by the verifier AND independently recomputed identical).
- Digest posture: WHOLE-DICT — the compact-canonical results dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`).

## Determinism
- In-process double-run guard: `determinism_double_run_ok: true` (the verifier runs `run_battery()` twice and asserts `r1 == r2`).
- Cross-invocation: two separate process runs produced byte-identical stdout (`run-stdout.txt` vs `run-stdout-2.txt`, `cmp` exit 0) and the same full-64 digest.

## Gate evaluation (each read in ITS OWN direction, against the proposal's OWN criteria)

- **G1 — EXACT 2D enumeration identity — PASS.** Brute-force count of every length-2n closed 2D lattice walk equals the closed form C(2n,n)² integer-exact at 2n ∈ {2,4,6}: **4 / 36 / 400** (enum == closed, all `eq: true`). Independently re-brute-forced here via `itertools.product` over the 4-move alphabet (a method distinct from the verifier's recursion) — identical 4/36/400. Direction: exact integer equality, any discrepancy FAILS.
- **G2 — EXACT 3D enumeration identity — PASS.** Brute-force count of every length-2n closed 3D lattice walk equals Σ_{i+j+k=n} (2n)!/(i!²j!²k!²) integer-exact at 2n ∈ {2,4}: **6 / 90** (enum == closed, all `eq: true`). Independently re-brute-forced — identical 6/90. Direction: exact integer equality.
- **G3 — 2D non-summable ⇒ recurrent — PASS.** n·p₂(2000) = **0.31827**, landing on 1/π = 0.31831 (band [0.30, 0.335]). The return-probability summand decays like 1/n (p₂(2n)~1/(πn)), so ΣU diverges ⇒ the Green's function is infinite ⇒ return probability 1 (recurrent). Direction: scaled value in the predicted 1/π band certifying divergent series.
- **G4 — 3D summable ⇒ transient — PASS.** n^1.5·p₃(60) = **0.231839**, near the local-CLT target 2·(3/4π)^1.5 = 0.233291 (band [0.19, 0.29]). The summand decays like n^(−3/2), so ΣU converges (Watson's integral ≈ 1.5164) ⇒ return probability 1 − 1/U ≈ 0.3405 < 1 (transient). Direction: scaled value in the predicted band certifying convergent series.
- **G5 — 3D empirically transient — PASS.** Monte-Carlo within-horizon 3D return fraction f3_hi = **0.335467** (inside [0.28, 0.38], near Pólya's constant 0.3405), sitting z = **42.6792** below the recurrence line 0.5 (≥ 3σ). Direction: (0.5 − f3)/σ ≥ 3 — a firsthand empirical corroboration that 3D return is bounded strictly under 1/2.
- **G6 — 2D dominates + horizon-shift — PASS.** 2D return fraction f2_hi = 0.6814 beats 3D f3_hi = 0.335467 with z_dominate = **63.8705** (≥ 3σ); 2D return fraction RISES with horizon (f2_lo 0.5808 → f2_hi 0.6814, z_shift_2d = **18.1551**) — the divergent return-count signature — while 3D stays comparatively flat (f3_lo 0.314667 → f3_hi 0.335467, z_shift_3d = **3.8467**), and z_shift_2d ≥ z_shift_3d + 3 (18.1551 ≥ 6.8467). Direction: dominance + a 2D-specific horizon rise that outpaces 3D by ≥ 3σ.

`gates = {G1: true, G2: true, G3: true, G4: true, G5: true, G6: true}`, `sim_ready: true`. Both directions of Pólya's claim hold: 2D is certainly recurrent (exact identities + divergent-series scaling + rising-with-horizon MC) and 3D is transient (convergent-series scaling + a return fraction pinned near 0.3405, ≫3σ below 1/2).

### Observed vs disclosed (all match)
| Quantity | Disclosed | Observed |
|---|---|---|
| 2D enum/closed 2n∈{2,4,6} | 4/36/400 | 4/36/400 |
| 3D enum/closed 2n∈{2,4} | 6/90 | 6/90 |
| n·p₂(2000) | ≈0.31827 (1/π≈0.31831) | 0.31827 |
| n^1.5·p₃(60) | ≈0.23184 (≈0.23329) | 0.231839 |
| f3_hi / z_transient | ≈0.3355 / z≈42.7 | 0.335467 / 42.6792 |
| z_dominate 2D>3D | ≈63.9 | 63.8705 |
| z_shift_2d (0.581→0.681) | ≈18.2 | 18.1551 (0.5808→0.6814) |
| z_shift_3d | ≈3.85 | 3.8467 |

## Grounding (accuracy scrutinized — per the V222 lesson)
Wikipedia "Random walk", oldid **1359285496**, raw-wikitext (action=raw) sha1 `bdcc6ea9d1ec88b8313eb470f475758301f9dd77` — CONFIRMED (`sha1sum` on the 57898 raw bytes == disclosed, full-40 hex match; disclosed pin = computed).

The proposal's caveat (its own Q5 answer) states the page asserts Pólya's theorem + "roughly 34%" + the aphorism, but does NOT contain the exact 0.3405, the enumeration identity, the decay-law check, or the seeded simulation. Verified against the wikitext:

**CONFIRMED PRESENT** (line 174):
> "In 1921 [[George Pólya]] proved that the person [[almost surely]] would in a 2-dimensional random walk, but for 3 dimensions or higher, the probability of returning to the origin decreases as the number of dimensions increases. In 3 dimensions, the probability decreases to roughly 34%."
> "The mathematician [[Shizuo Kakutani]] was known to refer to this result with the following quote: \"A drunk man will find his way home, but a drunk bird may get lost forever\"."

— Pólya's theorem (recurrent 1–2D, transient 3D+), the **1921** Pólya proof (also cited at line 365, *Mathematische Annalen* 84, 1921), "roughly **34%**" in 3D, and the drunk-man/drunk-bird aphorism are all on-page.

**CONFIRMED ABSENT on-page** (grep returned no hits):
- The exact figure **0.3405** — the page says only "roughly 34%"; the constant is reachable only via the linked MathWorld "Pólya's Random Walk Constants", not printed in the article text.
- The **enumeration identity** C(2n,n)² / the multinomial 3D count — not on the page.
- The **decay-law** scaling check (1/π, n^(−3/2), 2(3/4π)^1.5) — not on the page. (The page carries a general recurrence-probability integral at line 176, but not this firsthand finite-n scaling check.)
- The **seeded simulation** (SEED, 15000 walks, first-return fractions, z-scores) — not on the page. (Line 12 has a generic "Realizations … can be obtained by Monte Carlo simulation" sentence, which is NOT this proposal's specific seeded battery.)

**Assessment: HONEST.** The caveat states only what the page verbatim asserts (Pólya + "roughly 34%" + aphorism) and correctly scopes the exact 0.3405, the enumeration identities, the decay-law, and the seeded simulation as the verifier's OWN firsthand results — not lifted from the page. A well-scoped, accurate disclosure → APPROVE.

## Provenance
- P212: idea-engine slug random-walk-recurrence-dimension, landed on origin/main as merge 445a110 (PR #781); disclosed digest `66ca292316986d8121a552e3c4c61557182d787b2e25cf54659a0130d0dede07`.
- Claim: idea-engine PR #782 (control/claims/2026-07-20-verdict-225.md).
- Reproduction: sim-lab PR (branch `claude/verdict-225`); sim dir `sims/verdict-225-random-walk-recurrence/`.
- Verified at: Mon Jul 20 13:06:11 UTC 2026

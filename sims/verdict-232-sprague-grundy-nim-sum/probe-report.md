# VERDICT 232 — Probe report (reproduces PROPOSAL 219)

> In an impartial combinatorial game, a disjunctive-sum position is a loss for
> the player to move (a P-position) **iff the XOR ("nim-sum") of its component
> Grundy values is zero** (Sprague–Grundy). For the single-heap subtraction game
> Sub({1,…,k}) the Grundy value has the exact closed form **G(n) = n mod (k+1)**,
> and the Grundy value of a disjunctive sum of heaps equals the nim-sum (XOR) of
> the per-heap Grundy values. For d-heap Nim over {0,…,2^b−1} the exact
> P-position density is 1/2^b; for d=b=3 that is exactly 1/8.

- **Slice:** round-52 GAME, P219 → V232 (+13 offset)
- **Branch:** `claude/verdict-232-nim-sprague-grundy`
- **Sim dir:** `sims/verdict-232-sprague-grundy-nim-sum/`
- **Source:** PROPOSAL 219 (idea-engine `ideas/superbot-games/sprague-grundy-nim-sum-2026-07-20.md`), timestamp `2026-07-20T16:17:18Z`
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of the committed `sims/verdict-232-sprague-grundy-nim-sum/sprague_grundy_nim_sum.py`
→ scratch copy; `diff` committed ↔ copy exit **0** (byte-identical, logic unaltered).
Stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions.Fraction`). SEED = 20260717.

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256: e50e461d105e4984f6f562def0eba3f527ef4030512f9cf75294ddd6709002b7
```

- Disclosed target: `e50e461d105e4984f6f562def0eba3f527ef4030512f9cf75294ddd6709002b7`
- Literal string compare `[ "$REPRODUCED" = "$DISCLOSED" ]` → **MATCH** (length 64,
  no truncation, bit-exact). The committed `run-stdout.txt` carries the same digest.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical
  results dict's own sha256 IS the digest; the dict carries no self-field hash.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice and asserts the
  canonical-JSON forms are byte-identical before printing the digest (exit 3 on
  divergence, exit 0 here).
- **Cross-invocation:** a second separate process re-invocation produced a
  byte-identical digest. No wall-clock or OS randomness — the only RNG is a
  `random.Random(SEED)` seeded from the fixed SEED.

## 4. Gates — six, all PASS in their own directions, teeth confirmed

| Gate | Direction | Observed | Pass |
|------|-----------|----------|------|
| **G1** MC significance | AGREEMENT, |z| < 3 | 200 000 draws, phat=**0.12607** vs exact 1/8, z=**1.446904** | ✅ |
| **G2** exact density | EQUALITY, == Fraction(1,8) | count **64** of 512 triples, density **1/8** == expected | ✅ |
| **G3** Sub({1,2,3}) Grundy | ZERO MISMATCH, G(n)==n mod 4 on [0,256] | **0** mismatches | ✅ |
| **G4** Sprague–Grundy sum | ZERO MISMATCH, G_sum==G(a)⊕G(b) on [0,40]² | 1681 checked, **0** mismatches | ✅ |
| **G5** robustness | ZERO MISMATCH, G(n)==n mod (k+1), k∈{2,3,4,5} | all four k: **0** mismatches | ✅ |
| **G6** falsifiability | REJECTION, |z| > 3 | naive total-parity (density 1/2) REJECTED at z_naive=**−334.45316** | ✅ |

`all_pass=true`, `first_failing_gate=null`.

**Teeth read per gate (each in its own direction):**
- **G1** is a genuine independent stochastic estimate over 200 000 draws; the pass is
  agreement with the exact 1/8 within 3σ (a broken sampler or wrong density would
  diverge). Direction correct.
- **G2** is an exact rational equality over the full 512-triple enumeration. **SOFT
  NOTE:** it is near-definitional — group-uniformity of the nim-sum guarantees the
  density is exactly 1/8 — so the gate cannot fail while the XOR logic is correct.
  It is still an exact firsthand enumeration and is paired with the teeth-bearing
  G3/G4, so the ruling is unchanged.
- **G3** independently computes the mex recurrence for Sub({1,2,3}) and compares it to
  the closed form n mod 4 with zero tolerance — strong teeth, because this closed
  form is the firsthand claim that Wikipedia does NOT state as an equation.
- **G4** computes the disjunctive-sum Grundy value directly by mex over the joint move
  set and checks it equals G(a)⊕G(b) over all 1681 pairs — strong teeth; this is the
  Sprague–Grundy nim-sum criterion itself, an independent 2-D computation, not a
  restatement of G3.
- **G5** re-runs the closed form for four distinct subtraction sets — rules out a k=3
  coincidence.
- **G6** constructs a concrete WRONG model (loss iff a+b+c even → density 1/2) and
  rejects it at 334σ — strong teeth, opposite direction to G1, confirming G1 is not
  trivially passable.

## 5. Grounding — byte-pinned, sha1 match on both revisions; HONEST caveat

- **Nim**, oldid **1362772636**, `action=raw` wikitext (30 663 bytes): sha1 =
  `750a8fd6ead1d0b082596aab4f84d9d4bd49da78` = disclosed pinned sha1 → **MATCH**.
- **Sprague–Grundy theorem**, oldid **1362556548**, `action=raw` wikitext (20 199
  bytes): sha1 = `818faacdf5b5a059f160a8550c7b4c1acd5719a2` = disclosed pinned sha1
  → **MATCH**.

**On-page (confirmed present by grep):**
- Nim: verbatim "In a normal nim game, the player making the first move has a winning
  strategy if and only if the nim-sum of the sizes of the heaps is not zero"; and, in
  the subtraction-game section, the OUTCOME condition `0 = n (mod k+1)` (normal play).
- Sprague–Grundy: the mex (minimum exclusion) definition of the Grundy value; "A
  position is a loss for the next player to move … if and only if its Grundy value is
  zero"; and "The Grundy value of the sum of a finite set of positions is just the
  nim-sum of the Grundy values of its summands."

**Off-page (correctly absent, and the proposal says so):**
- NEITHER page states the closed-form Grundy-value equation `G(n) = n mod (k+1)`. The
  Nim page's subtraction-game section gives only the win/loss outcome condition
  `n ≡ 0 (mod k+1)`, not a Grundy-value formula; the Sprague–Grundy page does not
  treat bounded subtraction games at all (grep for "subtraction" → no matches).

### Grounding-accuracy assessment (per the V222 grounding-scrutiny lesson)

The proposal's caveat is **honest** — neither oversold nor undersold. It does not
oversell: it explicitly does NOT claim Wikipedia states the closed-form Grundy
equation, and correctly attributes only the XOR/nim-sum criterion and the mex/Grundy
framework to the pages. It does not undersell: it acknowledges those criteria are
genuinely on-page. The caveat cleanly separates the **firsthand-proven** results
(G(n)=n mod (k+1), the disjunctive-sum reproduction over [0,40]², and the digest)
from the **cited framework** (nim-sum-zero winning criterion, mex, P-position-iff-
Grundy-zero, disjunctive-sum-is-nim-sum). No mis-description of the source, so no
qualification is forced.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256 full-64
EXACT match (literal 64-char compare, bit-exact); determinism holds on both the
in-process double-run and the separate cross-invocation legs; all six pre-registered
gates PASS each in its own direction with the wrong model correctly rejected at 334σ;
grounding sha1 matches BOTH pinned revisions with the XOR/mex framework present
on-page and the closed-form Grundy equation honestly disclosed as firsthand-proven
rather than cited. One SOFT NOTE (G2 is near-definitional) that does not affect the
ruling because it is paired with the teeth-bearing G3/G4. No qualification required.

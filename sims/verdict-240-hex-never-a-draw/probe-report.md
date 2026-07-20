# VERDICT 240 — Probe report (reproduces PROPOSAL 227)

> Hex is never a draw: for every complete two-colouring of the n×n board exactly one player connects, so under a uniform random fill P(first player connects) = 1/2 EXACTLY, and #{Red}=#{Blue}=2^(n²−1).

- **Slice:** round-54 GAME slot · PROPOSAL 227 → VERDICT 240 (+13 offset)
- **Branch:** `claude/verdict-240-hex-never-a-draw`
- **Sim dir:** `sims/verdict-240-hex-never-a-draw/`
- **Source:** idea-engine `ideas/superbot-games/hex-never-a-draw-2026-07-20.md` (PROPOSAL 227, control/outbox.md)
- **Ruling recommendation:** APPROVE

## 1. Verifier copy — byte-identical

`hex-never-a-draw.py` is stdlib-only (sys, json, math, hashlib, random, collections.deque, fractions.Fraction). It is the firsthand artefact; the idea-engine doc references it by path. `SEED = 20260717`.

## 2. Digest — full-64 EXACT match

`results_sha256 = 76d9a3267140171bec9ad335b370c6028e1359d23f39c7c87f3d7125598ebed8`

Whole-dict sha256 over the canonical `json.dumps(sort_keys=True, separators=(",",":"))` form, no self-field embedded, printed to stdout only. Matches the digest disclosed in the PROPOSAL 227 idea doc and outbox block.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice and asserts the canonical forms are byte-identical (`sys.exit(3)` on divergence). Holds.
- **Separate re-invocation:** a second independent `python3 hex-never-a-draw.py` prints the identical digest. Holds.
- Single `random.Random(20260717)` consumed in the fixed order G2 → G3 → G4; all sampler-derived floats rounded to 6 decimals.

## 4. Gates — four, all PASS, each in its own direction

| Gate | Direction | Test | Result |
|------|-----------|------|--------|
| G1 | EQUALITY (exact) | exhaustive all 2^(n²) colourings, n∈{2,3,4}: draws==0, both==0, Red==Blue==2^(n²−1), Fraction(Red,2^(n²))==1/2 | PASS — 16→8, 512→256, 65536→32768 |
| G2 | AGREEMENT \|z\|<3 | MC fair fill n=11, N=120000: z of Red-wins vs N/2 | PASS — z=−0.826, p̂=0.498808, draws==both==0 |
| G3 | INVARIANT + AGREEMENT | draws==both==0 across n∈{5,7,9,11}×p∈{3/10,1/2,7/10}; complement symmetry P(Red\|p)+P(Red\|1−p)≈1 | PASS — all draws 0; symmetry z ∈ {−0.776, 0.179, −0.585, −0.480} |
| G4 | REJECTION \|z\|>6 | square (4-neighbour) lattice draws while hex does not; naive "hex draws at square rate" | PASS — square_draws=63128 (q=0.526), hex_draws=0, z=−364.97 REJECTED |

**Teeth read:**
- G1 is a zero-slack integer / Fraction equality over the complete colouring space — the exact core.
- G2 confirms the exact 1/2 survives at the standard 11×11 board under sampling.
- G3 shows the no-draw invariant is size- and density-independent and ties the 1/2 to the transpose-swap symmetry at p≠1/2.
- G4 is the falsifiability tooth: the never-draw property is *not* generic to planar connection games — drop the two diagonal hex neighbours and draws reappear at q≈0.53, rejecting the naive claim at 365σ.

## 5. Grounding

Pins English Wikipedia "Hex (board game)" oldid 1361476133 (2026-06-28T04:20:21Z), raw-wikitext sha1 `7a7263dbf907f9d92011cf4b8f2af614c632fa4a`. Quoted on that revision: the no-draw theorem, the first-player winning strategy, Nash's strategy-stealing argument, and the Gale-1979 Brouwer equivalence. The exact P=1/2-under-uniform-fill and the 2^(n²−1) count are DERIVED here (not stated on the page); attributed accordingly in the idea doc.

## 6. Ruling

**APPROVE.** The core identity is exactly true (exhaustive G1), reproduces byte-identically, and survives a pre-registered falsifiability gate at 365σ. Exhaustive coverage stops at n=4 by combinatorial necessity; n≥5 rests on the cited theorem plus the Monte-Carlo invariant gates — the intended division of labour. Digest `76d9a326…8ebed8`.

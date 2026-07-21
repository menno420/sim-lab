# VERDICT 256 reproduction mirror — Fibonacci nim (Whinihan's game): losing positions are exactly the Fibonacci numbers, PROPOSAL 243

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 256 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 243 (superbot-games · combinatorial game theory — Fibonacci nim P-positions are the Fibonacci numbers, optimal move is the smallest Zeckendorf summand)
**Lane:** P243 → V256 (+13 offset)
**Verifier:** `verify_243_fibonacci_nim.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 344cdaa21a550c745184aaab00951db1063f522d3fe25544738299fdf8ee7dce` — byte-identical to the idea-engine source digest.
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 EXACT identity (integer arithmetic) — a from-scratch bottom-up game oracle `win(n,cap)` over `n ∈ [1,800]` (a move takes `m ∈ 1..min(cap,n)`, `m=n` wins immediately, else the opponent faces `(n−m, min(n−m, 2m))`, the opening state is `(n, n−1)` and `n=1 → (1,0)` loses) gives `loses(n) == (n ∈ Fib)` for every `n`, mismatches = 0 (Fib built independently by integer recurrence); the constructive Zeckendorf strategy, for every winning `n`, removes the smallest Zeckendorf summand `s ≤ n−1` and leaves `win(n−s, min(2s, n−s)) == False`, zeckendorf_strategy_violations = 0 → PASS
- G2 Monte-Carlo agreement — exact P-density `p0 = |Fib ∩ [1,800]| / 800 = 14/800 = 7/400 = 0.0175`; 200 000 uniform ints in `[1,800]` classified via the DP table give `losses = 3570`, `p_hat = 0.01785`, `z = 1.19370699368`; `|z| < 3` (Z_GATE = 3.0) → PASS
- G3 invariance / robustness — (a) recomputing the oracle at a second independent horizon `N2 = 1200` reproduces the P-position set on the overlap `[1,800]` byte-identical and equal to the Fibonacci prefix, invariance_discrepancies = 0; (b) randomized-play robustness — from every winning start `n ∈ [1,800]`, `R = 40` complete games where our player picks a DP winning move and the opponent plays uniformly-random legal moves, `games_played = 31440`, `optimal_player_losses = 0` → PASS
- G4 falsifiability — the naive "P-positions are the multiples of 3" foil disagrees with the true DP outcome on 274/800 positions, `|z| = 20.413966739 ≫ 3` REJECTED; the secondary "P-positions are the powers of two" foil disagrees on 18/800, `|z| = 4.29119123911 > 3` REJECTED → PASS
- all_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

In Fibonacci nim (Whinihan 1963) — one pile of `n` tokens; the first move removes any `m` with `1 ≤ m ≤ n−1`; every subsequent move removes `1 ≤ m ≤ 2·(the number the opponent just removed)`, capped at the tokens left; the last token wins (normal play) — the player to move **loses** (the position is a P-position) if and only if `n` is a Fibonacci number (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, …). Equivalently, the first player has a winning strategy iff `n` is NOT a Fibonacci number, and the optimal winning move from any non-Fibonacci `n` is to remove the **smallest Fibonacci summand of n's Zeckendorf representation** (the unique representation as a sum of non-consecutive Fibonacci numbers), which is always legal (`≤ n−1`) and always leaves the opponent a P-position. Two naive rivals are shown false on the same evidence: "P-positions are the multiples of 3" (274/800 disagreements, rejected at `|z| ≈ 20`) and "P-positions are the powers of two" (18/800 disagreements, rejected at `|z| ≈ 4.3`).

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/superbot-games/verify_243_fibonacci_nim.py` (verifier file sha256 `d290db491e1f85827641c112bc98b33fc247f675d729fad094da37abb16c3350`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. The hashed results payload is a pure function of SEED and the module constants (the game oracle is deterministic integer arithmetic; the Monte-Carlo and randomized-play consume their own `random.Random(SEED)`-seeded streams in a fixed order; exact rationals serialize via `str(Fraction)` and every float via a fixed format string; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revisions (Fibonacci nim, oldid 1341159330; Zeckendorf's theorem, oldid 1344127047) and the quoted/derived split live with the source PROPOSAL 243, and the canonical grounding review belongs to the coordinator-driven VERDICT 256 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 256 slice, not here._

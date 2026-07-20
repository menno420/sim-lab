# VERDICT 228 — PROPOSAL 215 (Stackelberg commitment / first-mover advantage in a linear-demand quantity duopoly)

**Ruling: APPROVE**

Reproduced byte-exact; all four pre-registered gates independently confirmed each in its own direction; determinism holds in-process and cross-invocation.

Headline: commit publicly to an output you can never revise and the linear-demand duopoly pays you strictly more than moving simultaneously. With inverse demand `P(Q)=A−Q`, symmetric marginal cost C and `m=A−C>0`, a Stackelberg leader who publicly and irrevocably commits earns `π_leader = m²/8`, strictly above the simultaneous-move Cournot payoff `π_cournot = m²/9` (follower `= m²/16`), so the commitment advantage `π_leader − π_cournot = m²/8 − m²/9 = m²/72 > 0` for every market size m>0. The folk "keep your options open; moving first only leaks your hand" intuition is exactly wrong: the value comes precisely from the INABILITY to revise — a credible irrevocable commitment shapes the follower's best response in the leader's favour. On the pinned world A=12, C=0 (m=12): leader=18, cournot=16, follower=9, advantage=2. The closed forms equal exhaustive integer best-response enumeration exactly, the advantage survives a noisy follower at z≈105σ (and z≈209σ on a scaled world), it holds under scaled and cost-shifted worlds, and the static-follower accounting that ignores the reaction is correctly rejected and would flip the sign.

Verified 2026-07-20T14:32Z (`date -u`).

## Reproduction
- Source verifier: idea-engine `ideas/superbot-games/stackelberg_commitment_advantage.py`, copied **byte-identical** (`diff` source↔copy exit 0) to `sims/verdict-228-stackelberg-commitment/stackelberg_commitment_advantage.py`.
- SEED=20260717, stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions.Fraction`).
- `results_sha256 = f6fdd85e2c22a1d49be9af6bd7479ab2e59869be818e1c451d1ca40caba6fb7b` — **FULL-64 EXACT** match to the disclosed PROPOSAL 215 digest (64 hex chars, exact string compare, no truncation; printed by the verifier AND independently `grep`-extracted identical).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`); the dict carries no hash of itself; `main()` builds the results twice in-process and asserts byte-identical serializations before hashing. Nothing is written to disk.

## Determinism
- In-process double-build guard: `main()` runs `build_results()` twice and asserts `canonical(r1) == canonical(r2)` before hashing; the run exits 0, so the assert held.
- Cross-invocation: two separate processes produced byte-identical stdout (`diff run-stdout.txt run2.txt`, exit 0) and the same full-64 digest — three runs total agree.

## Gate evaluation (each read in ITS OWN direction, against the proposal's OWN criteria)

- **G1 — SIGNIFICANCE (noisy-follower realized advantage over Cournot, mean>0 ∧ z≥+3σ) — PASS.** Against an ε-noisy (boundedly-rational) follower that deviates uniformly by {−2,−1,0,+1,+2} units from its best response, the leader's REALIZED commitment payoff still beats the Cournot payoff on average: `mean_gap = 1.99223 ≈ m²/72 = 2`, `z_vs_0 = 105.045621` (≫3σ). Direction: upper-tail, mean>0 AND z≥+Z_GATE — a mean at or below zero, or z<3, FAILS. The advantage is not a knife-edge artifact of a perfectly-rational follower; it survives bounded rationality.
- **G2 — EXACT (closed form == exhaustive integer-grid enumeration, then leader>cournot) — PASS.** On the pinned world A=12,C=0 exhaustive backward-induction enumeration (leader over the integer grid 0..48, follower playing its exact-Fraction best response to each committed quantity) gives leader profit `18 == 144/8 = m²/8`, Cournot pure-Nash profit `16 == 144/9 = m²/9`, follower profit `9 == 144/16 = m²/16` EXACTLY (Fraction), and `18 > 16` strictly. Direction: `==`, `==`, `==`, then `>` — any inequality or mismatch FAILS. The closed form is not an approximation of the enumeration; it IS the enumeration, certified to the bit.
- **G3 — ROBUSTNESS / SHIFT (exact result and advantage persist across worlds, MC advantage on scaled world) — PASS.** The scaled world (A=24,C=0→m=24) gives leader `72 == 576/8`, cournot `64 == 576/9`, follower `36 == 576/16` exactly with leader>cournot, and the cost-shifted world (A=15,C=3→m=12 identical to the pinned world, demonstrating only m matters) reproduces leader 18/cournot 16/follower 9 exactly. The scaled-world Monte-Carlo advantage persists: `mean_gap = 7.94882 > 0`, `z_vs_0 = 209.424945 ≥ 3σ`. Direction: exact `==` and `>` on both shifted worlds AND MC mean>0 with z≥+Z_GATE. Only m=A−C drives the result; the level of A and C independently does not.
- **G4 — FALSIFIABILITY (a deliberately-wrong static-follower accounting is REJECTED, on the wrong side) — PASS.** The naive static-follower accounting — pricing the leader's commitment as if the follower ignored it and kept its Cournot quantity — yields leader profit `12`, which is NOT the true best-response value (`12 ≠ 18` → wrong rejected) and in fact sits BELOW Cournot (`12 < 16 < 18`), so ignoring the follower's reaction is correctly rejected and would FLIP the sign of the advantage. Direction: `wrong ≠ true` (rejected) AND `wrong < cournot < true`. The gate can fail (a wrong model that happened to conserve the sign would not falsify), so passing is informative — the whole premium lives in the follower's reaction, not in a static reallocation.

`all_pass = true`, `first_failing_gate = null`. The counterintuitive head — commitment value IS the inability to revise, worth exactly m²/72 over simultaneous Cournot — holds under zero-tolerance Fraction/integer-exact enumeration (G2/G3, self-certifying) and is corroborated on ε-noisy Stackelberg worlds where the advantage clears +3σ by two orders of magnitude (G1: z≈105, G3: z≈209) while the sign-flipping static-follower model is falsified (G4).

### Observed vs disclosed (all match)
| Quantity | Disclosed / expected | Observed |
|---|---|---|
| results_sha256 | f6fdd85e…fb7b | f6fdd85e…fb7b (full-64) |
| pinned leader profit | m²/8 = 18 | 18 (144/8) |
| pinned cournot profit | m²/9 = 16 | 16 (144/9) |
| pinned follower profit | m²/16 = 9 | 9 (144/16) |
| pinned advantage | m²/72 = 2 | 2 (144/72) |
| G1 mean_gap (≈m²/72) | ≈2 | 1.99223 |
| G1 z_vs_0 (≥3σ) | ≥3 | 105.045621 |
| G2 leader==m²/8, cournot==m²/9, follower==m²/16, leader>cournot | true | true |
| G3 scaled leader / cournot | 72 / 64 | 72 / 64 |
| G3 cost-shift m (A=15,C=3) | 12 | 12 (leader 18) |
| G3 scaled MC z_vs_0 | ≥3 | 209.424945 |
| G4 wrong static leader profit | 12 (≠18, <16) | 12 |
| all_pass | true | true |
| first_failing_gate | null | null |

## Independent check
An independent Fraction-based recomputation agrees on every gate: leader `m²/8 = 18` > cournot `m²/9 = 16` > follower `m²/16 = 9`, advantage `m²/72 = 2`; and the falsifiability ordering `12 < 16 < 18` confirms the static-follower accounting flips the sign.

## Grounding (honest)
Grounding source: Wikipedia "Stackelberg competition", oldid 1365066831, raw-wikitext sha1 `36004d1bfd7d09b149e3a78e4ea3f6bea0da4f06`, re-verified via `action=raw` (EXACT match). On-page firsthand (CONFIRMED present): the leader-follower subgame-perfect Nash equilibrium, backward induction, the commitment claim that the "inability to revise allows higher profits than Cournot", first-mover advantage, and a worked linear-demand example. The verifier's OWN work (CONFIRMED absent from the page): the exhaustive integer best-response enumeration, the exact-Fraction closed-form check, the noisy-follower significance test, the two-world robustness sweep, and the falsifiability rejection of the static-follower model. The proposal's caveat HONESTLY describes what the page does and does not carry — this supports APPROVE.

## Decision
All four gates pass in their stated directions; the full-64 digest matches the disclosed value exactly; determinism holds in-process (double-build assert) and cross-invocation (byte-identical stdout, three runs). **VERDICT 228 = APPROVE** (P215 → V228, +13 offset, lane GAME — the game slice of the round-51 cycle).

Offset note: PROPOSAL 215 → VERDICT 228 (+13).

Context note: this is the disclosed COMPLEMENT of the Penney/Efron result (VERDICT 204) where committing first LOSES — a different game structure (nontransitive sequential choice vs. quantity commitment with a reacting follower), not a contradiction. Whether moving first helps or hurts is a property of the game, not a universal law.

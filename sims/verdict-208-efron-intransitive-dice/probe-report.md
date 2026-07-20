# VERDICT 208 — PROPOSAL 195: Efron's intransitive dice

**Ruling: APPROVE (clean)**

_Probe run: 2026-07-20T03:51:19Z (UTC)._

## Target
PROPOSAL 195 (idea-engine, superbot-games lane), landed on origin/main: claim PR #723 → 0d7094b; proposal PR #725 → 387f937. Verifier `ideas/superbot-games/intransitive_efron_dice.py` copied byte-identical into `sims/verdict-208-efron-intransitive-dice/`.

## Head
Bradley Efron's four fair d6 — A(4,4,4,4,0,0), B(3,3,3,3,3,3), C(6,6,2,2,2,2), D(5,5,5,1,1,1) — form an intransitive cycle A≻B≻C≻D≻A in which each cyclic arrow is won by the earlier die with probability EXACTLY 2/3 (24 of 36 face pairs, zero ties), and the reverse of each arrow is exactly 1/3. The two non-cyclic pairs are asymmetric-but-not-cyclic: C beats A at 5/9 (A over C 4/9), and B vs D is a fair 1/2. "Beats more than half" is a directed 4-cycle → no maximum element, no best die; committing FIRST is the losing role because the die just before your choice in the cycle beats it 2:1.

## Reproduction
- Verifier copied byte-identical: `diff` source-vs-copy exit code **0**; stdlib-only (random, math, json, hashlib, fractions); SEED=20260717; process exit 0. Full stdout in `run-stdout.txt`.
- results-dict sha256 = `2dcf880be80df99fc6b30c63a3ff0682831cfbe34c4f3b41b48b984bb0f6d183` — **MATCHES** the disclosed PROPOSAL 195 digest across all 64 hex characters (independent recompute via `json.dumps(results, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`, exact-string assertion passed; on-stdout exact-string grep count = 1, no truncation).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS the digest (the digest is not a field of the hashed dict). all_pass=true, first_failing_gate=null.

## Determinism
- In-process: `main()` computes the dict twice and asserts `json.dumps(...sort_keys=True)` equality ("non-deterministic" guard) — passes (exit 0).
- Cross-invocation: two separate `python3` invocations produced byte-identical stdout (`diff` exit **0**) and the identical digest `2dcf880b…f0f183`.

## Gate evaluation (against the proposal's own criteria, z_gate = 3.0)

### G1 — statistical (≥3σ single-roll Monte-Carlo, T=200,000): **PASS**
Four cyclic MC winrates vs 0.5, all > 0.5, min z = **148.519635 ≥ 3**:

| pair | mc_winrate | z_vs_half | exact | dev_from_exact |
|------|-----------|-----------|-------|----------------|
| A>B | 0.66705 | 149.414062 | 2/3 | 0.000383 |
| B>C | 0.66855 | 150.755703 | 2/3 | 0.001883 |
| C>D | 0.66605 | 148.519635 | 2/3 | 0.000617 |
| D>A | 0.666475 | 148.899767 | 2/3 | 0.000192 |

min z = 148.519635 (matches disclosed ~148.52); all_above_half=true.

### G2 — exactly-true (zero-tolerance exact-Fraction enumeration): **PASS**
Verifier's exhaustive 36-pair `fractions.Fraction` matrix, cross-checked by an **independent** from-scratch Fraction enumeration written for this probe (dice redefined, all 36 ordered face pairs per die pair):

- Cyclic edges P(A>B)=P(B>C)=P(C>D)=P(D>A) = **2/3** exactly, tie-prob = **0** on all four; reverse each = 1/3.
- cycle A≻B≻C≻D≻A holds (each cyclic > 1/2, reverse < 1/2).
- Non-cyclic: **C-over-A = 5/9**, A-over-C = 4/9, **B-vs-D = 1/2** (both directions), no ties.
- MC agrees with exact within EXACT_TOL: max_mc_dev_from_exact = **0.001883 ≤ 0.01**.

Independent enumeration reproduced every rational exactly (2/3 cyclic / 0 ties / 5/9 C-over-A / 4/9 A-over-C / 1/2 B-vs-D) — G2 is a self-certifying exact proof, not a sampled estimate.

### G3 — robustness/shift (best-of-k majority amplification): **PASS**
Exact best-of-k min cyclic win-prob is strictly monotone increasing in k and stays > 1/2 at every k:

| k | min_winprob | min_margin | all_above_half |
|---|-------------|-----------|----------------|
| 1 | 0.666667 | 0.166667 | true |
| 3 | 0.740741 | 0.240741 | true |
| 5 | 0.790123 | 0.290123 | true |
| 7 | 0.826703 | 0.326703 | true |

cycle_persists_all_k=true, monotone_in_k=true; seeded MC best-of-7 z per cyclic pair [292.119921, 292.401665, 292.236196, 292.222780], **min z = 292.119921 ≥ 3** (matches disclosed ~292.12). The paradox is not a single-roll artefact — it survives and strengthens under longer matches.

**all_pass = true, first_failing_gate = null.**

## Grounding
Wikipedia "Intransitive dice" revision **oldid 1357047248** fetched raw (`?action=raw`) this session: **HTTP 200**, 33840 bytes, raw-wikitext sha1 = `b3fdd4b02fcf23195db6e6d217d34ef5b394a5c7` — **byte-exact match** to the disclosed pin. The § Efron's dice section states the die faces verbatim (A: 4,4,4,4,0,0 · B: 3,3,3,3,3,3 · C: 6,6,2,2,2,2 · D: 5,5,5,1,1,1) and asserts the head verbatim: "Each die is beaten by the previous die in the list with wraparound, with probability 2⁄3. C beats A with probability 5⁄9, and B and D have equal chances of beating the other." The pinned revision resolves AND supports the head, and the pin is byte-verifiable — a clean external, byte-pinned citation.

## Ruling: APPROVE (clean)
The head is correct and non-trivial (a directed 4-cycle in "beats-more-than-half", each edge exactly 2/3, no maximum element, first-mover a 2:1 losing role). All three pre-registered gates PASS in order by the proposal's own criteria; G2 is an exact self-certifying enumeration independently reproduced this session; the disclosed results-dict digest matches byte-identically across all 64 hex; output is deterministic in-process and cross-invocation; and the external Wikipedia citation is byte-exact-pinned and states the head verbatim. No model choice or sampling flips a gate. Offset note: PROPOSAL 195 → VERDICT 208 (+13).

📊 Model: Claude Opus · effort high · task-class verdict-reproduction

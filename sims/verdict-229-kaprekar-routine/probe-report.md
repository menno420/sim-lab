# VERDICT 229 — Probe report (reproduces PROPOSAL 216)

> Kaprekar's routine funnels every 4-digit number with at least two distinct
> digits to the single constant 6174 in at most 7 steps. The digit map
> D(n) = desc(n) − asc(n) is a global contraction onto one absorbing state,
> not a scrambler.

- **Slice:** round-51 UNRELATED, P216 → V229 (+13 offset)
- **Branch:** `claude/verdict-229-kaprekar`
- **Sim dir:** `sims/verdict-229-kaprekar-routine/`
- **Reproduced:** 2026-07-20T15:05:32Z
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of `idea-engine/ideas/fleet/kaprekar-constant-universal-funnel-2026-07-20.py`
→ `sims/verdict-229-kaprekar-routine/verifier.py`; `diff` source ↔ copy exit **0**
(byte-identical). Stdlib-only (`hashlib`, `json`, `fractions`). SEED = 20260717,
N_MC = 200000, null p0 = 99/100.

## 2. Digest — full-64 EXACT match

Ran `python3 verifier.py` (exit 0). Printed:

```
results_sha256=6ef877698bbb91eadffa8473c4a0ec6276f62fd3b8af73fd90855288b38ebf0d
```

- Disclosed target: `6ef877698bbb91eadffa8473c4a0ec6276f62fd3b8af73fd90855288b38ebf0d`
- Independently grep-extracted from `run-stdout.txt`, exact 64-char string compare → **MATCH** (printed digest is exactly 64 hex chars; no truncation).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical results dict's own sha256 IS the digest; the dict carries no hash of itself.

## 3. Determinism — both legs hold

- **In-process double-run:** the verifier builds the results dict twice and prints `determinism_double_run=True` (digest equality asserted before exit 0).
- **Cross-invocation:** a second separate process `python3 verifier.py > /tmp/rerun2.txt`; `diff run-stdout.txt /tmp/rerun2.txt` exit **0** (byte-identical stdout across separate process invocations). No wall-clock or OS randomness; the seeded draws use a fixed-constant LCG.

## 4. Gates — independent re-derivation (fresh Kaprekar implementation)

`independent-probe.py` carries its OWN from-scratch Kaprekar step (it does NOT
import `verifier.py`) and re-derives every gate. Observed values:

| Gate | Direction | Independently observed | Pass |
|------|-----------|------------------------|------|
| **G1** exhaustive + falsifiability | nonconverge==0 ∧ max_steps==7 (and "≤6" must be FALSE) | input_count=**8991**, nonconverge=**0**, max_steps=**7**, inputs_needing_exactly_7=**1980**, wrong_bound_≤6_is_FALSE=**True** | ✅ |
| **G2** unique fixed point | fixed_points == [6174] | non-repdigit 4-digit fixed points = **[6174]** | ✅ |
| **G3** Monte-Carlo significance | successes==200000 ∧ z≥3 | n_draws=**200000**, successes=**200000**, z=**44.946657** (parsed from run-stdout.txt) | ✅ |
| **G4** dimension-shift | nonconverge==0 ∧ fixed_points==[495] ∧ max_steps==6 | input_count=**891**, nonconverge=**0**, fixed_points=**[495]**, max_steps=**6** | ✅ |

All four gates PASS in their own directions. The G1 falsifiability leg is
load-bearing: exactly **1980** of the 8991 inputs require the full 7 steps, so
the deliberately-wrong tighter bound "≤6" is genuinely rejected by data, not by
construction. The verifier's own `sim_ready=true` and `wrong_bound_max6_rejected=true`
agree.

## 5. Grounding — byte-pinned, sha1 3-way match

- Source: Wikipedia "Kaprekar's routine", oldid **1364472561**, `action=raw` wikitext.
- Independently computed sha1 = `9190b7328602bbc2de0eaad722e5bba4218d8c5b` = disclosed sha1 → **3-way MATCH** (disclosed == fetched-raw == independently computed; 16893 bytes).
- On-page content confirmed by grep (all three present):
  - `6174` — present (13 occurrences), stated as Kaprekar's constant / fixed point.
  - `within seven iterations` — present: *"Any four-digit number (in base 10) with at least two distinct digits will reach 6174 within seven iterations"* (cited to Hanover 2017).
  - `495` — present (8 occurrences): *"the Kaprekar's constants are limited to two numbers, 495 (3 digits) and 6174 (4 digits)"* (Prichett et al. 1981).

### Grounding-accuracy assessment (per the V222 grounding-scrutiny lesson)

The proposal's caveat is **honest and accurate — neither oversold nor
undersold.** It does not undersell: it explicitly acknowledges that the pinned
revision literally states the 6174 constant, the "within seven iterations"
bound (attributing it to Hanover 2017), and the 495/6174 base-width limitation
(Prichett et al. 1981) — so it never falsely claims the page lacks content it
in fact has. It does not oversell: it does not claim the ≤7-step bound is a
novel discovery, but correctly distinguishes "the page asserts the bound by
citation" from "the verifier proves that exact ≤7-step bound firsthand by
exhaustive enumeration over all 8991 inputs" — a legitimate distinction, since
the page's bound is an appeal to a cited source whereas the verifier's is a
firsthand exhaustive proof (and the verifier additionally proves the ≤6-step
3-digit bound the same way). Unlike V222, where the disclosed caveat
mis-described its source and forced a QUALIFIED ruling, here the caveat matches
the pinned revision exactly, so no correction is required.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256
full-64 EXACT match; determinism holds on both the in-process double-run and the
separate cross-invocation legs; all four pre-registered gates (G1 exhaustive +
falsifiability, G2 unique fixed point, G3 Monte-Carlo ≥3σ, G4 dimension-shift)
independently re-derived and PASS in their own directions; grounding sha1 is a
3-way match with all three content claims literally on-page; and the grounding
caveat is honest (correctly distinguishing cited-bound from firsthand-exhaustive-
proof without over- or under-selling). No qualification required.

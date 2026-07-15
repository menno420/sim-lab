# verdict-089 — the check-digit transposition floor (INTAKE 076)

Prices idea-engine PROPOSAL 076's folk belief exactly where it lives:
"slap a check digit on it and typos are handled — any standard scheme
catches the errors that matter, and the newer standard is at least as
strong as the one it replaced." Three exact structure theorems carry the
verdict, every one re-derived from scratch here: **T1 — the FLOOR**: no
position-wise mod-10 scheme (sum sigma_i(d_i) = 0 mod 10, each sigma_i a
digit permutation — Luhn, plain weights, and every mixture) catches every
adjacent swap, by a ONE-LINE certificate (the ten boundary differences
tau(y) = sigma_i(y) − sigma_{i+1}(y) sum to 0 mod 10, while an injective
tau — a permutation — would sum to 45 ≡ 5; 0 ≠ 5) gated beside its own
EXHAUSTIVE confirmation: the complete census of all **3,628,800** quotient
permutations has min undetected ordered pairs = **2**, attained by
**46,400** quotients, no U = 0 bin anywhere — and **Luhn sits ON the
floor** (its miss set is exactly {(0,9),(9,0)}; there is nothing to
tune). The best all-singles LINEAR scheme misses 10 — 5× the nonlinear
floor. **T2 — the MIGRATION REGRESSION**: ISBN-10 (mod 11) censuses
**0** undetected singles and **0** undetected transpositions at EVERY
distance; its 2007 replacement EAN-13 (weights 1,3) misses **10/90** per
adjacent boundary and **90/90** at distance 2 — 120 + 990 escape
patterns over the full 13-digit code where the code it replaced had
zero. **T3 — the EXITS are real**: the pinned Damm quasigroup table
passes all three property gates and scores **0/900 + 0/900** on the same
ten digits (the barrier is the abelian-linear algebra, not the
alphabet; distance-2 honesty row 958/9000, reporting), and the 11-ary
mini-code word-enumerates to 1331/0/0. All decision arithmetic is
seedless exact integer counting (REJECT checked first). The runner is
hermetic — it reads ONLY `fixtures.json` (committed before the runner);
this head is FULLY HERMETIC at the model level too (every constant
invented-but-pinned in the idea file — no external repo to re-verify).

## Run

```
python3 sims/verdict-089-check-digit-transposition-floor/check_digit_transposition_floor_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~6 s (the 10!
census is the only heavy leg, ~3 s; everything else is ≤ 10^5 ops).
Every decision number is an exact small integer; the seeded Arm R
carries no statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 076 block / idea file (the Luhn fold, the Damm table, the
  ISBN-10/EAN-13/ALL-ONES/word-scheme pins, the twelve F3 census
  anchors, the four typed must-equal contacts + the disclosed drafting
  correction, the three pencil worlds, degeneracy controls, Arm-R
  parameters and seeds 20261680–683, the decision rule, the three
  registered margin-ledger equality cells). Two sim-chosen values
  disclosed as vacancies: the 6-permutation spot set (registered by
  size only) and the Arm-R per-episode draw order.
- `check_digit_transposition_floor_sim.py` — the three-arm runner
  (A seedless exact censuses / B independently-written word-level twin
  + reduced-census twin / R seeded reporting).
- `results.json` — canonical machine-readable outputs (sorted keys, no
  timestamps): the complete U histogram (both the full 10! census and
  the twin's 9! slice), every census, the word-level tables, the typed
  contacts, the margin ledger, the structured anomaly census, the seed
  registry.
- `run-stdout.txt` — the accepted run's stdout.
- `REPORT.md` — the ruling against the pre-registered bands, the
  numbers, the margin ledger, falsifiability, and the consequence
  hand-off.

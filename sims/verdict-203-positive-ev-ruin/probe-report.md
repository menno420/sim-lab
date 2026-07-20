# VERDICT 203 — positive-EV ruin (ergodicity): reproduce PROPOSAL 190

**Ruling: APPROVE (clean).** A repeated multiplicative bet with strictly positive
expected value (Peters coin: heads ×1.5 / tails ×0.6, each p=0.5 → ensemble
expected multiplier 1.05 = +5% EV) drives the TYPICAL investor toward ruin
because the TIME-AVERAGE (geometric) growth is negative (√0.9 = 0.9486832981 =
−5.27%/round). Reproduced byte-identically under SEED=20260717; the disclosed
results-dict sha256 matches across all 64 hex; all four of the proposal's own
gates PASS in order (≥3σ + robustness); determinism holds; grounding resolves.

## Reproduction — byte-identical verifier

- Source: idea-engine `ideas/venture-lab/positive-ev-time-average-ruin.py`,
  landed via PROPOSAL 190 squash @45ad3eb (main PR #705; claim PR #703 → 138835a).
- Copied byte-identically into `sims/verdict-203-positive-ev-ruin/positive-ev-time-average-ruin.py`:
  `diff` source↔copy exit 0; file sha256 `94d90595d7ab5e93ba7c0d235933cc0ca5c6d321dca055e4fbb239e5a24e777e`;
  git blob `2915195f628a7a13c99905a0cfa145424645a4ec` — identical to the source blob.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (compact-canonical
  results dict's own sha256 IS the digest, not a field inside it; stdout dump is
  pretty indent=2, hashed payload compact, floats 10 dp).

## Digest — full-64 MATCH

- Reproduced results-dict sha256 = `8d04b241d3589e2e49337c087da623d73c47dbe84074eaf5596bfa39db3c5336`.
- Disclosed (PROPOSAL 190) sha256 = `8d04b241d3589e2e49337c087da623d73c47dbe84074eaf5596bfa39db3c5336`.
- **MATCH across all 64 hex** — exact-string byte-grep of `run-stdout.txt` returns
  count 1 (no truncation, disclosed digest not "corrected"). An independent
  JSON-canonical recompute (`json.dumps(compute(), sort_keys=True, separators=(",",":"))`
  → sha256) reproduces the same 64 hex.

## Gates — all four PASS in order (measured vs disclosed, base + shift worlds)

Criteria are the proposal's own (≥3σ one-sided per signed gate; G4 = robustness
shift world U=1.6 / D=0.55 preserving all three signs at z≥3).

| Gate | Signal | Measured | ≥3σ? | Disclosed z | Result |
|------|--------|----------|------|-------------|--------|
| G1 time-avg growth < 0 (base) | mean_time_avg_growth = −0.0527741776 | z = 163.2077618449 | yes | 163.2077618449 | **PASS** |
| G2 arithmetic per-round EV > 0 (base) | mean_per_round_simple_return = 0.04990775 | z = 156.8448905713 | yes | 156.8448905713 | **PASS** |
| G3 majority ruined (base) | frac_below_start = 0.8623 (> 0.5) | z = 102.4739147296 | yes | 102.4739147296 | **PASS** |
| G4 robustness/shift world (U=1.6, D=0.55) | mean_time_avg_growth = −0.0632973382 (<0); mean_per_round_simple_return = 0.075609 (>0); frac_below_start = 0.8627 (>0.5) | z_timeavg = 169.6825537139, z_ev = 203.6710827592, z_below = 102.5870518145 | all yes | 169.6825537139 / 203.6710827592 / 102.5870518145 | **PASS** |

all_pass = **true**, first_failing_gate = **null**. Every disclosed z reproduced
to the last digit. Supporting base-world statistics: ensemble_expected_multiplier
1.05, geometric_per_round_multiplier 0.9486832981, mean_final_wealth 55.6049183908
(positive-EV tail confirmed), median_final_wealth 0.0051537752 (typical path
near-ruined), frac_ruined_10pct 0.75635.

## Determinism — confirmed three ways

1. In-process double-run: the script asserts `canonical(r1)==canonical(r2)` and
   prints `double_run_identical=true` (fresh `random.Random(SEED)` per full run).
2. Separate cross-invocation: a second `python3` invocation → `diff` against
   `run-stdout.txt` exit 0 (byte-identical stdout).
3. Independent canonical recompute reproduces the exact disclosed digest.

## Grounding — pin resolves, corroborated

- Pin: `https://raw.githubusercontent.com/elemer1/elemer1.github.io/def46918c26483bdd11580bc0851956536306c56/_markdown/The%20Barrier%20that%20Moved.md`
  (40-hex commit `def46918…306c56`, raw-file-at-SHA). Resolved live this session
  HTTP 200. The essay carries the exact claim verbatim: "If the coin comes up
  heads, I multiply your wealth by 1.5 … If it comes up tails, I multiply your
  wealth by 0.6", "½ × 1.5 + ½ × 0.6 = 1.05", "1.5 × 0.6 = 0.9 … costs you ten
  percent", and independently reproduces the simulation numbers — "eighty-six
  percent … ended with less than they started, and the … median fate … finished
  holding 0.0051 of their stake" (matches the verifier's frac_below_start 0.8623
  and median_final_wealth 0.0051537752).
- REST route: `https://api.github.com/repos/elemer1/elemer1.github.io/commits/def46918…`
  ALSO resolved HTTP 200 this session (real commit metadata, dated 2026-06-05,
  message "Fix currency $ signs rendered as MathJax…"). The proposal's disclosed
  caveat ("REST API may be 403 → verify via raw-file fetch") is therefore FAIR
  and conservative: raw-file-at-SHA is a valid pin-verification route, and here
  BOTH routes resolved — no defect.
- Corroboration: Wikipedia "Ergodicity economics"
  (`https://en.wikipedia.org/wiki/Ergodicity_economics`) resolved HTTP 200 —
  "heads, the person gains 50% … tails, the person loses 40%", "E[x(t+δt)] =
  1.05x(t)", and "over time, with probability one, wealth _decreases_ by about
  5% per round, in contrast to the increase by 5% per round of the expected
  value". Supports E[m]=1.05 vs E[ln m]<0 (broken ergodicity) exactly.

## Ruling — APPROVE (clean)

The positive-EV-ruin / ergodicity head reproduces exactly: a strictly positive
per-round arithmetic EV (+5%) coexists with a strictly negative time-average
(geometric) growth (−5.27%/round), so the ensemble mean final wealth rises
(~55.60, carried by a vanishing lucky tail) while the median collapses (~0.00515)
and 86.23% of paths finish below their starting stake. All four of the proposal's
own gates pass their criteria in order with z-scores reproduced to the last
digit; the disclosed results-dict digest matches to the byte with an independent
recompute confirming it; determinism holds across the in-process double-run and a
separate cross-invocation; and the grounding pin resolves (via both raw-file-at-SHA
and REST) with Wikipedia corroboration. No model choice flips a gate sign or the
order-of-magnitude — the shift world is a genuine robustness check, not a
sign-rescuing knob → clean APPROVE. The disclosed REST-403 → raw-fetch caveat is
fair. Full stdout: `run-stdout.txt`.

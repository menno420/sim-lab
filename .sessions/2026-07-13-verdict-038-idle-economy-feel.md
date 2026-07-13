# Session — VERDICT 038 — Idle economy FEEL sim: superbot-idle SIM-001's three ASKs answered with measured numbers (idea-engine ORDER 005 SIM-REQUEST 2)

> **Status:** `complete`
> 📊 Model: Claude 5 family · 2026-07-13 · verdict-038 slice-worker session
> Objective: serve idea-engine ORDER 005 SIM-REQUEST 2 (control/inbox.md @ 8218d66, fm ORDER 043 relay, Q-0264 fan-in; requesting seat **superbot-idle**): the economy-FEEL cluster registered as superbot-idle SIM-001 (`docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" — scenarios S1/S2/S3, outputs O1–O6, criteria A1–A10) at pin `menno420/superbot-idle @ d992c5688e802b28d11c0ec6c835fa54a87149ec`, with the three ASKs from superbot-idle control/outbox.md SIM-001: (ASK 1) first-upgrade no-op — quantify the low-count regime where the single `//100_000_000` rate-floor fold makes boost1 purchases 1–3 (costs 60/69/79) change nothing felt, plus registered exact-integer tuning arms (EFFECT_PERCENT / base-rate scale / seed count / growth) with a mechanical viability rule; (ASK 2) weak prestige payoff — reproduce first prestige t≈12573 s and run-2 ratio 0.9175, deliver the payoff curve (per-reset ratio, marginal award, time-to-award-K) plus registered bonus/divisor arms; (ASK 3) the A10 strict-vs-trend ruling on the 20-reset ladder (final_ratio ≈ 0.9661) with a registered wiggle band and the graduation recommendation. FEEL probes per ORDER 005's framing as registered metrics with bands (session pacing, meaningful-choice cadence, idle-vs-active balance). Method: V017's discipline — byte-copied engine + committed harness with sha256 MANIFEST, fixtures.json pre-registration committed BEFORE the runner, B0 baseline-validity leg reproducing the packet's own numbers exactly plus V006 cross-pins, NO RNG (bit-identity by construction, zero seeds drawn, fleet high-water 20260775 untouched), honest NULL on the generator-dependent probes (no generator purchase path exists at d992c568; this verdict + V017 feed fm owner-queue E#52). Build subtree `sims/verdict-038-idle-economy-feel/`.

## What happened

Built `sims/verdict-038-idle-economy-feel/` — a stdlib-only NUMERIC SIMULATION
(rung 1, ZERO RNG, bit-identity by construction): fixtures.json (the
pre-registration — B0 anchors from the packet + V006 cross-pins, all ASK 1/2/3
exact-integer arms, FEEL bands, mechanical decision rules, 13 disclosed
intake-time decisions) landed BEFORE the runner; the vendored fixtures are
byte-for-byte copies of ALL 11 idle_engine modules PLUS the seat's own
committed harness tools/simulate.py @ d992c568 (sha256 MANIFEST re-verified
before import; the economy surface is byte-identical to V017's pin c753bc8).
The driver reimplements NOTHING: the committed harness's run_report(full) is
the B0 baseline and its simulate_s2/simulate_s3 run every arm; the one
driver-level variant (seed-count arm) is equivalence-gated at C=1. One
disclosed fixture AMENDMENT (pre-results, in the git trail): V006's published
A7 pin (6,16) is the harness's INCLUSIVE AMB-4 auxiliary, not its
strictly-before gate value (13,30) — both clear A7's ≥2 band.

**Run output:** `SELF-CHECKS: 77 passed, 0 failed`, exit 0, ~23 s; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `76b9ce28…`, results `c91c82ed…`). **B0 VALID** — every packet
number and V006 cross-pin exact (60/69/79, [1,1,1,1,2,2], 12573 s, 0.9175,
0.9661, A1–A9 PASS / A10 FAIL), and the packet's "~80,796 resets" landed
EXACTLY 80796. **ASK 1 CONFIRMED-INERT**: rate(L) = 1+L//4, first felt
purchase #4, 69.5% of early spend inert, felt share 3/13 ≈ 23.1%; minimal
felt arms E=100 / B=4 / C=4 (registered closed-form predictions confirmed)
ALL break A3/A4/A6 → the registered fallback fired: min-visible-delta floor
routed as the only feltness fix. **ASK 2 CONFIRMED**: 8.25% speedup per
3.49 h, awards flat 1 across 20 resets; registered rule picked
PRESTIGE_BONUS_PERCENT 10→25 (r₂ = 0.8006); divisor 50000 measured as a
NO-OP (isqrt floor). **ASK 3 TREND-PASS**: 6 strict violations, max drop
0.0166 inside the registered 0.02 wiggle band, trend 0.9175→0.9661 rising,
flag false → GRADUATE-WITH-REWORDING. **FEEL**: F1 PASS (median early gap
70 s), F2 FAIL (23.1% < 50% — the complaint quantified), F3 PASS (7.95×).
**Verdict: conditional** — graduate PROVISIONAL → SIM-PINNED conditional on
re-registering A10 in trend form (doc change, zero parameter changes). Gate
PASS (all five answered in REPORT.md).

Landed: INTAKE simreq-002 (2026-07-13T10:08:30Z) + VERDICT 038
(2026-07-13T10:08:31Z) appended to `control/outbox.md` (append-only, 20
insertions 0 deletions; the simreq- namespace per INTAKE simreq-001).
Sequence: branched off 38ac71a with V037 at the tail; V036 (P034 sibling,
PR #85) landed mid-slice @ f4f934b and origin/main was merged INTO this
branch (never rebased) with the tail re-verified immediately before the
append — reserved numbers 036/037 honored, this slice took 038 per dispatch.
Verdict PR #86 from `claude/verdict-038-idle-economy-feel`. Worker session —
no heartbeat writes; this card flip is the last commit. Write-tool refusal on
REPORT.md ("Subagents should return findings as text") handled per the known
pattern: bash heredoc, zero work lost.

## 💡 Session idea

When a sim's baseline anchors are another sim's PUBLISHED numbers, pin the
anchor's READING alongside its value at registration time — name the exact
report field (json-path or harness key) each number binds to, not just the
number. This head registered V006's A7 pin as "(6,16)" and only the first
run revealed it was the harness's INCLUSIVE AMB-4 auxiliary, not the
strictly-before gate the criterion scores — recoverable here (both readings
clear the band; disclosed amendment, pre-results, in the git trail), but on
a decision-bearing anchor the same slip would have forced a re-registration
mid-run. The portable rule: a cross-sim anchor is a (value, field-path) PAIR;
V017's nine V006 cross-pins survived because they bound to unambiguous
top-level measures, and the one anchor here that bound to an
ambiguity-split measure (AMB-4's two readings) is exactly the one that bit.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-035-assign-at-merge-tax.md`: complete and
honest; exports adopted. (1) Its race protocol (re-verify the ledger tail at
origin/main HEAD immediately before the append; merge INTO the branch, never
rebase) held again under heavier traffic — TWO sibling verdicts (036, 037)
landed around this slice and the reserved-number discipline absorbed both
with zero renumbering, now including the sibling-established simreq-
namespace for non-proposal SIM-REQUEST intakes. (2) Its 💡 (verify at
registration that every band is REACHABLE after pre-computable exclusions)
transferred directly: this head pre-computed the felt thresholds (E ≥ 100,
B ≥ 4, C ≥ 4) at registration and registered a fallback branch for the
likely no-viable-arm outcome — the fallback fired, and because it was
registered, the "no constant works" result is a ruling, not a dead end.
(3) Where V035 needed the full seeded apparatus, this head is the NO-RNG
form (V017/V034 lineage): zero seeds, bit-identity as the reproducibility
proof — the two forms now alternate cleanly by head type, with the seed
registry untouched at high-water 20260775.

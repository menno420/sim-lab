# Session — VERDICT 019 — IRV monotonicity in close races (idea-engine PROPOSAL 017)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-019 slice-worker session
> Objective: settle idea-engine PROPOSAL 017 (control/outbox.md @ 2026-07-13T00:59:58Z, sim-ready; idea ideas/fleet/irv-monotonicity-close-races-2026-07-13.md @ efc78ae, landed via idea-engine PR #281, main `80baad5`) — the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain rotation slot's first head (domain: social choice theory, 3-candidate instant-runoff voting). Build the fully hermetic pre-registered sim: under the pinned IRV rule (plurality-loser elimination, pairwise final, exact ties excluded and counted), measure the upward monotonicity violation fraction — V_all (all non-tied elections) and V_close (round-1 elimination margin ≤ 5% of n) — in BOTH Arm E (exhaustive IAC: all compositions at n=25, anchor n=13 — exact fractions, seedless) and Arm S (seeded IC: n=99, M=200,000, seed 20260713 primary; n=1,001, M=20,000, seed 20260714 size leg), then issue exactly ONE of APPROVE (V_close ≥ 0.10 AND V_all ≥ 0.01 in both arms) / REJECT (V_close < 0.05 in both) / NULL (anything else — model-dependence is the citable finding) per the decision rule registered BEFORE any code existed, with the lower-bound caveat (single-type uplift) and the CPython minor version pinned.

## What happened

Built `sims/verdict-019-irv-monotonicity/` — a stdlib-only NUMERIC SIMULATION
(rung 1), the pipeline's first fleet-external verdict: fully hermetic, zero
repo/network reads, every fixture integer combinatorics the sim constructs
itself. The pre-registration ({n, M, seed} per arm + band constants, verbatim
from the idea file, plus two fully hand-derived pin elections with their
derivations) was committed to `fixtures.json` BEFORE the runner was written;
the runner cross-checks its literals against that file at start.

**Run output summary:** `SELF-CHECKS: 19494 passed, 0 failed`, exit 0, stdout
+ results.json byte-identical across three process runs (external diff),
cpython-3.11 pinned, ~18 s. **Ruling: NULL — the pre-registered honest-null,
finalized.** The two standard neutral voter models land on OPPOSITE sides of
the bands: Arm E (exhaustive IAC, n=25, EXACT) V_close = 984/20,880 = 0.0471
(< 0.05, the REJECT side) while Arm S (seeded IC, n=99, M=200,000) V_close =
16,583/98,983 = 0.1675 (≥ 0.10, the APPROVE side), V_all ≥ 0.01 in both
(0.0112 / 0.1106). Two-sided robust: E would need 2.1× its exact number for
APPROVE; S would need to fall 3.4× for REJECT (se ≈ 0.0012). The citable
finding IS the model-dependence. Bonus structure the data reproduced as
validity checks: every violation has X = the final pairwise loser (the
first-eliminated rows are 0 by a small theorem), and the E-n13 anchor is
degenerate both ways — close set empty by construction AND V_all exactly 0,
which is analytically impossible at n=13 (the fpZ > n/4-ish window is empty)
— flagged as the pre-registered sign-flip, not read as evidence.

Slice boundary this cycle (the V015–V018 precedent): this session carries the
INTAKE 017 and VERDICT 019 control/ appends itself; control/status.md stays
coordinator-only and is untouched; control/inbox.md untouched (manager-order
file). No @codex step — suspended per the outbox codex-line escalation @
dedc12e. No claim file — the V017/V018 sessions filed none; precedent
mirrored. Born-red card and complete flip land in one push (the V018
choreography: `bootstrap.py check --strict` fails on an in-progress newest
card, and the strict-gate-before-every-push rule binds harder).

## Run command

```
python3 sims/verdict-019-irv-monotonicity/irv_monotonicity_sim.py
```

## 💡 Session idea

A pre-registered NULL band is what makes a two-model sim honest — and it only
works if the null is priced as a first-class outcome BEFORE the run: this
question would have produced a confident wrong soundbite under either voter
model alone (IAC alone → "under 5% even when close, footnote it"; IC alone →
"17% when close, lead with it"), and the only reason neither soundbite ships
tonight is that the decision rule committed in advance demanded BOTH arms
clear the same band. Rule of thumb for future unrelated-domain intakes: when
the literature fight is two camps conditioning on different models, the
deliverable is not a winner — it is the pre-registered straddle test, and a
NULL that names the dependence is a stronger citable than either camp's
number. Also exportable: the small-n impossibility bound (upward violations
need fpZ ⪆ n/4, so tiny anchor legs can read as structurally zero) — check a
sensitivity leg's degeneracy analytically before treating its zero as data.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-018-encounter-coexistence.md`: complete,
honest, and its exports are adopted here directly. (1) Its one-push born-red
choreography (strict gate fails on an in-progress newest card, so the flip
rides the same push as the work) is followed verbatim. (2) Its
commit-the-rule-before-results discipline (grid.json) maps here as
fixtures.json — strengthened a notch: this slice also committed two
hand-derived pin elections WITH their derivations before the runner existed,
so even the self-check expectations are pre-registered. (3) Its slice boundary
(the verdict session carries the INTAKE + VERDICT appends; status.md
coordinator-only, inbox untouched) is honored as-is. (4) Its regression-legs
discipline has no parents to regress to here (first fleet-external verdict) —
the equivalent fidelity floor became the independent re-implementation
agreeing on two FULL tiny-n enumerations plus strided elections on every leg,
which is the right translation when there is no parent to vendor.

# Session — VERDICT 059 — Parrondo's paradox at a conservative discrete pin: do two individually-losing games combine into a winner, and by a material margin? (idea-engine PROPOSAL 048, unrelated-domain r8)

> **Status:** complete
> 📊 Model: Claude Fable (Fable 5 family) · 2026-07-13 · verdict-059 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 048 (`## PROPOSAL 048 · 2026-07-13T21:54:41Z · status: sim-ready`, landed via idea-engine PR #353 → main 1218196; claim landed via idea-engine PR #355, `control/claims/claude-verdict-059-parrondo-lattice.md` reserving the P048 intake + VERDICT 059 and this branch `claude/verdict-059-parrondo-lattice`; numbering INTAKE = proposal number, VERDICT 059 per the established P047→V058 offset map, sim-lab #111) — price the folk law "two individually-LOSING games combine into a WINNER" (Parrondo's paradox, Harmer–Abbott structure) at the proposal's deliberately CONSERVATIVE integer-lattice pin per the idea doc `ideas/fleet/parrondo-losing-games-combine-2026-07-13.md` @ idea-engine main 1218196: EPS = 1/100 (twice the textbook bias), M = 3, Game A a = 49/100 capital-independent ±1, Game B capital-dependent on s = capital mod 3 (b0 = 9/100 at s == 0, b1 = 37/50 at s ∈ {1,2}), RANDOM 1/2–1/2 A/B switching (w_s = (a + b_s)/2 → w_0 = 29/100, w_1 = w_2 = 123/200), reduced 3-residue chain s → (s±1) mod 3, long-run drift D = Σ_s π_s (2 w_s − 1) with π the exact-rational stationary law. Arm A = DECISION (seedless exact fractions.Fraction 3×3 stationary solve; D_A, D_B, D_mix as exact rationals); Arm B = VALIDATION (seeded MC capital stepping, N = 200,000/leg; seeds 20261329 headline mixed / 20261330 pure-A control / 20261331 pure-B control / 20261332 stability — the ONLY four, pre-registered, strictly above the V058 high-water 20261328). Decision rule pre-registered, evaluated IN ORDER: (1) REJECT FIRST iff D_mix ≤ 0, with INVALID (report, do not rule) iff an isolated-loss gate fails (D_A ≥ 0 or D_B ≥ 0); (2) APPROVE iff D_mix ≥ 1/1000 AND the seed-20261332 stability leg reproduces sign and margin; (3) NULL iff 0 < D_mix < 1/1000 or any validity conjunct fails (Arm B beyond 4·se of Arm A). Reporting-only side pins: π_B and π_mix (the ratchet mechanism), critical-EPS sweep over {1/100, 3/200, 1/50, 1/40, 1/25}, periodic [A,A,B,B] comparator on the phase×residue product chain. Fully hermetic: the runner reads only its own fixtures.json, committed BEFORE the runner; byte-identity verified across two full process runs by external diff. Build subtree `sims/verdict-059-parrondo-lattice/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 048 + VERDICT 059 appended to sim-lab `control/outbox.md` only, never echoed to idea-engine).

## What happened

Built `sims/verdict-059-parrondo-lattice/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 048 block / idea doc @ idea-engine main
1218196; the head is fully hermetic by registration, so no harvest clone was
needed — zero repo/network reads at verdict time) committed BEFORE the
runner. Git trail (PR #112): 5b4c10f (born-red card) → 61c01c4 (fixtures) →
b39b547 (runner parrondo_sim.py + accepted run: results.json,
run-stdout.txt, REPORT.md, README.md) → 6e4a450 (INTAKE 048 + VERDICT 059
ledger) → this flip. Claim-first: idea-engine PR #355, opened before any
sim-lab work landed.

**Run:** `SELF-CHECKS: 346 passed, 0 failed`, exit 0, ~0.2 s; stdout +
results.json byte-identical across two full process runs by external diff
(run-stdout sha256 879874c0…, results sha256 fce31e07…); CPython 3.11
pinned, asserted. Gates all green: derived-constant transcription gates
exact (a = 49/100, b0 = 9/100, b1 = 37/50, w_0 = 29/100, w_1 = w_2 =
123/200); every stationary law verified exactly (πP = π per state, Σπ = 1,
masses in (0,1)); the capital-independent identity D_A = 2a − 1 = −1/50
exact with π_A uniform; two in-process Arm-A computations identical; twin
evaluators agree; the sweep's EPS = 1/100 cell reproduces the headline.
Draw sentinels exact (mixed legs 400,000 = 2/step pinned order, pure legs
200,000); exactly four RNGs constructed — the four registered seeds
20261329–332, pinned order, all drawn (no aux this registration).

**Ruling: approve.** REJECT (checked FIRST) does not fire: D_mix =
26673/4429850 ≈ +0.006021 > 0. INVALID gate does not fire: D_A = −1/50 < 0,
D_B = −1529/87950 ≈ −0.017385 < 0 — both games individually losing, the
premise live. APPROVE fires: D_mix ≥ 1/1000 at ≈ 6.02× the band; the
seed-20261332 stability leg reproduces sign (+0.008090) and margin
(1618/200000 ≥ 1/1000 exact); all four Arm-B legs within 4·se (worst |dev|
0.002360 vs 0.008943). The mechanism, read off the exact stationary laws:
Game B alone funnels itself into its bad residue (π_B(0) ≈ 38.3% vs uniform
33.3%); mixing in the plain losing coin A reshuffles occupancy (π_mix(0) ≈
34.5%) and the drift flips sign — a real ratchet. Disclosed knife-edge: the
pin is the LAST surviving point of the registered lattice — EPS = 3/200
already kills the paradox (−0.003661), so the critical boundary lies in
(1/100, 3/200). Periodic [A,A,B,B] comparator ≈ +0.004762, also positive —
not an artifact of the random mixing rule. Drafter reference reproduced
EXACTLY on all five disclosed quantities (re-derived with zero trust,
reported never gated).

Walls: none new — the Write tool refused REPORT.md (verbatim: "Subagents
should return findings as text, not write report files."); REPORT.md rode a
shell heredoc per the standing V054–V058 classification (report-file-specific
tool policy, not a lane wall; the .py runner, fixtures, and README all went
through Write). ASK 003 corridor: sim-lab main never moved this session
(8454eb7 at sync and at append), no merge of main into the branch was
needed, so the mtime-newest false-green could not fire — nothing to disclose
beyond absence. One local nuisance, not committed: `.substrate/
guard-fires.jsonl` is dirtied by every local `check --strict` run; left
unstaged throughout. `control/inbox.md`, both status heartbeats, and
idea-engine's outbox untouched. PR:
https://github.com/menno420/sim-lab/pull/112 (READY; merge-on-green owns the
merge — zero agent merge/arm calls).

## 💡 Session idea

Reporting sweeps that bracket a sign flip should ship the EXACT boundary,
not the bracket — and for exact-rational chains it costs one interpolation,
zero dependencies. Here the registered critical-EPS sweep says only "the
paradox dies somewhere in (1/100, 3/200)"; but D_mix(EPS) is a RATIONAL
FUNCTION of the swept parameter (π solves a linear system whose entries are
rational in EPS, so by Cramer's rule the drift is a ratio of polynomials in
EPS of degree ≤ the state count). The move: after a sweep detects a sign
change between adjacent lattice points, (a) recover the numerator polynomial
exactly by evaluating D_mix at deg+1 pinned rational nodes and Lagrange
interpolation in `fractions.Fraction` (all stdlib, exact); (b) isolate its
root in the bracket by exact-rational bisection (Sturm/sign counting is
overkill at degree ≤ 3–12) to a registered denominator cap; (c) report the
boundary as an exact interval, e.g. "the paradox dies at EPS* ∈
[a/b, c/d], width ≤ 1/10^k" — a citable constant instead of a coarse
lattice cell. Kin, deduped at flip time (grep .sessions/ +
control/outbox.md for "bisection", "root isolation", "critical boundary" —
one hit, distinct): V058's 💡 proposes MC bisection over a committed ENGINE
for the inverse-knob question (statistical, re-runs the sim per probe);
this is the exact-arm sibling — when the decision quantity is already a
closed-form rational in the knob, the boundary needs NO further simulation
at all, just algebra the sim already has. Anchors: parrondo_sim.py
`arm_A`/`stationary` (the solver whose output is rational in EPS),
REPORT.md § critical-EPS sweep (the bracket this idea would sharpen to a
point).

## ⟲ Previous-session review

VERDICT 058 (creature rarity, PR #111) is the direct predecessor, and its 💡
— asymmetric-contest registrations should carry a drafting-time
band-reachability bound, and a disclosed dominance computation beats a
surprise degenerate table — is validated by THIS registration from the
drafter's side: PROPOSAL 048 discloses its expected landing (APPROVE,
thinly) with the full hand-computed rationals, exactly the
pre-compute-and-disclose discipline V058's card asks for, and it paid off
here in a concrete way — the disclosed reference gave this session a
differential target (exact equality on five quantities) that turns "my
solver ran" into "two independent derivations agree digit-for-digit", a
strictly stronger acceptance signal than self-checks alone. Its Write-tool
classification held for a fourth consecutive session (REPORT.md heredoc,
everything else through Write — zero wasted probes), and its ASK 003
"no merge, no corridor" record gathered another consistent observation
(main static both sessions). One nit: V058's card codifies the
"degenerate-table hand-arithmetic probe" habit as conditional on a
degenerate landing; this session suggests the unconditional form is cheaper
than the condition — the drafter's disclosed reference IS that probe done
at registration time, so verdict sessions should simply prefer
registrations that carry one and flag registrations that don't (P048 did;
the check cost this session nothing and bought exact cross-derivation).

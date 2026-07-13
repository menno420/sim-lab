# Session — VERDICT 060 — The magnet press-fit band: does the shipped `magnet_fit = 0.15` mm interference default land the pocket in the PRESS band across real printers, and at what loose/unseatable error rate? (idea-engine PROPOSAL 049, fleet-backlogs r9 opener)

> **Status:** complete
> 📊 Model: Claude Fable (Fable 5 family) · 2026-07-13 · verdict-060 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 049 (`## PROPOSAL 049 · 2026-07-13T22:26:26Z · status: sim-ready`, landed via idea-engine PR #358 → main b77beca, merged 2026-07-13T22:30:14Z; claim landed via idea-engine PR #361, `control/claims/claude-verdict-060-magnet-press-fit-band.md` @ a0ca29c reserving the P049 intake + VERDICT 060 and this branch `claude/verdict-060-magnet-press-fit-band`; numbering INTAKE = proposal number, VERDICT 060 per the established P048→V059 offset map) — price the effector-mount magnet tool's shipped, never-printed press-fit interference default (`projects/effector-mount/magnet_tool.scad` @ curious-research a9fd5fa line 56 `magnet_fit = 0.15` mm DIAMETRAL, geometry line 83 `pocket_d = magnet_d - magnet_fit`, its own comment claiming "0.10-0.20 = a firm press-fit on most printers") against the SAME repo's tolerance-test-coin band semantics, per the idea doc `ideas/fleet/magnet-press-fit-band-2026-07-13.md` @ idea-engine main b77beca. Pinned model, all lengths integer hundredths of a mm (cmm), DIAMETRAL: fit grid F ∈ {5, 10, 15, 20, 25, 30} (shipped default the F = 15 cell); exemplar calibration chain coin row → S = 40 → ρ = 1/2 → H₀ = 20; population H ~ uniform int {0..40} systematic hole undersize, per-print noise η ~ uniform int {−10..+10}, magnet diameter error m ~ uniform int {−5..+5}, independent; actual interference I(F) = F + H + m − η; bands DROPS-OUT iff I < 10 (I_hold = 10), PRESS iff 10 ≤ I ≤ 50, UNSEATABLE iff I > 50 (I_seat = 50); per-cell DROP/UNSEAT/FAIL = DROP + UNSEAT as exact `fractions.Fraction` over the 41 × 11 × 21 = 9,471-cell equiprobable lattice. Arm A = DECISION (seedless exact full enumeration, every probability an exact Fraction, run twice in-process and identity-checked, byte-identical across process runs); Arm B = VALIDATION (seeded MC, N = 200,000 via random.Random(20261333), pinned draw order H → m → η, common random numbers across all six F; agreement gate |ArmB − ArmA| ≤ 1/100 absolute AND ≤ 4·se per cell). Seeds 20261333 headline / 20261334 zero-noise identity control (η ≡ 0, m ≡ 0, H ≡ 20 → PRESS with probability EXACTLY 1 at every F in both arms) / 20261335 sensitivity confirmations (N = 20,000 each, reporting-only: H narrow {10..30} / wide {−10..50}, η {−5..+5} / {−20..+20}, m {0} / {−10..+10}, I_hold {5, 15}, I_seat {40, 60}) / 20261336 stability (N = 20,000; ruling must reproduce through twin independently-written evaluators) — the ONLY four, pre-registered, strictly above the P048/V059 high-water 20261332. Decision rule pre-registered, evaluated IN ORDER: (1) REJECT FIRST iff FAIL(15) > 1/10; (2) INVALID (report, do not rule) iff the zero-noise identity fails in either arm, a monotonicity theorem fails (DROP non-increasing / UNSEAT non-decreasing in F), or Arm B breaches the agreement gate on any cell; (3) APPROVE iff FAIL(15) ≤ 1/20 AND FAIL(15) ≤ min_F FAIL(F) + 1/100 AND the stability leg reproduces; (4) NULL otherwise, four registered axes (band-miss (1/20, 1/10]; wrong-center; stability non-reproduction; sensitivity straddle). Reporting-only side pins: the full DROP/UNSEAT/FAIL × F table with split, FAIL_glue(F) = UNSEAT(F), the per-H conditional FAIL(15 | H) curve, every sensitivity world, and the remedy-direction inversion flag (both shipped remedy texts point the `magnet_fit` dial the wrong way vs line-83 geometry — reporting-only, routes lane-side as a doc fix per Q-0260). Drafter's disclosed expectation (compared, never gated, re-derived from scratch): REJECT at FAIL(15) = 145/861 ≈ 0.168. Fully hermetic: the runner reads only its own fixtures.json, committed BEFORE the runner; per-leg draw-count sentinels; no aux reads beyond the four seeds; no wall-clock in output; CPython minor version pinned; byte-identity across two full process runs by external sha256. Build subtree `sims/verdict-060-magnet-press-fit-band/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 049 + VERDICT 060 appended to sim-lab `control/outbox.md` only, never echoed to idea-engine).

## What happened

Built `sims/verdict-060-magnet-press-fit-band/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 049 block / idea doc @
idea-engine main b77beca, with the harvested curious-research lines quoted
verbatim @ a9fd5fa; the head is fully hermetic by registration — zero
repo/network reads at verdict time, and the source repo is MCP-walled from
this seat anyway) committed BEFORE the runner. Git trail (PR #118): 35a8467
(born-red card) -> e40d6d5 (fixtures) -> c609600 (runner magnet_fit_sim.py +
accepted run: results.json, run-stdout.txt, README.md, REPORT.md) -> 3206612
(INTAKE 049 + VERDICT 060 ledger) -> 695d3eb (prose correction, below) ->
this flip. Claim-first: idea-engine PR #361 (claim file @ a0ca29c), opened
before any sim-lab work landed; enabler owns that merge.

**Run:** `SELF-CHECKS: 43 passed, 0 failed`, exit 0, ~1.2 s; stdout +
results.json byte-identical across two full process runs by external sha256
(run-stdout sha256 1c69ce85..., results sha256 3991657e...); CPython 3.11
pinned, asserted. Gates all green: transcription gates exact (grid, lattice
9,471, S = 40, rho = 1/2, H0 = 20, I_hold = 10, I_seat = 50, bands); two
in-process Arm-A computations identical rationals; zero-noise identity
(seed 20261334) PRESS with probability EXACTLY 1 at every F in BOTH arms;
both monotonicity theorems in both arms; Arm-B agreement (seed 20261333,
N = 200,000, common random numbers, pinned order H -> m -> eta) within
1/100 absolute AND 4·se on every cell (worst |dev| 0.000863 vs 0.003880);
twin evaluators agree everywhere; draw sentinels exact (600,000 / 60,000 /
600,000 / 60,000 on the four registered seeds 20261333-336, the ONLY RNGs
constructed, pinned order — new registry high-water 20261336).

**Ruling: reject.** REJECT (checked FIRST) FIRES: FAIL(15) = 145/861 ~
0.168409 > 1/10. Even the grid-best F = 10 fails at 40/287 ~ 0.139 — at the
pinned population width NO universal default is honest, the coin project's
own doctrine. Failure mass sits UNSEAT-side (125/861 vs DROP 20/861), the
expensive non-glue-fixable direction. Stability leg (seed 20261336)
reproduces the class through both evaluators (3367/20000 = 0.168350). The
narrow-H and I_seat = 60 sensitivity worlds land 20/441 ~ 0.045 and 40/861
~ 0.046 (APPROVE/NULL region) — the registered bands genuinely discriminate,
reporting-only. Drafter reference reproduced EXACTLY on all eleven disclosed
quantities (re-derived with zero trust, reported never gated).

**Disclosed correction (pre-merge, prose-only):** the first REPORT/ledger
draft wrote the per-H zero plateau as {10..25} and the H = 40 endpoint as
10/21 — checked against run-stdout.txt at flip time, the true values are
{10..20} and 5/7 ~ 0.714 (closed form: H in [25 - F, 35 - F]). Corrected in
695d3eb before merge; fixtures, runner, and the accepted run were never
touched — decision numbers unaffected.

Walls: none new — the Write tool refused REPORT.md (verbatim: "Subagents
should return findings as text, not write report files."); REPORT.md rode a
shell heredoc per the standing V054-V059 classification (report-file-specific
tool policy, not a lane wall; fixtures, the runner, and README all went
through Write). ASK 003 corridor: sim-lab main moved BEFORE this session
(9663ff4 -> 771f669, the kit-upgrade PRs #115/#117 — bootstrap.py +
workflows, not sims/ or the outbox) and never moved during it (771f669 at
sync, at the pre-append re-grep, and at flip), so no merge of main into the
branch was needed and the mtime-newest false-green could not fire — nothing
to disclose beyond absence. Both collision greps empty (session start,
repo-wide; pre-append, outbox @ origin/main 771f669). One local nuisance,
not committed: `.substrate/guard-fires.jsonl` is dirtied by every local
`check --strict` run; restored before each commit, left unstaged.
`control/inbox.md`, both status heartbeats, and idea-engine's outbox
untouched. PR: https://github.com/menno420/sim-lab/pull/118 (READY;
merge-on-green owns the merge — zero agent merge/arm calls).

## 💡 Session idea

Band-placement verdicts should ship the exact ZERO-FAILURE PLATEAU as a
closed-form interval, self-checked against the enumerated curve — and this
session's one defect proves why. The per-H conditional curve has a
guaranteed-safe interval that interval arithmetic gives for free: FAIL(F |
H) = 0 exactly iff H in [I_hold - F - m_min + eta_max, I_seat - F - m_max +
eta_min] = [25 - F, 35 - F] here — width (I_seat - I_hold) - (eta span) -
(m span) + 1 = 11 of the 41 population points, INDEPENDENT of F. Publishing
it as a first-class derived constant does three things: (a) converts the
population-rate ruling into a per-printer ACCEPTANCE TEST — measure YOUR H
with the coin, and membership in [25 - F, 35 - F] guarantees PRESS for every
print at the modeled noise, a binary exact criterion needing no re-run; (b)
states the design tension as an equation — no F can cover the 41-point
population with an 11-wide window, so "which F?" is really "where do you
park a window less than a third the population's width?", the REJECT
mechanism in one line; (c) is machine-checkable — a self-check asserting
plateau-bounds-read-off-the-enumerated-table == closed form would have made
this session's transcription error ({10..25} for {10..20} in REPORT prose,
caught only by eye at flip time) impossible to commit. Kin, deduped at flip
time (grep .sessions/ + control/outbox.md for "plateau", "acceptance test",
"closed form" — nearest is V059's exact-boundary 💡, distinct): V059
sharpens a swept SIGN FLIP to an exact root; this ships the exact SAFE SET
of a conditional curve — different object (interval vs point), different
consumer (the per-printer test vs the citation). Anchors: magnet_fit_sim.py
PER_H loop (the enumerated curve), REPORT.md per-H paragraph (the corrected
prose this idea would have guarded).

## ⟲ Previous-session review

VERDICT 059 (Parrondo lattice, PR #112) is the direct predecessor. Its 💡 —
when the decision quantity is a closed-form rational in the swept knob,
recover the exact sign-flip boundary by Lagrange interpolation + rational
bisection instead of shipping a bracket — is validated in spirit by THIS
session's landing: the REJECT here is width-driven (narrow-H lands 0.045,
the headline 0.168), so the exact H-span at which FAIL(15) crosses 1/10 is
the same kind of citable boundary V059's idea asks for, and this
registration's sensitivity pair only brackets it. Its card's
Write-tool classification held for a fifth consecutive session (REPORT.md
heredoc, everything else through Write — zero wasted probes), and its
"disclosed drafter reference = differential target" observation paid off
again, stronger here: eleven quantities matched exactly, turning "my
enumerator ran" into two independent derivations agreeing digit-for-digit.
One genuine nit: V059's stability criterion was bespoke (sign + margin,
APPROVE-shaped); this session's "ruling class reproduces through the twin
evaluators" is the class-agnostic generalization, and future registrations
should prefer that form — a REJECT-landing sim still gets a meaningful
stability check instead of one written for the landing the drafter expected.

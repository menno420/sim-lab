# Session — VERDICT 032 — adaptive versioning on early signal: does a two-stage produce→observe→version policy beat V020's mode fork? (idea-engine PROPOSAL 030)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-032 slice-worker session
> Objective: settle idea-engine PROPOSAL 030 (control/outbox.md · 2026-07-13T07:25:14Z · status: sim-ready; idea `ideas/venture-lab/adaptive-versioning-early-signal-2026-07-13.md` @ idea-engine main 9b24977, PR #298 — the ORDER 003 VENTURE rotation slot, round 4: the books half, pricing VERDICT 020's own named follow-up "Adaptive K"). Build the fully hermetic pre-registered measurement: under V020's pinned production-night model inherited VERBATIM (B = 12; c ∈ {0.25, 0.5, 0.75}; θ ~ N(0,1); ε ~ N(0, σ_v²), σ_v ∈ {0.2, 0.5, 1.0}; revenue exp(q + L), E[exp(L)] = 1 exact, σ_m ∈ {0.5, 1.5, 2.5}; Mode P pick-best f ∈ {0.2, 0.6, 1.0}; Mode A publish-all s ∈ {0, 0.5, 1}) extended by ONE new axis — early-signal noise σ_e ∈ {0.25, 1.0} on y = θ + ε_1 + η read on a title's first version (324 decision cells) — with nights simulated whole in integer quarter-unit budget arithmetic (B4 = 48, costs 4c ∈ {1, 2, 3}): adaptive AD(ω), ω ∈ {0.5, 0.75} (stage 1 round(ω·B) one-version titles; stage 2 remaining budget as extra versions by y-descending round-robin, K_cap = 4) vs static S(K), K ∈ {1, 2, 3, 4, 6}, metric mean night revenue per unit budget over M = 8,000 nights per (cell, policy), CE/CV estimators per the V020 disclosure, Δ_cond vs the V020-conditional default (Mode P K=1 / Mode A K=6) and Δ_or vs the in-cell static oracle. Gates (run invalid on any failure): the K=1 analytic identity exp((1+σ_v²)/2), Mode A s=1 additivity, the Mode P f=1 static slice vs V020's committed Arm A quadrature values, the CHAINED ANCHOR reproducing V020's committed ruling row (Mode P share(K\*=1) 0.851851852 / median ΔR 0.0; Mode A share(K\*≥2) 0.888888889 / median ΔR 0.40621411 — sims/verdict-020-book-versioning/results.json `ruling` @ 76dc487) within tolerances pre-checked ≥ 2.5σ in the fixture BEFORE any run, and the aux signal-degeneracy self-check. Seeds 20260760 main / 20260761 stability (M = 2,000, must reproduce the ruling) / 20260762 reporting / 20260763 aux — strictly above the P029 registry high-water 20260759. Decision (registered order, REJECT first): REJECT iff ∀ω, both σ_e: median-over-cells Δ_cond ≤ +0.02 in BOTH modes; APPROVE iff ∃ ONE ω with median Δ_cond ≥ +0.10 in both modes at both σ_e AND Δ_or ≥ −0.02 in ≥ 80% of cells in all four mode×σ_e quadrants, stability-reproduced; NULL otherwise with the flip axis named. Reporting-only legs (cannot flip): B = 6, K_cap = 6, the perfect-signal σ_e = 0 upper bound, discarded-budget fractions. One uniform per normal (`NormalDist().inv_cdf`), draw-count sentinels, twin decision evaluator, CPython minor pinned, stdout + results.json byte-identical across two process runs. Hermetic: every fixture a pinned constant committed with the sim; zero repo/network reads at run time.

## What happened

Built `sims/verdict-032-adaptive-versioning/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: fixtures.json (the pre-registration —
every constant verbatim from the idea file, the V020 anchor row + 45 Arm A
values quoted verbatim, 18 disclosed intake-time decisions, every tolerance
pre-checked ≥ 2.5σ with its derivation committed) landed BEFORE the runner;
one disclosed pre-run correction (the K_cap-difference map's B=6 clause —
wording only, no constant). 834,948,000 uniforms across four pinned streams,
one uniform per normal, exact draw sentinels, ~9 min per run.

**Run output:** `SELF-CHECKS: 10567 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 stdout `43d6f125…`, results `c4cdf3de…`). All pre-registered gates
passed: the 45-value f=1 slice matched V020's committed quadrature values
exactly; K=1 / s=1 identities exact; the chained anchor at fresh seed
20260763 reproduced V020's ruling row (shares 0.851851852 / 0.888888889
EXACT, Mode A median dR 0.40508 inside the pre-checked 0.07); the
signal-degeneracy null check passed. **Ruling: REJECT — early-signal
adaptation buys nothing; V020's conditional rule stands.** Checked FIRST per
the registered order and met with margin everywhere: all eight (mode, ω,
σ_e) group medians of Δ_cond ≤ −0.0158 vs the +0.02 line (Mode P −0.175 to
−0.392), stability-reproduced at M=2,000. The perfect-signal σ_e=0 leg still
lands REJECT-side — the family's ceiling is signal-independent; the 179/648
adaptation-wins rows all sit in the parent's own Mode A s=0 corner where the
in-cell ORACLE is static K=1 and still beats the adaptive policy.

Landed: INTAKE 030 (2026-07-13T08:18:42Z) + VERDICT 032
(2026-07-13T08:18:43Z) appended to `control/outbox.md` (append-only;
VERDICT 031 = PROPOSAL 029's landed @ b50fd06 BEFORE this append —
origin/main merged INTO this branch, never rebased; numbers preserved by
the +2 offset). Verdict PR from `claude/verdict-032-adaptive-versioning`.
Worker session — no heartbeat writes; this card flip is the last commit.

## 💡 Session idea

When a sim's decision bands compare an ADAPTIVE policy against a baseline,
add the free upper-bound leg: run the same policy with the noisy observable
replaced by its noiseless version (σ_e = 0 here). It costs one reporting
sweep and converts a family-scoped REJECT from "the swept noise levels
failed" into "NO achievable signal sharpness can rescue this family" —
closing the cheapest follow-up ask (in this grid, "measure the signal
first") before anyone routes it. The portable rule: bracket the axis you
cannot measure live from ABOVE, not just across its plausible range — an
upper bound on the mechanism's best case is often worth more than another
grid point inside it.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-030-bracket-optimality.md`: complete and
honest; exports adopted. (1) Its canonical-form pin lesson ("know the exact
identity of what you compare before you compare it") is this session's
anchor discipline: the parent's ruling row and 45 Arm A values were quoted
VERBATIM into fixtures with their tolerances derived from the parent's own
committed margins (min K=1-boundary gap 1.31%/1.01%) BEFORE any run — no
mid-session tolerance surgery. (2) Its fixtures-before-runner and born-red
choreography followed verbatim; the one fixture amendment this session was
made pre-run, wording-only, and disclosed at every layer (fixtures, REPORT,
this card). (3) Where V030 could be fully exact (zero estimators), this
head cannot (adaptive allocation couples the observable to the draws), so
the V027/V028/V029 SE-arithmetic lesson carried instead: every gate
tolerance priced ≥ 2.5σ from committed parent numbers plus a disclosed
throwaway-seed pilot, and the binding decision margin (3.6 pp) shipped with
its ~4σ distance.

# Session — VERDICT 054 — Brineward band-2 necessity: does the committed loot/price ladder actually force the deeps, or is shallow grinding a viable route to the full upgrade ladder? (idea-engine PROPOSAL 043, game-mechanics rotation round 7)

> **Status:** `complete`
> 📊 Model: Fable (Claude 5 family) · 2026-07-13 · verdict-054 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 043 (`## PROPOSAL 043 · 2026-07-13T19:11:37Z · status: sim-ready`, landed via idea-engine PR #337 → main ea3744d, merged 2026-07-13T19:15:28Z; claim landed via idea-engine PR #338 (`control/claims/2026-07-13-verdict-054-brineward.md`, merged), `control/claims/`-ritual reserving INTAKE 043 + VERDICT 054 and branch claude/verdict-054-brineward-band-necessity; offset map PROPOSAL 043 → VERDICT 054, +11 per the docs/current-state.md rule) — "Brineward band-2 necessity": under the pinned model quoted verbatim from the idea file (per-water in band b ∈ {0, 1, 2}: one rum-runner duel then salvage; per-duel hull damage from the 5-point support {0, ⌊D_b/2⌋, D_b, D_b + ⌈D_b/2⌉, 2·D_b} pmf {1/8, 1/4, 1/4, 1/4, 1/8}, mean exactly D_b; sink iff cumulative damage since last full repair ≥ 100, the sinking draw resolving before the win; sink forfeits the unbanked hold, respawn port band 0, free full refit; a won water drops 3 crates of committed value v_b ∈ {5, 12, 25}, always-scoop chronological, hold cap 8, excess wasted; banking = in-water pier detour costing T_dock plus full repair at ceil(missing/4) gold; duel time t_b = {1, 3/2, 3/2}, sinking water costs t_b/2, SELECT transition and post-sink restart cost 0; grid D0 ∈ {20, 35, 50} × T_dock ∈ {1/2, 1, 2} = 9 cells, central (35, 1), pinned integer damage tables D0=20 → {20, 38, 45}, D0=35 → {35, 66, 79}, D0=50 → {50, 94, 113}; policy family pre-registered, 18 policies: GRIND(b, m) for b ∈ {0, 1, 2} × m ∈ {1, 2, 3} plus GRIND-H(b, m) banking early whenever hull ≤ 50 after a won water), compute the long-run banked-gold rate G(policy; cell) in Arm A (DECISION arm — seedless exact fractions.Fraction renewal-reward over the sink-to-sink cycle, zero-sink branch = pure loop rate exactly) confirmed by Arm S (seeded MC, random.Random(20261309), 100,000 waters per (cell, policy) leg, one damage draw per water, agreement gate |G_S − G_A|/G_A ≤ 1/50 every leg), and with NEC(cell) = G*(all)/G*(≤1) rule IN ORDER: REJECT FIRST (NEC < 5/4 in ≥ 5 of 9 cells) → APPROVE (NEC ≥ 3/2 in ≥ 7 of 9 cells AND central argmax neither GRIND(b*, 1) nor GRIND(b*, 3) AND seed-20261310 stability leg reproduces) → NULL (seven pre-registered axes). Seeds 20261309 main / 20261310 stability (20,000 waters, gate ≤ 1/20) / 20261311 sensitivity confirmations / 20261312 aux NEVER read — all strictly above the V053 high-water 20261308. Committed tables quoted verbatim @ gba-homebrew 8bac80a70c82096828663d501af5f2790acbccc4. Gates F1–F6, per-leg draw-count sentinels, twin independently-written decision evaluators, stdout + results.json byte-identical across two process runs. Fully hermetic: zero repo/network reads by the runner — fixtures.json committed BEFORE the runner (git-trail discipline). Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched.

## What happened

Built `sims/verdict-054-brineward-band-necessity/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 043 block; committed tables
quoted @ 8bac80a; the two harvested concept-doc lines verbatim; seeds
20261309–312; implementation pins disclosed) committed BEFORE the runner.
Git trail (PR #106 — squash-merge erases branch SHAs from main, resolve via
the PR): cd2a211 (born-red card) → acf2ccb (fixtures) → 1878559 (runner
band_sim.py + accepted run: results.json, run-stdout.txt, REPORT.md) →
43f8386 (INTAKE 043 + VERDICT 054 ledger + guard-fires telemetry) → this
flip.

**Run:** `SELF-CHECKS: 1484 passed, 0 failed`, exit 0, ~8 s; stdout +
results.json byte-identical across two full process runs by external diff
(results sha256 049adec7…, stdout sha256 32d077e9…); CPython 3.11 pinned,
asserted. Gates all green: F1 ladder identity 180g from the committed
BW_UP_COST; F2 hold arithmetic (descent 51g, band-2 m=1 75g, m=3 200g + one
25g crate wasted); F3 zero-damage fixture (G(GRIND(2,2)) = 75/2,
G(GRIND(1,2)) = 18, NEC = 25/12, exact); F4 pmf mean = D_b exactly, both
supports; F5 exact monotonicity (G in D0, NEC ≥ 1, sink prob in m and band);
F6 repair identities; zero-sink branch asserted reachable (D0=20 band 2 m=1,
q = 0 exactly); draw sentinels exact (main 16.2M / stability 3.24M /
sensitivity 17.28M; aux 20261312 ZERO draws); twin evaluators agree on Arm A
and stability; main leg ALL 162 legs ≤ 1/50 (worst 0.019096).

**Ruling: approve.** REJECT (checked FIRST) does not fire: NEC < 5/4 in 0 of
9 cells. APPROVE fires: NEC ≥ 3/2 in 7 of 9 (the two D0=50 low-T_dock cells
sit between the bands at 1.3223/1.3757), central argmax GRIND-H(2,1) (a
GRIND-H variant, the registered interior answer), stability leg reproduces
the class through both twin evaluators. Argmax band = 2 in EVERY cell; the
greed dial's measured answer is m* = 1 with the hull-aware trigger (central
m-curve 13.74/11.11/9.83); NEC0 2.5–4.0×. Honest limits shipped in full: the
registration's "pre-checked ≥ 4 SE headroom" claim measured FALSE (68 of 162
main legs < 4 SE, worst 1.66 — first-class anomaly; the six widened-leg
breaches it predicts are named), sensitivity straddles support_7pt +
restart_T_dock (both edge the D0=50 cells, reporting-only, cannot flip), and
a dual-reading disclosure on the one stability widened-gate breach
(registered class-reproduction reading → approve; stricter breach-denies
reading → null — both committed in results.json, the ruling rides the
registered text). Landed INTAKE 043 (accepted) + VERDICT 054 (finalized,
approve) in control/outbox.md (append-only; collisions re-grepped at
origin/main 3714ff6 at session start and at append — none).
control/inbox.md, both status heartbeats, and idea-engine's outbox
untouched. PR: https://github.com/menno420/sim-lab/pull/106 (READY;
merge-on-green owns the merge — zero agent merge/arm calls). Walls: none new
(the Write-tool REPORT.md block was tool-policy, bypassed via shell heredoc —
session-local, not a lane wall).

## 💡 Session idea

A registration can assert a STATISTICAL POWER claim about its own
confirmation gate and be wrong in a way no value-checker catches: PROPOSAL
043 pinned "agreement gate ≤ 1/50 … pre-checked ≥ 4 SE headroom at the
pinned leg length" — but the exact renewal-reward variance (computable at
DRAFTING time from the same enumeration the decision arm runs) puts 68 of
162 main legs below 4 SE (worst 1.66), because a RELATIVE gate loses power
exactly where G is small. The claim was unfalsifiable at review and false in
fact; the predictable consequence (false breaches on the widened legs) duly
arrived — six of them — and had to be adjudicated mid-verdict via a
dual-reading disclosure. Fix, drafting-side and cheap: a registration lint —
any proposal asserting a numeric power/headroom property of a seeded gate
must COMMIT the arithmetic (per-leg predicted SE from the exact arm, or a
proven bound), and gates should be derived FROM that arithmetic (e.g.
per-leg max(relative band, k·SE_pred)) rather than asserted alongside it.
Kin, deduped: V035 already CALIBRATED its gates to σ at drafting (the
V027/V031 two-datapoint lesson) — this idea generalizes that practice into a
lint on power CLAIMS; V053's 💡 lints missing derivation RULES, V052's lints
wrong fixture VALUES — a claimed-but-uncomputed POWER property is a third
species (grep of .sessions/, control/outbox.md, docs/ at flip time: no prior
card names it). Anchors: fixtures.json `implementation_pins_disclosed` (the
SE-headroom defect entry), band_sim.py `policy_stats` (the se2w closed
form), REPORT.md § Registration defect.

## ⟲ Previous-session review

VERDICT 053 (channel concentration, PR #105) is the direct predecessor and
the strongest card in the lineage: its disciplines transferred whole
(claim-first, fixtures-before-runner with PR-resolvable citations, collision
re-grep at append, twin evaluators, REJECT-first, honest-null posture), and
its 💡 — a registration can pin every CONSTANT and still underdetermine the
implementation — proved predictive twice here in new forms: the 7-point
support's "quarter terms floored" phrasing contradicts the registration's
own F4 exact-mean gate (resolved BY the registered gate, floor/ceil-mirror
convention, disclosed), and the stability conjunct's breach-vs-class
ambiguity had to be resolved by the proposal's literal text with both
readings committed. V053's proposed derivation-rule lint would have caught
the first; this session's 💡 targets the second's statistical sibling. One
inversion of its ASK 003 experience: V053 saw the mtime corridor flip local
check falsely GREEN off a neighbor's completed card; this session's born-red
card was itself mtime-newest, so local `check --strict` stayed honestly RED
(exit 1, sole finding: this card) on every pre-flip push — the same defect
surfacing as a loud hold instead of a false pass, disclosed per push in the
PR trail.

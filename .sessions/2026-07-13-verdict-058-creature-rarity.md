# Session — VERDICT 058 — Creature-PvP rarity vs skill: does the committed level-normalized ruleset actually let a Common team counter an Epic, or is collection grind the pay-to-win side door? (idea-engine PROPOSAL 047, game-mechanics r8)

> **Status:** `complete`
> 📊 Model: Claude Fable (Claude 5 family) · 2026-07-13 · verdict-058 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 047 (`## PROPOSAL 047 · 2026-07-13T21:28:33Z · status: sim-ready`, landed via idea-engine PR #350 → main 2808b16; claim landed via idea-engine PR #352, `control/claims/claude-verdict-058-creature-rarity.md` reserving the P047 intake + VERDICT 058 and this branch `claude/verdict-058-creature-rarity`; numbering INTAKE = proposal number, VERDICT 058 per the established P046→V057 offset map, sim-lab #110) — price superbot's committed level-normalized creature-PvP battle engine's two never-cross-rarity-tested lines (`disbot/utils/creatures/battle.py` @ superbot 1cc553651a19016a4b1439f048b49e7baa28dfb1: the `RARITY_BUDGET` comment "rarer = stronger, but level + type + move choice still let a Common counter an Epic" and the module docstring "rewards *skill*, not *time spent*") per the idea doc `ideas/superbot/creature-rarity-skill-counter-2026-07-13.md` @ idea-engine main 2808b16: a pre-registered hermetic seeded-MC battle sweep over the pure committed engine re-implemented verbatim from quoted constants — THE unique committed all-Epic team vs three pinned element-complete max-skill Common compositions BAL/ATK/MIX, Epic pilot axis BEGINNER/MID/SKILLED, 9-cell grid, Arm S random.Random(20261325) N = 20,000/cell with W(cell) = P(Common side wins) as exact Fractions, mirror/naive/Rare-gradient reporting legs on the same stream, stability seed 20261326, sensitivity legs seed 20261327 (jitter-wide, jitter-degenerate, BUFF_CAP 3/4, level 5), aux 20261328 never read; Arm E seedless exact-Fraction catch-economics stakes arm (E_epic / E_common / TP). Decision rule pre-registered, evaluated IN ORDER: REJECT FIRST iff W(c, BEGINNER) < 2/5 in ≥ 2 of 3; APPROVE iff W(c, BEGINNER) ≥ 1/2 in ALL 3 AND W(c, SKILLED) < 1/2 in ≥ 2 of 3 AND stability reproduces; NULL else with five pre-registered axes. Gates F1–F6, per-leg draw sentinels, twin evaluators, two-process byte identity, CPython 3.11 pinned. Fully hermetic: the runner reads only its own fixtures.json, committed BEFORE the runner. Build subtree `sims/verdict-058-creature-rarity/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 047 + VERDICT 058 appended to sim-lab `control/outbox.md` only, never echoed to idea-engine).

## What happened

Built `sims/verdict-058-creature-rarity/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 047 block / idea doc @ idea-engine main
2808b16; all 24 catalog rows and the engine formulas source-verified this
session against a pinned shallow clone of superbot @ 1cc5536, fetched via
add_repo after the GitHub MCP's expected out-of-scope denial — verbatim:
"Access denied: repository \"menno420/superbot\" is not configured for this
session") committed BEFORE the runner. Git trail (PR #111): 1c8c295
(born-red card) → 94700f0 (fixtures) → 9795e78 (runner battle_sim.py +
accepted run: results.json, run-stdout.txt, REPORT.md, README.md) →
b9969b5 (INTAKE 047 + VERDICT 058 ledger) → this flip. Claim-first:
idea-engine PR #352, merged by the enabler at 21:41:45Z, before any sim
work landed.

**Run:** `SELF-CHECKS: 104 passed, 0 failed`, exit 0, ~20 s; stdout +
results.json byte-identical across two full process runs by external diff
(stdout sha256 369129f9…, results sha256 7ae143ef…); CPython 3.11 pinned,
asserted. Gates all green: F1–F4 exact (the 32-event Cindling-vs-Infernox
hand log reproduced exactly); F5 mirror 4977/10000 (dev 23/10000 ≤ 1/50),
naive direction confirmed, zero stall hits; F6 Arm E anchors exact (785;
49/20; Markov twin ≡ inclusion–exclusion). Draw sentinels exact (main
36,564,003 jitter ≡ damage events, 1,877,073 ties all in the mirror leg —
the only equal-SPD matchup); twin evaluators agree on main + stability;
aux 20261328 never constructed.

**Ruling: reject.** REJECT (checked FIRST) fires: W(c, BEGINNER) < 2/5 in
3 of 3 — measured W = 0/1 EXACT in every one of the 9 cells. The disclosed
first-class anomaly: the wall is TOTAL, not marginal — zero Common wins in
425,000 decision+reporting battles, including the Rare gradient (max-skill
Common vs naive 260-budget Rare team: 0/20,000). Mechanism, read off the
committed constants: budget enters BOTH sides of the damage quotient
((200/300)² = 4/9) while the type chart's maximum swing is 1.5/0.67 ≈ 2.239,
and 4/9 × 2.239 ≈ 0.995 — perfect type play exactly neutralizes the per-hit
budget square and never touches the HP pools (197 vs 236–386). Arm E prices
the wall: TP = 475/12 ≈ 39.58× grind premium for the Epic team. Disclosed
inertness: the BUFF_CAP 3/4 leg is a no-op by construction (policy_setup
buffs at most once — stage = min(cap, 1/4) either way); run anyway per the
registration. Fixture-choice disclosure: reporting legs pinned at
N = 20,000/leg (the registration numbers the other legs but not these).
Walls: none new — the Write tool served the .py runner and README while
REPORT.md rode a shell heredoc per the standing V054–V057 classification
(documented wall, not re-probed); the superbot MCP denial above resolved
via add_repo, not a lane wall. ASK 003 corridor: sim-lab main never moved
this session (32ff5c3 at sync and at append), no merge of main into the
branch was needed, so the mtime-newest false-green could not fire — nothing
to disclose beyond absence. One local nuisance, not committed:
`.substrate/guard-fires.jsonl` is dirtied by every local `check --strict`
run; left unstaged throughout. `control/inbox.md`, both status heartbeats,
and idea-engine's outbox untouched. PR:
https://github.com/menno420/sim-lab/pull/111 (READY; merge-on-green owns
the merge — zero agent merge/arm calls).

## 💡 Session idea

Asymmetric-contest registrations deserve a drafting-time BAND-REACHABILITY
bound — the continuous-ratio sibling of V057's pigeonhole lint. When the
decision metric is a win rate in a two-sided contest whose per-exchange
rates are monotone in a product of pinned ratios, one line of algebra at
drafting time brackets whether the registered bands are reachable at all:
here, best-case Common per-hit ratio = (budget_lo/budget_hi)² × max type
swing = 4/9 × (3/2)/(2/3) ≈ 0.995 ≤ 1, with strictly smaller HP pools on
the same side — so W ≈ 0 and the 2/5 and 1/2 bands were provably out of
reach BEFORE 425,000 battles ran; the MC was a confirmation, not an
experiment. The move: (a) registrations for contest sims should compute
this dominance bound at drafting and, when the primary bands are
unreachable, pre-register the INVERSE question as the decision surface —
the knob value that restores the band (what budget spread makes
W(BEGINNER) = 1/2? — a bisection over the same committed engine at the
same cost); (b) when the bound is computed but the bands are kept anyway,
register it as a theorem gate with its direction, so an all-zero table
reads as "predicted wall confirmed" rather than a surprise. Kin, deduped
at flip time (grep .sessions/ + control/outbox.md for "band reachability",
"dominance bound", "unreachable band" — zero hits): V057's 💡 is the
finite-counting (pigeonhole) case of the same drafting-time-arithmetic
family and names only exhaustion claims; V023's "gate on tails, deliver on
moments" is about which measured statistics to gate, not about drafting
reachability; V033's saturating-probe amendment scoped one gate
analytically but post-registration. Anchors: REPORT.md § mechanism,
battle_sim.py pair_tables (the ratio algebra), PROPOSAL 047's REJECT band
(2/5) vs the measured 0/1 table.

## ⟲ Previous-session review

VERDICT 057 (keyword tiling, PR #110) is the direct predecessor. Its calls
held up: (1) its fixtures-as-citation-surface practice (harvested sentences
as first-class fixture fields, inherited from V056's nit) transferred
directly — this build's fixtures.json carries the proposal header and both
harvested engine lines verbatim, and the outbox VERDICT cites them from
there; (2) its Write-tool classification ("report-file-specific tool
policy, not a lane wall") held for a third consecutive session — the .py
runner and README went through Write, REPORT.md rode a heredoc, zero
wasted probes; (3) its ASK 003 record ("no merge, no corridor") gathered
another consistent observation — main static, corridor never fired. Its 💡
(theorem gates keyed off measured structure + drafting-time pigeonhole
lint for finite-counting prose) partially transferred: this build's mirror
tie-count wiring check keys off measured structure in exactly that spirit,
and this card's 💡 extends the drafting-time-arithmetic family from finite
counting to continuous ratio bounds — the V057 idea's trigger (exhaustion
claims over finite cells) simply never fired here because P047 registers
no counting claim. One nit: V057's card labels its smoke coverage
implicitly; this session found real value in a two-line scratch
hand-arithmetic probe (best-case per-hit rates) AFTER the accepted run to
rule out sign inversion before shipping an all-zero table — worth making a
habit whenever a decision table lands degenerate (all-zero/all-one), since
degenerate tables are exactly where a silent side-swap bug would hide.

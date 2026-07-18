# VERDICT 132 — PRD proc-rate compression

Reproduce PROPOSAL 119 (round-27 GAME slot, P119 → V132, +13): the Warcraft III / Dota 2 Pseudo-Random Distribution (PRD) anti-streak proc system. Instead of a flat per-attempt chance p, PRD starts each proc's chance low and RAISES it by a constant increment C on every consecutive failure, resetting on a success: P(proc on the n-th attempt since the last proc)=min(1,C·n). The counterintuitive trap: the increment C is NOT the proc rate. A designer who wants "25% crit" and naively sets C=0.25 does NOT get a 25% effective rate — the escalating chance forces frequent early procs, so the long-run EFFECTIVE rate is 1/E[N] (E[N]=2.21875 for C=0.25) ≈ 0.4507, nearly DOUBLE the nominal. The fix is to SOLVE C for the target rate (C≈0.0847 yields effective 0.25), never set C=nominal; what PRD actually buys is a bad-luck-streak bound (⌈1/C⌉−1 misses), not a rate change.

> **Status:** `complete`
> 📊 Model: high · review/verify

Born red by design: this card lands `in-progress` in the first commit so the substrate-gate HOLD holds the PR red until the reproduction is proven and independently audited; the final commit flips it to `complete`, clearing the HOLD and releasing merge-on-green (ORDER 003). No gate was bypassed. PHASE 1 (reproduction + independent digest audit) is APPROVED: the verifier reproduced the disclosed digest byte-identical across 4 runs and gates G1/G2/G3 all PASS; this PHASE-2 commit flips the card to `complete` on that audited ruling.

## Objective
Reproduce the committed P119 reference verifier byte-identical under its pinned world (SEED=20260717, ATTEMPTS=2000000, C_NAIVE=0.25, TARGET=0.25) and confirm: (a) the compact-canonical results-dict sha256 equals the disclosed digest, (b) all three gates hold as disclosed, in order G1→G2→G3, (c) cross-invocation and in-process double runs are byte-identical. Source header (verbatim): `## PROPOSAL 119 · 2026-07-18T05:48:40Z · status: sim-ready` / `target: sim-lab (VERDICT 132, +13 offset)`.

## GROUNDING (verified at HEAD)
- idea-engine HEAD `e0612a90bd74f04d4d93eca4b44b8bd60be525b0` (#536); reference verifier `ideas/superbot-games/prd_proc_compression.py` — git blob `4d4e1865d9eb05e0cd5b625258c80cc5e0852f81`, sha256 `b2aef76244a566cb8879e7850eea324bdfc39a13aa20eabc872697903d9426d2`, 242 lines / 10523 bytes. Source: https://github.com/menno420/idea-engine/blob/main/ideas/superbot-games/prd_proc_compression.py
- sim-lab work branch cut from origin/main HEAD `ce9fc18b69483fc09e5f83c2f3b45aa8599028e5` (#205).
- DIGEST POSTURE: SELF-FIELD / stdout-line. The verifier computes the digest over `json.dumps(results, sort_keys=True, separators=(",",":"))` BEFORE adding the `results_sha256` field, then adds that field and writes the on-disk `prd_proc_compression_results.json` pretty-printed (indent=2) WITH the field — so `sha256sum` of the on-disk file is NOT the digest; the disclosed digest is the value printed on the `Results-JSON sha256:` stdout line (and stored in the file's own `results_sha256` field).
- Offset authority: idea-engine control/outbox.md P119 `depends:` ledger (P119→V132 +13, "Offset pinned") + control/status.md baton — not docs/current-state.md (dormant snapshot through V059).

## Constraints honored
Stdlib-only (random, math, json, hashlib); verifier copied byte-identical (diff exit 0, blob + sha256 match); pinned SEED unchanged; no numpy/scipy; forward-only git; verdict reproduced independently, not assumed.

## Gate plan (disclosed → reproduced)
- G1 naive-C overshoot (headline): measured effective_naive ≥ EFF_MIN=0.40 by ≥3σ (binomial se); the vs-nominal-0.25 z astronomically significant.
- G2 solve-C-fixes-it (control): solved C_solved yields measured effective within 3σ of TARGET=0.25 (|z|<3) AND C_solved ≤ SOLVED_MAX=0.15.
- G3 closed-form anchor + anti-streak: measured naive effective reproduces analytic 1/E[N]=0.450704 within 3σ (|z|<3) AND PRD max miss-streak strictly below the true-random max miss-streak.

## Outcome — APPROVE (exact reproduction)
Reproduced digest `ce121bd9885747c336bf8f655112dc0bbffb35ba0fbd01832c14eb57d4248911` == disclosed digest (MATCH). Cross-invocation A + B and an in-process double invocation all produced the identical digest (all exit 0). Verifier copy diff exit 0; blob + sha256 match source.
- **G1 naive-C overshoot: PASS** — eff_naive **0.450684** ≥ 0.40, **z=146.3107σ**, **z_vs_null_0.25=655.4296σ**.
- **G2 solve-C-fixes-it: PASS** — c_solved **0.084744** ≤ 0.15, eff_solved **0.24998** vs 0.25 |z|=0.0637 (<3).
- **G3 anchor + anti-streak: PASS** — eff_naive 0.450684 vs closed-form **0.450704** |z|=0.0589 (<3) AND PRD max miss-streak **3** < true-random **51**.
- Analytic anchors: E[N]=2.21875, eff_naive_closed_form=0.450704, c_solved=0.084744, eff_solved_closed_form=0.25, PRD max-streak bound ⌈1/C⌉−1=3. Sim: eff_naive 0.450684 (streak 3), eff_solved 0.24998 (streak 11), eff_random 0.249999 (streak 51). all_pass=true, exit 0. First-failing gate: none.

## ⟲ Previous-session review
Prior loop landed VERDICT 131 (P118 sales-ramp capacity drag, +13, sim-lab #205, digest 9b7d3b07…) — APPROVE, clean born-red flip, merge-on-green with no agent merge call. Standing fleet-lane gap persists: verdict-126 (P113) is still open (idea-engine PR #527 born-red) while V127–V131 merged; flagged, not this slice's scope.

## 💡 Session idea
Soft-pity gacha ramp misvaluation (game): the same PRD mechanism inverted — a "pity" system that raises the drop chance only AFTER a threshold of misses (chance = base until miss k0, then base + C·(misses−k0)) has an effective rate that is a piecewise function of both base and C, so the advertised headline rate under-states realized pulls-to-drop whenever the pity ramp is reachable. Sim: gate that the realized drop rate exceeds the naive base by ≥ a floor at ≥3σ, with a closed-form E[N] anchor from the two-regime renewal walk, isolating how much of a banner's "advertised 0.6%" is actually the pity ramp — distinct from PRD's from-attempt-1 escalation.

# Session — VERDICT 045 — exploration reward bands: TIER_CAPS vs Q-0087 dual-track bands + survival Medium/Hard gradient (idea-engine ORDER 006 SUPERBOT-GAMES BALANCE item 7, requesting seat superbot-games)

> **Status:** `complete`
> 📊 Model: Claude Fable 5 (family-level) · 2026-07-13 · verdict-045 slice-worker session
> Objective: serve item 7 of idea-engine `control/inbox.md` ORDER 006 @ 8218d6630f53633461d993d9a3caa4ad54ab251d — "(7) EXPLORATION-REWARD-BANDS — (a) reconcile games/exploration/quest/catalog.py TIER_CAPS (tier I 5/25/10 · II 10/60/25 · III 20/120/50, conservative placeholders per D-0008) against the real superbot Q-0087 dual-track bands; (b) ratify/tune the survival Medium/Hard gradient (games/exploration/survival/difficulty.py: Medium 50/15s/1, Hard 40/20s/1; Easy is byte-identical to the mining bar per D-0004).". Packet read READ-ONLY at menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94 and menno420/superbot @ 6d8148808e7965f61cd85625798252fe32e1a409 (recon-worker packet, byte-copies + sha256 manifest). KEY RECON FINDING carried in: Q-0087 defines a dual-track PHILOSOPHY + an approved sim METHODOLOGY whose "bands" are three FUTURE P0-harness output curves — NO numeric band constants exist in superbot today (D-0008: reconciliation waits on the upstream P0 artifact), so (a) scores TIER_CAPS against the band DEFINITIONS + the existing V018/V033 contracts, with honest NULL where only the upstream artifact can answer. Build `sims/verdict-045-exploration-bands/`: byte-copy the pinned modules (sha256 manifest re-verified after copy), B0 validity gate re-deriving TIER_CAPS + difficulty constants, pre-registered fixtures.json (bands, play profiles, decision rule) committed BEFORE results, exact/NO-RNG deterministic sweeps, byte-identical re-run. Land INTAKE simreq-009 + VERDICT 045 in `control/outbox.md` (append-only; VERDICT 041 (cookbooks) + simreq-005 RESERVED by the in-flight sibling; VERDICT 044 (escort) + simreq-008 landed before this branch was cut @ 59d1a0c). Worker session — no control/status.md or control/inbox.md writes anywhere; idea-engine, superbot-games, superbot untouched.

## What happened

Built `sims/verdict-045-exploration-bands/` — 13 modules byte-copied at packet
pin 57f69be3 (the full import closure of `quest/catalog.py` +
`survival/difficulty.py`, incl. the packet's OWN survival harness
`survival/sim.py`), `engine/MANIFEST.json` sha256 re-verified after copy
(13/13 OK). Standalone B0 gate `b0_check.py` (28 checks, exit 0) re-derives
every order-quoted constant from the copied source. Pre-registration
`fixtures.json` (Q-0087 band definitions verbatim, V018/V033 contract
anchors, play profiles, bands S1–S4/C1a–C3/GB0–GB5, decision rules, the
EXPECTED-NULL declaration) committed BEFORE the runner (git trail: 8c64ed5
precedes 9737207).

**B0 VALID** (all exact before any ruling): TIER_CAPS (5,25,10)/(10,60,25)/
(20,120,50), GLOBAL_MAX (20,120,50), capability=None everywhere, TUNABLES
(60,10,1)/(50,15,1)/(40,20,1), Easy ≡ mining bar BY IMPORT (D-0004,
drift-proof in source), energy bar (60,10,1).

**Run:** `SELF-CHECKS: 93 passed, 0 failed`, exit 0; stdout + results.json
byte-identical across two full process runs by external diff (sha256 stdout
8b3f6921…, results ba914ecc…); ZERO registry seed draws — fleet high-water
20261280 untouched.

**Ruling: ratify-with-null.** (a) RATIFY-AS-PLACEHOLDERS + honest NULL on
the numeric band import — Q-0087 carries NO numeric constants at superbot @
6d81488 (the "bands" are the future survival P0 harness's pinned outputs,
D-0008); structural S1–S4 all exact-PASS incl. the V033 cross-pin (farmer
ceilings re-derive as 125/4 = 31.25 and 125/2 = 62.50 currency/hr
digit-for-digit); D0 checks C1a–C3 all PASS (casual 15-min day = one tier-I
bundle/day; capability-per-currency 1/2, 2/5, 2/5 non-increasing; capability
play-only). (b) RATIFY Medium 50/15s/1 / Hard 40/20s/1: the packet's own
harness reproduces its pinned bands exactly (sustained 360/240/180, burst
60/50/40, casual 30 everywhere); profile sweep — casual/regular profiles
ZERO refusals on all difficulties, sustained ratios exactly 2/3 · 1/2 · 3/4
inside the registered bands, honest quest loop 15× headroom on Hard.

Landed INTAKE simreq-009 + VERDICT 045 in `control/outbox.md` (append-only;
V041 cookbooks + simreq-005 reserved by the in-flight sibling; branch cut
from origin/main @ 59d1a0c, VERDICT 044 tail re-verified, simreq-009 free).
`bootstrap.py check --strict` exit 0. PR:
https://github.com/menno420/sim-lab/pull/93 (READY; merge-on-green owns the
merge — zero agent merge calls). Worker session — no control/status.md or
control/inbox.md writes anywhere; idea-engine, superbot-games, superbot
untouched.

## 💡 Session idea

When an order says "reconcile X against the real Y" and recon shows Y does
not exist yet, the highest-value move is NOT a bare NULL — it is to split the
ask into the computable projection (score X against Y's DEFINITIONS and every
already-verdicted contract that constrains X) and the upstream remainder, and
then SHIP THE INSTRUMENT the future Y will be scored with (here: the
capability-gap table 7·h·g·global_xp/35, reduced to 4·h·g at tier III). The
NULL stays honest because it was registered as EXPECTED before the runner;
the future artifact's arrival turns reconciliation into a table lookup
instead of a fresh sim. Portable rule: an honest NULL plus a pre-built
scoring table is a deliverable; a bare NULL is a deferral.

## ⟲ Previous-session review

VERDICT 044 (escort, the direct sibling, PR #92) pre-registered its decision
rule before any probe and let the loopability MEASUREMENT decide intent —
applied here unchanged as rules-in-evaluation-order with the NULL cell
registered as expected. V043's two reusable moves both landed here: drive
the packet's OWN pinned harness through its public entry point (survival
sim.run(), zero weight edits — the same shape as catch_sim.run()), and
disclose packet-owned protocol seeds as protocol constants rather than
registry draws. V042's engine-copy + MANIFEST + closed-form-prediction
discipline transferred directly; its card suggested reusing the subtree
method for items 5–7 — item 7 is the last of them, closing the batch.

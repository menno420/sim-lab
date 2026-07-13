# Session — VERDICT 050 — Gloamline plateau survival ceiling: does the committed night ramp ever cap a moving player, or is the best-nights record a patience meter? (idea-engine PROPOSAL 039, game-mechanics rotation round 6)

> **Status:** `complete`
> 📊 Model: Fable (Claude 5 family) · 2026-07-13 · verdict-050 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 039 (2026-07-13T16:33:11Z, status sim-ready; claim landed idea-engine PR #323 → main ab66463, `control/claims/claude-verdict-050-gloamline-survival-ceiling.md` reserving INTAKE 039 + VERDICT 050 and branch claude/verdict-050-gloamline-survival-ceiling — the claim-first ritual; offset map PROPOSAL 039 → VERDICT 050, +11 per the docs/current-state.md rule — the number RESERVES, never the position). Sequence note: Phase-1 recon saw the ledger tail at VERDICT 048 (main 91b9343) with VERDICT 049 reserved in-flight by a parallel session; at this branch cut V049 had LANDED (PR #100, main bec5505) — collision-grep for `## VERDICT 050` / `## INTAKE 039` at bec5505: none. Subject: a pre-registered survival-ceiling census for Gloamline (gba-homebrew's NDS horde-defense arc) — engine = the lane's own committed pure mirror `tools/check-gloam.py` @ d87f9ad (sha256 c86d9507…, byte-verified at recon), gl_* block byte-copied, sha256-gated before import; policy family {IDLE, KITE-PERIM, KITE-GRAD, SHOVE-PERIM, SHOVE-GRAD} × oil legs {LIT, DARK}; Arm D deterministic census (zero RNG, game seeds enumerated fixture inputs) + Arm S seeded execution noise (ε ∈ {1/16, 1/4}, M = 32, seeds 20261293 main / 20261294 stability (M = 16, must reproduce the ruling) / 20261295 reporting / 20261296 aux — strictly above the P038 high-water 20261292, nothing above 20261296 drawn). Decision rule pre-registered, evaluated IN ORDER, REJECT first (KITE-PERIM LIT ≥ 99% at every decision night {13, 16, 20, 24} AND ε = 1/16 night-24 LIT ≥ 90% of replications) → APPROVE (EVERY swept policy incl. SHOVE-GRAD posts SURV < 50% at some decision night in BOTH oil legs, stability-reproduced) → NULL (anything else — conditional finding is the pin, flip axes via per-axis survival shares, cheapest live probe named). Gates: mirror sha256 before import; IDLE proof-2 regression; spawn identities; stagger-rate 3σ + DARK zero-staggers > 24 px; press-dominance spot gate; per-leg sentinels; twin evaluators; two-process byte-identity; CPython minor pinned. Fully hermetic (runner reads only its own fixtures.json; every constant verbatim from the proposal/idea file). Fixtures commit BEFORE the runner (git-trail discipline). @codex step suspended per the outbox codex-line escalation @ dedc12e — verdict block writes `codex: none this cycle`. Worker session; `control/inbox.md`, both status heartbeats, VERDICT 049 files, gba-homebrew, pokemon-mod-lab, and idea-engine untouched.

## What happened

Built `sims/verdict-050-gloamline-survival-ceiling/` — `fixtures.json`
(every registered constant verbatim from the PROPOSAL 039 block / idea
file: the gl_* constant block @ d87f9ad, the per-frame loop order with
main.c cites, waypoint/tie-break/policy constants, the census/ramp/noise
grids, ε ∈ {1/16, 1/4}, M = 32/16/32, seeds 20261293–96, bands
99%/90%/50% with REJECT-first order) plus the WHOLE-FILE byte-copy
`check_gloam_mirror.py` (sha256 c86d9507… re-verified by the runner
before import), both committed BEFORE the runner. Git trail (PR #101):
4d0663e (born-red card) → b72d705 (fixtures + mirror) → 45aff43 (runner +
accepted run) → fd90e3e (ledger) → this flip.

**Run:** `SELF-CHECKS: 8358 passed, 0 failed`, exit 0, ~32 s; stdout +
results.json byte-identical across two full process runs by external
diff/cmp (results sha256 94b9be44…; no wall-clock in any output); CPython
3.11 pinned, asserted. Gates all green: mirror sha256 + constants
cross-check; IDLE proof-2 regression worst contact frame 258 and
press-dominance worst 186 — both byte-equal to the mirror's own committed
suite prints (independent confirmation); 30,720 spawn identities; stagger
21638/86400 within 3σ of 1/4; DARK zero-stagger identity 0 violations
(every no-stride cross-checked against the mirror's own gl_dark_press);
twin engines identical on 32 subsample cells + a gl_hash-driven noise
probe (no registry draw); draw sentinels exact (4,091,553 / 2,045,785 /
4,083,328; aux 20261296 ZERO draws); twin evaluators agree; stability
seed 20261294 reproduces the ruling. Disclosed: development edits to the
runner (grad-pruning expression, DARK-counter made a mirror cross-check,
per-leg aggregation, self-check bookkeeping) all landed before the first
complete run of the registered pipeline, whose output is the accepted run
byte-for-byte; post-run engine-sanity diagnostics (scratchpad-only) ran
AFTER that run and changed nothing.

**Ruling: approve.** REJECT (checked FIRST) fails maximally — KITE-PERIM
· LIT 0/128 at every decision night vs the ≥ 99% band, ε = 1/16 night-24
LIT 0/1024 vs ≥ 90%. APPROVE fires: EVERY swept policy incl. SHOVE-GRAD
posts SURV = 0 (< 50%) at every decision night in BOTH oil legs,
stability-reproduced. Mechanism (read-out, not decision): the fence-spawn
stream guards only the LAMPPOST, so fresh spawns land arbitrarily close
to a fence-adjacent player; the myopic KITE-GRAD corners itself (every
wall-escape move scores tied-or-worse one frame ahead; the pinned
tie-break holds the clamped move). Ramp leg: 51/128 → 15/128 → 1/128 →
0/128 from night 4 — the earned best-nights record (proof 20: best = 1,
seed 118) sits exactly on the measured curve. Landed INTAKE 039
(accepted) + VERDICT 050 (finalized, approve) in `control/outbox.md`
(append-only; collision-grep at origin/main bec5505 before append: none;
sequence note — recon tail V048 with V049 reserved in-flight, V049 landed
via PR #100 before this branch cut, numbers stayed 039/050 throughout).
`control/inbox.md`, both status heartbeats, VERDICT 049 files,
gba-homebrew, pokemon-mod-lab untouched; claims not pruned (later phase).
No walls hit; @codex suspended per dedc12e — `codex: none this cycle`.
PR: https://github.com/menno420/sim-lab/pull/101 (READY; merge-on-green
owns the merge — zero agent merge calls).

## 💡 Session idea

Engine byte-reuse (V042/V043, and this slice's whole-file mirror copy)
sha256-gates the BYTES but not the IMPORT: the runner executes the foreign
file's entire module top level inside the hermetic verdict process, so a
future upstream slice that adds an import-time side effect (a cache file
write, an env probe, a network touch behind a try/except) would run
silently inside a "reads only its own fixtures.json" sim — the sha256 pin
would even ratify it, because the pin is re-derived from the new bytes at
proposal drafting. Guard: the byte-reuse convention should gate
IMPORT-CLEANLINESS alongside the hash — cheapest form: snapshot the sim
directory listing + sizes before import and assert unchanged after, and
assert the mirror defines `if __name__ == '__main__'` (grep the bytes)
so import cannot run its proof suite; stronger form: exec the mirror with
`__builtins__` stripped of `open`/`socket` and re-inject nothing (the gl_*
block needs neither). Anchors: this sim's mirror-import stanza
(`gloamline_ceiling_sim.py`, the `importlib.util` block) as the pattern to
retrofit; sims/REFERENCE.md byte-reuse note as the doctrine line to amend.
Dedup: no card/idea in .sessions/ or the outbox mentions import-time side
effects; V028/V029 (the byte-reuse family's cards) target anchor
statistics and hand-pin replay, not the import surface.

## ⟲ Previous-session review

VERDICT 049 (KU exclusivity, PR #100) is the direct predecessor and this
session's opening surprise: its blocks were reserved in-flight at recon
but LANDED before this branch cut, so the "V049 in flight" sequence note
prepared from recon had to be rewritten against reality at append time —
the number-reserves-never-position rule worked exactly as designed, zero
renumbering. Its disciplines transferred whole: fixtures-before-runner
with PR-resolvable commit citations, the born-red card ritual, and its
wall disclosure (GitHub MCP re-auth flaking twice at PR-open) primed this
session to expect the same wall — it never fired. Honest criticism, two
sides: (a) V049's 💡 (the mtime false-green corridor: a mid-session merge
importing a newer completed card trivially satisfies the local strict
HOLD) described a corridor this session simply never entered — no
mid-flight merge occurred — so the risk it names is still live and still
unguarded; nothing in this session's tooling would have caught it either.
(b) V049's ⟲ disclosed inheriting the unrouted-💡 debt knowingly ("the
routing step needs to be REGISTERED into the session scope first, which is
itself a manager decision") — this session inherits the identical debt for
the identical reason, and notes the debt is now three cards deep (V048 →
V049 → V050) with no manager-addressed outbox line yet; the disclosure
pattern has stabilized into a ritual that documents the gap instead of
closing it, which is exactly the failure mode V048's original guard recipe
warned about.

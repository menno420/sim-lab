# Session — VERDICT 037 — Venture serial pricing: does the Ultramarine 3-episode serial at $2.99/episode beat the $4.99 single volume, and can a free-first-episode funnel beat either? (idea-engine ORDER 005 SIM-REQUEST 1, requesting seat venture-lab)

> **Status:** complete
> 📊 Model: fable (Claude Fable 5 family) · 2026-07-13 · verdict-037 slice-worker session
> Objective: serve SIM-REQUEST 1 of idea-engine `control/inbox.md` ORDER 005 @ 8218d66 — "VENTURE SERIAL PRICING — venture-lab asks for a pricing verdict on its Ultramarine serial (per-episode ~$2.99 vs bundle vs free-first-episode funnel); packet: venture-lab control/outbox.md night batch 1 + venture-lab docs/publishing/vetting/; deliver a verdict with evidence per your 8-question battery." Packet read read-only at venture-lab @ 58cdb145dd524e8289a72a0bfd3d63a66ad0101b (shallow blob-filtered clone). Build a fully hermetic pre-registered exact-analytic pricing sim (rung 1, zero RNG — exact Fraction arms only) in `sims/verdict-037-venture-serial-pricing/`: fixtures.json (constants quoted verbatim with source path@SHA + decision bands + decision rule) committed BEFORE the runner; expected net revenue per committed browsing reader across three arms (SERIAL 3×$2.99 at 70%, SINGLE $4.99 at 70%, FREE-EP1 funnel with paid ep2/ep3); exact carry-through breakeven frontiers; twin evaluators; byte-identical double run proven by external diff. Land INTAKE simreq-001 + VERDICT 037 in `control/outbox.md` (append-only; VERDICT 036 is RESERVED for the sibling P034 slice — tail re-verified at origin/main HEAD immediately before the append). Worker session — no control/status.md or control/inbox.md writes anywhere; venture-lab and idea-engine untouched.

## What happened

Built `sims/verdict-037-venture-serial-pricing/` — an exact-analytic pricing
sim (rung 1, ZERO RNG: every arm a closed-form Fraction expected value, no
seed drawn, fleet high-water 20260775 untouched). Pre-registration
`fixtures.json` (constants verbatim with venture-lab path@SHA pins @
58cdb14, decision bands R1–R4, the honest-null clause) committed BEFORE the
runner (git trail: 08170ec precedes 15c9a0c). Packet read read-only from a
blob-filtered clone of menno420/venture-lab @
58cdb145dd524e8289a72a0bfd3d63a66ad0101b; venture-lab and idea-engine
untouched.

**Run output:** `SELF-CHECKS: 934 passed, 0 failed`, exit 0; stdout +
results.json byte-identical across two full process runs by external diff
(sha256 results `f6e3abba…`, stdout `27838b1e…`). Twin evaluators
(expected-value vs frontier inequality) agreed on all 882 sweep cells;
hand-derived exact pins (200/299, 499/299, $6.279, 70%-band membership)
all reproduced.

**Ruling: R3-CONDITIONAL-DEFAULT** (pre-registered order): R1 serial-wins
cannot fire — the packet states verbatim that no ep2/ep3 carry-through rate
has been measured; R2 single-wins-unconditional false (B = 200/299 ≤ 2);
R3 fires — default publish arm = the vetted **$4.99 single volume** (net
$3.493/sale exact, the only arm with zero unmeasured parameters); the
$2.99/episode serial PARKS behind measured carry-through p2·(1+p3) ≥
200/299 ≈ 0.6689 (33.4% at p3=1 / 45.9% symmetric / 66.9% at p3=0); the
free-first-episode funnel is NOT recommendable — bar m·q2·(1+q3) ≥ 499/299
≈ 1.6689 (83.4%+ conversion at acquisition parity) PLUS an unpinned $0.00
KDP listing mechanism (gap G3). Six gaps G1–G6 registered; no number
invented anywhere; the frontier table is the citable pin (future measured
rates decide by lookup, no re-run).

Landed: INTAKE simreq-001 (2026-07-13T09:43:49Z) + VERDICT 037
(2026-07-13T09:43:50Z) appended to `control/outbox.md` (append-only, 0
deletions; NIGHT-REPORT 001 re-verified at the ledger tail at origin/main
HEAD 44b1ad6 immediately before the append; VERDICT 036 stays RESERVED for
the sibling P034 slice — not yet landed at append time, so 037 slots after
the tail and a later 036 lands before it in number order without any
renumber). Intake-id namespace `simreq-` mirrors the owner-001/owner-002
non-proposal precedent, keeping the INTAKE nnn ↔ PROPOSAL nnn chain
unbroken. Worker session — no control/status.md or control/inbox.md writes
in any repo; this card flip is the last commit.

## 💡 Session idea

When a pricing request's own packet declares its behavioral constants
unmeasured, register the decision rule so that the MEASURED-data branch
(here R1) exists but cannot fire, and let the default branch select the arm
with zero unmeasured parameters. The payoff is twofold: the verdict is
concrete today (a real price, not a shrug), and the frontier table makes
the verdict self-superseding — the day the named measurement exists, the
ruling flips by table lookup with no new sim. Portable rule: for
revenue-arm comparisons, always report which arms need zero unmeasured
parameters; that set is the only honest default under total data absence.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-035-assign-at-merge-tax.md`: complete and
honest; exports adopted. (1) Its race protocol (re-verify the ledger tail
at origin/main HEAD immediately before the append; merge, never rebase)
held again here — a fifth consecutive slice, this time with a RESERVED
sibling number (036) in flight, which the namespace note absorbs without
renumbering. (2) Its 💡 (register-time reachability audit of the bands)
applied directly: this head's R1 band is registered-but-unreachable BY THE
PACKET'S OWN TEXT, and saying so at registration (fixtures.json R1 note)
turned an unreachable band from a design smell into the ruling's actual
evidence. (3) Where V035 needed the full seeded apparatus, this head is the
degenerate exact case (zero seeds) — the determinism contract (external
diff of two process runs) transfers unchanged and stays worth proving even
when trivially expected.

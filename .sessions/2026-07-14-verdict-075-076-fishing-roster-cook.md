# Session — VERDICT 075 + 076 — superbot-games fishing batch: the full-roster sell/XP curve (SIM-REQUEST · fishing-full-roster-economy · 2026-07-13) + the cook-leg constants (SIM-REQUEST · fishing-cook-economy · 2026-07-13), served in ONE batch run per the roster request's own fold-in clause (ORDER 008 item (2) routing, Q-0264)

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-14 · verdict-075/076 batch slice-worker session

Objective: serve the two superbot-games SIM-REQUESTs that never reached this
inbox (ORDER 008 · 2026-07-14T09:34:40Z item (2), verbatim: "superbot-games
filed two SIM-REQUESTs (fishing-full-roster + cook-leg, games PR #92 commit
`21937f3`) that never reached this inbox — verdict them today if feasible,
else park cited"). Specs retrieved at source: menno420/superbot-games added
to session scope this session, cloned, read at main HEAD
`ed2fabbef58f3b97a03e6586a4e03ad0ab89c451` — verbatim block names
`## SIM-REQUEST · fishing-full-roster-economy · 2026-07-13` (filed
22:06:03Z) and `## SIM-REQUEST · fishing-cook-economy · 2026-07-13` (filed
18:18:29Z), both `status: open`; the packet's own NIGHT HEADLINE block
confirms the roster request "filed via #92 at `21937f3`". One slice, one
branch (`claude/verdict-games-simrequests`, PR #139), two verdicts.
NUMBERING: **VERDICT 074 stays RESERVED** for idea-engine PROPOSAL 063 (the
constant +11 offset map, ORDER 008 item (3)); these finalized as VERDICT 075
(intake simreq-010) and VERDICT 076 (intake simreq-011), collision-grepped
clean at origin/main d4ff3c8 immediately before the ledger append. Worker
session; `control/inbox.md`, both status heartbeats, and superbot-games
files untouched (ledger appended to sim-lab `control/outbox.md` only;
delivery is the manager's Q-0264 fan-in). This card held the substrate gate
red deliberately until this flip (the born-red discipline — the designed
hold was the only red this branch produced itself).

## What happened

Built both sim subtrees under the V043/V044 packet discipline — 16-file
byte-copied import closure at the pin (sha256 MANIFEST, re-verified before
import), the packet's OWN resolver/harness driven with species tables
injected as DATA (its documented growth surface), registrations committed
BEFORE each runner, registry seeds 20261389–20261558 strictly above the
fleet high-water 20261388 (new high-water 20261558), CPython 3.11 asserted,
byte-identical double runs (hashes in both REPORTs). Git trail (PR #139):
born-red card → V075 fixtures → V075 pre-runner amendment (theorem F-STRICT,
before any run) → V075 runner + accepted run → V076 fixtures (embeds V075's
candidate table verbatim as the adversarial reporting world) → V076 runner +
accepted run → ledger append (simreq-010/011 + V075/V076) → this flip.

**VERDICT 075 — NULL (band-straddle, needs-reframing).** B0 all green incl.
EXACT reproduction of every published V043 §5 anchor through the packet's
own harness. Naming ruled mechanically: legend_carp DISTINCT from legacy
carp (the supersede reading breaks even weak monotonicity against pinned
pike); all 29 rows stand. Theorem F-STRICT: strict integer monotonicity is
impossible — minnow 8 @ rank 1 and bass 13 @ rank 9 leave 7 intermediate
ranks for 4 intermediate integers. Finding F-PINCER: exactly ONE weight
scale (k = 1.1) threads the guppy integer floor and the V043 parity band,
at margins (1.1% / 0.5%) smaller than seed-batch noise — the stability leg
broke both bands (+2.7% / +3.9%), the registered NULL axis. Candidate
33-row table published NOT-PINNED; three-way reframing fork named with
exact numbers (re-center parity band ~3–10% / new family with contribution
cap / waves of 12–16). XP arm: mapping game_xp = size_rank CONFIRMED,
ladder must rescale ×3 (L25 32.7 h vs 10.9 h) or V043's pacing breaks.
Boat-gate finding: ungated deepwater rows invert venue logic
(tide_pool/master becomes the top faucet at 13.41 c/e). Anomaly A1
disclosed: the runner's printed ruling line lacks the C9 stability
demotion — carried by the recorded check failures + exit 1 instead
(83/85 checks; the 2 failures ARE the finding).

**VERDICT 076 — APPROVE-WITH-CONSTANTS, P\* = 12.** Cook table wireable
today: minnow 1 · bass 1 · pike 2 · legend_carp 7 cooked energy
(E_s = max(1, round(S_s/12))); worst no-perpetual-motion ρ 0.815 eval /
0.848 stability, every cell ≤ 0.9; min implied price 8.0 c/e — 10× above
the V042-flagged 0.8 shop, above the V043 band top 10.20. F-FLAT30: the
committed flat `"cooked fish": 30` is perpetual motion at EVERY measured
cell (ρ 7.13–13.5, ≥ 4.5 by the packet's own bite floor) — must be
superseded before any haul cook op wires. Choice-realness split honestly:
real and context-dependent on the coin axis (rich mining-faucet players
cook, fresh players sell; pike knife-edge by 0.04), time axis measured,
value judgment labeled. Roster extension rule published; the WR adversarial
world (ρ 1.11 at P = 12) pins why the roster wave re-derives P at its own
pin. 37/37 checks, exit 0.

**Previous-session review** (newest prior verdict card,
`.sessions/2026-07-14-verdict-073-owner-queue-attention-order.md`): V073's
"anomaly section honestly empty rather than unexamined" bar — the full
drafter-comparison built before the run — is the standard this session had
to meet from the OTHER side: when the stability leg broke the bands, the
temptation was to widen the bar or re-pick the cell; instead the break
became the ruling (NULL) and the runner's own missing demotion line became
named anomaly A1. V073 also modeled the two-verdicts-one-mechanism shape
this batch reused: one measurement loop, two decision frames.

💡 **Session idea (genuine, this session):** pre-registration should
include a REGISTRATION-TIME ARITHMETIC PASS: before any runner exists, try
to PROVE each registered criterion satisfiable/unsatisfiable from the
pinned constants alone. It caught F-STRICT here (7 ranks into 4 integers —
amended pre-runner, honestly), but it would ALSO have caught the F-PINCER
knife-edge (the k-window [guppy-floor, parity-band] was computable to
±2% from the anchors before a single cast was simulated) and shrunk the
stability surprise to zero. Concretely for the kit: a `registration-audit`
checklist line in the sim README template — "for each band, derive the
feasible parameter window on paper; if the window is thinner than expected
batch noise, re-register the band or the leg BEFORE the runner" — turns
the most expensive class of NULL (knife-edge-by-construction) into a
pre-run reframing conversation with the requesting seat.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).

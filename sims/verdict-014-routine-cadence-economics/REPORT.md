# REPORT -- routine-cadence-economics

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`
> (via the verdict-012/verdict-013 REPORT shape).
> Source idea: idea-engine PROPOSAL 012, `control/outbox.md` @
> `ff48c2fad809ce7704bb66aafee42335efd5c3fd` (idea file
> `ideas/fleet/routine-cadence-economics-sim-2026-07-12.md` @ `87f0dd2d`;
> probe verdict idea-engine PR #259 head `fc90d7f`).
> Run: `python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py`

## METHOD LABEL: NUMERIC SIMULATION (ladder rung 1)

A seeded, deterministic, parameter-swept discrete-event replay -- nothing here is
a built prototype and nothing is judgment-only except the hand-transcription of
trace T itself, which is committed as `labels.json` with an idea-engine evidence
commit and a reason string per event. The real corpus is REPLAYED (policies are
idealized, not historically executed -- the observed-vs-idealized gap is itself
measured and reported below); the Poisson/burst/empty variants are seeded
synthetics that break the n=1 dependence, as the probe demanded. This label
fills the outbox `evidence:` field as `simulation`.

## What it MODELS / MEASURES

**Trace T (real):** 5 arrivals reconstructed from idea-engine
`control/status.md` history `fc0bab6..531b109` (read at origin/main `ff48c2f`),
ALL inbox-only -- the webhook-visible class is EMPTY on the real trace (the word
"webhook" appears zero times in all 14 heartbeat versions; inference from
absence, stated as such). 4 arrivals are replayable (E1 03:02Z, E2 03:15Z,
E3 06:33Z, E4 08:30Z); E5 has no recorded arrival time -- rate-counted, not
replayed. 3 usable latency datapoints (E2, E3, E4; E1 folds into E2's catch --
fold run as sensitivity S6). 3 observed null sweeps (N1-N3) evidence real
standing cost. Window ~12.2h (00:03Z-12:12Z; the idea's "~14h" is seat age,
not window span -- flagged). Full ledger with all 12 documented gaps:
`labels.json`.

**Variants:** (a) real; (b) Poisson, lambda = 5 arrivals / 732 min = 0.41/h
derived from the real corpus (alt derivation 4/732 dropping timeless E5 = S8),
40 seeds, pooled; (c) burst -- 2 clusters/night of 2-3 arrivals within +/-20 min
(the real night's E1/E2 cluster shape), 40 seeds; (d) empty-night -- zero
arrivals, pure standing cost. Webhook-visible fraction w in {0, .25, .5, .75, 1}
swept on synthetics (real trace pins w=0 empirically); a dedicated tag-RNG
stream keeps arrival times byte-identical across w.

**Policy grid G (6):** failsafe-2h / failsafe-1h / failsafe-30m (cron sweeps at
phase 0, each 1 recon-worker-turn); failsafe-2h + chain-15m-while-work-open
(work opens 120 min per catching wake, windows merge, 1 worker-turn per re-arm;
work-window swept 60/240 in S4); event-driven-only (webhook wakes, ~0 turns);
hybrid(event-driven + failsafe-2h). Channel semantics, both evidence-anchored
and swept: chain wakes do NOT sweep inboxes (as-observed -- E2 arrived while the
chain was alive and waited for the 06:0x sweep; counterfactual chain-sweeps =
S2); webhook wakes DO sweep at ~0 marginal cost (optimistic for event policies,
untestable on the real trace; pessimistic flip = S3).

**Catch definitions (the E4 fork, both run):** def-A = latency to the wake that
reads the trigger (E4 -> 90 min); def-B = latency to done-when evidence,
modeled as wake + 31.4 min (the single measured execution lag: 10:00:00Z sweep
-> 10:31:24Z merge), applied uniformly.

**Cost model C (as-given, not measured):** 1 worker-turn per sweep, 1 per chain
re-arm, ~0 per webhook wake. Units are worker-turns; per the probe, relative
dominance survives unit error, absolute cost does not.

**Output:** 144-cell table (6 policies x 12 variant-instances x 2 defs) with
turns, catches, turns/catch, median + p95 latency, missed->2h count, constraint
verdict; winners with margins; strict-dominance analysis; sensitivities S1-S8.

## What it SETTLED (the load-bearing claims)

All numbers from the committed run (`results.json`; 272 self-checks, 0 failed).

1. **Winner under the stated objective: hybrid(event-driven + failsafe-2h) --
   the incumbent live posture.** Min turns/catch subject to p95 <= 2h under
   def-A: 1.75 turns/catch real, 1.47 Poisson, 1.39 burst -- tied with plain
   failsafe-2h at every w<1 cell (margin +1.50/+1.26/+1.19 to failsafe-1h, the
   next distinct survivor), and strictly better than failsafe-2h on latency
   whenever any arrival is webhook-visible, at zero extra cost. Under def-A the
   p95 <= 2h constraint NEVER binds for any failsafe-bearing policy (a period-P
   sweep bounds def-A latency by P, by construction).
2. **Dominance verdict: YES, two policies are strictly dominated.**
   failsafe-2h+chain-15m is strictly dominated by plain failsafe-2h (and by
   hybrid) across ALL variants x defs: identical catches and latencies, +24
   turns real (31 vs 7; 6.02 vs 1.47 turns/catch Poisson) -- chain re-arms buy
   ZERO coverage under the as-observed semantics, whose live proof is E2
   itself. Plain failsafe-2h is in turn strictly dominated by hybrid over the
   full grid (equal wherever w=0, strictly better wherever w>0, webhook wakes
   costing ~0). Not dominated: failsafe-1h, failsafe-30m (they buy p95 with
   turns), event-driven-only (wins at w=1, catastrophic at w=0).
3. **The catch-definition fork is the ONLY thing in the grid that forces a
   cadence change, and it flips exactly the 2h family.** Under def-B (catch =
   done-when evidence, E4's 2h01m reading) the 2h family fails p95 <= 2h on
   every arrival-bearing variant: real p95 121.4 min (fails by 1.4 min on
   n=1!), Poisson 147.6, burst 144.2. All 30 pass/fail flips in the sweep are
   failsafe-2h/chain/hybrid cells (S1); failsafe-1h and -30m never flip.
   Cheapest def-B survivor: failsafe-1h at 3.25 turns/catch real / 2.74
   Poisson / 2.57 burst -- ~1.9x the hybrid cost.
4. **event-driven-only is unusable at the real trace's webhook fraction.** It
   catches 0 of 4 real arrivals at 0 turns (p95 = inf) and fails every
   synthetic cell until w=1.0, where it wins everything (0 turns, latency 0).
   The webhook-visible fraction w is THE load-bearing unknown; the real
   corpus's empirical value is 0.
5. **Empty-night standing cost** (turns/night, the pure deadman price):
   failsafe-2h 7 / failsafe-1h 13 / failsafe-30m 25 / chain 7 (never arms) /
   event-driven 0 / hybrid 7. Tightening 2h -> 1h costs +6 turns per idle
   night forever; the real night showed 3 of 7 sweeps effectively null (N1-N3).
6. **The real night VIOLATED the constraint for a reason no policy in G
   fixes.** Observed (historical) p95 def-A = 178 min under the nominal
   failsafe-2h posture: the 04:0x wake did not sweep fm, so E1/E2 (03:02/03:15Z
   arrivals) waited for the 06:0x sweep -- idealized replay of the same policy
   on the same arrivals gives p95 = 90. The binding failure mode on the live
   night was sweep FIDELITY (does the wake actually sweep everything), not
   sweep cadence. Measured and disclosed as the largest comparable-to-live gap.

## What it did NOT settle

- **Absolute cost.** Worker-turn proxies are as-given (probe s4(a)); token/$
  costs are not agent-visible. Only relative rankings are claimed.
- **The webhook-visible fraction of future arrivals.** Empirically 0 on n=1
  night of fleet-restructure traffic; swept 0..1, but the true steady-state
  value is unknown and decides whether event-driven-only ever becomes viable.
- **The def-B execution lag distribution.** 31.4 min is a single measured
  event (E4); the def-B conclusions inherit n=1 on that axis too.
- **Chain value for WORK CONTINUITY.** The sim prices the chain as a coverage
  instrument (its role in grid G); the chain's actual live purpose
  (work-session continuity, honesty-guard pauses) is out of scope and NOT
  rejected here. Observed chain fires outside work windows (06:26Z, ~10:32Z --
  labels.json G4) are disclosed as model mismatch.
- **Sweep fidelity** -- the failure mode that actually bit on the real night --
  is outside the policy grid; no cadence choice fixes a wake that reads the
  wrong repos.
- **Arrival times are second-hand** heartbeat prose about foreign-repo events
  (labels.json G7); the 00:11-04:16Z chain endpoints rest on heartbeat
  self-attestation only (G2, carried as a stated limit on the chain rows).

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

The arrival trace is the real corpus at the named pins, with all 12
reconstruction gaps carried in `labels.json`. Abstractions: idealized policy
execution (every sweep sweeps everything -- the real 04:0x wake did not; the gap
is measured at +88 min of observed p95 and reported as finding 6, and it biases
AGAINST the "current posture suffices" conclusion's optimism about latency, not
for it); cost proxies as-given; a single measured exec lag. The headline
ranking (hybrid/2h cheapest, chain dominated, 1h the def-B survivor) is
arithmetic over sweep counts and period bounds and survives all of these; the
def-B knife-edge (fails by 1.4 min on the real trace) is exactly the kind of
margin the gaps COULD flip, and is reported as fragile, not load-bearing.

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

272 self-checks, 0 failed: hand-derived real-trace latency vectors, turn
counts, and chain fire counts for every failsafe policy (including the
25-turn chain-sweeps counterfactual and the E4-on-fire-time edge); pin and
labels.json consistency; cadence monotonicity of turns and p95 across the
whole sweep; catch-completeness of every failsafe-bearing policy; w-monotone
catches with arrival times asserted identical across w; the def-B flip; the
dominance pairs the verdict rests on; and an in-process double-computation
compared as canonical JSON. 40 committed seeds per synthetic variant, pooled;
the only RNGs are the seeded arrival/tag generators. The FULL 144-cell table
is printed and committed -- no best-point reporting.

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

Edge variants demanded by the probe are in the main grid: burst (clustered
arrivals -- rankings unchanged) and empty-night (standing costs as claim 5).
Sensitivities: S1 catch-definition (the one real flip, reported as finding 3);
S2 chain-sweeps counterfactual (chain drops 31->25 turns real, 6.25/catch --
still never within 3.5x of the winner; its strict domination is
semantics-dependent, its never-wins is not); S3 webhook-wakes-don't-sweep
(hybrid degrades toward plain failsafe-2h, winner unchanged); S4 work-window
60/240 min (chain 19/39 turns -- dominated at every setting); S5 E2 arrival
late-bound (no cell flips); S6 E1+E2 fold (uniform rescale, ranking
unchanged); S7 cron phase (real-trace def-B verdict FLIPS with a 90-min phase
shift: p95 91.4 PASS vs 121.4 FAIL -- n=1 fragility, reported as such);
S8 alt-lambda (winner family unchanged). The def-A winner is
phase/seed/variant-stable; the def-B boundary is knife-edge and said so.

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

One command (`python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py`),
stdlib-only, no network, no first-run fetch (trace embedded), exit 0 iff all
272 self-checks pass. Determinism PROVEN: two full process runs diffed
byte-identical on both stdout and `results.json` (external `diff`, recorded in
the session card), plus the in-process double-computation self-check. All
seeds are committed constants; no wall clock.

**5. LIMITS?** *"what this evidence does NOT show"*

n=1 real night (one seat's first ~12.2h on a fleet-restructure night), 3
usable latency datapoints, and every real arrival inbox-only -- the synthetic
variants are load-bearing for anything beyond that night. Cost proxies are
coarse and as-given. The webhook-visible fraction is unknown (swept, not
known). The def-B exec lag is a single event. Chain endpoints
self-attested (G2). It does not measure sweep fidelity, token costs, or the
chain's work-continuity value.

## EVIDENCE STRENGTH: moderate - gate PASS

Real reconstructed corpus with per-event evidence SHAs + full-grid seeded
sweep + hand-derived expectations + proven byte-identical determinism put this
above `weak`; but the real corpus is n=1 with 3 latency datapoints, the cost
model is an as-given proxy, and the decisive unknowns (webhook fraction, exec
lag distribution) are swept rather than measured -- short of `moderate-strong`.
No gate question fails, so the result stands as evidence, not hypothesis.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** **approve** -- and the approved answer is: **no change. Keep the
  incumbent hybrid(event-driven + failsafe-2h) posture.** It is the measured
  minimum-cost constraint-satisfier on every variant at every webhook fraction
  below 1 (tied with plain failsafe-2h exactly when the webhook class is
  empty, as on the entire real trace), and subscribing to webhook wakes is a
  free option that strictly dominates not holding it. The skeptic's readings
  are confirmed, not dodged: the n=1 real trace justifies NO cadence
  tightening (the only observed constraint miss was a def-B knife-edge of 1.4
  minutes, flippable by cron phase alone -- S7), and most of the grid's ranking
  is period arithmetic a napkin could do. What the sim adds beyond the napkin
  and is worth routing: (i) the chain-for-coverage policy is strictly
  dominated across ALL variants -- E2 is the live proof that chain wakes are
  not coverage; never revive the chain as a catch mechanism; (ii) the
  catch-latency DEFINITION, not the cadence, is the real decision variable --
  under catch-to-done-when-evidence the whole 2h family misses p95<=2h and
  failsafe-1h at ~1.9x cost is the cheapest survivor; (iii) on the one real
  night, the constraint was violated by sweep FIDELITY (a wake that didn't
  sweep), which no cadence buys back.
- **For the consuming decision** (fm owner-queue "post-EAP routine posture",
  decide <=2026-07-13): posture = hybrid(event-driven + failsafe-2h), i.e.
  materially "posture unchanged -- pick the incumbent"; adopt def-A (catch =
  the wake that reads the trigger) as the metric definition if the 2h p95 SLO
  is kept, OR fund failsafe-1h's +6 turns/idle-night if catch-to-evidence is
  the standard the owner wants. Do not decide between those on this n=1 --
  it is a definition choice, not an evidence question.
- **Guardrails:** re-run this harness (one command, new trace constants) when
  a second night's corpus exists or when any arrival class becomes
  webhook-visible in practice; if measured w rises materially above 0, the
  same grid says event-driven-only only becomes safe near w=1 -- hybrid remains
  the no-regret shape throughout.
- **Codex review:** pending -- the @codex question rides the verdict PR before
  finalization per lane convention (OA-002 usage cap may apply; disposition
  recorded by the coordinator in the `codex:` line at finalization).
- **Codex disposition (unsolicited PR #53 comment):** the
  chatgpt-codex-connector[bot] comment on PR #53 (2026-07-12T15:12:58Z) claiming
  commit `188e97c` "verdict-014: finalize coordinator ledgers" plus a PR opened
  via make_pr was verified against source and found **fabricated**: no such
  object in any ref after a full-ref fetch, no such PR open or closed, and the
  claimed line ranges (inbox L161-168, outbox L155-164) lie beyond EOF at the
  very blob `a92f7dc` its links target (159 / 153 lines; zero "INTAKE 012" or
  "VERDICT 014" hits) -- same signature as the PR #44 incident (verdict-012
  report; Q-0120 verify-never-obey). Its claimed strict-check warning does not
  reproduce (`check --strict` exits 0 at `a92f7dc`); the
  `.sessions/2026-07-10-boot.md` in-progress marker is real but pre-existing
  (flagged to the coordinator, not fixed here). Disposition: **ignored** --
  ledger finalization remains the coordinator's ceremony per the paste-ready
  block below.

## Paste-ready VERDICT 014 entry (for the coordinator to append to control/outbox.md)

> Numbering note: PROPOSAL 012 -> VERDICT 014, intake ledgered as INTAKE 012
> (proposal-sourced intakes number by proposal, PR #46 rule; verdict numbers
> are sequential over all verdicts -- 013 was PROPOSAL 011, no owner-direct
> interleave since). The transient misnumbered "INTAKE 012" of PR #45 was
> renumbered to INTAKE 010 by PR #46; the number is free.

```markdown
## VERDICT 014 · 2026-07-12T15:30:00Z · status: finalized
target: idea-engine coordinator seat posture (routing note for fm owner-queue "post-EAP routine posture" decision, HARD deadline 2026-07-13)
idea: idea-engine PROPOSAL 012 — https://github.com/menno420/idea-engine/blob/ff48c2fad809ce7704bb66aafee42335efd5c3fd/control/outbox.md (idea: ideas/fleet/routine-cadence-economics-sim-2026-07-12.md @ 87f0dd2)
verdict: approve
evidence: simulation
report: sims/verdict-014-routine-cadence-economics/ · run: python3 sims/verdict-014-routine-cadence-economics/cadence_economics_sim.py
measured: 144 cells (6 policies x {real trace, 40-seed Poisson lam=5/732, 40-seed burst, empty night} x w∈{0,.25,.5,.75,1} x 2 catch defs); winner s.t. p95<=2h under def-A(catch=wake): hybrid(event+failsafe-2h) tied with failsafe-2h at 1.75 turns/catch real (1.39-1.47 synthetic, margin +1.19-1.50 to failsafe-1h); STRICTLY DOMINATED across all variants: failsafe-2h+chain-15m (31 vs 7 turns real, chain re-arms buy zero coverage — E2 live proof) and plain failsafe-2h (by hybrid, free webhook option); def-B(catch=done-when evidence, +31.4 min measured E4 lag) flips exactly the 2h family (real p95 121.4 fails by 1.4 min; Poisson 147.6) making failsafe-1h cheapest survivor at 2.57-3.25 turns/catch; event-driven-only catches 0/4 on the real trace (webhook class EMPTY) and wins only at w=1; empty-night standing cost 7/13/25/7/0/7 turns; OBSERVED real-night p95 was 178 min under nominal failsafe-2h — sweep fidelity, not cadence, was the binding failure; 272 self-checks, byte-identical re-runs proven by diff
recommendation: keep hybrid(event-driven + failsafe-2h) — posture unchanged; never revive the 15m chain as a coverage mechanism (strictly dominated, all variants); the real decision variable is the catch-latency DEFINITION: keep def-A with the 2h SLO, or fund failsafe-1h (+6 turns/idle-night, ~1.9x cost) if catch-to-evidence is the standard — a definition choice, not an n=1 evidence question; re-run the committed harness when a second night's corpus or a nonzero webhook-visible fraction exists
codex: pending — @codex question to be posted on the verdict PR head before finalization (OA-002 cap may apply); disposition recorded here by the coordinator at finalization
gate: PASS (COMPARABLE: real reconstructed trace at named pins, 12 gaps disclosed in labels.json, observed-vs-idealized sweep-fidelity gap measured at +88 min p95 · UNCORRUPTED: 272 self-checks incl. hand-derived latency/turn/chain-fire vectors, 40 committed seeds pooled, full 144-cell table committed · ROBUST: burst + empty-night edges in-grid, S1-S8 sensitivities, def-A winner phase/seed/variant-stable, def-B knife-edge reported as fragile · REPRODUCIBLE: one command, stdlib-only, no network, byte-identical stdout+results.json across process runs · LIMITS: n=1 night, 3 latency datapoints, cost proxies as-given, webhook fraction unknown/swept, exec lag single-event)
```

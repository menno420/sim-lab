# verdict-098 · round-robin-domain-starvation-cliff

Independent, hermetic, stdlib-only verification of idea-engine PROPOSAL 085
(`## PROPOSAL 085 · 2026-07-16T16:32:07Z · status: sim-ready`, idea
`ideas/fleet/round-robin-domain-starvation-cliff-2026-07-16.md`). P085 → V098 under
the constant +13 PROPOSAL↔VERDICT offset.

The head prices the folk belief that a FAIR round-robin (RR) rotation is harmless
when the server is underloaded and only its high-load starvation is interesting. On
a pinned single-WIP server (exactly one proposal emitted per round) over four domains
D=[fleet, venture, game, unrelated] with base arrival mix Λ={fleet:0.40, venture:0.25,
game:0.20, unrelated:0.15} and load family λ_d(ρ)=ρ·Λ_d for ρ∈{0.70,0.90,1.00,1.10},
RR (serve `D[t mod 4]`, forced FILLER when that domain's queue is empty) is compared
against LQF (serve `argmax_d q_d`, ties by rotation order, filler only when ALL queues
empty). A single arrival vector is drawn per round from ONE RNG stream and applied to
BOTH schedulers' queue copies (SHARED ARRIVALS — the schedulers see identical streams,
else the comparison would be NULL). P085 pre-registered an ACCEPT rule requiring ALL
four gates R1–R4. The measured run REJECTS: R1's low-load-harmlessness leg fails (at
ρ=0.70 filler(RR)=0.33314 > filler(LQF)+0.02=0.32021) and R3 fails (ρ=0.70
Var[total_backlog] RR 7991.62 ≫ LQF 1.50), while R2 (ρ=1.00 max_backlog RR 1561.20 ≥
3× LQF 109.20) and R4 (ρ=1.10 most-starved RR domain = `fleet`) pass. The starvation
phenomenon is REAL, but the pre-registered ACCEPT rule requires all four gates and two
fail — REJECT at first failing gate R1. Root cause: RR's fixed 1/4=0.25 per-domain
share is below fleet's arrival rate ρ·0.40 once ρ>0.625, so at the registered low
anchor ρ=0.70 fleet is ALREADY unstable under RR; the true harmless-load region is
ρ<0.625, below the tested 0.70.

## Run (one command)

```
python3 sims/verdict-098-round-robin-domain-starvation-cliff/round_robin_domain_starvation_cliff_sim.py
```

Exit 0 iff every self-check passes (6/6). Deterministic: `results.json` and
`run-stdout.txt` are byte-identical across process runs — no wall clock, no network,
no git at run time. Stdlib only, CPython 3.11.15. The RNG is `random.Random(seed)`
over the in-file seed constants S=[1,2,3,4,5]; the schedulers share one arrival stream
per round so RR and LQF are compared on identical inputs.

## Structure — two schedulers + twin evaluators

- **Scheduler A (RR)** — round t serves `D[t mod 4]`; if that domain's queue is empty
  at its turn it emits a FORCED FILLER and the queues are unchanged. A fixed 1/4=0.25
  service share per domain regardless of backlog.
- **Scheduler B (LQF)** — serve `argmax_d q_d`, ties broken by rotation order
  (fleet > venture > game > unrelated); filler ONLY when all queues are empty. The
  work-conserving comparison baseline.
- **Shared arrivals** — one arrival vector per round (per domain d: sum over k∈{0,1,2}
  of `[random() < ρ·λ_d/3]`, a Bernoulli-sum with E[arrivals_d]=ρ·λ_d, max 3/round)
  drawn from a single RNG stream and applied to BOTH schedulers' queue copies, so any
  metric gap is attributable to the scheduler, not the input.
- **Twin evaluators** — an if-chain scorer and an independently transcribed
  table-driven scorer agree on the ruling token AND the first-failing gate over the
  measured gate outcomes — REJECT/R1 both.

## Decision rule (pre-registered, from P085)

**ACCEPT iff R1 AND R2 AND R3 AND R4**, the rule firing in order R1→R2→R3→R4; else
**REJECT** at the first failing gate.

- **R1 crossover:** ρ=0.70 filler(RR) ≤ filler(LQF)+0.02 AND ρ=1.10 filler(RR) ≥
  filler(LQF)+0.10 (means over S). A two-legged gate — fails if either leg fails.
- **R2 backlog divergence @ criticality:** ρ=1.00 max_backlog(RR) ≥ 3·max_backlog(LQF)
  (means over S).
- **R3 low-load harmlessness:** ρ=0.70 Var[total_backlog](RR) ≤ Var[total_backlog](LQF)
  (means over S).
- **R4 starvation locality:** ρ=1.10 under RR, argmax_d mean(q_d over W..T) == fleet.

Full grammar and the pinned world in `fixtures.json`.

## Layout

- `fixtures.json` — the pinned world (Λ, ρ set, seeds, arrival grammar, domains, T, W),
  the pre-registered gates and decision rule, the source proposal header, and the
  seed-1 first-50-round total_backlog traces for BOTH schedulers (the committed
  fixture, re-verified each run).
- `round_robin_domain_starvation_cliff_sim.py` — the single runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

**VERDICT: REJECT** (first failing gate R1) — 6/6 self-checks, exit 0, byte-identical
double run, twin evaluators agree REJECT/R1.

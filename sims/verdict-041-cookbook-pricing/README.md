# verdict-041 · cookbook-pricing

Serves **idea-engine ORDER 006 SIM-REQUEST 3** (control/inbox.md @ 8218d66;
requesting seat **venture-lab**): narrow-TAM cookbook pricing — $19 fixed
vs PWYW, canonical case the Merge-Wall Cookbook $19 (publish-ready, owner-
gated). Packet read READ-ONLY at menno420/venture-lab @
`f15e9f187b41f7f968f67e22200f18d4a89dfcde` (`control/outbox.md` "night-run
MORNING TALLY" + `docs/publishing/vetting/merge-wall-cookbook.md` §3/§7 +
`candidates/merge-wall-cookbook/INTAKE.md` +
`docs/publishing/vetting/template-packs.md` §3 +
`docs/publishing/vetting/photo-packs.md` §3 +
`candidates/photo-packs/MARKET-PLAN.md` §(a) fee schedules +
`docs/publishing/OWNER-QUEUE.md` cookbook rows).

Fully hermetic: every constant is quoted verbatim with its source path@SHA
in the committed `fixtures.json` (the pre-registration — arms, grids,
decision rule R1–R4, and hand-derived exact pins landed BEFORE the runner;
git trail: fixtures commit precedes the runner commit). The sim reads
exactly ONE file (its own fixtures.json), draws ZERO seeds, and touches no
repo state, network, or wall clock.

Model (per committed baseline buyer — one $19-fixed cookbook buyer;
decision channel = Gumroad direct, the cookbook's §7 default, net(p) =
0.871p − 0.80 — the V037/V039/V040 kernel lineage):

- **FIXED_19** — the committed default: E[net] = **$15.749 exact**. Zero
  unmeasured parameters.
- **PWYW** (min $0/$3/$5) — E[net] = u·net(w̄); u = paid takes per baseline
  buyer, w̄ = mean paid amount, both unmeasured (G1). Frontier:
  **u·net(w̄) ≥ 15.749**; at u = 1 the bar is **w̄ = $19.00 exactly on
  every affine kernel** (kernel-invariance); each extra paid transaction
  costs exactly $0.80.
- **PWYW min $19** (= $19 fixed + voluntary overpay) — cannot lose per paid
  sale; parked on conversion-side risk (u unmeasured).

**Ruling: R3-CONDITIONAL-DEFAULT** per the pre-registered rule — no PWYW or
sales measurement exists anywhere in the packet (G1; the catalog's only
PWYW listing, template-packs $19 suggested, is not live), and neither arm
dominates the registered band (PWYW 803/1829 cells, FIXED 1026/1829) —
so: keep the committed **$19 one-time fixed**; PWYW parks behind the
measured frontier (landmark bars: w̄ ≥ $19 at u = 1; u ≥ 1.9910 at w̄ =
$10; u ≥ 1.2841 at w̄ = $15); the template-packs PWYW listing is the
catalog's designated measurement instrument.

## Run (one command)

```
python3 sims/verdict-041-cookbook-pricing/cookbook_pricing_sim.py
```

Exit 0 iff all self-checks pass (5,612 passed, 0 failed). Deterministic —
every decision quantity an exact Fraction closed form; ZERO seeds drawn
(fleet high-water 20261280 untouched); stdout + results.json byte-identical
across runs by external diff.

Files: `fixtures.json` (pre-registration) · `cookbook_pricing_sim.py`
(runner) · `results.json` (committed output) · `REPORT.md` (verdict
evidence — the 8-question battery + validity gate).

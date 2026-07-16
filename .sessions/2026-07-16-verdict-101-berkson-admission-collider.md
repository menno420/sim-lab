# Session — VERDICT 101 — Berkson admission-collider anticorrelation trap (P088, idea-engine). On a two-trait item world (each candidate item draws novelty N and rigor R independently — zero true correlation in the source population — from fixed independent marginals over a cohort of C trials/seed, seeds S=[1,2,3,4,5]) a DISJUNCTIVE admission gate keeps an item iff N ≥ a OR R ≥ b, and P088 pre-registers an APPROVE rule requiring ALL of R1–R4: R1 null-anchor (in the FULL unconditioned population corr(N,R) ≈ 0 within tolerance — the traits are drawn independent, so any admitted-set correlation is conditioning-induced, not a source signal), R2 effect (among ADMITTED items corr(N,R) is significantly NEGATIVE, margin ≥ 3σ over seeds — the spurious anticorrelation trap fires), R3 dose-response (tightening the gate — raising the OR-thresholds (a,b) so admission is scarcer — makes the admitted-set anticorrelation MONOTONE more negative across the pre-registered threshold ladder), R4 mechanism-isolation (swapping the DISJUNCTIVE OR-gate for a CONJUNCTIVE AND-gate (admit iff N ≥ a AND R ≥ b) on the identical draws does NOT produce the negative admitted correlation — isolating the collider/OR selection as the mechanism, not the marginals). Disclosed expected landing APPROVE (Berkson's paradox: selecting on the disjunction of two independent causes induces a negative association among the selected). Independent hermetic re-implementation, CPython 3 stdlib only, under COMMON RANDOM NUMBERS (per trial a single (u_N, u_R) uniform pair drawn ONCE via random.Random(seed), the SAME draws mapped to both the OR-gate and the AND-gate control and reused across every threshold rung, else NULL); twin evaluators (if-chain + table-driven) must agree on token AND first-failing gate (idea-engine PROPOSAL 088, outbox block `## PROPOSAL 088`; P088 → V101 under the +13 offset, twenty-fifth row; SEEDLESS ledger baton — seeds are the in-file constants S=[1..5], no seed-ledger block consumed, next free block stays 20261730, inherited from the V100 baton).

> **Status:** `complete`
> 📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

Objective: produce VERDICT 101 for idea-engine PROPOSAL 088 (the Berkson
admission-collider anticorrelation trap). One slice, one branch
(`claude/v101-berkson-admission-collider`), one verdict. NUMBERING, verified at
sim-lab origin/main (the V100 merge #172, c172698, is the tip at session start):
newest `## VERDICT` header is 100; `## VERDICT 101` / `verdict-101` / `v101`
collision-grepped — no ledger header, no `sims/verdict-101-*` competing path, no
competing session card — so idea-engine PROPOSAL 088 → **VERDICT 101**, the +13
offset's twenty-fifth row (INTAKE number = proposal number, unbroken; map-row
extension lands in `docs/current-state.md` this same PR). Worker session; ledger
appended to `control/outbox.md` only — `control/inbox.md` untouched (manager-order
file); this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P089 → V102). No idea-engine claim file written by this
sim-lab slice (the V074–V100 precedent — the idea-engine claim rides the idea-engine
mirror PR). This is a NUMERIC-SIMULATION head (rung 1, the P017–P087 hermetic
pre-registered discipline): an independent hermetic re-implementation of a
two-trait admission funnel where novelty N and rigor R are drawn INDEPENDENT and a
disjunctive OR-gate selects the admitted set, evaluated under COMMON RANDOM NUMBERS
(the OR-gate and the AND-gate control consume the identical per-trial (u_N, u_R)
draws, reused at every threshold rung, else the paired comparison is NULL), across
four pre-registered gates R1→R2→R3→R4, with twin evaluators (an if-chain scorer and
a table-driven scorer) that must agree on the ruling token AND the first failing
gate. The seeds are the in-file constants S=[1,2,3,4,5] (RNG = `random.Random(seed)`),
NOT a draw from the fleet seed ledger — this slice consumes NO seed-ledger block and
the next free block stays **20261730**, untouched (inherited from the V100 baton).
This card holds the substrate gate red deliberately until the flip (the born-red
discipline — the designed hold is the only red this branch produces itself); the
flip to `complete` is this session's LAST step (verdict APPROVE, all gates verified,
determinism + twin evaluators + self-checks all good), taken as the release-landing
commit.

## What happened

Built `sims/verdict-101-berkson-admission-collider/` under the standing discipline
(born-red card FIRST → sim + fixtures + README + REPORT + outbox + map row →
heartbeat → flip, this card). The runner is an INDEPENDENT hermetic
re-implementation of the two-trait admission funnel from the registered spec (NOT
copied from P088's disclosed `p088_drysim.py`, which is not committed). On the
pinned world — n = 2000 items/run, seeds S = [1,2,3,4,5] — each item carries two
latent scores, novelty `N` and rigor `R`, each iid `Normal(0,1)` drawn from
**SEPARATE** streams (`random.Random(seed)` for N, `random.Random(seed+10000)` for
R), so `corr(N,R) = 0` in the population BY CONSTRUCTION. Admission is a
**DISJUNCTIVE collider gate** — admit iff `N ≥ t OR R ≥ t` with `a = b = t`
calibrated to a target marginal admit rate T via `t = Φ⁻¹(√(1−T))` (independent
tails ⇒ OR rate `1−(1−p)²`); three stringency rungs T ∈ {0.50, 0.25, 0.10}
(reference 0.25) give thresholds t = 0.544952 / 1.107798 / 1.632219. The R4
falsifier is a **single-gate control** admitting on `N ≥ 0.674490` ALONE, matched
to the same ≈25% marginal rate. `Φ⁻¹` is Acklam's stdlib rational approximation;
the metric is Pearson `r` in pure stdlib — `ρ_full` over the full 2000 (R1),
`ρ_admit` over each OR-gate subset (R2/R3), `ρ_single` over the single-gate subset
(R4); pooled mean = mean of the 5 per-seed ρ, `σ` = sample SD (ddof=1), `SE =
σ/√5`. Achieved marginal admit rates land within 0.02 of every target
(0.5009/0.2513/0.1005 OR, 0.2497 single) — a miss trips the INVALID guard. Twin
evaluators (if-chain scorer + independently-transcribed table-driven scorer) must
agree on the ruling token AND the first-failing gate. Fixture: the seed-1
reference-stringency (25% OR-gate) admitted size (537) + first-20 admitted (N,R)
pairs at full `repr` precision + the four calibrated thresholds, committed on
first run and re-derived every run. Byte-identical double run via external diff +
sha256; CPython 3, stdlib only, zero repo/network reads at verdict time.

## Results

**VERDICT 101 — APPROVE** (first-failing-gate **None**; all of R1→R2→R3→R4 hold).
Measured margins over S = [1,2,3,4,5]:

- **R1 null anchor — PASS.** Full unselected 2000-item population `ρ_full` pooled
  mean **+0.000251** (SE 0.004738); `|mean| + 3·SE = 0.014465 ≤ 0.03` — ≥3σ INSIDE
  the ±0.03 null band. N ⟂ R by construction (separate seeded streams, +10000
  offset), so any post-selection correlation is genuinely selection-induced.
- **R2 effect @ T=0.25 — PASS.** OR-gate admitted-cohort `ρ_OR` pooled mean
  **−0.587329** (SE 0.006550); `mean + 3·SE = −0.567680 ≤ −0.45` — clears the
  pre-registered anticorrelation floor −ρ* = −0.45 by **20.97σ**. Conditioning on
  the disjunctive collider manufactures a strong negative correlation from two
  independent axes — the Berkson trap fires.
- **R3 dose-response — PASS.** Pooled `mean ρ_OR` strictly more negative as
  admission tightens: **−0.457816 (50%) > −0.587329 (25%) > −0.685281 (10%)**,
  adjacent separations **14.34σ** (50↔25) and **8.92σ** (25↔10), both ≥3σ. The
  collider bias scales monotonically with selection pressure.
- **R4 mechanism isolation — PASS.** Single-gate control (admit on N alone)
  `ρ_single` pooled mean **−0.013478** (`|mean| = 0.0135 ≤ 0.03`, the registered
  pooled-mean reading, ≈1.2 SE from exactly zero), AND `|ρ_OR − ρ_single| =
  0.573852` separated at **43.35σ**. Selecting on N alone conditions on N but says
  nothing about the independent R — no correlation appears; the disjunction is
  proven the sole cause. (The proposal discloses that R4's control on R1's stricter
  ≥3σ-inside grammar reads `|mean| + 3·SE = 0.047985 > 0.03` — finite-sample noise
  ≈1/√500 on ≈500 admitted/seed pokes the 3σ envelope just past 0.03; R4 is
  registered on the LOOSER pooled-mean reading + the decisive 43.35σ separation, not
  silently tightened.)

APPROVE fires — the pre-registered rule (APPROVE iff R1∧R2∧R3∧R4) returns APPROVE,
no failing gate; the REJECT/NULL/INVALID worlds were reachable (a shared-stream
population correlation failing R1, a non-monotone dose-response failing R3, a
single-gate control that ALSO anticorrelated failing R4, an admit-rate miss →
INVALID) and did not come live. **Twin evaluators agree APPROVE/None** on both the
ruling token and the first-failing gate. Every measured number reproduces the
proposal's disclosed dry-sim EXACTLY from the independent re-implementation.
**10/10 self-checks passed, exit 0**, < 1 s/run, hermetic. Byte-identical double
run confirmed by external diff + sha256:

- `results.json`   sha256 `5b8060dcf584566bba2e5678909f272ab67759d7ab3f2f0f8d6b003eb5a0bf03`
- `run-stdout.txt` sha256 `9991aba274703847d32072bfa43a7ddfd03b948eb4365afdb47b29028f49181b`
- `fixtures.json`  sha256 `09d61bd92960fecf6348be9725c9da70173d63e8a477cf00d3547070197d9132`

## ⟲ Previous-session review

⟲ previous session = **VERDICT 100**, sim-lab PR #172 → c172698 (idea-engine
**P087**, the hits-to-kill breakpoint-variance comb — an **ACCEPT** at
first-failing-gate None). V100 showed a lower-mean "TIGHT" build beating a
higher-mean "WILD" build at certain HP because hits-to-kill is a discrete
breakpoint comb `ceil(H/mean)` whose sign flips across the HP sweep (signs
+,+,−,+,− over H∈{80,100,140,300,500}), with a variance-free control proving the
win was variance-driven not mean-driven; per-H margins ran 40–110σ, 8/8
self-checks, byte-identical double run. Conventions consumed wholesale into V101:
the **born-red card as the FIRST commit** with the flip as the release-landing
commit; the **CRN shared-input discipline** (V100 reused draws across builds; V101
reuses the identical per-axis streams across the OR-gate, the single-gate control,
and every threshold rung); the **twin-evaluator agreement contract on BOTH the
token AND the first-failing gate**; the **typed margin ledger** (per-seed values →
pooled mean ± SE → margin in σ); the **+13 offset extended one row** (P087→V100 to
P088→V101, twenty-fifth row); and the **SEEDLESS-baton bookkeeping** (next free
block stays 20261730). Carry-forward lesson honored here: V100's ACCEPT rested on a
*control that removed the proposed mechanism and killed the effect* (variance-free
comb); V101 mirrors exactly that shape — the single-gate R4 control removes the
disjunction and the anticorrelation vanishes (−0.013 vs −0.587), which is what
turns "an effect exists" into "THIS mechanism causes it." The one place V101 had to
go BEYOND V100's grammar: the R4 control's 3σ envelope legitimately pokes past the
R1 null band on finite samples, so the reading had to be registered as pooled-MEAN
(not R1's stricter ≥3σ-inside) — a disclosed, spec-honored loosening, the successor
lesson being that a control-arm null and an anchor null need not share the same
band width when their sample sizes differ 4×.

💡 **Session idea (this session):** a **collider-vs-confounder discriminator** probe
as the natural next causal-inference head (candidate PROPOSAL 089 → VERDICT 102).
V101 shows conditioning on a common EFFECT (the OR-gate collider) CREATES a spurious
negative correlation between two independent axes. The dual, and the sharper test of
a verifier's causal literacy, is the common CAUSE: add a shared latent driver `Z`
that loads positively onto both N and R so the *population* correlation is genuinely
POSITIVE, then show that correlation is a confounder by pre-registering that it
VANISHES on back-door stratification by Z — while the V101 collider correlation is
absent in the population and only APPEARS on conditioning. The one hermetic sim would
run both worlds on common random numbers with a 2×2 registration — {collider,
confounder} × {unconditioned, conditioned} — and an APPROVE rule requiring the
diagnostic sign to flip in the correct direction in each cell (collider: 0 → negative
on conditioning; confounder: positive → ~0 on stratification). It converts "we can
detect a selection-induced correlation" into "we can tell WHICH way the conditioning
runs," and it reuses V101's exact scaffolding (separate seeded streams, Acklam Φ⁻¹,
stdlib Pearson r, twin evaluators, the pooled-mean-vs-3σ-band reading) so it is a
one-slice extension, not a rebuild. Deduped against `.sessions/` + `docs/` — no
existing card touches confounder/back-door/stratification.

📊 Model: Claude Opus 4 family · high effort · verifier-build task-class

## Baton

- **Next-2 for the successor:** (1) draft PROPOSAL 089 (the next rotation slot) →
  its **VERDICT 102**, the +13 offset's twenty-sixth row; (2) execute ORDER-010(c)
  kit upgrade v1.15.0 → v1.18.0 — STILL PARKED on owner auth + the ASK-005/006 watch
  (dispatch reports v1.18.0 vs on-disk v1.15.0); a verdict slice does not execute it.
- **Seed baton:** V101 is SEEDLESS — the seeds are the in-file constants S=[1,2,3,4,5]
  (`random.Random(seed)`), NOT a ledger draw; no seed-ledger block consumed, the next
  free block stays **20261730**, inherited unchanged from the V100 baton.
- **Ledger locations:** V001–071 in control/outbox-archive-2026-07.md, V072+ live in
  control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file,
  untouched by verdict slices).

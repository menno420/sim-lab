# REPORT — EXPLORE_ACTION pacing & the quest currency faucet: the third-trigger sweep (PROPOSAL 031)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 031** ·
> 2026-07-13T07:49:09Z · status: sim-ready (idea
> `ideas/superbot-games/explore-action-pacing-quest-mint-2026-07-13.md`,
> landed via idea-engine PR #299, main `6daf5ea`).
> Parent machinery: **VERDICT 018** (`sims/verdict-018-encounter-coexistence/`,
> itself the committed composition of V001 + V008) — all seven chained files
> sha256-pinned in `fixtures.json` and re-verified before any leg runs; the
> committed V018 runner was ALSO re-run out-of-sim in a scratchpad copy before
> this build (exit 0, 1500 self-checks, `results.json` byte-identical @ `b50fd06`).
> Quest-bundle integers quoted verbatim from superbot-games @ `5aec110`
> (TIER_CAPS, GLOBAL_MAX = (20, 120, 50), supply_run required=3) — carried
> inside `fixtures.json`, zero live reads (hermetic per the P017–P030 precedent).
> Run: `python3 sims/verdict-033-explore-pacing/explore_pacing_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic,
parameter-swept): the third-trigger completion sweep of the pipeline's
encounter family. Both live surfaces ride the parents' own committed trace
models (vendored via V018, never re-invented); the only new objects are the
explore attempt stream (one Poisson/paced arrival process), one admission
check against the extended contract, and one integer quest counter per
coupling. This label fills the outbox `evidence: simulation`. Item-faucet
reward VALUE is NOT sim-able and is declared out of scope below (the
parents' wall, restated verbatim, not re-attempted) — while the QUEST
faucet's currency conclusions are in ABSOLUTE native units by construction
(committed in-tree bundle integers), the registered asymmetry, stated
explicitly here.

## PREMISE

Hermetic by registration: "nothing external at sim time — every constant is
quoted in this file and committed as fixture JSON" (the proposal's own
`depends:` line; the P017–P030 hermetic precedent). The premise anchors were
verified at drafting by the proposal (superbot-games `5aec110` finalized the
exploration lane with the pacing constant explicitly host-gated/orphaned;
zero pacing surface at the seam) and travel as pinned constants. The
CHAINED anchor was re-verified live this session BEFORE the build: the
committed V018 runner re-run in a scratchpad copy — exit 0, 1500
self-checks, `results.json` byte-identical to the committed file @ `b50fd06`.

## What the sim MODELS

One player, THREE surfaces, one merged event stream (ties: chat < grid <
explore at equal t — V018's committed rule extended by one tag), 8 h window,
V018's 5 committed parent seeds for the vendored chat/grid surfaces, fresh
explore-layer seeds 20260764–67 (strictly above the P030 high-water
20260763), stdlib-only:

- **Chat / grid surfaces** — the V001 channel machine and the V008
  per-action gate, vendored verbatim via V018 and PROVEN equal, not assumed:
  exact regression to all 15 published parent numbers (V001 0.93/3.00/4.38
  spawns/hr + 4.00 farmer claims/hr; V008 0.20/2.80/5.20 @ 1 h and
  0.05/2.95/4.88 @ 8 h; V018 mixed-deep 3.275 uncapped / 2.875 @ K=4 /
  honest cost 0.400/hr; farmer 8.875 per-source / 4.000 @ K=4) plus 20
  empty-third-surface composition identities (fire logs AND every counter,
  event-for-event per seed, per-source AND C-cap-4, both V018 profiles).
- **Explore surface** — quest-beat attempts as a Poisson stream at r_E/hr
  (honest; the farmer: a deterministic paced 5 s saturating stream, 720
  attempts/hr), each attempt requesting EXPLORE_ACTION admission against the
  per-source clock c_E (c_E = 0: no clock) AND the shared sliding K-window
  over combined admitted encounters. **Gated coupling:** an admitted beat
  advances the active quest by 1. **Free coupling:** progress advances on
  every attempt; encounters fire only when admitted. A quest completes at B
  beats, mints its tier bundle, next quest offered instantly — completions
  == floor(beats/B), asserted per replication against the inline integer
  quest counter. Currency in ABSOLUTE native units: tier II 25/completion
  (the decision center — the tier factor cancels in the MINT ratio, fixtures
  D1), tier III 50 (the adversarial leg of the absolute table).
- **Profiles:** V018's regression pairs unchanged · quest-focused
  (explore-only, r_E = 12/hr; r_E ∈ {6, 30} reporting-only) ·
  mixed-triple-casual (med chat + casual grid + 6 beats/hr) ·
  mixed-triple-deep (V018's mixed-deep + 12 beats/hr — the stress row) ·
  the three-way beat-steering farmer (paced-spam chat + fastmine grid +
  saturating beats; explore-first steering emerges from attempt density —
  any freed budget is re-probed within ≤ 5 s).
- **Sweep:** c_E ∈ {0, 300, 600, 900} s × B ∈ {3, 5, 8} × coupling ∈
  {gated, free} at the COMMITTED K=4 (24 decision cells); the same grid at
  K=6 reporting-only (V018 carved K to the owner and priced it — nothing
  re-pins). M = 10 replications main (seed 20260764), half-M stability leg
  (20260765) that must reproduce the ruling, reporting legs (20260766),
  aux stream (20260767) never read by a decision number.

Bands (committed in `fixtures.json` before the runner, from the proposal
verbatim): **FLOW** — honest quest-focused admitted-beat rate ≥ 80% of the
cell's analytic ceiling min(3600/c_E, K, r_E)/hr AND completions/hr ≥ 0.8 ×
ceiling/B. **FAIR** — mixed-triple-deep keeps chat+grid ≥ 2.375/hr (V018's
committed 2.875 minus the 0.5/hr materiality allowance) AND ≥ 1 admitted
beat/hr. **MINT** — farmer currency/hr ≤ 2.0 × honest quest-focused
currency/hr (ARB_RATIO_MAX = 2.0, V018's committed bound reused).
**25,843 self-checks** tie every cell to its analytic ceiling (independent
sliding-window re-audit, per-source spacing, farmer saturation ≡ K exactly
where analytically guaranteed, quest-counter and bundle-cap identities) and
abort on violation.

## What it SETTLED (the load-bearing claims)

**(1) The third trigger CANNOT ride the shared K=4 window under gated
coupling — REJECT, by the registered first clause, with no knife-edge on
the deciding band.** In GATED coupling at K=4, NO c_E passes all three
bands in ≥ 2 of 3 B values — in fact **0 of the 24 decision cells pass all
three** (per-c_E B-pass counts: {0: 0, 300: 0, 600: 0, 900: 0}). The
stability leg (seed 20260765, half-M) reproduces REJECT.

**(2) FAIR is the binding axis in EVERY cell — the third surface silently
retaxes V018's honest player far past the registered allowance.** The
mixed-triple-deep player's chat+grid drops from V018's committed 2.875/hr
(K=4, two surfaces) to **1.188 / 1.363 / 1.425 / 1.688 /hr** at c_E = 0 /
300 / 600 / 900 — a clip of 1.188–1.688/hr, i.e. **2.4–3.4× the registered
0.5/hr materiality allowance**, vs the 2.375 band. The mechanism is
measured, not assumed: 12 explore attempts/hr claim 2.06–2.73 window
slots/hr from inside the honest player's own budget (explore share of the
mixed-triple-deep player's admitted encounters: 55–70%), and the grid
surface — 93% of the honest player's V018 mint — is exactly what gets
displaced. FAIR's beat half is never the problem (≥ 2.06 admitted
beats/hr everywhere, band 1.0). No c_E in the swept grid can fix this:
the tax DECREASES with c_E (1.688 at 900) while FLOW moves the other way —
the two honest bands scissor.

**(3) FLOW holds only at low c_E, and dies at 900 — the scissor's other
blade.** Honest quest-focused admitted beats: 3.812 / 3.688 / 3.562 /
3.013 /hr vs the 3.200 band (80% of the ceiling min(3600/c_E, K=4, 12) =
4/hr everywhere) — c_E = 900 fails on rate (the Poisson-wait arithmetic:
clock 900 s + mean 300 s attempt gap ≈ 3/hr = 75% of ceiling). The
completion half adds the disclosed B=8 squeeze (ceiling 0.5
completions/hr): measured 0.400 / 0.375 / 0.375 / 0.338 — B=8 passes only
at c_E=0. FLOW pass set (rate AND completions, gated K=4): c_E=0 {B3,5,8},
300 {B3,5}, 600 {B3}, 900 {} — with two knife-edge completion cells
disclosed (600|B5: 0.637 vs 0.640; 300|B8: 0.375 vs 0.400), neither able
to affect the ruling (FAIR already fails those cells by wide margins).

**(4) MINT: under GATED coupling the K-window closes the value-steering
channel — the farmer cannot out-mint the honest quest player.** Farmer
mint ratio at the tier-II center, gated K=4: **max 1.053** across all 12
cells (1.031 / 0.674 / 0.593 / 0.519 at B=3; the cap pins the farmer's
combined at exactly 4.000/hr in every K=4 replication — the saturation
gate — and steering splits its budget: explore share 97% at c_E=0 falling
to 42% at 900 as the c_E clock forces the budget back into chat+grid).
MINT passes all 24 gated cells (both K). The adversarial cross-tier ratio
(farmer steering into tier III vs honest at the II center) peaks at 2.06
(c_E=0, B=3) — reporting-only, disclosed: tier selection is the bracket,
not the sweep.

**(5) MINT under FREE coupling fails catastrophically — the quantified
proof that the lane's per-completion host gate is load-bearing.** With
progress on every attempt, the saturating farmer completes 720/B quests/hr
regardless of c_E: **6,000 currency/hr at tier II (12,000 at tier III) vs
the honest player's 93.75 — ratio 64–66×** in every free cell. Free
coupling makes encounter pacing irrelevant to the faucet: the ONLY mint
control left is the host's per-completion gate (exactly where the lane's
economy sim put it). This is the first encounter-family conclusion in
absolute native units — the registered asymmetry: quest-currency numbers
are absolute BY CONSTRUCTION (committed bundle integers @ `5aec110`);
chat/grid mint stays RATE-terms-only behind the parents' wall.

**(6) The absolute mint ceiling table (shipped regardless of ruling, the
row's first value line).** Honest quest-focused ceiling: 30.31 currency/hr
(c_E=0, B=3, tier II; 8.44 at the 900|B8 floor). Gated farmer ceiling:
31.25/hr tier II / 62.50/hr tier III (c_E=0, B=3) — bounded by K/B ×
bundle by construction. Free farmer: 6,000 / 12,000/hr. Every row passes
the bundle-cap identity (currency ≡ completions × tier, tier ≤ GLOBAL_MAX
component-wise, exact integers).

**(7) K=6 (reporting-only — V018's priced owner knob, not re-opened)
does not rescue gated coupling.** It halves the honest tax (deep chat+grid
1.575 / 1.962 / 2.312 / 2.550) and FAIR finally passes at c_E=900 — but
FLOW fails there (3.013 < 3.200) and everywhere FAIR passes: 0 all-band
cells at K=6 either. The scissor is structural, not a K=4 artifact:
per-axis pass shares (K=4 decision cells) — FAIR 0% everywhere; FLOW
100/83/67/0% across c_E; MINT 100% gated, 0% free.

**Pre-registered REJECT consequence (ships verbatim):** EXPLORE_ACTION
encounters JOIN the combined K-window (namespace unchanged, both parents'
defaults untouched), but quest PROGRESS must NOT be admission-gated — the
FREE coupling becomes the contract line; the lane pins quest pacing at its
own per-completion host-gate frame; the CONTRACT.md slice and the Q-0186
Encounters-cog build get the carve-out with the starvation table above
(claims 2, 3, 5 are the quantified rows: the honest tax 1.2–1.7/hr, the
900 s starvation, and the 64× free-coupling mint that the host gate must
absorb).

## What it did NOT settle

- **Item-faucet reward VALUE — the parents' wall, restated verbatim:** "no
  live fishing/mining earn-rate baseline exists, so loot values stay
  provisional and the slice must log the same named telemetry." Chat/grid
  mint conclusions here are RATE/fraction-only. The quest faucet is the
  registered exception — absolute by committed in-tree integers — and this
  asymmetry is stated, not smoothed.
- **dnd's escort bundle** — the other host-gated faucet, out of scope
  (different trigger surface); the natural follow-up now that MINT is shown
  to bind on the free side.
- **Tier selection** — bracketed {II center, III adversarial}, never swept;
  the decision ratio is tier-cancelling by fixtures D1, and the one bracket
  cell that crosses 2.0 (adversarial 2.06 at c_E=0|B3) is reported, not
  ruled on.
- **Real beat rates** — r_E is a dial until the named telemetry lands; the
  honest profiles BRACKET it (r_E ∈ {6, 30} reporting: at r_E=6 FLOW's rate
  half fails at every c_E ≥ 300 — a SLOWER honest player is starved even
  sooner; at r_E=30 it passes everywhere), and the farmer is the optimizing
  adversary.
- **K** — not re-opened: K=4 decision-binding (V018's committed row), K=6
  reporting-only against V018's own priced owner knob.
- **Live interleaving and resolution content** — V018's own disclosed
  limits, inherited unchanged.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The two live surfaces are two finalized verdicts' own fixtures, reproduced
exactly (15 regression numbers + 20 composition identities). New
abstractions: the explore attempt stream (Poisson honest / paced farmer —
r_E disclosed as a dial and bracketed both directions, with the slower
bracket failing FLOW even harder, so no plausible r_E flips the REJECT) and
instant quest re-offer (a live offer delay only LOWERS completion rates —
conservative for FLOW, and FAIR/MINT don't read completions on the deciding
side). The deciding FAIR failure is displacement arithmetic inside a
capped window — it survives any interleave stylization that keeps the
parents' own committed profiles (which are the regression-pinned ones).

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **25,843 self-checks, 0 failed**, exit-coded: sha256 pins on all
seven chained machinery files before any leg; exact regression to all 15
published parent numbers; 20 event-for-event composition identities;
per-cell analytic ceilings; per-source spacing audits (chat 900 / grid 600
/ explore c_E); an independent sliding-window re-audit recomputed without
the deque; farmer saturation ≡ K exactly on every replication where
analytically guaranteed (the one non-guaranteed reporting cell scoped by a
pre-runner fixtures amendment, committed before the runner existed);
quest-counter and bundle-cap identities per replication; 3 expect_reject
negatives; in-process full-sweep determinism with all CRN caches cleared.
Seeds: V018's 5 parent seeds × M=10 fresh explore substreams; the half-M
stability leg on its own seed reproduces the ruling; a 4×-M aux re-measure
confirms the FAIR margins (1.141–1.609 — the band never within reach). The
FULL 24+24-cell table is printed and committed; failures are first-class.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The REJECT is margin-free on its deciding band: FAIR fails all 24 decision
cells by 0.687–1.187/hr against a 0.5/hr-allowance band — no seed,
tolerance, or profile tweak closes a gap that is 2.4–3.4× the allowance
(aux 4×-M agrees; the stability leg agrees; K=6 shows the same scissor).
Two FLOW completion cells are knife-edge (0.003 and 0.025/hr) and are
disclosed — both sit inside cells FAIR already fails by > 1.0/hr, so they
cannot affect the ruling under the registered conjunction. The free-side
MINT failure is 64× against a 2.0 bound — structural arithmetic
(720/B completions/hr), not sampling.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, stdlib-only, fixed seeds, no network / git
/ wall clock / hash(); stdout AND `results.json` byte-identical across two
complete process runs by external diff (sha256 stdout `fd4cab3f…`, results
`86414288…`); cpython-3.11 pinned and asserted; ~5 s.

**5. "LIMITS? what this evidence does NOT show."**
It does not show item-faucet VALUE (the wall above); does not measure real
beat rates or interleaving (bracketed); does not sweep tier selection or
dnd's escort; does not re-open K or either parent default; and the
free-coupling contract line it recommends is a carve-out whose server-side
implementation (progress decoupled from admission, atomic host gate at
completion) is an engineering obligation the row states, not a thing this
sim can prove about unwritten code.

## EVIDENCE STRENGTH: **moderate–strong** — gate PASS

Gates 2 and 4 are strong (exact three-layer regression, 25,843 checks,
byte-identity, the anchor re-run out-of-sim); gate 3 is decisive (the
deciding band fails everywhere by multiples of its allowance, cross-checked
at 4× replication). Short of strong only because the honest-profile
interleave is stylized (the parents' own inherited limitation) and r_E is a
dial until the named telemetry lands. Under the README rule the sim
**PASSES** the gate for every claim it makes; the item-VALUE half was never
in scope.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `reject`** — the pre-registered REJECT arm, evaluated FIRST
  and hit exactly: in gated coupling at K=4 no c_E passes the three bands
  in ≥ 2 of 3 B values (0/24 cells pass; FAIR 0/24, the binding axis;
  stability-reproduced). "The third trigger cannot ride the shared window —
  carve quest progress out of admission-gating before the cog build fixes
  it."
- **THE CARVE-OUT ROW (for superbot-games' CONTRACT.md slice and the
  Q-0186 Encounters-cog build):**
  - **EXPLORE_ACTION encounters JOIN the combined K=4 window** (V018's row
    extends unchanged: per-source clocks at both parents' pinned defaults,
    K=4 per sliding 3600 s across ALL triggers — nothing re-pins).
  - **Quest PROGRESS must NOT be admission-gated — FREE coupling is the
    contract line.** Gated coupling measurably starves both honest bands:
    the mixed player loses 1.19–1.69/hr of chat+grid (vs the 0.5/hr
    allowance) at every swept c_E, and the quest player drops to 75% of
    ceiling at c_E=900 — the two bands scissor with no passing window.
  - **The lane's per-completion host gate is LOAD-BEARING and stays** (the
    lane's own economy-sim frame): under free coupling the encounter window
    provides ZERO mint protection — the saturating farmer mints 6,000
    currency/hr absolute (12,000 at tier III) vs honest 93.75 (64–66×).
    The host gate is the only control on that channel; the carve-out ships
    with this number attached.
  - **The absolute mint ceiling table** (first native-unit pin, tier II
    center / tier III adversarial): honest quest-focused ≤ 30.31/hr;
    gated farmer ≤ 31.25 / 62.50/hr; free farmer unbounded by pacing —
    bounded only by the host gate.
- **Telemetry (the parents' named lists EXTEND — the cheapest live probe,
  from the proposal's own consequence line):** the cog build ships V018's
  combined-window telemetry EXTENDED with per-trigger admitted/denied beat
  counts + per-player quest currency/day — measuring r_E and the real
  coupling cost at zero new tooling.
- **Not re-opened:** both parents' pinned defaults, V018's namespace + K=4
  row (this sweep's failing cells are all EXTENSIONS of the row, not the
  row), K itself (K=6 reporting: same scissor, no passing cell).
- **Natural follow-up if the carve-out lands:** dnd's escort bundle — the
  other host-gated faucet — under the same free-coupling + host-gate frame.
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015/V016/V017 slice boundary, with header timestamps from
live `date -u` at append time. -->

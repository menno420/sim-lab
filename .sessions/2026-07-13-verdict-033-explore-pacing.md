# Session — VERDICT 033 — EXPLORE_ACTION pacing & the quest currency faucet: V018's excluded third trigger, priced (idea-engine PROPOSAL 031)

> **Status:** complete
> 📊 Model: fable · 2026-07-13 · verdict-033 slice-worker session
> Objective: settle idea-engine PROPOSAL 031 (control/outbox.md · 2026-07-13T07:49:09Z · status: sim-ready; idea `ideas/superbot-games/explore-action-pacing-quest-mint-2026-07-13.md` @ idea-engine main 6daf5ea, PR #299 — the ORDER 003 GAME-MECHANICS rotation slot, round 4: V018 pinned the two-trigger contract row and ruled EXPLORE_ACTION out of its own sweep verbatim; the lane finalized @ superbot-games 5aec110 with the pacing constant explicitly host-gated/orphaned). Build the fully hermetic pre-registered composed sweep: V018's committed machinery (V001 chat machine verbatim + V008 grid gate verbatim + the contract state machine, sha256-pinned and regression-anchored) EXTENDED with the third surface — quest-beat attempts as a Poisson stream at r_E/hr, each attempt requesting EXPLORE_ACTION admission against the per-source clock c_E AND the shared sliding K-window; admitted beats advance the active quest by 1 under GATED coupling / progress advances on every attempt under FREE coupling with encounters firing only when admitted; a quest completes at B beats, mints its tier bundle (tier II 25-currency center, tier III 50 adversarial leg — TIER_CAPS/GLOBAL_MAX quoted verbatim @ 5aec110), next quest offered instantly. Sweep c_E ∈ {0, 300, 600, 900} s × B ∈ {3, 5, 8} × coupling ∈ {gated, free} at the COMMITTED K=4 (24 decision cells); the same grid at K=6 reporting-only. Profiles: V018's regression pairs unchanged · quest-focused (explore-only, r_E = 12/hr; r_E ∈ {6, 30} reporting-only) · mixed-triple-casual (med chat + casual grid + 6 beats/hr) · mixed-triple-deep (V018's mixed-deep + 12 beats/hr) · three-way beat-steering farmer (paced-spam chat + fastmine grid + saturating beat attempts, admission budget spent explore-first). Bands: FLOW (honest quest-focused admitted-beat rate ≥ 80% of the cell's analytic ceiling min(3600/c_E, K, r_E)/hr AND completions/hr ≥ 0.8 × ceiling/B) · FAIR (mixed-triple-deep keeps chat+grid ≥ 2.375/hr AND ≥ 1 admitted beat/hr) · MINT (farmer currency/hr ≤ 2.0 × honest quest-focused currency/hr, ARB_RATIO_MAX = 2.0; ABSOLUTE currency/hr table shipped regardless of ruling). Gates, run invalid on any failure: exact regression to V018's published set (mixed-deep 3.275/2.875/0.400; farmer 8.875/4.000; V001 0.93/3.00/4.38 + 4.00; V008 0.20/2.80/5.20), empty-third-surface composition identity to the V018 machine event-for-event per seed, per-cell analytic ceilings, independent sliding-window re-audit, bundle-cap identity, stdout + results.json byte-identical across two process runs, CPython minor pinned. Seeds 20260764 main / 20260765 stability (half-M, must reproduce the ruling) / 20260766 reporting / 20260767 aux — strictly above the P030 high-water 20260763. Decision (registered order, REJECT first): REJECT iff in GATED coupling at K=4 NO c_E passes all three bands in ≥ 2 of 3 B values; APPROVE iff ∃ ≥ 2 consecutive c_E grid values passing all three bands at K=4 GATED for ALL B, stability-reproduced; NULL otherwise (flip axis named via per-axis pass shares). Hermetic: every constant a pinned fixture committed with the sim; zero repo/network reads at run time.

## What happened

Anchor FIRST: before any build, the committed V018 runner was re-run in a
scratchpad copy — exit 0, 1500 self-checks, `results.json` byte-identical
to the committed file at main `b50fd06` (its own manifest sha256 pins on
the V001/V008 parents verified in-run). Then built
`sims/verdict-033-explore-pacing/` — stdlib-only NUMERIC SIMULATION
(rung 1), fully hermetic (reads only its own committed `fixtures.json` +
the sha256-pinned sibling machinery files, all seven re-verified before
any leg). Fixtures committed BEFORE the runner (8 intake-time decisions —
most load-bearing D1, the tier-cancelling MINT center with the cross-tier
adversarial ratio reporting-only; D5, completions == floor(beats/B) with
the inline integer counter asserted, making gated/free cells share
admission metrics exactly; D3, the farmer's 5 s paced saturating probe);
one pre-runner fixtures amendment scoped the farmer-saturation exactness
gate analytically (min(3600/c_E, 720) ≥ K) — committed before any code
ran, the V031 amendment discipline.

**Run:** `SELF-CHECKS: 25,843 passed, 0 failed`, exit 0, ~5 s;
byte-identical stdout + results.json across two process runs by external
diff (sha256 stdout `fd4cab3f…`, results `86414288…`). All 15 published
parent numbers reproduced exactly; 20 event-for-event composition
identities. **Ruling: REJECT (the registered first clause, met exactly)**
— in gated coupling at K=4 no c_E passes all three bands in ≥ 2 of 3 B
values: 0/24 decision cells pass, FAIR the binding axis in EVERY cell
(mixed-triple-deep chat+grid 1.188–1.688/hr vs the 2.375 band — a clip of
2.4–3.4× the registered 0.5/hr allowance; the honest bands scissor: FLOW
dies at c_E=900 exactly where FAIR's tax is smallest; K=6 reporting shows
the same scissor). MINT passes all 24 gated cells (farmer center ratio
≤ 1.053, combined pinned at exactly 4.000/hr) and fails all 12 free cells
at 64–66× (farmer 6,000 currency/hr absolute vs honest 93.75) — the
quantified proof the lane's per-completion host gate is load-bearing.
Stability leg reproduces REJECT; aux 4×-M confirms the FAIR margins. The
pre-registered REJECT consequence ships: encounters join the K-window,
quest PROGRESS is not admission-gated (free coupling is the contract
line), the host gate stays, and the CONTRACT.md slice + Q-0186 build get
the carve-out with the quantified starvation table.

Landed: INTAKE 031 (2026-07-13T08:25:46Z) + VERDICT 033
(2026-07-13T08:25:47Z) appended to `control/outbox.md` (append-only;
VERDICT 032 = PROPOSAL 030's landed @ c7340ae BEFORE this append — tail
re-verified at origin/main HEAD, this slice's unpushed branch re-stacked
onto it, numbers kept per the reserved +2 offset); verdict PR from
`claude/verdict-033-explore-pacing`. Worker session — no heartbeat
writes; this card flip is the last commit.

## 💡 Session idea

Pre-register the FLOW-style band's ceiling with its waiting-time term
included. FLOW compared the measured admitted rate against 80% of
min(3600/c_E, K, r_E) — a ceiling no Poisson attempt stream can approach
at high c_E because the renewal spacing is c_E + E[wait] = c_E + 3600/r_E,
not c_E. At c_E=900, r_E=12 the achievable rate is ~3.0/hr = 75% of the
registered ceiling, so that grid edge fails FLOW by construction for ANY
honest player, and the sim spends replications measuring an arithmetic
fact. The portable rule: when a band is "≥ x% of ceiling", register the
ceiling as the renewal-theoretic achievable rate (min(3600/(c_E +
3600/r_E)·…, K)) or explicitly disclose that the band prices the waiting
overhead as starvation (this run's reading — defensible, but it should be
chosen at registration, not discovered as a scissor blade). Here it could
not matter (FAIR failed everywhere by multiples of its allowance) but on
a closer grid the ceiling convention alone could flip REJECT↔NULL.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-032-adaptive-versioning.md` (the sibling
that landed while this slice was dispatched): complete and honest — its
merge-not-rebase race handling on a PUSHED branch, the reserved-number
discipline ("the number RESERVES, never the position"), and its one
disclosed pre-run correction all held; this session reused the cheaper
unpushed-branch form (re-stack onto the advanced origin/main, tail
re-verified pre-append) exactly as V031 did before it — the race
protocol is now proven in both branch states. Its 18-decisions-in-fixtures
trail is the deepest yet; this session's 8 + one pre-runner amendment
followed the same fixtures-first choreography and found the discipline's
real payoff: the amendment (scoping the farmer-saturation gate) was
forced by pre-runner analytic thinking, BEFORE results could bias it.
One export it could not give: its bands were medians over hundreds of
cells; this run's deciding band was a single profile's rate, where the
ceiling-convention issue above (this card's 💡) is sharper — new
material, not inherited.

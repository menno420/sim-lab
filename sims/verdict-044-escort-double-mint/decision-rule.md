# VERDICT 044 — pre-registered decision rule (DND-ESCORT-DOUBLE-MINT)

Registered 2026-07-13T10:58Z, BEFORE any probe was run. Pin: menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94. Modules byte-copied to `verdict-044/modules/` (sha256 in `manifest.sha256`).

## Ruling options

- `intended` — the 2× mint per traversal is ratified as-is.
- `mint-at-most-once` — recommend a concrete guard (named function + insertion point) so one escort mints the `safe_passage` bundle at most once.
- `NULL` — design intent genuinely undecidable from committed evidence at the pin.

## B0 gate (validity, must pass before any probe counts)

Drive ONE traversal through the byte-copied modules exactly as the packet describes: `waystation_road · advance_escort` → `waystation_gate · circle_to_treeline` → `treeline_watch · signal_escort`, via the audited seam `services.dnd_workflow.choose` with `DnDState()` defaults (seed=0, xp=0, player_id="player"), injected fixed `now` + counter mutation-id factory (zero wall-clock/uuid nondeterminism; the engine path itself has zero decision-bearing RNG — DetRng is seeded but the escort outcome is deterministic).
- B0 PASSES iff the traversal produces exactly TWO `safe_passage` COMPLETED events with TWO minted bundles, each exactly `TIER_CAPS[RewardTier.I] = RewardBundle(global_xp=5, game_xp=25, currency=10)`, running totals ending at g10/x50/c20, and two `reward:*` audit rows.
- If B0 FAILS: the headline is the non-reproduction; characterize actual behavior and rule on THAT (the ruling options above still apply to the actual behavior).

## Measurable criteria and thresholds (fixed up front)

### C1 — reward-scale consistency
Compare the traversal's 2× total, `2 × TIER_CAPS[I] = (global_xp=10, game_xp=50, currency=20)`, against the committed catalog scale at the pin (`games/exploration/quest/catalog.py`):
- TIER_CAPS[II] = (10, 60, 25); TIER_CAPS[III] = GLOBAL_MAX = (20, 120, 50).
- WITHIN-SCALE iff the 2× total is ≤ TIER_CAPS[II] component-wise (i.e., one traversal of the tier-I escort pays no more than one tier-II quest, the catalog's own next rung).
- SCALE-BREAKING iff the 2× total exceeds TIER_CAPS[II] on any component, or exceeds GLOBAL_MAX on any component.
- Threshold declared: WITHIN-SCALE leans `intended`; SCALE-BREAKING leans `mint-at-most-once`.

### C2 — loopability / farmability (the dominant criterion)
Mechanically test, in the byte-copied modules, whether the mint is repeatable beyond 2× in one session:
- (a) after `signal_escort` at `treeline_watch` (`next_scene_id=None` ⇒ state.scene_id unchanged per the seam's documented "stays" semantics), is `signal_escort` still choosable and does it mint again?
- (b) is any cooldown, one-shot flag, per-quest-instance persistence, or scene-re-entry block present anywhere on the path (DnDState, choose, resolve, _escort_step, engine)? (Each `_escort_step` runs a FRESH offer→accept→apply_event→grant_rewards cycle — verify no persisted instance blocks a repeat.)
- UNBOUNDED iff N=10 repeated legal (non-clamped) choices mint 10 bundles with totals = 10 × TIER_CAPS[I].
- Threshold declared: if UNBOUNDED, `intended` CANNOT be the ruling (the packet's own framing "one escort mints 2×" understates the surface; an uncapped faucet on a tier-capped catalog contradicts the catalog's stated cap discipline "always <= GLOBAL_MAX" as an economy invariant). UNBOUNDED ⇒ `mint-at-most-once` unless committed text at the pin explicitly blesses repeatable escort minting (C3 overrides only with explicit language).
- If BOUNDED at exactly 2× per session (some mechanism stops the 3rd mint), C2 is neutral and C1+C3 decide.

### C3 — design-doc / comment language at the pin
Search committed text (docs/, module docstrings/comments, tests, the packet itself) for once-per-escort vs per-step language:
- Counts for `mint-at-most-once`: any committed statement that the safe_passage bundle/reward is granted once per escort/quest/completion (e.g., "mints exactly TIER_CAPS[RewardTier.I]" phrased per-ESCORT), or a test asserting a single mint per arc.
- Counts for `intended`: any committed statement that each escort STEP mints, or a test asserting the 2× total.
- Neutral if only per-choice language exists ("a valid escort choice mints exactly ...") with no per-escort ceiling stated.

## Decision rule (apply in this order)

1. If B0 fails → rule on actual behavior; if actual behavior makes the packet's question moot, say so and rule on the real mechanism.
2. If C2 = UNBOUNDED and C3 does not explicitly bless repeat minting → `mint-at-most-once`.
3. Else if C1 = SCALE-BREAKING → `mint-at-most-once`.
4. Else if C2 bounded at 2× AND C1 WITHIN-SCALE AND C3 neutral-or-blessing → `intended`.
5. Else (criteria conflict irreconcilably, or C3 is the only discriminator and is silent both ways with C1/C2 split) → `NULL`.

## Guard recommendation shape (if mint-at-most-once)

Must name the exact function and insertion point. Candidates to be priced in the probes (fix-surface probe): (a) a seam-level one-shot flag on `DnDState` checked/set in `services/dnd_workflow.choose` (or `_fold_reward`); (b) scene rewiring in `games/dnd/data/scenes.py` (one of the two `escort_step` wirings becomes `scout_narrate`); (c) an engine-level persisted-instance check (largest surface). The recommendation picks the smallest surface that closes BOTH the 2× and any unbounded loop found in C2.

## Determinism policy

Zero decision-bearing RNG anywhere in the escort path (verified by module read; DetRng streams are seeded but unused by outcomes). Injected `now=datetime(2026,7,13,12,0,0,tzinfo=utc)` and mutation-id factory `f"m{counter:04d}"` for byte-identical audit rows. No seeds drawn from the fleet seed ladder needed; if any MC leg is added it registers seeds strictly above 20260880 (fleet high-water at sim-lab 48dd6a6).

# REPORT — owner-001: superbot-next settings / command / UX surface vs superbot

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: owner request (owner-001) — "did superbot-next improve the settings/command/UX surface, and by how much?"
> Run: `python3 sims/owner-001-superbot-next-settings-ux/settings_ux_sim.py`
> Inputs: `data/{next,old}/{settings,commands,panels}.json` (verbatim inventories).
> Pinned SHAs — superbot-next (NEW) `168ef8080347905766893fd92ae3be1ec2ebbc4c`; superbot (OLD) `9f46cb7840cb2216a012002fe27feb342d45f480`.

## METHOD LABEL: NUMERIC SIMULATION (rung 1–2, measured-from-code) + JUDGMENT-ONLY on "overall UX-improved"

This is the cheapest ADEQUATE evidence for the surface question: every structural
claim (inventory diff, dead/display-only counts, co-read collapse, reachability
graph depths, discoverability) is **measured** from the committed inventories at
pinned SHAs and self-checked. The seeded config-space number is a declared MODEL
(rung-1 sim, read-site-activation proxy), reported as SUPPORTING only. The final
"is the UX actually better for users, and by how much" question has no ground
truth reachable here (no users, no telemetry) and is carried as JUDGMENT-ONLY.

## What it MODELS / MEASURES

- **Inventory diff** (measured): settings matched by exact `name`
  (kept/added/removed/moved); commands matched by name normalized across the
  `/`-vs-bare prefix convention change; rename CANDIDATES flagged, never asserted.
- **Redundancy** (measured, from `read_where`): dead (no reader / `NO READER`),
  display-only (every read site is a `panels.py` render), duplicate-effect
  (identical read-site sets), subordinate (read-set strict subset of a master
  toggle).
- **Combinability** — structural co-read collapse (ROBUST, measured: group
  settings by identical read-site set per subsystem) + a seeded config-space
  DEMONSTRATION (SUPPORTING): dims = bool/enum settings, each a binary coord
  (default=0 / enabled-or-non-default=1); a config vector's "behavior signature"
  = UNION of read-site sets of its set bits; `collapse_ratio = distinct_signatures
  / n_sampled`. SEEDS = `[11,23,42,101,2027]`, K=256 (exhaustive when 2^dims≤256).
  **This is an abstraction — it does NOT execute real branch logic.**
- **Reachability** (measured graph): directed edges command→panel (opens_panel /
  opened_by), panel→panel (button navigation / parent-panel), panel→setting
  (`set_where` terminal panel), and the settings-hub subsystem-select wiring.
  `steps_to_reach` = multi-source BFS edge distance from the nearest entry
  command (≈clicks). Discoverability = BFS from the single `/settings` entry.
- **UX delta** (measured proxies): signed OLD→NEW deltas; regressions named.

556 self-checks; 5 seeds; full tables/distributions in `results.json`; byte-identical re-run.

## What it SETTLED (the load-bearing claims)

**Inventory (measured).** Settings NEW 125 vs OLD 118: **100 kept, 25 added, 18
removed, 2 moved** (`moderator_tier_role_id`, `trusted_tier_role_id`:
moderation→governance). Partition invariants hold (100+25=125; 100+18=118).
11 rename CANDIDATES flagged (dot-namespacing + type-label change
`str`→`binding:channel`, e.g. `welcome_channel`→`welcome.channel`,
`logging_mod_channel`→`logging.mod_channel`) — **candidates, not confirmed
renames**. Commands: raw **367 vs 484 (Δ −117)**; distinct-normalized 362 vs 365
(212 kept, 150 added, 153 removed). Biggest command cuts: `diagnostic` −19,
`ai_review` −11, `project_moon` −11 (renamed to `projmoon` +11 — a near-wash),
`setup` −11, `utility` −9, several `btd6_*` sub-namespaces folded away.

**Redundancy (measured).**
- **Dead** (no reader): NEW **8** `[ai.audit_log_channel,
  btd6_strategy_submission_channel, cleanup_spam_window_seconds,
  deathmatch_turn_timeout, moderation.public_log, skip_roles,
  welcome_card_enabled, welcome_min_account_age_days]`; OLD **5**
  `[btd6_cache_circuit_breaker_threshold, btd6_cache_default_interval_seconds,
  btd6_cache_freshness_warning_hours, btd6_strategy_submission_channel,
  skip_roles]`. **Δ +3 dead in NEW.**
- **Display-only** (read ONLY at a `panels.py` render, never a service/engine):
  NEW **19**, OLD **0**. The 19 are **all of `image_moderation` (8) + `security`
  (11)** — NEW ships a full image-moderation and raid/age-gate settings surface
  that is wired only to panel rendering, not to any enforcement engine in the
  inventory. **Headline defect.**
- **Duplicate-effect groups** (identical read-site sets): NEW 9, OLD 13. OLD's
  groups are subsystem-wide (all 15 automod, all 10 ai, all 12 welcome settings
  share one read site) — an artifact of OLD's single config-projection/load-policy
  loader. NEW's are smaller/granular except logging (11 channel bindings share one
  resolver) and the display-only security(9)/image_moderation(8) groups.
- **Subordinate pairs**: **0** in both (masters and their would-be subordinates
  read the SAME single site — equal, never a strict subset — so no strict
  subordination is measurable).

**Combinability.** Structural co-read collapse (ROBUST): OLD collapses nearly
every subsystem to one read site (ai {10}, automod {15}, welcome {12},
security {11}, moderation {13}+{2}) — its scalars funnel through one projection
loader. NEW is granular (most subsystems no collapse) EXCEPT logging {11}+{7},
and the display-only security {9}+{2} and image_moderation {8}. Seeded
config-space ratio (SUPPORTING, mean±sd over 5 seeds) confirms the direction:
NEW `collapse_ratio` = 1.0000±0 for ai/automod/moderation/role/welcome (behavior
signatures fully distinct — settings gate independent read sites), vs OLD
0.0156–0.25 (near-total collapse). NEW's LOW-ratio subsystems — image_moderation
0.0625, security 0.1250, logging 0.0406 — are low **because** they're display-only
(sec/img_mod) or share one binding resolver (logging), i.e. the low ratio there
reflects DEAD/undifferentiated wiring, **not** intentional combinability. The
model conflates "co-read" with "combinable"; interpret per subsystem.

**Reachability (measured graph).**
| metric | NEW | OLD |
|---|---|---|
| settings reachable | 125/125 | 108/118 |
| unreachable | **0** | **10** |
| avg steps | 3 | 2.907 |
| median steps | 3 | 3 |
| max steps | 3 | 3 |
| depth distribution | {3:125} | {2:10, 3:98} |
| discoverability from `/settings` | **125 (100%)** | **108 (91.5%)** |

NEW puts **every** setting at a uniform 3 clicks and reaches **100%** of settings
from the single `/settings` hub. OLD leaves **10 settings unreachable** from any
panel (`active_tournament, ai_review_channel, governance_version, skip_roles,
btd6_strategy_submission_channel` + 4 btd6 cache internals + `btd6_ct_group_id`)
— set only via runtime/service/command paths, never surfaced in the settings UI.
**Robust win: NEW unified settings discoverability to 100% (+8.5pp, +10 settings
brought under the hub).** Consistency over 100 matched settings: **86 same, 0
shallower in NEW, 10 deeper in NEW, 4 incomparable**. Task battery (one
alphabetical-first matched setting per subsystem, 17 tasks): mean clicks NEW 3.00
vs OLD 2.93 (Δ +0.067).

**The one measured REGRESSION — and why it likely does NOT survive scrutiny.**
The 10 "deeper in NEW" settings are the entire `ai` subsystem: in OLD the graph
reaches them at 2 clicks (`ai` cmd → `AIPanelView` → setting), in NEW at 3
(`/ai` → `ai.hub` → `ai.settings` → setting), also reflected in the ai task
(`ai_cooldown_seconds` +1). **But** OLD's `panels.json` has only 29 panels vs
NEW's 165: OLD's intermediate AI-settings sub-panel
(`_build_ai_settings_panel`, referenced but not captured as a node) is collapsed
into one hop, so OLD's true AI depth is plausibly 3 as well. This apparent
regression is **most likely a panel-inventory-granularity artifact, not a real
extra click** — see gate Q1/Q5. It is reported, not asserted as a real regression.

**UX delta (signed OLD→NEW, `better` direction noted).**
| metric | NEW | OLD | Δ | better | reading |
|---|---|---|---|---|---|
| total_settings | 125 | 118 | +7 | n/a | — |
| dead_settings | 8 | 5 | **+3** | lower | REGRESS |
| display_only_settings | 19 | 0 | **+19** | lower | REGRESS (headline) |
| unreachable_settings | 0 | 10 | **−10** | lower | WIN |
| discoverability_fraction | 1.000 | 0.915 | **+0.085** | higher | WIN |
| mean_steps_to_reach | 3.00 | 2.907 | +0.093 | lower | regress (AI artifact) |
| median_steps_to_reach | 3 | 3 | 0 | lower | flat |
| max_steps_to_reach | 3 | 3 | 0 | lower | flat |
| mean_task_battery_clicks | 3.00 | 2.933 | +0.067 | lower | regress (AI artifact) |

## AI PANEL — independent audit (mixed: measured file:line evidence + UX judgment)

> These are AI-panel improvables found **INDEPENDENTLY** by a read-only source audit of
> `sb/domain/ai/*` + `sb/kernel/panels/*` cross-referenced against OLD (`superbot/disbot/views/ai/*`,
> `cogs/ai_cog.py`). The owner suspected the AI panel had issues; we did **not** ask what he saw —
> every finding below is our own, each cited `file:line`. Severity mix per `findings.json`: **3 high,
> 4 medium, 1 low**.

**Flow characterization (entry → panels → widgets).** `!ai` / `!aimenu` / `/aimenu` all route to
`PanelRef("ai.hub")` (`sb/manifest/ai.py:101-141`). The hub is a live status embed (💤/⚠️/✅ over six
diagnostics fields, `operator_cards.py:188`, rendered by `panels.py:1116-1122`) above two button rows:
a **diagnostics quartet** Refresh / Diagnostics / Providers / Routing (`panels.py:144-196`, the latter
three are `HandlerRef`s into `service.py:140-159`, each presented via `_card`→`open_panel("ai.card")`)
and a **config quartet** Settings / Policy / Behavior / Tools that does in-place page swaps
(`ai.settings` typed edit/reset widgets through the audited `settings.set_scalar` op; `ai.policy_chooser`;
`ai.behavior_chooser`; `ai.tools_chooser`). Every widget/chooser page carries a `↩ Back` route **except
`ai.card`**, which carries none.

| id | sev | title | file:line | fix |
|---|---|---|---|---|
| AIP-01 | **high** | Tools chooser entirely non-functional — all 4 buttons dead-end to `chooser_scope_pending` | `sb/domain/ai/panels.py:434-439` (+224-234; `settings_widgets.py:367-385`) | wire the 4 tools pickers to real orchestration pages, or hide the Tools hub button until the slice exists |
| AIP-02 | **high** | Operator cards (`ai.card`) render no back/home/help — Diagnostics/Providers/Routing + both Preview flows strand the operator | `sb/domain/ai/panels.py:206-207` (+1125-1139; escapes never-strand fence via `compile.py:139-144`) | give `ai.card` a back route, or render diagnostics onto the hub view (retaining its buttons) as OLD did |
| AIP-03 | **high** | Doubled prefix in every settings ack/prompt: shows `ai.ai_enabled` (option value = `settings_key` formatted as `ai.{key}`); same embed's Scalar field prints single-prefix `ai_enabled` | `sb/domain/ai/panels.py:825-829` (+869; acks `settings_widgets.py:172/185/…/352`) | use `spec.name` as the option value (or strip leading `ai_`); align both spellings |
| AIP-04 | medium | Behavior "Routing matrix" button dead-ends (`chooser_scope_pending`) and overloads the word "Routing" (a live hub button already owns it) | `sb/domain/ai/panels.py:357-358` (+161-162; `settings_widgets.py:362-366`) | wire it to the dry-run resolver (reuse the preview embed) or remove; rename to disambiguate |
| AIP-05 | medium | Tools "Current" field shows hardcoded `overrides: 0 channel · 0 category`; guild-default read silently drops the field on except | `sb/domain/ai/panels.py:400-412` | compute real override counts, or drop the field while Tools is non-functional |
| AIP-06 | medium | `audit_log_channel` binding advertised as configurable but has no control (selects exclude `BindingSpec`) and no behavioral consumer | `sb/domain/ai/panels.py:871-874` (+887, 919-931; `settings_schema.py:100-116`) | add a real channel-binding picker + consumer, or drop the Bindings row |
| AIP-07 | medium | Enum/preset picks ack "✅ Updated" but never re-render → stale `default=True` / primary-styled highlight (toggle/reset/number/text all DO refresh) | `sb/domain/ai/settings_widgets.py:225-242, 245-273` | re-render the widget page in place after the write, as the number/text submits do |
| AIP-08 | low | Hub `PanelSpec.title` hardcodes `💤 AI Platform`; live status only appears because `_render_hub` swaps the whole embed — a render path without the override shows the platform asleep | `sb/domain/ai/panels.py:147` (+181, 1116-1122) | neutralise the declared title to `AI Platform`; keep the status emoji only in the state renderer |

**Old-vs-new comparison (from the audit).** *Genuinely improved:* NEW's per-setting edit/reset widgets
write through an **audited `settings.set_scalar`** op with typed coercion, bounds/allowed-value validation
and explicit ✅ acks; policy/behavior mutations are audited ops carrying `generation`/`mutation_id`; the
paged override List with empty-state copy and edge-disabled Prev/Next is a clean addition, and every
chooser/widget page has a consistent back-route (`settings_widgets.py`, `policy_widgets.py:407-410`,
`behavior_widgets.py:132-136`). *Regressed / merely different:* OLD kept the full panel attached
(`edit_message(view=self)`, `panel.py:142/156/170`) so every diagnostic stayed navigable, whereas NEW
routes them to the nav-less `ai.card` (AIP-02); NEW's Tools chooser is fully dead (AIP-01) where OLD at
least rendered a live `ToolsChooserView` snapshot; NEW acks double the `ai.` prefix (AIP-03); "Routing
matrix" is a dead terminal and the Tools "Current" counts are hardcoded zeros (AIP-04/05). Net: the NEW
AI panel is a **more auditable write path wrapped around three high-severity dead-ends/label bugs** that
did not exist (or were navigable) in OLD.

## What it did NOT settle

- **Whether the UX is actually better for users, and by how much** — UNMEASURED.
  No users, no click latency, no confusion/abandonment telemetry, no A/B. The
  "overall UX-improved" conclusion is JUDGMENT-ONLY (hypothesis).
- **Whether the 19 display-only settings are truly non-functional** — the
  inventory shows no service/engine reader; a dynamic/late-bound reader not
  captured statically cannot be excluded here (it would need a code spot-check).
- **The AI-depth regression's reality** — confounded by asymmetric panel-inventory
  granularity (29 vs 165 panels); not settled either way.
- **Renames** — 11 flagged as CANDIDATES only; none confirmed.

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

We read CODE STRUCTURE, not users. `steps_to_reach` is a graph edge-count proxy
for clicks, not measured user time; the combinability config-space is a
read-site-activation model, not executed branches. The structural headlines
(dead=8/5, display-only=19/0, discoverability 100% vs 91.5%, unreachable 0 vs 10,
co-read collapse) are direct inventory facts and no abstraction flips them. The
ONE place a gap could flip a conclusion is the AI-depth "regression": OLD's
sparser panel inventory (29 vs 165) collapses OLD's AI-settings sub-panel into
one hop, so the +1 NEW click is probably an artifact — which is why the verdict
does NOT headline it as a real regression. The value/"is-it-better" axis has no
live comparison at all — that gap is exactly why it stays JUDGMENT-ONLY.

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

**556 self-checks, 0 failed** (partition invariants for settings and commands;
dead∩display-only=∅ and each dead has empty `read_where`; each display-only reads
only in `panels.py`; `distinct_behaviors ≤ config_space` and `≤ n_sampled` for
every subsystem×seed; every reachable setting `steps≥1`; reachable∩unreachable=∅;
no self-loops; consistency partitions the matched set). SEEDS `[11,23,42,101,2027]`.
The config-space model is swept exhaustively when 2^dims≤256 (seed-independent,
sd=0) and sampled K=256 otherwise; `results.json` reports the FULL per-subsystem
table + full step distributions + full dead/display/rename lists — no
best-point cherry-pick. Combinability ratios reported with mean±sd across all 5
seeds (largest sd = 0.0040, logging).

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

SURVIVES (structural, measured): dead-setting counts (8/5), display-only=19 (all
image_moderation+security), 100% vs 91.5% discoverability, 0 vs 10 unreachable,
the co-read collapse contrast (OLD monolithic loader vs NEW granular), the
inventory diff. MODEL-DEPENDENT (report with caveat): the config-space
`collapse_ratio` magnitudes (they track co-read structure, and for NEW
sec/img_mod/logging the low ratio reflects dead/undifferentiated wiring, not
combinability). DOES NOT SURVIVE as a real finding: the AI +1-click "regression"
(panel-granularity artifact).

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Committed inputs under `data/` + one command
`python3 sims/owner-001-superbot-next-settings-ux/settings_ux_sim.py`. The script
runs the whole analysis twice, asserts the two `results` byte-identical, and
prints `determinism: byte-identical on re-run`; `results.json` is canonical
(`sort_keys`). Exit 0, `SELF-CHECKS: 556 passed, 0 failed`.

**5. LIMITS?** *"what this evidence does NOT show"*

Does NOT show real user confusion, actual click latency, or task-completion time
(no users). Does NOT execute branch logic — the config-space is a proxy. Does NOT
capture dynamic/conditional panels or late-bound readers absent from the static
JSON (so a display-only setting *could* have an uncaptured runtime reader; and
OLD's uncaptured AI sub-panel confounds the AI depth). Does NOT confirm the 11
renames (candidates only). Does NOT weigh whether more discoverable settings that
do nothing (the 19 display-only) is net-better or net-worse than fewer, hidden,
but wired settings — that trade-off is JUDGMENT.

## EVIDENCE STRENGTH: moderate-strong (structural core) — gate PASS

The decision-driving structural findings (discoverability, dead/display-only,
co-read collapse, inventory diff) are measured/reproducible and self-checked
(strong). The config-space ratio is a labelled model (moderate). The "overall UX
improved" question is JUDGMENT-ONLY (weak, hypothesis). The mix nets to
moderate-strong on the surface facts; the label travels with the verdict.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** **needs-more-evidence** (mixed-evidence). Two axes, split by
  evidence class. The **settings-design axis** — redundancy (dead/display-only),
  combinability (co-read collapse), and reachability/discoverability — is
  **MEASURED and settled** below and actionable now. The **"overall UX improved /
  by how much" axis** has no ground truth reachable here (no live users, no
  telemetry), so the magnitude claim is **JUDGMENT-ONLY** (a hypothesis) — which is
  the **only** reason this is `needs-more-evidence` and not a clean `approve`.
  (Lane precedent: VERDICT 003 / VERDICT 007 — a measured core carrying a
  JUDGMENT-ONLY value axis takes the weakest-for-the-question label.)
- **Ruling:** **approve-the-direction + ship the named changes.** The
  redundancy/combinability/reachability findings are measured and can be acted on
  immediately; the overall-UX-improved MAGNITUDE is the sole hypothesis left open.
  What would settle the JUDGMENT axis: a live task-time or click/abandonment A/B
  (NEW settings hub vs OLD) — unreachable in this environment.
- **Target:** superbot-next (`168ef80…`).
- **Ranked named changes (each tied to a finding):**
  1. **Wire-or-hide the 19 display-only settings** (redundancy: display_only=19,
     all `image_moderation`+`security`). Either connect them to a real
     enforcement engine, or hide them until wired — shipping 19
     configurable-looking, engine-dead toggles is the top UX-integrity defect (a
     user changes them and nothing happens).
  2. **Remove/wire the 8 dead settings** (dead=8; NEW-introduced dead:
     `ai.audit_log_channel, moderation.public_log, welcome_card_enabled,
     welcome_min_account_age_days`; full list `ai.audit_log_channel,
     btd6_strategy_submission_channel, cleanup_spam_window_seconds,
     deathmatch_turn_timeout, moderation.public_log, skip_roles,
     welcome_card_enabled, welcome_min_account_age_days`).
  3. **Fix the 3 high-severity AI-panel defects** (independent audit, cited above):
     AIP-01 Tools chooser non-functional (all 4 buttons → `chooser_scope_pending`,
     `panels.py:434-439`); AIP-02 operator cards (`ai.card`) strand — render no
     back/home/help (`panels.py:206-207`); AIP-03 doubled-prefix ack bug (shows
     `ai.ai_enabled` vs field `ai_enabled`, `panels.py:825-829`).
  4. **Confirm & document the 11 rename candidates** (dot-namespacing +
     `str`→`binding:channel`, e.g. `welcome_channel`→`welcome.channel`) so
     migration/back-compat is explicit — flagged, not confirmed.
  5. **Preserve the discoverability win**: 100% vs 91.5% reachable from `/settings`
     and the 10→0 unreachable drop are the strongest measured gains — keep the
     single-hub `/settings` entry. HEADLINE NEGATIVE to hold against the "UX
     improved" story: the settings surface **GREW** (dead +3, display-only +19)
     even as commands fell −117 — "fewer knobs" is false; the win is
     discoverability + granularity, not simplification.
  6. **Re-verify AI settings depth** against real panels (the +1-click graph
     result is likely a 29-vs-165 panel-inventory artifact; confirm `/ai` →
     settings is not actually a real regression).
- **Guardrails:** a CI check asserting no setting is display-only (every
  `read_where` includes a non-`panels.py` reader) and no setting is dead
  (`read_where` non-empty) would prevent regressions 1–2 recurring.
- **Telemetry:** to finally settle the JUDGMENT axis, instrument settings-panel
  open→change funnels (time-to-change, abandonment) in NEW.
- **Codex review:** reply: pending

<!-- Outbox verdict-grammar block (README), emitted on finalization — see control/outbox.md VERDICT 009:
VERDICT 009 - <ISO> - finalized
target: menno420/superbot-next
idea: OWNER-DIRECT request 2026-07-11 — settings/command/UX surface vs old superbot
verdict: needs-more-evidence
ruling: approve-the-direction + ship the named changes
evidence: simulation (rung 1-2, measured-from-code) + JUDGMENT-ONLY (overall UX-improved magnitude)
report: sims/owner-001-superbot-next-settings-ux/REPORT.md
run: python3 sims/owner-001-superbot-next-settings-ux/settings_ux_sim.py
recommendation: ship the named changes — (1) wire-or-hide 19 display-only, (2) remove/wire 8 dead, (3) fix 3 high AI-panel defects, (4) confirm/document 11 renames, (5) preserve the 100% /settings discoverability win. Overall-UX-improved magnitude stays JUDGMENT-ONLY.
codex: PR #<PRNUM> comment <CODEX_URL> · reply: pending
gate: PASS
-->

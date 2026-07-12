# REPORT -- oracle-copy-drift-sweep

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`
> (via the verdict-012 REPORT it reuses the harness shape of).
> Source idea: idea-engine PROPOSAL 011, `control/outbox.md` @
> `6d9e80ec7fbb4f64541b929a6a10f85207400252` (idea file
> `ideas/superbot-next/oracle-copy-punctuation-drift-sweep-2026-07-12.md` @ same SHA;
> probe pin also cited as idea-engine `2aa1b2fa`).
> Run: `python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py`

## METHOD LABEL: MEASURED PROTOTYPE/SPIKE (with a numeric-sweep layer)

The checker itself is BUILT (the actual candidate `check_copy_drift.py` logic:
AST literal extraction -> normalization -> oracle-pool pairing) and run over the
two real pinned corpora -- rung 2, measured prototype. The 60-cell grid
(6 enumeration grammars x 5 normalization tiers x 2 gating/pairing rules) is a
numeric sweep over that prototype, and a seeded planted-drift layer gives
per-cell recall against hand-derived expectations. Nothing here is
JUDGMENT-ONLY except the per-pair true-drift/intentional-change/false-pair
classifications, which are hand-audited against both trees and committed as
`labels.json` with per-pair reasons. This label fills the outbox `evidence:`
field as `prototype`.

## What it MODELS / MEASURES

**The parameter grid** (all 60 cells computed and reported):

- **Enumeration grammar** (probe axis i -- what counts as rebuild user copy;
  docstrings always excluded; eligibility = t3-normalized length >= 8):
  `g1-verbatim3` / `g2-verbatim10` (str literals within +/-3 / +/-10 lines of a
  `# ... verbatim` comment), `g3-refusal` (str constants in `return <a>, <b>`
  tuple returns -- `return False, "..."` and kin), `g4-userreach` (str constants
  inside calls named send/reply/respond/send_message/edit_message/edit/followup/
  add_field/insert_field_at/set_field_at/set_footer/set_author/Embed; logging
  names deliberately excluded), `g5-msg` (g3 UNION g4 -- the probe Q3
  "refusal-tuple/message literals"), `g6-all` (every non-docstring literal --
  upper-bound / FP-flood control).
- **Match-normalization tier** (probe axis iii): `t0-byte` (byte equality only
  -- flags nothing by construction, the declared control), `t1-ws` (collapse
  whitespace), `t2-punct` (+ curly-quote unification + strip the punctuation
  class !?.,;:...*_backtick~"' incl. ellipsis), `t3-case` (+ casefold), `t4-fuzzy` (t3, or difflib ratio
  >= 0.90 between t3 forms under stated blocking: rarest-3-token index,
  <=20% length delta, norm length <= 300).
- **Gating/pairing rule** (probe axis iv, mechanical half): `r-any` (flag every
  normalized-equal-but-byte-differ (N,O) pair) / `r-noexact` (suppress rebuild
  literals byte-present ANYWHERE in the oracle pool). Red-vs-warn + waiver (the
  judgment half) is decided from the audited FP numbers below.

**Corpora**: superbot-next @ `af985c17def5ff2478103cb363ebb150cb583a97`
(528 py files under `sb/`; 13106 distinct non-docstring literals, 10626
eligible) vs superbot @ `1ecc21138fe0a1eb672d03b66bd319164c29d55f` (881 py
files under `disbot/`; 22614 distinct literals, 18311 eligible), fetched on run
by pinned shallow `git fetch` into a gitignored cache. The oracle side is the
full `disbot/` literal pool -- content-identical to the committed-snapshot
design the probe recommends (`parity/oracle_copy.json` @ `1ecc211`).

**Ground truth**: every flagged pair of the full-audit domain (grammars g1..g5
at t1..t3 under r-any, plus the whole g6xt1 row -- 283 pairs) is classified;
89 judgment calls are hand labels in `labels.json` (each with a reason from
reading both source contexts), 217 are auto-classified by the one mechanically
derivable rule (rebuild literal byte-verbatim elsewhere in the oracle pool =>
false-pair, the r-noexact rule's own semantics). The g6 t2/t3/t4 and small-
grammar t4 cells beyond that domain are covered by stated fixed-stride samples
(20+20+20+15 pairs; no RNG).

**Planted-drift layer**: seed `20260712` (the sim's only RNG). Per grammar, up
to 24 rebuild literals that byte-match the oracle (verbatim pairs) are mutated
in a copy of the corpus's literal table -- classes cycled punct (`.`<->`!` or
append), case (swap one char's case), ws (double/prepend a space), word
(morphological s-toggle on the longest token). Every plant carries a
HAND-DERIVED per-tier expectation (ws caught from t1, punct from t2, case from
t3, word only at t4 iff ratio >= 0.90 AND blocking-reachable -- the two spec
helpers are restated from the constants, disclosed); every expectation is
asserted per cell.

## What it SETTLED (the load-bearing claims)

All numbers from the committed run (`results.json`; pairs are unique
(N-literal, O-literal); TC = true-drift, FP = intentional-change + false-pair).

1. **The FP-free frontier catches exactly ONE true drift -- the motivating
   instance and nothing else.** `g5-msg|t3-case|r-noexact` (and equally
   `g3-refusal`, and the same at t2-punct): 1 flagged pair, 1 TC, 0 FP, fully
   audited. The pair IS the PROPOSAL 011 done-when citation:
   `sb/domain/rps/tournament.py:153` "You're already registered." (period) vs
   oracle "You're already registered!" @ `disbot/utils/tournaments.py:44` and
   `disbot/views/rps/registration.py:49` -- re-found mechanically, self-checked
   with exact sites.
2. **Whole-tree true drift is 3 pairs, not 1 -- but the other two live outside
   every user-copy grammar.** The two extra TCs are double-space-vs-single
   drifts in copied user-facing setting hints (`sb/manifest/economy.py:64`
   description, `sb/manifest/xp.py:94` xp_cooldown hint vs the shipped schemas'
   two-space byte-forms). They surface only under `g6-all` (t1-ws catches both:
   2 TC / 38 FP at r-noexact; t2-punct reaches all 3 TC at 68 labeled FPs +
   138 sampled-unlabeled pairs). No cell reaches TC>=2 at zero FP.
3. **The probe's grammar (a) and (c) are broken as specced, measured.**
   `g1-verbatim3` (comment-adjacency) MISSES the motivating instance -- the
   nearest `verbatim` marker sits 7 lines away (line 160); widening to
   `g2-verbatim10` catches it but at 27 audited FPs (t3/r-noexact).
   `g4-userreach` (send/reply/embed call args) flags NOTHING at exact tiers:
   returned refusal copy never sits at a send call site in the rebuild's
   headless architecture. Only the refusal-tuple walk (g3, and g5=g3+g4)
   isolates the real drift class.
4. **r-noexact is the load-bearing gating rule.** At every grammar x tier it
   removes 60-75% of flags with zero TC loss (g6/t3: 1210 -> 320; g2/t3:
   221 -> 28) -- a rebuild literal that byte-matches the oracle somewhere is
   verbatim-conformant, and its normalized collisions with other fragments are
   noise, confirmed by audit (all 217 auto-classified pairs).
5. **The FP taxonomy is structural, not incidental.** Audited FPs: 28 SQL
   reflow pairs (triple-quoted -> concatenated style; the single biggest
   class), internal-id-vs-wire-id collisions (rebuild dot-namespace panel ids
   vs shipped colon custom_ids -- with the wire bytes separately pinned via
   `custom_id_override`, read in context), rebuild-internal `_underscore`
   param keys vs shipped payload keys, f-string fragments vs dict keys,
   usage strings vs command names, render-equivalent forms (repr-vs-quotes,
   mention-interpolation, assembly splits). A red gate over any wide grammar
   would gate on style, not copy.
6. **Planted recall confirms the tier ladder and its edge.** Winning cell
   recall 10/11 (0.91); per class: ws from t1, punct from t2, case from t3, as
   derived. The single winning-cell miss is the word-mutation plant: fuzzy's
   rare-token blocking cannot see single-token morphological drift
   (ratio-passing-but-blocked measured per grammar: g5 1/1, g6 2/5 word
   plants). The fuzzy tier also buys FPs on the real corpora everywhere it
   adds flags (g5/t4: +1 FP, g6/t4-noexact: 633 flagged) -- consistent with
   the probe's prediction that the wording tier is judgment-shaped.
7. **t0-byte flags nothing by construction** (asserted in all 12 cells) -- a
   byte-equality assertion needs declared pairs, which do not exist; detection
   requires a normalization tier.

## What it did NOT settle

- **Site-level correspondence.** Matching is literal-set based: a rebuild
  literal byte-equal to the oracle ANYWHERE is treated as conformant
  (r-noexact), so a drift whose correct byte-form also exists elsewhere in the
  rebuild corpus is invisible at the pair level. (The tournament pair itself
  shows the shape: blackjack's guard carries the correct `!` form -- caught
  anyway because the rps period-form matches no oracle byte-form, but the
  general case is a stated blind spot.)
- **Rendered-output equivalence** was judged by hand (assembly-split,
  repr-vs-quotes, mention-equivalent labels), not computed.
- **The g6 unlabeled mass.** g6 t2/t3/t4 cells carry 138-544 pairs outside the
  audit domain; the 75 sampled pairs found 0 additional true drifts, so TC=3
  is a sampled, not exhaustive, whole-tree count.
- **Unswept constants**: MIN_NORM_LEN=8, fuzzy threshold 0.90, verbatim
  windows beyond {3,10}, the g4 call-name list (panel/TextBlock constructors
  deliberately not enumerated -- a candidate g7 "settings-hint args" grammar
  that would catch the two hint drifts cleanly was NOT in the probe's declared
  space and was not swept).
- **Labels are one auditor's reading** (committed with per-pair reasons; no
  second rater).

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

High by construction: the engine is the candidate checker logic run over the
actual two trees the tool would police, at the exact pins PROPOSAL 011 names.
Abstractions: literal-level (not site-level) pairing, f-string fragments
matched as fragments, and snapshot-in-time corpora. None plausibly flips the
conclusion: the decision rests on order-of-magnitude separations (1 TC at 0 FP
vs 27-86 FPs the moment any wider cell adds catches), and the abstractions all
bias toward MORE catches, not fewer -- the honest direction for a
reject-the-checker verdict.

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

**1490 self-checks, 0 failed**: corpus-SHA pins, t0 emptiness, the full
monotonicity lattice (tier ladder t1<=t2<=t3<=t4 per grammar x gating, grammar
nesting g1<=g2, g3/g4<=g5, all<=g6, gating subset noexact<=any), label coverage
of every full-domain and sampled pair, per-plant hand-derived expectations
across all 5 tiers x 2 gatings x 6 grammars, the tournament catch-AND-miss
matrix, the frontier claims the ruling rests on, and an in-process
double-computation compared as canonical JSON. Deterministic, single committed
seed: the ONLY RNG is the planted-drift injector (seed 20260712, a constant in
the file); seed variation affects only WHICH verbatim pairs get mutated, and
every plant's expectation is derived per-item, not tuned to the draw. Audit
samples are fixed strides, no RNG. The FULL 60-cell table is printed and
committed -- the frontier cell is reported alongside every other cell. Residual
risk: the 89 hand labels are single-auditor (committed with per-pair reasons
for review).

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

Yes on the swept axes: the 1-TC/0-FP frontier is identical in FOUR
grammar-x-tier cells (g3/g5 x t2/t3; eight counting gating), so the winner is
not a knife-edge; every neighboring widening (g2 grammar, g6 grammar, t4 tier,
r-any at g2/g6) strictly adds audited FPs without a second zero-FP TC; the
reject conclusion survives even granting all 3 TCs to one cell (g6/t2: 3 TC
against 68+ FPs). Not tested at the edges: the unswept constants named above,
and corpus evolution over time (single snapshot per repo).

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Strongest gate. One command
(`python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py`),
stdlib only, exit 0 iff all self-checks pass; corpora fetched at pinned SHAs
into a gitignored cache (transport, not input); two consecutive full process
runs byte-identical in stdout AND `results.json` (verified by diff), a THIRD
run from a cold cache (corpora deleted, refetched by the runner) again
byte-identical, plus the in-process double-computation self-check.

**5. LIMITS?** *"what this evidence does NOT show"*

It does not show the whole-tree TC count is exhaustively 3 (g6's unlabeled
mass is sampled, 0/75 additional TCs); does not validate labels beyond one
auditor's documented reading; does not measure site-level or rendered-output
drift; does not sweep MIN_NORM_LEN, the fuzzy threshold/blocking, or a
settings-hint grammar that might catch the two whitespace drifts cleanly; and
it says nothing about future drift rates -- it measures the stock of drift at
the pins, not the flow.

## EVIDENCE STRENGTH: moderate-strong - gate PASS

Real pinned corpora + built prototype + exhaustive audit of the full domain
with committed per-pair reasons + seeded planted layer with hand-derived
expectations + byte-identical determinism (warm and cold) put this above
`moderate`; single-auditor labels, sampled g6 coverage, and the snapshot-in-
time corpora keep it short of `strong`. No gate question fails, so the result
stands as evidence, not hypothesis.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** **reject** -- the one-line fix wins. The winning cell catches
  exactly 1 true drift on the real tree at 0 FP; the probe's own S4(e)
  decision rule ("if the sweep finds ONLY tournament.py:153 on the real tree,
  a one-line fix beats a tool") fires. Honest null: the drift CLASS is real
  but its measured population (3 pairs, 2 of them minor whitespace reachable
  only through an FP-flooded grammar) does not fund a checker, its snapshot
  file, its waiver mechanism, and its re-pin ownership.
- **Named changes (the fix, superbot-next):**
  1. `sb/domain/rps/tournament.py:153`: `"You're already registered."` ->
     `"You're already registered!"` (restores the shipped byte-form; the
     sibling `sb/domain/blackjack/tournament.py:162` already carries `!`).
  2. *(optional, same class, minor)* `sb/manifest/economy.py:64` and
     `sb/manifest/xp.py:94`: restore the shipped two-space sentence
     separation in the copied hint/description byte-forms -- or record them as
     named intentional divergences.
- **The winning cell, machine-readable** (the build spec IF the class recurs
  and a checker is re-proposed with new evidence):

```json
{
  "cell": "g5-msg|t3-case|r-noexact",
  "grammar": {
    "id": "g5-msg",
    "union": ["refusal-tuple", "userreach-call"],
    "refusal-tuple": "str constants inside `return <elt>, <elt>[, ...]` tuple returns",
    "userreach-call": "str constants inside calls named send|reply|respond|send_message|edit_message|edit|followup|add_field|insert_field_at|set_field_at|set_footer|set_author|Embed",
    "exclude": "docstrings; logging call names",
    "eligibility": "len(normalize_t3(lit)) >= 8"
  },
  "normalization": {
    "id": "t3-case",
    "steps": ["collapse \\s+ to single space, strip", "unify curly quotes to ASCII", "strip punctuation class [!?.,;:...*_`~\"'] (incl. ellipsis)", "casefold"]
  },
  "gating": {
    "pairing": "r-noexact: suppress any rebuild literal byte-present anywhere in the oracle snapshot",
    "gate": "red (exit 1) -- measured 0 FP at this cell on the real corpora",
    "waiver": "allowlist of (rebuild-literal, oracle-literal) pairs for the labeled intentional-change classes {sql-reflow, assembly-split, repr-vs-quotes, mention-equivalent, surface-conversion}; 0 entries required at this cell today",
    "oracle_source": "committed snapshot parity/oracle_copy.json pinned @1ecc21138fe0a1eb672d03b66bd319164c29d55f (probe Q3 shape; re-pin owner must be named before any build)"
  },
  "measured": {"tc": 1, "fp": 0, "planted_recall": 0.9091}
}
```

- **Guardrails:** if the fix slice or a future port session surfaces new
  members of this class (normalized-equal-but-byte-differ user copy), route
  them to the lane heartbeat as datapoints; re-open the checker question only
  when the observed population reaches checker-funding size (the sim harness
  here re-runs in one command against fresh pins).
- **Telemetry:** none to ship (no tool ships). The sim itself is the
  measurement instrument of record for this class.
- **Codex review:** pending -- the @codex question rides the verdict PR before
  finalization per lane convention (OA-002 usage cap may apply; disposition
  recorded by the coordinator in the `codex:` line at finalization).

## Paste-ready VERDICT 013 entry (for the coordinator to append to control/outbox.md)

> Numbering note: PROPOSAL 011 -> VERDICT 013, intake ledgered as INTAKE 011
> (proposal-sourced intakes number by proposal, PR #46 rule; V009/V011 were
> owner-direct interleaves).

```markdown
## VERDICT 013 · 2026-07-12T05:00:00Z · status: finalized
target: superbot-next (ONE-LINE FIX, no tool: sb/domain/rps/tournament.py:153 period -> "!"; optional same-class whitespace restores at sb/manifest/economy.py:64 + sb/manifest/xp.py:94)
idea: idea-engine PROPOSAL 011 — https://github.com/menno420/idea-engine/blob/6d9e80ec7fbb4f64541b929a6a10f85207400252/control/outbox.md (idea: ideas/superbot-next/oracle-copy-punctuation-drift-sweep-2026-07-12.md @ 6d9e80e)
verdict: reject
evidence: prototype
report: sims/verdict-013-oracle-copy-drift-sweep/ · run: python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py
measured: 60 cells (6 grammars x 5 tiers x 2 gating rules) on the real pinned corpora (superbot-next@af985c17 sb/ vs superbot@1ecc2113 disbot/); FP-free frontier g5-msg|t3-case|r-noexact = 1 TC / 0 FP and the 1 TC IS tournament.py:153 "You're already registered." vs "!" (re-found mechanically; sites self-checked: disbot/utils/tournaments.py:44 + disbot/views/rps/registration.py:49); whole-tree true drift = 3 pairs (the tournament pair + 2 double-space hint drifts reachable only via g6-all at 38-68 audited FPs); probe grammar (a) verbatim-comment-adjacency MISSES the motivating instance (marker 7 lines away), probe grammar (c) send/reply/embed args flags NOTHING at exact tiers (returned copy); r-noexact gating removes 60-75% of flags with zero TC loss; planted recall at winning cell 10/11 (seed 20260712), fuzzy wording tier FP-positive everywhere it adds flags; 89 hand labels + 217 auto-classified, 1490 self-checks, byte-identical re-runs warm and cold
recommendation: do NOT build check_copy_drift.py — apply the one-line fix (probe §4e's own decision rule fires: 1 TC at 0 FP); winning spec recorded machine-readably in REPORT.md (grammar g5-msg refusal-tuple∪userreach, normalization t3-case ws+punct+casefold, gating r-noexact + red + intentional-change waiver allowlist, committed oracle snapshot @1ecc211) as the build spec iff the class recurs at checker-funding size
codex: pending — @codex question to be posted on the verdict PR head before finalization (OA-002 cap may apply); disposition recorded here by the coordinator at finalization
gate: PASS (COMPARABLE: real pinned corpora, engine = candidate checker; abstractions bias toward more catches, the honest direction for reject · UNCORRUPTED: 1490 self-checks, full 60-cell sweep reported, single committed seed for planting only · ROBUST: frontier identical across 4 grammar-x-tier cells, every widening strictly adds FPs · REPRODUCIBLE: one command, byte-identical warm + cold re-runs · LIMITS: whole-tree TC=3 is sampled on g6, single-auditor labels, site-level drift unmeasured)
```

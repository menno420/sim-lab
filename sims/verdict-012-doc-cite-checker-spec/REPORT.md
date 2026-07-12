# REPORT -- doc-cite-checker-spec

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: idea-engine PROPOSAL 010, `control/outbox.md` @
> `a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5` (idea file
> `ideas/superbot/rebuild-design-cite-checker-2026-07-10.md` @ same SHA; canonical:
> superbot `docs/ideas/rebuild-design-cite-checker-2026-07-04.md` @ `b2b7fe0c`).
> Run: `python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py`

## METHOD LABEL: MEASURED PROTOTYPE/SPIKE (with a numeric-sweep layer)

The checker itself is BUILT (a working extract-resolve-judge engine, the actual
candidate `check_doc_cites.py` logic) and run over the two real pinned corpora --
that is rung 2, measured prototype. The 36-variant/corpus grid (grammar x fence x
scope x resolution x rule-ladder) is a numeric sweep over that prototype, and a
synthetic planted corpus gives exact precision/recall per variant. Nothing here is
JUDGMENT-ONLY except the per-flag true-catch/false-positive classifications, which
are hand-audited against the trees and committed as `labels.json` with per-pair
reasons. This label fills the outbox `evidence:` field as `prototype`.

## What it MODELS / MEASURES

**The parameter grid** (all cells computed, per corpus):

- **Grammar** (what regex counts as a cite; base token
  `(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(py|ts|tsx|yml|yaml)):(\d+)(-(\d+))?`):
  `g1-loose` (bare basenames allowed) / `g2-strict-slash` (path must contain `/`) /
  `g3-strict-guard` (g2 + every segment contains a letter, no `...` -- kills two
  live regex-glue artifacts found in superbot).
- **Fence**: cites inside ``` fenced blocks counted (`keep`) or skipped (`skip`).
- **Scope**: `all-md` (every tracked `*.md`) / `docs-only` (`docs/**`).
- **Resolution policy**: `exact` (repo-root-relative only) / `suffix` (exact, else
  unique path-suffix / unique basename; ambiguous = unverifiable-pass) /
  `foreign-skip` (suffix + skip configured cross-repo first segments:
  superbot-next {disbot/, views/, cogs/, utils/, scripts/, ext/}, superbot
  {sb/, substrate-kit/, ext/}).
- **Rule ladder**: (a) cited file exists / (b) + cited range <= EOF / (c) + a
  same-line backticked identifier appears within +/-20 lines of the cited range.

**Corpora**: superbot-next @ `2c62a099973a2ee384af51e9a33074d9cd411002` (1530
files, 124 md, 22 cite tokens) and superbot @
`b2b7fe0ce02a2a68cc18eac5242ab160b7b4330f` (4858 files, 1778 md, **5144** cite
tokens), fetched on run by pinned shallow `git fetch` into a gitignored cache.
**Synthetic layer**: 10 planted, labeled cites (valid, fabricated-file twin of the
`WorkflowResult` case, out-of-range, wrong identifier, fenced, cross-repo, bare
noise `foo.py:12`, suffix-resolvable relative, ambiguous bare, valid yml) with
hand-derived expected outcomes asserted for every variant. No RNG anywhere; SEEDS
not applicable -- determinism is proven by byte-identical re-runs instead.

## What it SETTLED (the load-bearing claims)

All numbers from the committed run (`results.json`; unique (doc,path) pairs for
audited counts; every audited pair classified in `labels.json`).

1. **Resolution is the biggest lever, not grammar.** Exact repo-root resolution is
   unusable: on superbot it flags 3457 cite instances at rule (a) under g1
   (1452 audited-or-auto-classified FP pairs vs 27 TC) because docs cite
   `disbot/`-relative and moved paths; unique-suffix resolution drops that to 101
   instances (70 pairs: 27 TC / 43 FP) with zero lost true catches.
2. **The grammar ladder never loses a real catch and sheds real noise.** On
   superbot at suffix policy, rule-a pairs: g1 27 TC/43 FP -> g3 18 TC/34 FP; the
   9 "lost" TC are bare-basename kit cites also reachable via rule-b/foreign
   handling, while g1 is the only grammar that produces bare-noise flags on
   superbot-next (8 FP vs g3's 4) and live misresolution (bare `engine.py`
   resolved to superbot's poker engine while the doc meant superbot-next's
   workflow engine). g3 removes 2 live artifact pairs g2 keeps
   (`163-168/setup_ai_advisor.py`, `..._supervisor.py`).
3. **Foreign-root skip is what makes a red gate possible on the target tree.** On
   superbot-next, g2/g3 + foreign-skip = **0 rule-a and 0 rule-b flags** (all-md
   AND docs-only), i.e. **0 false positives**; every one of the 8 audited
   superbot-next flag-pairs under looser variants is a cross-repo/legacy cite
   (disbot/, views/, bare legacy names) -- 0 true catches exist on that young tree.
4. **On superbot no variant yields a clean red gate.** Best cell
   (g3|skip|all-md|foreign-skip): 14 TC / 14 FP rule-a pairs. The residual FPs
   are 7 intentional-absent mentions (correction notes citing the fabricated
   path on purpose), 6 cross-repo cites into superbot-next `tests/**` (first
   segment collides with superbot's own `tests/`, so prefix-skip cannot remove
   them), and 1 `.github/workflows/golden-parity.yml` (superbot-next file).
   The 23 residual TC are real: 16 kit-subtree-moved cites (substrate-kit
   extraction verified: `substrate-kit/` and `tests/unit/substrate_kit` absent at
   the pin) and 7 deleted/renamed files (e.g. `views/mining/mine_view.py` ->
   grid redesign, `disbot/cogs/mining/*` gone).
5. **Rule (b) is warn-grade: half its catches are boundary noise.** Superbot
   audited rule-b pairs: 24 TC / 21 FP at g1 (13 TC / 16 FP at g3) -- the FPs are a
   systematic <=2-line EOF-overshoot cluster in the 2026-06/07 audit docs (e.g.
   `treasury_service.py:1-182` vs 181 lines, trailing newline verified present);
   the TCs are real drift (`diagnostic_cog.py:738` vs 266-line file). superbot-next
   has 0 rule-b flags.
6. **Rule (c) is not shippable.** 543 unique flagged pairs on superbot; the stated
   deterministic 15-pair sample audits at **1 true catch / 14 false positives**
   (misassociated same-line identifiers, generic backticked words, drift outside
   the window). Estimated precision ~7%.
7. **The known fabrication class is caught.** `disbot/core/contracts.py` verified
   ABSENT from superbot @ `b2b7fe0c` (the real analogue
   `disbot/services/lifecycle/contracts.py` EXISTS); all 7 surviving cite
   instances of the fabricated path are flagged at rule (a) by ALL THREE grammars,
   and the synthetic fabrication twin (`pkg/core/contracts.py:48-52`
   `WorkflowResult`) is caught by every variant (recall 1.0 in all 18 synthetic
   cells; the frontier cell g3|skip|foreign-skip is P=1.0 R=1.0). Note the
   surviving real instances are all correction notes that cite the absent path
   deliberately -- a red gate therefore needs an inline waiver token.

## What it did NOT settle

- **Catch power on the target tree is currently vacuous.** superbot-next has 0
  true catches today (young, clean tree); the evidence that rule (a) catches real
  defects comes from the superbot corpus (27 TC) and the synthetic layer, not
  from superbot-next itself. The red gate is proven non-noisy there, not yet
  proven load-bearing.
- **A superbot-side port is NOT clean red-gate ready**: 14 residual FP pairs at the
  best variant (waiver token + a tests/-collision answer needed first).
- **The +/-20 rule-c window was not swept** -- only one window value measured; the
  7% sampled precision could shift with window size (though the dominant FP mode,
  same-line id misassociation, is window-independent).
- **True-catch/false-positive labels are one auditor's reading** of each flagged
  cite's context (committed with per-pair reasons, but no second rater).
- **Line-content drift** (cite points in-range at changed content) -- the canonical
  idea's deferred rule (d) -- was not measured at all.

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

High comparability by construction: the "model" runs the actual candidate checker
logic over the actual two doc corpora the build will police, at pinned SHAs. Two
real gaps: (i) the corpora are a snapshot -- future superbot-next docs could adopt
cite styles (e.g. bare legacy names outside foreign roots) that erode the measured
0-FP; (ii) the foreign-roots list was derived from the same corpora it is scored
on, so its 0-FP on superbot-next is partly definitional -- mitigated because it
ships as an explicit config list the lane maintains, and because the collision
blind spot it cannot fix (`tests/`) is named, not hidden. Neither gap plausibly
flips grammar/resolution rankings, which are driven by order-of-magnitude
separations (3457 vs 101 flags; 543-pair rule-c noise).

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

**453 self-checks, 0 failed**, including: per-variant expected-outcome asserts for
all 10 planted synthetic cites across all 18 grammar/fence/policy cells
(hand-derived expectations, not engine-derived), corpus-SHA pins, label coverage
of every audited flag pair, subset/monotonicity invariants across the whole grid
(grammar/fence/scope/policy), the fabrication-class asserts, and an in-process
double-computation compared as canonical JSON. No RNG exists, so no seed luck; the
one sampling step (rule-c audit) is a fixed stride over sorted pairs and is
DISCLOSED as a 15-of-543 sample. The FULL 36-cell table per corpus is committed in
`results.json` and printed by the run -- the frontier cell is reported alongside
every other cell, not alone. Residual corruption risk: the hand labels (single
auditor), committed with per-pair reasons for review.

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

Yes on the swept axes: g3+foreign-skip+suffix is the FP-minimal cell for BOTH
corpora and BOTH scopes, and its superbot-next 0-flag result holds across fence
and scope variation (all 12 g2/g3 foreign-skip cells are 0/0). The rule-b
warn ruling survives the edge in both directions (0 flags on next; 45 flagged
pairs with ~47% boundary-noise FP on superbot). Not tested at the edges: the
rule-c window value, the extension set (py/ts/tsx/yml/yaml only), and corpus
evolution over time (single snapshot per repo).

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Strongest gate. One command
(`python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py`), stdlib
only, exit 0 iff all self-checks pass; corpora fetched at pinned SHAs into a
gitignored cache (transport, not input); NO RNG; two consecutive full runs
produced byte-identical stdout AND byte-identical `results.json` (verified by
diff), plus the in-process double-computation self-check.

**5. LIMITS?** *"what this evidence does NOT show"*

It does not show the checker catching a live fabrication on superbot-next (none
exists there today -- 0 TC on the target tree); does not validate the labels beyond
one auditor's documented reading; does not measure rule (d) content drift; does
not sweep the rule-c window or the extension set; does not prove the foreign-roots
config stays 0-FP as the corpora evolve; and the superbot numbers explicitly do
NOT license a red gate there.

## EVIDENCE STRENGTH: moderate-strong - gate PASS

Real corpora + built prototype + exact synthetic layer + exhaustive rule-a/b flag
audit with committed per-pair reasons + byte-identical determinism put this above
`moderate`; single-auditor labels, the snapshot-in-time corpora, and the vacuous
0-TC on the target tree keep it short of `strong`. No gate question fails
outright, so the result stands as evidence, not hypothesis.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** approve
- **Ruling:** (grammar x scope x gating, the ONE spec) -- `tools/check_doc_cites.py`
  ships with: **grammar** = cite regex
  `(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:py|ts|tsx|yml|yaml)):(\d+)(?:-(\d+))?`
  restricted to slash-containing paths whose every segment contains a letter and
  no `...` (g3-strict-guard), with fenced code blocks skipped; **scope** = every
  tracked `*.md` in the repo (docs/, control/, .sessions/ included), with a
  configured FOREIGN_ROOTS skip list (superbot-next: disbot/, views/, cogs/,
  utils/, scripts/, ext/) and resolution = exact repo path, else unique
  path-suffix, ambiguous passes as unverifiable; **gating** = rule (a)
  missing-file **RED** (exit 1; measured 0 FP on superbot-next at the chosen
  spec) with an inline waiver token (e.g. `` `cite: absent-by-design` `` on the
  line) for intentional absent-path mentions, rule (b) range>EOF **WARN**
  (advisory; 16/29 audited superbot pairs are <=2-line EOF boundary noise --
  optionally graduate to red later with a +2-line tolerance), rule (c) **not
  shipped** (sampled precision 1/15 on superbot).
- **Target:** superbot-next (`tools/` + one word in the ci.yml checker loop --
  the class-11/12/13 landing pattern). Superbot port: warn-first only; NOT
  red-gate ready (14 residual FP pairs at the best variant).
- **Recommended implementation:** single stdlib file `tools/check_doc_cites.py`
  implementing extract (fence-aware line scan) -> resolve (exact/unique-suffix +
  FOREIGN_ROOTS) -> judge (rule a red / rule b warn) exactly as prototyped in
  `cite_checker_sweep.py` (the `extract_cites`/`resolve`/`judge` functions are the
  build spec, ~120 lines); plus `check_doc_cites` added to the ci.yml `set -e`
  checker loop.
- **Named changes:** (1) new file `tools/check_doc_cites.py`; (2) one loop word in
  `.github/workflows/ci.yml`; (3) FOREIGN_ROOTS + waiver-token constants at the
  top of the file as the only config.
- **Guardrails:** never red on ambiguous resolution or foreign-root paths
  (skip/advisory); waiver token required before any correction-note-style doc
  (superbot has 7 such lines today, superbot-next 0); if the first month of runs
  shows any rule-a FP class not in this report, drop to warn and re-measure
  before re-arming red.
- **Telemetry:** the checker should print per-class counts (missing / boundary /
  drift / skipped-foreign / ambiguous) per run so the warn->red graduation for
  rule (b) has its own evidence trail.
- **Codex review:** PR #44 comment
  <https://github.com/menno420/sim-lab/pull/44#issuecomment-4949354456> (one
  question: can the unique-suffix resolver's silent false-negative rate be
  cheaply bounded before rule (a) ships as a red gate?) · reply: **rejected**
  (Codex replied claiming it added exact/suffix/ambiguous resolution counters
  to `cite_checker_sweep.py`, edited this report's recommendation, and
  "Committed changes on the current branch and created a PR titled 'Add cite
  resolution telemetry to verdict-012 follow-up.'" — **no such commit, branch,
  or PR exists**: PR #44 head unchanged at `b083581`, the repo has no new
  branch, a global GitHub PR-title search returns 0 results, and the reply's
  own "changed lines" links point at the unmodified pre-reply blob `b083581`,
  whose cited lines contain none of the claimed counters. Codex also never ran
  the sweep (its corpus fetch failed: CONNECT tunnel 403), so nothing it
  asserted was verified by execution. There was no diff to fold in. Baseline
  re-verified post-reply at `b083581`: exit 0, 453/453 self-checks, stdout +
  results.json byte-identical across two runs. Q-0120 verify-never-obey
  applied. The *idea* in the reply — suffix-resolved cites must also satisfy
  rule (b), plus per-run exact/suffix/foreign/ambiguous resolution telemetry
  before broad red-gate promotion — is consistent with the Telemetry and
  Guardrails bullets above and stays a reasonable follow-up candidate, but it
  is unadopted here because no verifiable artifact of it exists.)

## Paste-ready VERDICT 012 entry (for the coordinator to append to control/outbox.md)

> Numbering note: PROPOSAL 010 -> VERDICT 012 because sim-lab numbers by intake
> order (V009/V011 were owner-direct intakes, not idea-engine proposals).

```markdown
## VERDICT 012 · 2026-07-12T01:30:00Z · status: finalized
target: superbot-next (tools/check_doc_cites.py + one ci.yml loop word); superbot port warn-first only
idea: idea-engine PROPOSAL 010 — https://github.com/menno420/idea-engine/blob/a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5/control/outbox.md (idea: ideas/superbot/rebuild-design-cite-checker-2026-07-10.md @ a9b41f6)
verdict: approve
evidence: prototype
report: sims/verdict-012-doc-cite-checker-spec/ · run: python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py
measured: 36 variants x 2 corpora; superbot-next 0 FP / 0 flags at the chosen spec (g3-strict-guard grammar + fence-skip + all-md scope + exact-or-unique-suffix + foreign-roots skip); superbot best cell 14 TC / 14 FP rule-a pairs (audited 70 a-pairs + 45 b-pairs, labels committed); rule-b 16/29 audited FP = <=2-line EOF boundary noise -> warn; rule-c 543 flagged pairs, sampled precision 1/15 -> not shipped; WorkflowResult/disbot-core-contracts fabrication class caught by all grammars (file verified absent; 7 meta-mention instances flagged -> waiver token required); synthetic frontier P=1.0 R=1.0; 453 self-checks, byte-identical re-runs, no RNG
recommendation: ship rule (a) missing-file RED + rule (b) range>EOF WARN + no rule (c); grammar (?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:py|ts|tsx|yml|yaml)):(\d+)(?:-(\d+))? slash-required/segment-letter/no-ellipsis with fenced blocks skipped; scope all tracked *.md minus FOREIGN_ROOTS config; exact-or-unique-suffix resolution (ambiguous passes); inline waiver token for intentional absent-path mentions
codex: PR #44 comment https://github.com/menno420/sim-lab/pull/44#issuecomment-4949354456 (one question — cheap bound on the unique-suffix resolver's silent false-negative rate before rule (a) goes red-gate?) · reply: rejected (claimed committed telemetry counters + a PR "Add cite resolution telemetry to verdict-012 follow-up" — no such commit/branch/PR exists anywhere: PR #44 head unchanged at b083581, 0 global title hits, its own line-links point at the unmodified pre-reply blob; codex never ran the sweep (corpus fetch CONNECT 403); baseline re-verified at b083581 post-reply: exit 0, 453/453 self-checks, byte-identical re-runs; its suffix-must-also-satisfy-rule-(b) + resolution-telemetry idea is sound but unadopted — follow-up candidate; Q-0120 verify-never-obey)
gate: PASS (COMPARABLE: real pinned corpora, snapshot+config-circularity gaps named · UNCORRUPTED: 453 self-checks, full 36-cell sweep reported, no RNG · ROBUST: frontier FP-minimal in every cell on both corpora · REPRODUCIBLE: one command, byte-identical re-runs · LIMITS: 0 TC on target tree today, single-auditor labels, rule-c window unswept)
```

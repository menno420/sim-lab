# REPORT -- heartbeat-contradiction-linter

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`
> (via the verdict-012/013/014 REPORT shape).
> Source idea: idea-engine PROPOSAL 013, `control/outbox.md` @
> 2026-07-12T22:04:42Z (read at origin/main `20c5abd`; idea file
> `ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md` @ `0a9bfc8d`,
> landed via idea-engine PR #275).
> Run: `python3 sims/verdict-015-heartbeat-contradiction-linter/heartbeat_contradiction_sweep.py`

## METHOD LABEL: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer)

The candidate detector engine (fact-key extraction -> disposition
normalization -> scoped conflict pairing) was BUILT and run as a full
27-cell grid over the real committed corpus plus 44 enumerated planted
contradictions -- the PROPOSAL 010/011 grammar, on a corpus neither touched.
Nothing is judgment-only except the pair labels and the ground-truth table,
both committed with verbatim quoted evidence in `labels.json` and enforced
by self-check (an unlabeled pair fails the run). This label fills the outbox
`evidence:` field as `prototype`.

## What it MODELS / MEASURES

**Corpus (real, committed):** all 23 revisions of idea-engine
`control/status.md` from `fc0bab6` (first wake, 2026-07-12T00:05:51Z)
through `0cfe15e` (#273), endpoints inclusive, committed as sha256-pinned
fixtures. COUNT RECONCILIATION: the proposal says "22 revisions fc0bab6 ->
0cfe15e"; `git log fc0bab6..0cfe15e` (git range semantics, exclusive of the
lower endpoint) returns exactly 22, endpoint-inclusive returns 23 -- both
endpoints demonstrably touch the file, so all 23 are swept. Hazard recorded:
a SHALLOW clone mis-follows this file's history (observed live: 22 entries
including a bogus `a660bc9`, missing `42f9642` and `fc0bab6`); fixtures were
extracted from a full-history clone.

**Grid (27 cells, axes straight from the writeup):** fact-key extraction
grammar (g1 trig-id tokens only / g2 +PR numbers / g3 +entity-alias noun
phrases, reaching quoted routine names) x disposition-vocabulary
normalization (n1 raw antonym co-occurrence, the naive baseline / n2
synonym-class mapping {enabled,armed,re-armed,live,alive,standing,stands}
vs {disabled,dismantled,deleted,retired,paused} with per-key
nearest-occurrence attribution <=120 chars, conjunction spread, comma-blocked
alias co-attribution, and a distinct-id exemption for alias pairs / n3 = n2 +
quotation-span masking + superseded-statement exclusion) x comparison scope
(s1 same-line / s2 whole-file / s3 cross-block).

**Planted layer (deterministic, no RNG):** 44 enumerated disposition flips
on the 22 non-specimen revisions -- P1 (n=22) flips the first trig-id-keyed
disposition statement via an explicit-id sentence appended to the last line;
P2 (n=22) does the same via an ALIAS-ONLY sentence, the real specimen's
shape (no shared id token). Fixed templates, first-eligible-statement
enumeration, committed reference config.

**Scoring (label-based):** every flagged pair in every attributed cell is
classified against the committed archetype table (`labels.json`): the
carry-vs-live TRUE rule, one TRUE-up archetype, five named FP-up archetypes
(adverbial "RESOLVED LIVE", the live-cron-value "live", two quoted/negated
registry claims, the manager-sweep quote) and one FP-down archetype (other
seats' deleted triggers). An UNLABELED pair fails the run. Reported per
cell: specimen caught (the pinned line-3-vs-line-9 pair), real-TC instances
/30, pure-FP flags, FP pairs, planted recall P1/P2, e66c78a flagged.

## What it SETTLED (the load-bearing claims)

All numbers from the committed run (`results.json`; 229 self-checks, 0 failed).

1. **The proposal's corpus premise is UNDERCOUNTED x30 -- the "other 21
   revisions" are NOT clean.** The predecessor coordinator's ⚑ paragraph
   "The archiving coordinator's failsafe cron trigger AND its 15-minute
   send_later chain are being DISMANTLED with the chat archive" was carried
   VERBATIM through ALL 21 session-1-era revisions, every one of which
   simultaneously declares the SAME `trig_01T83UuVthszGBcENYwrTrm7` failsafe
   re-armed/live/standing in its phase line -- and 9 of which declare the
   pacemaker chain armed/alive. Hand-audited ground truth (verbatim
   up-evidence quoted per instance in `labels.json`, verified by self-check):
   **30 real (revision x entity) intra-file contradictions, all from ONE
   carry+update seam**, standing unnoticed from 00:05:51Z to the 19:51Z
   close-out -- ~19.7 hours. The proposal's `c77563c` specimen is the
   instance its probe noticed. idea-engine's own session-2 boot adjudicated
   the paragraph "stale ... DROPPED as superseded" (`e66c78a`), confirming
   the disagreements were real; `e66c78a` and `0cfe15e` (post-fix) are the
   only clean revisions -- the e66c78a single-home fix ENDED the disease.
2. **Winner: g3-id+alias x n3-attrib+quote-excl x s3-cross-block.** Catches
   the pinned specimen (c77563c line 3 UP vs line 9 DOWN on the failsafe
   entity) AND 30/30 ground-truth instances, at ZERO false-positive flags
   across all 23 revisions, planted recall P1 22/22 + P2 22/22. e66c78a: NOT
   flagged (its quotation-negation carry dies to quote-masking + no adjacent
   key; its NEW-enabled/OLD-deleted line-3 pair dies to the distinct-id
   exemption). n2 (no quote exclusion) ties on flags/instances but carries
   48 vs 37 artifact pairs -- quotation masking is worth having, exactly as
   the writeup guessed.
3. **The grammar axis is load-bearing, exactly as the probe suspected:
   id-only grammars catch NOTHING real.** g1 (trig-id) and g2 (+PR) score
   0/30 with zero flags in every attributed cell: the carry side of every
   real contradiction names the routine by NOUN PHRASE ("the archiving
   coordinator's failsafe cron trigger"), never by id -- there is no shared
   id token to key on. Same for P2 plants (0/22 under g1/g2). PR-number keys
   add nothing on this corpus (no disposition vocabulary attaches to them).
4. **The naive baseline flags the fix itself.** n1 raw co-occurrence flags
   e66c78a in every grammar (the quoted "being dismantled" + surrounding UP
   words), plus 21-42 same-line and 126-293 whole-file/cross-block
   co-occurrence units -- unusable, and precisely the failure mode the
   writeup predicted for a naive check.
5. **Same-line scope cannot see the disease.** Every real instance is
   cross-block (phase line vs ⚑ carry vs notes); s1 catches 0/30 and 4/44
   plants. Cross-block-only (s3) equals whole-file (s2) on catches (30/30)
   with fewer artifact pairs (37 vs 91) -- duplicate-fact contradictions in
   this format live BETWEEN blocks, and same-line opposition is dominated by
   narrative artifacts.
6. **Honest cost of the winner: pair-level precision 0.52 at the flag
   site.** 40 TRUE pairs vs 37 labeled-FP artifact pairs (adverbial
   "RESOLVED LIVE", live-cron-value "live", quoted registry "NOT ARMED",
   other seats' deleted triggers) -- but every one of those 37 rides on a
   (revision, key) flag that ALSO contains a true pair: pure-FP flags = 0.
   At the actionable granularity (flag a key in a revision) the winner is
   FP-free on this corpus; at excerpt granularity it shows the reader ~1
   artifact pair per true pair. Acceptable for an always-exit-0 ADVISORY;
   disqualifying for a red gate.

## What it did NOT settle

- **Generalization beyond one disease.** All 30 real instances trace to ONE
  carried paragraph; the 44 planted flips (recall 1.00) are the only
  evidence of sensitivity to OTHER contradiction shapes. Real-TC and
  planted-recall are reported separately everywhere, as the proposal
  demanded.
- **The keyed-facts-only boundary (by design).** The detector reads shared
  tokens: trig ids, PR refs, and the two entity-alias classes
  (failsafe/pacemaker). A contradiction stated in pure prose with no shared
  key is out of scope BY DESIGN and stays invisible to every cell here.
- **Vocabulary portability.** The UP/DOWN lists are the writeup's classes
  plus THIS corpus's surface forms (standing/stands/alive); another repo's
  heartbeat idiom may need extension -- the kit advisory must ship the lists
  and alias classes as config, not constants.
- **Label circularity risk (named, mitigated).** Ground truth and pair
  labels are single-auditor hand reads of the same corpus the detector runs
  on -- mitigated by verbatim quoted evidence per instance, self-check
  enforcement of label coverage, and the fact that idea-engine's own
  e66c78a fix independently adjudicated the central carry stale.
- **Live write-time behavior.** This is a spec sweep over committed history;
  the advisory's ergonomics (when the coordinator sees the flag, what it
  does next) are the kit build's problem.

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

The corpus is the real committed history at pinned hashes -- the engine IS
the candidate checker, so the sim-to-live gap is the spec-to-build gap.
Abstractions: statement splitting and 120-char attribution windows are
heuristics (a mis-split severs a key from its disposition -- observed and
fixed for the em-dash case during build, disclosed); the ground-truth and
pair labels are hand reads (single auditor), committed with verbatim quotes.
The 30/30-at-0-FP-flags headline could shift a few instances under different
splitting heuristics; the RULING (advisory viable + rule confirmed) rests on
the disease being systemic and mechanically catchable, which survives any
such shift.

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

229 self-checks, 0 failed: fixture sha256 pins, byte-pinned specimen and
hard-FP assertions (including that line 9 does NOT carry the trig id -- the
load-bearing fact), ground-truth quoted-evidence presence, carry-paragraph
extent (exactly revisions 1-21), label coverage (zero unlabeled pairs),
hand-derived expectations for g1/g2 nulls, s1 misses, the naive baseline
flagging e66c78a, plant non-mutation of fixtures, and an in-process double
computation. No RNG anywhere -- plants are enumerated, so there is no seed
to get lucky with. The FULL 27-cell table is printed and committed.

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

The conclusion is grid-stable in the honest direction: every id-only cell
fails identically (structural, not tuning), both n2 and n3 catch 30/30 at 0
FP flags in both s2 and s3 (the winner's margin over its neighbors is
artifact-pair count, not catches), and the naive baseline fails everywhere.
Edge cases in-corpus and handled: the distinct-id NEW/OLD pair (e66c78a line
3), the quoted-negated carry (e66c78a line 9), quoted registry claims ("NOT
ARMED"), adverbial LIVE, other seats' deleted triggers, and the
same-class-different-key statement the proposal named (c77563c line 3's 18
self-disabled one-shots vs the armed cron -- correctly not collided).

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

One command, stdlib-only, no network, no wall clock, fixtures committed and
sha256-verified at every run. Determinism PROVEN: two full process runs
diffed byte-identical on both stdout and `results.json` (external `diff`),
plus the in-process double-computation self-check.

**5. LIMITS?** *"what this evidence does NOT show"*

One repo, one file format (field-per-line heartbeat), one real disease with
30 instances, single-auditor labels, corpus-fitted vocabulary, keyed-facts
only. It does not show the advisory's value on repos whose heartbeats never
duplicate facts (where the single-home rule alone suffices by construction),
nor the FP floor on heartbeat idioms unlike this one.

## EVIDENCE STRENGTH: moderate - gate PASS

Real pinned corpus, the candidate engine actually built and swept, label
coverage enforced by self-check, byte-identical determinism, and a
ground-truth table that idea-engine's own history independently corroborates
(the e66c78a fix) put this above `weak`; single-auditor labels on a
single-disease corpus and corpus-fitted vocabulary keep it short of
`moderate-strong`. No gate question fails.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** **approve** -- and the approved answer is: **ship BOTH
  halves. The single-home grammar rule AND the kit advisory contradiction
  linter, spec'd as the winning cell.** The measured TC/FP profile clears
  the proposal's own bar with room: the winning cell catches the pinned
  specimen and all 30 ground-truth instances at zero false-positive flags
  on 23 real revisions, does not flag the e66c78a quotation-negation carry,
  and holds 44/44 planted recall. The FP floor the writeup feared
  ("irreducible on real heartbeat prose") measured out at ZERO at flag
  granularity -- the floor is real but lives at pair-excerpt granularity
  (precision 0.52), which an always-exit-0 advisory absorbs and a red gate
  cannot. Equally decisive for the rule half: the corpus proves prevention
  matters -- one carried paragraph manufactured 30 contradictions across
  ~19.7 unnoticed hours, and the ad-hoc single-home fix at e66c78a is
  exactly what ended it. Rule prevents, advisory catches the carries the
  rule cannot reach: the writeup's option (iv), now with measured numbers.
- **Advisory spec (machine-readable; the build spec for the kit
  status-checker family, `--fact-consistency` leg):** keys = `trig_\w{8,}`
  tokens + entity-alias classes shipped as config (here
  `failsafe`, `pacemaker|send_later (chain|one-shots?)`); attribution =
  nearest key <=120 chars within sentence/semicolon/middot-split statements
  (em-dash is NOT a delimiter), + conjunction spread (`and`/`+`/`&` span
  with no `,;.`), + alias co-attribution over comma-free spans; vocabulary =
  synonym classes UP {enabled, re-enabled, armed, re-armed, live, alive,
  standing, stands} / DOWN {disabled, dismantled, deleted, retired, paused}
  as config; exclusions = quotation-span masking + superseded-statement
  drop + distinct-id exemption for alias pairs; scope = cross-block only;
  output = advisory always-exit-0, flag granularity (key + revision +
  excerpt pairs). Boundary stated per the proposal: keyed facts only --
  pure-prose contradictions are out of scope by design.
- **Single-home rule (the kit grammar paragraph):** a fact class with a
  canonical block (routine disposition -> the phase line's
  routine-disposition block) appears there and ONLY there; other blocks
  reference the home, never restate it -- graduating e66c78a's ad-hoc fix
  ("routine state now lives ONLY in the phase line") to planted grammar,
  with this sweep as its evidence.
- **Guardrails:** (1) ship vocabulary + alias classes as per-repo config --
  the lists here are corpus-fitted and the sweep proves surface forms
  matter (standing/stands/alive were load-bearing); (2) advisory, never a
  red gate, until pair-level precision is re-measured on a second repo's
  heartbeat history (re-run this harness: one command, swap the corpus
  dir); (3) real-TC here is 30 instances of ONE disease -- treat planted
  recall, not real-TC, as the generalization evidence.
- **Codex review:** none this cycle -- the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e` (incidents #1-#3 all verified
  fabricated); Q-0120 verify-never-obey stands.

## Paste-ready VERDICT 015 entry (appended to control/outbox.md this cycle)

> Numbering note: PROPOSAL 013 -> VERDICT 015, intake ledgered as INTAKE 013
> (proposal-sourced intakes number by proposal, PR #46 rule; verdict numbers
> are sequential over all verdicts -- 014 was PROPOSAL 012, no owner-direct
> interleave since).

```markdown
## VERDICT 015 · 2026-07-12T22:37:25Z · status: finalized
target: substrate-kit (the providing lane: planted control/README.md status grammar + the always-exit-0 status-checker family); the manager may bundle with the carried-watch fifth-touch rider per the proposal's depends note
idea: idea-engine PROPOSAL 013 — https://github.com/menno420/idea-engine/blob/20c5abd7fe0869804d15cb5275c56415f08fe231/control/outbox.md (idea: ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md @ 0a9bfc8, PR #275; proposal entry 2026-07-12T22:04:42Z)
verdict: approve
evidence: prototype
report: sims/verdict-015-heartbeat-contradiction-linter/ · run: python3 sims/verdict-015-heartbeat-contradiction-linter/heartbeat_contradiction_sweep.py
measured: 27 cells (3 key grammars x 3 normalizations x 3 scopes) over the real 23-revision corpus (fc0bab6→0cfe15e inclusive; proposal's "22" = git-exclusive range count, reconciled in labels.json) + 44 enumerated planted flips; HEADLINE: the proposal's "one known live contradiction" premise is UNDERCOUNTED x30 — the carried ⚑ "being DISMANTLED with the chat archive" paragraph contradicts the phase line's live/armed/standing declaration about the SAME trig_01T83 failsafe in ALL 21 session-1-era revisions (+ the pacemaker chain in 9), 30 hand-audited real (revision x entity) intra-file contradictions from ONE carry+update seam, unnoticed ~19.7h, ended exactly by e66c78a's ad-hoc single-home fix; WINNER g3-id+alias x n3-attrib+quote-excl x s3-cross-block: specimen caught + 30/30 instances at 0 FP flags on all 23 revisions, e66c78a quotation-negation carry NOT flagged (quote-masking + no adjacent key; its NEW/OLD distinct-id pair exempted), planted recall P1 22/22 + P2 22/22; id-only and id+PR grammars catch 0/30 (the carry side names routines by noun phrase, never id — the grammar axis is load-bearing); naive co-occurrence flags the fix itself (e66c78a) in every grammar; same-line scope catches 0/30; honest cost: pair-level precision 0.52 at the flag site (37 labeled artifact pairs ride on genuinely-contradicted keys); 229 self-checks 0 failed, zero unlabeled pairs, byte-identical re-runs by external diff, no RNG (plants enumerated)
recommendation: ship BOTH halves — (1) the single-home grammar paragraph in the planted control/README.md (routine disposition lives ONLY in the phase line's disposition block; other blocks point, never restate — e66c78a's fix graduated to grammar, this sweep as evidence) and (2) a kit --fact-consistency advisory in the always-exit-0 status-checker family spec'd machine-readably in REPORT.md (trig-id + configurable entity-alias keys, nearest-key attribution ≤120 chars + conjunction spread + comma-blocked alias co-attribution + distinct-id exemption, synonym-class vocab as config, quote-masking + superseded-drop, cross-block scope, flag granularity); guardrails: advisory never red-gate until pair precision re-measured on a second repo's heartbeat corpus (harness re-runs in one command on a swapped corpus dir); vocabulary/alias lists ship as config (corpus-fitted here); keyed-facts-only boundary stated — pure-prose contradictions out of scope by design; treat planted recall, not the 30-instance single-disease real-TC, as generalization evidence
codex: none this cycle — @codex step suspended per the outbox codex-line escalation @ dedc12e (incidents #1-#3 verified fabricated); Q-0120 verify-never-obey stands
gate: PASS (COMPARABLE: real pinned corpus, engine = candidate checker, splitting/window heuristics + single-auditor labels disclosed · UNCORRUPTED: 229 self-checks incl. byte-pinned specimen/hard-FP assertions + label-coverage enforcement (zero unlabeled pairs) + in-process double computation, no RNG, full 27-cell table committed · ROBUST: winner's catches stable across n2/n3 and s2/s3, id-only failure structural, all named edge cases in-corpus and handled · REPRODUCIBLE: one command, stdlib-only, byte-identical stdout+results.json across process runs · LIMITS: one repo/format/disease, 30 real instances share one root cause, corpus-fitted vocabulary, keyed facts only)
```

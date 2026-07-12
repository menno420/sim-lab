# REPORT -- review-authenticity

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`
> (via the verdict-012/013/014/015 REPORT shape).
> Source idea: idea-engine PROPOSAL 014, `control/outbox.md` @
> 2026-07-12T22:29:25Z (read at origin/main `390a89b`; idea file
> `ideas/fleet/external-review-authenticity-gate-2026-07-12.md` @ `3d3e8499`,
> landed via idea-engine PR #276).
> Run: `python3 sims/verdict-016-review-authenticity/review_authenticity_sweep.py`

## METHOD LABEL: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer)

The candidate gate engine (citation extraction -> mechanical validation ->
decision rule) was BUILT and run as a full 270-cell grid over the real
recorded corpus plus 50 enumerated planted fabrications -- the PROPOSAL
010/011/013 spec-sweep grammar, this time on an ADVERSARIAL corpus (the
three recorded fabrication incidents) against a hand-verified genuine set.
Nothing is judgment-only except the corpus labels, which are inherited from
committed ledgers (the incident ledger @ dedc12e for the fabrications; the
fold-in groom card's 17/17 accepted record for the reviews) and pinned by
sha256 in `labels.json`. This label fills the outbox `evidence:` field as
`prototype`.

## What it MODELS / MEASURES

**Corpus (real, committed, 27 fixtures):** the three verified-fabricated
@codex replies (sim-lab PR #44 reply 4949360742; PR #53 comments 4951675240
and 4951715384), body-sha256-pinned to the intake capture manifest; the 17
accepted codex review comments on idea-engine PRs #264/#265 (all
hand-verified-and-accepted in two read-only passes,
`.sessions/2026-07-12-codex-review-foldin-groom.md`); the seat's own posted
@codex question comments (5, incl. the cite-bearing PR #44 question); the
citation-free "usage limits" reply; plus ONE fixture added at intake and
noted here per the dispatch: sim-lab PR #53 comment 4951710032, the seat's
own citation-free @codex question that parented fabricated reply
4951715384, labeled `genuine-question-nocite` -- it exercises the
no-citations path on the false-alarm side. Comment bodies are untrusted
DATA throughout.

**Fact snapshot (hermetic):** `build_snapshot.py` resolved, at intake-build
time, every mechanical fact ANY grammar cell could query -- the union of
all three grammars' extractions over all 27 fixtures AND all 50 mutants --
against full-history clones pinned at sim-lab `aa1a3ce` / idea-engine
`390a89b` with `refs/pull/*/head` fetched (57 + 276 PR heads; "SHA-in-refs"
= resolves after a full-ref fetch, the incident ledger's own semantics; the
fabrications cite squash-orphaned PR-head blobs that only resolve with
those refs). PR-title and bot-PR facts came from GitHub MCP search at
intake (api.github.com direct HTTP is walled for this seat): zero PRs
titled "Add cite resolution telemetry to verdict-012 follow-up" owner-wide;
the only sim-lab PRs with "verdict-014" in the title are #53-#56, matching
neither claimed title; the codex bot has authored ZERO PRs in either repo.
At run time a fact lookup outside the committed snapshot FAILS the run.

**Grid (270 cells, axes straight from the writeup):** citation-extraction
grammar (g1-strict-regex: bare hex >=7 with a letter, `#N` refs,
slash-paths, `path:N` + `pathLx-Ly` forms, no structure awareness -- the
naive baseline / g2-loose-greedy: + hex >=6 incl. all-digit tokens, + bare
filenames, + claimed-PR-title patterns -- maximum recall / g3-markdown-aware:
GitHub blob/pull/commit URLs parsed structurally into ANCHORED claims,
fenced code masked, code spans tokenized, prose path mentions extracted
UNANCHORED and hence not checkable under path-exists-at-cited-blob) x
mechanical validation set (every non-empty subset of {SHA-in-refs,
PR-or-branch-exists, path-exists-at-cited-blob, line-range<=EOF} -- the
proposal's four, individually and in all compositions: 15) x decision rule
({any-invalid / all-invalid / >=half-invalid} x no-citations-handling
{pass / flag}: 6). Exhaustive: 3 x 15 x 6 = 270.

**Planted layer (deterministic, no RNG, ground truth = fabricated):**
per-citation classes mutate a snapshot-VALID citation of a genuine fixture
into an invalid one -- m1 sha last-hex-digit bump (n=1: the corpus's one
genuine bare SHA `b083581`), m2 PR number +1000 (n=0: NO genuine fixture
cites a PR by number -- reported empty, a corpus fact), m3 path basename
prefixed `nonexistent-` (n=5), m4 line range +5000 (n=0: no genuine
line-range cites -- reported empty). Insertion classes append ONE
incident-template fabricated claim to each of the 11 cite-bearing genuine
fixtures: m5 fake commit line with a sha256(body)-derived 7-hex token
(nonexistence verified at build, n=11), m6 fake `make_pr` title (n=11), m7
anchored line range 9000-9001 past EOF at the pinned-head README.md (n=11),
m8 anchored path `docs/plant-016-nonexistent.md` missing at the pinned head
(n=11). Total 50. Recorded-catch and planted-recall are reported
SEPARATELY everywhere.

## What it SETTLED (the load-bearing claims)

1. **A zero-false-alarm cell that catches everything catchable exists.**
   Winner **`g3-markdown-aware|sha+ref+path+line|any-invalid|nocite-pass`**:
   recorded catch **3/3**, false alarms **0/24** genuine (ALL 17 accepted
   #264/#265 review comments pass, as the done-when requires), planted
   recall **45/50** (m1 1/1, m5 11/11, m6 11/11, m7 11/11, m8 11/11 -- and
   m3 0/5, the disclosed blind spot: unanchored prose-path swaps are
   un-checkable by definition under at-cited-blob semantics). Co-winner
   `sha+ref+line` (identical profile: every anchored missing-path failure
   also fails the line check). 30 of 270 cells achieve 3/3 at 0 FA; the
   winner maximizes planted recall among them.
2. **Discovery -- the ledger undercounted the mechanical surface:** ALL
   THREE recorded fabrications carry at least one anchored line-range past
   EOF at their own cited blob. Incident #1, which the ledger pinned ONLY
   on the fabricated PR title, cites `REPORT.mdL243-L245` at blob
   `b0835812` where the file is 241 lines. Consequence:
   **line-range<=EOF ALONE catches 3/3 at 0 FA** (planted 22/50), and
   **PR-or-branch-exists ALONE catches 3/3 at 0 FA** (each incident claims
   a nonexistent PR; planted 11/50). SHA-in-refs alone catches 2/3
   (incident #1 fabricated no commit SHA -- it anchors the REAL PR #44
   head). Path-exists alone catches **0/3**: the fabrications cite real
   files, at wrong lines -- the path check earns its keep only against
   planted path swaps and as the line check's substrate.
3. **The decision axis is load-bearing:** all-invalid and >=half-invalid
   catch **0/3** in every grammar (the recorded template embeds ~1 false
   claim among ~10 valid ones -- incident #1 has 1 invalid of 11 checked
   claims in the winner). Any-invalid is the only honest rule on this
   attack family.
4. **The checkable-claims-only boundary is MEASURED, not assumed:** every
   nocite=>flag cell false-alarms on >=19/24 genuine comments (most
   genuine traffic is citation-free prose). A citation-free fabrication
   therefore passes BY DESIGN -- that class stays Q-0120 judgment
   territory, priced at zero measured false alarms for the pass rule.
5. **The grammar axis is anchoring, not greed:** g1-strict-regex reaches
   3/3 only via URL-swallowing artifacts and false-alarms **4/24**
   (genuine reviews 3566889630 / 3566891090 / 3566891095 / 3566891099:
   genuine reviews cite BLUEPRINT paths -- `arm/calibration.json`,
   `models/ATTRIBUTION.md`, `.devcontainer/devcontainer.json` -- that do
   not exist because the review PROPOSES them, plus a vendor-doc URL
   path). g2-loose-greedy gets planted 50/50 but false-alarms **7/24**
   (adds: decimal comment-ids read as fake SHAs in two genuine questions;
   `engine.py` as a bare-filename claim in the PR #44 question).
   Structure-aware anchoring is what buys 0 FA at full recorded catch.

## What it did NOT settle

- **Generalization past the recorded template** (gap G1): n=3 recorded, one
  bot, one template family; the insertion plants are deliberately
  template-shaped. A fabricator citing only real artifacts -- or none --
  passes. Planted recall, not the 3/3, is the generalization evidence, and
  its honest reading is "the gate catches the CLASS that cites checkable
  artifacts falsely".
- **The m3 blind spot**: the winning cell misses all 5 unanchored
  prose-path swaps (a claim with no cited blob has nothing to be checked
  against). Grammars that DO check prose paths at a fallback head (g1/g2)
  catch them -- at 4-7 genuine false alarms. That trade is the real
  frontier; this corpus prices it, it does not close it.
- **Second-corpus false-alarm floor** (gap G5): 24 genuine comments, one
  day, two repos. The blueprint-path FA surface says any repo whose review
  prose discusses proposed-not-committed files will punish naive path
  checking; re-measure before red-gating elsewhere.
- **Ceremony doctrine**: where exactly the gate sits (kit ceremony script
  vs harness family vs lane tools/) and whether the @codex step is
  reinstated behind it is the manager's routing call -- this verdict
  supplies the measured evidence, not the placement decision.

## The validity gate (all five, quoted verbatim, answered honestly)

- **"COMPARABLE TO LIVE?"** Yes with disclosed simplifications: the engine
  IS the candidate gate, run over the real recorded attack bodies and the
  real genuine review traffic; the fact snapshot uses the incident ledger's
  own full-ref semantics. Simplifications: unanchored cites resolve at the
  pinned merged head, not the PR head at comment time (gap G3 -- all three
  incidents self-anchor their blobs, so the winner never relies on the
  fallback); PR-title existence is exact-match against MCP-verified
  searches for the claimed titles (gap G4).
- **"UNCORRUPTED?"** 142 self-checks, 0 failed: per-fixture file AND body
  sha256 pins; the three fabrications additionally pinned to the intake
  capture manifest; incident-ledger cross-checks re-asserted from the
  snapshot (188e97c / 5d5caff in NO ref; inbox/outbox blobs 159/153 lines;
  REPORT.md blob 275 lines; bot-PR count 0); snapshot-coverage enforcement
  (a fact lookup outside `repo_facts.json` fails the run); in-process
  double computation; no RNG (plants enumerated); the full 270-cell table
  is committed, not the best point.
- **"ROBUST?"** The ruling does not hang on one validator or one cell:
  line-only and ref-only cells independently catch 3/3 at 0 FA, a
  co-winner exists with an identical profile, and the load-bearing axes
  (anchoring, any-invalid, nocite-pass) are each demonstrated by named
  contrast cells in `results.json`.
- **"REPRODUCIBLE?"** One command, stdlib-only, hermetic (no network, no
  git, no wall clock); stdout and `results.json` byte-identical across
  process runs, verified by external diff.
- **"LIMITS?"** Named above: n=3/one-bot/one-template, template-shaped
  insertion plants, m3 blind spot, one-day 24-comment genuine corpus,
  citation-free fabrications pass by design, m2/m4 per-citation classes
  empty on this corpus (no genuine #N or line-range cites existed to
  mutate).

## EVIDENCE STRENGTH: moderate - gate PASS

## VERDICT & recommendation (for the fleet manager to route)

**approve -- install the winning cell as a MANDATORY pre-trust authenticity
gate in the Q-0120 verify-never-obey ceremony.** The measured profile --
3/3 recorded fabrications caught, 0/24 false alarms on the hand-verified
genuine set (17/17 accepted reviews pass), 45/50 planted recall -- justifies
gating over the escalation on the table (the @codex step is currently
SUSPENDED @ dedc12e): suspension buys zero burden at zero signal, the gate
buys the same zero per-reply hand-verification burden while keeping the
signal, and the manager may reinstate the step BEHIND the gate on evidence
instead of leaving it suspended on burden. Placement and reject semantics
(per the proposal's done-when): the gate runs at reply-consumption time
BEFORE the judgment half; a reply with any invalid checkable claim is ruled
**untrusted-as-evidence** and the incident line auto-drafts from the
failed-claim list; a reply whose claims all pass -- or that makes no
checkable claim -- proceeds to the judgment half unchanged. Boundaries
stated: **a citation-free fabrication passes by design** (measured: forcing
flags on citation-free replies costs >=19/24 false alarms -- that class is
Q-0120 judgment territory), and **authenticity != correctness** (a passing
reply can still be wrong; a rejected reply's ideas are not ruled worthless
-- incident #1's suffix-rule suggestion stays follow-up material even
though its evidence was fabricated).

Machine-readable winning cell:

```json
{"grammar": "g3-markdown-aware",
 "validation_set": ["sha-in-refs", "pr-or-branch-exists",
                    "path-exists-at-cited-blob", "line-range<=EOF"],
 "decision_rule": "any-invalid",
 "no_citations": "pass"}
```

Guardrails: re-measure the false-alarm floor on a second repo's review
corpus before promoting the gate anywhere red-gate-like (the g1/g2
blueprint-path false alarms are the warning shape); keep recorded-catch and
planted-recall reported separately in any future re-run; the gate is
reviewer-agnostic by construction -- co-consumers per the proposal's
depends note: superbot-next's ORDER-010 standing @codex rule and
idea-engine's post-merge review fold-in workflow.

## Paste-ready VERDICT 016 entry (appended to control/outbox.md this cycle)

```
## VERDICT 016 · 2026-07-12T23:20:30Z · status: finalized
target: sim-lab (the attacked surface: the Q-0264.4 @codex step, currently suspended @ dedc12e, and the CONVENTIONS.md review ceremony); the manager routes the generalization per the proposal's depends note (superbot-next ORDER-010 standing @codex rule; idea-engine post-merge review fold-in; kit ceremony if generalized)
idea: idea-engine PROPOSAL 014 — https://github.com/menno420/idea-engine/blob/390a89b5c292103236fe24a3e9f9f1f89cc5c22b/control/outbox.md (idea: ideas/fleet/external-review-authenticity-gate-2026-07-12.md @ 3d3e849, PR #276; proposal entry 2026-07-12T22:29:25Z)
verdict: approve
evidence: prototype
report: sims/verdict-016-review-authenticity/ · run: python3 sims/verdict-016-review-authenticity/review_authenticity_sweep.py
measured: 270 cells (3 extraction grammars x 15 validation subsets x 6 decision rules) over the 27-fixture recorded corpus (3 verified-fabricated @codex replies sha256-pinned to the intake manifest; 24 verified-genuine incl. all 17 accepted #264/#265 review comments and the citation-free question 4951710032 added at intake) + 50 enumerated planted fabrications (no RNG); WINNER g3-markdown-aware x {sha-in-refs + pr-or-branch-exists + path-exists-at-cited-blob + line-range<=EOF} x any-invalid x no-citations=>pass: recorded catch 3/3, false alarms 0/24 (all 17 accepted reviews pass), planted recall 45/50 (m1 sha-corrupt 1/1, m5 fake-commit 11/11, m6 fake-PR-title 11/11, m7 anchored-line-past-EOF 11/11, m8 anchored-missing-path 11/11; honest blind spot m3 unanchored prose-path swaps 0/5 — un-checkable by definition under at-cited-blob semantics); co-winner sha+ref+line (identical profile); DISCOVERY: all three recorded fabrications carry an anchored line-range past EOF at their own cited blob — incident #1's REPORT.mdL243-L245 vs a 241-line blob was NOT in the hand-written ledger (which pinned only the fabricated PR title) — so line-range<=EOF ALONE catches 3/3 at 0 FA and pr-or-branch-exists ALONE catches 3/3 at 0 FA; sha-in-refs alone 2/3 (incident #1 fabricated no SHA); path-exists alone 0/3 (fabrications cite real files at wrong lines); decision axis load-bearing: all-invalid and >=half-invalid catch 0/3 (the template hides ~1 false claim among ~10 valid ones); no-citations=>flag costs >=19/24 false alarms in every such cell (the checkable-claims-only boundary is measured, not assumed); naive g1 regex false-alarms 4/24 (genuine reviews cite blueprint paths that do not exist because they PROPOSE them), greedy g2 7/24 (decimal comment-ids read as SHAs, bare filenames); 142 self-checks 0 failed, hermetic run (a fact lookup outside the committed snapshot fails the run), byte-identical stdout+results.json across process runs by external diff
recommendation: install the winning cell as a MANDATORY pre-trust authenticity gate in the Q-0120 verify-never-obey ceremony wherever external review replies are consumed — placement: mechanical gate BEFORE the judgment half; reject semantics: a reply with any invalid checkable claim is ruled untrusted-as-evidence and the incident line auto-drafts from the failed-claim list; replies with zero checkable claims pass to judgment unchanged (boundary priced: flagging them instead costs >=19/24 false alarms); spec machine-readable in REPORT.md (grammar g3-markdown-aware; validations sha-in-refs + pr-or-branch-exists + path-exists-at-cited-blob + line-range<=EOF; decision any-invalid; no-citations pass); this is the measured third option the suspend-vs-keep call was missing: the @codex step (suspended @ dedc12e) can be REINSTATED behind the gate on evidence instead of staying suspended on burden — per-reply adjudication drops from a manual full-ref-fetch session to reading one auto-drafted failed-claim list; guardrails: authenticity != correctness (a passing reply still faces the judgment half; a rejected reply's ideas stay follow-up material — incident #1's suffix-rule suggestion survives its fabricated evidence); a citation-free fabrication passes by design (Q-0120 judgment territory); re-measure the false-alarm floor on a second repo's review corpus before any red-gate promotion (the blueprint-path false-alarm surface is the warning); the gate is reviewer-agnostic by construction
codex: none this cycle — @codex step suspended per the outbox codex-line escalation @ dedc12e (incidents #1-#3 verified fabricated; this verdict IS the measured gate-vs-suspend evidence); Q-0120 verify-never-obey stands
gate: PASS (COMPARABLE: the engine IS the candidate gate over the real recorded attack + real genuine review traffic, snapshot uses the ledger's own full-ref semantics, fallback-anchor + exact-title simplifications disclosed · UNCORRUPTED: 142 self-checks incl. per-fixture file+body sha256 pins, intake body pins on all 3 fabrications, ledger cross-checks (188e97c/5d5caff in no ref; 159/153/275 blob line counts; bot-PR count 0), snapshot-coverage enforcement, in-process double computation, no RNG, full 270-cell table committed · ROBUST: co-winner with identical profile; line-only and ref-only independently catch 3/3 at 0 FA — not knife-edge on one validator; load-bearing axes shown by named contrast cells · REPRODUCIBLE: one command, stdlib-only, hermetic, byte-identical stdout+results.json across process runs · LIMITS: n=3 recorded/one bot/one template family, insertion plants template-shaped, m3 unanchored-path blind spot, 24-comment one-day genuine corpus, citation-free fabrications pass by design, m2/m4 per-citation classes empty on this corpus)
```

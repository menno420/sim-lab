# verdict-012 · doc-cite-checker-spec

Spec sweep for `tools/check_doc_cites.py` (superbot-next). Answers idea-engine
PROPOSAL 010 (control/outbox.md @ `a9b41f6d`): which cite grammar (regex), doc-tree
scope, and warn-vs-red gating the checker should ship with, measured as true catches
vs false positives per variant on the two real doc corpora
(superbot-next@`2c62a099`, superbot@`b2b7fe0c`) plus a planted synthetic corpus.

## Run (one command)

```
python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py
```

Exit 0 iff all 453 self-checks pass. Deterministic — NO RNG anywhere (the rule-c
audit sample is a fixed stride over the sorted flag list); stdout and `results.json`
are byte-identical across re-runs. First run fetches the two pinned corpora into
`./corpora/` (gitignored) via shallow `git fetch origin <sha>`; SHA-pinning makes
the cache a transport detail, not an input degree of freedom. Runtime ~5 s warm,
plus the two shallow fetches cold.

## Files

- `cite_checker_sweep.py` — checker prototype + 36-variant/corpus sweep
  (3 grammars × fence-skip on/off × 2 scopes × 3 resolution policies × rule ladder
  a/b/c) + synthetic planted corpus + fabrication check + 453 self-checks.
- `labels.json` — the hand audit: every unique (doc,path) pair flagged at rule a/b
  by the audit variant on BOTH corpora (78 + 45 pairs), classified true-catch vs
  false-positive with per-pair reasons, plus the stated 15-pair rule-c sample.
- `results.json` — committed run output: full sweep table, per-variant audited
  TC/FP counts, every flagged cite line of the audit variant (1132 + 8 records),
  fabrication-check detail, synthetic precision/recall.
- `REPORT.md` — the finalizable verdict report (validity gate + ruling +
  paste-ready VERDICT 012 outbox entry).

## Verdict (summary — full report in REPORT.md)

**approve** · evidence: prototype (measured spike w/ numeric sweep) · gate PASS.
The ruling: grammar = strict slash-required + segment-letter guard + fenced-block
skip over exts {py,ts,tsx,yml,yaml}; scope = all tracked `*.md` minus a configured
foreign-roots skip list; resolution = exact-or-unique-suffix (ambiguous passes);
gating = rule (a) missing-file RED (0 FP measured on the target tree across all
variants at the chosen spec), rule (b) line-range WARN (16/29 audited superbot
flag-pairs are ≤2-line EOF boundary noise), rule (c) identifier-near NOT shipped
(sampled precision 1/15). The known `WorkflowResult`/`disbot/core/contracts.py:48-52`
fabrication class is caught by every grammar (file verified ABSENT from superbot @
`b2b7fe0c`; all 7 surviving cite instances are correction notes, which is why the
red gate also needs an inline waiver token).

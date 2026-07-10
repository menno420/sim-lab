# REPORT -- <idea slug>

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: <idea-engine outbox entry @ SHA, or control/inbox.md citation>
> Run: `python3 sims/<slug>/<script>.py`

## METHOD LABEL: <NUMERIC SIMULATION | MEASURED PROTOTYPE/SPIKE | JUDGMENT-ONLY>

<One line: why this rung is the cheapest ADEQUATE evidence for this idea. This
label fills the outbox `evidence:` field and travels with the verdict.>

## What it MODELS / MEASURES

<The dynamics modeled or the thing built. Parameters, seeds (SEEDS), sweep grid.
State the smallest faithful model plainly.>

## What it SETTLED (the load-bearing claims)

<Each claim cites a committed run / number. Recommended defaults vs analytic
caps. Numbers, not adjectives.>

## What it did NOT settle

<Negatives as HEADLINES, not footnotes. What stayed out of scope.>

## The validity gate (all five, quoted verbatim, answered honestly)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

<answer>

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point)"*

<answer -- cite the self-check count, the SEEDS used, and the FULL sweep table>

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

<answer>

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

<answer -- the one run command; the determinism check>

**5. LIMITS?** *"what this evidence does NOT show"*

<answer>

## EVIDENCE STRENGTH: <weak | moderate | moderate-strong | strong> - gate PASS|FAIL

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict:** <approve | reject | needs-more-evidence>
- **Ruling:** <only when needs-more-evidence -- what would settle it>
- **Target:** <repo(s)>
- **Recommended implementation:** <the best implementation found>
- **Named changes:** <concrete>
- **Guardrails:** <>
- **Telemetry:** <>
- **Codex review:** reply: pending

<!-- Outbox verdict-grammar block (README), emitted on finalization:
VERDICT <n> - <ISO> - finalized
target: <repo>
idea: <source @ SHA>
verdict: <approve|reject|needs-more-evidence>
evidence: <ladder label>
report: sims/<slug>/REPORT.md
run: python3 sims/<slug>/<script>.py
recommendation: <one line>
codex: <disposition>
gate: PASS|FAIL
-->

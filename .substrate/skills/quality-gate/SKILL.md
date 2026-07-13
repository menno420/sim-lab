---
name: quality-gate
description: "Run the project's full verification before pushing and report what must be fixed."
---

# quality-gate

Prove a change is good before pushing sim-lab.

1. Run `python3 bootstrap.py check --strict (the substrate gate); plus each touched sim's own documented run command reproducing its committed result` — the project's full verification (tests + lint/types).
2. Run `python3 bootstrap.py check --strict` — doc + session-log hygiene.
3. Report every failure with the exact command to reproduce it.
4. Do NOT push on red — green here should mean green in CI.

Declared capabilities: run.

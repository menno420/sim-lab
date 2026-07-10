# CAPABILITIES.md — sample render (schema `CAPABILITIES.v1`)

> DETERMINISTIC sample emitted by `analyze.py` over the frozen runs. **Seat-annotated** — a whole-repo single-seat regeneration would launder one seat's absences into repo-wide walls (see the three-way diff).

> Frozen run stamps: 2026-07-10T23:05:22.163908Z .. 2026-07-10T23:05:26.995389Z (5 runs).


## Subprocess plane (seat-invariant, read-only probed)

| id | result | agreement | baseline | false-wall | false-cap |
|----|--------|-----------|----------|-----------|-----------|
| sp:tool-git | present | 1.00 (5 runs) | present | False | False |
| sp:net-raw-cross-repo | present | 1.00 (5 runs) | present | False | False |
| sp:net-api-repo-object | wall | 1.00 (5 runs) | wall | False | False |
| sp:net-api-branch-protection | wall | 1.00 (5 runs) | wall | False | False |
| sp:net-proxy-status | present | 1.00 (5 runs) | present | False | False |
| sp:env-token-names | present | 1.00 (5 runs) | present | False | False |
| sp:push-main | not-probeable | n/a (0 runs) | wall | False | False |

## Agent plane — seat: `coordinator`

| id | result | baseline | false-wall | false-cap |
|----|--------|----------|-----------|-----------|
| ap:subagent-spawn | present | capable | False | False |
| ap:bash-shell | absent | capable | True | False |
| ap:file-io | absent | capable | True | False |
| ap:grep-glob | absent | capable | True | False |
| ap:github-mcp | present | capable | False | False |
| ap:webagent-reply | present | capable | False | False |
| ap:send_later-selfbind | present | capable | False | False |
| ap:create_trigger-crosssession | present | walled | False | True |
| ap:workflow | present | capable | False | False |

## Agent plane — seat: `worker`

| id | result | baseline | false-wall | false-cap |
|----|--------|----------|-----------|-----------|
| ap:subagent-spawn | absent | capable | True | False |
| ap:bash-shell | present | capable | False | False |
| ap:file-io | present | capable | False | False |
| ap:grep-glob | present | capable | False | False |
| ap:github-mcp | present | capable | False | False |
| ap:webagent-reply | absent | capable | True | False |
| ap:send_later-selfbind | present | capable | False | False |
| ap:create_trigger-crosssession | present | walled | False | True |
| ap:workflow | present | capable | False | False |

## Roll-up

- seat divergence (agent plane): **5** items — ap:subagent-spawn, ap:bash-shell, ap:file-io, ap:grep-glob, ap:webagent-reply
- false-walls (single-seat vs fleet baseline): **5**
- false-capabilities: **1** — ap:create_trigger-crosssession
- subprocess-plane flaky items: none
- baseline-B (fleet-manager) reachable from probing seat: True

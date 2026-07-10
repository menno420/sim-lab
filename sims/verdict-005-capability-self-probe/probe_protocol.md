# Probe protocol — VERDICT 005 capability self-awareness probe (re-measurement spec)

This is the exact two-plane battery that produced `runs/`. The **live layer is the real
environment** (git, network, env, and the running seat's own toolset), so re-running yields
a **similar-but-not-identical** transcript — a network status can flake, a seat's tools are
whatever that seat was granted. `analyze.py` is what reproduces exactly, byte-for-byte, over
the frozen `runs/`.

## The two planes

- **Subprocess plane** — facts a stdlib Python subprocess can test read-only from *inside*
  the container: is `git` here, does a raw cross-repo URL answer, does `api.github.com`
  answer or 403, is the egress proxy reachable, which env-var NAMES look like credentials.
  These are **seat-invariant** (any seat's subprocess sees the same container) and
  **read-only**. `probe.py` tests them live and records `present | wall | error` with the
  verbatim status/exception. One subprocess item, `sp:push-main`, is **not** read-only
  probeable (a real push is a side-effect), so it is carried from the ledger as a wall.
- **Agent plane** — which *tools* the running seat holds: subagent-spawn, Bash, file I/O,
  grep/glob, GitHub MCP, webagent reply, `send_later`, `create_trigger`, workflow control.
  These are **seat-variant** and are **not** subprocess-testable — a subprocess cannot see
  the agent's tool list. `probe.py` therefore emits every agent-plane item as
  `not-probeable / source=ledger`; the real `present/absent` values are captured by each
  seat, in its own voice, in `runs/agent_inventory_<seat>.json`.

## The ≥2 documented seat types

| seat | what it is | agent-plane toolset (measured this cycle) |
|------|-----------|-------------------------------------------|
| **coordinator** | the orchestrating session — the one that talks to the owner and dispatches work | subagent-spawn ✓, webagent-reply ✓, github-mcp ✓, send_later(self-bind) ✓, create_trigger ✓ (cross-session bind **org-walled**, OA-003), workflow ✓ — **no** Bash / file / grep of its own |
| **worker** | a coordinator-spawned Bash seat (this session) | Bash ✓, file-io ✓, grep/glob ✓, github-mcp ✓, send_later ✓, create_trigger ✓ (cross-session bind org-walled), workflow ✓ — **no** subagent-spawn, **no** webagent-reply |

The two seats are the OA-003 `create_trigger`/`send_later` split made concrete: the
coordinator spawns workers and self-binds triggers; a worker has the hands (Bash/file/grep)
but cannot spawn or reply to the owner. Their five *seat-defining* tools are disjoint
(subagent-spawn + webagent-reply on the coordinator; Bash + file-io + grep-glob on the
worker); the four platform tools (github-mcp, send_later, create_trigger, workflow) are shared.

## The battery (subprocess plane, `probe.py`)

| id | probe | pass/wall rule |
|----|-------|----------------|
| `sp:tool-git` | `git --version` | exit 0 → present |
| `sp:net-raw-cross-repo` | GET `raw.githubusercontent.com/menno420/idea-engine/main/control/outbox.md` | 200 → present |
| `sp:net-api-repo-object` | GET `api.github.com/repos/menno420/sim-lab` | 403 → wall (verbatim body head) |
| `sp:net-api-branch-protection` | GET `.../branches/main/protection` | 403 → wall (OA-001 note) |
| `sp:net-proxy-status` | GET `$HTTPS_PROXY/__agentproxy/status` | reachable → present |
| `sp:env-token-names` | scan env keys `~(TOKEN|KEY|SECRET|PASSWORD|CRED)` | any → present; **NAMES + count only, never values** |
| `sp:push-main` | *not run* | `not-probeable`, ledger wall (CONVENTIONS forward-only + OA-001) |

All HTTP honors `HTTPS_PROXY`, ~10 s timeout; any exception → `error` with the verbatim text.

## Run commands

```
# live layer (per seat, per run) — non-deterministic:
for i in 1 2 3 4 5; do \
  python3 sims/verdict-005-capability-self-probe/probe.py \
    --seat worker --run-id $i \
    --out sims/verdict-005-capability-self-probe/runs/probe_worker_run$i.json; done

# agent-plane inventories — each seat enumerates its OWN tools (ToolSearch + known toolset),
#   writing runs/agent_inventory_<seat>.json  (a subprocess cannot do this for the seat).

# baseline — hand-assembled from the ledgers into runs/baseline.json (cite every item).

# deterministic layer — reproduces exactly:
python3 sims/verdict-005-capability-self-probe/analyze.py
```

## How to re-measure

1. Re-run `probe.py` N times in each seat (freeze each transcript into `runs/`).
2. Re-enumerate each seat's agent inventory (tools can change between grants).
3. Refresh `runs/baseline.json` from the current ledgers.
4. Run `analyze.py` — it recomputes agreement, seat-divergence, and the three-way diff.

## Why the environment probes are NOT seed-deterministic

There is no seed for "is the network up" or "what tools does this seat hold." A status code
can flake; a 403 body can change wording; a seat is granted whatever it is granted.
**Reproducibility here is defined as (a) agreement-rate bounds over N frozen runs** — the
subprocess plane was **unanimous (rate 1.00) on all six items across 5 runs this cycle** — and
**(b) byte-identical `analyze.py` output over the frozen runs** (verified: same md5 on
re-run). Only `analyze.py` is bit-identical; the live layer is honest-but-noisy by nature,
and the report says so rather than dressing a live probe as a seeded simulation.

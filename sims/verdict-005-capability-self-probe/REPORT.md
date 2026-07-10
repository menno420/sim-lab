# REPORT — VERDICT 005 / PROPOSAL 005: capability self-awareness probe (two-seat)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> **Source idea:** `menno420/idea-engine` `control/outbox.md` **PROPOSAL 005** pinned
> `e0f207d51aa731ce6924abff84aca63727b42d97` (canonical superbot
> `docs/ideas/project-capability-self-awareness-2026-07-10.md` @
> `9624c5399f5b1a3da293c07ce930e8b0410d79e4`; batched agent-plane half
> `ideas/superbot/session-start-capability-self-probe-2026-07-10.md` folded in). **Probe +
> analyzer:** this subtree. **Run:**
> `python3 sims/verdict-005-capability-self-probe/analyze.py`
> (deterministic, stdlib-only, exit 0 iff all 394 self-checks pass; recomputes every number
> from the frozen `runs/`).

---

## METHOD LABEL: `MEASURED PROTOTYPE` (rung 2)

Method ladder rung 2 (MEASURED PROTOTYPE/SPIKE — "build the smallest real thing and measure
it"). Capability availability has **no seedable dynamics to simulate**: whether `api.github.com`
403s, whether a seat holds the subagent-spawn tool, whether a cross-session trigger binds — these
are facts of THIS live container and THIS session's grant, discoverable only by probing them.
So the sim builds the smallest real probe (a stdlib two-plane read-only battery), runs it from
**two documented seat types**, freezes the transcripts, and a **deterministic analyzer**
recomputes the headlines over the frozen runs. This fills the outbox `evidence: prototype`. The
live layer is **not** bit-reproducible (a network status can flake, a seat's tools are what they
are); the analyzer **is** — reproducibility is defined as agreement-rate bounds over N runs plus
byte-identical analyzer output, not seed-identity of the live layer (the `intake-001` precedent).

## What it MODELS / MEASURES

A **two-plane, read-only capability battery** run from **>=2 seats**, 5 runs in the worker seat,
**394 self-checks** in the analyzer. Named pieces (see `probe.py` / `probe_protocol.md`):

- **Subprocess plane** (`sp:*`, seat-invariant, read-only *probed*) — `tool-git`,
  `net-raw-cross-repo`, `net-api-repo-object`, `net-api-branch-protection`, `net-proxy-status`,
  `env-token-names` (recorded as **NAMES + count only, never values**), plus `push-main` carried
  as a ledger wall (a real push is a side-effect, so it is `not-probeable`, not tested).
- **Agent plane** (`ap:*`, seat-variant, *ledger*) — `subagent-spawn`, `bash-shell`, `file-io`,
  `grep-glob`, `github-mcp`, `webagent-reply`, `send_later-selfbind`,
  `create_trigger-crosssession`, `workflow`. A subprocess **cannot** see the agent's tool list,
  so `probe.py` emits these as `not-probeable`; each seat enumerates its OWN tools into
  `runs/agent_inventory_<seat>.json`.
- **Seats** — **coordinator** (orchestrating session: subagent-spawn + webagent-reply, no
  Bash/file/grep) and **worker** (spawned Bash seat: Bash/file/grep, no subagent-spawn/reply) —
  the OA-003 `create_trigger`/`send_later` split made concrete.
- **Baseline** — `runs/baseline.json`, hand-assembled from `PLATFORM-LIMITS.md`, `CONVENTIONS.md`,
  `control/status.md` (OA-001/002/003), and the planted `docs/CAPABILITIES.md` seed; every item
  cites its source file + line/section.

The analyzer computes **(1)** internal agreement per subprocess item across the 5 runs, **(2)**
seat divergence per agent item, and **(3)** the three-way diff (coordinator vs worker vs
baseline; subprocess-modal vs baseline) with false-wall / false-capability counts, then emits the
proposed `CAPABILITIES.v1` schema instance.

## What it SETTLED (the load-bearing claims)

**(1) The two documented seats have near-disjoint agent-plane toolsets — measured divergence =
5 of 9 items.** Coordinator-vs-worker disagree on exactly the five *seat-defining* tools:
`subagent-spawn` (coordinator present / worker absent), `webagent-reply` (present / absent),
`bash-shell` (absent / present), `file-io` (absent / present), `grep-glob` (absent / present).
The four *platform* tools agree present in both: `github-mcp`, `send_later-selfbind`,
`create_trigger-crosssession`, `workflow`. So a single seat regenerating a **whole-repo**
`CAPABILITIES.md` writes its own five absences as repo-wide walls.

**(2) Every seat-divergent tool is a FALSE WALL from the other seat's single-seat view — 5 false
walls.** Diffed against the ledger baseline (which records the fleet-true capability), the
worker's `absent` on `subagent-spawn` and `webagent-reply`, and the coordinator's `absent` on
`bash-shell`/`file-io`/`grep-glob`, are each a capability the *fleet* has — just not in that
seat. `analyze.py` asserts each divergent item is a false wall in **exactly one** seat. This is
the laundering the proposal named: file-granularity, single-seat regeneration cannot be honest.

**(3) The subprocess plane is seat-invariant, read-only-probeable, and reproduces the ledgered
walls EXACTLY — 0 false walls, agreement 1.00.** All six probed items were **unanimous across
all 5 runs** (rate 1.00 each; overall flakiness NONE). `net-api-repo-object` and
`net-api-branch-protection` both returned **403 verbatim** ("GitHub access is not enabled for
this session...") — matching the baseline's `docs/CAPABILITIES.md` L53 ("api.github.com direct
HTTP: blocked -> GitHub access is MCP-tools-only") and OA-001 (REST branch-protection reads 403).
`tool-git`, `net-raw-cross-repo`, `net-proxy-status`, `env-token-names` all `present`. **Zero**
subprocess false-walls: the read-only probe is a faithful, low-variance witness of that plane.

**(4) A naive present/absent projection launders 1 FALSE CAPABILITY.** `create_trigger`
is tool-*visible* in both seats, so a naive schema records it `present` — but OA-003 records its
**cross-session bind as org-walled**. The honest schema keeps the wall note in `detail`
(`present-but-walled`); the naive collapse to `present` is a false capability in both seats. This
is the mirror of the false-wall failure: file-granularity probing also over-claims.

**(5) The seat-variant BEHAVIORAL walls are NOT read-only probeable — they must be inherited from
the ledger.** `push-main` and `create_trigger`-cross-session-bind cannot be tested without
committing the side-effect they gate; the probe carries them as `not-probeable / source=ledger`
(CONVENTIONS forward-only + OA-001; OA-003). An honest probe **must** mark these ledger-sourced,
never silently "absent/present."

## What it did NOT settle (negatives as headlines)

- **Generality beyond THIS container/session is JUDGMENT-ONLY.** The measurement is exact for
  *these two seats in this one environment on 2026-07-10*. Whether a third seat type, a different
  container, or a later tool-grant would diverge the same way is not measured — it is a judgment
  that the *structure* (seat-variance in the agent plane, seat-invariance in the subprocess
  plane) generalizes, not a measured fact.
- **The fleet-manager baseline-B is reachable here — but that is a per-seat finding, not a
  guarantee.** `menno420/fleet-manager` `docs/capabilities.md` returned **HTTP 200, 14882 bytes**
  from this worker seat (a nonexistent path on the same repo returns a 14-byte "404: Not Found";
  `master`==`main`). So the roll-up baseline the proposal worried might be unreadable **is**
  readable from this seat this cycle — but a different seat (e.g. one without raw egress) could
  wall it, which is itself the point: reachability of the diff baseline is *also* seat-variant.
- **Only 2 seat types, 1 environment, 1 cycle.** Five runs bound the subprocess-plane flakiness
  at 0/5 *this cycle*; a longer campaign could surface a network flake the 5 runs missed. The
  agent-plane inventories are single-snapshot self-enumerations (N=1 per seat), exact for the
  snapshot, not swept.

---

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the
conclusion;"**
High for what it directly probes; honestly bounded elsewhere. The subprocess plane **is** live —
`probe.py` hits the real git/network/env of THIS container read-only, so there is no
"abstraction" between model and live for those six items (this is why they reproduce the ledger
walls to the verbatim 403 body). The agent-plane inventory is **exact for these two seats** — it
is each seat enumerating its own actual tools, not a model of them. What the sim abstracts away is
**generality**: two seats, one environment, one cycle. No gap can flip the load-bearing structural
claim (agent plane is seat-variant -> single-seat whole-repo regen launders; subprocess plane is
seat-invariant -> probeable) because that claim is *demonstrated by the measured divergence
itself*, not inferred. The gap bears only on *how far it generalizes*, which is labeled
JUDGMENT-ONLY above.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical
stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. *Bugs:* **394 self-checks** in `analyze.py` tie every headline to the frozen data —
schema completeness (25 records, every `result` in {present,absent,wall,not-probeable}, every
`source` in {probed,ledger}), count consistency (divergence == |divergent list|, false-walls ==
|items|, false-caps == |item-set|), the structural asserts (each divergent item is a false wall
in exactly one seat; `create_trigger` is *the* false capability; subprocess false-walls == 0),
and an explicit **no-secret-value guard** (the env-token detail must state "values withheld" and
every recorded name must be a bare identifier with no `=`). *Seeded luck:* there is no seed to
rig — the honesty control is **agreement across 5 live runs** (all six subprocess items unanimous,
rate 1.00) plus **byte-identical analyzer output** (same md5 on re-run). *Cherry-picking:* the
analyzer prints the **full** per-item agreement table, the **complete** seat-divergence list AND
the agreeing items, and **every** false-wall (seat,id) pair — the ruling is argued from the whole
diff, not a selected item.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
Yes for the structural claim. Across all 5 runs the subprocess plane never wavered (0/5
disagreement on every item) and the two 403 walls were identical each time; the seat-divergence
and false-wall/false-capability counts are properties of the two inventories + baseline, invariant
to run count. The honest edge is **network flake**: a single transient 502 on a `net-*` item would
drop that item's agreement below 1.00 — the analyzer is built to *surface* exactly that
(`agreement_rate`, `subprocess_flaky_items`) rather than hide it; none occurred this cycle.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong for the analyzer; honest for the live layer. Reproducibility is **two-part**: (a) the live
layer reproduces as **agreement-rate bounds** — re-running `probe.py` yields a similar
distribution, measured at **rate 1.00 on all six subprocess items over 5 runs** this cycle; (b)
the deterministic layer is **byte-identical** — one documented command
(`python3 sims/verdict-005-capability-self-probe/analyze.py`), stdlib-only, no wall-clock inside
the output (it copies the frozen run stamps), verified **same md5 on consecutive runs**, exit 0
only when all 394 self-checks pass. Committed and public.

**5. "LIMITS? what this evidence does NOT show."**
It does not show that a third seat type or a different environment would diverge the same way
(generality = JUDGMENT-ONLY), does not sweep the agent inventories (single snapshot per seat),
does not bound network flakiness beyond 5 runs, and cannot probe the behavioral walls
(`push-main`, cross-session trigger bind) without committing their side-effects — those are
inherited from the ledger and labeled `not-probeable`. It answers "do two documented seats
diverge enough that single-seat whole-repo regeneration is dishonest, and which plane is
faithfully probeable" — **not** "what is the complete capability set of every possible seat."

---

## EVIDENCE STRENGTH: **moderate-strong** · gate **PASS**

Two-tier, like the measured half of the precedent. The **load-bearing claims are strong**: the
seat-divergence (5/9), the false-wall count (5, one per divergent item), the false-capability
(1, `create_trigger`), and the subprocess plane's exact reproduction of the ledger walls (0
false-walls, agreement 1.00) are all *measured* from the live environment and *self-checked* to
consistency (394 asserts), deterministic and reproducible. The **generality** claim (that this
structure holds beyond two seats / one container) is explicitly **JUDGMENT-ONLY** and carried as
such, not as evidence.

Under the README rule — "A result that fails the gate is a hypothesis, not evidence" — the probe
**PASSES** the gate for the claims it covers (no gate question fails): the divergence and the
diff are settled by direct measurement. The generality is labeled a judgment, not a failed claim.
Evidence strength: **moderate-strong** (measured core strong; generality is judgment).

---

## VERDICT & recommendation (for the fleet manager to route)

**Verdict: `[COORDINATOR TO FINALIZE]`.** The measured core points to one ruling — **"probe must
annotate per-seat-type sections (schema named); regenerate-whole-file from one seat is NOT
honest"** — because the two documented seats' seat-defining tools are disjoint (divergence 5) and
each is a false wall from the other's single-seat view (5), while a naive present/absent
projection also over-claims one walled capability (1). The subprocess plane *is* honestly
whole-repo-probeable (seat-invariant, 0 false-walls), so the honest artifact is **subprocess plane
= one shared section; agent plane = one section PER seat type, with ledger-sourced behavioral
walls marked `not-probeable`.** The coordinator finalizes the exact ruling wording + status.

**Recommended output schema — `CAPABILITIES.v1`** (what a substrate-kit `capabilities --probe`
ORDER should implement; emitted this cycle as `CAPABILITIES.json`):

```
record:
  id            : "sp:*" | "ap:*"
  plane         : "subprocess" | "agent"
  seat          : "seat-invariant" | "coordinator" | "worker" | <seat-type>
  seat_variant  : bool
  result        : "present" | "absent" | "wall" | "not-probeable"
  detail        : verbatim status / error / ledger note (env: NAMES + count, NEVER values)
  source        : "probed" | "ledger"
  agreement     : { runs: int, rate: float|null }          # over N frozen live runs
  baseline_diff : { baseline_expected, false_wall: bool, false_capability: bool }
rollup:
  subprocess_agreement, seat_divergence{count,items},
  baseline_diff{false_walls, false_capabilities, ...}, baseline_b_reachable
```

**Guardrails the ORDER must carry:**
- **Agent-plane sections are per-seat-type; never collapse them into one whole-repo verdict.**
- **`env-token-names` records NAMES + count only — never a value** (self-checked here).
- **Behavioral walls (`push-main`, cross-session trigger bind) are `source=ledger /
  not-probeable`** — a probe must not silently claim/deny them.
- **Emit `agreement.rate` per probed item** so a network flake is visible, not averaged away.
- **Diff against the fleet baseline, but record baseline-B reachability per seat** (it is itself
  seat-variant — reachable from this worker seat this cycle: HTTP 200).

**Codex review:** _placeholder — the coordinator will post the `@codex` review comment (one
specific question, on the final PR head); reply disposition to be recorded in the outbox verdict._

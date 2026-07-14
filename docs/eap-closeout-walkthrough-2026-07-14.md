# sim-lab — EAP close-out walkthrough (2026-07-14)

> **Status:** `owner-guidance`
>
> The sim-lab half of the Ideas Lab seat's EAP close-out, ordered as inbox
> **ORDER 008 item (b)** (`control/inbox.md`). Written for the owner: what
> this repo did, how to verify it yourself, and exactly which clicks and
> decisions remain. Companion seat-level walkthrough (covers BOTH repos):
> idea-engine [`docs/eap-closeout-walkthrough-2026-07-14.md`](https://github.com/menno420/idea-engine/blob/main/docs/eap-closeout-walkthrough-2026-07-14.md)
> (lands in parallel, same day). Depth behind every number here: the seat
> audit [idea-engine `docs/audits/eap-project-audit-2026-07-14.md` @ 8162d1e](https://github.com/menno420/idea-engine/blob/8162d1e/docs/audits/eap-project-audit-2026-07-14.md)
> — measured, never estimated. Facts below re-verified at HEAD `9aaf72b`, 2026-07-14T12:39Z.

## A. What this seat did

sim-lab is the fleet's **evidence seat**: idea-engine proposes, sim-lab
reproduces evidence and finalizes a verdict, the fleet-manager routes it
(Q-0264 — this repo never dispatches to lanes). In ~3.6 days
(2026-07-10 → 2026-07-14):

- **76 verdicts finalized, V001–V076** — every idea-engine PROPOSAL
  P001–P063 verdicted (63; offset map in
  [`docs/current-state.md`](current-state.md) § Verdict-numbering map),
  plus 11 fleet SIM-REQUESTs (`simreq-001…011`) and 2 owner-direct audits
  (V009, V011). Ruling split through V072 (audit §1): 23 approve · 20
  reject · 12 null · 7 needs-more-evidence · 6 conditional · 4 other.
  Honest negatives and nulls are headlines here, not footnotes.
- **141 PRs, 0 abandoned, 0 open** — every PR self-landed via the
  merge-on-green enabler (PR #50); zero owner merge clicks needed after it.
- **Final-day close (2026-07-14):** heartbeat + ledger refresh through V073
  (#137 → `fa1ae2d`) · ORDER 008 landing (#138 → `d4ff3c8`) · **VERDICT 075**
  (NULL — fishing full-roster band-straddle; theorems F-STRICT + F-PINCER;
  three-way reframing fork named; 33-row candidate table published
  NOT-PINNED) + **VERDICT 076** (APPROVE-WITH-CONSTANTS — cooked-fish price
  P\*=12, per-species cooked-energy minnow 1 / bass 1 / pike 2 /
  legend_carp 7; bonus finding F-FLAT30: the committed flat
  `"cooked fish": 30` is perpetual motion at every measured cell) via
  #139 → `d0a5a75` · **VERDICT 074** on idea-engine PROPOSAL 063
  (REJECT-REORDER, certified: width-2 mint partition exactly {0, 1/2};
  the shipped ordering's inversion confirmed 8/8 pre-registered predictions,
  E[mints, T=20] −35.1%) via #140 → `9aaf72b`.
- **Second product:** sim harness v0.1 (`harness/simharness.py` + template
  + selftest), consumed by other Projects via raw/copy; the release tag is
  the one un-shipped bit (OA-004 below).

## B. Current state + how to run/verify

State at this doc's landing: substrate gate green · verdict ledger complete
through V076 · proposal pipeline **dry** (P063 verdicted same day) · fleet
seed high-water **20261562** · 0 open PRs.

Verify the repo gate (must exit 0):

```
python3 bootstrap.py check --strict
```

Re-run a verdict sim and compare against its pinned result (V074 example;
every `sims/verdict-*/README.md` documents its own one command):

```
python3 sims/verdict-074-menu-width-leverage/menu_width_leverage_sim.py
sha256sum sims/verdict-074-menu-width-leverage/results.json   # vs the hash pinned in its REPORT.md
```

~75 s, stdlib-only, CPython 3.11 asserted, byte-identical across runs.
Note: this runner exits 1 **by design on the accepted run** — the 59
recorded self-check failures are disclosed ANOMALY A1 (a tolerance-clause
artifact on near-one ONCE cells, REPORT.md § Anomalies), not a twin
disagreement; the decision path is exact-arithmetic only.

Where the ledger lives: `control/outbox.md` is canonical (V072–V076 live;
V001–V071 rolled byte-faithful to `control/outbox-archive-2026-07.md` with
one-line pointer stubs, per ORDER 006). Count parity:
`grep -hc '^## VERDICT ' control/outbox.md control/outbox-archive-2026-07.md`
→ 76 headers in the live file (71 of them ROLLED stubs) and 71 full blocks
in the archive.

## C. OWNER ACTIONS checklist

Verified live this session (GitHub API, 2026-07-14T12:41Z): **0 open PRs —
zero pending merge clicks.** OA-005 is RESOLVED (triggers deleted before
archive). `ROUTINE_PAT` unset is a manager note only — the `GITHUB_TOKEN`
fallback works. What genuinely remains — three clicks and one decision:

- [ ] **OA-002 — Codex usage quota** (INC-04; split verdict: integration
  enabled = RESOLVED, quota = OPEN). Deep link: <https://chatgpt.com/codex>
  → settings/usage; the symptom:
  <https://github.com/menno420/sim-lab/pull/38#issuecomment-4948283951>.
  **Recommendation: reset/raise the quota only if you want @codex review
  fold-ins back — the step is SUSPENDED behind the V016 authenticity gate
  regardless (3 fabricated-evidence incidents), so this click alone does
  not resume it.** VERIFY: after clicking, an @codex mention on a fresh
  sim-lab PR draws a substantive reply, not "reached usage limits".
- [ ] **OA-003 — review-site deploy** (VERDICT 011). Deep link:
  <https://github.com/menno420/sim-lab/tree/main/sims/owner-002-websites-purpose-nav>
  (the evidence: built locally, no deployed URL).
  **Recommendation: route it through the websites lane's standard deploy
  flow rather than a one-off manual upload.** VERIFY: after deploying, the
  review site's public URL returns HTTP 200 and shows the reviewer-facing
  content VERDICT 011 describes.
- [ ] **OA-004 — harness tag-push 403** (non-blocking; raw/copy consumption
  works today). Deep link: <https://github.com/menno420/sim-lab/tags>
  (currently empty). **Recommendation: push the tag yourself from any fresh
  clone — `git tag harness-v0.1.0 && git push origin refs/tags/harness-v0.1.0`
  — rather than widening agent push rights.** VERIFY: after pushing, the
  tags page lists `harness-v0.1.0`.
- [ ] **DECISION — VERDICT 075's three-way reframing fork** (fishing
  full-roster; routed to you via the fleet-manager, so this may arrive as a
  manager ask). Deep link:
  <https://github.com/menno420/sim-lab/tree/main/sims/verdict-075-fishing-full-roster-economy>.
  The request's premises cannot all hold at once; pick ONE re-registration:
  (1) re-center the parity band · (2) contribution cap above a rank
  threshold · (3) land the roster in waves of ~12–16 species.
  **Recommendation: option (1), the cheapest — re-center the parity band to
  admit fresh@dock ≈ 4.75–4.95; k=1.1, δ=0.6 is the measured stable
  interior.** VERIFY: a re-registered SIM-REQUEST naming the picked option
  reaches the sim-lab intake (it becomes the next verdict's subject).

Honest nulls: no other pending clicks, settings, or decisions were found at
HEAD — no PR awaits a merge, no verdict awaits finalization, no order is
un-acked (ORDER 008's done-flip rides the next heartbeat, a coordinator
step, not an owner one).

## D. 5-minute verify-it-yourself tour

1. **(90 s)** Open
   [`sims/verdict-074-menu-width-leverage/REPORT.md`](../sims/verdict-074-menu-width-leverage/REPORT.md)
   — read the verdict line, the {0, 1/2} partition theorem, and the five
   validity-gate answers at the end. This is the house style: pre-registered
   decision rule first, result second.
2. **(60 s)** Open
   [`sims/verdict-076-fishing-cook-economy/REPORT.md`](../sims/verdict-076-fishing-cook-economy/REPORT.md)
   — the wire-verbatim constants (P\*=12, per-species energy) and the
   F-FLAT30 perpetual-motion finding that must supersede the committed flat
   30.
3. **(60 s)** Open [`control/outbox.md`](../control/outbox.md) and scroll to
   the tail — INTAKE 063 + VERDICT 074, then the CLOSE-OUT REPORT block this
   doc landed with. This file is the canonical ledger the manager consumes.
4. **(90 s)** Double-run hash check — run the § B command twice and diff:
   byte-identical stdout and `results.json` both times (the pinned sha256 in
   REPORT.md is the committed accepted run).
5. **(30 s)** `python3 bootstrap.py check --strict` → exit 0: the same gate
   CI enforces on every PR.

## E. Handoff notes

- **Baton — V074 (REJECT-REORDER) routes to superbot-games via the
  fleet-manager** (Q-0264 fan-in; this repo never seat-directs). The named
  escalation: width must stop selecting by prefix — per-option `min_width`
  or width-indexed option sets; NZM/ZNM priced as the interim zero-floor
  menu.
- **Baton — V075's reframing fork awaits the manager/owner pick** (§ C);
  nothing from V075 is wire-able until then (the 33-row table is published
  NOT-PINNED).
- **Baton — V076's F-FLAT30 supersede is a build precondition:** the flat
  `"cooked fish": 30` must be superseded before any haul-cook op wires.
- **Seed discipline:** the fleet seed high-water is **20261562** (V074);
  the next sim registers strictly above it.
- **Ledger/pipeline:** verdicts complete through V076; the proposal pipeline
  is dry; the P→V offset map (`docs/current-state.md`) is current through
  P063→V074 (+11).
- **Next heartbeat stamp** (coordinator-only; deliberately NOT written this
  session): it should flip ORDER 008 to done, carry the ledger through V076
  with the V074/075/076 SHAs, restate 0 open PRs and the unchanged OA
  ledger, and point at this walkthrough.

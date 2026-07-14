# Session — EAP close-out walkthrough: docs/eap-closeout-walkthrough-2026-07-14.md on main + the CLOSE-OUT REPORT block in control/outbox.md (inbox ORDER 008 item (b), the sim-lab half)

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-14 · eap-closeout-walkthrough worker session

Objective: land the sim-lab EAP close-out walkthrough
(`docs/eap-closeout-walkthrough-2026-07-14.md`, sections A–E per ORDER 008
item (b)) with its Status badge in the first 12 lines and a real markdown
link from the docs router (`docs/AGENT_ORIENTATION.md`, mirroring how the
2026-07-13 fleet-cleanup audit is indexed), PLUS the CLOSE-OUT REPORT 001
block appended to `control/outbox.md` (target: fleet-manager, NIGHT-REPORT
grammar, 11 lines ≤ 40) carrying the OWNER ACTIONS checklist verbatim —
outbox as venue because the heartbeat is coordinator-only and off-limits
this session. Companion seat-level walkthrough (both repos) lands in
parallel at idea-engine `docs/eap-closeout-walkthrough-2026-07-14.md`.
This card held the substrate gate red until this flip — the designed hold
was the only red this branch produced itself.

## What happened

HARD-SYNC to origin/main @ 9aaf72b, then every restated fact re-verified at
HEAD before writing (Q-0120): 76 distinct verdicts V001–V076 counted from
the `## VERDICT` headers (71 full blocks archived + 71 ROLLED stubs + 5
live in `control/outbox.md`); final-day SHAs #137→fa1ae2d · #138→d4ff3c8 ·
#139→d0a5a75 · #140→9aaf72b read from `git log`; 0 open PRs read live from
the GitHub API; OA-002/003/004 open + OA-005 resolved read from the
`control/status.md` ⚑ block; seed high-water 20261562 from the V074 card
and ledger; the seat audit pin verified readable at idea-engine `8162d1e`.
Landed in one PR (#141, branch `claude/eap-closeout-walkthrough`): the
walkthrough doc (badge `owner-guidance`, sections A–E, honest nulls stated
— zero pending merge clicks), the router index row, and the outbox block.
Untouched by design: `control/status.md`, both inboxes, `sims/`, and every
other repo. `python3 bootstrap.py check --strict` exit 0 at this flip.

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-074-menu-width-leverage.md`): its
tolerance-audit idea — walk every registered MC check over the exact arm's
own predictions before the runner runs — is the right pre-run instrument
discipline and belongs in the sim README template's registration checklist;
this close-out session had no runner to apply it to, but its §B/§D text
deliberately teaches the owner that V074's exit-1 is that card's disclosed
A1 artifact rather than a failure, which is exactly the downstream payoff
of that card's honesty.

💡 **Session idea (genuine, this session):** the same four OWNER ACTIONS
were hand-copied onto three surfaces today (the `control/status.md` ⚑
block, walkthrough § C, the outbox CLOSE-OUT block) with only the verbatim
discipline preventing drift — make the ⚑ block the single grammar-checked
source and RENDER the rest: a tiny stdlib `scripts/render_owner_actions.py`
that reads the ⚑ entries and emits the owner-facing checklist grammar
(deep link first, **bolded recommendation**, VERIFY step), so any
walkthrough/report surface is generated + diff-checked and owner-action
drift becomes a checker failure instead of a proofreading task.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).

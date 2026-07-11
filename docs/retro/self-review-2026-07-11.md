# Self-review — 2026-07-11 (ORDER 002, fleet-wide self-review relay)

> **Status:** `reference` — durable home for the ORDER-002 self-review.
> Moved here from control/status.md (which is overwritten each heartbeat).
> Covers the last ~24h of sim-lab evidence work (VERDICTs 006–011 + hardening).

## One-line health
Green. 11 verdicts finalized end-to-end (V001–011), validity-gate PASS on
every one, all verdict PRs merged, queue drained to empty with no dropped intake.

## What went well
- Cheapest-adequate-evidence ladder held: numeric sims where dynamics modeled
  (001, 004, 008, 010), measured prototypes where not (002, 005, 011), and
  explicit JUDGMENT-ONLY where neither applied (003, 007) — the label traveled
  with every verdict.
- Negative results shipped as headlines: 5 needs-more-evidence + 1 redirect
  saved lanes wasted sessions.
- Empty-queue honesty guard worked: instead of inventing intake, the
  queue-empty windows hardened the newest verdict (VERDICT 008 wider-variation
  pass; VERDICT 011 wider-cap re-crawl) and the harness.

## What went wrong / friction
- Codex review step (Q-0264.4) is effectively blocked: OA-002 — the bot replies
  "reached usage limits" on every verdict PR; 6+ @codex questions pending, none
  landed. Verdicts finalized without the fold-in (merge not gated per
  CONVENTIONS) but the disposition stays "pending".
- Auto-merge SQUASH race repeatedly split a verdict's sim PR from its heartbeat
  commit (forced follow-up control fast-lane PRs on #38/#39 and #40/#41). Not
  harmful (forward-only) but noisy.
- Recurring EVIDENCE GAP: no live fishing/mining earn-rate baseline exists in
  source, so reward-VALUE conclusions stayed provisional in VERDICTs 001 and
  008. An idea-engine / telemetry dependency, not fixable in sim-lab.

## Owner-attention (mirrored to ⚑ needs-owner)
OA-002 Codex usage cap · OA-003 review-site deploy · OA-004 harness tag-push
403 · OA-005 standing failsafe trigger still bound to the to-be-archived
coordinator session (disable in Routines or re-arm per PLATFORM-LIMITS.md).

## Validity-gate re-ask (lane rider) — two most recent verdicts
- VERDICT 010 (settle-once guard): COMPARABLE — reconstruction rung 1–2 of a
  known contract; UNCORRUPTED — 72 self-checks, deterministic; ROBUST — catch
  matrix swept; REPRODUCIBLE — one command; LIMITS — models the fence contract,
  not the live editor. Gate PASS.
- VERDICT 011 (four websites): COMPARABLE — MEASURED crawl of 3 live sites +
  local review build; UNCORRUPTED — 243→2829 self-checks, byte-identical
  re-runs; ROBUST — wider-cap re-crawl (400/8) confirmed no verdict-flipping
  route hidden by the 80-cap; REPRODUCIBLE — analyze_nav.py / analyze_wide.py;
  LIMITS — review site has no deployed URL (measured local build only). Gate PASS.

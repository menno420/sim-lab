# INTAKE 001 — Panel-mode vs single-pass probing (VERDICT 002)

Measured-prototype head-to-head: does panel-mode probing (mode 2 — 3 ideation personas + a synthesizer) change the recommendation or materially improve probe-report quality vs the single-pass battery (mode 1), enough to justify its multi-agent cost? Ran both modes on 3 real idea-engine backlog ideas, 3 reps each, + 2 blind judges/idea, instrumenting agents/tokens/wall-time.

**Verdict:** `approve` — selectively. Adopt panel **only for big-or-contested ideas** (README default, now measured); **reject always-on**. Panel flipped the verdict on 2/3 ideas (both BUILD→HOLD, on the contested ideas), not on the well-scoped one, at ~4× agents / 3.05× tokens / 1.61× wall; blind judges preferred it 6/6 (slight, no position bias). Verdict *correctness* is not measured — see `REPORT.md`.

Source idea: `menno420/idea-engine` `ideas/superbot/idea-probe-brainstorm-simulator-2026-07-10.md` @ `3e3e80d73ea4ad2af1a0f8bee49262db1da09302`.

## One run command
```
python3 sims/intake-001-probe-panel-vs-single-pass/analyze.py
```
Deterministic, stdlib-only, exit 0 iff all self-checks pass. It recomputes every headline number from the frozen runs in `runs/cells.json`. The live probe layer (LLM agents) is not bit-reproducible; re-measuring via `probe_protocol.md` yields a similar distribution, not identical numbers.

## Files
- `REPORT.md` — the live verdict (8-section, all five validity-gate answers).
- `analyze.py` — deterministic analysis + self-checks over the frozen runs.
- `probe_protocol.md` — exact prompts + matrix, so the head-to-head can be re-measured.
- `runs/cells.json` — the 18 frozen probe cells + 6 judge records (source of truth for `analyze.py`).
- `runs/raw/<slug>/` — full per-agent transcripts + instrumentation (audit trail).

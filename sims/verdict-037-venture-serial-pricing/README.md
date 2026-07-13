# verdict-037 · venture-serial-pricing

Serves **idea-engine ORDER 005 SIM-REQUEST 1** (control/inbox.md @ 8218d66;
requesting seat **venture-lab**): a pricing verdict on the Ultramarine
3-episode serial — per-episode ~$2.99 vs bundle (the vetted $4.99 single
volume) vs a free-first-episode funnel. Packet read READ-ONLY at
menno420/venture-lab @ `58cdb145dd524e8289a72a0bfd3d63a66ad0101b`
(`control/outbox.md` "night batch 1" +
`candidates/adult-novels/ultramarine/versions/serial-edition/NOTES.md` +
`docs/publishing/vetting/ultramarine.md` + `docs/publishing/CHECKLIST.md` §4).

Fully hermetic: every constant is quoted verbatim with its source path@SHA in
the committed `fixtures.json` (the pre-registration — decision bands and the
decision rule landed BEFORE the runner existed; git trail: fixtures commit
precedes the runner commit). The sim reads exactly ONE file (its own
fixtures.json) and touches no repo state, network, or wall clock.

Model (exact, per committed browsing reader — the packet's own frame):

- **SERIAL** — buy ep1 at $2.99 (net r = 0.70·$2.99 = $2.093 exact), continue
  to ep2 w.p. p2, ep3 w.p. p3: E[net] = r·(1 + p2 + p2·p3).
- **SINGLE** (the "bundle" arm) — one $4.99 listing: E[net] = s = $3.493
  exact. Zero unmeasured parameters.
- **FREE_FUNNEL** — ep1 free (the $0.00 mechanism itself UNPINNED in the
  packet, gap G3), paid ep2/ep3 at conversion q2/q3, acquisition multiplier
  m: E[net] = m·r·(q2 + q2·q3).

Breakeven (the packet's own asked-for quantity): SERIAL ≥ SINGLE iff
**p2·(1+p3) ≥ 200/299 ≈ 0.6689** — p2 ≥ 33.4% if p3 = 1, ~45.9% symmetric,
66.9% if ep3 never sells. FREE_FUNNEL ≥ SINGLE iff m·q2·(1+q3) ≥ 499/299 ≈
1.6689 (at m = 1: q2 ≥ 83.4% even with perfect ep3 carry). At equal rates
and m = 1, SERIAL − FREE_FUNNEL = r exactly (free wins only via m).

**Ruling: R3-CONDITIONAL-DEFAULT** per the pre-registered rule — no measured
carry-through/conversion/multiplier datum exists anywhere in the packet (the
packet says so verbatim), so the default publish arm is the only arm with
zero unmeasured parameters: **the single volume at the vetted $4.99**.
Serial parks behind the named measurement; free-first-episode is not
recommendable (unmeasured behavior bar AND unpinned platform mechanism).

## Run (one command)

```
python3 sims/verdict-037-venture-serial-pricing/serial_pricing_sim.py
```

Exit 0 iff all self-checks pass (934 passed, 0 failed). Deterministic —
**ZERO RNG** (every arm is closed-form Fraction arithmetic; the seed
high-water mark 20260775 is untouched, no seed drawn); stdout + results.json
byte-identical across runs by external diff.

Files: `fixtures.json` (pre-registration) · `serial_pricing_sim.py` (runner)
· `results.json` (committed output) · `REPORT.md` (verdict evidence — the
8-question battery + validity gate).

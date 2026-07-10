# Probe protocol — INTAKE 001 head-to-head (re-measurement spec)

This is the exact protocol that produced `runs/`. The live layer is LLM agents, so re-running yields a **similar distribution, not identical numbers**; `analyze.py` is what reproduces exactly, over the frozen `runs/cells.json`.

## Modes
- **Mode 1 (single-pass):** 1 agent, 1 pass over the battery → JSON verdict.
- **Mode 2 (panel):** 3 personas (skeptic, builder, user_value) run in parallel + 1 synthesizer → JSON verdict. **N=3 and the roster are a documented choice** — the source docs say "N personas + synthesizer" without pinning N.

## Shared output schema (every probe agent returns ONLY this)
`{"recommendation":"BUILD|HOLD|KILL","confidence":0.0-1.0,"top_risk":"...","cheapest_evidence":"...","report":"markdown"}`

## Battery (embedded in every probe prompt)
> Probe the idea using this battery: (1) What is this really / the core claim? (2) Strongest failure mode? (3) What would falsify it / the cheapest adequate evidence to build confidence? (4) Cost/complexity vs payoff? (5) Smallest shippable slice? Ground every statement in the idea as given; where something is unknown or unmeasured, write "not measured" — do NOT invent specifics; a filled-in picture of invented detail is worse than a blank.

## Prompts
- **mode1:** "You are an idea-probe agent. In ONE pass, probe this idea with the battery, then return ONLY the JSON schema. IDEA: <desc>. BATTERY: <battery>."
- **skeptic:** "Red-team lens: attack this idea; find why it fails or should not be built. Probe with the battery. Return ONLY the JSON."
- **builder:** "Pragmatist/build lens: is it feasible cheaply? true MVP and real complexity/cost? Probe with the battery. Return ONLY the JSON."
- **user_value:** "User/value lens: who wants this, does it move a real metric, opportunity cost vs alternatives? Probe with the battery. Return ONLY the JSON."
- **synthesizer:** "You are the panel synthesizer. Three independent persona probes of the SAME idea follow as JSON. Reconcile disagreements, weigh them, emit ONE final probe report in the SAME JSON schema."
- **judge:** "Blind quality judge. Two probe reports A and B (sources hidden). Score EACH on 5 criteria 1-5: risk_surfacing, specificity (grounded vs generic), actionability, calibration (not overconfident), coverage. Penalise fabricated specifics hard under specificity. Return ONLY JSON {A:{...}, B:{...}, winner, margin, why}."

## Matrix
3 ideas × (mode1 ×3 reps + mode2 ×3 reps) + 2 blind judges/idea (A/B order swapped: judge_1 A=mode1/B=mode2, judge_2 A=mode2/B=mode1), comparing each mode's rep-1 report.

## Instrumentation
Per agent: `subagent_tokens` (tokens) + `duration_ms` (wall_ms) from its `<usage>` block. Panel cell_tokens = Σ(3 personas + synth); panel cell_wall_parallel_ms = max(3 persona wall_ms) + synth wall_ms (models parallel persona execution). Absolute values are Opus-4.8/this-environment specific; the mode2/mode1 ratios are the transferable measurement.

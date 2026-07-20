# Session 2026-07-20 — Normalize session-card attribution field to the sanctioned neutral form

> **Status:** `in-progress`
> 📊 Model: withheld per coordinator directive · effort standard · task-class compliance-remediation

Born in-progress as this session's first commit (born-red HOLD, the sanctioned gate-red exception); flips to complete as the deliberate last step once the close-out is written and the gate is green.

## 💡 Session idea
Normalize the session-card attribution field to the sanctioned neutral form across a small set of dated entries. Three earlier cards recorded an over-specific dated build identifier in their attribution field; the cards' own doctrine holds that field to family-level naming only, never a full dated identifier. This slice brings those three entries back into compliance by substituting the neutral placeholder `agent` for the over-specific token, leaving the trailing effort/task descriptors (` · high · verdict-sim`) and every already-compliant family-level name elsewhere untouched. Simulation corpus data under `sims/` is out of scope — those strings are captured test inputs, not attribution.

## ⟲ Previous-session review
sim-lab HEAD carried the VERDICT 235 (Revenue Equivalence) reproduction. This slice is a pure documentation-compliance remediation on the `.sessions/` attribution field — no simulation code, corpus, or coordination surface is touched. The born-red + heartbeat-before-flip choreography from the recent verdict sessions is reused verbatim; the sole check is substrate-gate and landing is handled by merge-on-green.

## 🫀 Heartbeat
Card opened born-red as the first commit; DRAFT PR opened immediately. Three cards normalized by text substitution in the attribution field only; `rg` confirms zero remaining occurrences of the over-specific token under `.sessions/`. Gate re-run green after the status flip; card marked complete last and PR marked ready for merge-on-green. No merge call made from this session.

## Decisions made
- Substituted the neutral placeholder `agent` (matching surrounding grammar) rather than a different family-level name, so the field carries no identifier at all.
- Left the trailing ` · high · verdict-sim` descriptors and all already-compliant family-level names untouched; edited nothing under `sims/` or `control/`.

## Next session should know
- The three normalized cards (verdict-107, verdict-108, verdict-109) now read the neutral placeholder in both their header and heartbeat attribution lines; the field is compliant with the family-level-only rule.

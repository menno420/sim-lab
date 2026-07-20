# Session — VERDICT 240 (reproduce PROPOSAL 227, Hex never-a-draw)

> **Status:** `in-progress`
> Born-red HOLD: lands `in-progress` on the first commit to hold the PR red through substrate-gate, flips to `complete` as the last commit once the verifier, probe report, and captured stdout are in place and verified. Merge-on-green lands it (ORDER 003, zero agent merge calls).

## 💡 Session idea

Reproduce PROPOSAL 227 (round-54 GAME slot) as VERDICT 240 (+13 offset): the Hex no-draw theorem and its exact corollary P(first player connects)=1/2 under a uniform random fill, with #{Red}=#{Blue}=2^(n²−1). Firsthand stdlib-only verifier under `sims/verdict-240-hex-never-a-draw/`.

## ⟲ Previous-session review

VERDICT 239 (Myerson optimal reserve, PROPOSAL 226) verifier landed (#320). The verdict ledger is contiguous through V238 in the idea-engine outbox mirror; V239/V240 verdict blocks mirror on the idea-engine side.

## 🫀 Heartbeat

`hex-never-a-draw.py` verified green: exit 0, four gates PASS each in its own direction, digest `76d9a3267140171bec9ad335b370c6028e1359d23f39c7c87f3d7125598ebed8` byte-identical across in-process double-run and separate re-invocation (~40 s, SEED=20260717). G1 exhaustive-exact n∈{2,3,4}; G2 MC n=11 z=−0.826; G3 12-cell never-draw invariant + symmetry; G4 square-lattice falsifiability z=−364.97. run-stdout.txt captures the full results dict + digest.

> 📊 Model: Claude Opus · high · verdict-reproduction / GAME slot

## Decisions made

- APPROVE: exact core (exhaustive G1), byte-identical reproduction, falsifiability gate survives at 365σ.
- Verifier is the firsthand artefact; the idea-engine doc references it by path.

## Next session should know

- Round-54 rotation continues: UNRELATED slot next (P228 → V241).
- VERDICT 240 verdict block to be mirrored into idea-engine control/outbox.md alongside the pending V239 mirror.

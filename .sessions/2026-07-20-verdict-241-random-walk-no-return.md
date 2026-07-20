# Session — VERDICT 241 (reproduce PROPOSAL 228, random-walk no-return identity)

> **Status:** `in-progress`
> Born-red HOLD: lands `in-progress` on the first commit to hold the PR red through substrate-gate, flips to `complete` as the last commit once the verifier, probe report, and captured stdout are in place and verified. Merge-on-green lands it (ORDER 003, zero agent merge calls).

## 💡 Session idea

Reproduce PROPOSAL 228 (round-54 UNRELATED slot) as VERDICT 241 (+13 offset): Feller's no-return identity for the simple symmetric random walk on Z — P(S₁≠0,…,S_{2n}≠0) = P(S_{2n}=0) = u_{2n} = C(2n,n)/4ⁿ, so over all 2^(2n) sign sequences #{never revisit 0}=#{at 0 at time 2n}=C(2n,n) EXACTLY. Firsthand stdlib-only verifier under `sims/verdict-241-random-walk-no-return/`.

## ⟲ Previous-session review

VERDICT 240 (Hex never-a-draw, PROPOSAL 227) verifier landed (#324). Round-54 rotation continues: this is the UNRELATED slot (P228 → V241), following the GAME slot V240.

## 🫀 Heartbeat

`random-walk-no-return.py` verified green: exit 0, four gates PASS each in its own direction, digest `75f5b3c166916598983389896cc762c906b1ef346c70f8b5c639b3a60e140f46` byte-identical across in-process double-run and separate re-invocation (~1.7 s, SEED=20260717). G1 exhaustive-exact n∈{1..6} (counts {2,6,20,70,252,924}=C(2n,n), A==B exact); G2 MC n=12 (24 steps) p̂_return z=+0.954 / p̂_noreturn z=−2.658 vs shared u_24; G3 4-size invariance {5,8,12,20} + left/right symmetry; G4 naive-2⁻ⁿ falsifiability rejected at z=+4544.27. run-stdout.txt captures the full results dict + digest.

> 📊 Model: Claude Opus · high · verifier-authoring / UNRELATED slot

## Decisions made

- APPROVE: exact core (exhaustive G1 over n∈{1..6}, both counts = C(2n,n)), byte-identical reproduction, falsifiability gate rejects the naive 2⁻ⁿ independence model at ~4544σ.
- Verifier is the firsthand artefact; the idea-engine doc references it by path.

## Next session should know

- Round-54 rotation continues after the UNRELATED slot closer.
- VERDICT 241 verdict block to be mirrored into idea-engine control/outbox.md alongside any pending mirror.

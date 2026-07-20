# PROPOSAL 219 — Nim / Sprague–Grundy: a position is a second-player (P) loss iff the nim-sum (XOR of heap sizes) is zero, and the single-pile Subtraction game Sub({1..k}) has Grundy value G(n)=n mod (k+1) — stage the SEED=20260717 stdlib verifier so VERDICT 232 can reproduce it

> **Status:** `in-progress`

📊 Model: Claude Opus · high · verification/staging

started: 2026-07-20T00:00:00Z

💓 Heartbeat: round-52 GAME slot (fleet→venture→game→unrelated) P219 → V232 (+13 offset); reproduction staged on branch `claude/p219-sprague-grundy-nim-sum`; sim dir `sims/verdict-232-sprague-grundy-nim-sum/` (byte-identical verifier copy + run-stdout.txt). Disclosed results-dict full-64 sha256 `e50e461d105e4984f6f562def0eba3f527ef4030512f9cf75294ddd6709002b7` (printed on the verifier's last stdout line, exact 64-char compare, no truncation). Determinism CONFIRMED (in-process double-run + separate cross-invocation byte-identical). All 6 pre-registered gates PASS. Born-red HOLD armed on this first card commit; released only by the deliberate `complete` flip LAST. VERDICT 232 ruling pending.

⏳ Flip note (born-red): this card ships `> **Status:** \`in-progress\`` on its FIRST commit so the substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST commit — only after the sim dir (byte-identical verifier copy + captured reproduction stdout), the digest match (full-64 exact `e50e461d105e4984f6f562def0eba3f527ef4030512f9cf75294ddd6709002b7`), and the six-gate evaluation (all PASS) have landed. That flip clears the HOLD and releases merge-on-green. NO merge API calls are made from this session; CI + the landing automation merge the green PR.

## What this verdict does

Stage the SEED=20260717 stdlib verifier for PROPOSAL 219 (Nim / Sprague–Grundy nim-sum zero criterion + Sub({1..k}) Grundy closed form G(n)=n mod (k+1)) in sim-lab so VERDICT 232 (+13 offset) can reproduce it. All 6 gates PASS deterministically (in-process double-run + separate re-invocation byte-identical). Disclosed results-dict sha256 = e50e461d105e4984f6f562def0eba3f527ef4030512f9cf75294ddd6709002b7.

## ⟲ Previous-session review

Previous-session review: Round-52 GAME slot. Verifier byte-identical to the idea-engine copy at ideas/superbot-games/sprague-grundy-nim-sum-2026-07-20.py. Gates: G1 MC P-density approx 1/8 (|z|<3, z=1.446904); G2 exhaustive density == Fraction(1,8) (64/512); G3 G(n)==n mod 4 on [0,256] zero-mismatch; G4 disjunctive-sum G_sum==G(a)^G(b) on [0,40]^2 zero-mismatch; G5 G(n)==n mod (k+1) for k in {2,3,4,5}; G6 naive total-parity rejected (z=-334.45).

## 💡 Session idea

Reproduction harness staged at sims/verdict-232-sprague-grundy-nim-sum/; VERDICT 232 ruling pending. PROPOSAL 219 → VERDICT 232 (+13 offset).

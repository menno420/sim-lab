# Session — PROPOSAL 229 → VERDICT 242 staging (derangement routing: P(no agent to its home task) = D_N/N! → 1/e)

> **Status:** `complete`
> Born-red HOLD: lands `in-progress` on the first commit to hold the PR red through substrate-gate, flips to `complete` as the last commit once the byte-identical verifier, probe report, and captured stdout are in place and verified. Merge-on-green lands it (zero agent merge calls).

## 💡 Session idea

Stage the SEED=20260717 stdlib verifier for idea-engine PROPOSAL 229 (round-54 FLEET slot) as VERDICT 242 (+13 offset). Claim: routing N agents to N tasks by a uniformly-random permutation (a random bijection) leaves NO agent on its own home task with probability p_N = D_N/N! = Σ_{k=0}^{N} (−1)^k/k! → 1/e ≈ 0.367879 — it never decays to 0 as the fleet grows — and it is NOT the naive independence estimate (1−1/N)^N. Firsthand stdlib-only verifier under `sims/verdict-242-derangement-routing/verify_229_derangement_routing.py` (byte-identical copy of the idea-engine source, diff exit 0).

## ⟲ Previous-session review

VERDICT 241 (random-walk no-return, PROPOSAL 228) landed (#325). Round-54 rotation continues fleet → venture → game → unrelated; this is the FLEET slot staging (P229 → V242), following the UNRELATED slot V241. Carry-forward: GATE-POLARITY discipline — read each gate in its own direction (exact identity = zero-error pass, agreement = small |z| pass, falsifiability = large |z| pass) — and V235/V238 GROUNDING-accuracy discipline (attribute quoted vs derived honestly against the pinned revision).

## 🫀 Heartbeat

`verify_229_derangement_routing.py` verified green: exit 0, four gates PASS each in its own direction, results-dict sha256 `1f68c3d1cb6003f6ede1bc1d47e18f27a996bea9fa716f759d38fc2c3832365a` byte-identical across in-process double-run (`in_process_double_run: IDENTICAL`) and separate re-invocation (stdout sha256 `7f0b6c26e3b5950e6459088045a19a2634f239e63ef1573bad78a8e00fefc16f`), SEED=20260717, stdlib-only. G1 EXACT two-route identity p_n=Fraction(D_n,n!) == Σ(−1)^k/k! for n=1..12 (p_7=103/280=1854/5040); G2 MC agreement N=7 T=2,000,000 z=−1.151504<3 (phat=0.3674645 over 734929/2000000); G3 exact invariants — second recurrence D_n=n·D_{n−1}+(−1)^n (n=1..15), 0<p_n<1 (n=2..15), alternating straddle p_even>1/e>p_odd (n=2..12); G4 FALSIFIABILITY naive independence q_7=(6/7)^7=0.339917 REJECTED z_naive=82.246356≥8 while the exact model is accepted. `run-stdout.txt` captures the full results dict + digest; `probe-report.md` records the gate polarity + grounding split.

> 📊 Model: Claude Opus · high · verifier-staging / FLEET slot

## Decisions made

- Stage as sim-ready for VERDICT 242: exact core (G1 two independent routes agree as Fractions for n=1..12; G3 exact invariants + alternating straddle of 1/e), byte-identical reproduction (diff exit 0), determinism held (double-run + separate invocation), and the falsifiability gate rejects the naive (1−1/N)^N independence model at ~82σ while the exact model is accepted.
- The verifier is the firsthand artefact; the idea-engine doc references it and ships its own copy at `ideas/fleet/verify_229_derangement_routing.py`.
- Grounding byte-pinned to Wikipedia "Derangement" oldid 1364530247 (raw-wikitext sha1 ba6f5759199b761a56d50342132212bbc99ed505, API-sha1 = self-computed match); split HONEST — closed form, both recurrences, nearest-integer, and the 1/e derangement-probability limit are QUOTED literally on the pinned revision; the fleet-routing framing, the p_7 ratio, the naive falsifier, and all MC z-values are DERIVED firsthand.

## Next session should know

- PROPOSAL 229 → VERDICT 242 (+13 offset); round-54 FLEET slot. Sim dir `sims/verdict-242-derangement-routing/` (verifier + run-stdout.txt + probe-report.md).
- VERDICT 242 ruling pending; this staging opens READY and lands via merge-on-green (substrate-gate sole check, no agent merge calls).
- Distinct from the existing hat-check reproduction (P204→V217, fixed-point COUNT ~ Poisson(1)); this pins the k=0 nobody-home RATIO with a two-route exact identity + independence falsifier.

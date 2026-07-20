# Session 2026-07-20 — VERDICT 239 · Myerson optimal reserve

> **Status:** `complete`

## 💡 Session idea
Reproduce Ideas Lab PROPOSAL 226 (Myerson optimal reserve for iid Uniform[0,1] bidders: the revenue-maximizing single-item mechanism is a second-price auction with reserve r*=1/2 — the SAME for every n — with exact expected revenue R*(n)=2n/(n+1)−1+(1/2)^n/(n+1); so R*(2)=5/12 vs the no-reserve 1/3, an extra 1/12). Stdlib-only firsthand verifier, SEED=20260717, Z_GATE=3.0, N_MC=200000, full-64 digest, seven gates each in its own direction -> APPROVE.

## ⟲ Previous-session review
sim-lab HEAD carried VERDICT 237 (Cayley's formula T(n)=n^(n−2) via the Prüfer bijection). Carry-forward is GATE-POLARITY discipline: read each gate in ITS OWN direction — exact identities are self-certifying theorems (G1 virtual value psi(1/2)=0, G2 three independent exact revenue routes agreeing R_closed==R_integral==R_decomp for n∈{1..5}, G3 the exact rationals R*(2)=5/12, no-reserve 1/3, gain 1/12), Monte-Carlo z-tests are AGREEMENT gates when the closed form is the null (G4 n=2 vs 5/12, G5 n=3 vs 17/32, both |z|<3), a dyadic-grid sweep is a ROBUSTNESS gate (G6 R(n,r) maximized at r=1/2 for n∈{2,3,5}), and the deliberately-wrong "no reserve is optimal" model that must be REJECTED is a FALSIFIABILITY gate read at the opposite polarity (G7 paired MC gain rejected at z=175.4≫10).

## 🫀 Heartbeat
> 📊 Model: Claude Opus · high · verify/reproduction

Firsthand verifier `myerson-optimal-reserve.py` (stdlib-only) reproduces results_sha256 b125afaf186e8d2430783b89af1a877193a65752db77884458485ced7ec918f0; determinism confirmed both ways (in-process double-run guard + separate cross-invocation byte-identical); all seven gates PASS. `python3 bootstrap.py check --strict` exits 0. Born-red HOLD armed on this first card commit (in-progress); the sims/ dir lands mid-branch; this card flips to `complete` in the LAST commit to release merge-on-green. NO merge API calls from this session; CI + the landing automation merge the green PR.

⏳ Flip note (born-red): this card ships `> **Status:** `in-progress`` on its FIRST commit so the substrate born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the deliberate LAST commit — only after the verifier reproduction (byte-identical, full-64 digest match, seven-gate evaluation each in its own direction, determinism both ways) is confirmed. That flip clears the HOLD and releases merge-on-green.

## Decisions made
- Staged as a reproduction dir (verifier + run-stdout.txt + probe-report.md), mirroring the verdict-235/236/237 pattern. R*(n)=2n/(n+1)−1+(1/2)^n/(n+1) proven FIRSTHAND: (a) three independent exact routes (closed form, virtual-surplus integral, sell-decomposition) agree as Fractions for n∈{1..5} with Rstar={1:1/4, 2:5/12, 3:17/32, 4:49/80, 5:43/64}; (b) the virtual value psi(v)=2v−1 vanishes at r*=1/2; (c) Monte-Carlo revenue at n=2,3 agrees with the closed form within 3σ; (d) a dyadic-grid sweep confirms r=1/2 is the exact maximizer; (e) the paired no-reserve alternative is rejected at z≫10.
- N_MC=200000 held (no bump needed): G4 z=−0.822244, G5 z=1.815919, G7 paired-gain z=175.44 — G4/G5 within 3σ, G7 rejected far beyond, at SEED=20260717.
- Outbox NOT appended in this PR: the recent verdict PRs (233–237) do not touch control/outbox.md; the outbox append is the fleet-manager's separate sweep step, so replicating the verdict-237 PR shape means session-card + claim + sim-dir only.

## Next session should know
- verdict-239 reproduction present and green; digest b125afaf…18f0. Reserve r*=1/2 is n-independent; R*(2)=5/12 beats no-reserve 1/3 by exactly 1/12. Grounding pinned to Wikipedia "Regular distribution (economics)" oldid 1304906615 (quotes the virtual-valuation formula and reserve principle; the specific numbers are derived, not quoted).

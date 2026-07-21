# VERDICT 251 reproduction mirror — insurance risk-pooling / diversification variance law, PROPOSAL 238

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 251 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 238 (venture · insurance / diversification variance law · ρ=0 independent baseline)
**Lane:** P238 → V251 (+13 offset)
**Verifier:** `verify_238_risk_pooling.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 1e0520c849597c1b6a4135598ee76617488c49659c1820e1841b255b9115cbbb`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical
- G1 EXACT — Var[L̄] computed two independent ways via `fractions.Fraction` (closed form Var(S)/n² vs full-binomial-pmf reconstruction E[(S/n)²]−E[S/n]²), both == 9/10000 with zero error; pmf sums to exactly 1 → PASS
- G2 Monte-Carlo agreement — 100 000 independent pools of n=100 Bernoulli(1/10) members; empirical mean cost vs p and empirical Var[L̄] vs 9/10000, max |z| = 1.4513 (< 3, Z_ACCEPT = 3.0) → PASS
- G3 invariance — (i) Var[L̄]·n == p(1−p) exactly across n ∈ {1,10,100,1000} (the σ²/n law); (ii) coefficient of variation independent of claim severity, CV² = (1−p)/(pn) → PASS
- G4 falsifiability — the naive comonotonic Var = 9/100 (ρ=1 limit) rejected by the independent pool's empirical Var[L̄] at |z| ≈ 21771.77 (≫ 8, Z_REJECT = 8.0) → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

A mutual pool has n members, each carrying an **independent** Bernoulli(p) unit loss (loss 1 with probability p, else 0). The pooled per-member cost is L̄ = S/n where S = Σ of the n losses ~ Binomial(n, p). Then exactly E[L̄] = p (the fair premium is scale-free in n) and Var[L̄] = p(1−p)/n (per-member risk falls as 1/√n). At p = 1/10, n = 100: the fair premium stays 0.1 while a single member's cost standard deviation 0.3 falls to exactly 0.03 — an exact √n = 10× reduction (Var = 9/10000). The mechanism is Bienaymé (variance of a sum of independent terms is the sum of variances → Var(S) = np(1−p)) composed with scaling (Var(aX) = a²Var(X) with a = 1/n → Var(S/n) = Var(S)/n²). The naive comonotonic belief that pooling buys nothing — Var[L̄] = p(1−p) = 9/100 for every n, the perfectly correlated ρ = 1 limit — is provably wrong: independence collapses Bienaymé's covariance cross-terms and drives the pooled variance down by the pool size n.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/venture-lab/verify_238_risk_pooling.py` (verifier file sha256 `cf35691b99fd9363d8a22a6d393f2feddb55bef07cfb193703c27c86bf179cde`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded.

## Grounding pins (informational)

The source PROPOSAL 238 pins two Wikipedia articles at their current revision; for both the API `revisions.sha1` exactly matches the self-computed `sha1sum` of the raw wikitext:

- **Variance** — `https://en.wikipedia.org/wiki/Variance@fc0e7d78428fe749117408dbeceb3d004b978c6f` (rev 1364418626) — quoted: `Var(aX) = a²Var(X)` and Bienaymé's `Var(ΣXᵢ) = ΣVar(Xᵢ)`.
- **Binomial distribution** — `https://en.wikipedia.org/wiki/Binomial_distribution@c6efae850469278e57d9b578c96871400e61c6b2` (rev 1359203125) — quoted: `npq = np(1−p)`.

The pooled law p(1−p)/n, the 0.3 → 0.03 √n reduction, and the comonotonic ρ = 1 foil are derived firsthand (grep count 0 on the pinned raw wikitext).

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 251 slice, not here._

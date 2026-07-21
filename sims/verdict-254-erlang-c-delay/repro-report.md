# VERDICT 254 reproduction mirror — Erlang-C delay probability for an M/M/c agent pool, PROPOSAL 241

> **Status:** reproduction-only — the canonical APPROVE/QUALIFIED/REJECT ruling is deferred to the coordinator-driven VERDICT 254 slice. This mirror does NOT advance the verdict high-water and does NOT append a VERDICT block.

**Source proposal:** idea-engine PROPOSAL 241 (fleet · queueing / teletraffic — the M/M/c delay (Erlang-C) probability)
**Lane:** P241 → V254 (+13 offset)
**Verifier:** `verify_241_erlang_c_delay.py` (byte-identical copy of the firsthand idea-engine verifier; stdlib only: json, hashlib, math, random, fractions)
**SEED:** 20260717

## Reproduction result

Ran the byte-identical verifier here; `run-stdout.txt` holds the full output.

- `results_sha256 = 4d382264df161dcd033abc0592afc58a84173b58aaf061449d6c7d72d832dc39`
- in-process double-run: IDENTICAL · separate re-invocation: byte-identical · `--selfcheck`: byte-identical
- G1 EXACT identity — direct == from_b == stationary, exact via `fractions.Fraction`. Over the panel {(2,1),(3,2),(5,3),(10,6),(10,17/2),(20,15)} the three independent routes to C(c,a) — the direct Erlang-C sum, the Erlang-B bridge C=B/(1−ρ(1−B)), and the birth-death stationary reconstruction — agree bit-for-bit; error_count = 0; C(2,1) = 1/3, C(10,6) = 1458/14393 → PASS
- G2 Monte-Carlo agreement (PASTA) — a correct FIFO discrete-event M/M/c simulator; warm-up 10 000 discarded, then MC_N = 200 000 measured arrivals thinned every THIN=50 to keep the binomial SE honest under queue autocorrelation; for (c=2, λ=1, μ=1 → a=1, expect 1/3) z = −0.2355896857, for (c=10, λ=6, μ=1 → a=6, expect 1458/14393) z = 0.8459716886; both |z| < 3 (Z_ACCEPT = 3.0) → PASS
- G3 invariance — time-scale invariance C = f(c, a=λ/μ) only: (i) exactly, C for (λ,μ) ∈ {(1,1),(3,3),(7,7)} (all a=1, c=2) are the identical Fraction 1/3 (exact_identical = True, mismatch_count = 0); (ii) the DES at (λ,μ)=(3,3) and (7,7) with c=2 both agree with 1/3 at z = −0.2355896857 and z = −0.2355896857 (byte-identical to the (1,1) run — at a=1 the sample path scales by 1/λ, so event ordering and every wait decision are unchanged); both |z| < 3 → PASS
- G4 falsifiability — on the SAME (c=2, a=1) MC sample: the naive "delay = utilization ρ = 1/2" is rejected at z_naive_rho = −149.2933145858 (|z| ≥ 6, Z_REJECT = 6.0); and the naive "Erlang-C = Erlang-B" is refuted both exactly (1/3 ≠ 1/5 = B(2,1), exact_distinct = True) and at z_naive_b = 148.7935533928 → PASS
- all_gates_pass = true · first_failing_gate = null · decision = PASS

## Claim reproduced

Model a pool of c parallel agents as an M/M/c queue: Poisson arrivals at rate λ, exponential service at rate μ per agent, offered load a = λ/μ Erlangs (require a < c for stability), utilization ρ = a/c. The probability that an arriving task must WAIT — it finds all c agents busy — is exactly the Erlang-C formula

    C(c,a) = [ a^c/c! · c/(c−a) ] / [ Σ_{k=0}^{c−1} a^k/k!  +  a^c/c! · c/(c−a) ].

Headline exact rationals: C(2,1) = 1/3 (c=2, a=1, ρ=1/2); C(10,6) = 1458/14393 (c=10, a=6, ρ=0.6). Two naive rivals are shown false on the same evidence: "delay probability = utilization ρ = a/c" (at c=2,a=1 that gives 1/2 ≠ 1/3, rejected at ≈149σ on the same sample where 1/3 agrees at <1σ) and "delay = blocking, i.e. Erlang-C = Erlang-B" (B(2,1) = 1/5 ≠ 1/3, exact, and ≈149σ on the sample) — the M/M/c DELAY (queued) probability is a distinct object from the M/M/c/c LOSS (blocked-calls-cleared) probability.

## Verifier source integrity

Byte-identical to idea-engine's firsthand verifier `ideas/fleet/verify_241_erlang_c_delay.py` (verifier file sha256 `98238c7eba39db20199297a11557ae2d8370ea547f9f099ee5a6ffc3cfe2be46`). The copy in this directory carries the same sha256, confirming a byte-for-byte reproduction of the source verifier; stdlib-only, no network, SEED hardcoded. build_results() is a pure function of SEED and the module constants (each Monte-Carlo run consumes its own random.Random(SEED)-seeded stream in a fixed event order; exact rationals serialize via str(Fraction) and every float via a fixed f"{v:.10f}" string; no wall-clock / PID / unordered-set iteration enters the hashed payload), so the in-process double-run and the separate subprocess re-invocation are byte-identical and the results_sha256 reproduces exactly.

## Grounding

Grounding is omitted from this mirror by design — the pinned Wikipedia revision (M/M/c queue, oldid 1349283273) and the quoted/derived split live with the source PROPOSAL 241, and the canonical grounding review belongs to the coordinator-driven VERDICT 254 slice, not to this reproduction-only mirror.

---

_Reproduction-only mirror; the canonical APPROVE/QUALIFIED/REJECT ruling lives in the coordinator-driven VERDICT 254 slice, not here._

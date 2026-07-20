# VERDICT 226 — PROPOSAL 213 (Little's law as a pathwise, distribution-and-discipline-free identity)

**Ruling: APPROVE**

Reproduced byte-exact; all four pre-registered gates independently confirmed each in its own direction; determinism holds in-process and cross-invocation; grounding sha1-pinned and the caveat is HONEST.

Headline: change the scheduler, change every wait — but throughput × mean-time-in-system still counts the queue to the bit. On every sample path of a work-conserving queue, `area under N(t) == Σ (dep−arr)` as an exact bookkeeping identity, so `L = λ·W` holds exactly per realization for FIFO, LIFO, SIRO, and priority — with L and W discipline-dependent but the emptying time T (hence λ) invariant.

## Reproduction
- Source verifier: idea-engine `ideas/fleet/littles-law-distribution-free-2026-07-20.py`, copied **byte-identical** (`diff` source↔copy exit 0) to `sims/verdict-226-littles-law-pathwise/littles-law-distribution-free-2026-07-20.py`.
- SEED=20260717, stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions.Fraction`).
- `results_sha256 = 51c34924d9bc600417a69ad84c60780c337efda7d70fd3929e3d2801daf4131f` — **FULL-64 EXACT** match to the disclosed PROPOSAL 213 digest (64 hex chars, exact string compare, no truncation; printed by the verifier AND independently `grep`-extracted identical).
- Digest posture: WHOLE-DICT — the compact-canonical results dict's own sha256 IS the digest (`json.dumps(r1, sort_keys=True, separators=(",",":"))` → `hashlib.sha256`).

## Determinism
- In-process double-run guard: `determinism_double_run_ok: true` (the verifier runs `run_battery()` twice and compares digests).
- Cross-invocation: two separate process runs produced byte-identical stdout (`run-stdout.txt` vs `run-stdout-2.txt`, `diff` exit 0) and the same full-64 digest. The idea-engine source and the sim-lab copy also produced the identical digest across four total invocations.

## Gate evaluation (each read in ITS OWN direction, against the proposal's OWN criteria)

- **G1 — pathwise identity + throughput invariance — PASS.** For all 200 realizations × all four disciplines {FIFO, LIFO, SIRO, priority} the exact-Fraction identity `area_under_N == Σ(dep−arr)` holds (`identity_exact_all: true`, zero-tolerance equality), AND the final emptying time T is identical across the four disciplines in every realization (`lambda_invariant_all: true`). Independently re-exercised on a fresh realization (`Random(999)`, n=30): all four disciplines gave `area == sumW`; the four T values collapsed to a single value (T=124); and the **per-customer wait vectors genuinely differ FIFO vs LIFO** — the identity is not holding because the waits are constant, it holds because area and ΣW are the same object counted two ways. Direction: exact equality, any mismatch FAILS.
- **G2 — non-triviality (L is discipline-dependent) — PASS.** `L_discipline_dependent_count = 200/200 (> 0)` — in every realization the time-average number in system L (=area) differs across disciplines. Independently on the fresh `Random(999)` realization: 4 distinct L values, e.g. FIFO L=1006 vs LIFO L=1115. So the exact identity of G1 is non-trivial: L and W move with the discipline while their relation to λ does not. Direction: count > 0.
- **G3 — Monte-Carlo two-sided M/M/1 discrimination — PASS.** Batch-means L̂=2.303624 (ρ=0.7, 120000 arrivals, 20000 warmup, 40 batches, se=0.032095). Against the correct closed form L=ρ/(1−ρ)=2.333333, `z_correct_abs = 0.92568 < Z_AGREE(4.0)` (agrees). Against the wrong alternative (mean *queue* length L_q=ρ²/(1−ρ)=1.633333), `z_wrong_abs = 20.884821 > Z_SEP(6.0)` (rejected by ≫6σ). BOTH sides fire: the estimate accepts the correct L and separates from the plausible wrong one — real discriminating power, not "fails to reject". Independently re-running `gate_mc_mm1` with a fresh `Random(SEED)` (a different rng consumption path than the shared battery rng) preserved the direction: z_correct=0.308 (<4) and z_wrong=16.06 (>6) — the two-sided verdict is robust to rng state; the disclosed 0.926/20.885 are the canonical battery values that produce the digest. Direction: |z_correct| below Z_AGREE AND |z_wrong| above Z_SEP.
- **G4 — robustness + falsifiability — PASS.** The identity holds exactly under **deterministic** service (svc≡4: `identity_exact_deterministic_service: true`) and under **high-variance** bimodal service (svc∈{1,7} at the same mean 4: `identity_exact_highvariance_service: true`) — invariance to service-time variance. And a deliberately perturbed accounting that drops one sojourn is **rejected** (`area != Σ_bad`, `perturbed_accounting_rejected: true`) — the gate can fail, so passing is informative. Independently re-exercised (`Random(1234)`, n=30): deterministic exact, high-variance exact, and the drop-one-sojourn perturbation strictly `!=` area. Direction: exact equality under correct accounting; strict inequality under perturbation.

`gates = {G1: true, G2: true, G3: true, G4: true}`, `sim_ready: true`. The counterintuitive head — occupancy needs no service-distribution model and the identity is exact per sample path — holds under zero-tolerance Fraction equality (G1/G2/G4) and is corroborated on a stochastic M/M/1 world with two-sided discriminating power (G3).

### Observed vs disclosed (all match)
| Quantity | Disclosed | Observed |
|---|---|---|
| results_sha256 | 51c34924…4131f | 51c34924…4131f (full-64) |
| identity_exact_all (200×4) | true | true |
| lambda_invariant_all | true | true |
| L_discipline_dependent_count | 200 | 200 |
| L_hat / se | 2.303624 / 0.032095 | 2.303624 / 0.032095 |
| z_correct_abs (<4) | 0.92568 | 0.92568 |
| z_wrong_abs (>6) | 20.884821 | 20.884821 |
| identity_exact_deterministic_service | true | true |
| identity_exact_highvariance_service | true | true |
| perturbed_accounting_rejected | true | true |

## Grounding (accuracy scrutinized — per the V222 lesson)
Wikipedia "Little's law", oldid **1362803400**, raw-wikitext (`action=raw`) sha1 `1f5cd6c91d404f83bacff533e81c0c509b973c36` — **CONFIRMED** (`sha1sum` on the 16570 raw bytes == disclosed pin, full-40 hex match).

The proposal's caveat (its Q6 answer) claims the page states `L = λW` and its independence from the arrival distribution, the service distribution, and the service order, but does NOT carry the sample-path / Brumelle (H=λG) per-realization form nor the discipline-dependence experiment. Verified against the wikitext:

**CONFIRMED PRESENT:**
- `L = \lambda W` — the identity appears twice in the wikitext (the lead math line and the mathematical-statement section).
- The generality sentence, verbatim: *"The relationship is not influenced by the arrival process distribution, the service distribution, the service order, or practically anything else."* — this is exactly the distribution-free AND service-order (discipline)-free generality of the *relationship* that the proposal cites.

**CONFIRMED ABSENT on-page** (grep returned no hits):
- **Brumelle / "sample path" / "pathwise" / H=λG** — zero occurrences. The per-realization sample-path form is not on the page.
- **The discipline-dependence experiment** — no FIFO/LIFO/SIRO/priority comparison showing L and W individually DEPEND on the discipline while T/λ do not. The only scheduling-discipline mention is "first come, first served" inside the *Distributional form* section (Keilson–Servi 1988), an unrelated distributional result — not this proposal's discipline-dependence-of-L experiment.

**Assessment: HONEST.** The caveat asserts only what the page verbatim carries (`L=λW` + the not-influenced-by-distribution-or-order generality of the relationship) and correctly scopes the sample-path/Brumelle form and the FIFO→LIFO→SIRO→priority discipline-dependence experiment as the verifier's OWN firsthand contributions, not lifted from the page. A well-scoped, accurate disclosure → APPROVE.

## Decision
All four gates pass in their stated directions; the full-64 digest matches the disclosed value exactly; determinism holds in-process and cross-invocation; the grounding is byte-pinned and the caveat is honest. **VERDICT 226 = APPROVE** (P213 → V226, +13 offset, lane fleet, round-51 FLEET opener).

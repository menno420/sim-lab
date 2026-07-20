# VERDICT 226 — change the scheduler, change every wait, but throughput × mean-time-in-system still counts the queue to the bit: Little's law L=λW is an EXACT pathwise identity for every work-conserving discipline (FIFO/LIFO/SIRO/priority), distribution-and-discipline-free, with L,W discipline-dependent but T/λ invariant — reproduce PROPOSAL 213

> **Status:** complete

📊 Model: Opus family · high · review/verify

started: 2026-07-20T13:35:41Z

💓 Heartbeat: round-51 FLEET opener P213 → V226 (+13); reproduction on branch `claude/verdict-226-littles-law`;
sim dir `sims/verdict-226-littles-law-pathwise/` (byte-identical verifier copy + run-stdout.txt + run-stdout-2.txt
+ probe-report). Digest target full-64 `51c34924d9bc600417a69ad84c60780c337efda7d70fd3929e3d2801daf4131f`
(printed AND independently grep-extracted, full-64 EXACT string compare, no truncation). Determinism CONFIRMED
(in-process double-run guard `determinism_double_run_ok: true` AND two separate-invocation runs byte-identical
stdout; idea-engine source and sim-lab copy agree across four total invocations). Four pre-registered gates each
in its own direction — G1 PATHWISE IDENTITY + λ-INVARIANCE: `area_under_N == Σ(dep−arr)` exact-Fraction for all
200 realizations × all 4 disciplines AND T identical across disciplines every realization (independently
re-exercised: per-customer wait vectors DIFFER FIFO vs LIFO while the identity still holds exactly, T collapses
to one value); G2 NON-TRIVIALITY: `L_discipline_dependent_count=200/200 > 0` (independently 4 distinct L values,
FIFO 1006 vs LIFO 1115); G3 M/M/1 TWO-SIDED: z_correct_abs=0.92568 < Z_AGREE 4.0 (agrees with L=ρ/(1−ρ)=2.3333)
AND z_wrong_abs=20.884821 > Z_SEP 6.0 (rejects the mean-queue alternative L_q=1.6333) — both sides fire; G4
ROBUSTNESS + FALSIFIABILITY: identity exact under deterministic (svc≡4) AND high-variance bimodal (svc∈{1,7},
same mean) service, and a dropped-sojourn perturbed accounting is REJECTED (`area != Σ_bad`) — all PASS,
`sim_ready: true`. Grounding byte-pinned (Wikipedia "Little's law" oldid 1362803400, raw-wikitext sha1
`1f5cd6c91d404f83bacff533e81c0c509b973c36` CONFIRMED on 16570 raw bytes); the disclosed caveat (page carries
`L=λW` and its independence from the arrival distribution, service distribution, and service order; the
sample-path / Brumelle H=λG per-realization form and the FIFO→LIFO→SIRO→priority discipline-dependence
experiment are the verifier's OWN firsthand results, NOT on the page) is ACCURATE — HONEST scope. APPROVE.
Born-red HOLD armed on this first card commit; released by the deliberate `complete` flip LAST.

⏳ Flip note (born-red): this card ships `> **Status:** in-progress` on its FIRST commit so the substrate
born-red gate holds the sim-lab PR RED until the slice is genuinely done. It flips to `complete` as the
deliberate LAST commit — only after the sim dir (byte-identical verifier copy + both reproduction stdouts +
probe-report), the digest match (full-64 exact `51c34924d9bc600417a69ad84c60780c337efda7d70fd3929e3d2801daf4131f`
— printed + independently reproduced), the four-gate evaluation each in its own direction (all PASS), the
determinism check (in-process double-run guard held AND separate-invocation stdout byte-identical), and the
grounding-accuracy check (raw-wikitext sha1 confirmed, caveat verified HONEST) have ALL landed, and the
status.md heartbeat is re-stamped. That flip clears the HOLD and releases merge-on-green. NO merge API calls
are made from this session; CI + the landing automation merge the green PR.

## What this verdict does

Reproduces PROPOSAL 213 (P213 → V226, +13 offset, lane FLEET — opens the round-51 fleet→venture→game→unrelated
cycle): **change the scheduler, change every wait — but throughput × mean-time-in-system still counts the queue
to the bit.** For a single-server, work-conserving, non-preemptive queue that starts and ends empty, the area
under the number-in-system curve N(t) is, by construction, the sum of the individual sojourn times — so
`L = λ·W` is not an ensemble approximation but an EXACT bookkeeping identity that holds on every sample path,
for any arrival process, any service-time distribution, and any work-conserving discipline. The non-trivial
twist the proposal pins: switch FIFO→LIFO→SIRO→priority on the SAME arrival and service streams and you change
who waits, how long each waits, AND the time-average number in system L — yet the final emptying time T (hence
λ) is byte-identical, and `L=λW` holds exactly for every discipline. L and W are discipline-dependent; their
relation to λ is not. Copies the disclosed verifier `ideas/fleet/littles-law-distribution-free-2026-07-20.py`
(idea-engine) byte-identical into `sims/verdict-226-littles-law-pathwise/`, reproduces the results-dict sha256,
confirms determinism, and evaluates the four pre-registered gates each in its own direction against the
proposal's OWN criteria.

## Method

- Byte-identical verifier copy (`diff` source↔copy exit 0), stdlib-only (`hashlib`, `json`, `math`, `random`,
  `fractions.Fraction`). SEED = 20260717.
- Digest posture: WHOLE-DICT / STDOUT — the compact-canonical results dict's own sha256 IS the digest; target
  `51c34924d9bc600417a69ad84c60780c337efda7d70fd3929e3d2801daf4131f` (full-64 exact).
- Gates (each read in ITS OWN direction — against the proposal's OWN criteria):
  - **G1 — pathwise identity + λ-invariance** (direction: exact-Fraction equality, zero tolerance):
    `area_under_N == Σ(dep−arr)` for all 200 realizations × 4 disciplines AND T identical across disciplines
    every realization. Independently re-exercised on `Random(999)`: identity exact for all 4, T collapses to a
    single value, per-customer wait vectors DIFFER FIFO vs LIFO (non-trivial).
  - **G2 — non-triviality** (direction: count > 0): `L_discipline_dependent_count = 200/200`. Independently 4
    distinct L values on `Random(999)` (FIFO 1006 vs LIFO 1115).
  - **G3 — M/M/1 two-sided discrimination** (direction: |z_correct| < 4 AND |z_wrong| > 6): L̂=2.303624,
    se=0.032095; z_correct_abs=0.92568 (agrees with L=ρ/(1−ρ)=2.3333), z_wrong_abs=20.884821 (rejects the
    mean-queue alternative L_q=1.6333). Both sides fire — real discriminating power.
  - **G4 — robustness + falsifiability** (direction: exact under correct accounting, strict inequality under
    perturbation): identity exact under deterministic (svc≡4) AND high-variance bimodal (svc∈{1,7}, same mean)
    service, and a dropped-sojourn perturbed accounting is REJECTED (`area != Σ_bad`). Independently
    re-exercised on `Random(1234)`.
- Grounding (disclosed, honestly bounded): Wikipedia "Little's law" oldid 1362803400, byte-pinned by
  raw-wikitext sha1 `1f5cd6c91d404f83bacff533e81c0c509b973c36`. The page carries `L=λW` and its independence
  from the arrival distribution, service distribution, and service order; the sample-path / Brumelle (H=λG)
  per-realization form and the FIFO→LIFO→SIRO→priority discipline-dependence experiment are the verifier's OWN
  firsthand results, disclosed as not lifted from the page.

## ⟲ Previous-session review

Previous-session review: VERDICT 225 (Pólya recurrence — a drunk man finds home in 2D / a drunk bird may be
lost forever in 3D; the simple symmetric lattice walk returns w.p. 1 in 2D but only ~0.3405 in 3D; PROPOSAL 212
→ V225) landed **APPROVE** with a full-64 digest MATCH
(`66ca292316986d8121a552e3c4c61557182d787b2e25cf54659a0130d0dede07`) and all six gates PASS via the born-red
HOLD choreography. Its carry-forward is GATE-POLARITY discipline: read each gate in ITS OWN direction — an
exact-Fraction / integer-exact residual is a self-certifying theorem, a ≥3σ z is an EFFECT gate, a
decay-in-band is a CONVERGENCE gate. V226 leans on that same discipline but spans a DIFFERENT polarity mix in
one slice: G1/G2/G4 are exact-Fraction identity gates (zero-tolerance `area == ΣW` — any discrepancy FAILS,
self-certifying), while G3 is a genuinely TWO-SIDED ≥kσ effect gate — not a one-sided "≥3σ from a folk null"
but a simultaneous accept-the-correct (|z|<4) AND reject-the-wrong (|z|>6) test, which is stronger evidence of
discriminating power than either side alone. That two-sidedness is the load-bearing improvement over the V220
single-null surprise gate and the V224/V225 dominance gates: it certifies the estimator lands on the RIGHT
closed form and is separated from a PLAUSIBLE wrong one (mean-queue vs mean-system), catching the classic
Little's-law confusion. V225 also carried a disclosed grounding caveat (qualitative-on-the-page, exact framing
owned by the proposal); V226's grounding is the same good posture and the better inverse of V222 — the page's
`L=λW` + not-influenced-by-distribution-or-order sentence is on the byte-pinned revision, while the sample-path
/ Brumelle form and the discipline-dependence experiment are the verifier's OWN firsthand contributions
(checked in the probe-report against the raw wikitext: "Brumelle"/"sample path"/"pathwise"/FIFO-LIFO-SIRO
comparison all return zero on-page hits). Standing non-contiguity persists: landing V226 does not imply every
lower verdict below the high-water is closed.

## 💡 Session idea

The verifier proves `L=λW` exactly on each sample path and shows L,W move with the discipline while T/λ do not —
but it demonstrates discipline-INVARIANCE of T only for order-based, non-size-based disciplines (FIFO/LIFO/SIRO/
priority-by-random-key). The proposal's own Model basis flags the real knife-edge: SIZE-BASED PREEMPTIVE
disciplines (SRPT — shortest-remaining-processing-time) can change the number-in-system trajectory AND the
emptying time is no longer the naive last-departure of a non-preemptive run. A cheap, orthogonal follow-on
(call it P-next) would reproduce, Fraction-exact, the **boundary of the T-invariance claim**: add a preemptive
SRPT discipline to the same seeded arrival/service streams and show (a) `L=λW` STILL holds exactly per
realization whenever the window opens and closes empty (the identity survives — it is pure area/ΣW bookkeeping,
preemption-agnostic), while (b) the T-invariance BREAKS — the SRPT emptying time can differ from the
work-conserving-non-preemptive T because preemption reshuffles which jobs are in service at the window edge
unless the queue is genuinely empty at close. The gate: `area==ΣW` exact for SRPT (identity robust) AND a
positive count of realizations where T_SRPT != T_FIFO (invariance-scope boundary pinned). It reuses the V226
`simulate`/`area_under_N` machinery — `simulate` needs only a preempt-on-shorter-remaining branch — and turns
"SRPT is out of scope of the T-invariance claim" from a stated caveat into a pinned exact object: the identity
is universal, the T-invariance is disciplined. Pairs cleanly with the standing grounding-caveat-automation idea
(a deterministic checker diffing the verifier's claimed page-facts against the byte-pinned revision), which this
slice would have caught the `L=λW` + not-influenced-by-order sentence for automatically.

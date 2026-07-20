# VERDICT 220 — Complete rent dissipation in the all-pay auction: n rivals burn a total of exactly V, no more, and every bidder breaks even. In the symmetric complete-information all-pay auction (prize V, n ≥ 2 risk-neutral bidders, highest bid wins, EVERYONE pays), the symmetric mixed-strategy equilibrium F(b)=(b/V)^(1/(n−1)) burns total expected effort exactly V independent of n, and each bidder's expected net payoff is exactly zero — adding rivals only thins the per-head slice to V/n — reproduce PROPOSAL 207

- **Slice:** sim-lab VERDICT 220 (reproduce and rule on PROPOSAL 207; P207 → V220, +13 offset; lane superbot-games)
- **Source proposal:** PROPOSAL 207 — `ideas/superbot-games/allpay-rent-dissipation-2026-07-20.md` (idea-engine); verifier landed on origin/main at commit f82153c (idea-engine PR #764)
- **Verifier (source):** `ideas/superbot-games/allpay-rent-dissipation-2026-07-20.py` (idea-engine) — copied byte-identical into this sim dir as `verifier.py`
- **Reproduced by:** copy the verifier byte-identical (diff exit 0), run it, capture stdout, recompute the results-dict sha256 and confirm full-64 match; two cross-invocation runs byte-identical
- **Timestamp (date -u):** 2026-07-20T10:29:32Z
- **SEED:** 20260717

## 📊 Model: Opus family · high effort · verdict-reproduction

## Ruling: APPROVE

Fully reproduced. The results-dict sha256 `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70`
matches the disclosed PROPOSAL 207 digest across all 64 hex characters — printed by the verifier AND
independently recomputed here by re-canonicalizing the printed results dict (0 divergence). The verifier
was copied byte-identical (diff exit 0). All three gates PASS each read in its own direction; the G1 leg
is a self-certifying EXACT-Fraction identity (revenue and payoff residuals are exactly 0, not tuned
tolerances). The head is honestly scoped to the COMPLETE-INFORMATION symmetric all-pay auction and is
externally grounded to a sha1-pinned Wikipedia revision whose complete-info sentence firsthand-supports
the break-even / revenue=V leg; the proposal explicitly discloses the two grounding caveats and does NOT
conflate the complete-info R=V head with the page's different incomplete-info E[R]=1/3 example.

## Head

Complete rent dissipation in the all-pay auction. In a symmetric complete-information all-pay auction for
a prize worth V among n ≥ 2 risk-neutral bidders (highest bid wins; EVERYONE pays their own bid), the
symmetric mixed-strategy equilibrium CDF `F(b) = (b/V)^(1/(n−1))` on [0, V] burns total expected effort
**exactly V, independent of n**, and every bidder's expected net payoff is **exactly zero**. Each bidder
wins with probability 1/n, so expected gross is V/n and indifference forces expected payment to V/n too,
giving aggregate n·(V/n) = V — the entire rent and nothing more, regardless of field size. Adding rivals
does not raise total effort; it only splits the same V into thinner per-head slices (V/n each). The
win-probability identity `F(b)^(n−1) = ((b/V)^(1/(n−1)))^(n−1) = b/V` collapses the fractional root to a
rational, so `Π(b) = V·(b/V) − b = 0` for every b ∈ [0, V] as an EXACT Fraction — no irrational
arithmetic in any equality decision.

## Reproduction

- Verifier copied byte-identical: `diff ideas/superbot-games/allpay-rent-dissipation-2026-07-20.py sims/verdict-220-all-pay-rent-dissipation/verifier.py` → **exit 0**.
- results-dict sha256 posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical dict's own sha256 IS the digest (`json.dumps(results, sort_keys=True, separators=(",",":"))`, exact Fractions serialized as "num/den" strings, floats rounded to 6 dp, no self-referential sha field).
- Disclosed digest:              `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70`
- Reproduced (printed by run):   `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70`
- Independently recomputed:      `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70` — recomputed OUTSIDE the verifier by parsing the printed results dict from `run-stdout.txt`, re-serializing compact-canonical (`sort_keys=True, separators=(",",":")`), and hashing sha256 → identical across all 64 hex chars.
- **FULL-64 EXACT MATCH** (printed == independently-recomputed == disclosed target). The printed token is 64 hex chars, no truncation.
- Full reproduction stdout: `run-stdout.txt` (cross-invocation copy `run-stdout-2.txt`).

## Determinism

- In-process double-run: `build_results()` runs the computation twice in-process and aborts (exit 3) on any divergence before `main()` emits the digest; the run exited 0, so the in-process guard held.
- Cross-invocation: two separate process invocations → `run-stdout.txt` and `run-stdout-2.txt`, `diff` **exit 0** (byte-identical whole files including the digest line). The proposal reports three separate processes all emitting `f771cd42…b91d70`; this reproduction confirms it across two.

## Gate evaluation (against PROPOSAL 207's OWN criteria, in order — each read in ITS direction)

- **G1 — EXACT rent dissipation + break-even** (n∈{2..8}×V∈{1,2,3,1/2}, rational bid grid b=k·V/12 for k=0..12; direction: residual == 0, exact Fraction equality). Closed-form total R == V and per-player == V/n exactly (`revenue_residual_max = 0`), AND `Π(b) = V·(b/V) − b == 0` across the whole rational bid grid (`pi_residual_max = 0`), with `per_player_ok_all = true`. The win-prob identity `F(b)^(n−1) = b/V` makes every equality an exact-Fraction decision with no float and no irrational root, so the identity is n-independent by construction. Witness cell n=5, V=1: `per_player = 1/5 = closed_per_player`, total = 1 = V. **revenue_residual_max=0 AND pi_residual_max=0 → PASS.** (Self-certifying: an exact-0 residual is a theorem, not a tuned tolerance.)
- **G2 — competition does NOT scale total effort with n** (M=100000 seeded auctions at n=5, V=1; direction: measured ≪ naive AND |measured−V| < 3σ). Per-auction revenue = sum of n bids with bid = V·u^(n−1). `measured_R = 0.99836` ≈ V, against the naive n·(V/2) = `naive_R = 2.5` "everyone bids half" guess: `se = 0.001876`, `z_below_naive = 800.469813` (measured sits ~800σ BELOW the linear-growth prediction — captures "more rivals ≠ more total effort"), and simultaneously consistent with the closed-form V: `consistency_abs = 0.00164 < 3·se`, `consistency_within_3se = true`. **z_below_naive ≈ 800.47 ≥ 3 AND within_3se → PASS.**
- **G3 — the total is V across the whole grid** (36 cells n∈{2..10}×V∈{1,2,3,1/2}, M=10000 auctions/cell; direction: ratio → 1, max deviation < 3σ — a CONVERGENCE gate). Measured R̂/V stays within 3σ of 1 in EVERY cell: `all_within_3sigma = true`, worst cell n=8, V=2 has `ratio = 0.984982`, `max_dev_z = 2.365573`. Below-3 is the PASS direction (R̂/V → 1 within Monte-Carlo noise). **max_dev_z = 2.365573 < 3.0 → PASS.**

Overall: gates {G1:true, G2:true, G3:true}, `all_pass: True`, no first-failing gate.

## Grounding

- External, sha1-pinned: Wikipedia "All-pay auction", oldid **1345188183**, raw-wikitext sha1 `276dc7a58c201dce404fb2e3ef0006f072b01c8a` (byte-pinned; matches the disclosed grounding token). Fetched 2026-07-20T10:06:48Z per the proposal.
- Firsthand support for the break-even / revenue=V CORE, from the COMPLETE-INFORMATION case on the page: **"expected pay-offs are zero. The seller's expected revenue is equal to the value of the prize."** This is exactly the two legs of the head — every bidder breaks even (Π=0) and the seller/field revenue equals the prize value V — and the page names the mixed-strategy complete-information equilibrium.
- **Model-scope assessment (the load-bearing honesty check):** P207's head is the COMMON-VALUE, COMPLETE-INFORMATION symmetric all-pay auction (known common prize V), NOT the incomplete-information independent-private-values model. The proposal scopes this correctly and discloses BOTH caveats in its "Model basis" and probe-report §7:
  1. The page does not literally print the words "total bids = V"; the exact R = V is the arithmetic consequence of zero net payoff + win-probability 1/n (phenomenon-on-page, derived firsthand). Disclosed.
  2. The page's worked **E[R] = 1/3** example is the DIFFERENT incomplete-information / IPV model (uniform valuations), NOT this common-value complete-information model. Disclosed in "Model basis" (line 67) and probe-report §7 (line 79).
- The two models are **not conflated**: the proposal cites the complete-info "expected pay-offs are zero / revenue equals the prize value" sentence for the R=V head, and explicitly quarantines the incomplete-info 1/3 example as a departure ("the incomplete-information IPV variant yields a strictly smaller expected revenue"). The "core-on-page, exact-R=V-derived-firsthand" split is FAIR — the break-even leg is revision-pinned externally and the arithmetic R=V is exactly what a firsthand verifier certifies (G1 exact residual 0).

## Novelty

Distinct from every prior head. `grep -ri` across ideas/** for all-pay / "all pay auction" / rent dissipation / rent-seeking / Tullock / war-of-attrition returns nothing prior (the only hit is a forward-looking mention in the P199 Vickrey card, not a built head). Adjacent but distinct: Vickrey second-price (P199 — winner-PAYS sealed bid, truthful dominance) vs here EVERYONE pays and the result is a revenue/effort INVARIANCE, not a dominant strategy; balance-triangle (zero-sum matrix value); price-of-anarchy / Braess (routing inefficiency). No prior head computes an all-pay equilibrium or the rent-dissipation invariant.

## Ruling evidence summary

VERDICT 220 reproduces PROPOSAL 207 bit-exact: the verifier copied byte-identical (diff exit 0), the results-dict sha256 `f771cd427068cd273eb545a40179233ddbc5ec7658e69cf4e6cadb97dbb91d70` matches the disclosed digest across all 64 hex characters — printed AND independently recomputed outside the verifier (0 divergence) — and determinism holds (in-process double-run guard held at exit 0 AND two cross-invocation processes byte-identical). All three pre-registered gates PASS each read in its own direction: G1's EXACT-Fraction rent-dissipation + break-even identity (revenue_residual_max=0, pi_residual_max=0 across n∈{2..8}×V∈{1,2,3,1/2}; self-certifying), G2's ≥3σ effect (n=5 measured_R=0.99836 sits z=800.47 below the naive 2.5 and within 3σ of V), and G3's convergence/robustness across 36 cells (max_dev_z=2.365573<3.0, worst cell n=8,V=2). The break-even / revenue=V core is externally grounded to a sha1-pinned Wikipedia revision (oldid 1345188183, wikitext sha1 `276dc7a58c201dce404fb2e3ef0006f072b01c8a`) via its complete-info sentence, with the head honestly scoped to the complete-information model and both grounding caveats disclosed (the page does not literally print "total bids=V"; the E[R]=1/3 example is the different incomplete-info IPV model) — no conflation. The head is genuinely distinct from the shipped Vickrey/winner-pays and routing heads. **Ruling: APPROVE.**

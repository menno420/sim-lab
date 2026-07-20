# Reproduction mirror — PROPOSAL 233 / VERDICT 246 (secretary optimal stopping)

> **Status:** `reproduction` — PRE-VERDICT reproduction of idea-engine PROPOSAL 233; the byte-identical verifier reproduced green. This PR lands ONLY the reproduction material — it does NOT append a VERDICT block, does NOT author any ruling text, and does NOT advance the verdict high-water. The canonical independent APPROVE/QUALIFIED/REJECT VERDICT 246 is a separate coordinator-owned slice; adjudication is pending that slice.

## Source
idea-engine PROPOSAL 233 — ideas/fleet/verify_233_secretary_stopping.py (branch claude/proposal-233-secretary-stopping). Byte-identical copy here: sims/verdict-246-secretary-optimal-stopping/verify_233_secretary_stopping.py (diff exit 0).

## Claim
For n candidates of distinct qualities arriving in uniformly random order and observed ONLY by relative rank, the threshold rule "reject the first r−1, then take the first candidate better than every one seen so far" selects the overall-best candidate with probability EXACTLY P(r,n)=((r−1)/n)·Σ_{i=r}^{n} 1/(i−1) (with P(1,n)=1/n). The optimal cutoff r*(n) is the smallest r≥1 with Σ_{k=r}^{n−1} 1/k ≤ 1, and P(r*(n),n)→1/e≈0.36787944117144233 as n→∞ — provably beating the naive "take the first candidate" rule whose win probability is exactly 1/n→0.

## Reproduced firsthand
- SEED=20260717, stdlib-only (json, hashlib, math, random, fractions, itertools), Python 3.11.15.
- results_sha256 = 048261949a65653b7ad49d90c4968780cc5af2cb77705c9292d409743da68cac (full 64 hex), byte-identical across the in-process double-run guard + a separate re-invocation (see run-stdout.txt); the canonical results dict is saved verbatim in results.json.
- G1 EXACT identity via fractions.Fraction: for every n∈{4,5,6,7} and every r∈{1..n} the empirical win fraction (win_count/n!) equals the closed form ((r−1)/n)Σ_{i=r}^{n}1/(i−1) as Fractions; argmax_r == r*(n) (r*={4:2,5:3,6:3,7:3}); P(1,n)=1/n; P(r*,n)={11/24,13/30,77/180,29/70}.
- G2 MC agreement n=100 r*=38 N=200000: p0=P(38,100)≈0.371042778712643; p̂=0.370775; z_optimal=−0.247895 (|z|<3); asymptote 1/e≈0.36787944117144233.
- G3 invariance (both sub-checks): (a) an independent forward record-indicator DP (raw (1−1/s) products, never the telescoped form) reproduces P(r,n) as Fractions for all r and all n∈{4,5,6,7}; (b) rank-only MC drawing qualities from U³ (strictly monotone, independent seed) agrees with the same p0 at z_invariance=0.798199 (p̂=0.371905, |z|<3).
- G4 falsifiability: on the SAME MC sample as G2 the naive take-first (r=1) rule is statistically consistent with its OWN exact 1/100 (z_naive_self=−0.40452, |z|<3) yet REJECTS the optimal target p0 at z_naive_vs_optimal=−334.317693 (|z|≥6) while the optimal rule is accepted.
- all_gates_pass=true, first_failing_gate=null.

## Grounding (from the proposal, recorded for the ruling slice)
Wikipedia "Secretary problem" oldid 1356180684 sha1 9257ff8e73001e2b517dca2adab94ea46dc6a7e2 (raw-wikitext self-computed sha1 == API revision sha1; 46,543 bytes). QUOTED on the pinned revision: the exact closed form P(r)=\frac{r-1}{n}\sum_{i=r}^{n}\frac{1}{i-1} and the special case P(1)=1/n; the relative-rank-only stopping strategy and the "reject the first r−1 then take the first candidate better than all preceding" rule; the 1/e≈0.368≈37% asymptote with optimal cutoff → n/e; and the table of optimal thresholds r for n=1..10 (so r*(4)=2, r*(5)=3, r*(6)=3, r*(7)=3 are present, computed on the page via argmax). DERIVED firsthand (absent from the page): the Σ-inequality cutoff characterization "smallest r with Σ_{k=r}^{n−1}1/k≤1", the large-n cutoff r*(100)=38 and p0=0.371042778712643 (table stops at n=10), the exact reduced-Fraction forms of P(r*,n), the independent record-indicator DP second route, the naive take-first 1/n falsifier and its rejection, the rank-only U³ invariance experiment, every Monte-Carlo z-value, and the results_sha256.

## Deferred
The independent adversarial ruling (re-grounding quoted-vs-derived firsthand, re-evaluating each gate in its own direction, and the APPROVE/QUALIFIED/REJECT verdict) is the dedicated VERDICT 246 slice's deliverable. This mirror asserts reproduction only and takes no position on adjudication.

# Session — VERDICT 244 reproduction mirror (Shapley value of the airport cost-sharing game, from PROPOSAL 231)

> **Status:** in-progress
> Born-red HOLD: lands `in-progress` on the first commit to hold the PR red through substrate-gate; flips to `complete` as the last commit once the byte-identical verifier, run-stdout, and probe-report are in place and verified. Merge-on-green lands it (zero agent merge calls).

## 💡 Session idea

Reproduction mirror of idea-engine PROPOSAL 231 (round-54 GAME slot, offset +13): the cooperative Shapley VALUE of the airport cost-sharing COST game. An airport runway must be long enough for the most demanding plane; player i needs runway cost c_i, and a coalition needs v(S)=max_{i∈S} c_i. The Shapley value splits the grand cost v(N)=max c_i by sharing each ascending-sorted runway segment equally among the planes that still need it — φ_j = Σ_{k=1}^{j}(c_(k)−c_(k−1))/(n−k+1), c_(0)=0 — equivalently the average marginal contribution over uniformly random join-orders. The fair split is NOT equal shares of the total: for costs (1,2,4,8) the Shapley vector is (1/4, 7/12, 19/12, 67/12), summing exactly to the grand cost 8, while the naive equal split would charge 2 each. This PR lands ONLY the reproduction material (byte-identical verifier + firsthand run evidence + probe-report) under `sims/verdict-244-shapley-airport-cost-sharing/`; the canonical independent APPROVE/QUALIFIED/REJECT ruling is a separate coordinator-driven VERDICT 244 slice, and the verdict high-water is intentionally NOT advanced here.

## ⟲ Previous-session review

VERDICT 243 (bilateral double auction, PROPOSAL 230) reproduction mirror landed (#327). Round-54 rotation continues; this is a reproduction mirror of PROPOSAL 231 (the GAME slot), paired with idea-engine branch `claude/p231-shapley-airport`. Distinct from the already-built Shapley–Shubik power index (P203 → V216, a simple VOTING game): different characteristic function (max-cost vs pivotal-swing) and different object (a cost-allocation vector vs a per-voter power number).

## 🫀 Heartbeat

`verify_shapley_airport.py` reproduced green byte-identical to idea-engine PROPOSAL 231 (diff exit 0 vs `ideas/superbot-games/verify_shapley_airport.py`; both sha256 `0a4389a1a571a9d6a8f86de95a2a338fb3bb656f184e66b6c9ffa35e3415f7f0`): exit 0, SEED=20260717, results-dict sha256 `9cbd3c4ec0026187cd64a20bbb79167209f071adbd9a21ecade0787b55d0f4f2` (full 64 hex) byte-identical across in-process double-run and separate re-invocation. All four gates PASS each in its own direction: G1 EXACT (Fraction) closed form == n! enumeration for n=4,5 (main φ=(1/4,7/12,19/12,67/12)); G2 MC top player 200,000 join-orders z=−1.311312 (|z|<3, mean 5.57834 vs 67/12≈5.5833333); G3 efficiency Σφ=8/1==grand cost 8 AND symmetry on (2,5,5,9) sym pair 3/2==3/2; G4 naive equal split 8/4=2/1 REJECTED at z=939.716932 (>6). run-stdout.txt captures the full results dict + digest.

> 📊 Model: Claude Opus · high · review/verify

## Decisions made

- Reproduction-only: this PR lands the byte-identical verifier + firsthand run-stdout + probe-report under `sims/verdict-244-shapley-airport-cost-sharing/` and nothing else. No APPROVE/QUALIFIED/REJECT ruling block was written.
- The canonical independent VERDICT 244 ruling is deferred to a dedicated coordinator-driven slice; the verdict high-water is intentionally NOT advanced.
- control/status.md was not touched. Merge-on-green lands this green claude/* PR (zero agent merge calls).

## Next session should know

- The canonical VERDICT 244 ruling (re-grounding quoted-vs-derived firsthand against the pinned Shapley_value + Airport_problem revisions, re-evaluating each gate in its own direction, and the adversarial verdict) is a dedicated VERDICT 244 slice's deliverable, paired with idea-engine PROPOSAL 231.
- Verifier: `sims/verdict-244-shapley-airport-cost-sharing/verify_shapley_airport.py`, results-dict sha256 `9cbd3c4ec0026187cd64a20bbb79167209f071adbd9a21ecade0787b55d0f4f2`. Grounding pins Wikipedia "Shapley value" oldid 1364397219 (raw-wikitext sha1 c557fc821d4fab14d90c3f7434e1120e6e9cf020) and "Airport problem" oldid 1312709389 (raw-wikitext sha1 cc179b50972d2bf70492e5099ad242273874258a).

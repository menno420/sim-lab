# VERDICT 195 — pay-to-play cramdown cliff (reproduce PROPOSAL 182)

In a down round a pay-to-play provision converts non-participating preferred to common at a 1:1 ratio, wiping its liquidation preference. Conditional on a non-home-run exit, the marginal pro-rata dollar that keeps a holder in the preferred class is the highest-return dollar on the cap table, and the driver is the preferred to common conversion (the preference wipe), not simple dilution. The effect sharpens in cold markets.

> **Status:** complete
> 📊 Model: Claude Opus · effort high · task-class simulation-reproduction
> **Result:** reproduced — digest matches, all three gates PASS, grounding live. APPROVE.

## Objective

Copy PROPOSAL 182's verifier byte-identically into `sims/verdict-195-pay-to-play-cramdown/`, run it at SEED=20260717, confirm the in-process double-run and a separate cross-invocation byte-match, confirm the disclosed results-dict sha256, then rule VERDICT 195 strictly on what the reproduction shows.

## GROUNDING (verified at HEAD)

https://www.fenwick.com/insights/publications/what-is-a-pay-to-play-financing@8552d3db117ccbbb2c4dd7014b987834666bb971

Documents "All current preferred stock is converted to common stock at a 1:1 ratio."

## Constraints honored

- stdlib only (hashlib, json, math, random)
- SEED=20260717, TRIALS=200000
- verifier copied byte-identically (diff exit 0; file sha256 eab29688…, git blob c4214e3)

## Gate plan

G1 in-band marginal-dollar return mean >= 2.0 -> G2 conversion/dilution ratio >= 1.5 -> G3 cold-market danger-band probability plus cold conversion/dilution ratio.

## Probe questions

See `sims/verdict-195-pay-to-play-cramdown/probe-report.md` (8-item audit).

## Outcome

Byte-identical reproduction (diff exit 0; git blob c4214e36426b2c9fb6e7030abdb26af8bd8c1eac). Deterministic: in-process double-run equal, separate cross-invocation byte-match (crossdiff exit 0). Emitted results-dict sha256 `ed8a081bb104683d1ee8c0c2ec9b90e2a1212100495d9d44b5e484016a75b243` MATCHES the disclosed target.

- G1 in-band return mean 2.674407 >= 2.0 (z 308.093567) — PASS
- G2 conversion/dilution 2.362501 >= 1.5 (conv 2.348806 / dil 0.994203, z 848.320658) — PASS
- G3 cold danger-band prob 0.601695 > base 0.42401 (z 112.415006), cold conv/dil 2.516596 — PASS
- all_pass = true

Mechanism confirmed: the driver is the preferred-to-common conversion (preference wipe), not simple dilution (G2 isolates conv 2.35 vs dil 0.99); the effect amplifies cold (G3).

## ⟲ Previous-session review

VERDICT 194 (Bloom-filter optimal-k) landed its outbox ruling APPROVE while its session card Outcome still read Pending — a card/ledger seam. This card avoids that: Outcome and Status flip together at reproduction confirmation.

## 💡 Session idea

The G2 conversion-vs-dilution isolation is a reusable scoring pattern: any term whose value comes from a state conversion rather than a quantity change should be scored by a conversion-vs-baseline ratio, not a level. Worth a proposal generalizing conversion-driven vs dilution-driven scoring across the venture-lab preference-mechanics family.

**Recommendation: APPROVE — reproduces cleanly, digest matches, all three gates pass, grounding live.**

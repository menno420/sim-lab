# VERDICT 195 — pay-to-play cramdown cliff (reproduce PROPOSAL 182)

In a down round a pay-to-play provision converts non-participating preferred to common at a 1:1 ratio, wiping its liquidation preference. Conditional on a non-home-run exit, the marginal pro-rata dollar that keeps a holder in the preferred class is the highest-return dollar on the cap table, and the driver is the preferred to common conversion (the preference wipe), not simple dilution. The effect sharpens in cold markets.

> **Status:** `in-progress`
> 📊 Model: Claude Opus · effort high · task-class simulation-reproduction
> **Result:** reproduction in progress — born-red hold until gates and results-dict digest are confirmed.

## Objective

Copy PROPOSAL 182's verifier byte-identically into `sims/verdict-195-pay-to-play-cramdown/`, run it at SEED=20260717, confirm the in-process double-run and a separate cross-invocation byte-match, confirm the disclosed results-dict sha256, then rule VERDICT 195 strictly on what the reproduction shows.

## GROUNDING (verified at HEAD)

pending live-resolve confirmation of the Fenwick pay-to-play grounding URL

## Constraints honored

- stdlib only (hashlib, json, math, random)
- SEED=20260717, TRIALS=200000
- verifier copied byte-identically (diff exit 0)

## Gate plan

G1 in-band marginal-dollar return mean >= 2.0 -> G2 conversion/dilution ratio >= 1.5 -> G3 cold-market danger-band probability plus cold conversion/dilution ratio.

## Probe questions

pending — completed at flip

## Outcome

_Pending reproduction._

## ⟲ Previous-session review

pending

## 💡 Session idea

pending

**Recommendation: pending reproduction.**

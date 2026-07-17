# VERDICT 115 — the growth cash-trough trap: two subscription ventures with IDENTICAL positive per-customer unit economics (LTV=100 > CAC=60) differ ONLY in acquisition growth rate g, and because CAC is paid UPFRONT while margin accrues over the customer's lifetime, the faster grower has a strictly DEEPER cumulative-cash trough and higher ruin probability for equal starting capital — above a closed-form critical rate g_crit=CAC·s/(CAC−m) per-period cash flow is PERMANENTLY negative despite every customer being profitable, so "positive LTV/CAC, scale hard" is a ruin trap driven by cash TIMING, not unit economics (P102, +13)

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · low · review/verify

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the verdict artifacts + heartbeat.

## Objective
Reproduce idea-engine PROPOSAL 102 (outbox `## PROPOSAL 102 · 2026-07-17T23:24:36Z · status: sim-ready`, round-23 VENTURE slot), offset +13 (P102 → V115): on the pinned subscription-venture world, does the FASTER grower (g_high=1.30) have a strictly DEEPER cumulative-cash trough than the slower (g_low=1.05) despite IDENTICAL positive per-customer unit economics, and does the fluid-limit anchor MATCH? Run the DISCLOSED stdlib-only reference verifier (idea-engine `ideas/venture-lab/growth_cash_trough_trap.py`) VERBATIM under the pinned SEED=20260717, confirm all three pre-registered gates hold, and confirm the results-dict sha256 reproduces `5e6b4ce7cf3a58e6c5fa912ee5365ff4152c162818113320a8c2332195bc4d95`.

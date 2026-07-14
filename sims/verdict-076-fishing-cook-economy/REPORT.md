# VERDICT 076 — fishing cook-leg constants — REPORT

> **Status:** `complete`
> Source: superbot-games `## SIM-REQUEST · fishing-cook-economy · 2026-07-13` (filed 2026-07-13T18:18:29Z), read at packet pin `ed2fabbef58f3b97a03e6586a4e03ad0ab89c451`, status `open`; served in the VERDICT 075 batch per the roster request's fold-in clause.
> Ruling: **APPROVE-WITH-CONSTANTS — P\* = 12**, cook table {minnow 1, bass 1, pike 2, legend_carp 7} + roster extension rule; finding F-FLAT30.

## 1. What was asked

(a) a per-species COOKED value and (b) energy-restore constants + a pricing
guardrail simmed against the VERDICT 042 FAUCET-BYPASS boundary (rations
20→25 / drinks 40→50 = 0.8 coins/energy, below the faucet at every depth;
follow-up PROPOSAL 035 → VERDICT 046: NULL, admission cap seals only at
C = 60). The committed architecture collapses (a) into (b): cooked fish is a
CONSUMABLE, not sellable ("you sell the raw fish; you cook it for a meal
instead") — a cooked fish is worth ENERGY.

## 2. Answer to the request's premise (B0)

The claim "there are no cooked-value or energy-restore constants anywhere in
the repo" is **partially false at the pin**: `games/mining/core/energy.py`
carries a FLAT `"cooked fish": 30` (the legacy campfire meal). No per-species
constants exist. **F-FLAT30:** the flat 30 measured against the packet's own
resolver is a self-sustaining energy loop at EVERY cell of EVERY world —
ρ_flat = bite_rate × 30 / CAST_COST = 15 × bite_rate ≥ 4.5 by the packet's own
MIN_BITE_CHANCE floor (measured min 7.13, max 13.5): every 2-energy cast
returns 30 energy on ~half of casts. It MUST be superseded by the per-species
table before any fishing-haul cook op wires.

## 3. Method

Same packet discipline as V075 (16-file byte-copied closure, own MANIFEST
copy, re-verified; species tables injected as DATA; the packet's own
`resolve_cast` + equipment tiers). Catch streams are P-independent, so each
world is measured once (species counts per (spot,tier)) and the whole P grid
folds arithmetically — convention K1. Decision world **W4** = the committed
4-species surface (the one the request was filed against). Reporting world
**WR** = the V075 round-1 candidate 33-row table, embedded VERBATIM in the
registration (V075 ruled NULL — no decision gates on WR). Eval seeds
20261509–20261548, stability 20261549–20261558; **fleet high-water after this
PR: 20261558** (exactly as reserved in the V075 registration). CPython 3.11
asserted. Double run byte-identical — sha256 `run-stdout.txt`
`dd33ca3eba6198b1f3282d4d6b956feb37cb5b26758d1b90c414846ae7a1fa80`,
`results.json`
`92141587409fbe186a821c0e7e4563396911b5d9550c0ed3d0d88f0f0d56488e`.

## 4. The P sweep

Family: `E_s = max(1, round(S_s / P))`, P = the implied coins-per-energy price
of cooking (forgone sell value per energy point). Worst-cell ρ on W4 (bar 0.9):

| P | 6 | 8 | 10 | **12** | 14 | 16 | 20 | 24 | 28 |
|---|---|---|----|----|----|----|----|----|----|
| worst ρ (W4) | 1.500 | 1.216 | 0.985 | **0.815** | 0.758 | 0.701 | 0.531 | 0.474 | 0.474 |
| pass | ✗ | ✗ | ✗ (margin) | **✓** | ✓ | ✓ | ✓ | ✓ | ✓ |

P ≤ 8 is perpetual motion outright (ρ > 1); P = 10 clears 1.0 but not the 0.9
margin bar. Selector (smallest passing P, maximizing cooked energy subject to
safety) → **P\* = 12**: worst ρ 0.815 eval / **0.848 stability** (10 fresh
seeds, every cell ≤ 0.9 — the K6 gate held); min implied price 8.0
coins/energy ≥ the 0.8 shop boundary (C2 — cooking never widens the V042
bypass, it prices energy 10× above the flagged shop); P = 12 sits ABOVE the
V043 fishing faucet band top (10.20) and below the mining ceiling proxy
(13.48).

**Constants (wireable today, W4):** minnow 1 · bass 1 · pike 2 ·
legend_carp 7 cooked energy. **Extension rule** for any later-pinned roster
species: `E_s = max(1, round(S_s / 12))` — but the WR adversarial world
measures worst ρ 1.11 at P = 12, so the roster wave MUST re-derive P via this
same registered selector at its own pin (roster per-species values inherit
V075's NULL either way).

## 5. Choice-realness (C3 — split honestly)

Coin axis (arithmetic, at the mining ceiling 13.48 coins/energy): cook beats
sell for minnow (13.48 > 8), bass (13.48 > 13) and legend_carp (94.4 > 80);
pike is knife-edge dominated (26.96 < 27, by 0.04). At the fresh fishing
faucet (≈ 4.42) sell beats cook everywhere. So cook-vs-sell is a REAL,
context-dependent choice — rich-faucet players cook, fresh players sell —
while ρ < 1 keeps the loop non-exploitable at every cell. Time axis
(measured): a cooked fish skips `E_s × 10 s` of passive regen (legend_carp
70 s). The VALUE of immediacy and campfire shop-independence is
JUDGMENT-ONLY, labeled. Under the committed 0.8-shop, sell-then-buy-rations
still yields more energy per forgone coin — by design (the anti-bypass
direction); that comparison is V042's open intent call, not this verdict's.

## 6. Recommendations (for the manager to relay)

1. WIRE the per-species table VERBATIM: cook consumes the fish from the same
   haul the sell leg debits (the PR #83 exclusivity, V043 G4), restore =
   {minnow 1, bass 1, pike 2, legend_carp 7}; keep the restore data-driven off
   the species row (the Q-0267 shape) rather than a name-keyed flat map.
2. SUPERSEDE the flat `"cooked fish": 30` before any fishing-haul cook op
   lands (F-FLAT30 — perpetual motion at every measured cell); ration/drink
   rows are untouched (V042's open intent call).
3. If the V046 C = 60 admission-cap conditional ever lands, cooked fish
   should count INSIDE the same admission quantum (recommendation, not a
   wired constant).
4. Roster wave: re-run this registered selector at the roster's own pin
   (WR measured ρ 1.11 at P = 12 — P likely lands 14–16 there).

## 7. Self-checks & reproducibility

37 self-checks, 0 failed, exit 0. Registration committed BEFORE the runner;
first complete run = the accepted run; no fix-forwards. Hermetic, stdlib-only;
byte-identical double run (hashes § 3).

# VERDICT 164 — St. Petersburg cap-collapse — probe report (reproduction only)

PROPOSAL 151 → VERDICT 164 (+13), round-35 GAME slot. This report records the raw
reproduced numbers only. No APPROVE/REJECT verdict is made here.

## Identity
- Reproduced verifier: `sims/verdict-164-st-petersburg-cap/st_petersburg_cap_collapse.py`
- Source (byte-identical copy of): idea-engine `ideas/superbot-games/st_petersburg_cap_collapse.py`
  @ commit `ba785559380d6dee2478feb68b37eaf23e9b2d77` (PROPOSAL 151, idea-engine #609)
- File sha256: `55d4f9bca3b50dff0c0a30c8b5c1e02001aaca5d12779c422b4585b452cb0c76` (8990 bytes, 236 lines)
- Git blob: `36d66eb5c072d9a11cda215dd7fdbea24dbc9eec`
- Disclosed results-dict sha256 (P151 outbox done-when): `e1919f49d20df0b50121864b8e35f78be0637e4eeb812799e9f0d8af535ef078`
- Reproduced results-dict sha256: `e1919f49d20df0b50121864b8e35f78be0637e4eeb812799e9f0d8af535ef078` — **MATCH** (all 64 hex)

## Reproduction
- Run A (`SEED=20260717 python3 st_petersburg_cap_collapse.py`): exit code **0**
- Run B (separate process, same command): exit code **0**
- Cross-invocation byte-match (`diff run-stdout.txt /tmp/run-b.txt`): **YES** — byte-identical, diff exit 0
- In-process double-run determinism assert (`main()` builds the dict twice, `assert h1 == h2`):
  **PASSED** (did not raise; both invocations exited 0 and printed the digest). Both runs printed
  `Results-JSON sha256: e1919f49…5ef078`.
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY, P127+ compact-canonical twist (floats
  rounded 6 dp; the printed digest is over the compact sorted-keys/comma-colon serialization, not the
  pretty indent=2 stdout dump).

## Gates (as printed, order G1 → G2 → G3)
- **G1 finite_price_collapse:** z = **16496.525875** — **PASS**
  (nominal cap 2^12 = 4096; MC fair price 7.067918 vs half-cap 2048.0; closed_form 7.0)
- **G2 sublinear_scaling:** z = **1998.187697** — **PASS**
  (delta_measured 3.069885 vs delta_cap_proportional_pred 251.876047; log-rule anchor z_logrule 0.561254,
  delta_logrule_pred 3.0; m_lo 6 → m_hi 12)
- **G3 robust_under_shifted_coin:** z = **-1.000661** — **PASS**
  (shifted coin p=0.4 / r=2.5 / cap_bits 10; MC fair price 6.828497 vs closed_form 7.0; |z| ≤ 3 anchor;
  slope_per_bit_pred 0.6)
- all_pass = **true**, first_failing_gate = **null**, exit **0**

## Closed-form sanity (EV_cap formula vs Monte-Carlo)
Closed form on the critical curve p·r = 1: **EV_cap = (1−p)·M + 1**.

Nominal / fair-doubling world (p=0.5, r=2.0):
| M (cap-bits) | cap (r^M) | closed_form (1−p)·M+1 | MC mean | se | z_anchor |
|---|---|---|---|---|---|
| 6 | 64.0 | 4.0 | 3.998032 | 0.014066 | -0.139879 |
| 8 | 256.0 | 5.0 | 4.952937 | 0.029604 | -1.589759 |
| 10 | 1024.0 | 6.0 | 6.121433 | 0.063216 | 1.920911 |
| 12 | 4096.0 | 7.0 | **7.067918** | 0.123719 | 0.548966 |

- Nominal-world MC mean (M=12 cap 4096): **7.067918** vs closed form **7.0**.
- Cap-sweep increment (2^6 → 2^12): measured **3.069885** vs log-rule prediction **3.0**
  (anchor z 0.561254) vs cap-proportional prediction **251.876047**.

Shifted world (biased coin p=0.4, r=2.5, cap_bits 10, still on p·r = 1):
- MC price **6.828497** vs its closed form **7.0** (= (1−0.4)·10 + 1), z **-1.000661**, cap 9536.743164.

## Verdict: APPROVE — verifier byte-identical (sha256 55d4f9bc…), results-dict sha256 e1919f49… matches disclosed, deterministic (in-process double-run + cross-invocation byte-identical, exit 0); G1 z=16496.53 PASS, G2 z=1998.19 PASS, G3 z=-1.00 PASS; closed-form EV_cap=(1-p)M+1=7.0 consistent with MC (nominal 7.068, shifted 6.828).

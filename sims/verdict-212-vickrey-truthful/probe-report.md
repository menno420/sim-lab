# VERDICT 212 — Vickrey second-price auction, truthful bidding is weakly dominant: reproduce PROPOSAL 199

- **Slice:** VERDICT 212 · PROPOSAL 199 (P199 → V212, +13 offset)
- **Source proposal:** idea-engine PROPOSAL 199 — Vickrey second-price auction: truthful bidding `b = v` is a weakly dominant strategy; the shade `v·(n−1)/n` that strictly helps in first-price is useless in Vickrey (`ideas/superbot-games/vickrey-truthful-dominance-2026-07-20.md`)
- **Verifier (source):** idea-engine `ideas/superbot-games/vickrey-truthful-dominance-2026-07-20.py` (git blob `a3ccd070682205118a0c622dcf8243c543c0eafb`, origin/main `602f315`)
- **Reproduced by:** sim-lab session 2026-07-20-verdict-212-vickrey-truthful, HEAD-synced idea-engine `602f315` / sim-lab `f046440` (branch `claude/verdict-212`)
- **Timestamp (date -u):** 2026-07-20T06:06:48Z
- **SEED:** 20260717 · stdlib-only (`hashlib`, `json`, `math`, `random`, `fractions`, `itertools`) · Z_GATE=3.0

## Head

In a sealed-bid **second-price (Vickrey) auction** with `n` bidders, the highest
bidder wins the item but pays the **second-highest** bid. The claim: bidding your
true value `b = v` is a **weakly dominant strategy** — for EVERY profile of opponent
bids, no alternative bid earns strictly more, and some alternative bids earn strictly
less. The reason is structural: a winner's payment depends only on the *opponents'*
highest bid, never on the winner's own bid, so a bidder can only change *whether* they
win, never *what* they pay conditional on winning — and truthful bidding wins exactly
when winning is profitable (`v ≥ max_opp ⟹ v − max_opp ≥ 0`) and loses exactly when it
is not. The sharp, non-obvious contrast that makes the theorem non-vacuous: the
symmetric first-price equilibrium **shade** `s = v·(n−1)/n` (bidding strictly below
value) STRICTLY raises expected surplus in a *first-price* auction, but the SAME shade
is inert in Vickrey — it can only weakly LOWER surplus (by occasionally dropping a
profitable win), never raise it. Truthful dominance in Vickrey and profitable shading
in first-price are two faces of the same payment-rule difference.

## Reproduction

- **Verifier copy byte-identical:** `diff <idea-engine source> <sim-lab copy>` →
  **exit 0** (git blob `a3ccd070682205118a0c622dcf8243c543c0eafb` on both sides;
  `git hash-object` of the copy equals the source blob).
- **Ran under SEED=20260717**, full stdout captured to `run-stdout.txt`, process
  **exit 0** (`all_pass = True`).
- **Results-dict sha256 (compact-canonical, `json.dumps(d, sort_keys=True,
  separators=(",",":"))`):**
  - disclosed (PROPOSAL 199): `a96d59f378e5d04a4e211dafafa22244e09d22126ba2c9b1e5f1cc0bdeb6527c`
  - reproduced (this run):    `a96d59f378e5d04a4e211dafafa22244e09d22126ba2c9b1e5f1cc0bdeb6527c`
  - — **EXACT MATCH** across all **64** hex characters (byte-for-byte string equality,
    hex-char count = 64, no truncation). The verifier PRINTS this digest
    (`results_sha256: …`); an independent out-of-band recompute
    (`hashlib.sha256(canonical(build_results()).encode()).hexdigest()`) reproduces the
    same 64 hex, and two fresh cross-invocation runs are byte-identical — all agree.
- Digest posture: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the compact-canonical
  results dict's own sha256 IS the digest; it is not a field inside the dict.

## Determinism

- **In-process double-run** — `main()` calls `build_results()` twice and asserts
  `canonical(results_2) == canonical(results)`, exiting 3 with "NON-DETERMINISTIC:
  in-process double-run diverged" otherwise; the guard holds, exit 0. Each Monte-Carlo
  gate constructs a fresh `random.Random(SEED)` at entry, so the two builds draw the
  identical stream.
- **Separate cross-invocation** — two independent `python3` invocations produced
  byte-identical stdout, hence the identical results-dict sha256 `a96d59f…6527c`.

## Exact-arithmetic self-certification (the load-bearing evidence)

The two firsthand gates are not statistical estimates. **G1** is an EXHAUSTIVE
integer-exact enumeration: `g1_dominance` iterates over EVERY focal value `v ∈ [0,
val_max]` and EVERY opponent bid profile `opp ∈ [0, bid_max]^(n−1)`, and for each it
compares the truthful utility `vickrey_utility(v, v, opp)` against `vickrey_utility(b,
v, opp)` for EVERY alternative bid `b ∈ [0, bid_max]` — pure integer arithmetic, zero
sampling, zero float. `deviations_strictly_better` counts every `(profile, b)` where a
lie strictly beats truthful; a PASS requires this to be exactly `0`. **G2** is an
EXACT closed-form expectation in `fractions.Fraction` over the full value grid
(`(val_max+1)^n` profiles): `E[Δ firstprice]`, `E[Δ vickrey]`, and `E[truthful
first-price surplus]` are exact rationals, and the gate checks their signs
(`E_fp > 0 and E_vk <= 0 and E_tf == 0`) as exact-rational comparisons. G1's zero and
G2's `−27/343 ≤ 0` are self-certifying, independently re-checkable identities — this is
what makes the APPROVE clean; the G3/G4 z-scores corroborate but are not the primary
evidence.

## Gate evaluation (against PROPOSAL 199's OWN criteria, in order)

- **G1 — EXHAUSTIVE weak dominance (integer-exact; 0 strict deviations is the PASS):**
  config n=3, val_max=4, bid_max=6 → **245 profiles**. Truthful bidding `b = v`
  weakly dominates every alternative bid over the FULL grid:
  - `deviations_strictly_better = 0` (no lie ever strictly beats truthful),
  - `profiles_truthful_optimal = 245 / 245` (truthful is a best response on 100% of
    profiles),
  - `truthful_strictly_better_instances = 485 > 0` (NON-VACUOUS — truthful strictly
    beats some lie on a positive-measure set, so the dominance is weak-and-nontrivial,
    not a degenerate tie).
  **g1_pass = true.** *(core proof — the firsthand weak-dominance theorem)*
- **G2 — EXACT-EXPECTATION contrast (Fraction-exact closed form; sign match is the
  PASS):** config n=3, val_max=6 → **343 profiles**. The shade `s = v·(n−1)/n`:
  - `E[Δ firstprice] = +114/343 > 0` (float `+0.332362`) — shading STRICTLY helps in
    first-price in expectation,
  - `E[Δ vickrey] = −27/343 ≤ 0` (float `−0.078717`) — the SAME shade weakly HURTS in
    Vickrey in expectation,
  - `E[truthful first-price surplus] = 0/1` **EXACTLY** — the closed-form first-price
    truthful surplus is exactly zero (truthful first-price bidders capture no
    expected surplus at value = bid), the exact anchor the contrast is measured
    against.
  **g2_pass = true.**
- **G3 — MONTE-CARLO surprise (two-sided contrast; high z first-price, z≤0 Vickrey is
  the PASS):** config n=3, val_max=12, draws=200000, seed=20260717:
  - `z_firstprice = +192.175024 ≥ 3` — against truthful rivals the shade genuinely,
    significantly HELPS in first-price (a large positive z is the PASS on this side),
  - `z_vickrey = −155.312083 ≤ 0` — the SAME shade NEVER helps in Vickrey (a
    non-positive z is the PASS on this side).
  The PASS is the *contrast*: identical shade, opposite verdict by auction rule.
  **g3_pass = true.**
- **G4 — ROBUSTNESS / SHIFT (0 mismatches + persistent contrast is the PASS):** the
  dominance and the contrast survive grid/`n` shifts:
  - n=2 shift (val_max=6, bid_max=8, **63 profiles**): `deviations_strictly_better =
    0`, `profiles_truthful_optimal = 63/63`,
  - n=4 shift (val_max=3, bid_max=5, **864 profiles**): `deviations_strictly_better =
    0`, `profiles_truthful_optimal = 864/864`,
  - shifted Monte-Carlo (n=4, val_max=20, 200000 draws): `z_firstprice =
    +156.675416 ≥ 3`, `z_vickrey = −142.040465 ≤ 0`.
  The result is not an artifact of one `n` or one grid scale. **g4_pass = true.**

**all gates pass in order**, `all_pass = true`.

## Grounding

- **Source:** Wikipedia "Vickrey auction" oldid **1338833083**, raw wikitext
  (`index.php?title=Vickrey_auction&oldid=1338833083&action=raw`, MediaWiki API).
- **Fetch:** revision RESOLVES (raw wikitext, **12916 bytes**); raw-wikitext sha1
  `398d2e4148cc7ee83f1343f720f6e243926bb895` — **EXACT MATCH** to the disclosed pin
  (local `sha1sum` of the raw wikitext byte stream).
- **Content:** the revision contains the section **"== Proof of dominance of truthful
  bidding =="**, which proves that truthful bidding is weakly dominant in a
  second-price / Vickrey auction, working both cases — a bidder who **overbids** and a
  bidder who **underbids** relative to true value — and showing neither can strictly
  improve on truthful. This is exactly the head the verifier reproduces
  (G1's exhaustive weak dominance). **STRONG external byte-pinned grounding** — the
  pin resolves, the sha1 is byte-exact, and the pinned section states the theorem in
  full.

## Ruling evidence summary

Digest matches full-64 exact (`a96d59f…6527c`, printed `results_sha256:` +
independently recomputed + byte-identical across two cross-invocation runs, all agree,
64 hex no truncation); verifier byte-identical (`diff` exit 0, git blob `a3ccd07`);
deterministic (in-process double-run guard holds, exit 0). The load-bearing gates are
firsthand exact: **G1** is an EXHAUSTIVE integer enumeration with
`deviations_strictly_better = 0` over 245 profiles and truthful optimal on 245/245,
non-vacuous at 485 strict-improvement instances — a self-certifying proof that
truthful bidding weakly dominates; **G2** is an EXACT `Fraction` closed form giving
`E[Δ firstprice] = +114/343 > 0`, `E[Δ vickrey] = −27/343 ≤ 0`, and
`E[truthful first-price surplus] = 0/1` exactly. **G3** corroborates with a genuine
two-sided Monte-Carlo contrast (`z_firstprice = +192.18 ≥ 3`, `z_vickrey = −155.31 ≤
0`), and **G4** re-passes under n=2 (0/63), n=4 (0/864), and a shifted contrast
(`z_firstprice = +156.68`, `z_vickrey = −142.04`). Grounding resolves byte-exact
(Wikipedia "Vickrey auction" oldid 1338833083, raw-wikitext sha1
`398d2e4148cc7ee83f1343f720f6e243926bb895`) and the pinned "Proof of dominance of
truthful bidding" section states the theorem. Reproduces the disclosed digest
byte-for-byte, all four gates hold in their stated directions, strong byte-pinned
external grounding → **APPROVE**. Final ruling is the coordinator's: **APPROVE**.

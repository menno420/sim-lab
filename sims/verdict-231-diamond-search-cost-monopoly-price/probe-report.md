# VERDICT 231 — Probe report (reproduces PROPOSAL 218)

> With N identical zero-marginal-cost sellers and buyers who pay any strictly
> positive cost s to inspect one more price, the unique symmetric price
> equilibrium is the full monopoly (reservation) price v — for EVERY N and every
> s > 0. Adding competitors never lowers the price; the Bertrand descent to
> marginal cost never begins. The competitive outcome exists only at exactly zero
> friction (s = 0) — a discontinuity at zero search cost. Diamond's paradox.

- **Slice:** round-52, P218 → V231 (+13 offset)
- **Branch:** `claude/verdict-231-diamond-search-cost-monopoly-price`
- **Sim dir:** `sims/verdict-231-diamond-search-cost-monopoly-price/`
- **Source:** PROPOSAL 218 (idea-engine `ideas/venture-lab/diamond-search-cost-monopoly-price-2026-07-20.md`)
- **Ruling recommendation: APPROVE**

## 1. Verifier copy — byte-identical

`cp` of idea-engine `ideas/venture-lab/diamond-search-cost-monopoly-price-2026-07-20.py`
→ `sims/verdict-231-diamond-search-cost-monopoly-price/diamond-search-cost-monopoly-price.py`;
`diff` source ↔ copy exit **0** (byte-identical, sha256 `2ed1b427…0f02`). Stdlib-only. SEED = 20260717.

## 2. Digest — full-64 EXACT match

Ran the verifier (exit 0). Printed:

```
results_sha256=c71985cb55577757ed79772b3fabb7677611f3469531c10ab60f8e73a91d8036
```

- Disclosed target: `c71985cb55577757ed79772b3fabb7677611f3469531c10ab60f8e73a91d8036`
- Independent `grep -o` 64-char string compare → **MATCH** (exactly 64 hex, no truncation, bit-exact).
- Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the canonical-JSON sha256 of the full results dict IS the digest; the dict carries no self-hash. Human detail (the G2 z line) goes to stderr and is not digested.

## 3. Determinism — both legs hold

- **In-process double-run:** `main()` builds the results dict twice and asserts canonical-JSON equality before printing (exit 0).
- **Cross-invocation:** separate process invocations produced byte-identical stdout. No wall-clock or OS randomness.

## 4. Gates — four, all PASS in their own directions

| Gate | Direction | Observed | Pass |
|------|-----------|----------|------|
| **G1** EXACT unique equilibrium (Fraction) | unique symmetric equilibrium == monopoly price v, exhaustive best-response enumeration | 200/200 problems: eqs == [v] exactly | Yes |
| **G2** SURPRISE ≥3σ | equilibrium price rejects the marginal-cost folk claim; == v every market | z_reject_folk=100.551 (≥3σ); price==v in all 3000 markets (N up to 400) | Yes |
| **G3** ROBUSTNESS + discontinuity | equilibrium invariant to N & every s>0; monopoly price is eq iff s>0 | invariant 120/120; discontinuity (eq at s>0, NOT at s=0) 120/120 | Yes |
| **G4** identity + FALSIFIABILITY | industry profit == v (split v/N); folk Bertrand profile falsified; true profile deviation-free | industry==v 200/200; folk falsified 200/200; true no-deviation 200/200 | Yes |

`all_pass=true`. G1 is Fraction-exact exhaustive enumeration — with s≥1 the symmetric best response forces p=v. G3's discontinuity leg confirms an undercut to v−1 captures full mass at s=0 (profit v−1 > v/N for N≥2), destroying the monopoly equilibrium at zero friction. G4's falsifiability leg computes the best response against the folk all-at-0 profile (best price = s, profit s/N > 0) and confirms the marginal-cost profile is strictly NOT Nash.

**Adversarial notes (soft, do not change the ruling):** (1) G2's z=100.551 is a distance-of-mean-from-marginal-cost in SE units; its magnitude is inflated by M=3000 (z grows ~√M), so the number is somewhat theatrical — but it is genuine, correctly directed, and the airtight leg is the exact `price == v` on all 3000 markets. (2) G4's `industry==v` leg is near-definitional given `deviant_demand(v,v)=1/N`, but it is precisely the profit-split identity being asserted and is paired with a real-teeth Bertrand-profile falsification.

## 5. Grounding — byte-pinned, sha1 match; HONEST caveat

- Source: Wikipedia "Price dispersion", oldid **1345367307**, `action=raw` wikitext.
- Raw-wikitext sha1 = `930ead7d5a9ce98d5ae063c4cbfea4bf3315c63f` = disclosed pinned sha1, and equals MediaWiki's canonical rev sha1 via the API → **MATCH**.
- **On-page** (confirmed present, qualitative): "Diamond's paradox" (Diamond 1971); each firm acting as a monopoly on its share choosing the "monopoly price"; the Bertrand marginal-cost limit ("prices … equal to marginal costs … as in a Bertrand economy").
- **Off-page** (correctly absent, and the caveat says so): the discrete-grid exact unique-equilibrium enumeration, the explicit N/s-invariance, and the monopoly-profit-split identity (v/N per seller, industry == v) with the Bertrand-profile falsification — none are computed on the page; they are the verifier's firsthand work.
- **Title fallback legitimate:** the title `Diamond_paradox` genuinely does not exist on Wikipedia (API returns `missing`, no redirect, no disambiguation), so grounding on "Price dispersion" (whose Diamond's-paradox section carries the mechanism) is a legitimate fallback.

### Grounding-accuracy assessment
The caveat is **honest** — neither oversold nor undersold. It does not oversell (it explicitly does NOT claim the page computes the three firsthand legs) and does not undersell (it acknowledges the page genuinely states Diamond's paradox and both endpoints qualitatively). Clean separation of firsthand-proven result from cited motivation; no mis-description forces a qualification.

## 6. Ruling

**APPROVE.** Byte-identical verifier copy (diff exit 0); results-dict sha256 full-64 EXACT match (bit-exact, no truncation); determinism holds on both the in-process double-run and separate cross-invocations; all four pre-registered gates pass in their own directions with the folk marginal-cost profile correctly falsified; grounding sha1 matches the pinned revision with the on-page mechanism present and the three exact legs honestly disclosed as firsthand. The soft notes (G2's M-inflated z; G4's near-definitional identity leg) do not undermine the core claim and do not force a qualification.

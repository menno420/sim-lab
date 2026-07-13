#!/usr/bin/env python3
"""VERDICT 045 — exploration reward bands (idea-engine ORDER 006 item 7).

(a) reconcile quest-catalog TIER_CAPS against the superbot Q-0087 dual-track
    bands (band DEFINITIONS + V018/V033 contracts; the numeric band import is
    the registered honest NULL — no upstream constants exist, D-0008);
(b) ratify/tune the survival Medium/Hard gradient vs the Easy ≡ mining-bar
    anchor (D-0004) under pre-registered play profiles.

Rung 1 numeric simulation. Every decision-bearing number is EXACT (integer /
Fraction) arithmetic over the byte-copied pinned modules, or produced by the
packet's OWN survival harness driven through its public run() entry point.
ZERO decision-bearing RNG; zero registry seed draws (fleet high-water 20261280
untouched). stdlib-only, hermetic: reads only ./fixtures.json + ./engine.

Run:  python3 sims/verdict-045-exploration-bands/exploration_bands_sim.py
Exit 0 with "SELF-CHECKS: N passed, 0 failed" on success; exit 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True  # keep the byte-copied engine tree pristine

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engine"
sys.path.insert(0, str(ENGINE))

FIXTURES = json.loads((HERE / "fixtures.json").read_text())

_PASS = 0
_FAIL: list[str] = []


def sc(name: str, ok: bool, detail: str = "") -> None:
    """Self-check: count, and record failures loudly."""
    global _PASS
    if ok:
        _PASS += 1
    else:
        _FAIL.append(name)
        print(f"SELF-CHECK FAIL: {name} {detail}")


def frac_str(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# B0 — validity gate (replicated in-process; b0_check.py is the standalone)
# ---------------------------------------------------------------------------

def b0() -> None:
    manifest = json.loads((ENGINE / "MANIFEST.json").read_text())
    for rel, want in manifest["files"].items():
        got = hashlib.sha256((ENGINE / rel).read_bytes()).hexdigest()
        sc(f"B0.0 sha256 {rel}", got == want)

    from games.exploration.quest import catalog
    from games.exploration.quest.models import RewardBundle, RewardTier
    from games.exploration.survival.difficulty import TUNABLES, Difficulty
    from games.mining.core import energy

    want_caps = {"I": (5, 25, 10), "II": (10, 60, 25), "III": (20, 120, 50)}
    for tier in RewardTier:
        b = catalog.TIER_CAPS[tier]
        sc(
            f"B0.1 TIER_CAPS[{tier.value}]",
            (b.global_xp, b.game_xp, b.currency, b.capability)
            == (*want_caps[tier.value], None),
        )
    gm = catalog.GLOBAL_MAX
    sc("B0.2 GLOBAL_MAX", (gm.global_xp, gm.game_xp, gm.currency) == (20, 120, 50))
    doc = catalog.__doc__ or ""
    sc(
        "B0.3 placeholder note verbatim",
        "the exact superbot Q-0087 dual-track band constants were not\n"
        "sourced into this repo" in doc,
    )
    sc(
        "B0.3 play-only capability line",
        "Capability\nunlocks are play-only (tier III completion), never bought "
        "with currency" in doc,
    )
    want_tun = {"easy": (60, 10, 1), "medium": (50, 15, 1), "hard": (40, 20, 1)}
    for d in Difficulty:
        t = TUNABLES[d]
        sc(
            f"B0.4 TUNABLES[{d.value}]",
            (t.max_energy, t.regen_seconds, t.cost) == want_tun[d.value],
        )
    easy = TUNABLES[Difficulty.EASY]
    sc(
        "B0.4 Easy ≡ mining bar by import (D-0004)",
        (easy.max_energy, easy.regen_seconds, easy.cost)
        == (energy.MAX_ENERGY, energy.REGEN_SECONDS, energy.DIG_COST),
    )
    sc(
        "B0.5 mining bar (60,10,1)",
        (energy.MAX_ENERGY, energy.REGEN_SECONDS, energy.DIG_COST) == (60, 10, 1),
    )
    sc(
        "B0.6 RewardBundle fields",
        tuple(RewardBundle.__dataclass_fields__)
        == ("global_xp", "game_xp", "currency", "capability"),
    )
    msrc = (ENGINE / "games/exploration/quest/models.py").read_text()
    sc(
        "B0.7 tier semantics casual/standard/prestige",
        'I = "I"  # casual' in msrc
        and 'II = "II"  # standard' in msrc
        and 'III = "III"  # prestige' in msrc,
    )


# ---------------------------------------------------------------------------
# Part (a) — TIER_CAPS vs the Q-0087 band definitions + V018/V033 contracts
# ---------------------------------------------------------------------------

def part_a() -> dict:
    from games.exploration.quest import catalog
    from games.exploration.quest.models import RewardTier

    caps = {
        t.value: (
            catalog.TIER_CAPS[t].global_xp,
            catalog.TIER_CAPS[t].game_xp,
            catalog.TIER_CAPS[t].currency,
        )
        for t in RewardTier
    }
    gm = (catalog.GLOBAL_MAX.global_xp, catalog.GLOBAL_MAX.game_xp,
          catalog.GLOBAL_MAX.currency)

    # S1 in-band
    s1 = all(all(caps[t][i] <= gm[i] for i in range(3)) for t in caps)
    sc("S1 every tier <= GLOBAL_MAX component-wise", s1)
    # S2 strict monotone
    s2 = all(caps["I"][i] < caps["II"][i] < caps["III"][i] for i in range(3))
    sc("S2 strict component-wise monotone I < II < III", s2)
    # S3 ceiling binds
    s3 = caps["III"] == gm
    sc("S3 GLOBAL_MAX == TIER_CAPS[III] exactly", s3)
    # S4 V033 consistency — exact re-derivation of the published farmer ceilings
    K, B, HOURS = 4, 3, 8
    farmer_completions_per_hr = Fraction((K * HOURS) // B, HOURS)  # floor(32/3)/8
    farmer_ii = farmer_completions_per_hr * caps["II"][2]
    farmer_iii = farmer_completions_per_hr * caps["III"][2]
    sc("S4 farmer ceiling II == 125/4 (31.25/hr, V033)", farmer_ii == Fraction(125, 4))
    sc("S4 farmer ceiling III == 125/2 (62.50/hr, V033)", farmer_iii == Fraction(125, 2))
    honest_ceiling = Fraction(3031, 100)  # V033's published measured 30.31/hr
    sc("S4 honest 30.31 <= farmer 31.25", honest_ceiling <= farmer_ii)
    sc(
        "S4 farmer/honest <= ARB_RATIO_MAX 2.0",
        farmer_ii / honest_ceiling <= Fraction(2),
    )
    s4 = (farmer_ii == Fraction(125, 4) and farmer_iii == Fraction(125, 2)
          and honest_ceiling <= farmer_ii
          and farmer_ii / honest_ceiling <= 2)

    # C1a/C1b — registered casual profiles (exact)
    r_e_per_hr = 12  # V033's honest quest-focused attempt rate
    cas_a_beats_per_day = r_e_per_hr * 15 // 60          # 3
    cas_a_completions_per_day = cas_a_beats_per_day // B  # 1
    cas_a_daily = tuple(c * cas_a_completions_per_day for c in caps["I"])
    cas_a_weekly = tuple(7 * v for v in cas_a_daily)
    cas_b_beats_per_day = r_e_per_hr * 10 // 60          # 2
    cas_b_completions_per_week = (7 * cas_b_beats_per_day) // B  # floor(14/3)=4
    cas_b_weekly = tuple(c * cas_b_completions_per_week for c in caps["I"])
    sc("C1a CAS_A daily grant strictly positive", all(v > 0 for v in cas_a_daily))
    sc("C1a CAS_B weekly grant strictly positive", all(v > 0 for v in cas_b_weekly))
    sc("pred CAS_A daily == (5,25,10)", cas_a_daily == (5, 25, 10))
    sc("pred CAS_A weekly == (35,175,70)", cas_a_weekly == (35, 175, 70))
    sc("pred CAS_B weekly == (20,100,40)", cas_b_weekly == (20, 100, 40))
    c1b = cas_a_weekly[0] >= gm[0] and cas_b_weekly[0] >= gm[0]
    sc("C1b casual weekly global_xp >= GLOBAL_MAX.global_xp (20)", c1b,
       f"CAS_A {cas_a_weekly[0]}, CAS_B {cas_b_weekly[0]} vs {gm[0]}")
    # C1c — couples (a) to (b): the casual quest day never energy-blocks on Hard
    from games.exploration.survival.difficulty import TUNABLES, Difficulty
    hard = TUNABLES[Difficulty.HARD]
    casual_day_energy = cas_a_beats_per_day * hard.cost  # 3 * 1
    hard_burst = hard.max_energy // hard.cost            # 40
    c1c = casual_day_energy <= hard_burst
    sc("C1c casual day energy (3) <= Hard burst (40)", c1c)

    # C2 capability-per-currency non-increasing
    cpc = [Fraction(caps[t][0], caps[t][2]) for t in ("I", "II", "III")]
    c2 = cpc[0] >= cpc[1] >= cpc[2]
    sc("C2 global_xp/currency non-increasing (1/2, 2/5, 2/5)", c2, str(cpc))
    sc("pred capability_per_currency == [1/2, 2/5, 2/5]",
       cpc == [Fraction(1, 2), Fraction(2, 5), Fraction(2, 5)])
    gxp = [Fraction(caps[t][1], caps[t][0]) for t in ("I", "II", "III")]
    sc("pred game_xp/global_xp == [5, 6, 6]",
       gxp == [Fraction(5), Fraction(6), Fraction(6)])

    # C3 capability play-only (structural: no bundle grants capability; B0.3 text)
    from games.exploration.quest import catalog as _cat
    c3 = all(_cat.TIER_CAPS[t].capability is None for t in RewardTier)
    sc("C3 no TIER_CAPS bundle grants capability", c3)

    # R1 reporting: grinder surplus/day vs casual (currency axis)
    r1 = {
        f"h={h}": {
            "honest_grinder_currency_per_day_ceiling": float(honest_ceiling * h),
            "cas_a_currency_per_day": cas_a_daily[2],
        }
        for h in (1, 2, 4, 8)
    }
    # R2 reporting: weekly capability-gap ratio table = 7*h*g*global_xp[tier]/35
    gap_table = {}
    for tier in ("II", "III"):
        for g_label, g in (("0.5", Fraction(1, 2)), ("1", Fraction(1)),
                           ("1.25", Fraction(5, 4)), ("2", Fraction(2))):
            for h in (1, 2, 4, 8):
                ratio = Fraction(7 * h * caps[tier][0], cas_a_weekly[0]) * g
                gap_table[f"tier{tier} g={g_label}/hr h={h}h/day"] = frac_str(ratio)
    sc("R2 identity: tier III ratio == 4*h*g at h=4,g=1.25 (== 20)",
       Fraction(gap_table["tierIII g=1.25/hr h=4h/day"].split("/")[0],) /
       Fraction(gap_table["tierIII g=1.25/hr h=4h/day"].split("/")[1] or 1)
       == Fraction(20) if "/" in gap_table["tierIII g=1.25/hr h=4h/day"]
       else Fraction(gap_table["tierIII g=1.25/hr h=4h/day"]) == 20)

    # Decision rule (registered order)
    structural_ok = s1 and s2 and s3 and s4
    d0_ok = (all(v > 0 for v in cas_a_daily) and all(v > 0 for v in cas_b_weekly)
             and c1b and c1c and c2 and c3)
    if not structural_ok or not d0_ok:
        ruling = "TUNE"
    else:
        ruling = "RATIFY-AS-PLACEHOLDERS + HONEST-NULL(numeric-band-import)"
    sc("RULE-A3 fired (all S + C pass)", ruling.startswith("RATIFY"))

    return {
        "ruling": ruling,
        "tier_caps": caps,
        "global_max": gm,
        "structural": {"S1": s1, "S2": s2, "S3": s3, "S4": s4},
        "d0_checks": {
            "C1a_cas_a_daily": cas_a_daily,
            "C1a_cas_b_weekly": cas_b_weekly,
            "C1b_pass": c1b,
            "C1c_pass": c1c,
            "C2_capability_per_currency": [frac_str(x) for x in cpc],
            "C3_pass": c3,
        },
        "v033_rederived": {
            "farmer_ceiling_II_currency_per_hr": frac_str(farmer_ii),
            "farmer_ceiling_III_currency_per_hr": frac_str(farmer_iii),
            "honest_published_ceiling_currency_per_hr": "30.31 (V033 measured, quoted)",
            "farmer_over_honest": f"{float(farmer_ii / honest_ceiling):.4f} <= 2.0",
        },
        "honest_null": (
            "the numeric-band import half of ask (a): NO canonical Q-0087 band "
            "constants exist in superbot @ 6d81488 (the bands are the future "
            "survival P0 harness's pinned outputs; D-0008) — reconciliation "
            "re-opens against the shipped capability-gap table when that "
            "artifact lands; the 'diminishing' half of curve 2 is likewise "
            "unscoreable from flat per-completion caps (host-gate property, G2)"
        ),
        "R1_grinder_surplus_reporting": r1,
        "R2_capability_gap_table": gap_table,
    }


# ---------------------------------------------------------------------------
# Part (b) — survival Medium/Hard gradient
# ---------------------------------------------------------------------------

def leg_b1() -> dict:
    """Drive the packet's OWN harness through run() — zero edits."""
    from games.exploration.survival import sim as ssim
    from games.exploration.survival.difficulty import Difficulty

    rep1 = ssim.run(seeds=range(400))
    rep2 = ssim.run(seeds=range(400))
    sc("GB1 harness deterministic (two in-process runs equal)", rep1 == rep2)

    pins_sustained = {"easy": 360, "medium": 240, "hard": 180}
    pins_burst = {"easy": 60, "medium": 50, "hard": 40}
    pred_grind8h = {"easy": 2940, "medium": 1970, "hard": 1480}
    out = {}
    for d in Difficulty:
        s = rep1.stats(d)
        sc(f"GB1 sustained[{d.value}] == {pins_sustained[d.value]}",
           s.sustained_digs_per_hour == pins_sustained[d.value],
           f"got {s.sustained_digs_per_hour}")
        sc(f"GB1 burst[{d.value}] == {pins_burst[d.value]}",
           s.burst_capacity == pins_burst[d.value], f"got {s.burst_capacity}")
        sc(f"GB1 casual_per_day[{d.value}] == 30", s.casual_per_day == 30,
           f"got {s.casual_per_day}")
        sc(f"GB1 grinder_8h[{d.value}] == {pred_grind8h[d.value]} (closed form)",
           s.grinder_8h == pred_grind8h[d.value], f"got {s.grinder_8h}")
        sc(f"GB1 capability_gap[{d.value}] == grinder_8h/casual",
           s.capability_gap == s.grinder_8h / s.casual_per_day)
        out[d.value] = {
            "sustained_per_hr": s.sustained_digs_per_hour,
            "burst": s.burst_capacity,
            "casual_per_day": s.casual_per_day,
            "grinder_8h": s.grinder_8h,
            "capability_gap": s.capability_gap,
        }
    return out


def leg_b2() -> dict:
    """Registered attempt-paced profiles on the byte-copied engine. NO RNG."""
    from games.exploration.survival.difficulty import TUNABLES, Difficulty
    from games.mining.core import energy
    from games.mining.core.energy import EnergyState

    profiles = FIXTURES["part_b_survival_gradient"]["registered_play_profiles"]
    out: dict[str, dict] = {}
    for pname, p in profiles.items():
        spacing = p["attempt_spacing_seconds"]
        attempts = p["attempts"]
        sc(f"{pname} attempts == session/spacing",
           attempts == p["session_seconds"] // spacing)
        out[pname] = {}
        for d in Difficulty:
            t = TUNABLES[d]
            state = EnergyState(t.max_energy, 0)
            completed = refused = 0
            first_refusal = None
            for k in range(attempts):
                now = k * spacing
                if energy.can_dig(state, now, cost=t.cost,
                                  max_energy=t.max_energy,
                                  regen_seconds=t.regen_seconds):
                    state = energy.spend(state, now, cost=t.cost,
                                         max_energy=t.max_energy,
                                         regen_seconds=t.regen_seconds)
                    completed += 1
                else:
                    refused += 1
                    if first_refusal is None:
                        first_refusal = now
            rf = Fraction(refused, attempts)
            out[pname][d.value] = {
                "attempted": attempts,
                "completed": completed,
                "refused": refused,
                "refusal_fraction": frac_str(rf),
                "refusal_fraction_float": float(rf),
                "tier_I_completions_proxy_B3": completed // 3,
                "time_to_first_refusal_s": first_refusal,
            }
    return out


def part_b(b1: dict, b2: dict) -> dict:
    # GB2 casual immunity
    gb2 = True
    for pname in ("P-CAS-10", "P-CAS-15", "P-REG-60"):
        for d in ("easy", "medium", "hard"):
            cell = b2[pname][d]
            ok = cell["refused"] == 0 and cell["completed"] == cell["attempted"]
            gb2 = gb2 and ok
            sc(f"GB2 {pname} zero refusals on {d}", ok,
               f"completed {cell['completed']}/{cell['attempted']}")

    # GB3 orders
    sus = {d: b1[d]["sustained_per_hr"] for d in ("easy", "medium", "hard")}
    gb3 = sus["easy"] > sus["medium"] > sus["hard"]
    sc("GB3 sustained strictly decreasing E>M>H", gb3)
    sat = {d: b2["P-SAT-480"][d]["completed"] for d in ("easy", "medium", "hard")}
    ok = sat["easy"] > sat["medium"] > sat["hard"]
    gb3 = gb3 and ok
    sc("GB3 P-SAT-480 completed strictly decreasing E>M>H", ok, str(sat))
    satr = {d: b2["P-SAT-480"][d]["refusal_fraction_float"]
            for d in ("easy", "medium", "hard")}
    ok = satr["easy"] < satr["medium"] < satr["hard"]
    gb3 = gb3 and ok
    sc("GB3 P-SAT-480 refusal strictly increasing E<M<H", ok, str(satr))
    grdr = {d: b2["P-GRD-240"][d]["refusal_fraction_float"]
            for d in ("easy", "medium", "hard")}
    ok = grdr["easy"] < grdr["medium"] < grdr["hard"] and grdr["easy"] == 0.0
    gb3 = gb3 and ok
    sc("GB3 P-GRD-240 refusal strictly increasing, Easy exactly 0", ok, str(grdr))

    # closed-form prediction bands (±1) on the two saturating profiles
    preds = {
        ("P-GRD-240", "easy"): 1440, ("P-GRD-240", "medium"): 1009,
        ("P-GRD-240", "hard"): 759,
        ("P-SAT-480", "easy"): 2939, ("P-SAT-480", "medium"): 1969,
        ("P-SAT-480", "hard"): 1479,
    }
    for (pname, d), want in preds.items():
        got = b2[pname][d]["completed"]
        sc(f"pred {pname} {d} completed == {want} ± 1", abs(got - want) <= 1,
           f"got {got}")

    # GB4 magnitude
    me = Fraction(sus["medium"], sus["easy"])
    he = Fraction(sus["hard"], sus["easy"])
    hm = Fraction(sus["hard"], sus["medium"])
    gb4 = (Fraction(55, 100) <= me <= Fraction(80, 100)
           and Fraction(40, 100) <= he <= Fraction(60, 100)
           and Fraction(60, 100) <= hm <= Fraction(90, 100))
    sc("GB4 sustained M/E == 2/3 in [0.55,0.80]", me == Fraction(2, 3), frac_str(me))
    sc("GB4 sustained H/E == 1/2 in [0.40,0.60]", he == Fraction(1, 2), frac_str(he))
    sc("GB4 sustained H/M == 3/4 in [0.60,0.90]", hm == Fraction(3, 4), frac_str(hm))
    sat_me = Fraction(sat["medium"], sat["easy"])
    sat_he = Fraction(sat["hard"], sat["easy"])
    ok = abs(sat_me - me) <= Fraction(5, 100) and abs(sat_he - he) <= Fraction(5, 100)
    gb4 = gb4 and ok
    sc("GB4 P-SAT-480 ratios within ±0.05 of sustained ratios", ok,
       f"M/E {float(sat_me):.4f} vs {float(me):.4f}; H/E {float(sat_he):.4f} vs {float(he):.4f}")

    # GB5 honest quest loop never bound
    r_e = 12  # beats/hr, V033 honest
    crossover = {d: sus[d] for d in sus}  # beats/hr where energy would bind
    ok = all(r_e * 15 <= crossover[d] * 15 and r_e <= crossover[d] for d in crossover)
    headroom = Fraction(crossover["hard"], r_e)
    gb5 = r_e <= crossover["hard"] and headroom >= 15
    sc("GB5 honest r_E=12/hr <= Hard sustained 180/hr with >=15x headroom",
       gb5, f"headroom {frac_str(headroom)}")

    gb0 = True  # asserted in B0.4 (Easy ≡ mining bar by import)
    gb1 = not any(f.startswith("GB1") for f in _FAIL)
    ruling = ("RATIFY" if (gb0 and gb1 and gb2 and gb3 and gb4 and gb5)
              else ("NULL-INVALID" if not gb1 else "TUNE"))
    sc("RULE-B3 fired (GB0-GB5 all pass)", ruling == "RATIFY")

    # R4 reporting: difficulty-independent boosters, refill share per difficulty
    from games.mining.core import energy as _e
    r4 = {
        item: {d: f"{val}/{cap} of the bar"
               for d, cap in (("easy", 60), ("medium", 50), ("hard", 40))}
        for item, val in _e.RESTORE_VALUES.items()
    }

    return {
        "ruling": ruling,
        "gradient_ratios_sustained": {
            "medium_over_easy": frac_str(me),
            "hard_over_easy": frac_str(he),
            "hard_over_medium": frac_str(hm),
        },
        "crossover_beats_per_hr_where_energy_binds": crossover,
        "R3_superbot_d1_draft_note": (
            "historical D1 draft Energy row (Medium cap 10 / regen ~10/hr, "
            "Hard cap 5) was re-baselined by D-0004 — the shipped gradient is "
            "5x-8x more generous and anchored to the shipped mining bar; "
            "context only, not the reconciliation target"
        ),
        "R4_booster_refill_share_by_difficulty": r4,
    }


# ---------------------------------------------------------------------------

def main() -> int:
    print("VERDICT 045 — exploration reward bands (ORDER 006 item 7)")
    print("=" * 72)
    print("\n[B0] validity gate")
    b0()
    if _FAIL:
        print(f"\nB0 FAILED — NULL-INVALID. {_FAIL}")
        return 1

    print("\n[A] TIER_CAPS vs Q-0087 band definitions + V018/V033 contracts")
    a = part_a()
    print(f"  ruling (a): {a['ruling']}")
    print(f"  tier caps: {a['tier_caps']}  GLOBAL_MAX: {a['global_max']}")
    print(f"  V033 re-derived: {a['v033_rederived']}")
    print(f"  CAS_A daily {a['d0_checks']['C1a_cas_a_daily']} · weekly "
          f"global_xp 35 >= 20 · CAS_B weekly {a['d0_checks']['C1a_cas_b_weekly']}")
    print(f"  capability/currency: {a['d0_checks']['C2_capability_per_currency']}")

    print("\n[B1] packet's own survival harness (run(seeds=range(400)))")
    b1 = leg_b1()
    for d, row in b1.items():
        print(f"  {d:<7} sustained {row['sustained_per_hr']:>4}/hr  burst "
              f"{row['burst']:>3}  casual/day {row['casual_per_day']:>3}  "
              f"grind8h {row['grinder_8h']:>5}  gap {row['capability_gap']:.2f}")

    print("\n[B2] registered profile sweep (deterministic, NO RNG)")
    b2 = leg_b2()
    for pname, per_d in b2.items():
        cells = "  ".join(
            f"{d}: {c['completed']}/{c['attempted']} "
            f"(refused {c['refused']}, {c['refusal_fraction_float']:.3f})"
            for d, c in per_d.items()
        )
        print(f"  {pname:<10} {cells}")

    print("\n[B] gradient ruling")
    b = part_b(b1, b2)
    print(f"  ruling (b): {b['ruling']}")
    print(f"  sustained ratios: {b['gradient_ratios_sustained']}")

    results = {
        "verdict": "VERDICT 045",
        "part_a": a,
        "part_b": {"harness_leg_B1": b1, "profile_leg_B2": b2, **b},
        "self_checks": {"passed": _PASS + (0 if _FAIL else 1), "failed": len(_FAIL)},
        "seed_policy": FIXTURES["registration"]["seed_policy"],
    }

    print()
    ok = not _FAIL
    # the final self-check: the run itself completed with zero failures
    print(f"SELF-CHECKS: {_PASS + (1 if ok else 0)} passed, {len(_FAIL)} failed")
    if not ok:
        print(f"FAILED: {_FAIL}")
        return 1

    (HERE / "results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True, default=str) + "\n"
    )
    print("results.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())

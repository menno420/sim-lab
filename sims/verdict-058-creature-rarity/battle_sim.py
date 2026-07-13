#!/usr/bin/env python3
"""VERDICT 058 — creature-PvP rarity vs skill (idea-engine PROPOSAL 047).

Prices superbot's committed level-normalized creature-PvP ruleset
(disbot/utils/creatures/battle.py @ 1cc553651a19016a4b1439f048b49e7baa28dfb1)
on its own never-cross-rarity-tested promise: can a MAX-SKILL Common team
counter THE committed all-Epic team at the engine's own normalized level?

Arm S (the DECISION arm, seeded MC): random.Random(20261325), the 9-cell
composition x pilot grid at N = 20,000 battles/cell, W(cell) = P(Common side
wins) as an exact fractions.Fraction; reporting legs (mirror / naive-vs-naive
/ Rare gradient) on the same stream; stability leg seed 20261326; sensitivity
legs seed 20261327 (reporting-only); aux seed 20261328 never read.
Arm E (exact stakes arm, seedless Fractions): expected-encounter cost of the
committed catch economy by max-min inclusion-exclusion + a subset-Markov twin,
output E_epic / E_common / TP.

Hermetic: reads ONLY its own fixtures.json (committed before this runner).
Stdlib-only, deterministic; stdout + results.json byte-identical across two
process runs (no wall-clock in any output). CPython 3.11 pinned (asserted).
The engine is re-implemented verbatim from the quoted constants/formulas —
zero imports from superbot.
"""

from __future__ import annotations

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
FX = json.load(open(os.path.join(HERE, "fixtures.json"), encoding="utf-8"))

# ---------------------------------------------------------------------------
# self-check machinery
# ---------------------------------------------------------------------------

_CHECKS = {"passed": 0, "failed": 0}
_FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        _FAILURES.append(label)
        print(f"CHECK FAILED: {label}")


def frs(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# pinned CPython minor
# ---------------------------------------------------------------------------

check(
    f"{sys.version_info.major}.{sys.version_info.minor}" == FX["cpython_minor_pin"],
    "cpython minor pinned 3.11",
)

# ---------------------------------------------------------------------------
# engine re-implementation (verbatim from the quoted constants @ 1cc5536)
# ---------------------------------------------------------------------------

CYCLE = tuple(FX["element_cycle"])
EIDX = {el: i for i, el in enumerate(CYCLE)}
STRONG = FX["strong_mult"]
WEAK = FX["weak_mult"]
NEUTRAL = FX["neutral_mult"]
NORMAL_TYPE = FX["normal_type"]


def effectiveness(attack_type: str, defender_element: str) -> float:
    if attack_type == NORMAL_TYPE:
        return NEUTRAL
    a = EIDX.get(attack_type)
    d = EIDX.get(defender_element)
    if a is None or d is None:
        return NEUTRAL
    delta = (d - a) % 6
    if delta in (1, 2):
        return STRONG
    if delta in (4, 5):
        return WEAK
    return NEUTRAL


RARITY_BUDGET = FX["rarity_budget"]
ARCH_W = {k: tuple(v) for k, v in FX["archetype_weights"].items()}
NORMAL_POWER = FX["moves"]["normal_power"]
ELEMENT_POWER = FX["moves"]["element_power"]
BUFF_STEP = FX["moves"]["buff_step"]
HP_PER_LVL = FX["level_scaling"]["hp_per_lvl"]
OFF_PER_LVL = FX["level_scaling"]["off_per_lvl"]
LEVEL_50 = FX["level_scaling"]["normalized_level"]
STALL_GUARD = FX["battle_rules"]["stall_guard"]
EXP_CONST = FX["expected_damage_constant"]

CATALOG = {name: tuple(row) for name, row in FX["catalog_rows_verbatim"].items()}


def derive_stats(rarity: str, archetype: str) -> tuple[int, int, int, int]:
    """Verbatim float replication of battle.py derive_stats (banker's rounding)."""
    budget = RARITY_BUDGET[rarity]
    hp_w, atk_w, df_w, spd_w = ARCH_W[archetype]
    total = hp_w + atk_w + df_w + spd_w
    return (
        round(budget * hp_w / total),
        round(budget * atk_w / total),
        round(budget * df_w / total),
        round(budget * spd_w / total),
    )


# --- F1: effectiveness hand table -----------------------------------------

for atype in list(CYCLE) + [NORMAL_TYPE]:
    row = FX["effectiveness_hand_table_F1"][atype]
    for j, del_el in enumerate(CYCLE):
        check(
            effectiveness(atype, del_el) == row[j],
            f"F1 effectiveness {atype} vs {del_el} == {row[j]}",
        )

# --- F2: derived-stat quadruples (the six used pairs) ----------------------

for key, pinned in FX["derived_stats_gate_F2"].items():
    if key.startswith("_"):
        continue
    rarity, arche = key.split("/")
    got = derive_stats(rarity, arche)
    check(list(got) == pinned, f"F2 derived stats {key} == {pinned} (got {list(got)})")
check(
    sum(derive_stats("Epic", "tank")) == FX["epic_tank_total_overshoot"],
    "F2 tank-Epic total 301 (the committed overshoot)",
)
check(
    Fraction(RARITY_BUDGET["Epic"], RARITY_BUDGET["Common"]) == Fraction(3, 2),
    "F5 RARITY_BUDGET spread 300/200 == 3/2 exact",
)

# --- F3: level-50 identities ------------------------------------------------

hp_mult_50 = 1 + HP_PER_LVL * (LEVEL_50 - 1)
off_mult_50 = 1 + OFF_PER_LVL * (LEVEL_50 - 1)
check(hp_mult_50 == FX["level_scaling"]["gate_F3"]["hp_mult_at_50"], "F3 HP mult 3.94 exact")
check(off_mult_50 == FX["level_scaling"]["gate_F3"]["off_mult_at_50"], "F3 off mult 2.715 exact")
check(
    round(derive_stats("Common", "balanced")[0] * hp_mult_50)
    == FX["level_scaling"]["gate_F3"]["balanced_common_max_hp_at_50"],
    "F3 balanced Common max_hp 197",
)
check(
    round(derive_stats("Epic", "tank")[0] * hp_mult_50)
    == FX["level_scaling"]["gate_F3"]["tank_epic_max_hp_at_50"],
    "F3 tank Epic max_hp 386",
)
for lvl in (5, 50):
    m = 1 + OFF_PER_LVL * (lvl - 1)
    ratio = (60 * m) / (50 * m)
    check(abs(ratio - 1.2) < 1e-12, f"F3 atk/df level-invariance 60/50 == 1.2 at level {lvl}")

# ---------------------------------------------------------------------------
# seeded-RNG discipline
# ---------------------------------------------------------------------------

_CONSTRUCTED_SEEDS: list[int] = []


class RngWrap:
    """Counting wrapper: same underlying stream as the engine's rng calls."""

    __slots__ = ("rng", "jitter_draws", "tie_draws")

    def __init__(self, seed: int) -> None:
        _CONSTRUCTED_SEEDS.append(seed)
        self.rng = random.Random(seed)
        self.jitter_draws = 0
        self.tie_draws = 0

    def jitter(self, lo: float, hi: float) -> float:
        self.jitter_draws += 1
        return self.rng.uniform(lo, hi)

    def tie(self) -> float:
        self.tie_draws += 1
        return self.rng.random()


# ---------------------------------------------------------------------------
# team construction + ordering
# ---------------------------------------------------------------------------

TEAMS = FX["teams"]
COMPS = FX["grid"]["compositions_outer"]  # ["BAL", "ATK", "MIX"]
PILOTS = FX["grid"]["pilots_inner"]  # ["BEGINNER", "MID", "SKILLED"]
COMP_NAMES = {
    "BAL": TEAMS["common_BAL"],
    "ATK": TEAMS["common_ATK"],
    "MIX": TEAMS["common_MIX"],
}
EPIC = TEAMS["epic"]
RARE = TEAMS["rare"]

POL_NAIVE, POL_BEST, POL_SETUP = 0, 1, 2
PILOT_POLICY = {"BEGINNER": POL_NAIVE, "MID": POL_BEST, "SKILLED": POL_SETUP}


def order_type_aware(names: list[str], opp_lead_name: str) -> list[str]:
    """Stable sort by descending effectiveness vs the opponent's PRE-ordering lead."""
    opp_el = CATALOG[opp_lead_name][0]
    return sorted(names, key=lambda nm: -effectiveness(CATALOG[nm][0], opp_el))


def build_side(names: list[str], level: int) -> dict:
    """Per-combatant derived battle values (engine-faithful float ops)."""
    off_m = 1 + OFF_PER_LVL * (level - 1)
    hp_m = 1 + HP_PER_LVL * (level - 1)
    side = {"names": list(names), "el": [], "max_hp": [], "spd": [],
            "atk_stat": [], "df_stat": [], "hp06": []}
    for nm in names:
        el, rarity, arche = CATALOG[nm]
        hp, atk, df, spd = derive_stats(rarity, arche)
        mh = round(hp * hp_m)
        side["el"].append(EIDX[el])
        side["max_hp"].append(mh)
        side["spd"].append(spd * off_m)
        side["atk_stat"].append(atk)
        side["df_stat"].append(df)
        side["hp06"].append(0.6 * mh)
        side["off_m"] = off_m
    return side


def pair_tables(att: dict, dfn: dict, buff_cap: float) -> tuple:
    """Precompute per (buffed, attacker i, defender j): naive base, best base,
    best expected — float ops associated exactly as battle.py move_damage /
    expected_damage compute them."""
    off_m = att["off_m"]
    n_a, n_d = len(att["names"]), len(dfn["names"])
    sig = [[[0.0] * n_d for _ in range(n_a)] for _ in range(2)]
    best = [[[0.0] * n_d for _ in range(n_a)] for _ in range(2)]
    bexp = [[[0.0] * n_d for _ in range(n_a)] for _ in range(2)]
    for buf in (0, 1):
        stage = 0.0 if buf == 0 else min(buff_cap, 0.0 + BUFF_STEP)
        for i in range(n_a):
            atk = att["atk_stat"][i] * off_m * (1 + stage)
            a_el = CYCLE[att["el"][i]]
            for j in range(n_d):
                df = dfn["df_stat"][j] * off_m * (1 + 0.0)
                ratio = atk / max(1.0, df)
                d_el = CYCLE[dfn["el"][j]]
                strike_base = ratio * NORMAL_POWER * NEUTRAL
                sig_base = ratio * ELEMENT_POWER * effectiveness(a_el, d_el)
                strike_exp = strike_base * EXP_CONST
                sig_exp = sig_base * EXP_CONST
                sig[buf][i][j] = sig_base
                # engine max() keeps the FIRST max — moves list order [Strike, sig]
                if strike_exp >= sig_exp:
                    best[buf][i][j] = strike_base
                    bexp[buf][i][j] = strike_exp
                else:
                    best[buf][i][j] = sig_base
                    bexp[buf][i][j] = sig_exp
    return sig, best, bexp


def run_cell(names_a, names_b, pol_a, pol_b, n, rngw, jlo, jhi, degenerate,
             level, buff_cap=None):
    """N battles of team a vs team b; returns wins_a + leg stats.

    buff_cap defaults to the committed 0.5. The cap is inert under the
    committed policy family (policy_setup buffs at most once, so the stage is
    min(cap, 0.25) either way) — honored anyway per the registration.
    """
    if buff_cap is None:
        buff_cap = FX["moves"]["buff_cap"]
    A = build_side(names_a, level)
    B = build_side(names_b, level)
    sigA, bestA, bexpA = pair_tables(A, B, buff_cap)
    sigB, bestB, bexpB = pair_tables(B, A, buff_cap)
    mh_a, mh_b = A["max_hp"], B["max_hp"]
    spd_a, spd_b = A["spd"], B["spd"]
    th_a, th_b = A["hp06"], B["hp06"]
    len_a, len_b = len(names_a), len(names_b)
    wins = 0
    dmg_events = 0
    tie_events = 0
    stall_hits = 0
    uni = rngw.jitter
    tie = rngw.tie
    for _ in range(n):
        ia = ib = 0
        hp_a = mh_a[0]
        hp_b = mh_b[0]
        buf_a = buf_b = 0
        guard = 0
        while True:
            guard += 1
            if guard > STALL_GUARD:
                stall_hits += 1
                # engine: higher remaining-HP side wins (run-invalidating anyway)
                rem_a = hp_a + sum(mh_a[ia + 1:])
                rem_b = hp_b + sum(mh_b[ib + 1:])
                win_a = rem_a >= rem_b
                break
            sa = spd_a[ia]
            sb = spd_b[ib]
            if sa > sb:
                a_first = True
            elif sb > sa:
                a_first = False
            else:
                tie_events += 1
                a_first = tie() < 0.5
            for actor_is_a in ((True, False) if a_first else (False, True)):
                if actor_is_a:
                    if hp_a <= 0 or hp_b <= 0:
                        continue
                    if pol_a == POL_NAIVE:
                        base = sigA[buf_a][ia][ib]
                    elif pol_a == POL_BEST:
                        base = bestA[buf_a][ia][ib]
                    else:
                        if bexpA[buf_a][ia][ib] >= hp_b:
                            base = bestA[buf_a][ia][ib]
                        elif buf_a == 0 and hp_a >= th_a[ia] and sa >= sb:
                            buf_a = 1
                            continue
                        else:
                            base = bestA[buf_a][ia][ib]
                    j = 0.925 if degenerate else uni(jlo, jhi)
                    d = round(base * j)
                    if d < 1:
                        d = 1
                    hp_b -= d
                    dmg_events += 1
                else:
                    if hp_b <= 0 or hp_a <= 0:
                        continue
                    if pol_b == POL_NAIVE:
                        base = sigB[buf_b][ib][ia]
                    elif pol_b == POL_BEST:
                        base = bestB[buf_b][ib][ia]
                    else:
                        if bexpB[buf_b][ib][ia] >= hp_a:
                            base = bestB[buf_b][ib][ia]
                        elif buf_b == 0 and hp_b >= th_b[ib] and sb >= sa:
                            buf_b = 1
                            continue
                        else:
                            base = bestB[buf_b][ib][ia]
                    j = 0.925 if degenerate else uni(jlo, jhi)
                    d = round(base * j)
                    if d < 1:
                        d = 1
                    hp_a -= d
                    dmg_events += 1
            advanced = False
            if hp_a <= 0:
                ia += 1
                advanced = True
                if ia < len_a:
                    hp_a = mh_a[ia]
                    buf_a = 0
            if hp_b <= 0:
                ib += 1
                advanced = True
                if ib < len_b:
                    hp_b = mh_b[ib]
                    buf_b = 0
            if advanced and (ia >= len_a or ib >= len_b):
                win_a = ib >= len_b  # engine: "a" if ib >= len(team_b) else "b"
                break
        if win_a:
            wins += 1
    return wins, dmg_events, tie_events, stall_hits

# ---------------------------------------------------------------------------
# F4: the deterministic hand-traced fixture battle (event-logged slow path)
# ---------------------------------------------------------------------------


def fixture_battle() -> list[list]:
    """Cindling vs Infernox 1v1, both policy_best_damage, jitter == 0.925."""
    events = []
    A = build_side(["Cindling"], LEVEL_50)
    B = build_side(["Infernox"], LEVEL_50)
    cap = FX["moves"]["buff_cap"]
    sigA, bestA, bexpA = pair_tables(A, B, cap)
    sigB, bestB, bexpB = pair_tables(B, A, cap)
    hp_a, hp_b = A["max_hp"][0], B["max_hp"][0]
    turn = 0
    guard = 0
    # both pick the element signature (Cinderlash) — best expected damage
    move_a = FX["element_move_names"][CYCLE[A["el"][0]]]
    move_b = FX["element_move_names"][CYCLE[B["el"][0]]]
    check(A["spd"][0] > B["spd"][0], "F4 Cindling acts first (135.75 > 122.175)")
    check(bestA[0][0][0] == sigA[0][0][0], "F4 Cindling best move is the signature")
    check(bestB[0][0][0] == sigB[0][0][0], "F4 Infernox best move is the signature")
    while hp_a > 0 and hp_b > 0:
        guard += 1
        if guard > STALL_GUARD:
            raise AssertionError("fixture stall")
        turn += 1
        # Cindling (a) first
        d = max(1, round(bestA[0][0][0] * 0.925))
        hp_b -= d
        events.append([turn, "a", "Cindling", move_a, d, max(0, hp_b), hp_b <= 0])
        if hp_b <= 0:
            break
        d = max(1, round(bestB[0][0][0] * 0.925))
        hp_a -= d
        events.append([turn, "b", "Infernox", move_b, d, max(0, hp_a), hp_a <= 0])
    return events


fx4 = FX["hand_fixture_F4"]
ev = fixture_battle()
check(len(ev) == len(fx4["event_log"]), f"F4 event count {len(fx4['event_log'])}")
check(ev == [list(e) for e in fx4["event_log"]], "F4 full event log reproduced exactly")
check(all(e[4] == fx4["cindling_per_action_damage"] for e in ev if e[1] == "a"),
      "F4 Cindling per-action damage 6")
check(all(e[4] == fx4["infernox_per_action_damage"] for e in ev if e[1] == "b"),
      "F4 Infernox per-action damage 13")
b_actions = [e for e in ev if e[1] == "b"]
check(len(b_actions) == fx4["infernox_ko_action"] and b_actions[-1][6],
      "F4 Infernox KOs on its 16th action")
check(sum(e[4] for e in ev if e[1] == "a") == fx4["cindling_total_dealt"],
      "F4 Cindling dealt 96 total")

# ---------------------------------------------------------------------------
# Arm E — exact stakes arm (seedless Fractions)
# ---------------------------------------------------------------------------

AE = FX["arm_e"]
W_RAR = {k: Fraction(v) for k, v in AE["rarity_encounter_weight"].items()}
BASE = {k: Fraction(v) for k, v in AE["rarity_catch_base"].items()}
COUNTS = AE["catalog_counts"]
total_weight = sum(W_RAR[r] * COUNTS[r] for r in COUNTS)
check(total_weight == AE["total_weight"], "Arm E total catalog weight 1884")
bonus = min(Fraction(AE["max_catch_bonus"]), AE["player_level"] * Fraction(AE["catch_bonus_per_level"]))
CATCH50 = {r: min(Fraction(AE["max_catch_chance"]), BASE[r] + bonus) for r in BASE}
for r, pin in AE["catch_at_level_50"].items():
    check(CATCH50[r] == Fraction(pin), f"Arm E catch@50 {r} == {pin}")


def p_specific(rarity: str) -> Fraction:
    return (W_RAR[rarity] / total_weight) * CATCH50[rarity]


check(p_specific("Epic") == Fraction(1, 785), "F6 p(specific Epic) == 1/785")
check(1 / p_specific("Epic") == 785, "F6 single specific Epic costs exactly 785 encounters")


def e_max_inclusion_exclusion(ps: list[Fraction]) -> Fraction:
    n = len(ps)
    total = Fraction(0)
    for mask in range(1, 1 << n):
        s = Fraction(0)
        bits = 0
        for i in range(n):
            if mask >> i & 1:
                s += ps[i]
                bits += 1
        total += (Fraction(1) if bits % 2 == 1 else Fraction(-1)) / s
    return total


def e_max_markov(ps: list[Fraction]) -> Fraction:
    n = len(ps)
    memo: dict[int, Fraction] = {0: Fraction(0)}

    def solve(mask: int) -> Fraction:
        if mask in memo:
            return memo[mask]
        p_s = sum(ps[i] for i in range(n) if mask >> i & 1)
        e = 1 / p_s + sum((ps[i] / p_s) * solve(mask & ~(1 << i))
                          for i in range(n) if mask >> i & 1)
        memo[mask] = e
        return e

    return solve((1 << n) - 1)


ps_epic = [p_specific("Epic")] * 6
ps_common = [p_specific("Common")] * 6
E_epic_ie = e_max_inclusion_exclusion(ps_epic)
E_epic_mk = e_max_markov(ps_epic)
E_common_ie = e_max_inclusion_exclusion(ps_common)
E_common_mk = e_max_markov(ps_common)
check(E_epic_ie == E_epic_mk, "F6 Markov twin == inclusion-exclusion (E_epic) at exact equality")
check(E_common_ie == E_common_mk, "F6 Markov twin == inclusion-exclusion (E_common) at exact equality")
check(E_epic_ie == 785 * Fraction(49, 20), "F6 equal-p identity: E_epic == 785 * 49/20 exact")
check(E_common_ie == (1 / p_specific("Common")) * Fraction(49, 20),
      "F6 equal-p identity: E_common == (1/p) * 49/20 exact")
TP = E_epic_ie / E_common_ie
check(abs(float(TP) - 39.6) < 0.1, "Arm E TP lands in the hand span (approx 39.6)")

# ---------------------------------------------------------------------------
# Arm S — the decision arm
# ---------------------------------------------------------------------------

BC = FX["battle_counts"]
SEEDS = FX["seeds"]
JLO, JHI = FX["jitter_bounds"]


def epic_lead():
    return EPIC[0]


def make_grid_cells(level=LEVEL_50):
    """The 9 pinned cells: (label, names_a(ordered), names_b(ordered), pol_a, pol_b)."""
    cells = []
    for comp in COMPS:
        common = COMP_NAMES[comp]
        common_ordered = order_type_aware(common, EPIC[0])  # vs Epic PRE-ordering lead
        for pilot in PILOTS:
            if pilot == "SKILLED":
                epic_team = order_type_aware(EPIC, common[0])  # vs Common PRE-ordering lead
            else:
                epic_team = list(EPIC)
            cells.append((f"{comp}/{pilot}", common_ordered, epic_team,
                          POL_SETUP, PILOT_POLICY[pilot]))
    return cells


def run_grid(rngw, n, jlo=JLO, jhi=JHI, degenerate=False, level=LEVEL_50,
             buff_cap=None):
    out = {}
    stats = {"battles": 0, "damage_events": 0, "tie_events": 0, "stall_hits": 0}
    for label, na, nb, pa, pb in make_grid_cells():
        wins, de, te, sh = run_cell(na, nb, pa, pb, n, rngw, jlo, jhi,
                                    degenerate, level, buff_cap)
        out[label] = Fraction(wins, n)
        stats["battles"] += n
        stats["damage_events"] += de
        stats["tie_events"] += te
        stats["stall_hits"] += sh
    return out, stats


# --- main leg (seed 20261325): grid then reporting legs, one stream ---------

rng_main = RngWrap(SEEDS["main"])
W_main, st_main = run_grid(rng_main, BC["main_grid_per_cell"])

NREP = BC["reporting_legs_per_leg"]
rep = {}
rep_stats = {"battles": 0, "damage_events": 0, "tie_events": 0, "stall_hits": 0}


def add_leg(label, wins_stats):
    wins, de, te, sh = wins_stats
    rep[label] = Fraction(wins, NREP)
    rep_stats["battles"] += NREP
    rep_stats["damage_events"] += de
    rep_stats["tie_events"] += te
    rep_stats["stall_hits"] += sh


bal = COMP_NAMES["BAL"]
bal_vs_epic = order_type_aware(bal, EPIC[0])
bal_vs_bal = order_type_aware(bal, bal[0])
bal_vs_rare = order_type_aware(bal, RARE[0])
rare_skilled = order_type_aware(RARE, bal[0])

add_leg("mirror_BAL_vs_BAL_max_skill",
        run_cell(bal_vs_bal, bal_vs_bal, POL_SETUP, POL_SETUP, NREP, rng_main,
                 JLO, JHI, False, LEVEL_50))
add_leg("naive_vs_naive_BAL_vs_Epic",
        run_cell(bal, list(EPIC), POL_NAIVE, POL_NAIVE, NREP, rng_main,
                 JLO, JHI, False, LEVEL_50))
add_leg("rare_gradient_BEGINNER",
        run_cell(bal_vs_rare, list(RARE), POL_SETUP, POL_NAIVE, NREP, rng_main,
                 JLO, JHI, False, LEVEL_50))
add_leg("rare_gradient_SKILLED",
        run_cell(bal_vs_rare, rare_skilled, POL_SETUP, POL_SETUP, NREP, rng_main,
                 JLO, JHI, False, LEVEL_50))

# main-leg sentinels
main_jitter_expected = st_main["damage_events"] + rep_stats["damage_events"]
main_ties_expected = st_main["tie_events"] + rep_stats["tie_events"]
check(rng_main.jitter_draws == main_jitter_expected,
      "sentinel: main-leg jitter draws == damage events")
check(rng_main.tie_draws == main_ties_expected,
      "sentinel: main-leg tie-flip draws == recorded ties")
check(st_main["stall_hits"] + rep_stats["stall_hits"] == 0,
      "F5 zero stall-guard hits (main leg, invalidating)")
check(st_main["battles"] == 9 * BC["main_grid_per_cell"], "main grid battle count 180000")
check(rep_stats["battles"] == 4 * NREP, "reporting legs battle count 80000")

# F5 mirror + naive direction
mirror_dev = abs(rep["mirror_BAL_vs_BAL_max_skill"] - Fraction(1, 2))
check(mirror_dev <= Fraction(1, 50),
      f"F5 mirror match within 1/50 of 1/2 (|dev| = {frs(mirror_dev)})")
NAIVE_DIRECTION_OK = rep["naive_vs_naive_BAL_vs_Epic"] < Fraction(1, 2)
if not NAIVE_DIRECTION_OK:
    print("EXPECTED-DIRECTION FLAG (loud, not invalidating): naive-vs-naive "
          f"W = {frs(rep['naive_vs_naive_BAL_vs_Epic'])} >= 1/2 — the raw wall "
          "did not show; investigate before trusting the grid.")
check(True, "F5 naive-vs-naive expected-direction evaluated (loud flag, not invalidating)")

# --- stability leg (seed 20261326) ------------------------------------------

rng_stab = RngWrap(SEEDS["stability"])
W_stab, st_stab = run_grid(rng_stab, BC["stability_per_cell"])
check(rng_stab.jitter_draws == st_stab["damage_events"],
      "sentinel: stability jitter draws == damage events")
check(rng_stab.tie_draws == st_stab["tie_events"],
      "sentinel: stability tie draws == recorded ties")
check(st_stab["stall_hits"] == 0, "F5 zero stall-guard hits (stability leg)")

# --- sensitivity legs (seed 20261327, one stream, pinned scenario order) -----

rng_sens = RngWrap(SEEDS["sensitivity_reporting"])
SCEN = FX["sensitivity_scenarios"]
W_sens = {}
sens_stats = {}
for scen in FX["sensitivity_scenarios_order"]:
    cfg = SCEN[scen]
    if scen == "jitter_wide":
        w, st = run_grid(rng_sens, BC["sensitivity_per_cell"],
                         jlo=cfg["jitter_bounds"][0], jhi=cfg["jitter_bounds"][1])
    elif scen == "jitter_degenerate":
        before = rng_sens.jitter_draws
        w, st = run_grid(rng_sens, BC["sensitivity_per_cell"], degenerate=True)
        check(rng_sens.jitter_draws - before == cfg["jitter_draws_sentinel"],
              "sentinel: degenerate scenario draws 0 jitters (pinned)")
    elif scen == "buff_cap_75":
        w, st = run_grid(rng_sens, BC["sensitivity_per_cell"], buff_cap=cfg["buff_cap"])
    else:  # level_5
        w, st = run_grid(rng_sens, BC["sensitivity_per_cell"], level=cfg["level"])
    W_sens[scen] = w
    sens_stats[scen] = st
    check(st["stall_hits"] == 0, f"F5 zero stall-guard hits (sensitivity {scen})")
sens_dmg_nondegen = sum(sens_stats[s]["damage_events"]
                        for s in W_sens if s != "jitter_degenerate")
check(rng_sens.jitter_draws == sens_dmg_nondegen,
      "sentinel: sensitivity jitter draws == damage events (non-degenerate scenarios)")
check(rng_sens.tie_draws == sum(sens_stats[s]["tie_events"] for s in W_sens),
      "sentinel: sensitivity tie draws == recorded ties")

# --- aux seed never read -----------------------------------------------------

check(SEEDS["aux_never_read"] not in _CONSTRUCTED_SEEDS,
      "aux seed 20261328 never read (no RNG constructed with it)")
check(_CONSTRUCTED_SEEDS == [SEEDS["main"], SEEDS["stability"],
                             SEEDS["sensitivity_reporting"]],
      "exactly three RNGs constructed, in pinned order")

# ---------------------------------------------------------------------------
# twin decision evaluators
# ---------------------------------------------------------------------------

TWO_FIFTHS = Fraction(2, 5)
HALF = Fraction(1, 2)


def evaluator_fraction(W: dict) -> tuple:
    """Twin 1: Fraction comparisons, compositions in pinned order."""
    reject_ct = 0
    beg_all_half = True
    skilled_below_ct = 0
    for c in COMPS:
        wb = W[f"{c}/BEGINNER"]
        if wb < TWO_FIFTHS:
            reject_ct += 1
        if wb < HALF:
            beg_all_half = False
        if W[f"{c}/SKILLED"] < HALF:
            skilled_below_ct += 1
    return (reject_ct >= 2, beg_all_half and skilled_below_ct >= 2,
            reject_ct, skilled_below_ct)


def evaluator_integer(W: dict) -> tuple:
    """Twin 2: pure-integer cross-multiplication, opposite iteration order."""
    rc = 0
    ba = True
    sc = 0
    for c in reversed(COMPS):
        f = W[f"{c}/BEGINNER"]
        if 5 * f.numerator < 2 * f.denominator:  # W < 2/5
            rc += 1
        if 2 * f.numerator < f.denominator:  # W < 1/2
            ba = False
        g = W[f"{c}/SKILLED"]
        if 2 * g.numerator < g.denominator:  # W < 1/2
            sc += 1
    return (rc >= 2, ba and sc >= 2, rc, sc)


def base_class(W: dict) -> tuple[str, list[str]]:
    """Pre-registered rule, evaluated IN ORDER — REJECT first."""
    e1 = evaluator_fraction(W)
    e2 = evaluator_integer(W)
    check(e1 == e2, "twin evaluators agree")
    reject, approve_band = e1[0], e1[1]
    if reject:
        return "REJECT", []
    if approve_band:
        return "APPROVE", []
    axes = []
    beg = [W[f"{c}/BEGINNER"] for c in COMPS]
    if any(x >= HALF for x in beg) and any(x < TWO_FIFTHS for x in beg):
        axes.append("composition-straddle")
    if all(TWO_FIFTHS <= x < HALF for x in beg):
        axes.append("margin-band")
    if sum(1 for c in COMPS if W[f"{c}/SKILLED"] >= HALF) >= 2:
        axes.append("budget-inert")
    return "NULL", axes


main_class, main_axes = base_class(W_main)
stab_class, stab_axes = base_class(W_stab)
stability_reproduced = stab_class == main_class

if stability_reproduced:
    ruling = main_class
    ruling_axes = main_axes
else:
    ruling = "NULL"
    ruling_axes = ["stability non-reproduction"]

# sensitivity straddles (reporting-only — name the axis, never flip)
fired_straddles = []
for scen in FX["sensitivity_scenarios_order"]:
    s_class, s_axes = base_class(W_sens[scen])
    if s_class != main_class:
        fired_straddles.append({"scenario": scen, "class": s_class, "axes": s_axes})

# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------


def wtab(W):
    return {k: {"exact": frs(v), "float": float(v)} for k, v in sorted(W.items())}


results = {
    "verdict": FX["verdict"],
    "intake": FX["intake"],
    "proposal_header_verbatim": FX["proposal_header_verbatim"],
    "harvest_source": FX["harvest_source"],
    "cpython": f"{sys.version_info.major}.{sys.version_info.minor}",
    "seeds": SEEDS,
    "arm_s": {
        "main_grid_W": wtab(W_main),
        "reporting_legs_W": wtab(rep),
        "stability_grid_W": wtab(W_stab),
        "sensitivity_grids_W": {s: wtab(W_sens[s]) for s in FX["sensitivity_scenarios_order"]},
        "sentinels": {
            "main": {"jitter_draws": rng_main.jitter_draws, "tie_draws": rng_main.tie_draws,
                     "damage_events": main_jitter_expected, "tie_events": main_ties_expected,
                     "battles": st_main["battles"] + rep_stats["battles"], "stall_hits": 0},
            "stability": {"jitter_draws": rng_stab.jitter_draws, "tie_draws": rng_stab.tie_draws,
                          "battles": st_stab["battles"], "stall_hits": 0},
            "sensitivity": {"jitter_draws": rng_sens.jitter_draws, "tie_draws": rng_sens.tie_draws,
                            "battles": sum(s["battles"] for s in sens_stats.values()),
                            "stall_hits": 0},
        },
        "naive_direction_ok": NAIVE_DIRECTION_OK,
        "mirror_deviation_from_half": frs(mirror_dev),
    },
    "arm_e": {
        "p_specific": {r: frs(p_specific(r)) for r in ("Common", "Uncommon", "Rare", "Epic")},
        "E_epic": {"exact": frs(E_epic_ie), "float": float(E_epic_ie)},
        "E_common_BAL": {"exact": frs(E_common_ie), "float": float(E_common_ie)},
        "TP": {"exact": frs(TP), "float": float(TP)},
        "anchors": {"single_specific_epic": 785, "equal_p_identity": "E == (1/p) * 49/20",
                    "markov_twin_equality": "exact"},
    },
    "derived_stats_reporting": {
        f"{r}/{a}": list(derive_stats(r, a))
        for r, a in [("Rare", "attacker"), ("Rare", "tank"), ("Rare", "balanced"),
                     ("Rare", "speedster")]
    },
    "evaluators": {
        "main": {"fraction": evaluator_fraction(W_main), "integer": evaluator_integer(W_main)},
        "stability": {"fraction": evaluator_fraction(W_stab), "integer": evaluator_integer(W_stab)},
    },
    "decision": {
        "main_class": main_class,
        "main_axes": main_axes,
        "stability_class": stab_class,
        "stability_axes": stab_axes,
        "stability_reproduced": stability_reproduced,
        "fired_sensitivity_straddles": fired_straddles,
        "ruling": ruling,
        "ruling_axes": ruling_axes,
        "rule": FX["decision_bands"],
    },
    "buff_cap_inertness_note": SCEN["buff_cap_75"]["_note"],
}

check(_CHECKS["failed"] == 0, "all prior checks green")

results["self_checks"] = {"passed": _CHECKS["passed"], "failed": _CHECKS["failed"],
                          "failures": _FAILURES}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=1, sort_keys=True, default=list)
    f.write("\n")

print("VERDICT 058 — creature-PvP rarity vs skill (PROPOSAL 047)")
print(f"cpython {results['cpython']} | seeds {SEEDS['main']}/{SEEDS['stability']}/"
      f"{SEEDS['sensitivity_reporting']} (aux {SEEDS['aux_never_read']} never read)")
print(f"-- 9-cell W grid (P(Common side wins), main leg, N={BC['main_grid_per_cell']}/cell) --")
for c in COMPS:
    row = "  ".join(f"{p}: {frs(W_main[f'{c}/{p}'])} ({float(W_main[f'{c}/{p}']):.4f})"
                    for p in PILOTS)
    print(f"  {c}: {row}")
print(f"-- reporting legs (N={NREP} each) --")
for k in sorted(rep):
    print(f"  {k}: {frs(rep[k])} ({float(rep[k]):.4f})")
print(f"-- stability grid (seed {SEEDS['stability']}, N={BC['stability_per_cell']}/cell) --")
for c in COMPS:
    row = "  ".join(f"{p}: {float(W_stab[f'{c}/{p}']):.4f}" for p in PILOTS)
    print(f"  {c}: {row}")
print(f"-- sensitivity grids (seed {SEEDS['sensitivity_reporting']}, "
      f"N={BC['sensitivity_per_cell']}/cell, reporting-only) --")
for scen in FX["sensitivity_scenarios_order"]:
    row = " | ".join(f"{c}/{p}: {float(W_sens[scen][f'{c}/{p}']):.3f}"
                     for c in COMPS for p in ("BEGINNER", "SKILLED"))
    print(f"  {scen}: {row}")
print("-- Arm E (exact stakes) --")
print(f"  E_epic = {frs(E_epic_ie)} = {float(E_epic_ie)}")
print(f"  E_common(BAL) = {frs(E_common_ie)} = {float(E_common_ie)}")
print(f"  TP = {frs(TP)} = {float(TP):.4f}")
print("-- decision --")
print(f"  main class: {main_class} (axes: {main_axes})")
print(f"  stability class: {stab_class} (reproduced: {stability_reproduced})")
print(f"  fired sensitivity straddles: "
      f"{[s['scenario'] for s in fired_straddles] or 'none'}")
print(f"  RULING: {ruling}" + (f" — axes: {ruling_axes}" if ruling_axes else ""))
print(f"SELF-CHECKS: {_CHECKS['passed']} passed, {_CHECKS['failed']} failed")
sys.exit(0 if _CHECKS["failed"] == 0 else 1)

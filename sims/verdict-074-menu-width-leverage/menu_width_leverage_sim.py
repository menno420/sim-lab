#!/usr/bin/env python3
"""VERDICT 074 — menu-width leverage inversion (idea-engine PROPOSAL 063).

Hermetic: reads ONLY its sibling fixtures.json. Exact-Fraction forward
recursion (decision-bearing) + seeded Monte-Carlo twin (20,000 episodes/cell,
3-sigma agreement per convention C7). Gates F1-F4 (+F1b) fail-loud before any
cell is read; decision per the registered rule (NULL on gate failure, else
APPROVE-REORDER iff >= 1 policy passes all four bands, else REJECT-REORDER).

stdout is deterministic (no timestamps/durations); timing goes to stderr.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------- #
# self-check machinery
# ----------------------------------------------------------------------- #
_PASS = 0
_FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    global _PASS
    if ok:
        _PASS += 1
    else:
        _FAILS.append(f"{name}: {detail}" if detail else name)
        print(f"SELF-CHECK FAIL: {name} {detail}")
    return ok


def frs(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


# ----------------------------------------------------------------------- #
# fixtures
# ----------------------------------------------------------------------- #
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check(
    "cpython-pin",
    platform.python_implementation() == "CPython"
    and f"{sys.version_info[0]}.{sys.version_info[1]}" == FX["cpython_minor_pinned"],
    f"need CPython {FX['cpython_minor_pinned']}, got {platform.python_implementation()} {sys.version_info[:2]}",
)

SCENE_IDS = ["waystation_road", "waystation_gate", "treeline_watch"]
S_INDEX = {sid: i for i, sid in enumerate(SCENE_IDS)}
ROLES = ["M", "N", "Z"]
POLICIES: list[str] = FX["policies"]
SHIPPED: str = FX["shipped_policy"]
WIDTHS = [2, 3, 4]
HORIZONS: list[int] = FX["horizons_T"]
T_MAX = max(HORIZONS)
N_EP: int = FX["mc"]["episodes_per_cell"]
SIGMA: int = FX["mc"]["tolerance_sigma"]
CURRENCY_PER_MINT: int = FX["mint"]["tier_caps_I"]["currency"]

B4_PS = [Fraction(p) for p in FX["behaviours"]["B4"]["p_values"]]
BEHAVIOURS = ["B1", "B2", "B3"] + [f"B4(p={frs(p)})" for p in B4_PS]
B4_OF = {f"B4(p={frs(p)})": p for p in B4_PS}

# Action = (mints: bool, next_scene_index: int, noop: bool)
ROLE_ACT: dict[tuple[int, str], tuple[bool, int, bool]] = {}
for sid in SCENE_IDS:
    si = S_INDEX[sid]
    for role in ROLES:
        r = FX["scenes"][sid]["roles"][role]
        nxt = S_INDEX[r["next_scene_id"]] if r["next_scene_id"] else si
        ROLE_ACT[(si, role)] = (bool(r["mints"]), nxt, r["effect_id"] == "rest_noop")

# ----------------------------------------------------------------------- #
# F1 — fixture identity
# ----------------------------------------------------------------------- #
WL = FX["width_law"]


def menu_width(xp: int) -> int:
    w = WL["base_menu_width"] + max(0, xp) // WL["xp_per_extra_option"]
    return max(WL["base_menu_width"], min(w, WL["max_menu_width"]))


for xp_s, w_pin in WL["fixture_table"].items():
    check(f"F1-width({xp_s})", menu_width(int(xp_s)) == w_pin, f"got {menu_width(int(xp_s))}")
for w_s, xp_pin in WL["width_axis_xp"].items():
    check(f"F1-axis(w{w_s})", menu_width(xp_pin) == int(w_s))

for sid in SCENE_IDS:
    sc = FX["scenes"][sid]
    role_ids = {sc["roles"][r]["option_id"] for r in ROLES}
    check(f"F1-{sid}-ids", role_ids == set(sc["shipped_literal_order"]))
    check(
        f"F1-{sid}-default-Z-last",
        sc["default_option_id"] == sc["roles"]["Z"]["option_id"]
        and sc["shipped_literal_order"][2] == sc["default_option_id"],
    )
    for r in ROLES:
        ro = sc["roles"][r]
        check(
            f"F1-{sid}-{r}-mint-iff-escort",
            bool(ro["mints"]) == (ro["effect_id"] == "escort_step"),
        )
si_t = S_INDEX["treeline_watch"]
check(
    "F1-treeline-absorbing",
    all(ROLE_ACT[(si_t, r)][1] == si_t for r in ROLES),
    "treeline_watch must stay at every option (every width/ordering)",
)
tc = FX["mint"]["tier_caps_I"]
check("F1-tier-caps-I", (tc["global_xp"], tc["game_xp"], tc["currency"]) == (5, 25, 10))
gm = FX["mint"]["global_max"]
check("F1-global-max", (gm["global_xp"], gm["game_xp"], gm["currency"]) == (20, 120, 50))
check(
    "F1-global-max-caps-tier",
    tc["global_xp"] <= gm["global_xp"] and tc["game_xp"] <= gm["game_xp"] and tc["currency"] <= gm["currency"],
)
check("F1-dedup-witness", FX["dedup_witness"]["_FULL_MENU_XP"] == 5000)
check("F1-policy-family-complete", sorted(POLICIES) == sorted(["MNZ", "MZN", "NMZ", "NZM", "ZMN", "ZNM"]))

# F1b — literal-shipped prefix-SET equivalence with the MNZ policy (convention C1)
for sid in SCENE_IDS:
    sc = FX["scenes"][sid]
    literal = sc["shipped_literal_order"]
    mnz = [sc["roles"][r]["option_id"] for r in "MNZ"]
    for w in WIDTHS:
        k = min(len(literal), w, WL["max_menu_size"])
        check(
            f"F1b-{sid}-w{w}",
            set(literal[:k]) == set(mnz[:k]),
            f"literal prefix set {literal[:k]} vs MNZ {mnz[:k]}",
        )

# ----------------------------------------------------------------------- #
# behaviour-induced per-scene action distributions (exact)
# ----------------------------------------------------------------------- #


def prefix_roles(policy: str, width: int) -> list[str]:
    k = min(3, width, WL["max_menu_size"])
    return list(policy[:k])


def scene_dist(policy: str, beh: str, width: int, si: int) -> list[tuple[Fraction, tuple[bool, int, bool]]]:
    """Exact distribution over actions for one turn in scene si."""
    roles = prefix_roles(policy, width)
    acts = [ROLE_ACT[(si, r)] for r in roles]
    if beh == "B1":
        u = Fraction(1, len(acts))
        return [(u, a) for a in acts]
    if beh == "B2":
        for a in acts:  # surfaced mint first (prefix order; never binds — <=1 mint/scene)
            if a[0]:
                return [(Fraction(1), a)]
        for a in acts:  # surfaced progress edge next
            if a[1] != si:
                return [(Fraction(1), a)]
        u = Fraction(1, len(acts))
        return [(u, a) for a in acts]
    if beh == "B3":
        for pref in "NZM":
            if pref in roles:
                return [(Fraction(1), ROLE_ACT[(si, pref)])]
        raise AssertionError("unreachable")
    p = B4_OF[beh]
    z_full = ROLE_ACT[(si, "Z")]  # FULL-scene default (convention C9)
    u = (1 - p) * Fraction(1, len(acts))
    return [(p, z_full)] + [(u, a) for a in acts]


# ----------------------------------------------------------------------- #
# exact arm — forward recursion over (scene, visited-mask, minted)
# ----------------------------------------------------------------------- #


def exact_cell(policy: str, beh: str, width: int) -> dict:
    dists = [scene_dist(policy, beh, width, si) for si in range(3)]
    state: dict[tuple[int, int, bool], Fraction] = {(0, 1, False): Fraction(1)}
    cum_mints = Fraction(0)
    cum_noop = Fraction(0)
    out: dict = {"checkpoints": {}}
    trace: list[dict] = []
    for t in range(1, T_MAX + 1):
        mint_p = Fraction(0)
        noop_p = Fraction(0)
        nstate: dict[tuple[int, int, bool], Fraction] = {}
        for (si, vis, minted), pr in state.items():
            for q, (m, nxt, np_) in dists[si]:
                pq = pr * q
                if m:
                    mint_p += pq
                if np_:
                    noop_p += pq
                key = (nxt, vis | (1 << nxt), minted or m)
                nstate[key] = nstate.get(key, Fraction(0)) + pq
        cum_mints += mint_p
        cum_noop += noop_p
        state = nstate
        if t <= 2:
            dist_scene: dict[str, Fraction] = {}
            for (si, _v, _m), pr in state.items():
                dist_scene[SCENE_IDS[si]] = dist_scene.get(SCENE_IDS[si], Fraction(0)) + pr
            trace.append({"turn": t, "mint_prob": mint_p, "dist_after": dist_scene})
        if t in HORIZONS:
            p_minted = sum((pr for (_s, _v, mm), pr in state.items() if mm), Fraction(0))
            e_distinct = sum(pr * bin(vis).count("1") for (_s, vis, _m), pr in state.items())
            out["checkpoints"][t] = {
                "E_mints_perapp": cum_mints,
                "E_mints_once": p_minted,
                "P_ge1_mint": p_minted,
                "E_currency_perapp": cum_mints * CURRENCY_PER_MINT,
                "E_currency_once": p_minted * CURRENCY_PER_MINT,
                "E_distinct_scenes": e_distinct,
                "E_noop_turns": cum_noop,
            }
    total = sum(state.values())
    check(f"exact-mass-{policy}-{beh}-w{width}", total == 1, f"probability mass {total}")
    out["trace2"] = trace

    # long-run rate per convention C6 (scene-level chain; DAG absorption)
    trans = [dict() for _ in range(3)]
    mintp = [Fraction(0)] * 3
    for si in range(3):
        for q, (m, nxt, _np) in dists[si]:
            trans[si][nxt] = trans[si].get(nxt, Fraction(0)) + q
            if m:
                mintp[si] += q
    check(f"exact-dag-{policy}-{beh}-w{width}", 0 not in trans[1] and list(trans[2]) == [2], "back-edge found")
    if trans[0].get(0, Fraction(0)) == 1:
        absorb = {0: Fraction(1)}
    else:
        g = trans[0].get(1, Fraction(0))
        tt = trans[0].get(2, Fraction(0))
        norm = g + tt
        hit_gate = g / norm
        if trans[1].get(1, Fraction(0)) == 1:
            absorb = {1: hit_gate, 2: 1 - hit_gate}
        else:
            absorb = {2: Fraction(1)}
    out["longrun_mint_rate"] = sum(absorb[s] * mintp[s] for s in absorb)
    return out


EXACT: dict[tuple[str, str, int], dict] = {}
for pol in POLICIES:
    for beh in BEHAVIOURS:
        for w in WIDTHS:
            EXACT[(pol, beh, w)] = exact_cell(pol, beh, w)

# ----------------------------------------------------------------------- #
# gates F2, F3, F4
# ----------------------------------------------------------------------- #
f2 = FX["gates"]["F2"]
c_w2 = EXACT[(SHIPPED, "B1", 2)]
c_w3 = EXACT[(SHIPPED, "B1", 3)]
check("F2-longrun-w2", c_w2["longrun_mint_rate"] == Fraction(f2["longrun_w2"]), frs(c_w2["longrun_mint_rate"]))
check("F2-longrun-w3", c_w3["longrun_mint_rate"] == Fraction(f2["longrun_w3"]), frs(c_w3["longrun_mint_rate"]))
check(
    "F2-E20-w2",
    c_w2["checkpoints"][20]["E_mints_perapp"] == Fraction(f2["E_mints_T20_w2"]),
    frs(c_w2["checkpoints"][20]["E_mints_perapp"]),
)
check(
    "F2-E20-w3",
    c_w3["checkpoints"][20]["E_mints_perapp"] == Fraction(f2["E_mints_T20_w3"]),
    frs(c_w3["checkpoints"][20]["E_mints_perapp"]),
)

for pol in POLICIES:
    for beh in BEHAVIOURS:
        a, b = EXACT[(pol, beh, 3)], EXACT[(pol, beh, 4)]
        check(
            f"F3-{pol}-{beh}",
            a["checkpoints"] == b["checkpoints"] and a["longrun_mint_rate"] == b["longrun_mint_rate"],
        )

f4 = FX["gates"]["F4"]
tr = EXACT[(SHIPPED, "B1", 2)]["trace2"]
check("F4-turn1-mint", tr[0]["mint_prob"] == Fraction(f4["turn1"]["mint_prob"]), frs(tr[0]["mint_prob"]))
check("F4-turn2-mint", tr[1]["mint_prob"] == Fraction(f4["turn2"]["mint_prob"]), frs(tr[1]["mint_prob"]))
for tt, hand in ((0, f4["turn1"]["dist_after"]), (1, f4["turn2"]["dist_after"])):
    got = {k: v for k, v in tr[tt]["dist_after"].items() if v}
    want = {k: Fraction(v) for k, v in hand.items()}
    check(f"F4-dist-after-turn{tt + 1}", got == want, f"got { {k: frs(v) for k, v in got.items()} }")
check(
    "F4-E-T2",
    tr[0]["mint_prob"] + tr[1]["mint_prob"] == Fraction(f4["E_mints_T2"]),
)

GATES_GREEN = not _FAILS

# ----------------------------------------------------------------------- #
# bands + decision (exact arm, PER-APP, as registered)
# ----------------------------------------------------------------------- #
FLOOR = Fraction(1, 6)
FARM_RATIO = Fraction(3, 4)
shipped_farm_cur = EXACT[(SHIPPED, "B2", 2)]["checkpoints"][20]["E_currency_perapp"]

BANDS: dict[str, dict] = {}
for pol in POLICIES:
    e20 = {w: EXACT[(pol, "B1", w)]["checkpoints"][20]["E_mints_perapp"] for w in WIDTHS}
    monotone = e20[2] <= e20[3] and e20[3] == e20[4]
    lr2 = EXACT[(pol, "B1", 2)]["longrun_mint_rate"]
    floor_ok = lr2 >= FLOOR
    cur = EXACT[(pol, "B2", 2)]["checkpoints"][20]["E_currency_perapp"]
    farmer_ok = cur <= FARM_RATIO * shipped_farm_cur
    conform = "Z" in pol[:2]
    BANDS[pol] = {
        "MONOTONE": monotone,
        "POSITIVE_FLOOR": floor_ok,
        "FARMER": farmer_ok,
        "CONFORM": conform,
        "all_four": monotone and floor_ok and farmer_ok and conform,
        "B1_E_mints_T20_by_width": {w: e20[w] for w in WIDTHS},
        "B1_longrun_w2": lr2,
        "B2_currency_T20_w2": cur,
    }

passing = [p for p in POLICIES if BANDS[p]["all_four"]]

partition = sorted({BANDS[p]["B1_longrun_w2"] for p in POLICIES})
check(
    "PARTITION-{0,1/2}",
    partition == [Fraction(0), Fraction(1, 2)],
    f"got {[frs(x) for x in partition]}",
)
for pol in POLICIES:
    m_in_p2 = "M" in pol[:2]
    check(
        f"PARTITION-{pol}",
        BANDS[pol]["B1_longrun_w2"] == (Fraction(1, 2) if m_in_p2 else Fraction(0)),
        frs(BANDS[pol]["B1_longrun_w2"]),
    )
    check(
        f"JOINT-UNSAT-{pol}",
        not (BANDS[pol]["MONOTONE"] and BANDS[pol]["POSITIVE_FLOOR"]),
        "MONOTONE and POSITIVE-FLOOR jointly satisfied — impossibility refuted",
    )

if not GATES_GREEN:
    VERDICT = "NULL"
    VERDICT_WHY = "gate failure (see SELF-CHECK FAIL lines) — the fixture does not reproduce the harvested pins"
elif passing:
    VERDICT = "APPROVE-REORDER"
    VERDICT_WHY = f"passing set: {passing}"
else:
    VERDICT = "REJECT-REORDER"
    VERDICT_WHY = (
        "no ordering passes all four bands; w2 B1 long-run partition "
        f"{{{', '.join(frs(x) for x in partition)}}} forces MONOTONE and POSITIVE-FLOOR to be jointly unsatisfiable"
    )

# ----------------------------------------------------------------------- #
# drafter-disclosed landing — re-derived, COMPARED, never gated
# ----------------------------------------------------------------------- #
d = FX["drafter_disclosed_never_gated"]
lr_fall = (
    EXACT[(SHIPPED, "B1", 2)]["longrun_mint_rate"] == Fraction(1, 2)
    and EXACT[(SHIPPED, "B1", 3)]["longrun_mint_rate"] == Fraction(1, 3)
)
e2f = EXACT[(SHIPPED, "B1", 2)]["checkpoints"][20]["E_mints_perapp"]
e3f = EXACT[(SHIPPED, "B1", 3)]["checkpoints"][20]["E_mints_perapp"]
drop_pct = float(1 - e3f / e2f) * 100
b2w = {w: EXACT[(SHIPPED, "B2", w)]["checkpoints"][20] for w in WIDTHS}
DRAFTER_CMP = {
    "shipped_longrun_fall_1/2_to_1/3": lr_fall,
    "shipped_E_T20_drop_pct": {"derived": round(-drop_pct, 1), "disclosed": -35.1, "match": abs(drop_pct - 35.1) < 0.05},
    "shipped_B2_19_mints_190_currency_every_width": all(
        b2w[w]["E_mints_perapp"] == 19 and b2w[w]["E_currency_perapp"] == 190 for w in WIDTHS
    ),
    "w2_B1_partition_0_half": partition == [Fraction(0), Fraction(1, 2)],
    "conform_false_policies": sorted(p for p in POLICIES if not BANDS[p]["CONFORM"]) == sorted(d["conform_false_policies"]),
    "zero_floor_orderings": sorted(p for p in POLICIES if BANDS[p]["B1_longrun_w2"] == 0) == sorted(d["zero_floor_orderings"]),
    "zero_floor_farmer_gated_to_zero": all(
        EXACT[(p, "B2", 2)]["checkpoints"][20]["E_currency_perapp"] == 0 for p in d["zero_floor_orderings"]
    ),
    "predicted_verdict_matches": VERDICT == d["predicted_verdict"],
}

# ----------------------------------------------------------------------- #
# Monte-Carlo twin (legs per convention C10)
# ----------------------------------------------------------------------- #
SEEDS = FX["seeds_registered"]
RNGS_CONSTRUCTED: list[str] = []
DRAWS = {"A": 0, "B": 0, "B4-stress": 0, "holdout": 0}
TURNS = {"A": 0, "B": 0, "B4-stress": 0, "holdout": 0}


def substream(leg_seed: int, pol: str, beh: str, width: int) -> random.Random:
    tag = f"{leg_seed}|{pol}|{beh}|w{width}"
    RNGS_CONSTRUCTED.append(tag)
    return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "big"))


def mc_rules(pol: str, beh: str, width: int):
    """Per-scene compiled rule: (is_random, t1, t2, t3, a0, a1, a2, a3, det)."""
    rules = []
    for si in range(3):
        dist = scene_dist(pol, beh, width, si)
        if len(dist) == 1:
            rules.append((False, 0.0, 0.0, 0.0, None, None, None, None, dist[0][1]))
        else:
            acts = [a for _q, a in dist]
            cum, thresholds = Fraction(0), []
            for q, _a in dist[:-1]:
                cum += q
                thresholds.append(float(cum))
            while len(thresholds) < 3:
                thresholds.append(1.0)
            while len(acts) < 4:
                acts.append(acts[-1])
            rules.append((True, thresholds[0], thresholds[1], thresholds[2], acts[0], acts[1], acts[2], acts[3], None))
    return rules


def run_mc_cell(pol: str, beh: str, width: int, rng: random.Random, leg: str) -> dict:
    rules = mc_rules(pol, beh, width)
    rnd = rng.random
    n = N_EP
    stats = {
        T: {"sum_m": 0, "sumsq_m": 0, "n_minted": 0, "sum_noop": 0, "sum_distinct": 0} for T in HORIZONS
    }
    draws = 0
    for _ in range(n):
        s = 0
        mints = 0
        noop = 0
        vis = 1
        t = 0
        for Tc in HORIZONS:
            while t < Tc:
                t += 1
                rule = rules[s]
                if rule[0]:
                    u = rnd()
                    draws += 1
                    if u < rule[1]:
                        a = rule[4]
                    elif u < rule[2]:
                        a = rule[5]
                    elif u < rule[3]:
                        a = rule[6]
                    else:
                        a = rule[7]
                else:
                    a = rule[8]
                if a[0]:
                    mints += 1
                if a[2]:
                    noop += 1
                ns = a[1]
                if ns != s:
                    s = ns
                    vis |= 1 << ns
            st = stats[Tc]
            st["sum_m"] += mints
            st["sumsq_m"] += mints * mints
            if mints:
                st["n_minted"] += 1
            st["sum_noop"] += noop
            st["sum_distinct"] += bin(vis).count("1")
    DRAWS[leg] += draws
    TURNS[leg] += n * T_MAX

    exact_cp = EXACT[(pol, beh, width)]["checkpoints"]
    out = {}
    for T in HORIZONS:
        st = stats[T]
        mean = st["sum_m"] / n
        var = (st["sumsq_m"] - n * mean * mean) / (n - 1)
        se = math.sqrt(max(var, 0.0) / n)
        ex = float(exact_cp[T]["E_mints_perapp"])
        ok = (abs(mean - ex) <= SIGMA * se) if se > 0 else (mean == ex)
        check(f"MC-{leg}-{pol}-{beh}-w{width}-T{T}-perapp", ok, f"mc {mean} exact {ex} se {se}")
        ph = st["n_minted"] / n
        se1 = math.sqrt(ph * (1 - ph) / (n - 1)) if 0 < ph < 1 else 0.0
        ex1 = float(exact_cp[T]["P_ge1_mint"])
        ok1 = (abs(ph - ex1) <= SIGMA * se1) if se1 > 0 else (ph == ex1)
        check(f"MC-{leg}-{pol}-{beh}-w{width}-T{T}-once", ok1, f"mc {ph} exact {ex1} se {se1}")
        out[T] = {
            "mean_mints_perapp": mean,
            "se_mints_perapp": se,
            "p_ge1_mint": ph,
            "mean_noop": st["sum_noop"] / n,
            "mean_distinct": st["sum_distinct"] / n,
        }
    return out


ALL_CELLS = [(pol, beh, w) for pol in POLICIES for beh in BEHAVIOURS for w in WIDTHS]
LEGS = {
    "A": (SEEDS["leg_A_main"], ALL_CELLS),
    "B": (SEEDS["leg_B_twin"], ALL_CELLS),
    "B4-stress": (SEEDS["leg_B4_clamp_stress"], [c for c in ALL_CELLS if c[1].startswith("B4")]),
    "holdout": (SEEDS["leg_holdout"], [c for c in ALL_CELLS if c[0] == SHIPPED and c[1] == "B1"]),
}
MC_RESULTS: dict[str, dict] = {}
for leg, (seed, cells) in LEGS.items():
    leg_out = {}
    for pol, beh, w in cells:
        rng = substream(seed, pol, beh, w)
        leg_out[f"{pol}|{beh}|w{w}"] = run_mc_cell(pol, beh, w, rng, leg)
    MC_RESULTS[leg] = leg_out

check("RNG-registry-count", len(RNGS_CONSTRUCTED) == 90 + 90 + 36 + 3, f"got {len(RNGS_CONSTRUCTED)}")
for leg, (seed, cells) in LEGS.items():
    check(f"RNG-leg-{leg}", sum(1 for t in RNGS_CONSTRUCTED if t.startswith(f"{seed}|")) == len(cells))
    check(f"TURNS-{leg}", TURNS[leg] == len(cells) * N_EP * T_MAX, f"got {TURNS[leg]}")
check(
    "RNG-only-registered-base-seeds",
    {t.split("|")[0] for t in RNGS_CONSTRUCTED}
    == {str(SEEDS["leg_A_main"]), str(SEEDS["leg_B_twin"]), str(SEEDS["leg_B4_clamp_stress"]), str(SEEDS["leg_holdout"])},
)

# ----------------------------------------------------------------------- #
# results.json + stdout
# ----------------------------------------------------------------------- #


def ser(x):
    if isinstance(x, Fraction):
        return {"frac": frs(x), "float": float(x)}
    if isinstance(x, dict):
        return {str(k): ser(v) for k, v in x.items()}
    if isinstance(x, list):
        return [ser(v) for v in x]
    return x


results = {
    "verdict": VERDICT,
    "verdict_why": VERDICT_WHY,
    "passing_set": passing,
    "bands": ser({p: {k: v for k, v in BANDS[p].items()} for p in POLICIES}),
    "partition_w2_B1_longrun": [frs(x) for x in partition],
    "exact_grid": ser(
        {
            f"{pol}|{beh}|w{w}": {
                "longrun_mint_rate": EXACT[(pol, beh, w)]["longrun_mint_rate"],
                "checkpoints": EXACT[(pol, beh, w)]["checkpoints"],
            }
            for (pol, beh, w) in ALL_CELLS
        }
    ),
    "default_in_prefix2_by_policy": {p: "Z" in p[:2] for p in POLICIES},
    "mc": MC_RESULTS,
    "mc_draws_per_leg": DRAWS,
    "mc_turns_per_leg": TURNS,
    "rngs_constructed": len(RNGS_CONSTRUCTED),
    "drafter_comparison_never_gated": ser(DRAFTER_CMP),
    "self_checks": {"passed": None, "failed": None},  # filled below
    "seeds": SEEDS,
}

results["self_checks"]["passed"] = _PASS
results["self_checks"]["failed"] = len(_FAILS)
results["failed_check_names"] = _FAILS

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, sort_keys=True, indent=1)
    fh.write("\n")

print("VERDICT 074 — menu-width leverage inversion (idea-engine PROPOSAL 063)")
print(f"gates: F1/F1b/F2/F3/F4 {'GREEN' if GATES_GREEN else 'FAILED (NULL)'}")
print(f"verdict: {VERDICT} — {VERDICT_WHY}")
print()
print("band table (PER-APP, exact arm):")
hdr = f"{'policy':7s} {'MONOTONE':9s} {'FLOOR':6s} {'FARMER':7s} {'CONFORM':8s} {'B1 E20 w2':>12s} {'w3':>10s} {'lr w2':>6s} {'B2 cur w2':>10s}"
print(hdr)
for pol in POLICIES:
    b = BANDS[pol]
    print(
        f"{pol + (' *' if pol == SHIPPED else ''):7s} "
        f"{str(b['MONOTONE']):9s} {str(b['POSITIVE_FLOOR']):6s} {str(b['FARMER']):7s} {str(b['CONFORM']):8s} "
        f"{float(b['B1_E_mints_T20_by_width'][2]):>12.6f} {float(b['B1_E_mints_T20_by_width'][3]):>10.6f} "
        f"{frs(b['B1_longrun_w2']):>6s} {float(b['B2_currency_T20_w2']):>10.1f}"
    )
print("  (* = SHIPPED)")
print()
print(f"F2 exact: SHIPPED×B1 E[mints,T=20] w2 = {frs(e2f)} ≈ {float(e2f):.6f}, w3 = {frs(e3f)} ≈ {float(e3f):.6f} ({-drop_pct:+.1f}%)")
print(f"partition of w2 B1 long-run rates: {{{', '.join(frs(x) for x in partition)}}}")
print(f"drafter comparison (never gated): {json.dumps(ser(DRAFTER_CMP), sort_keys=True)}")
print(f"MC draws per leg: {json.dumps(DRAWS, sort_keys=True)}; RNGs constructed: {len(RNGS_CONSTRUCTED)}")
print()
print(f"SELF-CHECKS: {_PASS} passed, {len(_FAILS)} failed")
sys.exit(0 if not _FAILS else 1)

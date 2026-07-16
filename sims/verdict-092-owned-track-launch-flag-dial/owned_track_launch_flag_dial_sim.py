#!/usr/bin/env python3
"""VERDICT 092 — the owned-track launch-flag dial (idea-engine PROPOSAL 079).

Three-arm, hermetic, pre-registered (fixtures.json committed BEFORE this
runner; the P017–P078 discipline):

  Arm A — closed-form constants and the predicate s·n >= theta_k
          (seedless exact integer arithmetic, DECISION-bearing).
  Arm B — the REAL vendored engine + runtime (byte-copy of superbot-idle
          @ 884aeae, sha256-manifest-verified at start) driven through
          play.dispatch / play.advance — the live walk must reproduce
          every Arm-A number through the four typed contacts C1–C4.
  Arm R — seeded random command traces, REPORTING-ONLY (seeds
          20261710/711/712, aux 20261713 never read; the registered
          draw-order grammar with draw-count sentinels).

Decision rule (registered order): REJECT -> INVALID -> APPROVE -> NULL.
Zero network, zero git, zero wall clock in any output. stdout and
results.json are byte-identical across process runs. Requires PyYAML +
jsonschema (the vendored lane's own committed dependencies — see
fixtures.json vendor.third_party_note); every decision computation is
stdlib + the vendored engine.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True  # keep the sha256-manifest-pinned vendor tree byte-clean

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
WITNESS = os.path.join(HERE, "witness")

# --- self-check ledger --------------------------------------------------------

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    CHECKS.append((name, bool(ok), detail))
    return bool(ok)


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text)


# --- Arm A: closed forms (seedless, exact, engine-independent) ------------------

THETA = (10, 100, 1000)
RUNGS = ("owned-1", "owned-2", "owned-3")
BONUS = 5
FOLD_DEN = 100_000_000


def a_predicate(s: int, n: int) -> dict[str, bool]:
    """owned-k earned iff s*n >= theta_k — the birth/never dichotomy."""
    return {RUNGS[i]: s * n >= THETA[i] for i in range(3)}


def a_flip(theta: int, n: int) -> int:
    """s* = ceil(theta/n) — the flip law."""
    return -(-theta // n)


def a_gen_rate(base_rate: int, count: int, milestone_pct: int) -> int:
    """The committed fold for one generator at neutral upgrade/prestige/theme."""
    return base_rate * count * 100 * 100 * milestone_pct * 100 // FOLD_DEN


def a_pack_rate(rates: list[int], count: int, milestone_pct: int) -> int:
    return sum(a_gen_rate(b, count, milestone_pct) for b in rates)


def evaluator_a(inputs: dict[str, bool]) -> str:
    """Decision evaluator, Arm-A side: plain if-chain in the registered order."""
    assert set(inputs) == {"R1", "R2", "R3", "R4", "gates_ok", "approve_witness"}
    if inputs["R1"] and inputs["R2"] and inputs["R3"] and inputs["R4"]:
        return "REJECT"
    if not inputs["gates_ok"]:
        return "INVALID"
    if inputs["approve_witness"]:
        return "APPROVE"
    return "NULL"


def evaluator_b(inputs: dict[str, bool]) -> str:
    """Decision evaluator, Arm-B side: table-driven, independently written."""
    assert set(inputs) == {"R1", "R2", "R3", "R4", "gates_ok", "approve_witness"}
    reject = all(inputs[k] for k in ("R1", "R2", "R3", "R4"))
    ladder = (
        ("REJECT", reject),
        ("INVALID", not inputs["gates_ok"]),
        ("APPROVE", inputs["approve_witness"]),
        ("NULL", True),
    )
    return next(ruling for ruling, fired in ladder if fired)


# --- main ----------------------------------------------------------------------


def main() -> int:
    out: dict = {"verdict_id": "VERDICT 092", "proposal": "idea-engine PROPOSAL 079 · 2026-07-16T00:39:30Z"}

    # F0 — environment + fixture + vendor manifest -----------------------------
    check("F0.python-minor-pinned", sys.version_info[:2] == (3, 11),
          f"CPython {sys.version_info[0]}.{sys.version_info[1]} (pinned 3.11)")
    with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
        FX = json.load(fh)
    manifest = FX["vendor"]["manifest_sha256"]
    bad = [rel for rel, want in manifest.items()
           if sha256_file(os.path.join(VENDOR, rel)) != want]
    extra = []
    for root, dirs, files in os.walk(VENDOR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]  # interpreter cache, not vendored bytes
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), VENDOR)
            if rel not in manifest:
                extra.append(rel)
    check("F0.vendor-manifest", not bad and not extra and len(manifest) == 35,
          f"{len(manifest)} files sha256-verified vs superbot-idle 884aeae; mismatched={bad} extra={extra}")
    wbad = [f for f, want in FX["witness_packs"]["files_sha256"].items()
            if sha256_file(os.path.join(WITNESS, f)) != want]
    check("F0.witness-manifest", not wbad, f"mismatched={wbad}")

    # import the vendored runtime (play.py inserts vendor/ itself)
    sys.path.insert(0, os.path.join(VENDOR, "tools"))
    sys.path.insert(0, VENDOR)
    import play  # noqa: E402  (vendored)
    from idle_engine.achievements import milestone_percent  # noqa: E402
    from idle_engine.engine import production_per_second  # noqa: E402
    from idle_engine.state import GameState  # noqa: E402
    from idle_engine.theme import load_theme  # noqa: E402
    check("F0.vendored-import", play.__file__ == os.path.join(VENDOR, "tools", "play.py"),
          "play resolved to the vendored copy")

    # F1 — identities + catalog censuses + sentence pins ------------------------
    packs = play.available_packs()
    GRID = tuple(FX["flag_grid"])
    check("F1.pack-glob", packs == FX["catalog"]["packs_sorted"] and len(packs) == 18,
          f"{len(packs)} packs")
    themes = {p: play.load_pack(p) for p in packs}
    rosters = {p: len(t.generators) for p, t in themes.items()}
    roster_ms: dict[int, int] = {}
    rate_ms: dict[int, int] = {}
    balance_blocks = 0
    for p, t in themes.items():
        roster_ms[rosters[p]] = roster_ms.get(rosters[p], 0) + 1
        for g in t.generators.values():
            rate_ms[g.base_rate] = rate_ms.get(g.base_rate, 0) + 1
            if g.rate_multiplier_pct != 100:
                balance_blocks += 1
    check("F1.roster-multiset", roster_ms == {1: 1, 2: 17} and rosters["egg-farm"] == 1,
          f"{sorted(roster_ms.items())}")
    check("F1.base-rate-multiset", rate_ms == {1: 18, 5: 17}, f"{sorted(rate_ms.items())}")
    check("F1.zero-balance-blocks", balance_blocks == 0, f"{balance_blocks} non-neutral pcts")
    owned_slots = sum(sum(1 for s in t.milestone_specs() if s.kind == "owned") for t in themes.values())
    skinned = sum(sum(1 for m in t.milestones if m.startswith("owned-")) for t in themes.values())
    check("F1.54-slots", owned_slots == 54 == 18 * 3 and skinned == 54,
          f"slots={owned_slots} skinned={skinned}")
    check("F1.216-cells", len(packs) * len(GRID) == 216, "18 x 12")
    check("F1.648-cell-rungs", 216 * 3 == 648, "216 x 3")
    from idle_engine import economy  # noqa: E402
    check("F1.ladder-constants",
          economy.MILESTONE_OWNED_THRESHOLDS == (10, 100, 1000) and economy.MILESTONE_BONUS_PERCENT == 5,
          f"{economy.MILESTONE_OWNED_THRESHOLDS} +{economy.MILESTONE_BONUS_PERCENT}%")
    for pin in FX["sentence_pins"]["pins"]:
        body = norm_ws(open(os.path.join(VENDOR, pin["file"]), encoding="utf-8").read())
        check(f"F1.sentence-{pin['id']}", norm_ws(pin["text"]) in body, pin["file"])

    # Arm B corpus drive over all 216 cells -------------------------------------
    CORPUS = FX["canonical_corpus"]["commands"]
    EXT = CORPUS + FX["canonical_corpus"]["extension_control"]
    check("F1.corpus-shape", len(CORPUS) == 11 and "prestige do" in CORPUS and "offline 200000" in CORPUS,
          "11 commands incl. a full prestige cycle")

    def drive(theme, s: int, commands: list[str]) -> dict:
        """Independently-written live walk: dispatch only, own bookkeeping."""
        sess = play.new_session(theme, start_count=s)
        n_expected = s * len(theme.generators)
        rec = {"violations": 0, "first_earned": None, "final_earned": None,
               "prestige_performed": False, "boundaries": 0}
        if sum(sess.state.owned.values()) != n_expected:
            rec["violations"] += 1
        for i, cmd in enumerate(commands):
            sess, msg = play.dispatch(sess, cmd, start_count=s)
            rec["boundaries"] += 1
            if sum(sess.state.owned.values()) != n_expected:
                rec["violations"] += 1
            if cmd == "prestige do" and msg.startswith("Prestiged"):
                rec["prestige_performed"] = True
                rec["post_prestige_owned"] = dict(sess.state.owned)
            if i == 0:
                rec["first_earned"] = {r: sess.state.milestones.get(r, 0) >= 1 for r in RUNGS}
        rec["final_earned"] = {r: sess.state.milestones.get(r, 0) >= 1 for r in RUNGS}
        return rec

    inv_cells = dich_first = dich_final = 0
    contact_c4 = 0
    prestige_cycles = prestige_refusals = 0
    fixed_point_ok = True
    for p in packs:
        n = rosters[p]
        for s in GRID:
            rec = drive(themes[p], s, CORPUS)
            pred = a_predicate(s, n)
            if rec["violations"] == 0:
                inv_cells += 1
            if rec["first_earned"] == pred:
                dich_first += 1
            if rec["final_earned"] == pred:
                dich_final += 1
            contact_c4 += sum(1 for r in RUNGS if rec["first_earned"][r] == pred[r] == rec["final_earned"][r])
            if rec["prestige_performed"]:
                prestige_cycles += 1
                if rec["post_prestige_owned"] != {g: s for g in themes[p].generators}:
                    fixed_point_ok = False
            elif s == 0:
                prestige_refusals += 1
    check("R1.invariance-216", inv_cells == 216, f"{inv_cells}/216 cells, zero violations")
    check("R1.dichotomy-first-boundary", dich_first == 216, f"{dich_first}/216")
    check("R1.dichotomy-post-corpus", dich_final == 216, f"{dich_final}/216")
    check("C4.contact-648", contact_c4 == 648, f"{contact_c4}/648 Arm-A==Arm-B cell-rungs")
    check("R1.prestige-cycle", prestige_cycles == 198 and prestige_refusals == 18,
          f"{prestige_cycles} performed (every s>=1 cell), {prestige_refusals} refused (every s=0 cell)")
    check("R1.prestige-fixed-point", fixed_point_ok, "re-grant == birth grant on every performed cycle")
    out["R1"] = {"invariance_cells": inv_cells, "dichotomy_first": dich_first,
                 "dichotomy_final": dich_final, "c4_contacts": contact_c4,
                 "prestige_cycles": prestige_cycles, "prestige_refusals": prestige_refusals}

    # explicit fixed-point spot check at the registered (2-gen, s=5) cell
    fp_theme = themes["royal-bakery"]
    fp = play.new_session(fp_theme, start_count=5)
    fp = play.advance(fp, 200_000)
    fp, _ = play.dispatch(fp, "prestige do", start_count=5)
    check("F4.fixed-point-cell", fp.state.owned == {"tier1": 5, "tier2": 5},
          f"{dict(sorted(fp.state.owned.items()))}")

    # R2 — the catalog census with rendered lock lines ---------------------------
    def owned_lines(theme, state) -> list[str]:
        from idle_engine.render import render_achievements  # vendored
        embed = render_achievements(state, theme)
        lines = []
        for field, spec in zip(embed["fields"], theme.milestone_specs()):
            if spec.kind == "owned":
                lines.append(field["value"].split("\n")[0])
        return lines

    census_rows = 0
    frozen_fields = 0
    lock1_two = lock1_egg = 0
    lock_lines_out = {}
    for p in packs:
        n = rosters[p]
        sess = play.new_session(themes[p], start_count=1)
        before = owned_lines(themes[p], sess.state)
        end = play.new_session(themes[p], start_count=1)
        for cmd in CORPUS:
            end, _ = play.dispatch(end, cmd, start_count=1)
        after = owned_lines(themes[p], end.state)
        if before == after and len(before) == 3:
            frozen_fields += 3
        if n < 10:
            census_rows += 1
        if before[0] == "\U0001f512 2 / 10" and n == 2:
            lock1_two += 1
        if before[0] == "\U0001f512 1 / 10" and n == 1:
            lock1_egg += 1
        lock_lines_out[p] = before
    check("R2.census-rows", census_rows == 18, f"{census_rows}/18 packs with s*n < theta_1 at the default flag")
    check("R2.frozen-54", frozen_fields == 54, f"{frozen_fields}/54 owned fields byte-stable across the corpus")
    check("R2.lock-line-two-gen", lock1_two == 17, f"{lock1_two}/17 packs render exactly '\U0001f512 2 / 10'")
    check("R2.lock-line-egg-farm", lock1_egg == 1, f"{lock1_egg}/1 pack renders exactly '\U0001f512 1 / 10'")
    out["R2"] = {"lock_lines": lock_lines_out}

    # R3 — flip rows (margin-0 quadruple, quantified over the whole class) -------
    def earned_after_first_boundary(theme, s: int, rung: str) -> bool:
        sess = play.advance(play.new_session(theme, start_count=s), 1)
        return sess.state.milestones.get(rung, 0) >= 1

    flip_ok = {"m0.two-gen-s5": True, "m0.egg-s10": True, "m0.two-gen-s50": True, "m0.two-gen-s500": True}
    for p in packs:
        n, t = rosters[p], themes[p]
        rows = ((5, 10, "owned-1", "m0.two-gen-s5"), (50, 100, "owned-2", "m0.two-gen-s50"),
                (500, 1000, "owned-3", "m0.two-gen-s500")) if n == 2 else \
               ((10, 10, "owned-1", "m0.egg-s10"),)
        for s_star, theta, rung, key in rows:
            ok = (a_flip(theta, n) == s_star and s_star * n == theta
                  and earned_after_first_boundary(t, s_star, rung)
                  and not earned_after_first_boundary(t, s_star - 1, rung))
            flip_ok[key] = flip_ok[key] and ok
    for key, ok in sorted(flip_ok.items()):
        check(f"R3.{key}", ok, "s*n == theta exactly; earned at s*, refused at s*-1 (whole pack class)")

    # R3 — dial cells (live, owned-only earned sets by construction) -------------
    def live_rate(theme, state) -> int:
        gens, ups, pres, mils = play._spec_bundle(theme)
        return sum(production_per_second(state, gens, ups, pres, mils).values())

    def tier_rate(theme, state, gid: str) -> int:
        gens, ups, pres, mils = play._spec_bundle(theme)
        gen = [g for g in gens if g.spec_id == gid]
        return sum(production_per_second(state, gen, ups, pres, mils).values())

    egg = themes["egg-farm"]
    dial = {}
    for s, pre_want, post_want in ((10, 10, 10), (19, 19, 19), (20, 20, 21)):
        sess = play.new_session(egg, start_count=s)
        pre = live_rate(egg, sess.state)
        post = live_rate(egg, play.advance(sess, 30).state)
        dial[f"egg-farm-s{s}"] = [pre, post]
        check(f"R3.dial-egg-s{s}", (pre, post) == (pre_want, post_want),
              f"{pre} -> {post} (registered {pre_want} -> {post_want})")
    rb = themes["royal-bakery"]
    sess = play.new_session(rb, start_count=5)
    pre_total, pre_t1, pre_t2 = live_rate(rb, sess.state), tier_rate(rb, sess.state, "tier1"), tier_rate(rb, sess.state, "tier2")
    post = play.advance(sess, 30).state
    post_total, post_t1, post_t2 = live_rate(rb, post), tier_rate(rb, post, "tier1"), tier_rate(rb, post, "tier2")
    dial["two-gen-s5"] = {"total": [pre_total, post_total], "tier1": [pre_t1, post_t1], "tier2": [pre_t2, post_t2]}
    check("R3.dial-two-gen-s5", (pre_total, post_total, pre_t1, post_t1, pre_t2, post_t2) == (30, 31, 5, 5, 25, 26),
          f"total {pre_total}->{post_total}, tier1 {pre_t1}->{post_t1} (floor-eaten), tier2 {pre_t2}->{post_t2}")

    # the (3000, 3450) cell on the registered owned-only pinned GameStates
    wedge_pcts = []
    wedge_rates = []
    gens, ups, pres, mils = play._spec_bundle(rb)
    for earned in ({}, {"owned-1": 1}, {"owned-1": 1, "owned-2": 1, "owned-3": 1}):
        st = GameState(owned={"tier1": 500, "tier2": 500}, milestones=dict(earned))
        wedge_pcts.append(milestone_percent(st, mils))
        wedge_rates.append(sum(production_per_second(st, gens, ups, pres, mils).values()))
    dial["two-gen-s500-owned-only"] = {"percents": wedge_pcts, "rates": wedge_rates}
    check("R3.wedge-percents", wedge_pcts == [100, 105, 115], f"{wedge_pcts}")
    check("R3.dial-two-gen-s500", (wedge_rates[0], wedge_rates[2]) == (3000, 3450),
          f"{wedge_rates[0]} -> {wedge_rates[2]} (+15% exactly)")
    check("F4.s500-no-floor-loss",
          a_gen_rate(1, 500, 115) == 575 and a_gen_rate(5, 500, 115) == 2875 and 575 + 2875 == 3450
          and 3450 == 3000 * 115 // 100, "575 + 2875 == 3450 == 3000 + 15%")
    out["R3_dial"] = dial

    # R3 — boundary-lag pairs -----------------------------------------------------
    lag = {}
    sess = play.new_session(rb, start_count=5)
    a1 = play.advance(sess, 30)
    a2 = play.advance(a1, 30)
    lag["span30"] = [a1.state.balances.get("primary", 0),
                     a2.state.balances.get("primary", 0) - a1.state.balances.get("primary", 0)]
    sess = play.new_session(rb, start_count=5)
    b1 = play.advance(sess, 3600)
    b2 = play.advance(b1, 3600)
    lag["span3600"] = [b1.state.balances.get("primary", 0),
                       b2.state.balances.get("primary", 0) - b1.state.balances.get("primary", 0)]
    lag["span3600_second_span_pct"] = milestone_percent(b1.state, play._spec_bundle(rb)[3])
    check("R3.lag-span30", lag["span30"] == [900, 930], f"{lag['span30']}")
    check("R3.lag-span3600", lag["span3600"] == [108000, 118800] and lag["span3600_second_span_pct"] == 115,
          f"{lag['span3600']} at second-span pct {lag['span3600_second_span_pct']}")
    check("F4.pencil-30s", 30 * 30 == 900 and 31 * 30 == 930, "30*30 == 900; 31*30 == 930")
    out["R3_lag"] = lag

    # R4 — the roster back door ----------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        cat = os.path.join(tmp, "catalog20")
        os.makedirs(cat)
        for p in packs:
            shutil.copy(os.path.join(VENDOR, "themes", f"{p}.yaml"), cat)
        for w in ("witness-ten.yaml", "witness-nine.yaml"):
            shutil.copy(os.path.join(WITNESS, w), cat)
        proc = subprocess.run(
            [sys.executable, os.path.join(VENDOR, "tools", "theme_gate.py"), cat],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        gate_last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    check("R4.gate-exit-0", proc.returncode == 0, f"exit {proc.returncode}: {gate_last}")
    check("R4.gate-20-packs", gate_last == "theme-gate: all 20 pack(s) valid (schema v1)", gate_last)
    wt = load_theme(os.path.join(WITNESS, "witness-ten.yaml"))
    wn = load_theme(os.path.join(WITNESS, "witness-nine.yaml"))
    st = play.advance(play.Session(theme=wt, state=play.new_session(wt, start_count=1).state), 1)
    sn = play.advance(play.Session(theme=wn, state=play.new_session(wn, start_count=1).state), 1)
    ten_rate, nine_rate = live_rate(wt, st.state), live_rate(wn, sn.state)
    ten_blessed = st.state.milestones.get("owned-1", 0) >= 1
    nine_blessed = any(sn.state.milestones.get(r, 0) >= 1 for r in RUNGS)
    check("R4.born-blessed", ten_blessed and not nine_blessed,
          "10-gen pack earns owned-1 at its first boundary at the DEFAULT flag; the 9-gen twin earns nothing")
    check("R4.rates-210-180", (ten_rate, nine_rate) == (210, 180), f"{ten_rate} vs {nine_rate}, permanently")
    check("R4.arm-a-twin", a_pack_rate([20] * 10, 1, 105) == 210 and a_pack_rate([20] * 9, 1, 100) == 180,
          "closed-form fold reproduces 210/180")
    out["R4"] = {"gate_exit": proc.returncode, "gate_line": gate_last,
                 "ten_rate": ten_rate, "nine_rate": nine_rate}

    # F5 — degeneracy / convention controls -----------------------------------------
    z = play.new_session(rb, start_count=0)
    z_rate = live_rate(rb, z.state)
    z2, zmsg = play.dispatch(play.advance(z, 3600), "prestige do", start_count=0)
    check("F5.s0-degenerate", z.state.owned == {} and z_rate == 0
          and zmsg.startswith("Not eligible") and sum(z2.state.owned.values()) == 0,
          "empty grant, zero production, prestige refused, invariant 0")
    ext_ok = bump_ok = True
    for p in packs:
        n = rosters[p]
        for s in GRID:
            if drive(themes[p], s, EXT)["violations"]:
                ext_ok = False
        for s in FX["canonical_corpus"]["grid_bump_control"]:
            rec = drive(themes[p], s, CORPUS)
            if rec["violations"] or rec["final_earned"] != a_predicate(s, n):
                bump_ok = False
    check("F5.corpus-extension", ext_ok, f"invariance holds on all 216 cells under the {len(EXT)}-command extension")
    check("F5.grid-bump", bump_ok, "invariance + dichotomy hold at s in {2, 7, 1000} on all 18 packs")
    wt_data = {k: v for k, v in json.loads(json.dumps(_yaml_load(os.path.join(WITNESS, "witness-ten.yaml")))).items()}
    wn_data = {k: v for k, v in json.loads(json.dumps(_yaml_load(os.path.join(WITNESS, "witness-nine.yaml")))).items()}
    same_prefix = wt_data["generators"][:9] == wn_data["generators"]
    others = all(wt_data.get(k) == wn_data.get(k) for k in wt_data if k not in ("theme", "generators"))
    check("F5.witness-roster-only", len(wt_data["generators"]) == 10 and len(wn_data["generators"]) == 9
          and same_prefix and others, "the pair differs ONLY in roster length (field-by-field)")

    # Arm R — seeded traces, REPORTING-ONLY ------------------------------------------
    CMD5 = ("wait", "offline", "buy-max", "prestige-do", "achievements")
    AWARDING = {"wait", "offline"}

    def run_seed(seed: int) -> tuple[list[int], str]:
        rng = random.Random(seed)
        draws = 0

        def rr(n: int) -> int:
            nonlocal draws
            draws += 1
            return rng.randrange(n)

        def ri(a: int, b: int) -> int:
            nonlocal draws
            draws += 1
            return rng.randint(a, b)

        violations = blessed = boundaries = 0
        blessed_closed = 0
        digest = hashlib.sha256()
        for _trace in range(2000):
            d0 = draws
            p = packs[rr(18)]
            s = GRID[rr(12)]
            L = ri(3, 10)
            theme = themes[p]
            n_expected = s * rosters[p]
            sess = play.new_session(theme, start_count=s)
            has_awarding = False
            for _step in range(L):
                cmd = CMD5[rr(5)]
                dur = ri(60, 7200)
                if cmd == "wait":
                    line, has_awarding = f"wait {dur}", True
                elif cmd == "offline":
                    line, has_awarding = f"offline {dur}", True
                elif cmd == "buy-max":
                    first_up = next(iter(theme.upgrades), None)
                    line = f"buy {first_up} max" if first_up else "shop"
                elif cmd == "prestige-do":
                    line = "prestige do"
                else:
                    line = "achievements"
                sess, _msg = play.dispatch(sess, line, start_count=s)
                boundaries += 1
                if sum(sess.state.owned.values()) != n_expected:
                    violations += 1
            if any(sess.state.milestones.get(r, 0) >= 1 for r in RUNGS):
                blessed += 1
            if n_expected >= 10 and has_awarding:
                blessed_closed += 1
            if draws - d0 != 3 + 2 * L:
                raise AssertionError("draw-count sentinel violated")
            digest.update(f"{p}|{s}|{L}|{sum(sess.state.owned.values())}\n".encode())
        if blessed != blessed_closed:
            raise AssertionError("blessed closed form diverged from the live census")
        return [violations, blessed, boundaries], digest.hexdigest()

    arm_r = {}
    det_ok = True
    for seed in FX["armR"]["seeds"]:
        triple1, dig1 = run_seed(seed)
        triple2, dig2 = run_seed(seed)
        det_ok = det_ok and triple1 == triple2 and dig1 == dig2
        arm_r[str(seed)] = {"triple": triple1, "trace_digest": dig1}
        want = FX["armR"]["registered_previews"][str(seed)]
        check(f"ArmR.preview-{seed}", triple1 == want,
              f"(violations, blessed, boundaries) = {triple1} (registered {want})")
    check("ArmR.determinism", det_ok, "each seed reproduced itself byte-identically (double run in-process)")
    check("ArmR.draw-grammar-sentinels", True, "3 + 2L draws per trace asserted on every one of the 6,000 traces x2")
    check("ArmR.aux-seed-never-read", True, "seed 20261713 never constructed (no random.Random(20261713) call exists in this runner)")
    out["armR"] = arm_r

    # the twin evaluators over the ENUMERATED input set --------------------------------
    def named(prefix: str) -> list[tuple[str, bool, str]]:
        return [c for c in CHECKS if c[0].startswith(prefix)]

    def all_ok(prefix: str) -> bool:
        rows = named(prefix)
        return bool(rows) and all(ok for _n, ok, _d in rows)

    r1 = all_ok("R1.") and all_ok("C4.")
    r2 = all_ok("R2.")
    r3 = all_ok("R3.")
    r4 = all_ok("R4.")
    gates_ok = all_ok("F0.") and all_ok("F1.") and all_ok("F4.") and all_ok("F5.") and all_ok("ArmR.")
    # APPROVE witness: measured — at the default flag over the corpus, did total
    # owned ever change or any owned rung get earned? (computed from the live drive)
    approve_witness = False
    for p in packs:
        rec = drive(themes[p], 1, CORPUS)
        if rec["violations"] or any(rec["final_earned"].values()):
            approve_witness = True
    inputs = {"R1": r1, "R2": r2, "R3": r3, "R4": r4,
              "gates_ok": gates_ok, "approve_witness": approve_witness}
    ruling_a, ruling_b = evaluator_a(inputs), evaluator_b(inputs)
    check("F6.twin-evaluators", ruling_a == ruling_b, f"{ruling_a} / {ruling_b}")
    out["decision_inputs"] = inputs
    out["ruling"] = ruling_a

    # ledger + emit --------------------------------------------------------------------
    passed = sum(1 for _n, ok, _d in CHECKS if ok)
    failed = len(CHECKS) - passed
    out["self_checks"] = {"total": len(CHECKS), "passed": passed, "failed": failed}
    out["checks"] = [{"name": n, "ok": ok, "detail": d} for n, ok, d in CHECKS]

    lines = []
    lines.append("VERDICT 092 sim — owned-track launch-flag dial (PROPOSAL 079)")
    lines.append(f"vendored engine: superbot-idle @ 884aeae (35 files sha256-verified)")
    for n, ok, d in CHECKS:
        lines.append(f"  [{'PASS' if ok else 'FAIL'}] {n}: {d}")
    lines.append(f"decision inputs: {json.dumps(inputs, sort_keys=True)}")
    lines.append(f"RULING: {ruling_a} (twin evaluators agree: {ruling_a} / {ruling_b})")
    lines.append(f"self-checks: {len(CHECKS)} total, {passed} passed, {failed} failed")
    stdout_text = "\n".join(lines) + "\n"
    sys.stdout.write(stdout_text)

    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(HERE, "run-stdout.txt"), "w", encoding="utf-8") as fh:
        fh.write(stdout_text)
    return 0 if failed == 0 else 1


def _yaml_load(path: str):
    import yaml  # the vendored lane's own dependency
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


if __name__ == "__main__":
    raise SystemExit(main())

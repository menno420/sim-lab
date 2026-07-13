#!/usr/bin/env python3
"""VERDICT 050 (INTAKE 039) — Gloamline plateau survival ceiling.

Pre-registered policy census over the committed Gloamline night frame
(idea-engine PROPOSAL 039; engine = gba-homebrew tools/check-gloam.py @
d87f9ad, byte-copied into this directory and sha256-gated before import).

Usage: python3 sims/verdict-050-gloamline-survival-ceiling/gloamline_ceiling_sim.py

stdlib-only, hermetic (reads only its own fixtures.json + check_gloam_mirror.py),
fully deterministic: stdout + results.json byte-identical across process runs.
Arm D is zero-RNG; Arm S draws exactly one random.random() per frame from the
registered seeds 20261293 (main) / 20261294 (stability) / 20261295 (reporting);
20261296 (aux) is reserved and draws ZERO. Exit 0 only if every gate and
self-check passes; any failure invalidates the run (no verdict is emitted).
"""

import hashlib
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print(f"FAIL: {label}")
    return cond


def hard(cond, label):
    """Gate: run invalid on failure."""
    if not check(cond, label):
        print(f"GATE FAILURE — run invalid: {label}")
        print(f"SELF-CHECKS: {CHECKS['passed']} passed, {CHECKS['failed']} failed")
        sys.exit(1)


# ------------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "rb") as fh:
    FIX = json.loads(fh.read().decode("utf-8"))

# ------------------------------------------------- mirror sha256 gate + import
MIRROR_PATH = os.path.join(HERE, FIX["engine"]["mirror_file"])
with open(MIRROR_PATH, "rb") as fh:
    mirror_bytes = fh.read()
digest = hashlib.sha256(mirror_bytes).hexdigest()
hard(digest == FIX["engine"]["mirror_sha256"],
     f"mirror sha256 {digest} != pinned {FIX['engine']['mirror_sha256']}")

hard(sys.version_info[:2] == (3, 11),
     f"CPython minor {sys.version_info[:2]} != pinned (3, 11)")

spec = importlib.util.spec_from_file_location("gl_mirror", MIRROR_PATH)
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

# ------------------------------------------------------- constants cross-check
C = FIX["engine"]["constants"]
ONE = C["GL_ONE"]
XMIN, XMAX = C["GL_ARENA_X_MIN"], C["GL_ARENA_X_MAX"]
YMIN, YMAX = C["GL_ARENA_Y_MIN"], C["GL_ARENA_Y_MAX"]
PSX, PSY = C["GL_PLAYER_START_X"], C["GL_PLAYER_START_Y"]
PSPD, PDIAG = C["GL_PLAYER_SPEED"], C["GL_PLAYER_DIAG"]
ZSPD, ZDIAG = C["GL_SHAMBLER_SPEED"], C["GL_SHAMBLER_DIAG"]
DEADZONE = C["GL_AXIS_DEADZONE"]
CONTACT = C["GL_CONTACT_RANGE"]
SAFE = C["GL_SAFE_RADIUS"]
CAP = C["GL_ZOMBIE_CAP"]
SPAN = C["GL_WAVE_SPAWN_SPAN"]
NF = C["GL_NIGHT_FRAMES"]
SHOVE_RANGE = C["GL_SHOVE_RANGE"]
SHOVE_PUSH = C["GL_SHOVE_PUSH"]
SHOVE_STUN = C["GL_SHOVE_STUN"]
SHOVE_CD = C["GL_SHOVE_COOLDOWN"]
OIL_MAX = C["GL_OIL_MAX"]
LIGHT_R_MIN = C["GL_LIGHT_R_MIN"]

for name, want in [
    ("GL_ONE", ONE), ("GL_ARENA_X_MIN", XMIN), ("GL_ARENA_X_MAX", XMAX),
    ("GL_ARENA_Y_MIN", YMIN), ("GL_ARENA_Y_MAX", YMAX),
    ("GL_PLAYER_START_X", PSX), ("GL_PLAYER_START_Y", PSY),
    ("GL_PLAYER_SPEED", PSPD), ("GL_PLAYER_DIAG", PDIAG),
    ("GL_SHAMBLER_SPEED", ZSPD), ("GL_SHAMBLER_DIAG", ZDIAG),
    ("GL_AXIS_DEADZONE", DEADZONE), ("GL_CONTACT_RANGE", CONTACT),
    ("GL_SAFE_RADIUS", SAFE), ("GL_ZOMBIE_CAP", CAP),
    ("GL_WAVE_SPAWN_SPAN", SPAN), ("GL_NIGHT_FRAMES", NF),
    ("GL_SHOVE_RANGE", SHOVE_RANGE), ("GL_SHOVE_PUSH", SHOVE_PUSH),
    ("GL_SHOVE_STUN", SHOVE_STUN), ("GL_SHOVE_COOLDOWN", SHOVE_CD),
    ("GL_OIL_MAX", OIL_MAX), ("GL_LIGHT_R_MIN", LIGHT_R_MIN),
]:
    hard(getattr(cg, name) == want, f"constant cross-check {name}: mirror "
         f"{getattr(cg, name)} != fixture {want}")

check(cg.gl_light_radius(0) == LIGHT_R_MIN, "gl_light_radius(0) == GL_LIGHT_R_MIN")
check(cg.gl_dark_press(OIL_MAX, 10 * LIGHT_R_MIN) is False
      or cg.gl_dark_press(OIL_MAX, 10 * LIGHT_R_MIN) == 0,
      "gl_dark_press identically falsy at GL_OIL_MAX (LIT leg)")
check(bool(cg.gl_dark_press(0, LIGHT_R_MIN + 1)), "gl_dark_press(0, 24px+1) fires")
check(not cg.gl_dark_press(0, LIGHT_R_MIN), "gl_dark_press(0, 24px) does not fire")

# ------------------------------------------------------------- stagger table
STAG = [bytes(1 if cg.gl_shambler_staggers(i, f) else 0 for f in range(NF))
        for i in range(CAP)]
stag_mean_num = sum(sum(row) for row in STAG)
n_grid = CAP * NF
# 3-sigma band around 1/4 on the pinned 86,400-cell grid (exact integer bound:
# |mean - 1/4| <= 3*sqrt(3/16/n)  <=>  (16*num - 4*n)^2 <= 9*48*n)
hard((16 * stag_mean_num - 4 * n_grid) ** 2 <= 9 * 48 * n_grid,
     f"stagger-rate identity: {stag_mean_num}/{n_grid} outside 3 sigma of 1/4")

# --------------------------------------------------------------- policy tables
TIE_ORDER = FIX["policies"]["KITE_GRAD"]["tie_order"]
KDELTA = [tuple(FIX["policies"]["KITE_GRAD"]["keyset_deltas"][k]) for k in TIE_ORDER]
hard(KDELTA == [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0),
                (-1, -1), (0, 0)], "keyset deltas in pinned tie order")
WPS = [(x * ONE, y * ONE) for x, y in FIX["policies"]["KITE_PERIM"]["waypoints_px"]]
ADV = 2 * ONE  # waypoint advance radius, 2 px

EPS_LIST = [Fraction(1, 16), Fraction(1, 4)]
hard([str(e) for e in EPS_LIST] == FIX["arm_s"]["grid"]["eps"], "eps grid matches fixture")

SEEDS = FIX["registry_seeds"]
hard(SEEDS["main"] == 20261293 and SEEDS["stability"] == 20261294
     and SEEDS["reporting"] == 20261295 and SEEDS["aux"] == 20261296,
     "registry seeds 20261293-96")
hard(max(SEEDS["main"], SEEDS["stability"], SEEDS["reporting"], SEEDS["aux"])
     == 20261296 and min(SEEDS["main"], SEEDS["stability"], SEEDS["reporting"],
                         SEEDS["aux"]) > SEEDS["prior_high_water"],
     "seeds strictly above prior high-water, nothing above 20261296")

# ------------------------------------------------------------ spawn identities
_spawn_cache = {}
_spawn_checked = set()
SPAWN_CHECKS = {"spawns": 0}


def on_perimeter(x, y):
    return (XMIN <= x <= XMAX and YMIN <= y <= YMAX
            and (x == XMIN or x == XMAX or y == YMIN or y == YMAX))


def night_spawns(seed, night):
    key = (seed, night)
    got = _spawn_cache.get(key)
    if got is None:
        total = cg.gl_wave_count(night)
        hard(total == min(2 * night - 1, CAP),
             f"gl_wave_count({night}) == min(2n-1, 24)")
        sf = [cg.gl_spawn_frame(night, i) for i in range(total)]
        sp = [cg.gl_spawn_of_night(seed, night, i) for i in range(total)]
        if key not in _spawn_checked:
            _spawn_checked.add(key)
            prev = 0
            ok_perim = ok_safe = ok_frames = True
            for i in range(total):
                x, y = sp[i]
                ok_perim &= on_perimeter(x, y)
                ok_safe &= cg.gl_chebyshev(x, y, PSX, PSY) >= SAFE
                ok_frames &= prev <= sf[i] < SPAN
                prev = sf[i]
                SPAWN_CHECKS["spawns"] += 1
            hard(ok_perim, f"spawn perimeter identity seed {seed} night {night}")
            hard(ok_safe, f"spawn safe-radius identity seed {seed} night {night}")
            hard(ok_frames,
                 f"spawn frames non-decreasing < 2400 seed {seed} night {night}")
        got = (total, sf, sp)
        _spawn_cache[key] = got
    return got


# ------------------------------------------------------------------ fast engine
def run_night(seed, night, policy, dark, shove, rng=None, eps=None,
              probe=None):
    """One night. Returns (death_frame, min_gap, connects, frames, draws,
    dark_viol, crowd) — death_frame 0 = survived; crowd = final positions.

    policy: 'perim' | 'grad'.  rng: counting-RNG for Arm S noise (eps = float
    probability).  probe: deterministic gl_hash-driven u stream (twin-engine
    noise-path gate; no registry draw).
    """
    total, sf, sp = night_spawns(seed, night)
    zx, zy, zst = [], [], []
    zc = 0
    # start_night: player at the lamppost, empty crowd, spawn_due once
    px, py = PSX, PSY
    while zc < total and sf[zc] <= 0:
        zx.append(sp[zc][0]); zy.append(sp[zc][1]); zst.append(0)
        zc += 1
    wi = 0
    cd = 0
    connects = 0
    dark_viol = 0
    draws = 0
    min_gap = 1 << 60
    stag = STAG
    epsf = float(eps) if eps is not None else 0.0
    for f in range(NF):
        # --- policy keys from the frame-start state (pre-spawn) -------------
        if policy == "perim":
            wx, wy = WPS[wi]
            dxw = wx - px; dyw = wy - py
            if (dxw if dxw >= 0 else -dxw) <= ADV and (dyw if dyw >= 0 else -dyw) <= ADV:
                wi = (wi + 1) % 4
                wx, wy = WPS[wi]
                dxw = wx - px; dyw = wy - py
            mx = (1 if dxw > DEADZONE else 0) - (1 if dxw < -DEADZONE else 0)
            my = (1 if dyw > DEADZONE else 0) - (1 if dyw < -DEADZONE else 0)
        else:
            m0 = 1 << 60
            for i in range(zc):
                dx = px - zx[i]; dy = py - zy[i]
                adx = dx if dx >= 0 else -dx
                ady = dy if dy >= 0 else -dy
                ch = adx if adx > ady else ady
                if ch < m0: m0 = ch
            # exact pruning: a Shambler with Chebyshev > m0 + 2*GL_PLAYER_SPEED
            # can never be the argmin for any candidate move (each move shifts
            # Chebyshev by at most GL_PLAYER_SPEED, and the frame-start argmin
            # bounds every candidate's min from above by m0 + GL_PLAYER_SPEED)
            lim = m0 + 2 * PSPD
            cand = [i for i in range(zc)
                    if (px - zx[i] if px >= zx[i] else zx[i] - px) <= lim
                    and (py - zy[i] if py >= zy[i] else zy[i] - py) <= lim]
            best = -1
            mx = my = 0
            for cmx, cmy in KDELTA:
                spd = PDIAG if (cmx and cmy) else PSPD
                nx = px + cmx * spd
                if nx < XMIN: nx = XMIN
                elif nx > XMAX: nx = XMAX
                ny = py + cmy * spd
                if ny < YMIN: ny = YMIN
                elif ny > YMAX: ny = YMAX
                sc = 1 << 60
                for i in cand:
                    dx = nx - zx[i]; dy = ny - zy[i]
                    adx = dx if dx >= 0 else -dx
                    ady = dy if dy >= 0 else -dy
                    ch = adx if adx > ady else ady
                    if ch < sc: sc = ch
                if sc > best:
                    best = sc; mx, my = cmx, cmy
        a_press = False
        if shove and cd == 0 and zc > 0:
            nd = 1 << 60
            for i in range(zc):
                dx = px - zx[i]; dy = py - zy[i]
                adx = dx if dx >= 0 else -dx
                ady = dy if dy >= 0 else -dy
                ch = adx if adx > ady else ady
                if ch < nd: nd = ch
            a_press = nd <= SHOVE_RANGE
        # --- execution noise (Arm S): one draw per frame ---------------------
        if rng is not None:
            u = rng.random()
            draws += 1
            if u < epsf:
                k = int(u / epsf * 9)
                if k > 8: k = 8
                mx, my = KDELTA[k]
        elif probe is not None:
            u = cg.gl_hash(probe, f) / 4294967296.0
            if u < epsf:
                k = int(u / epsf * 9)
                if k > 8: k = 8
                mx, my = KDELTA[k]
        # --- spawn due --------------------------------------------------------
        while zc < total and sf[zc] <= f:
            zx.append(sp[zc][0]); zy.append(sp[zc][1]); zst.append(0)
            zc += 1
        # --- player step ------------------------------------------------------
        if mx or my:
            spd = PDIAG if (mx and my) else PSPD
            px += mx * spd
            if px < XMIN: px = XMIN
            elif px > XMAX: px = XMAX
            py += my * spd
            if py < YMIN: py = YMIN
            elif py > YMAX: py = YMAX
        # --- shove verb (cooldown pre-decrement, attempt arms hit or whiff) --
        if shove:
            if cd > 0:
                cd -= 1
            if a_press and cd == 0:
                cd = SHOVE_CD
                ni = 0
                nd = 1 << 60
                for i in range(zc):
                    dx = px - zx[i]; dy = py - zy[i]
                    adx = dx if dx >= 0 else -dx
                    ady = dy if dy >= 0 else -dy
                    ch = adx if adx > ady else ady
                    if ch < nd: nd = ch; ni = i
                if zc > 0 and nd <= SHOVE_RANGE:
                    dx = zx[ni] - px; dy = zy[ni] - py
                    sx = (1 if dx > DEADZONE else 0) - (1 if dx < -DEADZONE else 0)
                    sy = (1 if dy > DEADZONE else 0) - (1 if dy < -DEADZONE else 0)
                    x = zx[ni] + sx * SHOVE_PUSH
                    if x < XMIN: x = XMIN
                    elif x > XMAX: x = XMAX
                    y = zy[ni] + sy * SHOVE_PUSH
                    if y < YMIN: y = YMIN
                    elif y > YMAX: y = YMAX
                    zx[ni] = x; zy[ni] = y; zst[ni] = SHOVE_STUN
                    connects += 1
        # --- the dead's step + min-gap + contact ------------------------------
        g = 1 << 60
        for i in range(zc):
            if zst[i] > 0:
                zst[i] -= 1
                dx = px - zx[i]; dy = py - zy[i]
                adx = dx if dx >= 0 else -dx
                ady = dy if dy >= 0 else -dy
                ch = adx if adx > ady else ady
                if ch < g: g = ch
                continue
            x = zx[i]; y = zy[i]
            dx = px - x; dy = py - y
            adx = dx if dx >= 0 else -dx
            ady = dy if dy >= 0 else -dy
            ch = adx if adx > ady else ady
            if stag[i][f]:
                if not (dark and ch > LIGHT_R_MIN):
                    # stagger holds (no stride). Measured DARK identity: the
                    # inline press test must agree with the mirror's own
                    # gl_dark_press at oil 0 on every DARK-leg no-stride —
                    # a no-stride the mirror says should have been pressed
                    # into a stride is a violation.
                    if dark and cg.gl_dark_press(0, ch):
                        dark_viol += 1
                    if ch < g: g = ch
                    continue
                # dark press cancels the stagger: fall through to stride
            mvx = (1 if dx > DEADZONE else 0) - (1 if dx < -DEADZONE else 0)
            mvy = (1 if dy > DEADZONE else 0) - (1 if dy < -DEADZONE else 0)
            spd = ZDIAG if (mvx and mvy) else ZSPD
            x += mvx * spd
            if x < XMIN: x = XMIN
            elif x > XMAX: x = XMAX
            y += mvy * spd
            if y < YMIN: y = YMIN
            elif y > YMAX: y = YMAX
            zx[i] = x; zy[i] = y
            dx = px - x; dy = py - y
            adx = dx if dx >= 0 else -dx
            ady = dy if dy >= 0 else -dy
            ch = adx if adx > ady else ady
            if ch < g: g = ch
        if g < min_gap:
            min_gap = g
        if g < CONTACT:
            return (f + 1, min_gap, connects, f + 1, draws, dark_viol,
                    (px, py, tuple(zx), tuple(zy)))
    return (0, min_gap, connects, NF, draws, dark_viol,
            (px, py, tuple(zx), tuple(zy)))


# ------------------------------------------------------------ reference engine
def ref_run_night(seed, night, policy, dark, shove, probe=None, eps=None):
    """Independently-written reference: mirror functions only, structured on
    main.c (spawn_due -> player step -> do_shove_verb -> step_the_dead ->
    the_cold_hands). Twin-engine gate: must equal run_night exactly."""
    oil_for_press = 0 if dark else OIL_MAX
    total = cg.gl_wave_count(night)
    zombies = []  # [x, y, stun]
    px, py = PSX, PSY
    z_count = 0

    def spawn_due(frame):
        nonlocal z_count
        while (z_count < total
               and cg.gl_spawn_frame(night, z_count) <= frame):
            sx, sy = cg.gl_spawn_of_night(seed, night, z_count)
            zombies.append([sx, sy, 0])
            z_count += 1

    spawn_due(0)  # start_night
    wp_i = 0
    shove_cd = 0
    connects = 0
    min_gap = 1 << 60
    for run_frame in range(NF):
        # keys scanned at loop top (frame-start state)
        if policy == "perim":
            tx, ty = WPS[wp_i]
            if cg.gl_chebyshev(px, py, tx, ty) <= ADV:
                wp_i = (wp_i + 1) % 4
                tx, ty = WPS[wp_i]
            keys_r = (tx - px) > DEADZONE
            keys_l = (tx - px) < -DEADZONE
            keys_d = (ty - py) > DEADZONE
            keys_u = (ty - py) < -DEADZONE
        else:
            scored = []
            for kname, (dxk, dyk) in zip(TIE_ORDER, KDELTA):
                nx, ny = cg.gl_player_step(px, py, dyk < 0, dyk > 0,
                                           dxk < 0, dxk > 0)
                s = min(cg.gl_chebyshev(nx, ny, z[0], z[1]) for z in zombies)
                scored.append(s)
            pick = max(range(9), key=lambda j: (scored[j], -j))
            dxk, dyk = KDELTA[pick]
            keys_u, keys_d = dyk < 0, dyk > 0
            keys_l, keys_r = dxk < 0, dxk > 0
        a_down = False
        if shove and shove_cd == 0 and zombies:
            nearest_d = min(cg.gl_chebyshev(px, py, z[0], z[1])
                            for z in zombies)
            a_down = nearest_d <= SHOVE_RANGE
        if probe is not None:
            u = cg.gl_hash(probe, run_frame) / 4294967296.0
            if u < float(eps):
                k = min(8, int(u / float(eps) * 9))
                dxk, dyk = KDELTA[k]
                keys_u, keys_d = dyk < 0, dyk > 0
                keys_l, keys_r = dxk < 0, dxk > 0
        spawn_due(run_frame)
        px, py = cg.gl_player_step(px, py, keys_u, keys_d, keys_l, keys_r)
        if shove:
            if shove_cd > 0:
                shove_cd -= 1
            if a_down and shove_cd == 0:
                shove_cd = SHOVE_CD
                nearest, best = 0, 1 << 60
                for i, z in enumerate(zombies):
                    d = cg.gl_chebyshev(px, py, z[0], z[1])
                    if d < best:
                        best, nearest = d, i
                if zombies:
                    hit, nx, ny = cg.gl_shove(px, py, zombies[nearest][0],
                                              zombies[nearest][1])
                    if hit:
                        zombies[nearest][0] = nx
                        zombies[nearest][1] = ny
                        zombies[nearest][2] = SHOVE_STUN
                        connects += 1
        # step_the_dead
        for zid, z in enumerate(zombies):
            if z[2] > 0:
                z[2] -= 1
                continue
            if (not cg.gl_shambler_staggers(zid, run_frame)
                    or cg.gl_dark_press(oil_for_press,
                                        cg.gl_chebyshev(px, py, z[0], z[1]))):
                z[0], z[1] = cg.gl_shambler_stride(z[0], z[1], px, py)
        gap = min(cg.gl_chebyshev(px, py, z[0], z[1]) for z in zombies)
        min_gap = min(min_gap, gap)
        if any(cg.gl_contact(px, py, z[0], z[1]) for z in zombies):
            return (run_frame + 1, min_gap, connects,
                    (px, py, tuple(z[0] for z in zombies),
                     tuple(z[1] for z in zombies)))
    return (0, min_gap, connects,
            (px, py, tuple(z[0] for z in zombies),
             tuple(z[1] for z in zombies)))


# ================================================================ GATE: proof 2
worst_idle = 0
ok_mono = ok_bound = True
for seed in range(64):
    for night in range(1, 5):
        zx0, zy0 = cg.gl_spawn_of_night(seed, night, 0)
        dist = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
        for frame in range(400):
            if cg.gl_contact(PSX, PSY, zx0, zy0):
                worst_idle = max(worst_idle, frame)
                break
            zx0, zy0 = cg.gl_shambler_step(zx0, zy0, PSX, PSY, 0, frame)
            nd = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
            if nd > dist:
                ok_mono = False
            dist = nd
        else:
            ok_bound = False
hard(ok_mono, "IDLE proof-2 monotone chase (index 0)")
hard(ok_bound, "IDLE proof-2 contact within 400 frames (index 0)")

# every-spawn extension (registered): every scheduled index, id = index
ok_mono = ok_bound = True
idle_chases = 0
for seed in range(64):
    for night in range(1, 5):
        total = cg.gl_wave_count(night)
        for index in range(total):
            zx0, zy0 = cg.gl_spawn_of_night(seed, night, index)
            dist = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
            idle_chases += 1
            for frame in range(400):
                if cg.gl_contact(PSX, PSY, zx0, zy0):
                    worst_idle = max(worst_idle, frame)
                    break
                zx0, zy0 = cg.gl_shambler_step(zx0, zy0, PSX, PSY, index, frame)
                nd = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
                if nd > dist:
                    ok_mono = False
                dist = nd
            else:
                ok_bound = False
hard(ok_mono, "IDLE every-spawn monotone chase")
hard(ok_bound, "IDLE every-spawn contact within 400 frames")

# ====================================================== GATE: press dominance
ok_press = True
worst_pressed = 0
for seed in range(64):
    for night in range(1, 5):
        sx0, sy0 = cg.gl_spawn_of_night(seed, night, 0)
        contact_frame = {}
        for mode in ("lit", "dark"):
            zx0, zy0 = sx0, sy0
            dist = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
            for frame in range(400):
                if cg.gl_contact(PSX, PSY, zx0, zy0):
                    contact_frame[mode] = frame
                    break
                if (not cg.gl_shambler_staggers(0, frame)
                        or (mode == "dark"
                            and cg.gl_dark_press(0, cg.gl_chebyshev(
                                PSX, PSY, zx0, zy0)))):
                    zx0, zy0 = cg.gl_shambler_stride(zx0, zy0, PSX, PSY)
                nd = cg.gl_chebyshev(PSX, PSY, zx0, zy0)
                if nd > dist:
                    ok_press = False
                dist = nd
            else:
                ok_press = False
        if "lit" in contact_frame and "dark" in contact_frame:
            if contact_frame["dark"] > contact_frame["lit"]:
                ok_press = False
            worst_pressed = max(worst_pressed, contact_frame["dark"])
hard(ok_press, "press-dominance spot gate (proof 11d range)")

# ============================================================ GATE: twin engines
twin_cells = []
for policy, shove in (("perim", False), ("perim", True),
                      ("grad", False), ("grad", True)):
    for dark in (False, True):
        for night, seeds in ((13, (0, 17, 31)), (24, (5,))):
            for s in seeds:
                twin_cells.append((policy, shove, dark, night, s))
ok_twin = True
for policy, shove, dark, night, s in twin_cells:
    df, mg, cn, _fr, _dr, _dv, crowd = run_night(s, night, policy, dark, shove)
    rdf, rmg, rcn, rcrowd = ref_run_night(s, night, policy, dark, shove)
    if (df, mg, cn, crowd) != (rdf, rmg, rcn, rcrowd):
        ok_twin = False
        print(f"twin-engine mismatch at {policy}/{shove}/{dark}/{night}/{s}: "
              f"fast {(df, mg, cn)} ref {(rdf, rmg, rcn)}")
hard(ok_twin, f"twin engines identical on {len(twin_cells)} subsample cells")

# noise-path replay equivalence (deterministic gl_hash probe, no registry draw)
df, mg, cn, _fr, _dr, _dv, crowd = run_night(
    0, 24, "perim", False, False, probe=0x5EED, eps=Fraction(1, 16))
rdf, rmg, rcn, rcrowd = ref_run_night(
    0, 24, "perim", False, False, probe=0x5EED, eps=Fraction(1, 16))
hard((df, mg, cn, crowd) == (rdf, rmg, rcn, rcrowd),
     "twin engines identical on the noise-path probe replay")

# ================================================================ Arm D census
POLICIES_PERIM = [("KITE-PERIM", "perim", False), ("SHOVE-PERIM", "perim", True)]
POLICIES_GRAD = [("KITE-GRAD", "grad", False), ("SHOVE-GRAD", "grad", True)]
NIGHTS_PERIM = FIX["arm_d"]["perim_grid"]["nights"]
NIGHTS_GRAD = FIX["arm_d"]["grad_grid"]["nights"]
OILS = [("LIT", False), ("DARK", True)]

census = {}          # (policy, oil, night) -> dict
armd_frames = 0
armd_dark_viol = 0


def quartiles(vals):
    v = sorted(vals)
    n = len(v)
    return [v[(n - 1) // 4], v[(n - 1) // 2], v[(3 * (n - 1)) // 4]]


def census_cell(pname, pkind, shove, oname, dark, night, n_seeds):
    global armd_frames, armd_dark_viol
    deaths, gaps, conn = [], [], 0
    surv = 0
    cell_viol = 0
    for s in range(n_seeds):
        df, mg, cn, fr, _dr, dv, _crowd = run_night(s, night, pkind, dark, shove)
        armd_frames += fr
        cell_viol += dv
        conn += cn
        gaps.append(mg)
        if df == 0:
            surv += 1
        else:
            deaths.append(df)
    armd_dark_viol += cell_viol
    hard(cell_viol == 0,
         f"DARK zero-stagger identity, cell ({pname},{oname},{night})")
    census[(pname, oname, night)] = {
        "surv_count": surv,
        "n_seeds": n_seeds,
        "SURV": str(Fraction(surv, n_seeds)),
        "median_death_frame": (sorted(deaths)[(len(deaths) - 1) // 2]
                               if deaths else None),
        "min_gap_quartiles_subpx": quartiles(gaps),
        "shove_connects": conn,
    }


for pname, pkind, shove in POLICIES_PERIM:
    for oname, dark in OILS:
        for night in NIGHTS_PERIM:
            census_cell(pname, pkind, shove, oname, dark, night, 128)
for pname, pkind, shove in POLICIES_GRAD:
    for oname, dark in OILS:
        for night in NIGHTS_GRAD:
            census_cell(pname, pkind, shove, oname, dark, night, 32)

# ramp leg (reporting-only): KITE-PERIM x LIT x nights 1..12 x seeds 0..127
ramp = {}
for night in range(1, 13):
    surv = 0
    deaths = []
    for s in range(128):
        df, _mg, _cn, fr, _dr, _dv, _crowd = run_night(s, night, "perim",
                                                       False, False)
        armd_frames += fr
        if df == 0:
            surv += 1
        else:
            deaths.append(df)
    ramp[night] = {
        "surv_count": surv, "n_seeds": 128, "SURV": str(Fraction(surv, 128)),
        "median_death_frame": (sorted(deaths)[(len(deaths) - 1) // 2]
                               if deaths else None),
    }

# ================================================================= Arm S noise
class CountingRNG:
    __slots__ = ("r", "n")

    def __init__(self, seed):
        self.r = random.Random(seed)
        self.n = 0

    def random(self):
        self.n += 1
        return self.r.random()


NOISE_POLICIES = [("KITE-PERIM", "perim"), ("KITE-GRAD", "grad")]
NOISE_NIGHTS = FIX["arm_s"]["grid"]["nights"]


def noise_pass(registry_seed, m_reps):
    rng = CountingRNG(registry_seed)
    legs = {}
    for pname, pkind in NOISE_POLICIES:
        for oname, dark in OILS:
            for night in NOISE_NIGHTS:
                for eps in EPS_LIST:
                    surv = 0
                    frames = 0
                    leg_viol = 0
                    draws_before = rng.n
                    for s in range(32):
                        for _rep in range(m_reps):
                            df, _mg, _cn, fr, dr, dv, _cr = run_night(
                                s, night, pkind, dark, False,
                                rng=rng, eps=eps)
                            frames += fr
                            leg_viol += dv
                            if df == 0:
                                surv += 1
                    hard(leg_viol == 0,
                         f"DARK zero-stagger identity, noise leg "
                         f"({pname},{oname},{night},{eps})")
                    leg_draws = rng.n - draws_before
                    hard(leg_draws == frames,
                         f"draw-count sentinel ({pname},{oname},{night},{eps}): "
                         f"{leg_draws} draws != {frames} frames")
                    legs[(pname, oname, night, str(eps))] = {
                        "surv_count": surv,
                        "n_reps": 32 * m_reps,
                        "SURV": str(Fraction(surv, 32 * m_reps)),
                        "frames": frames,
                        "draws": leg_draws,
                    }
    return legs, rng.n


noise_main, draws_main = noise_pass(SEEDS["main"], FIX["arm_s"]["M_main"])
noise_stab, draws_stab = noise_pass(SEEDS["stability"], FIX["arm_s"]["M_stability"])
noise_rep, draws_rep = noise_pass(SEEDS["reporting"], FIX["arm_s"]["M_reporting"])
aux_rng = CountingRNG(SEEDS["aux"])
hard(aux_rng.n == 0, "aux seed 20261296: ZERO draws")

# ============================================================ decision evaluators
BAND_CENSUS = Fraction(99, 100)
BAND_NOISE = Fraction(90, 100)
BAND_APPROVE = Fraction(50, 100)
DECISION_NIGHTS = {p: tuple(v) for p, v in FIX["decision"]["decision_nights"].items()}


def evaluator_a(cens, noise):
    """Imperative twin A."""
    # REJECT, checked FIRST
    reject_census = True
    for n in DECISION_NIGHTS["KITE-PERIM"]:
        c = cens[("KITE-PERIM", "LIT", n)]
        if Fraction(c["surv_count"], c["n_seeds"]) < BAND_CENSUS:
            reject_census = False
    leg = noise[("KITE-PERIM", "LIT", 24, "1/16")]
    reject_noise = Fraction(leg["surv_count"], leg["n_reps"]) >= BAND_NOISE
    if reject_census and reject_noise:
        return "reject"
    # APPROVE
    approve = True
    for pol in ("KITE-PERIM", "SHOVE-PERIM", "KITE-GRAD", "SHOVE-GRAD"):
        for oil in ("LIT", "DARK"):
            hit = False
            for n in DECISION_NIGHTS[pol]:
                c = cens[(pol, oil, n)]
                if Fraction(c["surv_count"], c["n_seeds"]) < BAND_APPROVE:
                    hit = True
            if not hit:
                approve = False
    if approve:
        return "approve"
    return "null"


def evaluator_b(cens, noise):
    """Comprehension-built twin B (independently written)."""
    surv = {k: Fraction(v["surv_count"], v["n_seeds"]) for k, v in cens.items()}
    nleg = noise[("KITE-PERIM", "LIT", 24, "1/16")]
    fires_reject = (
        min(surv[("KITE-PERIM", "LIT", n)]
            for n in DECISION_NIGHTS["KITE-PERIM"]) >= BAND_CENSUS
        and Fraction(nleg["surv_count"], nleg["n_reps"]) >= BAND_NOISE)
    fires_approve = all(
        any(surv[(pol, oil, n)] < BAND_APPROVE for n in DECISION_NIGHTS[pol])
        for pol in ("KITE-PERIM", "SHOVE-PERIM", "KITE-GRAD", "SHOVE-GRAD")
        for oil in ("LIT", "DARK"))
    return "reject" if fires_reject else ("approve" if fires_approve else "null")


class_main_a = evaluator_a(census, noise_main)
class_main_b = evaluator_b(census, noise_main)
class_stab_a = evaluator_a(census, noise_stab)
class_stab_b = evaluator_b(census, noise_stab)
hard(class_main_a == class_main_b, "twin evaluators agree (main)")
hard(class_stab_a == class_stab_b, "twin evaluators agree (stability)")
hard(class_main_a == class_stab_a,
     f"stability leg (seed {SEEDS['stability']}, M=16) reproduces the ruling: "
     f"main {class_main_a} vs stability {class_stab_a}")
VERDICT = class_main_a

# per-axis survival shares (NULL narrative / reporting)
per_axis = {}
for axis, keysel in (("policy", 0), ("oil", 1), ("night", 2)):
    agg = {}
    for k, v in census.items():
        a = str(k[keysel])
        num, den = agg.get(a, (0, 0))
        agg[a] = (num + v["surv_count"], den + v["n_seeds"])
    per_axis[axis] = {a: str(Fraction(n, d)) for a, (n, d) in sorted(agg.items())}

# ==================================================================== output
def fmt_key(k):
    return " · ".join(str(x) for x in k)


print("VERDICT 050 sim — Gloamline plateau survival ceiling (PROPOSAL 039)")
print(f"mirror sha256 OK: {digest}")
print(f"python: cpython-{sys.version_info[0]}.{sys.version_info[1]} (pinned)")
print(f"stagger grid mean: {stag_mean_num}/{n_grid} (band 3-sigma around 1/4)")
print(f"IDLE regression: {idle_chases} every-spawn chases + 256 proof-2 chases, "
      f"worst contact frame {worst_idle} (bound 400)")
print(f"press-dominance: proof-11d range green, worst pressed contact "
      f"{worst_pressed}")
print(f"spawn identities: {SPAWN_CHECKS['spawns']} census spawns green")
print(f"twin engines: {len(twin_cells)} cells + noise probe replay identical")
print()
print("Arm D census (SURV = survivors/seeds; mdf = median death frame; "
      "gaps q1/q2/q3 subpx; conn = shove connects):")
for k in sorted(census.keys()):
    v = census[k]
    print(f"  {fmt_key(k)}: SURV {v['surv_count']}/{v['n_seeds']} = "
          f"{v['SURV']} · mdf {v['median_death_frame']} · gaps "
          f"{v['min_gap_quartiles_subpx']} · conn {v['shove_connects']}")
print()
print("Ramp leg (KITE-PERIM · LIT, reporting-only):")
for n in sorted(ramp.keys()):
    v = ramp[n]
    print(f"  night {n}: SURV {v['surv_count']}/128 · mdf "
          f"{v['median_death_frame']}")
print()
for name, legs in (("main 20261293 (M=32)", noise_main),
                   ("stability 20261294 (M=16)", noise_stab),
                   ("reporting 20261295 (M=32)", noise_rep)):
    print(f"Arm S noise legs — {name}:")
    for k in sorted(legs.keys()):
        v = legs[k]
        print(f"  {fmt_key(k)}: SURV {v['surv_count']}/{v['n_reps']} = "
              f"{v['SURV']} (draws {v['draws']})")
    print()
print(f"Arm D frames total: {armd_frames} (zero RNG); Arm S draws: "
      f"main {draws_main} / stability {draws_stab} / reporting {draws_rep}; "
      f"aux 20261296 draws: {aux_rng.n}")
print(f"DARK zero-stagger-beyond-24px violations: {armd_dark_viol} (must be 0)")
print()
print("Decision (pre-registered order, REJECT first):")
print(f"  evaluator A main: {class_main_a} · evaluator B main: {class_main_b}")
print(f"  evaluator A stability: {class_stab_a} · evaluator B stability: "
      f"{class_stab_b}")
print(f"RULING: {VERDICT.upper()}")
print(f"per-axis survival shares: {json.dumps(per_axis, sort_keys=True)}")

results = {
    "verdict": VERDICT,
    "mirror_sha256": digest,
    "python": f"cpython-{sys.version_info[0]}.{sys.version_info[1]}",
    "census": {fmt_key(k): v for k, v in sorted(census.items())},
    "ramp_kite_perim_lit": {str(k): v for k, v in sorted(ramp.items())},
    "noise_main_20261293": {fmt_key(k): v for k, v in sorted(noise_main.items())},
    "noise_stability_20261294": {fmt_key(k): v for k, v in sorted(noise_stab.items())},
    "noise_reporting_20261295": {fmt_key(k): v for k, v in sorted(noise_rep.items())},
    "per_axis_survival_shares": per_axis,
    "gates": {
        "stagger_grid_mean": f"{stag_mean_num}/{n_grid}",
        "idle_worst_contact_frame": worst_idle,
        "press_worst_pressed_contact": worst_pressed,
        "spawn_identities_checked": SPAWN_CHECKS["spawns"],
        "twin_engine_cells": len(twin_cells),
        "arm_d_frames": armd_frames,
        "arm_s_draws": {"main": draws_main, "stability": draws_stab,
                        "reporting": draws_rep, "aux": aux_rng.n},
        "dark_zero_stagger_violations": armd_dark_viol,
        "evaluators": {"main": [class_main_a, class_main_b],
                       "stability": [class_stab_a, class_stab_b]},
    },
    "registry_seeds": {"main": SEEDS["main"], "stability": SEEDS["stability"],
                       "reporting": SEEDS["reporting"], "aux": SEEDS["aux"],
                       "new_high_water": 20261296},
}

hard(CHECKS["failed"] == 0, "zero failed self-checks before results write")
results["self_checks"] = {"passed": CHECKS["passed"], "failed": CHECKS["failed"]}
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2, sort_keys=True)
    fh.write("\n")
print(f"SELF-CHECKS: {CHECKS['passed']} passed, {CHECKS['failed']} failed")
sys.exit(0)

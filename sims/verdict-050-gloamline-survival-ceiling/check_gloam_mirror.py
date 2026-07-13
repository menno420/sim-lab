#!/usr/bin/env python3
"""Gloamline host proof (stdlib-only, <2s) — arc slice 10: watch-map polish.

The check-cave.py sibling for Gloamline: a line-for-line Python mirror of
the pure simulation layer in games/gloamline-nds/source/gl_sim.c
(gl_hash / gl_spawn_of_night / gl_player_step / gl_shambler_staggers /
gl_shambler_stride / gl_shambler_step / gl_chebyshev / gl_contact /
gl_wave_count / gl_spawn_frame / gl_shove / gl_barricade_blocks /
gl_planks_at_dawn / gl_cache_of_interlude / gl_cache_grab /
gl_planks_after_grab / gl_oil_burn / gl_light_radius / gl_dark_press /
gl_flask_of_interlude / gl_oil_after_flask / gl_save_checksum /
gl_save_encode / gl_save_decode / gl_record_improves / gl_map_col /
gl_map_row / gl_mark_of_cell / gl_mark_of_touch / gl_gloam_out), proving
the meaningful invariants for EVERY reachable input instead of the
handful a replay touches:

  1. spawn schedule — for seeds 0..255 x nights 1..8 (index 0) PLUS every
     scheduled index of seeds 0..127 x nights 1..13: the spawn is a pure
     deterministic function (recompute-equal), lands ON the fence
     perimeter, inside the arena, and NEVER inside the safe radius of the
     player's night-start position;
  2. chase convergence — from every spawn (seeds 0..63 x nights 1..4), an
     idle player is reached: the Chebyshev distance is monotonically
     non-increasing under gl_shambler_step and contact happens within 400
     frames (the stagger hash can only delay, never stall);
  3. arena containment — under 20,000 frames of hash-driven adversarial
     input (movement AND shove attempts against a full 24-Shambler
     crowd) neither the player nor any Shambler ever leaves the arena;
  4. wave schedule — for nights 1..64: gl_wave_count ramps by +2 per
     night from 1, never exceeds the 24 cap, reaches it at night 13 and
     plateaus; gl_spawn_frame is deterministic, starts every night at
     frame 0, is non-decreasing in index, and finishes strictly inside
     the GL_WAVE_SPAWN_SPAN window (crowd only grows until dawn);
  5. shove — for thousands of hash-generated reachable configurations:
     deterministic (recompute-equal), a miss (outside GL_SHOVE_RANGE)
     never moves the zombie, a hit never pulls it closer, a hit with
     wall room pushes the Chebyshev distance out by exactly
     GL_SHOVE_PUSH, and the result is always inside the arena;
  6. barricade block predicate — for thousands of hash-generated moves:
     deterministic, blocks EXACTLY the enter-moves (new position inside
     GL_BARRICADE_RANGE, old outside), a body already inside may always
     leave, and a no-move step is never blocked (a staggered Shambler
     cannot chew);
  7. barricade no-trap / eventual pressure — the player's trajectory is
     bit-identical with and without barricades on the field (the player
     is never blocked: can't be sealed in, BY CONSTRUCTION), and from
     every spawn (seeds 0..31 x nights 1..4) a Shambler walled off an
     idle player by the full 8-barricade cap still reaches contact
     within a computable bound: every blocked attempt chews exactly 1
     hp, hp is monotone non-increasing, breach frees the slot, and the
     dead ALWAYS get through — a wall is a timer, never a softlock;
  8. plank economy — gl_planks_at_dawn is deterministic, monotone
     non-decreasing in its argument, grants exactly GL_PLANK_DAWN below
     the cap, and never exceeds GL_PLANK_MAX; gl_planks_after_grab the
     same with GL_CACHE_PLANKS.
     (Proof 3's containment run also drives hash-driven B presses, so
     place/repair state is inside the adversarial containment surface.)
  9. cache schedule (slice 6) — for seeds 0..255 x nights 1..13 x every
     cache index: gl_cache_of_interlude is a pure deterministic function
     (recompute-equal) and lands in the interior box inset
     GL_CACHE_INSET from the fence — never ON the spawn perimeter,
     always inside the arena;
 10. interlude honesty (slice 6) — the interlude is never a scam: for
     seeds 0..127 x nights 1..13, a greedy nearest-neighbor walk from
     the lamppost (where SELECT puts the player) over all caches fits
     inside GL_SCAVENGE_FRAMES even under the conservative
     per-frame-progress bound (GL_PLAYER_DIAG Chebyshev units — the
     player's WORST optimal speed), so every cache is reachable in
     principle within the dawn light; and the full loot out-earns the
     flat GL_PLANK_DAWN skip grant it replaces (static). Entry is
     never instant death by construction: SELECT recenters the player
     on the lamppost and returns every Shambler to its own night spawn
     point, and proof 1/1b already show every such spawn is outside
     GL_SAFE_RADIUS of the lamppost;
 11. lantern light + dark press (slice 7) — gl_light_radius is pure,
     monotone non-decreasing in oil, bounded [GL_LIGHT_R_MIN,
     GL_LIGHT_R_MAX], and EXACTLY GL_LIGHT_R_MAX for every oil >=
     GL_OIL_LOW; gl_dark_press matches its truth table for thousands
     of hash-driven (oil, dist) cases and is IDENTICALLY 0 whenever
     oil >= GL_OIL_LOW (the zero-re-pin gate: a fresh lantern's
     GL_OIL_MAX = 3 nights of burn outlasts every pre-slice-7 proof
     window, so the old chase is bit-identical); the shambler-step
     decomposition is exact (step == staggers ? no-op : stride, for
     hash-driven states); and the WORST-CASE pressed chase (empty
     lantern, guttering GL_LIGHT_R_MIN light) still converges from
     every spawn — monotone non-increasing distance, contact within
     the 400-frame bound, and never LATER than the lit chase from the
     same spawn (the press only removes hesitation, it cannot stall);
 12. flask schedule + oil economy (slice 7) — gl_flask_of_interlude is
     pure/interior-box/off-fence like the caches (and independent of
     the cache stream); gl_oil_burn floors at 0; gl_oil_after_flask is
     deterministic, monotone, +GL_OIL_FLASK below the cap, never above
     GL_OIL_MAX; a greedy lamppost walk over ALL interlude pickups
     (caches + flasks) still fits the dawn light; and the economy is
     sustainable-by-choice: one interlude's full flask yield
     (GL_FLASK_COUNT x GL_OIL_FLASK) out-earns one night's burn
     (GL_NIGHT_FRAMES x GL_OIL_BURN), while a skipped interlude gives
     NOTHING back — the pressure is real but never a scripted loss;
 13. synthesized-audio decision layer (slice 8) — gl_amb_tier matches
     its truth table for thousands of hash-driven (is_night, oil,
     press) cases and is ALWAYS plain NIGHT at healthy night oil and
     ALWAYS DAY in daylight (the zero-re-pin gate: audio adds no new
     observable at full light); the drone rows climb strictly in
     frequency with legal duty codes and audible in-range volumes; the
     8 one-shot cue rows are PSG-legal (freq 50..4000 Hz), bounded
     (hold 1..90 frames — no cue hogs the channel), audible, and the
     cue ids are exactly the documented priority ranking that main.c
     and the mirror resolve a multi-event frame with;
 14. best-nights save record (slice 9) — gl_save_encode/gl_save_decode
     roundtrip byte-deterministically over a value grid incl. extremes
     (golden bytes pinned for the CI battery cross-check; the blob is
     exactly one type-2 EEPROM page); EVERY bad blob decodes to the
     fresh table and never anything else — blank chips (all-00 /
     all-FF), every single-byte corruption of a valid blob, and
     wrong-magic / future-version blobs each carrying a VALID
     recomputed checksum (so magic and version reject on their own);
     and gl_record_improves is strictly-better-only over its truth
     table (equal runs write nothing — EEPROM wear discipline);
 15. watch-map chalk mark + watch line (slice 10) — gl_mark_of_cell is
     deterministic, places a strictly-interior yard point for EVERY
     plot cell, and round-trips EXACTLY (gl_map_col/gl_map_row of the
     mark = the very cell — no +-1 smear); every off-plot cell rejects;
     gl_mark_of_touch aliases the cell placement for every pixel of the
     256x192 bottom LCD (no second geometry) and rejects negatives; the
     forward map (moved verbatim from main.c) lands the arena extremes
     on the plot edges; gl_gloam_out matches max(total - spawned, 0)
     over its full reachable truth table.

MIRROR RULE (keep in lockstep): every function and constant below mirrors
games/gloamline-nds/source/gl_sim.c. Any change to the C MUST land here in
the same PR — same discipline as tools/check-cave.py <-> lumen-drift.

Usage: python3 tools/check-gloam.py           # exit 0 = green
"""

import sys

# --- constants (mirror gl_sim.h; fixed point 8.8) ---------------------------
GL_ONE = 256
GL_ARENA_X_MIN = 16 * GL_ONE
GL_ARENA_X_MAX = 239 * GL_ONE
GL_ARENA_Y_MIN = 32 * GL_ONE
GL_ARENA_Y_MAX = 175 * GL_ONE
GL_PLAYER_START_X = 128 * GL_ONE
GL_PLAYER_START_Y = 104 * GL_ONE
GL_PLAYER_SPEED = 384
GL_PLAYER_DIAG = 271
GL_SHAMBLER_SPEED = 192
GL_SHAMBLER_DIAG = 135
GL_AXIS_DEADZONE = 128
GL_CONTACT_RANGE = 10 * GL_ONE
GL_SAFE_RADIUS = 64 * GL_ONE
GL_ZOMBIE_CAP = 24
GL_WAVE_SPAWN_SPAN = 2400
GL_SHOVE_RANGE = 24 * GL_ONE
GL_SHOVE_PUSH = 40 * GL_ONE
GL_SHOVE_STUN = 45
GL_SHOVE_COOLDOWN = 90
GL_BARRICADE_CAP = 8
GL_BARRICADE_HP = 240
GL_BARRICADE_RANGE = 16 * GL_ONE
GL_PLANK_STOCK = 6
GL_PLANK_DAWN = 2
GL_PLANK_MAX = 9
GL_SCAVENGE_FRAMES = 1200
GL_CACHE_COUNT = 5
GL_CACHE_PLANKS = 1
GL_CACHE_RANGE = 12 * GL_ONE
GL_CACHE_INSET = 16 * GL_ONE
GL_CACHE_SALT = 0x5CAF0157
GL_OIL_MAX = 10800
GL_OIL_BURN = 1
GL_OIL_LOW = 3000
GL_LIGHT_R_MAX = 80 * GL_ONE
GL_LIGHT_R_MIN = 24 * GL_ONE
GL_FLASK_COUNT = 2
GL_OIL_FLASK = 3600
GL_FLASK_SALT = 0xF1A5C01D
GL_AMB_TIER_DAY = 0
GL_AMB_TIER_NIGHT = 1
GL_AMB_TIER_GUTTER = 2
GL_AMB_TIER_PRESS = 3
GL_AMB_TIERS = 4
GL_CUE_NONE = 0
GL_CUE_SHOVE = 1
GL_CUE_PLANK = 2
GL_CUE_CACHE = 3
GL_CUE_FLASK = 4
GL_CUE_BREACH = 5
GL_CUE_NIGHTFALL = 6
GL_CUE_DAWN = 7
GL_CUE_DEATH = 8
GL_CUE_COUNT = 9
GL_CUE_ON_NOISE = 255
GL_SAVE_MAGIC = 0x474C5356
GL_SAVE_VERSION = 1
GL_SAVE_WORDS = 8
GL_SAVE_BYTES = 32
GL_SAVE_ADDR = 0
GL_SAVE_EEPROM_TYPE = 2
GL_SAVE_SALT = 0x53415645
GL_SAVE_POLL_BOUND = 4096
GL_MAP_COL0 = 2
GL_MAP_ROW0 = 5
GL_MAP_COLS = 28
GL_MAP_ROWS = 14
GL_MAP_CELL_PX = 8
GL_NIGHT_FRAMES = 3600

U32 = 0xFFFFFFFF


def gl_hash(a, b):
    """Mirror of gl_hash()."""
    h = ((a * 0x9E3779B9) & U32) ^ ((b * 0x85EBCA6B) & U32)
    h ^= h >> 16
    h = (h * 0x7FEB352D) & U32
    h ^= h >> 15
    h = (h * 0x846CA68B) & U32
    h ^= h >> 16
    return h


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def gl_spawn_of_night(seed, night, index):
    """Mirror of gl_spawn_of_night() -> (x, y)."""
    w = (GL_ARENA_X_MAX - GL_ARENA_X_MIN) // GL_ONE            # 223
    h = (GL_ARENA_Y_MAX - GL_ARENA_Y_MIN) // GL_ONE            # 143
    per = 2 * (w + h)

    p = gl_hash(gl_hash(seed, night), index) % per

    for guard in range(2):
        if p < w:                          # north fence, west -> east
            sx, sy = GL_ARENA_X_MIN + p * GL_ONE, GL_ARENA_Y_MIN
        elif p < w + h:                    # east fence, north -> south
            sx, sy = GL_ARENA_X_MAX, GL_ARENA_Y_MIN + (p - w) * GL_ONE
        elif p < 2 * w + h:                # south fence, east -> west
            sx, sy = GL_ARENA_X_MAX - (p - w - h) * GL_ONE, GL_ARENA_Y_MAX
        else:                              # west fence, south -> north
            sx = GL_ARENA_X_MIN
            sy = GL_ARENA_Y_MAX - (p - 2 * w - h) * GL_ONE

        if (gl_chebyshev(sx, sy, GL_PLAYER_START_X, GL_PLAYER_START_Y)
                >= GL_SAFE_RADIUS or guard == 1):
            return sx, sy
        p = (p + per // 2) % per           # too close: opposite fence point
    raise AssertionError('unreachable')


def gl_player_step(px, py, up, down, left, right):
    """Mirror of gl_player_step() -> (px, py)."""
    dx = (1 if right else 0) - (1 if left else 0)
    dy = (1 if down else 0) - (1 if up else 0)
    speed = GL_PLAYER_DIAG if (dx and dy) else GL_PLAYER_SPEED
    return (_clamp(px + dx * speed, GL_ARENA_X_MIN, GL_ARENA_X_MAX),
            _clamp(py + dy * speed, GL_ARENA_Y_MIN, GL_ARENA_Y_MAX))


def gl_shambler_staggers(zombie_id, frame):
    """Mirror of gl_shambler_staggers()."""
    return (gl_hash(zombie_id, frame) & 3) == 0


def gl_shambler_stride(zx, zy, px, py):
    """Mirror of gl_shambler_stride() -> (zx, zy)."""
    dx = px - zx
    dy = py - zy
    sx = (1 if dx > GL_AXIS_DEADZONE else 0) - (1 if dx < -GL_AXIS_DEADZONE
                                                else 0)
    sy = (1 if dy > GL_AXIS_DEADZONE else 0) - (1 if dy < -GL_AXIS_DEADZONE
                                                else 0)
    speed = GL_SHAMBLER_DIAG if (sx and sy) else GL_SHAMBLER_SPEED
    return (_clamp(zx + sx * speed, GL_ARENA_X_MIN, GL_ARENA_X_MAX),
            _clamp(zy + sy * speed, GL_ARENA_Y_MIN, GL_ARENA_Y_MAX))


def gl_shambler_step(zx, zy, px, py, zombie_id, frame):
    """Mirror of gl_shambler_step() -> (zx, zy)."""
    if gl_shambler_staggers(zombie_id, frame):
        return zx, zy
    return gl_shambler_stride(zx, zy, px, py)


def gl_chebyshev(ax, ay, bx, by):
    """Mirror of gl_chebyshev()."""
    return max(abs(ax - bx), abs(ay - by))


def gl_contact(px, py, zx, zy):
    """Mirror of gl_contact()."""
    return gl_chebyshev(px, py, zx, zy) < GL_CONTACT_RANGE


def gl_wave_count(night):
    """Mirror of gl_wave_count()."""
    count = 2 * night - 1                  # 1, 3, 5, ... ramp
    return GL_ZOMBIE_CAP if count > GL_ZOMBIE_CAP else count


def gl_spawn_frame(night, index):
    """Mirror of gl_spawn_frame()."""
    return index * GL_WAVE_SPAWN_SPAN // gl_wave_count(night)


def gl_shove(px, py, zx, zy):
    """Mirror of gl_shove() -> (connected, zx, zy)."""
    if gl_chebyshev(px, py, zx, zy) > GL_SHOVE_RANGE:
        return 0, zx, zy

    dx = zx - px
    dy = zy - py
    sx = (1 if dx > GL_AXIS_DEADZONE else 0) - (1 if dx < -GL_AXIS_DEADZONE
                                                else 0)
    sy = (1 if dy > GL_AXIS_DEADZONE else 0) - (1 if dy < -GL_AXIS_DEADZONE
                                                else 0)
    return (1,
            _clamp(zx + sx * GL_SHOVE_PUSH, GL_ARENA_X_MIN, GL_ARENA_X_MAX),
            _clamp(zy + sy * GL_SHOVE_PUSH, GL_ARENA_Y_MIN, GL_ARENA_Y_MAX))


def gl_barricade_blocks(bx, by, ox, oy, nx, ny):
    """Mirror of gl_barricade_blocks()."""
    return (gl_chebyshev(nx, ny, bx, by) < GL_BARRICADE_RANGE
            and gl_chebyshev(ox, oy, bx, by) >= GL_BARRICADE_RANGE)


def gl_planks_at_dawn(planks):
    """Mirror of gl_planks_at_dawn()."""
    p = planks + GL_PLANK_DAWN
    return GL_PLANK_MAX if p > GL_PLANK_MAX else p


def gl_cache_of_interlude(seed, night, index):
    """Mirror of gl_cache_of_interlude() -> (x, y)."""
    w = (GL_ARENA_X_MAX - GL_ARENA_X_MIN - 2 * GL_CACHE_INSET) // GL_ONE
    h = (GL_ARENA_Y_MAX - GL_ARENA_Y_MIN - 2 * GL_CACHE_INSET) // GL_ONE

    hx = gl_hash(gl_hash(seed ^ GL_CACHE_SALT, night), index)
    hy = gl_hash(hx, index)

    return (GL_ARENA_X_MIN + GL_CACHE_INSET + (hx % (w + 1)) * GL_ONE,
            GL_ARENA_Y_MIN + GL_CACHE_INSET + (hy % (h + 1)) * GL_ONE)


def gl_cache_grab(px, py, cx, cy):
    """Mirror of gl_cache_grab()."""
    return gl_chebyshev(px, py, cx, cy) < GL_CACHE_RANGE


def gl_planks_after_grab(planks):
    """Mirror of gl_planks_after_grab()."""
    p = planks + GL_CACHE_PLANKS
    return GL_PLANK_MAX if p > GL_PLANK_MAX else p


def gl_oil_burn(oil):
    """Mirror of gl_oil_burn()."""
    return oil - GL_OIL_BURN if oil > GL_OIL_BURN else 0


def gl_light_radius(oil):
    """Mirror of gl_light_radius()."""
    if oil >= GL_OIL_LOW:
        return GL_LIGHT_R_MAX
    return (GL_LIGHT_R_MIN
            + (GL_LIGHT_R_MAX - GL_LIGHT_R_MIN) * oil // GL_OIL_LOW)


def gl_dark_press(oil, dist):
    """Mirror of gl_dark_press()."""
    return oil < GL_OIL_LOW and dist > gl_light_radius(oil)


def gl_flask_of_interlude(seed, night, index):
    """Mirror of gl_flask_of_interlude() -> (x, y)."""
    w = (GL_ARENA_X_MAX - GL_ARENA_X_MIN - 2 * GL_CACHE_INSET) // GL_ONE
    h = (GL_ARENA_Y_MAX - GL_ARENA_Y_MIN - 2 * GL_CACHE_INSET) // GL_ONE

    hx = gl_hash(gl_hash(seed ^ GL_FLASK_SALT, night), index)
    hy = gl_hash(hx, index)

    return (GL_ARENA_X_MIN + GL_CACHE_INSET + (hx % (w + 1)) * GL_ONE,
            GL_ARENA_Y_MIN + GL_CACHE_INSET + (hy % (h + 1)) * GL_ONE)


def gl_oil_after_flask(oil):
    """Mirror of gl_oil_after_flask()."""
    o = oil + GL_OIL_FLASK
    return GL_OIL_MAX if o > GL_OIL_MAX else o


def gl_amb_tier(is_night, oil, press_nearest):
    """Mirror of gl_amb_tier()."""
    if not is_night:
        return GL_AMB_TIER_DAY
    if oil >= GL_OIL_LOW:
        return GL_AMB_TIER_NIGHT             # full light: one sound only
    return GL_AMB_TIER_PRESS if press_nearest else GL_AMB_TIER_GUTTER


# Mirror of GL_AMB_ROWS: { freq Hz, duty code, vol } per tier.
GL_AMB_ROWS = (
    (55, 0, 10),                             # DAY: the moor at dawn
    (65, 1, 18),                             # NIGHT: the gloam hum
    (82, 2, 30),                             # GUTTER: the lamp fails
    (110, 3, 44),                            # PRESS: the dark comes on
)


def gl_amb_freq(tier):
    """Mirror of gl_amb_freq()."""
    return GL_AMB_ROWS[tier if tier < GL_AMB_TIERS else 0][0]


def gl_amb_duty(tier):
    """Mirror of gl_amb_duty()."""
    return GL_AMB_ROWS[tier if tier < GL_AMB_TIERS else 0][1]


def gl_amb_vol(tier):
    """Mirror of gl_amb_vol()."""
    return GL_AMB_ROWS[tier if tier < GL_AMB_TIERS else 0][2]


# Mirror of GL_CUE_ROWS: { freq Hz, len frames, duty|ON_NOISE, vol }.
GL_CUE_ROWS = (
    (0, 0, 0, 0),                            # NONE
    (196, 8, 6, 88),                         # SHOVE: G3 thump, wide duty
    (262, 10, 3, 80),                        # PLANK: C4 knock of wood
    (523, 12, 4, 78),                        # CACHE: C5 pocketed bright
    (784, 14, 4, 84),                        # FLASK: G5 brass slosh
    (900, 20, GL_CUE_ON_NOISE, 100),         # BREACH: splintering noise
    (98, 40, 2, 96),                         # NIGHTFALL: G2 toll
    (392, 50, 4, 90),                        # DAWN: G4 bell
    (220, 60, GL_CUE_ON_NOISE, 112),         # DEATH: the cold rattle
)


def gl_cue_freq(cue):
    """Mirror of gl_cue_freq()."""
    return GL_CUE_ROWS[cue if cue < GL_CUE_COUNT else 0][0]


def gl_cue_len(cue):
    """Mirror of gl_cue_len()."""
    return GL_CUE_ROWS[cue if cue < GL_CUE_COUNT else 0][1]


def gl_cue_duty(cue):
    """Mirror of gl_cue_duty()."""
    return GL_CUE_ROWS[cue if cue < GL_CUE_COUNT else 0][2]


def gl_cue_vol(cue):
    """Mirror of gl_cue_vol()."""
    return GL_CUE_ROWS[cue if cue < GL_CUE_COUNT else 0][3]


def gl_save_checksum(words):
    """Mirror of gl_save_checksum()."""
    h = GL_SAVE_SALT
    for i in range(GL_SAVE_WORDS - 1):
        h = gl_hash(h, words[i])
    return h


def gl_save_encode(best_nights, best_seed):
    """Mirror of gl_save_encode() (returns the blob as bytes)."""
    w = [GL_SAVE_MAGIC, GL_SAVE_VERSION, best_nights & U32, best_seed & U32,
         0, 0, 0, 0]
    w[GL_SAVE_WORDS - 1] = gl_save_checksum(w)
    return b''.join(x.to_bytes(4, 'little') for x in w)


def gl_save_decode(blob):
    """Mirror of gl_save_decode() (returns (ok, best_nights, best_seed);
    on ok == 0 the C leaves its outputs untouched — callers keep the
    fresh table)."""
    w = [int.from_bytes(blob[4 * i:4 * i + 4], 'little')
         for i in range(GL_SAVE_WORDS)]
    if w[0] != GL_SAVE_MAGIC:
        return 0, 0, 0
    if w[1] != GL_SAVE_VERSION:
        return 0, 0, 0
    if w[GL_SAVE_WORDS - 1] != gl_save_checksum(w):
        return 0, 0, 0
    return 1, w[2], w[3]


def gl_record_improves(best_nights, nights):
    """Mirror of gl_record_improves()."""
    return 1 if nights > best_nights else 0


def _div_toward_zero(a, b):
    """C integer division truncates toward zero; Python floors."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def gl_map_col(x):
    """Mirror of gl_map_col()."""
    px = _div_toward_zero(x, GL_ONE)                     # 16..239
    col = GL_MAP_COL0 + _div_toward_zero((px - 16) * GL_MAP_COLS, 224)
    if col < GL_MAP_COL0:
        col = GL_MAP_COL0
    if col > GL_MAP_COL0 + GL_MAP_COLS - 1:
        col = GL_MAP_COL0 + GL_MAP_COLS - 1
    return col


def gl_map_row(y):
    """Mirror of gl_map_row()."""
    py = _div_toward_zero(y, GL_ONE)                     # 32..175
    row = GL_MAP_ROW0 + _div_toward_zero((py - 32) * GL_MAP_ROWS, 144)
    if row < GL_MAP_ROW0:
        row = GL_MAP_ROW0
    if row > GL_MAP_ROW0 + GL_MAP_ROWS - 1:
        row = GL_MAP_ROW0 + GL_MAP_ROWS - 1
    return row


def gl_mark_of_cell(col, row):
    """Mirror of gl_mark_of_cell() -> (ok, x, y)."""
    if (col < GL_MAP_COL0 or col >= GL_MAP_COL0 + GL_MAP_COLS
            or row < GL_MAP_ROW0 or row >= GL_MAP_ROW0 + GL_MAP_ROWS):
        return 0, 0, 0                       # off the plot: no chalk
    x = (16 + ((col - GL_MAP_COL0) * 224 + 224 // 2) // GL_MAP_COLS) \
        * GL_ONE
    y = (32 + ((row - GL_MAP_ROW0) * 144 + 144 // 2) // GL_MAP_ROWS) \
        * GL_ONE
    return 1, x, y


def gl_mark_of_touch(tx, ty):
    """Mirror of gl_mark_of_touch() -> (ok, x, y)."""
    if tx < 0 or ty < 0:
        return 0, 0, 0                       # defensive: no negative cell
    return gl_mark_of_cell(tx // GL_MAP_CELL_PX, ty // GL_MAP_CELL_PX)


def gl_gloam_out(wave_total, spawned):
    """Mirror of gl_gloam_out()."""
    return wave_total - spawned if spawned < wave_total else 0


def gl_rematch_available(best_nights):
    """Mirror of gl_rematch_available()."""
    return 1 if best_nights > 0 else 0


def gl_run_seed(rematch, best_nights, best_seed, latched):
    """Mirror of gl_run_seed()."""
    return (best_seed if rematch and gl_rematch_available(best_nights)
            else latched)


# --- proofs ------------------------------------------------------------------

def on_perimeter(x, y):
    return (x in (GL_ARENA_X_MIN, GL_ARENA_X_MAX)
            and GL_ARENA_Y_MIN <= y <= GL_ARENA_Y_MAX) or \
           (y in (GL_ARENA_Y_MIN, GL_ARENA_Y_MAX)
            and GL_ARENA_X_MIN <= x <= GL_ARENA_X_MAX)


def main():
    failures = 0

    # 1. spawn schedule: pure, on-fence, in-bounds, outside the safe radius.
    spawns = 0
    for seed in range(256):
        for night in range(1, 9):
            x, y = gl_spawn_of_night(seed, night, 0)
            spawns += 1
            if (x, y) != gl_spawn_of_night(seed, night, 0):
                failures += 1
                print(f'FAIL determinism: spawn({seed},{night},0) unstable')
            if not on_perimeter(x, y):
                failures += 1
                print(f'FAIL perimeter: spawn({seed},{night},0) = '
                      f'({x},{y}) is off the fence line')
            if gl_chebyshev(x, y, GL_PLAYER_START_X,
                            GL_PLAYER_START_Y) < GL_SAFE_RADIUS:
                failures += 1
                print(f'FAIL safe radius: spawn({seed},{night},0) = '
                      f'({x},{y}) inside {GL_SAFE_RADIUS}')

    # 2. chase convergence onto an idle player: monotone, bounded.
    chases = 0
    worst = 0
    for seed in range(64):
        for night in range(1, 5):
            zx, zy = gl_spawn_of_night(seed, night, 0)
            px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
            dist = gl_chebyshev(px, py, zx, zy)
            chases += 1
            for frame in range(400):
                if gl_contact(px, py, zx, zy):
                    worst = max(worst, frame)
                    break
                zx, zy = gl_shambler_step(zx, zy, px, py, 0, frame)
                new_dist = gl_chebyshev(px, py, zx, zy)
                if new_dist > dist:
                    failures += 1
                    print(f'FAIL monotone chase: seed {seed} night {night} '
                          f'frame {frame}: {dist} -> {new_dist}')
                    break
                dist = new_dist
            else:
                failures += 1
                print(f'FAIL bounded chase: seed {seed} night {night}: '
                      f'no contact in 400 frames (dist {dist})')

    # 1b. every SCHEDULED index (waves): same spawn invariants hold for
    # index > 0 across the full ramp (night 13 = the 24 cap).
    for seed in range(128):
        for night in range(1, 14):
            for index in range(gl_wave_count(night)):
                x, y = gl_spawn_of_night(seed, night, index)
                spawns += 1
                if (x, y) != gl_spawn_of_night(seed, night, index):
                    failures += 1
                    print(f'FAIL determinism: spawn({seed},{night},{index}) '
                          'unstable')
                if not on_perimeter(x, y):
                    failures += 1
                    print(f'FAIL perimeter: spawn({seed},{night},{index}) = '
                          f'({x},{y}) is off the fence line')
                if gl_chebyshev(x, y, GL_PLAYER_START_X,
                                GL_PLAYER_START_Y) < GL_SAFE_RADIUS:
                    failures += 1
                    print(f'FAIL safe radius: spawn({seed},{night},{index}) '
                          f'= ({x},{y}) inside {GL_SAFE_RADIUS}')

    # 3. arena containment under adversarial hash-driven input — the full
    # 24-Shambler crowd, hash-driven shove attempts (bit 4 = press A at
    # the nearest zombie) AND hash-driven barricade verbs (bit 5 = press
    # B: repair-in-range-else-place, main.c's rule; the plank pocket
    # refills when empty so placements keep happening for all 20k
    # frames), the whole slice-5 state surface. Blocked steps chew.
    px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
    zombies = [list(gl_spawn_of_night(0, 13, i)) + [0]   # [zx, zy, stun]
               for i in range(gl_wave_count(13))]
    barr = []                                            # [bx, by, hp]
    planks = GL_PLANK_STOCK
    for frame in range(20000):
        h = gl_hash(0xADBEEF, frame)
        px, py = gl_player_step(px, py, h & 1, h & 2, h & 4, h & 8)
        if h & 16:
            nearest = min(zombies,
                          key=lambda z: gl_chebyshev(px, py, z[0], z[1]))
            hit, nearest[0], nearest[1] = gl_shove(px, py, nearest[0],
                                                   nearest[1])
            if hit:
                nearest[2] = GL_SHOVE_STUN
        if h & 32:
            if planks == 0:
                planks = GL_PLANK_STOCK        # adversarial refill
            intact = [b for b in barr if b[2] > 0]
            near_b = min(intact,
                         key=lambda b: gl_chebyshev(px, py, b[0], b[1]),
                         default=None)
            if (near_b is not None and gl_chebyshev(px, py, near_b[0],
                                                    near_b[1])
                    <= GL_BARRICADE_RANGE):
                if near_b[2] < GL_BARRICADE_HP:
                    near_b[2] = GL_BARRICADE_HP
                    planks -= 1
            elif len(intact) < GL_BARRICADE_CAP:
                barr = intact + [[px, py, GL_BARRICADE_HP]]
                planks -= 1
        for zid, z in enumerate(zombies):
            if z[2] > 0:
                z[2] -= 1
                continue
            nx, ny = gl_shambler_step(z[0], z[1], px, py, zid, frame)
            blocker = next((b for b in barr if b[2] > 0
                            and gl_barricade_blocks(b[0], b[1], z[0], z[1],
                                                    nx, ny)), None)
            if blocker is not None:
                blocker[2] -= 1
            else:
                z[0], z[1] = nx, ny
        actors = ([('player', px, py)]
                  + [(f'shambler{i}', z[0], z[1])
                     for i, z in enumerate(zombies)]
                  + [(f'barricade{i}', b[0], b[1])
                     for i, b in enumerate(barr) if b[2] > 0])
        for label, x, y in actors:
            if not (GL_ARENA_X_MIN <= x <= GL_ARENA_X_MAX
                    and GL_ARENA_Y_MIN <= y <= GL_ARENA_Y_MAX):
                failures += 1
                print(f'FAIL containment: {label} at ({x},{y}) frame {frame}')

    # 4. wave schedule: ramp, cap, plateau, spawn-frame shape.
    prev_count = 0
    for night in range(1, 65):
        count = gl_wave_count(night)
        expected = min(2 * night - 1, GL_ZOMBIE_CAP)
        if count != expected:
            failures += 1
            print(f'FAIL wave count: night {night}: {count} != {expected}')
        if count < prev_count or count > GL_ZOMBIE_CAP:
            failures += 1
            print(f'FAIL wave ramp/cap: night {night}: {prev_count} -> '
                  f'{count} (cap {GL_ZOMBIE_CAP})')
        if night >= 13 and count != GL_ZOMBIE_CAP:
            failures += 1
            print(f'FAIL wave plateau: night {night}: {count} != cap')
        prev_count = count
        prev_frame = None
        for index in range(count):
            sframe = gl_spawn_frame(night, index)
            if sframe != gl_spawn_frame(night, index):
                failures += 1
                print(f'FAIL spawn-frame determinism: ({night},{index})')
            if index == 0 and sframe != 0:
                failures += 1
                print(f'FAIL spawn frame: night {night} index 0 at {sframe}')
            if prev_frame is not None and sframe < prev_frame:
                failures += 1
                print(f'FAIL spawn order: night {night} index {index}: '
                      f'{prev_frame} -> {sframe}')
            if not 0 <= sframe < GL_WAVE_SPAWN_SPAN:
                failures += 1
                print(f'FAIL spawn window: night {night} index {index}: '
                      f'{sframe} outside [0, {GL_WAVE_SPAWN_SPAN})')
            prev_frame = sframe

    # 5. shove: deterministic, miss = no-op, hit never pulls closer, hit
    # with wall room pushes Chebyshev out by exactly GL_SHOVE_PUSH, and
    # the result stays inside the arena. Configurations are hash-driven
    # reachable states: player anywhere in the arena, zombie offset up to
    # ~2x shove range on each axis but never inside contact range (a
    # contact frame is death, not a shove).
    shoves = 0
    exact_pushes = 0
    for case in range(4096):
        px = GL_ARENA_X_MIN + gl_hash(case, 1) % (GL_ARENA_X_MAX
                                                  - GL_ARENA_X_MIN + 1)
        py = GL_ARENA_Y_MIN + gl_hash(case, 2) % (GL_ARENA_Y_MAX
                                                  - GL_ARENA_Y_MIN + 1)
        span = 4 * GL_SHOVE_RANGE + 1
        zx = _clamp(px + gl_hash(case, 3) % span - 2 * GL_SHOVE_RANGE,
                    GL_ARENA_X_MIN, GL_ARENA_X_MAX)
        zy = _clamp(py + gl_hash(case, 4) % span - 2 * GL_SHOVE_RANGE,
                    GL_ARENA_Y_MIN, GL_ARENA_Y_MAX)
        before = gl_chebyshev(px, py, zx, zy)
        if before < GL_CONTACT_RANGE:
            continue                        # dead, not shoving
        shoves += 1
        hit, nx, ny = gl_shove(px, py, zx, zy)
        if (hit, nx, ny) != gl_shove(px, py, zx, zy):
            failures += 1
            print(f'FAIL shove determinism: case {case}')
        after = gl_chebyshev(px, py, nx, ny)
        if not (GL_ARENA_X_MIN <= nx <= GL_ARENA_X_MAX
                and GL_ARENA_Y_MIN <= ny <= GL_ARENA_Y_MAX):
            failures += 1
            print(f'FAIL shove containment: case {case}: ({nx},{ny})')
        if not hit:
            if before <= GL_SHOVE_RANGE:
                failures += 1
                print(f'FAIL shove range: case {case}: miss at {before}')
            if (nx, ny) != (zx, zy):
                failures += 1
                print(f'FAIL shove miss moved: case {case}')
            continue
        if before > GL_SHOVE_RANGE:
            failures += 1
            print(f'FAIL shove range: case {case}: hit at {before}')
        if after < before:
            failures += 1
            print(f'FAIL shove pulled closer: case {case}: '
                  f'{before} -> {after}')
        room = (GL_ARENA_X_MIN + GL_SHOVE_PUSH <= zx
                <= GL_ARENA_X_MAX - GL_SHOVE_PUSH
                and GL_ARENA_Y_MIN + GL_SHOVE_PUSH <= zy
                <= GL_ARENA_Y_MAX - GL_SHOVE_PUSH)
        if room:
            if after - before != GL_SHOVE_PUSH:
                failures += 1
                print(f'FAIL shove push: case {case}: {before} -> {after} '
                      f'(want +{GL_SHOVE_PUSH})')
            exact_pushes += 1

    # 6. barricade block predicate: deterministic, blocks exactly the
    # enter-moves, a body inside may always leave, a no-move step never
    # blocks (a staggered Shambler cannot chew a barricade).
    block_cases = 0
    blocked_enters = 0
    for case in range(8192):
        bx = GL_ARENA_X_MIN + gl_hash(case, 11) % (GL_ARENA_X_MAX
                                                   - GL_ARENA_X_MIN + 1)
        by = GL_ARENA_Y_MIN + gl_hash(case, 12) % (GL_ARENA_Y_MAX
                                                   - GL_ARENA_Y_MIN + 1)
        span = 4 * GL_BARRICADE_RANGE + 1
        ox = _clamp(bx + gl_hash(case, 13) % span - 2 * GL_BARRICADE_RANGE,
                    GL_ARENA_X_MIN, GL_ARENA_X_MAX)
        oy = _clamp(by + gl_hash(case, 14) % span - 2 * GL_BARRICADE_RANGE,
                    GL_ARENA_Y_MIN, GL_ARENA_Y_MAX)
        step = GL_SHAMBLER_SPEED
        nx = _clamp(ox + (gl_hash(case, 15) % 3 - 1) * step,
                    GL_ARENA_X_MIN, GL_ARENA_X_MAX)
        ny = _clamp(oy + (gl_hash(case, 16) % 3 - 1) * step,
                    GL_ARENA_Y_MIN, GL_ARENA_Y_MAX)
        block_cases += 1
        got = gl_barricade_blocks(bx, by, ox, oy, nx, ny)
        if got != gl_barricade_blocks(bx, by, ox, oy, nx, ny):
            failures += 1
            print(f'FAIL block determinism: case {case}')
        want = (gl_chebyshev(nx, ny, bx, by) < GL_BARRICADE_RANGE
                and gl_chebyshev(ox, oy, bx, by) >= GL_BARRICADE_RANGE)
        if bool(got) != want:
            failures += 1
            print(f'FAIL block truth-table: case {case}: got {got}')
        if got:
            blocked_enters += 1
        if (gl_chebyshev(ox, oy, bx, by) < GL_BARRICADE_RANGE and got):
            failures += 1
            print(f'FAIL block pinning: case {case}: inside body pinned')
        if gl_barricade_blocks(bx, by, ox, oy, ox, oy):
            failures += 1
            print(f'FAIL block stagger: case {case}: no-move step blocked')

    # 7. barricade no-trap / eventual pressure.
    # 7a. the player is NEVER blocked: the player trajectory under 4000
    # hash-driven input frames is bit-identical with an 8-barricade ring
    # on the field and without it (regression tripwire: player movement
    # must never grow a barricade argument without this proof changing).
    ring = [(24, 0), (-24, 0), (0, 24), (0, -24),
            (24, 24), (24, -24), (-24, 24), (-24, -24)]
    trail_with, trail_without = [], []
    for with_barr in (True, False):
        px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
        trail = trail_with if with_barr else trail_without
        for frame in range(4000):
            h = gl_hash(0xB0A7, frame)
            px, py = gl_player_step(px, py, h & 1, h & 2, h & 4, h & 8)
            trail.append((px, py))
    if trail_with != trail_without:
        failures += 1
        print('FAIL no-seal: player trajectory differs with barricades up')
    # 7b. eventual pressure: an idle player walled in by the FULL cap (a
    # legally placeable ring: every pair >= GL_BARRICADE_RANGE apart)
    # is still reached from every spawn — every blocked attempt chews
    # exactly 1 hp, hp is monotone non-increasing, and contact arrives
    # within the travel + chew bound. A wall is a timer, never a
    # softlock.
    pressure_runs = 0
    worst_contact = 0
    bound = 400 + GL_BARRICADE_CAP * GL_BARRICADE_HP * 2
    for seed in range(32):
        for night in range(1, 5):
            px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
            barr = [[px + dx * GL_ONE, py + dy * GL_ONE, GL_BARRICADE_HP]
                    for dx, dy in ring]
            for a in range(len(barr)):
                for b in range(a + 1, len(barr)):
                    if gl_chebyshev(barr[a][0], barr[a][1], barr[b][0],
                                    barr[b][1]) < GL_BARRICADE_RANGE:
                        failures += 1
                        print(f'FAIL ring legality: {a} and {b} overlap')
            zx, zy = gl_spawn_of_night(seed, night, 0)
            pressure_runs += 1
            for frame in range(bound):
                if gl_contact(px, py, zx, zy):
                    worst_contact = max(worst_contact, frame)
                    break
                nx, ny = gl_shambler_step(zx, zy, px, py, 0, frame)
                blocker = next((b for b in barr if b[2] > 0
                                and gl_barricade_blocks(b[0], b[1], zx, zy,
                                                        nx, ny)), None)
                if blocker is not None:
                    hp_before = blocker[2]
                    blocker[2] -= 1
                    if hp_before - blocker[2] != 1 or blocker[2] < 0:
                        failures += 1
                        print(f'FAIL chew math: seed {seed} night {night} '
                              f'frame {frame}')
                else:
                    zx, zy = nx, ny
            else:
                failures += 1
                print(f'FAIL eventual pressure: seed {seed} night {night}: '
                      f'no contact within {bound} frames (walled out '
                      'forever)')

    # 8. plank economy: deterministic, monotone, +GL_PLANK_DAWN (dawn
    # grant) / +GL_CACHE_PLANKS (cache grab) below the cap, never above
    # GL_PLANK_MAX.
    for label, fn, grant in (('plank', gl_planks_at_dawn, GL_PLANK_DAWN),
                             ('grab', gl_planks_after_grab,
                              GL_CACHE_PLANKS)):
        prev = None
        for p in range(GL_PLANK_MAX + 4):
            got = fn(p)
            if got != fn(p):
                failures += 1
                print(f'FAIL {label} determinism: {p}')
            if got != min(p + grant, GL_PLANK_MAX):
                failures += 1
                print(f'FAIL {label} grant: {p} -> {got}')
            if prev is not None and got < prev:
                failures += 1
                print(f'FAIL {label} monotone: {p - 1}:{prev} -> {p}:{got}')
            if got > GL_PLANK_MAX:
                failures += 1
                print(f'FAIL {label} cap: {p} -> {got}')
            prev = got

    # 9. cache schedule (slice 6): pure, interior-box, off the fence.
    caches = 0
    for seed in range(256):
        for night in range(1, 14):
            for index in range(GL_CACHE_COUNT):
                x, y = gl_cache_of_interlude(seed, night, index)
                caches += 1
                if (x, y) != gl_cache_of_interlude(seed, night, index):
                    failures += 1
                    print(f'FAIL cache determinism: '
                          f'({seed},{night},{index}) unstable')
                if not (GL_ARENA_X_MIN + GL_CACHE_INSET <= x
                        <= GL_ARENA_X_MAX - GL_CACHE_INSET
                        and GL_ARENA_Y_MIN + GL_CACHE_INSET <= y
                        <= GL_ARENA_Y_MAX - GL_CACHE_INSET):
                    failures += 1
                    print(f'FAIL cache box: ({seed},{night},{index}) = '
                          f'({x},{y}) outside the inset interior')
                if on_perimeter(x, y):
                    failures += 1
                    print(f'FAIL cache on fence: ({seed},{night},{index})')

    # 10. interlude honesty (slice 6): every cache reachable within the
    # dawn light. Greedy nearest-neighbor from the lamppost (SELECT
    # recenters the player there); conservative per-leg frame cost
    # ceil(dist / GL_PLAYER_DIAG) — GL_PLAYER_DIAG is the player's
    # WORST optimal Chebyshev progress per frame (straight legs move
    # GL_PLAYER_SPEED, faster). No credit taken for the GL_CACHE_RANGE
    # pickup reach.
    routes = 0
    worst_route = 0
    for seed in range(128):
        for night in range(1, 14):
            remaining = [gl_cache_of_interlude(seed, night, i)
                         for i in range(GL_CACHE_COUNT)]
            px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
            frames = 0
            while remaining:
                nxt = min(remaining,
                          key=lambda c: gl_chebyshev(px, py, c[0], c[1]))
                dist = gl_chebyshev(px, py, nxt[0], nxt[1])
                frames += -(-dist // GL_PLAYER_DIAG)     # ceil
                px, py = nxt
                remaining.remove(nxt)
            routes += 1
            worst_route = max(worst_route, frames)
            if frames > GL_SCAVENGE_FRAMES:
                failures += 1
                print(f'FAIL interlude honesty: seed {seed} night {night}: '
                      f'greedy route {frames} > {GL_SCAVENGE_FRAMES}')
    if GL_CACHE_COUNT * GL_CACHE_PLANKS <= GL_PLANK_DAWN:
        failures += 1
        print('FAIL interlude economy: full loot '
              f'{GL_CACHE_COUNT * GL_CACHE_PLANKS} does not out-earn the '
              f'flat skip grant {GL_PLANK_DAWN} it replaces')

    # 11. lantern light + dark press (slice 7).
    # 11a. gl_light_radius: pure, monotone non-decreasing, bounded, and
    # EXACTLY full for every oil >= GL_OIL_LOW (zero-re-pin gate).
    prev_r = None
    for oil in list(range(0, GL_OIL_LOW + 2)) + [GL_OIL_MAX,
                                                 GL_OIL_MAX * 2]:
        r = gl_light_radius(oil)
        if r != gl_light_radius(oil):
            failures += 1
            print(f'FAIL radius determinism: oil {oil}')
        if not GL_LIGHT_R_MIN <= r <= GL_LIGHT_R_MAX:
            failures += 1
            print(f'FAIL radius bounds: oil {oil} -> {r}')
        if oil >= GL_OIL_LOW and r != GL_LIGHT_R_MAX:
            failures += 1
            print(f'FAIL radius inertness: oil {oil} -> {r} != full '
                  f'{GL_LIGHT_R_MAX} (zero-re-pin gate broken)')
        if prev_r is not None and r < prev_r:
            failures += 1
            print(f'FAIL radius monotone: oil {oil}: {prev_r} -> {r}')
        prev_r = r
    # The fresh lantern outlasts every pre-slice-7 proof window: the
    # longest old route burns 2 full nights of PLAYING frames.
    if GL_OIL_MAX - 2 * GL_NIGHT_FRAMES * GL_OIL_BURN < GL_OIL_LOW:
        failures += 1
        print('FAIL oil headroom: a fresh lantern goes LOW inside the '
              '2-night pre-slice-7 proof window — old pins would drift')
    # 11b. dark-press truth table over hash-driven (oil, dist) cases;
    # identically 0 at healthy oil.
    press_cases = 0
    pressed = 0
    for case in range(8192):
        oil = gl_hash(case, 21) % (GL_OIL_MAX + 1)
        dist = gl_hash(case, 22) % (2 * GL_LIGHT_R_MAX + 1)
        press_cases += 1
        got = gl_dark_press(oil, dist)
        if got != gl_dark_press(oil, dist):
            failures += 1
            print(f'FAIL press determinism: case {case}')
        want = oil < GL_OIL_LOW and dist > gl_light_radius(oil)
        if bool(got) != want:
            failures += 1
            print(f'FAIL press truth-table: case {case}: got {got}')
        if oil >= GL_OIL_LOW and got:
            failures += 1
            print(f'FAIL press inertness: case {case}: oil {oil} '
                  '(healthy) pressed — zero-re-pin gate broken')
        if got:
            pressed += 1
    # 11c. the step decomposition is exact: step == staggers ? no-op
    # : stride, for hash-driven reachable states.
    for case in range(4096):
        px = GL_ARENA_X_MIN + gl_hash(case, 23) % (GL_ARENA_X_MAX
                                                   - GL_ARENA_X_MIN + 1)
        py = GL_ARENA_Y_MIN + gl_hash(case, 24) % (GL_ARENA_Y_MAX
                                                   - GL_ARENA_Y_MIN + 1)
        zx = GL_ARENA_X_MIN + gl_hash(case, 25) % (GL_ARENA_X_MAX
                                                   - GL_ARENA_X_MIN + 1)
        zy = GL_ARENA_Y_MIN + gl_hash(case, 26) % (GL_ARENA_Y_MAX
                                                   - GL_ARENA_Y_MIN + 1)
        zid = gl_hash(case, 27) % GL_ZOMBIE_CAP
        frame = gl_hash(case, 28) % (3 * GL_NIGHT_FRAMES)
        want = ((zx, zy) if gl_shambler_staggers(zid, frame)
                else gl_shambler_stride(zx, zy, px, py))
        if gl_shambler_step(zx, zy, px, py, zid, frame) != want:
            failures += 1
            print(f'FAIL step decomposition: case {case}')
    # 11d. worst-case pressed chase (empty lantern, guttering light):
    # from every spawn, an idle player is still reached monotonically
    # within the 400-frame bound, and never LATER than the lit chase —
    # the press removes hesitation, it cannot stall or slow.
    pressed_chases = 0
    worst_pressed = 0
    for seed in range(64):
        for night in range(1, 5):
            sx0, sy0 = gl_spawn_of_night(seed, night, 0)
            px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
            contact_frame = {}
            for mode in ('lit', 'dark'):
                zx, zy = sx0, sy0
                dist = gl_chebyshev(px, py, zx, zy)
                for frame in range(400):
                    if gl_contact(px, py, zx, zy):
                        contact_frame[mode] = frame
                        break
                    if (not gl_shambler_staggers(0, frame)
                            or (mode == 'dark'
                                and gl_dark_press(0, gl_chebyshev(
                                    px, py, zx, zy)))):
                        zx, zy = gl_shambler_stride(zx, zy, px, py)
                    new_dist = gl_chebyshev(px, py, zx, zy)
                    if new_dist > dist:
                        failures += 1
                        print(f'FAIL pressed monotone: seed {seed} night '
                              f'{night} frame {frame} ({mode})')
                        break
                    dist = new_dist
                else:
                    failures += 1
                    print(f'FAIL pressed bounded: seed {seed} night '
                          f'{night} ({mode}): no contact in 400 frames')
            pressed_chases += 1
            if 'lit' in contact_frame and 'dark' in contact_frame:
                if contact_frame['dark'] > contact_frame['lit']:
                    failures += 1
                    print(f'FAIL press never-slower: seed {seed} night '
                          f'{night}: dark {contact_frame["dark"]} > lit '
                          f'{contact_frame["lit"]}')
                worst_pressed = max(worst_pressed, contact_frame['dark'])

    # 12. flask schedule + oil economy (slice 7).
    flasks = 0
    for seed in range(256):
        for night in range(1, 14):
            for index in range(GL_FLASK_COUNT):
                x, y = gl_flask_of_interlude(seed, night, index)
                flasks += 1
                if (x, y) != gl_flask_of_interlude(seed, night, index):
                    failures += 1
                    print(f'FAIL flask determinism: '
                          f'({seed},{night},{index}) unstable')
                if not (GL_ARENA_X_MIN + GL_CACHE_INSET <= x
                        <= GL_ARENA_X_MAX - GL_CACHE_INSET
                        and GL_ARENA_Y_MIN + GL_CACHE_INSET <= y
                        <= GL_ARENA_Y_MAX - GL_CACHE_INSET):
                    failures += 1
                    print(f'FAIL flask box: ({seed},{night},{index}) = '
                          f'({x},{y}) outside the inset interior')
                if on_perimeter(x, y):
                    failures += 1
                    print(f'FAIL flask on fence: ({seed},{night},{index})')
    # oil burn floors at 0; flask top-up deterministic/monotone/capped.
    if gl_oil_burn(0) != 0 or gl_oil_burn(1) != 0 \
            or gl_oil_burn(GL_OIL_MAX) != GL_OIL_MAX - GL_OIL_BURN:
        failures += 1
        print('FAIL oil burn: floor/step broken')
    prev = None
    for oil in range(0, GL_OIL_MAX + 2 * GL_OIL_FLASK, 997):
        got = gl_oil_after_flask(oil)
        if got != gl_oil_after_flask(oil):
            failures += 1
            print(f'FAIL flask top-up determinism: {oil}')
        if got != min(oil + GL_OIL_FLASK, GL_OIL_MAX):
            failures += 1
            print(f'FAIL flask top-up: {oil} -> {got}')
        if prev is not None and got < prev:
            failures += 1
            print(f'FAIL flask top-up monotone: {got} < {prev}')
        prev = got
    # greedy lamppost walk over ALL interlude pickups (caches + flasks)
    # still fits the dawn light, same conservative bound as proof 10.
    full_routes = 0
    worst_full = 0
    for seed in range(128):
        for night in range(1, 14):
            remaining = ([gl_cache_of_interlude(seed, night, i)
                          for i in range(GL_CACHE_COUNT)]
                         + [gl_flask_of_interlude(seed, night, i)
                            for i in range(GL_FLASK_COUNT)])
            px, py = GL_PLAYER_START_X, GL_PLAYER_START_Y
            frames = 0
            while remaining:
                nxt = min(remaining,
                          key=lambda c: gl_chebyshev(px, py, c[0], c[1]))
                frames += -(-gl_chebyshev(px, py, nxt[0], nxt[1])
                            // GL_PLAYER_DIAG)                   # ceil
                px, py = nxt
                remaining.remove(nxt)
            full_routes += 1
            worst_full = max(worst_full, frames)
            if frames > GL_SCAVENGE_FRAMES:
                failures += 1
                print(f'FAIL full-pickup honesty: seed {seed} night '
                      f'{night}: greedy route {frames} > '
                      f'{GL_SCAVENGE_FRAMES}')
    # sustainable-by-choice: one interlude's flasks out-earn one
    # night's burn; the cap keeps hoarding finite.
    if GL_FLASK_COUNT * GL_OIL_FLASK <= GL_NIGHT_FRAMES * GL_OIL_BURN:
        failures += 1
        print('FAIL oil economy: an interlude cannot pay for a night — '
              'the run is a scripted loss')
    if GL_OIL_MAX < GL_OIL_LOW + GL_NIGHT_FRAMES * GL_OIL_BURN:
        failures += 1
        print('FAIL oil economy: a fresh lantern cannot even cover one '
              'night before going LOW')

    # 13. synthesized-audio decision layer (slice 8).
    # 13a. gl_amb_tier truth table over hash-driven (is_night, oil,
    # press) cases; the zero-re-pin gate: at night with healthy oil the
    # tier is ALWAYS plain NIGHT (one sound only — nothing for an old
    # route to hear differently), and daylight is ALWAYS DAY.
    tier_cases = 0
    for case in range(8192):
        is_night = gl_hash(case, 31) & 1
        oil = gl_hash(case, 32) % (GL_OIL_MAX + 1)
        press = gl_hash(case, 33) & 1
        tier_cases += 1
        got = gl_amb_tier(is_night, oil, press)
        if got != gl_amb_tier(is_night, oil, press):
            failures += 1
            print(f'FAIL tier determinism: case {case}')
        want = (GL_AMB_TIER_DAY if not is_night
                else GL_AMB_TIER_NIGHT if oil >= GL_OIL_LOW
                else GL_AMB_TIER_PRESS if press else GL_AMB_TIER_GUTTER)
        if got != want:
            failures += 1
            print(f'FAIL tier truth-table: case {case}: got {got}')
        if is_night and oil >= GL_OIL_LOW and got != GL_AMB_TIER_NIGHT:
            failures += 1
            print(f'FAIL tier inertness: case {case}: healthy-oil night '
                  f'tier {got} != NIGHT — zero-re-pin gate broken')
        if not GL_AMB_TIER_DAY <= got < GL_AMB_TIERS:
            failures += 1
            print(f'FAIL tier bounds: case {case}: {got}')
    # 13b. ambience rows: freq strictly climbs with the tier (the moor
    # hums higher as the night closes in), duty is a legal DutyCycle
    # code, volume audible and inside the 0..127 hardware range.
    prev_f = 0
    for tier in range(GL_AMB_TIERS):
        f, d, v = (gl_amb_freq(tier), gl_amb_duty(tier), gl_amb_vol(tier))
        if (f, d, v) != (gl_amb_freq(tier), gl_amb_duty(tier),
                         gl_amb_vol(tier)):
            failures += 1
            print(f'FAIL amb determinism: tier {tier}')
        if f <= prev_f:
            failures += 1
            print(f'FAIL amb freq climb: tier {tier}: {f} <= {prev_f}')
        if not 0 <= d <= 7:
            failures += 1
            print(f'FAIL amb duty code: tier {tier}: {d}')
        if not 1 <= v <= 127:
            failures += 1
            print(f'FAIL amb volume: tier {tier}: {v}')
        prev_f = f
    if gl_amb_freq(GL_AMB_TIERS + 3) != gl_amb_freq(0):
        failures += 1
        print('FAIL amb out-of-range: bad tier must fall back to DAY')
    # 13c. cue table: row 0 is a no-op; every real cue has a PSG-legal
    # frequency, a bounded channel hold (a cue can never hog the SFX
    # channel), an audible in-range volume, and a legal duty code or
    # the noise-channel marker; ids are exactly the documented priority
    # ranking (death > dawn > nightfall > breach > flask > cache >
    # plank > shove — highest id wins a frame, mirrored in main.c).
    if (gl_cue_freq(GL_CUE_NONE), gl_cue_len(GL_CUE_NONE),
            gl_cue_vol(GL_CUE_NONE)) != (0, 0, 0):
        failures += 1
        print('FAIL cue NONE: row 0 must be a no-op')
    for cue in range(1, GL_CUE_COUNT):
        f, ln = gl_cue_freq(cue), gl_cue_len(cue)
        d, v = gl_cue_duty(cue), gl_cue_vol(cue)
        if (f, ln, d, v) != (gl_cue_freq(cue), gl_cue_len(cue),
                             gl_cue_duty(cue), gl_cue_vol(cue)):
            failures += 1
            print(f'FAIL cue determinism: id {cue}')
        if not 50 <= f <= 4000:
            failures += 1
            print(f'FAIL cue freq: id {cue}: {f} outside [50, 4000]')
        if not 1 <= ln <= 90:
            failures += 1
            print(f'FAIL cue hold: id {cue}: {ln} frames outside [1, 90]')
        if not (0 <= d <= 7 or d == GL_CUE_ON_NOISE):
            failures += 1
            print(f'FAIL cue duty: id {cue}: {d}')
        if not 1 <= v <= 127:
            failures += 1
            print(f'FAIL cue volume: id {cue}: {v}')
    ranking = [GL_CUE_SHOVE, GL_CUE_PLANK, GL_CUE_CACHE, GL_CUE_FLASK,
               GL_CUE_BREACH, GL_CUE_NIGHTFALL, GL_CUE_DAWN, GL_CUE_DEATH]
    if ranking != sorted(ranking) or ranking != list(range(1, 9)):
        failures += 1
        print('FAIL cue priority: ids are not the documented ranking')
    if gl_cue_len(GL_CUE_COUNT + 5) != 0:
        failures += 1
        print('FAIL cue out-of-range: bad id must fall back to the no-op')

    # 14. best-nights save record (slice 9).
    # 14a. encode/decode roundtrip over a value grid incl. extremes:
    # deterministic byte-identical encoding, exact blob size, and the
    # decode returns exactly what was encoded.
    save_cases = 0
    for best in (0, 1, 2, 3, 13, 999, 0xFFFFFFFF):
        for seed in (0, 118, 348, 0xDEADBEEF, 0xFFFFFFFF):
            blob = gl_save_encode(best, seed)
            save_cases += 1
            if blob != gl_save_encode(best, seed):
                failures += 1
                print(f'FAIL save determinism: ({best},{seed})')
            if len(blob) != GL_SAVE_BYTES:
                failures += 1
                print(f'FAIL save size: ({best},{seed}): {len(blob)}')
            if gl_save_decode(blob) != (1, best, seed):
                failures += 1
                print(f'FAIL save roundtrip: ({best},{seed}) -> '
                      f'{gl_save_decode(blob)}')
    # Golden-bytes pin: the "survived night 1, seed 118" record that the
    # CI battery-roundtrip proof reads back out of the DeSmuME battery
    # file — C encoder <-> this mirror drift is caught at byte level.
    if gl_save_encode(1, 118).hex() != ('56534c47' '01000000' '01000000'
                                        '76000000' '00000000' '00000000'
                                        '00000000' '75ed83cd'):
        failures += 1
        print('FAIL save golden bytes: encode(1, 118) drifted')
    # One-page invariants: the blob is exactly the 8 words it claims and
    # sits page-aligned inside one 32-byte type-2 EEPROM page (main.c's
    # save_write_backup relies on never crossing a page boundary).
    if GL_SAVE_BYTES != GL_SAVE_WORDS * 4 or GL_SAVE_BYTES > 32 \
            or GL_SAVE_ADDR % 32 != 0:
        failures += 1
        print('FAIL save layout: blob does not fit one EEPROM page')
    # 14b. rejection = fresh table, never a crash: blank chips (all-00 /
    # all-FF), EVERY single-byte corruption of a valid blob (the spares
    # are inside the checksum too), a wrong-magic blob and a
    # future-version blob EACH WITH A RECOMPUTED (valid) checksum — so
    # magic and version are proven to reject on their own — all decode
    # to (0, _, _).
    rejects = 0
    for label, blob in (('all-00', b'\x00' * GL_SAVE_BYTES),
                        ('all-FF', b'\xff' * GL_SAVE_BYTES)):
        if gl_save_decode(blob)[0] != 0:
            failures += 1
            print(f'FAIL save reject {label}: accepted')
        rejects += 1
    valid = gl_save_encode(3, 12345)
    for i in range(GL_SAVE_BYTES):
        mut = bytearray(valid)
        mut[i] ^= 0xFF
        rejects += 1
        if gl_save_decode(bytes(mut))[0] != 0:
            failures += 1
            print(f'FAIL save reject: byte {i} corruption accepted')
    for label, w0, w1 in (('future-version', GL_SAVE_MAGIC,
                           GL_SAVE_VERSION + 1),
                          ('wrong-magic', gl_hash(GL_SAVE_MAGIC, 1) & U32,
                           GL_SAVE_VERSION)):
        w = [w0, w1, 3, 12345, 0, 0, 0, 0]
        w[GL_SAVE_WORDS - 1] = gl_save_checksum(w)
        crafted = b''.join(x.to_bytes(4, 'little') for x in w)
        rejects += 1
        if gl_save_decode(crafted)[0] != 0:
            failures += 1
            print(f'FAIL save reject {label}: accepted despite a valid '
                  'checksum')
    # 14c. the record moves on STRICTLY better runs only (equal runs
    # write nothing — EEPROM wear discipline), full truth table.
    improve_cases = 0
    for best in list(range(30)) + [0xFFFFFFFE, 0xFFFFFFFF]:
        for nights in list(range(30)) + [0xFFFFFFFE, 0xFFFFFFFF]:
            improve_cases += 1
            if gl_record_improves(best, nights) != (1 if nights > best
                                                    else 0):
                failures += 1
                print(f'FAIL record improves: ({best},{nights})')

    # 15. watch-map chalk mark + watch line (slice 10).
    # 15a. every plot cell places: gl_mark_of_cell is deterministic,
    # returns a strictly-interior arena point (chalk marks a yard spot,
    # never the fence), and ROUND-TRIPS EXACTLY — gl_map_col/gl_map_row
    # of the placed mark give back the very cell (the mark renders in
    # the cell you tapped, no +-1 smear).
    mark_cells = 0
    for col in range(GL_MAP_COL0, GL_MAP_COL0 + GL_MAP_COLS):
        for row in range(GL_MAP_ROW0, GL_MAP_ROW0 + GL_MAP_ROWS):
            ok, mx, my = gl_mark_of_cell(col, row)
            mark_cells += 1
            if (ok, mx, my) != gl_mark_of_cell(col, row):
                failures += 1
                print(f'FAIL mark determinism: cell ({col},{row})')
            if not ok:
                failures += 1
                print(f'FAIL mark placement: plot cell ({col},{row}) '
                      'rejected')
                continue
            if not (GL_ARENA_X_MIN < mx < GL_ARENA_X_MAX
                    and GL_ARENA_Y_MIN < my < GL_ARENA_Y_MAX):
                failures += 1
                print(f'FAIL mark interior: cell ({col},{row}) -> '
                      f'({mx},{my}) not strictly inside the arena')
            if on_perimeter(mx, my):
                failures += 1
                print(f'FAIL mark on fence: cell ({col},{row})')
            if (gl_map_col(mx), gl_map_row(my)) != (col, row):
                failures += 1
                print(f'FAIL mark round-trip: cell ({col},{row}) -> '
                      f'({mx},{my}) -> cell '
                      f'({gl_map_col(mx)},{gl_map_row(my)})')
    # 15b. everything OFF the plot rejects: the border/header/gauge
    # cells around the plot (one full ring plus the console's edges).
    off_cells = 0
    for col in range(-1, 33):
        for row in range(-1, 25):
            inside = (GL_MAP_COL0 <= col < GL_MAP_COL0 + GL_MAP_COLS
                      and GL_MAP_ROW0 <= row < GL_MAP_ROW0 + GL_MAP_ROWS)
            if inside:
                continue
            off_cells += 1
            if gl_mark_of_cell(col, row)[0] != 0:
                failures += 1
                print(f'FAIL mark off-plot: cell ({col},{row}) accepted')
    # 15c. the touch alias covers the WHOLE bottom LCD: every pixel of
    # the 256x192 screen either lands in the plot (and equals the
    # cell's own placement — the alias adds no second geometry) or
    # rejects; negative coordinates reject defensively.
    touch_px = 0
    for ty in range(192):
        for tx in range(256):
            touch_px += 1
            got = gl_mark_of_touch(tx, ty)
            want = gl_mark_of_cell(tx // GL_MAP_CELL_PX,
                                   ty // GL_MAP_CELL_PX)
            if got != want:
                failures += 1
                print(f'FAIL touch alias: ({tx},{ty}): {got} != {want}')
    for tx, ty in ((-1, 100), (100, -1), (-8, -8)):
        if gl_mark_of_touch(tx, ty)[0] != 0:
            failures += 1
            print(f'FAIL touch negative: ({tx},{ty}) accepted')
    # 15d. the map geometry mirrors main.c's render VERBATIM: spot
    # checks of the forward map (arena corners + center land inside
    # the plot, clamped), and gl_gloam_out's full truth table over
    # every reachable (wave_total, spawned) pair.
    if (gl_map_col(GL_ARENA_X_MIN) != GL_MAP_COL0
            or gl_map_col(GL_ARENA_X_MAX) != GL_MAP_COL0 + GL_MAP_COLS - 1
            or gl_map_row(GL_ARENA_Y_MIN) != GL_MAP_ROW0
            or gl_map_row(GL_ARENA_Y_MAX) != GL_MAP_ROW0 + GL_MAP_ROWS - 1):
        failures += 1
        print('FAIL map corners: arena extremes do not land on the plot '
              'edges')
    out_cases = 0
    for total in range(GL_ZOMBIE_CAP + 1):
        for spawned in range(GL_ZOMBIE_CAP + 8):
            out_cases += 1
            got = gl_gloam_out(total, spawned)
            if got != gl_gloam_out(total, spawned):
                failures += 1
                print(f'FAIL gloam-out determinism: ({total},{spawned})')
            if got != max(total - spawned, 0):
                failures += 1
                print(f'FAIL gloam-out: ({total},{spawned}) -> {got}')

    # 16. best-night rematch (slice 11).
    # 16a. the offer gate: a rematch is available IFF a record exists —
    # exactly the "no empty boasts" rule the title/card BEST lines use.
    rematch_cases = 0
    for best in list(range(30)) + [0xFFFFFFFE, 0xFFFFFFFF]:
        rematch_cases += 1
        got = gl_rematch_available(best)
        if got != gl_rematch_available(best):
            failures += 1
            print(f'FAIL rematch determinism: best {best}')
        if got != (1 if best > 0 else 0):
            failures += 1
            print(f'FAIL rematch gate: best {best} -> {got}')
    # 16b. seed choice truth table: the RECORDED seed iff rematch AND a
    # record exists; the frame-counter latch otherwise (a rematch call
    # without a record falls back to the latch — defense in depth over
    # the main.c verb gate). Extremes included: seed words are opaque
    # u32s, never arithmetic.
    seed_cases = 0
    for rematch in (0, 1):
        for best in (0, 1, 13, 0xFFFFFFFF):
            for best_seed in (0, 118, 0xDEADBEEF, 0xFFFFFFFF):
                for latched in (1, 118, 428, 0xFFFFFFFF):
                    seed_cases += 1
                    got = gl_run_seed(rematch, best, best_seed, latched)
                    want = (best_seed if rematch and best > 0
                            else latched)
                    if got != gl_run_seed(rematch, best, best_seed,
                                          latched):
                        failures += 1
                        print(f'FAIL run-seed determinism: '
                              f'({rematch},{best},{best_seed},{latched})')
                    if got != want:
                        failures += 1
                        print(f'FAIL run-seed: ({rematch},{best},'
                              f'{best_seed},{latched}) -> {got}')
    # 16c. the replay contract: a rematch run's ENTIRE spawn schedule is
    # the record run's, spawn for spawn — because gl_run_seed returns
    # the recorded seed verbatim and the schedule is pure f(seed, night,
    # index). Checked explicitly over sample records so the contract
    # survives any future seed-derivation cleverness.
    replay_checks = 0
    for best_seed in (0, 118, 348, 0xDEADBEEF):
        seed = gl_run_seed(1, 2, best_seed, 999)
        for night in (1, 2, 3, 13):
            for index in range(gl_wave_count(night)):
                replay_checks += 1
                if (gl_spawn_of_night(seed, night, index)
                        != gl_spawn_of_night(best_seed, night, index)):
                    failures += 1
                    print(f'FAIL rematch replay: seed {best_seed} '
                          f'night {night} index {index} drifted')

    if failures:
        print(f'check-gloam: {failures} failure(s)')
        return 1

    print(f'check-gloam OK: {spawns} spawns pure/on-fence/safe-radius '
          '(incl. every scheduled wave index to the night-13 cap), '
          f'{chases} idle-player chases converge monotonically '
          f'(worst contact frame {worst}), player + 24-Shambler crowd + '
          'barricades contained over 20000 adversarial move+shove+build '
          'frames, wave schedule ramps 1..24 and plateaus with in-window '
          f'ordered spawn frames (nights 1..64), {shoves} shove cases '
          f'deterministic/never-closer/contained ({exact_pushes} wall-free '
          f'cases pushed exactly +{GL_SHOVE_PUSH}), {block_cases} barricade '
          f'block cases deterministic/enter-only/never-pinning '
          f'({blocked_enters} blocked), player trajectory bit-identical '
          f'with barricades up (no-seal), {pressure_runs} full-cap '
          'walled-in runs all breached to contact (worst frame '
          f'{worst_contact} vs bound {bound}), plank grant + cache grab '
          f'deterministic/monotone/capped, {caches} cache positions '
          f'pure/interior/off-fence, {routes} greedy interlude routes '
          f'all fit the dawn light (worst {worst_route} vs '
          f'{GL_SCAVENGE_FRAMES} frames) and the loot out-earns the '
          f'skip grant, light radius pure/monotone/bounded and full at '
          f'healthy oil, {press_cases} dark-press cases truth-table-exact '
          f'({pressed} pressed, zero at healthy oil), step decomposition '
          f'exact, {pressed_chases} guttering-light pressed chases '
          f'converge monotonically and never slower than lit (worst '
          f'contact frame {worst_pressed}), {flasks} flask positions '
          f'pure/interior/off-fence, burn floors at 0, flask top-up '
          f'capped at {GL_OIL_MAX}, {full_routes} greedy full-pickup '
          f'routes fit the dawn light (worst {worst_full}), one '
          'interlude of flasks out-earns one night of burn, '
          f'{tier_cases} ambience-tier cases truth-table-exact (always '
          'NIGHT at healthy oil, always DAY in daylight), drone rows '
          'climb/legal, all 8 cue rows PSG-legal/bounded with the '
          'id order = the documented priority ranking, '
          f'{save_cases} save-record roundtrips byte-deterministic '
          f'(golden bytes pinned, one-page layout), {rejects} bad-blob '
          'decodes ALL reject to the fresh table (blank chips, every '
          'single-byte corruption, wrong-magic + future-version each '
          f'with a valid checksum), {improve_cases} record-update '
          f'cases strictly-better-only, {mark_cells} chalk-mark plot '
          'cells place strictly-interior with EXACT cell round-trips '
          f'({off_cells} off-plot cells all reject), {touch_px} touch '
          'pixels alias the cell placement exactly (negatives reject), '
          f'map corners land on the plot edges, {out_cases} '
          'gloam-out cases match max(total - spawned, 0), '
          f'{rematch_cases} rematch-gate cases record-iff-available, '
          f'{seed_cases} run-seed cases truth-table-exact (recorded '
          f'seed iff rematch and a record), and {replay_checks} '
          'rematch spawn checks replay the record run spawn for spawn')
    return 0


if __name__ == '__main__':
    sys.exit(main())

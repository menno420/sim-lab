#!/usr/bin/env python3
"""VERDICT 086 runner — the write-contract rate-tier degeneracy (idea-engine P073).

Hermetic: reads ONLY the fixtures.json beside this file. Zero repo/network
reads at verdict time (the mineverse/superbot grounding pins were re-verified
firsthand BEFORE the fixture was written; see fixtures._grounding).

Model: slotted time (slot delta s), arrivals per slot unbounded, admitted =
the schedule itself when it satisfies the limiter. Disciplines: SLIDING /
FIXED-ALIGNED / FIXED-ADVERSARIAL / BUCKET (cap B, refill B/w per second at
slot boundaries after the slot, capped, start full). N_disc(L) = adversary's
maximum admits in any L-second span.

Arms:
  A — seedless closed forms (exact ints/Fractions): N_slide = B*ceil(L/w),
      N_fixed_adv = B*(ceil((L-delta)/w)+1), N_fixed_aligned = B*L/w (w|L),
      N_bucket = B + floor((L/delta - 1)*(B/w)*delta); dead-tier checks,
      redundancy law, separating triple. DECISION-bearing.
  B — INDEPENDENTLY WRITTEN twin: greedy schedule construction with
      feasibility witness + matching combinatorial upper bound, explicit
      alignment enumeration, exhaustive small-world searches, its own
      two-bucket min-level trace, its own separating-schedule search.
      Must equal every Arm-A number exactly; powers the second evaluator.
  R — seeded Poisson click streams through a VERBATIM re-implementation of
      the shim's _consume_budget (deque + eviction + Retry-After), plus the
      deterministic obedient Retry-After client. REPORTING-ONLY (no
      statistical gate; draw-count sentinels + per-trace theorem check).

Gates F1-F6 per the P073 registration; decision order REJECT -> INVALID ->
APPROVE -> NULL (REJECT evaluated FIRST) via twin independently-written
evaluators. Disclosed Arm-R reporting-landing mismatches raise first-class
anomalies (fixture convention C3), never silent gates.
"""

import json
import math
import random
import sys
from collections import deque
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent

assert sys.version_info[:2] == (3, 11), (
    "CPython 3.11 pinned (fixtures cpython_pin); got %s" % (sys.version_info[:2],)
)

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- plumbing
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []
ANOMALIES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
    return bool(cond)


def anomaly(text):
    ANOMALIES.append("A%d: %s" % (len(ANOMALIES) + 1, text))


def fr(a, b=1):
    return Fraction(a) / Fraction(b)


def fstr(x):
    x = Fraction(x)
    return "%d/%d" % (x.numerator, x.denominator) if x.denominator != 1 else str(x.numerator)


def ceil_fr(x):
    x = Fraction(x)
    return -((-x.numerator) // x.denominator)


def floor_fr(x):
    x = Fraction(x)
    return x.numerator // x.denominator


# seed constructor registry (C7)
SEED_REGISTRY = []


class CountingRandom(random.Random):
    def __init__(self, seed):
        SEED_REGISTRY.append(seed)
        super().__init__(seed)
        self.expovariate_draws = 0
        self.shuffle_calls = 0

    def expovariate(self, lambd):
        self.expovariate_draws += 1
        return super().expovariate(lambd)

    def shuffle(self, x):
        self.shuffle_calls += 1
        super().shuffle(x)


# ================================================================ Arm A
# Seedless closed forms, exact integers/Fractions. DECISION-bearing.

def A_n_slide(L, B, w):
    return B * ceil_fr(fr(L) / fr(w))


def A_n_fixed_adv(L, B, w, delta=fr(1)):
    return B * (ceil_fr((fr(L) - fr(delta)) / fr(w)) + 1)


def A_n_fixed_aligned(L, B, w):
    assert fr(L) % fr(w) == 0, "aligned form requires w | L"
    return B * int(fr(L) / fr(w))


def A_n_bucket(L, B, w, delta=fr(1)):
    n_slots = fr(L) / fr(delta)
    assert n_slots.denominator == 1
    r = fr(B, w) * fr(delta)
    return B + floor_fr((n_slots - 1) * r)


def A_n_bucket_closed(L, B, w):
    return B + floor_fr(fr(L) * fr(B) / fr(w))


def A_bucket_pair_min_level(B, w, S, T, horizon_slots):
    """Sustained-bucket minimum level under adversarial burst-admissible
    traffic. Exact invariant: equal refill rates (B/w == S/T) keep
    d = sustained - burst >= S - B (capping only ever grows d at the burst
    cap or holds d >= S - B at the sustained cap), so min = S - B, attained
    the moment the burst bucket is drained. Verified against a greedy
    front-load trace over the horizon."""
    assert fr(B, w) == fr(S, T), "invariant requires equal refill rates"
    assert S >= B
    invariant_min = S - B
    # greedy front-load trace (Arm A's own code; Arm B re-traces independently)
    b, s = fr(B), fr(S)
    seen_min = s
    for _ in range(horizon_slots):
        take = floor_fr(b)
        b -= take
        s -= take
        if s < seen_min:
            seen_min = s
        b = min(fr(B), b + fr(B, w))
        s = min(fr(S), s + fr(S, T))
    return invariant_min, seen_min


# ================================================================ Arm B
# INDEPENDENTLY WRITTEN twin (C2): greedy witnesses + matching upper bounds,
# explicit alignment enumeration, exhaustive small worlds, its own bucket
# trace and separating search. Works in integer slots throughout.

def B_slide_max(L_slots, w_slots, B):
    """Sliding max admits in an L-span: explicit feasible schedule (bursts of
    B every w slots) + partition upper bound. Returns the exact max."""
    sched = [0] * L_slots
    t = 0
    while t < L_slots:
        sched[t] = B
        t += w_slots
    feasible = all(
        sum(sched[i:i + w_slots]) <= B for i in range(L_slots)
    )
    lower = sum(sched)
    blocks = (L_slots + w_slots - 1) // w_slots
    upper = blocks * B
    assert feasible and lower == upper, "sliding witness/bound must meet"
    return lower


def B_fixed_adv_max(L_slots, w_slots, B):
    """Fixed windows, adversarial alignment: enumerate every span offset
    against the grid, count intersected windows, then verify the best count
    with an explicit schedule through a fixed-window counter simulation."""
    best, best_off = -1, 0
    for a in range(w_slots):
        first = a // w_slots
        last = (a + L_slots - 1) // w_slots
        if (last - first + 1) * B > best:
            best = (last - first + 1) * B
            best_off = a
    # witness: B arrivals in one slot of each intersected window's overlap
    a = best_off
    first = a // w_slots
    last = (a + L_slots - 1) // w_slots
    arrivals = {}
    for k in range(first, last + 1):
        slot = max(a, k * w_slots)  # first span slot inside window k
        arrivals[slot] = B
    counts = {}
    admitted = 0
    for slot, n in sorted(arrivals.items()):
        k = slot // w_slots
        assert counts.get(k, 0) + n <= B, "witness must be admissible"
        counts[k] = counts.get(k, 0) + n
        admitted += n
    assert admitted == best, "fixed-adv witness must achieve the bound"
    return best


def B_fixed_aligned_max(L_slots, w_slots, B):
    """Aligned span [0, L) with w | L: each of L/w grid windows carries B."""
    assert L_slots % w_slots == 0
    windows = L_slots // w_slots
    sched = {k * w_slots: B for k in range(windows)}
    counts = {}
    admitted = 0
    for slot, n in sorted(sched.items()):
        k = slot // w_slots
        assert counts.get(k, 0) + n <= B
        counts[k] = counts.get(k, 0) + n
        admitted += n
    return admitted


def B_bucket_max(n_slots, refill_per_slot, cap, refills_inside):
    """Greedy drain of a token bucket (start full, refill after each slot,
    capped) + token-conservation upper bound. refills_inside = number of
    refill boundaries inside the span (n_slots - 1 half-open; n_slots for
    the closed-interval exhibit)."""
    level = fr(cap)
    total = 0
    refills_done = 0
    for i in range(n_slots):
        take = floor_fr(level)
        total += take
        level -= take
        if refills_done < refills_inside:
            level = min(fr(cap), level + fr(refill_per_slot))
            refills_done += 1
    upper = cap + floor_fr(fr(refill_per_slot) * refills_inside)
    assert total == upper, "bucket greedy must meet the conservation bound"
    return total


def B_bucket_span_max(L_slots, w_slots, B, delta=fr(1)):
    """Half-open span: n_slots slots, n_slots - 1 refills inside."""
    r = fr(B, w_slots)  # per-slot refill = (B/w_seconds)*delta = B/w_slots
    return B_bucket_max(L_slots, r, B, L_slots - 1)


def B_bucket_span_max_closed(L_slots, w_slots, B):
    """Closed-interval exhibit: the final boundary refill (and instant) counts."""
    r = fr(B, w_slots)
    return B_bucket_max(L_slots + 1, r, B, L_slots)


def B_exhaustive_slide_max(L_slots, w_slots, B):
    """Exhaustive search over all (B+1)^L per-slot schedules under the
    sliding constraint (every w-slot window sum <= B)."""
    best = 0
    for sched in product(range(B + 1), repeat=L_slots):
        ok = True
        for i in range(L_slots - w_slots + 1):
            if sum(sched[i:i + w_slots]) > B:
                ok = False
                break
        if ok:
            total = sum(sched)
            if total > best:
                best = total
    return best


def B_two_bucket_trace(B, w, S, T, horizon_slots):
    """Independent greedy front-load two-bucket trace: adversary drains the
    burst bucket every slot; the sustained bucket is the observer. Returns
    (min sustained level seen, any sustained rejection)."""
    burst = fr(B)
    sust = fr(S)
    min_sust = sust
    sust_rejected = False
    for _ in range(horizon_slots):
        send = floor_fr(burst)  # max the burst bucket admits this slot
        if send > sust:
            sust_rejected = True  # would need more tokens than sustained has
            send = floor_fr(sust)
        burst -= send
        sust -= send
        if sust < min_sust:
            min_sust = sust
        burst = min(fr(B), burst + fr(B, w))
        sust = min(fr(S), sust + fr(S, T))
    return min_sust, sust_rejected


def B_two_bucket_exhaustive_min(bcap, scap, refill, slots):
    """Exhaustive scaled world: every burst-admissible integer schedule,
    tracking the sustained minimum; confirms greedy front-load minimizes."""
    best_min = fr(scap)
    for sched in product(range(bcap + 1), repeat=slots):
        b, s = fr(bcap), fr(scap)
        ok = True
        lo = s
        for send in sched:
            if send > b:
                ok = False
                break
            b -= send
            s -= send
            if s < lo:
                lo = s
            b = min(fr(bcap), b + fr(refill))
            s = min(fr(scap), s + fr(refill))
        if ok and lo < best_min:
            best_min = lo
    return best_min


def B_separating_search_committed(S):
    """Own separating-schedule reasoning at the committed pair: the sliding
    max over any 60 s span is B_slide_max(60,10,10); a separating schedule
    exists iff that max exceeds S."""
    return B_slide_max(60, 10, 10) > S


def B_s50_witness():
    """The committed S = 50 witness: six 10-bursts at t = 0,10,...,50.
    Verify burst-sliding feasibility with Arm B's own checker and count."""
    sched = [0] * 60
    for t in range(0, 60, 10):
        sched[t] = 10
    feasible = all(sum(sched[i:i + 10]) <= 10 for i in range(60))
    return feasible, sum(sched)


def B_aligned_61_probe():
    """Two-tier aligned-fixed limiter fed 61 requests in an aligned minute:
    the 61st must be rejected by the BURST tier first; the sustained counter
    never exceeds 60 and never rejects."""
    requests = []
    for win in range(6):
        for _ in range(10):
            requests.append(win * 10)
    requests.append(0)  # the 61st, in window 0
    requests.sort()
    burst_counts = {}
    sust_count = 0
    max_sust = 0
    rejects = []
    for t in requests:
        k = t // 10
        if burst_counts.get(k, 0) >= 10:
            rejects.append(("burst", t))
            continue
        if sust_count >= 60:
            rejects.append(("sustained", t))
            continue
        burst_counts[k] = burst_counts.get(k, 0) + 1
        sust_count += 1
        max_sust = max(max_sust, sust_count)
    return max_sust, rejects


# ================================================================ Arm R
# Verbatim re-implementation of the shim's _consume_budget core
# (tests/shim/shim_bot.py:340-366 @ b9ade33): deque, eviction
# `now - times[0] >= window`, reject at len >= max, Retry-After
# = max(1, ceil(times[0] + window - now)). REPORTING-ONLY.

class ShimLimiter:
    def __init__(self, max_requests, window):
        self.max_requests = max_requests
        self.window = window
        self.times = deque()

    def request(self, now):
        times = self.times
        while times and now - times[0] >= self.window:
            times.popleft()
        if len(times) >= self.max_requests:
            return False, max(1, math.ceil(times[0] + self.window - now))
        times.append(now)
        return True, None


def R_poisson_trace(seed, n_events, rate):
    rng = CountingRandom(seed)
    lim = ShimLimiter(10, 10.0)
    t = 0.0
    admitted_times = []
    rejected = 0
    for _ in range(n_events):
        t += rng.expovariate(rate)
        ok, _ra = lim.request(t)
        if ok:
            admitted_times.append(t)
        else:
            rejected += 1
    # worst trailing 60 s admitted-window: admits in (t_i - 60, t_i]
    worst = 0
    j = 0
    for i, ti in enumerate(admitted_times):
        while admitted_times[j] <= ti - 60.0:
            j += 1
        worst = max(worst, i - j + 1)
    return {
        "seed": seed,
        "events": n_events,
        "draws": rng.expovariate_draws,
        "admitted": len(admitted_times),
        "rejected": rejected,
        "horizon_s": round(t, 3),
        "worst_trailing_60s_window": worst,
    }, rng


def R_obedient_client(horizon_s):
    """Deterministic (no RNG): send immediately; on 429 wait exactly the
    Retry-After header. C10: the 3600/3600 s anchor is an F3 gate."""
    lim = ShimLimiter(10, 10.0)
    t = 0.0
    admits = 0
    while t < horizon_s:
        ok, ra = lim.request(t)
        if ok:
            admits += 1
        else:
            t += ra
    return admits


# ================================================================ run
def main():
    cc = FIX["committed_constants"]
    B, w, S, T = cc["B"], cc["w_seconds"], cc["S"], cc["T_seconds"]
    band = fr("21/20")

    # ---------------------------------------------------------- F1 identities
    check("F1 equal-average identity B*T == 600", B * T == 600)
    check("F1 equal-average identity S*w == 600", S * w == 600)
    check("F1 B*T == S*w", B * T == S * w)
    check("F1 fixture identity value", cc["identity_BT_eq_Sw"] == B * T)
    # partition bound, numeric leg: every exhaustive small-world max respects
    # B*ceil(L/w) (checked below in F5); symbolic leg: the closed form IS the
    # partition count, asserted structurally here on the committed cell.
    check("F1 partition bound at committed cell",
          A_n_slide(60, B, w) == B * ceil_fr(fr(60, w)))
    # Retry-After formula reproduced verbatim: known-value probes
    lim = ShimLimiter(10, 10.0)
    for i in range(10):
        ok, _ = lim.request(0.0)
        check("F1 retry-after probe admit %d" % i, ok)
    ok, ra = lim.request(3.2)
    check("F1 retry-after probe reject", not ok)
    check("F1 retry-after value ceil(0+10-3.2) == 7", ra == 7)
    ok, ra = lim.request(9.999)
    check("F1 retry-after floor-at-1", (not ok) and ra == 1)

    # ---------------------------------------------------------- Arm A census
    armA = {
        "N_slide_60": A_n_slide(60, B, w),
        "N_fixed_adv_60": A_n_fixed_adv(60, B, w),
        "N_fixed_aligned_60": A_n_fixed_aligned(60, B, w),
        "N_bucket_60": A_n_bucket(60, B, w),
        "N_bucket_60_closed": A_n_bucket_closed(60, B, w),
        "N_fixed_adv_2": A_n_fixed_adv(2, B, w),
        "N_slide_2": A_n_slide(2, B, w),
        "w7_cell": A_n_slide(60, 10, 7),
    }
    inv_min, greedy_min = A_bucket_pair_min_level(B, w, S, T, 600)
    armA["bucket_pair_min_level"] = inv_min
    check("A bucket invariant == greedy trace over 600 s", inv_min == greedy_min)

    # ---------------------------------------------------------- Arm B census
    armB = {
        "N_slide_60": B_slide_max(60, 10, B),
        "N_fixed_adv_60": B_fixed_adv_max(60, 10, B),
        "N_fixed_aligned_60": B_fixed_aligned_max(60, 10, B),
        "N_bucket_60": B_bucket_span_max(60, 10, B),
        "N_bucket_60_closed": B_bucket_span_max_closed(60, 10, B),
        "N_fixed_adv_2": B_fixed_adv_max(2, 10, B),
        "N_slide_2": B_slide_max(2, 10, B),
        "w7_cell": B_slide_max(60, 7, 10),
    }
    b_min, b_sust_rejected = B_two_bucket_trace(B, w, S, T, 600)
    armB["bucket_pair_min_level"] = b_min
    check("B two-bucket trace: sustained never rejects", not b_sust_rejected)

    for key in sorted(armA):
        check("F6 twin exact: %s (A %s == B %s)" % (key, armA[key], armB[key]),
              armA[key] == armB[key])

    # ---------------------------------------------------------- F3 anchors
    F3 = FIX["census_anchors_F3"]
    check("F3 N_slide(60) == 60", armA["N_slide_60"] == F3["N_slide_60"] == 60)
    check("F3 N_fixed_adv(60) == 70", armA["N_fixed_adv_60"] == F3["N_fixed_adv_60"] == 70)
    check("F3 N_fixed_aligned(60) == 60",
          armA["N_fixed_aligned_60"] == F3["N_fixed_aligned_60"] == 60)
    check("F3 N_bucket(60) == 69", armA["N_bucket_60"] == F3["N_bucket_60"] == 69)
    check("F3 N_bucket closed-interval exhibit == 70",
          armA["N_bucket_60_closed"] == F3["N_bucket_60_closed_interval"] == 70)
    check("F3 N_fixed_adv(2) == 20", armA["N_fixed_adv_2"] == F3["N_fixed_adv_2"] == 20)
    check("F3 N_slide(2) == 10", armA["N_slide_2"] == F3["N_slide_2"] == 10)
    check("F3 w=7 cell == 90", armA["w7_cell"] == F3["w7_cell"] == 90)
    check("F3 bucket-pair min level == 50 over 600 s",
          armA["bucket_pair_min_level"] == F3["bucket_pair_min_level"] == 50)
    excess_fixed = fr(armA["N_fixed_adv_60"], S)
    excess_bucket = fr(armA["N_bucket_60"], S)
    check("F3 excess fixed == 7/6", excess_fixed == fr("7/6"))
    check("F3 excess bucket == 23/20", excess_bucket == fr("23/20"))
    margin_fixed = excess_fixed / band
    margin_bucket = excess_bucket / band
    check("F3 margin fixed == 10/9", margin_fixed == fr("10/9"))
    check("F3 margin bucket == 23/21", margin_bucket == fr("23/21"))

    # ---------------------------------------------------------- T1 dead tier
    check("T1 uniform sliding contact: N_slide(60) == S (margin 0, registered)",
          armA["N_slide_60"] == S)
    check("T1 uniform aligned-fixed contact: max aligned minute == S",
          armA["N_fixed_aligned_60"] == S)
    max_sust, rejects = B_aligned_61_probe()
    check("T1 61-probe: sustained counter caps at 60", max_sust == 60)
    check("T1 61-probe: the 61st is rejected by BURST first",
          len(rejects) == 1 and rejects[0][0] == "burst")
    check("T1 bucket dead margin: min level 50 >= 1",
          armA["bucket_pair_min_level"] >= 1)
    no_separating_committed = not B_separating_search_committed(S)
    check("T1 no separating schedule at committed pair under sliding",
          no_separating_committed)

    # ---------------------------------------------------------- T2 fork
    check("T2 fixed >= 21/20 band", excess_fixed >= band)
    check("T2 bucket >= 21/20 band (half-open)", excess_bucket >= band)
    check("T2 bucket >= 21/20 band (closed-interval)",
          fr(armA["N_bucket_60_closed"], S) >= band)
    check("T2 straddle N_fixed_adv(2) == 2B exactly",
          armA["N_fixed_adv_2"] == 2 * B)
    check("T2 sliding straddle stays 10", armA["N_slide_2"] == B)

    # ---------------------------------------------------------- T3 lattice
    lat = FIX["theorems"]["T3_lattice"]
    lhs = B * ceil_fr(fr(T, w))
    check("T3 committed lattice equality B*ceil(T/w) == S (60 == 60)",
          lhs == S == lat["committed_equality"][0])
    s50_feasible, s50_admits = B_s50_witness()
    check("T3 S=50 witness feasible under burst-sliding", s50_feasible)
    check("T3 S=50 witness admits == 60 > 50",
          s50_admits == lat["S50_witness"]["admits"] and s50_admits > 50)
    check("T3 separating schedule EXISTS at S=50", B_separating_search_committed(50))
    check("T3 w=7 world: 90 > 60",
          armA["w7_cell"] == lat["w7_world"]["value"] and armA["w7_cell"] > S)
    check("T3 S=70 world: fixed contact 70 == 70 (registered margin-0)",
          armA["N_fixed_adv_60"] == 70 == lat["S70_world_fixed_contact"][0])

    # redundancy law over the full grid + discipline ordering (F2/F5)
    grid_rows = {}
    for (gB, gw) in [tuple(x) for x in FIX["grids"]["Bw"]]:
        a_s = A_n_slide(60, gB, gw)
        row = {
            "N_slide_60": a_s,
            "N_fixed_adv_60": A_n_fixed_adv(60, gB, gw),
            "N_bucket_60": A_n_bucket(60, gB, gw),
            "redundant_at_S": {},
        }
        check("F2 grid twin slide (%d,%d)" % (gB, gw),
              a_s == B_slide_max(60, gw, gB))
        check("F2 grid twin fixed_adv (%d,%d)" % (gB, gw),
              row["N_fixed_adv_60"] == B_fixed_adv_max(60, gw, gB))
        check("F2 grid twin bucket (%d,%d)" % (gB, gw),
              row["N_bucket_60"] == B_bucket_span_max(60, gw, gB))
        for gS in FIX["grids"]["S"]:
            law = gB * ceil_fr(fr(60, gw)) <= gS
            scan = a_s <= gS  # redundant iff sliding max cannot exceed S
            check("T3 redundancy law == scan at (%d,%d,S=%d)" % (gB, gw, gS),
                  law == scan)
            row["redundant_at_S"][str(gS)] = law
        for L in FIX["grids"]["L"]:
            ns = A_n_slide(L, gB, gw)
            nb = A_n_bucket(L, gB, gw)
            nf = A_n_fixed_adv(L, gB, gw)
            check("F5 ordering slide<=bucket<=fixed_adv at (%d,%d,L=%d)" % (gB, gw, L),
                  ns <= nb <= nf)
        grid_rows["%d,%d" % (gB, gw)] = row
    check("F3 grid row (20,10) == 120/140/138",
          [grid_rows["20,10"]["N_slide_60"], grid_rows["20,10"]["N_fixed_adv_60"],
           grid_rows["20,10"]["N_bucket_60"]] == F3["grid_row_20_10_at_L60"])
    check("F3 grid row (5,10) == 30/35/34",
          [grid_rows["5,10"]["N_slide_60"], grid_rows["5,10"]["N_fixed_adv_60"],
           grid_rows["5,10"]["N_bucket_60"]] == F3["grid_row_5_10_at_L60"])
    check("F3 grid row (20,10): every S live",
          not any(grid_rows["20,10"]["redundant_at_S"].values()))
    check("F3 grid row (5,10): every S dead",
          all(grid_rows["5,10"]["redundant_at_S"].values()))

    # ---------------------------------------------------------- F4 pencil world
    hw = FIX["hand_world_F4"]
    p_slide_A = A_n_slide(hw["L"], hw["B"], hw["w"])
    p_fixed_A = A_n_fixed_adv(hw["L"], hw["B"], hw["w"])
    p_bucket_A = A_n_bucket(hw["L"], hw["B"], hw["w"])
    check("F4 pencil sliding == 4 (closed form)", p_slide_A == hw["sliding"])
    check("F4 pencil fixed-adversarial == 6", p_fixed_A == hw["fixed_adversarial"])
    check("F4 pencil bucket == 5", p_bucket_A == hw["bucket"])
    p_slide_ex = B_exhaustive_slide_max(hw["L"], hw["w"], hw["B"])
    check("F4 pencil exhaustive 3^4 sliding == 4", p_slide_ex == hw["sliding"])
    check("F4 pencil twin fixed-adv", B_fixed_adv_max(hw["L"], hw["w"], hw["B"]) == 6)
    check("F4 pencil twin bucket", B_bucket_span_max(hw["L"], hw["w"], hw["B"]) == 5)

    # ---------------------------------------------------------- F5 controls
    triple = {}
    for ds in FIX["model"]["delta_grid"]:
        d = fr(ds)
        slots_per_s = int(fr(1) / d)
        a_triple = (
            A_n_slide(60, B, w),
            A_n_fixed_adv(60, B, w, d),
            A_n_bucket(60, B, w, d),
        )
        b_triple = (
            B_slide_max(60 * slots_per_s, 10 * slots_per_s, B),
            B_fixed_adv_max(60 * slots_per_s, 10 * slots_per_s, B),
            B_bucket_span_max(60 * slots_per_s, 10 * slots_per_s, B),
        )
        check("F5 granularity triple at delta=%s (A)" % ds,
              list(a_triple) == FIX["controls_F5"]["granularity_triple"])
        check("F5 granularity triple at delta=%s (B twin)" % ds,
              a_triple == b_triple)
        triple[ds] = list(a_triple)
    check("F5 bucket endpoint pair {69, 70} both >= 21/20*S",
          sorted([armA["N_bucket_60"], armA["N_bucket_60_closed"]]) ==
          FIX["controls_F5"]["bucket_endpoint_pair"] and
          all(fr(v, S) >= band for v in FIX["controls_F5"]["bucket_endpoint_pair"]))
    small_worlds = {}
    for (L_, w_, B_) in [tuple(x) for x in FIX["controls_F5"]["small_worlds_LwB"]]:
        ex = B_exhaustive_slide_max(L_, w_, B_)
        cf = A_n_slide(L_, B_, w_)
        check("F5 small world (%d,%d,%d): exhaustive %d == closed form %d"
              % (L_, w_, B_, ex, cf), ex == cf)
        small_worlds["%d,%d,%d" % (L_, w_, B_)] = ex
    # C12 battery: greedy front-load is the minimizer on the scaled world
    scaled_greedy, _ = B_two_bucket_trace(2, 2, 6, 6, 6)
    scaled_exhaustive = B_two_bucket_exhaustive_min(2, 6, 1, 6)
    check("C12 scaled two-bucket world: greedy min == exhaustive min == 4",
          scaled_greedy == scaled_exhaustive == 4)

    # ---------------------------------------------------------- Arm R
    ar = FIX["arm_R"]
    trace_main, rng_main = R_poisson_trace(ar["main"]["seed"], ar["main"]["events"], 2.0)
    trace_stab, rng_stab = R_poisson_trace(ar["stability"]["seed"],
                                           ar["stability"]["events"], 2.0)
    check("F6 Arm R draw sentinel (main): %d draws" % trace_main["draws"],
          trace_main["draws"] == ar["main"]["events"])
    check("F6 Arm R draw sentinel (stability): %d draws" % trace_stab["draws"],
          trace_stab["draws"] == ar["stability"]["events"])
    check("F6 per-trace theorem (main): worst 60 s window <= 60",
          trace_main["worst_trailing_60s_window"] <= 60)
    check("F6 per-trace theorem (stability): worst 60 s window <= 60",
          trace_stab["worst_trailing_60s_window"] <= 60)
    # disclosed reporting landing (C3: mismatch -> first-class anomaly)
    disc = ar["disclosed_reporting_landing"]
    for label, got, want in (
        ("main admitted", trace_main["admitted"], disc["main_admitted"]),
        ("main rejected", trace_main["rejected"], disc["main_rejected"]),
        ("stability admitted", trace_stab["admitted"], disc["stability_admitted"]),
        ("stability rejected", trace_stab["rejected"], disc["stability_rejected"]),
        ("main worst-window contact", trace_main["worst_trailing_60s_window"],
         disc["worst_window_contact"]),
        ("stability worst-window contact", trace_stab["worst_trailing_60s_window"],
         disc["worst_window_contact"]),
    ):
        if got != want:
            anomaly("disclosed Arm-R reporting value '%s': drafter disclosed %s, "
                    "this run measured %s (reporting-only, no decision clause "
                    "reads it; C3 first-class anomaly)" % (label, want, got))
    obedient = R_obedient_client(ar["obedient_client"]["horizon_s"])
    check("F3/C10 obedient Retry-After client: exactly 3600 admits in 3600 s",
          obedient == F3["obedient_client"]["admits"])
    check("F3 obedient long-run rate == 1/s",
          fr(obedient, ar["obedient_client"]["horizon_s"]) == fr(F3["obedient_client"]["long_run_rate"]))
    # presentation leg: shuffle the printed grid-row order (presentation only)
    rng_pres = CountingRandom(ar["presentation_shuffle_seed"])
    pres_rows = sorted(grid_rows)
    rng_pres.shuffle(pres_rows)
    check("F6 presentation seed read by presentation legs only",
          rng_pres.shuffle_calls == 1 and rng_pres.expovariate_draws == 0)
    check("F6 seed constructor registry == [20261650, 20261651, 20261652]",
          SEED_REGISTRY == [ar["main"]["seed"], ar["stability"]["seed"],
                            ar["presentation_shuffle_seed"]])
    check("F6 aux seed 20261653 never read",
          ar["aux_seed_never_read"] not in SEED_REGISTRY)

    # ---------------------------------------------------------- margin ledger
    ledger = {
        "R2_fixed_margin": fstr(margin_fixed),
        "R2_bucket_margin": fstr(margin_bucket),
        "straddle": "exact equality by law (20 == 2B) — no margin concept",
        "registered_margin0_contacts": [
            "sliding N(60) == S (60 == 60)",
            "aligned-fixed max aligned minute == S (60 == 60)",
            "S=70 falsifiability world: fixed 70 == 70",
            "R3 lattice equality B*ceil(T/w) == S (60 == 60)",
        ],
        "fat_margin": "bucket dead check: min level 50 vs 1-token threshold (49 tokens)",
    }
    # C5 gate: no UNregistered decision comparison sits at margin 0.
    # The unregistered strict/inequality comparisons and their margins:
    check("C5 R2 fixed clears the band strictly (margin 10/9 > 1)", margin_fixed > 1)
    check("C5 R2 bucket clears the band strictly (margin 23/21 > 1)", margin_bucket > 1)
    check("C5 bucket dead margin fat (50 >= 1 by 49)", armA["bucket_pair_min_level"] - 1 == 49)
    check("C5 w=7 clause margin (90 - 60 = 30 > 0)", armA["w7_cell"] - S == 30)
    check("C5 S=50 witness margin (60 - 50 = 10 > 0)", s50_admits - 50 == 10)

    # ---------------------------------------------------------- evaluators
    gates_green = CHECKS["failed"] == 0

    def evaluator_one(a):
        """Reads Arm A numbers. Registered order REJECT -> INVALID -> APPROVE -> NULL."""
        r1 = (a["N_slide_60"] <= S and a["N_slide_60"] == S
              and a["N_fixed_aligned_60"] == S
              and a["bucket_pair_min_level"] == 50 and a["bucket_pair_min_level"] >= 1)
        r2 = (fr(a["N_fixed_adv_60"], S) >= band
              and fr(a["N_bucket_60"], S) >= band
              and fr(a["N_bucket_60_closed"], S) >= band
              and a["N_fixed_adv_2"] == 2 * B)
        r3 = (B * T == S * w and B_slide_max(60, 10, 10) > 50
              and a["w7_cell"] > S)
        if r1 and r2 and r3:
            return "REJECT", {"R1": r1, "R2": r2, "R3": r3}
        if not gates_green:
            return "INVALID", {"R1": r1, "R2": r2, "R3": r3}
        approve = (a["N_slide_60"] > S) or (a["N_fixed_adv_60"] <= S
                                            and a["N_bucket_60"] <= S)
        if approve:
            return "APPROVE", {"R1": r1, "R2": r2, "R3": r3}
        return "NULL", {"R1": r1, "R2": r2, "R3": r3}

    def evaluator_two(b):
        """INDEPENDENTLY WRITTEN second evaluator: reads Arm B numbers only,
        different clause construction (list-of-predicates form)."""
        dead_checks = [
            b["N_slide_60"] - S == 0,
            b["N_fixed_aligned_60"] - S == 0,
            b["bucket_pair_min_level"] - 50 == 0,
            b["bucket_pair_min_level"] >= 1,
            not (b["N_slide_60"] > S),  # no separating schedule
        ]
        fork_checks = [
            20 * b["N_fixed_adv_60"] >= 21 * S,
            20 * b["N_bucket_60"] >= 21 * S,
            20 * b["N_bucket_60_closed"] >= 21 * S,
            b["N_fixed_adv_2"] - 2 * B == 0,
        ]
        lattice_checks = [
            B * T - S * w == 0,
            b["N_slide_60"] > 50,  # separating schedule exists at S = 50
            b["w7_cell"] > S,
        ]
        reject = all(dead_checks) and all(fork_checks) and all(lattice_checks)
        if reject:
            return "REJECT"
        if not gates_green:
            return "INVALID"
        if (b["N_slide_60"] > S) or (b["N_fixed_adv_60"] <= S
                                     and b["N_bucket_60"] <= S):
            return "APPROVE"
        return "NULL"

    ruling_one, clauses = evaluator_one(armA)
    ruling_two = evaluator_two(armB)
    check("F6 twin evaluators agree (%s == %s)" % (ruling_one, ruling_two),
          ruling_one == ruling_two)
    ruling = ruling_one if ruling_one == ruling_two else "INVALID"
    if CHECKS["failed"] > 0 and ruling == "REJECT":
        # registered order: REJECT is evaluated first and stands; gate health
        # is reported alongside (a failed gate with REJECT clauses all firing
        # would still have surfaced above as failed self-checks -> exit 1).
        pass

    # ---------------------------------------------------------- results
    results = {
        "verdict": ruling,
        "clauses": {k: bool(v) for k, v in clauses.items()},
        "committed_constants": {"B": B, "w_s": w, "S": S, "T_s": T,
                                "identity": B * T},
        "census": {k: int(v) for k, v in armA.items()},
        "excesses": {"fixed": fstr(excess_fixed), "bucket": fstr(excess_bucket)},
        "margin_ledger": ledger,
        "grid_rows_at_L60": {
            k: {kk: (vv if not isinstance(vv, dict) else vv)
                for kk, vv in v.items()} for k, v in grid_rows.items()},
        "granularity_triple": triple,
        "small_worlds_exhaustive": small_worlds,
        "pencil_world": {"sliding": p_slide_A, "fixed_adversarial": p_fixed_A,
                         "bucket": p_bucket_A, "exhaustive_sliding": p_slide_ex},
        "separating_triple": {
            "committed_S60": "none (N_slide(60) = 60 <= 60)",
            "S50": "exists (six 10-bursts, 60 admits > 50)",
            "S70": "none, doubly slack, fixed contact 70 == 70",
        },
        "arm_R": {
            "main": trace_main,
            "stability": trace_stab,
            "obedient_client_admits": obedient,
            "presentation_row_order": pres_rows,
            "statistical_gate": "none (reporting-only)",
        },
        "seeds": {"registry": SEED_REGISTRY,
                  "aux_never_read": ar["aux_seed_never_read"]},
        "anomalies": ANOMALIES,
        "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                        "failures": FAILURES},
        "falsifiability": {
            "S50_world": "sustained LIVE under every discipline (witness above)"
                         " — APPROVE's first clause flips one constant-step down",
            "w7_world": "redundancy dies by divisibility alone (90 > 60)",
            "discipline_pin_world": "a one-sentence sliding pin would moot R2's"
                                    " fork; finding degrades to dead-ink only"
                                    " (reporting demonstration, not a code path)",
        },
    }
    out = json.dumps(results, sort_keys=True, indent=1)
    (HERE / "results.json").write_text(out + "\n", encoding="utf-8")

    print("VERDICT 086 — write-contract rate-tier degeneracy (P073)")
    print("ruling: %s (twin evaluators %s / %s)" % (ruling, ruling_one, ruling_two))
    print("committed pair: B=%d per %d s, S=%d per %d s; B*T = S*w = %d"
          % (B, w, S, T, B * T))
    print("census: slide60=%d fixed_adv60=%d aligned60=%d bucket60=%d "
          "bucket60_closed=%d straddle2=%d slide2=%d w7=%d bucket_min=%d"
          % (armA["N_slide_60"], armA["N_fixed_adv_60"],
             armA["N_fixed_aligned_60"], armA["N_bucket_60"],
             armA["N_bucket_60_closed"], armA["N_fixed_adv_2"],
             armA["N_slide_2"], armA["w7_cell"], armA["bucket_pair_min_level"]))
    print("excesses: fixed %s (margin %s), bucket %s (margin %s), straddle 20 = 2B"
          % (fstr(excess_fixed), fstr(margin_fixed),
             fstr(excess_bucket), fstr(margin_bucket)))
    print("granularity triple: %s" % json.dumps(triple, sort_keys=True))
    print("small worlds (exhaustive == closed form): %s"
          % json.dumps(small_worlds, sort_keys=True))
    print("arm R main: admitted=%d rejected=%d worst60=%d draws=%d"
          % (trace_main["admitted"], trace_main["rejected"],
             trace_main["worst_trailing_60s_window"], trace_main["draws"]))
    print("arm R stability: admitted=%d rejected=%d worst60=%d draws=%d"
          % (trace_stab["admitted"], trace_stab["rejected"],
             trace_stab["worst_trailing_60s_window"], trace_stab["draws"]))
    print("obedient client: %d admits in 3600 s (rate exactly 1/s)" % obedient)
    print("presentation row order (seed 20261652): %s" % ",".join(pres_rows))
    print("seed registry: %s (aux %d never read)"
          % (SEED_REGISTRY, ar["aux_seed_never_read"]))
    if ANOMALIES:
        print("anomalies (%d):" % len(ANOMALIES))
        for a_ in ANOMALIES:
            print("  " + a_)
    else:
        print("anomalies: none")
    print("self-checks: %d passed, %d failed"
          % (CHECKS["passed"], CHECKS["failed"]))
    if FAILURES:
        for f in FAILURES:
            print("  FAILED: " + f)
    # C13 exit contract
    sys.exit(0 if not FAILURES and ruling in
             ("REJECT", "APPROVE", "NULL", "INVALID") else 1)


if __name__ == "__main__":
    main()

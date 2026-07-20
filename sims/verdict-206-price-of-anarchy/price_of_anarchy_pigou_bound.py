"""Price of anarchy — selfish two-pool routing costs at most 4/3 of optimal.

Head: route unit demand across two parallel server pools whose per-request
latency is affine in that pool's load. Let each request pick the pool that is
fastest FOR IT (the Wardrop/Nash equilibrium). The equilibrium's average
latency is at most 4/3 of the coordinated (social-optimum) average latency for
EVERY affine-latency instance -- and exactly 4/3 in the tight Pigou instance
(top pool latency = load x, bottom pool a constant 1): selfish routing piles
all demand onto the pool that is never slower and pays average latency 1, while
the optimal split (half-and-half) pays 3/4, so 1 / (3/4) = 4/3. No affine
topology does worse (Roughgarden-Tardos). The bound is regime-specific: make
the constant pool expensive enough (constant >= twice the congestible slope)
and selfish routing is already optimal (price of anarchy = 1).

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical
sha256 (sort_keys=True, separators=(",",":")) over the results dict IS the digest;
the dict carries no self-referential field; pretty dump to stdout; floats rounded
6 dp; Fractions serialized as strings; no on-disk JSON. SEED=20260717; in-process
double-run asserts byte-identical; gates use Z_GATE=3.0.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0

# Pinned worlds (each a two-parallel-pool instance; demand is a unit split, so
# flow on a pool is a Fraction in [0, 1] and average latency == total cost).
# A pool's per-request latency is affine in its own flow: latency = a * flow + b.
#   PIGOU    -- the TIGHT worst case: top = x (a=1, b=0), bottom = 1 (a=0, b=1).
#   INTERIOR -- both pools congestible, a genuine interior equilibrium (G2).
PIGOU = (Fraction(1), Fraction(0), Fraction(0), Fraction(1))          # a_top,b_top,a_bot,b_bot
INTERIOR = (Fraction(1), Fraction(0), Fraction(1), Fraction(1, 2))
GRID = 12               # exhaustive rational-grid resolution for the G1 enumeration
K_QUANTA = 4000         # best-response granularity for G2 (divisible by 4)
BR_TRIALS = 50          # random-init best-response runs for G2
TRIALS = 20000          # random-instance draws for G3 (paradox band) and G4 (control)


def latency(a, b, x):
    """Affine per-request latency of a pool at flow x (Fraction)."""
    return a * x + b


def total_cost(inst, x):
    """Average latency (== total cost, demand is unit) with flow x on top, 1-x on bottom."""
    a_top, b_top, a_bot, b_bot = inst
    return x * latency(a_top, b_top, x) + (1 - x) * latency(a_bot, b_bot, 1 - x)


def potential(inst, x):
    """Beckmann potential; its minimizer is the Wardrop (selfish) equilibrium flow."""
    a_top, b_top, a_bot, b_bot = inst
    return (a_top * x * x / 2 + b_top * x
            + a_bot * (1 - x) * (1 - x) / 2 + b_bot * (1 - x))


def _clamp01(x):
    if x < 0:
        return Fraction(0)
    if x > 1:
        return Fraction(1)
    return x


def wardrop_flow(inst):
    """Closed-form selfish-equilibrium flow on the top pool (exact Fraction)."""
    a_top, b_top, a_bot, b_bot = inst
    denom = a_top + a_bot
    if denom == 0:  # both pools constant -- everyone takes the cheaper one
        return Fraction(1) if b_top <= b_bot else Fraction(0)
    return _clamp01((a_bot + b_bot - b_top) / denom)


def optimal_flow(inst):
    """Closed-form social-optimum flow on the top pool (marginal-cost condition)."""
    a_top, b_top, a_bot, b_bot = inst
    denom = 2 * (a_top + a_bot)
    if denom == 0:
        return Fraction(1) if b_top <= b_bot else Fraction(0)
    return _clamp01((2 * a_bot + b_bot - b_top) / denom)


def price_of_anarchy(inst):
    """Exact PoA = selfish average latency / optimal average latency (Fraction)."""
    c_eq = total_cost(inst, wardrop_flow(inst))
    c_opt = total_cost(inst, optimal_flow(inst))
    return c_eq / c_opt, c_eq, c_opt


def best_response_equilibrium(inst, K, rng):
    """Sequential single-request best-response over K load quanta to a fixed point.

    State is k = quanta on top (K-k on bottom); a quantum moves whenever the other
    pool would be strictly faster for it. A congestion game is a potential game, so
    this converges to the (here unique) pure equilibrium regardless of start/order.
    Returns (k_final, moves).
    """
    a_top, b_top, a_bot, b_bot = inst
    k = rng.randint(0, K)
    moves = 0
    while True:
        order = [0, 1]
        rng.shuffle(order)
        improved = False
        for d in order:
            if d == 0 and k > 0:  # try to move a top quantum down to bottom
                cur = a_top * Fraction(k, K) + b_top
                alt = a_bot * Fraction(K - k + 1, K) + b_bot
                if alt < cur:
                    k -= 1
                    moves += 1
                    improved = True
                    break
            if d == 1 and k < K:  # try to move a bottom quantum up to top
                cur = a_bot * Fraction(K - k, K) + b_bot
                alt = a_top * Fraction(k + 1, K) + b_top
                if alt < cur:
                    k += 1
                    moves += 1
                    improved = True
                    break
        if not improved:
            return k, moves


def run():
    rng = random.Random(SEED)

    # G1: EXACTLY-TRUE -- closed form vs exhaustive rational-grid enumeration on the
    # tight Pigou instance. The grid minimizer of the Beckmann potential is the
    # selfish equilibrium flow; the grid minimizer of total cost is the social
    # optimum. Both closed forms land on the grid, so the identity is exact.
    grid = [Fraction(i, GRID) for i in range(GRID + 1)]
    eq_x_grid = min(grid, key=lambda x: (potential(PIGOU, x), x))
    opt_x_grid = min(grid, key=lambda x: (total_cost(PIGOU, x), x))
    eq_x_cf = wardrop_flow(PIGOU)
    opt_x_cf = optimal_flow(PIGOU)
    poa_pigou, c_eq_pigou, c_opt_pigou = price_of_anarchy(PIGOU)
    g1_pass = (
        eq_x_grid == eq_x_cf
        and opt_x_grid == opt_x_cf
        and c_eq_pigou == Fraction(1)
        and c_opt_pigou == Fraction(3, 4)
        and poa_pigou == Fraction(4, 3)
        and poa_pigou > 1
    )

    # G2: closed form vs best-response on the interior instance. Best-response from
    # BR_TRIALS random starts/orders must converge to the exact closed-form
    # equilibrium every time (unique pure Nash: k* = 3K/4, average latency 3/4).
    eq_x_int = wardrop_flow(INTERIOR)                 # = 3/4
    c_eq_int_cf = total_cost(INTERIOR, eq_x_int)      # = 3/4
    k_star = eq_x_int.numerator * K_QUANTA // eq_x_int.denominator
    br_latencies = []
    br_k = []
    br_moves_max = 0
    for _ in range(BR_TRIALS):
        k_final, moves = best_response_equilibrium(INTERIOR, K_QUANTA, rng)
        br_k.append(k_final)
        br_latencies.append(total_cost(INTERIOR, Fraction(k_final, K_QUANTA)))
        br_moves_max = max(br_moves_max, moves)
    g2_pass = (
        all(k == k_star for k in br_k)
        and all(lat == c_eq_int_cf for lat in br_latencies)
    )
    poa_int, _, c_opt_int = price_of_anarchy(INTERIOR)

    # G3: >=3sigma statistical -- random Pigou-family instances in the paradox band
    # (top congestible slope a, bottom constant c with 0 < c < a). Every instance
    # must obey PoA <= 4/3 (the tight ceiling never violated) and carry a strictly
    # positive anarchy loss, and the mean loss must be >= Z_GATE sigma above 0.
    losses = []
    within = 0
    positive = 0
    poa_max = Fraction(1)
    for _ in range(TRIALS):
        a = rng.randint(2, 100)
        c = rng.randint(1, a - 1)  # 0 < c < a  -> interior selfish equilibrium
        inst = (Fraction(a), Fraction(0), Fraction(0), Fraction(c))
        poa, _, _ = price_of_anarchy(inst)
        loss = poa - 1
        losses.append(float(loss))
        if poa <= Fraction(4, 3):
            within += 1
        if loss > 0:
            positive += 1
        if poa > poa_max:
            poa_max = poa
    n = len(losses)
    mean_loss = sum(losses) / n
    var_loss = sum((v - mean_loss) ** 2 for v in losses) / n
    std_loss = math.sqrt(var_loss)
    z3 = mean_loss / (std_loss / math.sqrt(n)) if std_loss > 0 else float("inf")
    frac_within = within / n
    frac_positive = positive / n
    g3_pass = (frac_within == 1.0) and (frac_positive == 1.0) and (z3 >= Z_GATE)

    # G4: ROBUSTNESS / REGIME-SHIFT control -- when the constant pool is expensive
    # enough (c >= 2a) selfish routing already IS the social optimum: PoA == 1, zero
    # loss. The 4/3 effect is regime-specific, not a modeling artifact.
    ctrl_efficient = 0
    ctrl_loss_max = Fraction(0)
    for _ in range(TRIALS):
        a = rng.randint(2, 100)
        c = rng.randint(2 * a, 5 * a)  # c >= 2a -> constant pool never worth using
        inst = (Fraction(a), Fraction(0), Fraction(0), Fraction(c))
        poa, _, _ = price_of_anarchy(inst)
        if poa == Fraction(1):
            ctrl_efficient += 1
        if poa - 1 > ctrl_loss_max:
            ctrl_loss_max = poa - 1
    frac_efficient = ctrl_efficient / TRIALS
    g4_pass = (frac_efficient == 1.0) and (ctrl_loss_max == Fraction(0))

    results = {
        "head": "price-of-anarchy-pigou-4-3-bound",
        "seed": SEED,
        "world": {
            "pigou": [str(v) for v in PIGOU],
            "interior": [str(v) for v in INTERIOR],
            "grid": GRID,
            "k_quanta": K_QUANTA,
            "br_trials": BR_TRIALS,
            "trials": TRIALS,
            "z_gate": Z_GATE,
        },
        "g1_exactly_true_pigou": {
            "eq_flow_grid": str(eq_x_grid),
            "eq_flow_closed_form": str(eq_x_cf),
            "opt_flow_grid": str(opt_x_grid),
            "opt_flow_closed_form": str(opt_x_cf),
            "selfish_avg_latency": str(c_eq_pigou),
            "optimal_avg_latency": str(c_opt_pigou),
            "price_of_anarchy": str(poa_pigou),
            "price_of_anarchy_float": round(float(poa_pigou), 6),
            "grid_points": len(grid),
            "exact_match": g1_pass,
            "pass": g1_pass,
        },
        "g2_best_response_interior": {
            "eq_flow_closed_form": str(eq_x_int),
            "k_star": k_star,
            "br_k_unique": len(set(br_k)) == 1,
            "converged_avg_latency": str(br_latencies[0]) if br_latencies else None,
            "closed_form_avg_latency": str(c_eq_int_cf),
            "optimal_avg_latency": str(c_opt_int),
            "price_of_anarchy": str(poa_int),
            "price_of_anarchy_float": round(float(poa_int), 6),
            "trials": BR_TRIALS,
            "moves_max": br_moves_max,
            "pass": g2_pass,
        },
        "g3_bound_and_loss_random": {
            "trials": n,
            "frac_within_4_3_bound": round(frac_within, 6),
            "frac_positive_loss": round(frac_positive, 6),
            "mean_loss": round(mean_loss, 6),
            "std_loss": round(std_loss, 6),
            "z": round(z3, 6),
            "max_poa_float": round(float(poa_max), 6),
            "pass": g3_pass,
        },
        "g4_regime_shift_control": {
            "trials": TRIALS,
            "frac_efficient_poa_1": round(frac_efficient, 6),
            "max_loss": str(ctrl_loss_max),
            "pass": g4_pass,
        },
    }
    results["all_pass"] = g1_pass and g2_pass and g3_pass and g4_pass
    return results


def main():
    r1 = run()
    r2 = run()
    assert r1 == r2, "non-deterministic results dict"
    blob = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(blob.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()

"""Bertrand paradox -- 'probability a random chord exceeds the inscribed-triangle side' has no single answer.

Head: Ask for the probability that a "random" chord of a circle is longer than
the side of the inscribed equilateral triangle, and three equally natural
definitions of "random chord" give EXACTLY 1/3, 1/2, and 1/4. The question is
underspecified, not hard: "uniformly at random" is undefined for a continuous
geometric object until the sampling mechanism is pinned (Bertrand 1889).

Three mechanisms on a circle of radius R (inscribed equilateral triangle side
= sqrt(3)*R); a chord counts as "long" iff it exceeds sqrt(3)*R. The chord's
perpendicular distance from the centre for the threshold length is d* = R/2
(chord = 2*sqrt(R^2 - d^2) = sqrt(3)*R  <=>  d = R/2):
  A "random endpoints": two independent uniform points on the circle.
      long iff the angular gap phi in (2pi/3, 4pi/3)              -> P = 1/3.
  B "random radial point": uniform direction, midpoint uniform on that radius.
      long iff distance d < R/2, with d ~ U[0,R]                  -> P = 1/2.
  C "random midpoint in disk": midpoint uniform over the disk area.
      long iff midpoint within radius R/2, area ratio (1/2)^2     -> P = 1/4.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical
sha256 (sort_keys=True, separators=(",",":")) over the results dict IS the
digest; the dict carries no self field; pretty dump to stdout; floats rounded
6 dp; no on-disk JSON. SEED=20260717; in-process double-run asserts
byte-identical; gates use Z_GATE=3.0.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
M_TRIALS = 200000            # Monte-Carlo draws per method for G1
GRID_1D = 200000            # deterministic 1-D quadrature resolution
GRID_2D = 1500              # deterministic 2-D (disk) quadrature resolution per axis
GRID_TOL = 1e-3             # quadrature vs closed-form agreement tolerance
R_SHIFT = (1, 2, 5, 10)     # scale-invariance sweep radii

METHODS = ("endpoints", "radial", "midpoint")

# Pre-registered exact closed forms (the three classic Bertrand answers).
CF = {"endpoints": Fraction(1, 3), "radial": Fraction(1, 2), "midpoint": Fraction(1, 4)}


def threshold(R):
    """Chord length that equals the inscribed-equilateral-triangle side."""
    return math.sqrt(3.0) * R


def mc_endpoints(R, trials, rng):
    thr = threshold(R)
    hits = 0
    for _ in range(trials):
        a = rng.uniform(0.0, 2.0 * math.pi)
        b = rng.uniform(0.0, 2.0 * math.pi)
        chord = 2.0 * R * abs(math.sin((a - b) / 2.0))
        if chord > thr:
            hits += 1
    return hits / trials


def mc_radial(R, trials, rng):
    thr = threshold(R)
    hits = 0
    for _ in range(trials):
        d = rng.uniform(0.0, R)
        chord = 2.0 * math.sqrt(R * R - d * d)
        if chord > thr:
            hits += 1
    return hits / trials


def mc_midpoint(R, trials, rng):
    thr = threshold(R)
    hits = 0
    for _ in range(trials):
        r = R * math.sqrt(rng.random())   # uniform-in-disk radial coordinate
        chord = 2.0 * math.sqrt(R * R - r * r)
        if chord > thr:
            hits += 1
    return hits / trials


MC = {"endpoints": mc_endpoints, "radial": mc_radial, "midpoint": mc_midpoint}


def quad_endpoints(R):
    """Deterministic 1-D quadrature over the angular gap phi in [0, 2pi)."""
    thr = threshold(R)
    hits = 0
    for i in range(GRID_1D):
        phi = 2.0 * math.pi * (i + 0.5) / GRID_1D
        chord = 2.0 * R * math.sin(phi / 2.0)
        if chord > thr:
            hits += 1
    return hits / GRID_1D


def quad_radial(R):
    """Deterministic 1-D quadrature over the midpoint distance d in [0, R]."""
    thr = threshold(R)
    hits = 0
    for i in range(GRID_1D):
        d = R * (i + 0.5) / GRID_1D
        chord = 2.0 * math.sqrt(max(0.0, R * R - d * d))
        if chord > thr:
            hits += 1
    return hits / GRID_1D


def quad_midpoint(R):
    """Deterministic 2-D quadrature over the disk area (exhaustive grid)."""
    thr = threshold(R)
    inside = 0
    hits = 0
    for ix in range(GRID_2D):
        x = -R + 2.0 * R * (ix + 0.5) / GRID_2D
        for iy in range(GRID_2D):
            y = -R + 2.0 * R * (iy + 0.5) / GRID_2D
            r2 = x * x + y * y
            if r2 <= R * R:
                inside += 1
                chord = 2.0 * math.sqrt(max(0.0, R * R - r2))
                if chord > thr:
                    hits += 1
    return hits / inside


QUAD = {"endpoints": quad_endpoints, "radial": quad_radial, "midpoint": quad_midpoint}


def exact_fractions():
    """Exact closed forms derived from the geometry (pi cancels)."""
    # Threshold perpendicular distance fraction d*/R from chord = sqrt(3)R:
    #   R^2 - d^2 = 3R^2/4  =>  (d/R)^2 = 1/4.
    d2_over_r2 = Fraction(1, 4)
    d_over_r = Fraction(1, 2)               # sqrt(1/4); verified against d2 below
    assert d_over_r * d_over_r == d2_over_r2
    # endpoints: favourable gap measure (4/3 - 2/3)*pi over 2*pi (pi cancels).
    endpoints = (Fraction(4, 3) - Fraction(2, 3)) / Fraction(2, 1)
    radial = d_over_r                        # d < R/2 over [0, R]
    midpoint = d2_over_r2                     # area within radius R/2 over disk
    return {"endpoints": endpoints, "radial": radial, "midpoint": midpoint}


def run():
    rng = random.Random(SEED)

    # G1 -- Monte-Carlo agreement with each exact closed form at R=1 (>= 3 sigma).
    g1 = {}
    g1_pass = True
    for m in METHODS:
        p_star = float(CF[m])
        p_hat = MC[m](1.0, M_TRIALS, rng)
        se = math.sqrt(p_star * (1.0 - p_star) / M_TRIALS)
        z = abs(p_hat - p_star) / se
        ok = z < Z_GATE
        g1_pass = g1_pass and ok
        g1[m] = {"p_star": round(p_star, 6), "p_hat": round(p_hat, 6),
                 "std_error": round(se, 6), "z": round(z, 6), "pass": ok}

    # G2 -- exactly-true: exact geometric fraction == pre-registered closed form,
    # corroborated by deterministic quadrature within GRID_TOL.
    exact = exact_fractions()
    g2 = {}
    g2_pass = True
    for m in METHODS:
        frac_ok = (exact[m] == CF[m])
        q = QUAD[m](1.0)
        quad_ok = abs(q - float(CF[m])) < GRID_TOL
        ok = frac_ok and quad_ok
        g2_pass = g2_pass and ok
        g2[m] = {"exact_numerator": exact[m].numerator,
                 "exact_denominator": exact[m].denominator,
                 "closed_form_numerator": CF[m].numerator,
                 "closed_form_denominator": CF[m].denominator,
                 "exact_match": frac_ok,
                 "quadrature": round(q, 6),
                 "quadrature_agrees": quad_ok,
                 "pass": ok}

    # G3 -- robustness/shift: each method's probability is scale-invariant
    # (within-method spread across radii < 0.01), AND the three answers genuinely
    # differ (cross-method spread of the exact values > 0.08): the paradox is real.
    sweep = {m: {str(R): round(QUAD[m](R), 6) for R in R_SHIFT} for m in METHODS}
    within = {}
    g3a = True
    for m in METHODS:
        vals = list(sweep[m].values())
        spread = max(vals) - min(vals)
        within[m] = round(spread, 6)
        g3a = g3a and (spread < 0.01)
    cf_floats = [float(CF[m]) for m in METHODS]
    cross_spread = max(cf_floats) - min(cf_floats)
    g3b = cross_spread > 0.08
    g3_pass = g3a and g3b

    results = {
        "head": "bertrand-paradox-chord-nonuniqueness",
        "seed": SEED,
        "world": {
            "methods": list(METHODS),
            "m_trials": M_TRIALS,
            "grid_1d": GRID_1D,
            "grid_2d": GRID_2D,
            "grid_tol": GRID_TOL,
            "r_shift": list(R_SHIFT),
            "z_gate": Z_GATE,
        },
        "g1_montecarlo_vs_closedform": g1,
        "g2_exactly_true": g2,
        "g3_robustness_shift": {
            "sweep": sweep,
            "within_method_spread": within,
            "cross_method_spread": round(cross_spread, 6),
            "scale_invariant": g3a,
            "answers_differ": g3b,
            "pass": g3_pass,
        },
        "g1_pass": g1_pass,
        "g2_pass": g2_pass,
        "g3_pass": g3_pass,
    }
    results["all_pass"] = g1_pass and g2_pass and g3_pass
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

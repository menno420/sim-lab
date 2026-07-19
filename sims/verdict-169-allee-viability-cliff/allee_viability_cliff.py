#!/usr/bin/env python3
"""PROPOSAL 156 — The strong Allee effect viability cliff: below a critical
density A a population deterministically DRAINS to extinction, above A it
climbs to carrying capacity K — a sharp basin boundary, not a gentle slope
(round-36 UNRELATED slot).

Head claim (G1/G2): under the strong-Allee growth law a population seeded
JUST BELOW the critical density A is doomed (extinction fraction ≈ 1) while a
population seeded JUST ABOVE A persists (extinction fraction ≈ 0) — a viability
CLIFF at N = A, not a smooth dose-response. G3: the cliff survives a shift to
heavier demographic noise (the below/above extinction gap stays wide).

Mechanism. The strong Allee effect gives a per-capita growth rate that is
NEGATIVE below A (mate-finding / cooperation failure at low density) and
positive between A and K. The deterministic per-step map (dt small):
    dN = r * N * (1 - N/K) * (N/A - 1)
    N_{t+1} = N_t + dt * dN
has THREE fixed points: 0 (stable), A (UNSTABLE — the Allee threshold), and K
(stable). A is the separatrix: the basin boundary between the extinction well
(0) and the persistence well (K). Deterministically, N0 < A → 0 and N0 > A → K,
so a bisection on the initial density that separates "drains to 0" from "climbs
to K" must land EXACTLY on A (invariance probe below, across three (r,K) pairs).

Add demographic noise (fluctuation scales with sqrt(N), the standard
population-size term):
    N_{t+1} = N_t + dt*dN + sigma * sqrt(max(N_t,0)) * sqrt(dt) * eps,  eps~N(0,1)
A trajectory is EXTINCT if N ever falls to EXT_EPS within T_STEPS. The cliff
becomes a stochastic statement: p_below ≈ 1, p_above ≈ 0.

Grounded in Allee (1931) — the original aggregation/undercrowding studies — and
the modern synthesis Courchamp, Berec & Gascoigne, "Allee Effects in Ecology
and Conservation" (2008). Reference: Wikipedia "Allee effect".

Gates (evaluation order; APPROVE iff ALL hold; z on the /se convention, gate 3.0):
  G1  doomed-below : p_below from N0=A(1-DELTA);  z1 = (p_below - 0.5)/se        >= 3
  G2  safe-above   : p_above from N0=A(1+DELTA);  z2 = (0.5 - p_above)/se        >= 3
  G3  robust-shift : gap' = p_below_hi - p_above_hi at sigma_hi;
                     z3 = (gap' - GAP_MIN)/se_gap                                >= 3
G2 mirrors the sibling leak-ceiling NEGATION pattern: a "below-a-ceiling"
quantity (p_above must sit UNDER 0.5) is gated as (0.5 - stat)/se.

Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. SEED pinned; two in-process
runs asserted identical; results dict plus its sha256 printed. Stdlib only.
"""

import hashlib
import json
import math
import random

SEED = 20260717

# --- strong-Allee growth law (main world) -----------------------------------
R_MAIN = 0.6         # intrinsic growth rate
K_MAIN = 100.0       # carrying capacity (stable)
A = 30.0             # Allee threshold (UNSTABLE separatrix)
DT = 0.02            # integration step

# --- deterministic basin-boundary invariance probe --------------------------
# three (r, K) pairs, all sharing A=30 — the boundary must be A for every pair
DET_PAIRS = [(0.6, 100.0), (0.3, 150.0), (0.9, 80.0)]
DET_STEPS = 6000     # steps per deterministic run inside the bisection
DET_ITERS = 100      # bisection iterations
DET_TOL = 1e-6       # boundary tolerance vs A

# --- stochastic (demographic-noise) layer -----------------------------------
R_TRIALS = 400
T_STEPS = 2000
EXT_EPS = 0.5        # extinction absorbing level
DELTA = 0.15         # offset from A: below = A(1-DELTA), above = A(1+DELTA)
SIGMA_LO = 0.25      # baseline demographic-noise amplitude
SIGMA_HI = 0.55      # shifted (heavier) demographic-noise amplitude

# --- gate machinery ---------------------------------------------------------
Z_GATE = 3.0
SE = math.sqrt(0.25 / R_TRIALS)            # proportion se, conservative H0=0.5
SE_GAP = math.sqrt(2.0 * 0.25 / R_TRIALS)  # se of a difference of two proportions
GAP_MIN = 0.6                              # minimum below/above extinction gap


def det_step(n, r, k, a, dt):
    dn = r * n * (1.0 - n / k) * (n / a - 1.0)
    return n + dt * dn


def det_final(n0, r, k, a, dt, steps):
    n = n0
    for _ in range(steps):
        n = det_step(n, r, k, a, dt)
    return n


def basin_boundary(r, k, a, dt):
    """Bisect the initial density separating drain-to-0 from climb-to-K.

    A is the unstable fixed point, so the deterministic flow is monotone away
    from it: N0 > A ends above A, N0 < A ends below A. Classifying a finished
    run by (final > A) therefore converges the bisection exactly onto A — no
    noise, no rng consumed.
    """
    lo = 1.0            # < A → drains (final < A)
    hi = 0.6 * k        # > A and < K → climbs (final > A)
    for _ in range(DET_ITERS):
        if hi - lo <= DET_TOL:
            break
        mid = 0.5 * (lo + hi)
        if det_final(mid, r, k, a, dt, DET_STEPS) > a:
            hi = mid    # mid climbed → boundary is below mid
        else:
            lo = mid    # mid drained → boundary is above mid
    return 0.5 * (lo + hi)


def is_extinct(rng, n0, r, k, a, dt, sigma, t_steps, ext_eps):
    """One stochastic trajectory; True iff N reaches the extinction level."""
    n = n0
    root_dt = math.sqrt(dt)
    for _ in range(t_steps):
        dn = r * n * (1.0 - n / k) * (n / a - 1.0)
        n = n + dt * dn + sigma * math.sqrt(max(n, 0.0)) * root_dt * rng.gauss(0.0, 1.0)
        if n <= ext_eps:
            return True
    return False


def extinction_fraction(rng, n0, r, k, a, dt, sigma, trials, t_steps, ext_eps):
    ext = 0
    for _ in range(trials):
        if is_extinct(rng, n0, r, k, a, dt, sigma, t_steps, ext_eps):
            ext += 1
    return ext / trials


def r6(x):
    return round(float(x), 6)


def run():
    rng = random.Random(SEED)

    # deterministic invariance probe (consumes no rng)
    boundaries = [basin_boundary(r, k, A, DT) for (r, k) in DET_PAIRS]

    n_below = A * (1.0 - DELTA)
    n_above = A * (1.0 + DELTA)

    # baseline noise: G1 (below) and G2 (above), drawn in fixed order
    p_below = extinction_fraction(rng, n_below, R_MAIN, K_MAIN, A, DT, SIGMA_LO, R_TRIALS, T_STEPS, EXT_EPS)
    p_above = extinction_fraction(rng, n_above, R_MAIN, K_MAIN, A, DT, SIGMA_LO, R_TRIALS, T_STEPS, EXT_EPS)

    # shifted (heavier) noise: G3
    p_below_hi = extinction_fraction(rng, n_below, R_MAIN, K_MAIN, A, DT, SIGMA_HI, R_TRIALS, T_STEPS, EXT_EPS)
    p_above_hi = extinction_fraction(rng, n_above, R_MAIN, K_MAIN, A, DT, SIGMA_HI, R_TRIALS, T_STEPS, EXT_EPS)

    z1 = (p_below - 0.5) / SE
    z2 = (0.5 - p_above) / SE
    gap = p_below_hi - p_above_hi
    z3 = (gap - GAP_MIN) / SE_GAP

    g1 = z1 >= Z_GATE
    g2 = z2 >= Z_GATE
    g3 = z3 >= Z_GATE
    all_pass = g1 and g2 and g3
    order = [("G1", g1), ("G2", g2), ("G3", g3)]
    first_failing = next((name for name, ok in order if not ok), None)

    return {
        "params": {
            "r": R_MAIN,
            "k": K_MAIN,
            "a": A,
            "dt": DT,
            "seed": SEED,
            "r_trials": R_TRIALS,
            "delta": DELTA,
            "sigma_lo": SIGMA_LO,
            "sigma_hi": SIGMA_HI,
            "t_steps": T_STEPS,
            "ext_eps": EXT_EPS,
            "z_gate": Z_GATE,
            "gap_min": GAP_MIN,
        },
        "det_pairs": [[r6(r), r6(k)] for (r, k) in DET_PAIRS],
        "det_basin_boundaries": [r6(b) for b in boundaries],
        "n_below": r6(n_below),
        "n_above": r6(n_above),
        "p_below": r6(p_below),
        "p_above": r6(p_above),
        "z1": r6(z1),
        "z2": r6(z2),
        "p_below_hi": r6(p_below_hi),
        "p_above_hi": r6(p_above_hi),
        "gap": r6(gap),
        "z3": r6(z3),
        "g1_doomed_below": g1,
        "g2_safe_above": g2,
        "g3_robust_shift": g3,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
    }


def main():
    results = run()
    again = run()
    assert results == again, "non-deterministic: in-process double run diverged"

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print("Strong-Allee viability-cliff verifier — deterministic basin + demographic noise")
    print(f"  det boundaries (must ≈ A={A}) : {results['det_basin_boundaries']}")
    print(f"  G1 doomed-below : p_below={results['p_below']:.6f}  z1={results['z1']:+.6f}  (null=0.5)")
    print(f"  G2 safe-above   : p_above={results['p_above']:.6f}  z2={results['z2']:+.6f}  (ceiling null=0.5)")
    print(f"  G3 robust-shift : gap={results['gap']:.6f}  z3={results['z3']:+.6f}  (null={GAP_MIN})")
    print(f"  gates : G1={results['g1_doomed_below']}  G2={results['g2_safe_above']}  G3={results['g3_robust_shift']}  all_pass={results['all_pass']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

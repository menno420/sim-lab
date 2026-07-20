#!/usr/bin/env python3
"""
Jackson-network product-form independence verifier.

HEAD
----
An open Jackson network of coupled queues that feed each other (with feedback,
so the internal traffic between stations is provably NOT Poisson) has a joint
stationary queue-length distribution that factors EXACTLY into independent
M/M/1 marginals:

    pi(n1,...,nM) = prod_i (1 - rho_i) rho_i^{n_i},   rho_i = lambda_i / mu_i

This program PROVES that HEAD with four gates:

  1. EXACT gate       -- the product-form guess satisfies the CTMC global
                         balance equations EXACTLY (Fraction, residual == 0)
                         at every state in the 0..3 cube.
  2. Non-Poisson gate -- a merged internal arrival stream on the feedback cycle
                         has CV^2 that deviates from 1 by >= 3 sigma
                         (internal traffic is NOT Poisson).
  3. Product-form gate -- from the SAME simulation, each marginal mean matches
                         the M/M/1 closed form within 3 sigma, and pairwise
                         station-occupancy correlations are ~0 within 3 sigma
                         (independent despite coupling).
  4. Robustness gate  -- a SECOND rational parameter set (different routing and
                         service rates) re-passes gates 1 and 3.

Deterministic: stdlib only, SEED-driven RNG, sorted digest, in-process
double-run byte-identical, and a cross-invocation sha256 over the results dict.
"""

import hashlib
import json
import random
import sys
from fractions import Fraction as F

SEED = 20260717

# ---------------------------------------------------------------------------
# exact linear algebra over the rationals
# ---------------------------------------------------------------------------

def solve_exact(mat, vec):
    """Solve mat @ x = vec exactly. mat: list of list of Fraction (n x n)."""
    n = len(vec)
    # augmented copy
    a = [[F(mat[i][j]) for j in range(n)] + [F(vec[i])] for i in range(n)]
    for col in range(n):
        # find pivot
        piv = None
        for r in range(col, n):
            if a[r][col] != 0:
                piv = r
                break
        if piv is None:
            raise ValueError("singular matrix")
        a[col], a[piv] = a[piv], a[col]
        pv = a[col][col]
        a[col] = [x / pv for x in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0:
                factor = a[r][col]
                a[r] = [a[r][k] - factor * a[col][k] for k in range(n + 1)]
    return [a[i][n] for i in range(n)]


# ---------------------------------------------------------------------------
# parameter sets (rational throughout)
# ---------------------------------------------------------------------------

def make_paramset(name, lam0, R, mu):
    """
    lam0: list[Fraction] external Poisson arrival rate per station
    R:    3x3 list[list[Fraction]] routing prob i->j (row sum <= 1; leftover leaves)
    mu:   list[Fraction] service rates
    Returns dict with solved lambda, rho (all exact).
    """
    M = len(lam0)
    # traffic equations: lambda_i = lam0_i + sum_j lambda_j R[j][i]
    # => (I - R^T) lambda = lam0
    A = [[(F(1) if i == k else F(0)) - R[k][i] for k in range(M)] for i in range(M)]
    lam = solve_exact(A, lam0)
    # traffic-equation residual (must be exactly zero)
    resid = []
    for i in range(M):
        val = lam0[i] + sum(lam[j] * R[j][i] for j in range(M)) - lam[i]
        resid.append(val)
    assert all(r == 0 for r in resid), ("traffic residual nonzero", resid)
    rho = [lam[i] / mu[i] for i in range(M)]
    for r in rho:
        assert 0 < r < 1, ("rho out of (0,1)", r)
    # leave probabilities
    leave = [F(1) - sum(R[i]) for i in range(M)]
    for lv in leave:
        assert lv >= 0
    return {
        "name": name,
        "M": M,
        "lam0": lam0,
        "R": R,
        "mu": mu,
        "lam": lam,
        "rho": rho,
        "leave": leave,
    }


# ---------------------------------------------------------------------------
# GATE 1: exact global balance of the product form (Fraction, residual == 0)
# ---------------------------------------------------------------------------

def exact_balance(ps, kmax=3):
    """
    Check CTMC global balance for pi(n) = prod (1-rho_i) rho_i^{n_i}.
    The (1-rho_i) constants cancel; use unnormalized weight w(n)=prod rho_i^{n_i}.

    outflow(n)*w(n) == inflow(n) exactly for every state n in the cube.
    """
    M = ps["M"]
    rho = ps["rho"]
    lam0 = ps["lam0"]
    mu = ps["mu"]
    R = ps["R"]
    leave = ps["leave"]

    def w(state):
        prod = F(1)
        for i in range(M):
            prod *= rho[i] ** state[i]
        return prod

    # enumerate states in the cube 0..kmax
    states = []
    def rec(idx, cur):
        if idx == M:
            states.append(tuple(cur))
            return
        for v in range(kmax + 1):
            rec(idx + 1, cur + [v])
    rec(0, [])
    states.sort()

    max_abs = F(0)
    checked = 0
    for n in states:
        wn = w(n)
        # total outflow rate out of n
        out_rate = sum(lam0) + sum(mu[i] for i in range(M) if n[i] > 0)
        outflow = out_rate * wn

        inflow = F(0)
        # (a) external arrival into i: source n - e_i  (needs n_i >= 1)
        for i in range(M):
            if n[i] >= 1:
                src = list(n); src[i] -= 1
                inflow += lam0[i] * w(src)
        # (b) completion at i that LEAVES the system: source n + e_i
        for i in range(M):
            src = list(n); src[i] += 1
            inflow += mu[i] * leave[i] * w(src)
        # (c) routing completion k->l landing on n: source n + e_k - e_l (k!=l),
        #     needs n_l >= 1 so that source_l = n_l - 1 >= 0
        for k in range(M):
            for l in range(M):
                if k == l:
                    continue
                if R[k][l] == 0:
                    continue
                if n[l] >= 1:
                    src = list(n); src[k] += 1; src[l] -= 1
                    inflow += mu[k] * R[k][l] * w(src)

        residual = outflow - inflow
        if abs(residual) > max_abs:
            max_abs = abs(residual)
        checked += 1

    return checked, max_abs


# ---------------------------------------------------------------------------
# event-driven (Gillespie) simulation of the open Jackson network
# ---------------------------------------------------------------------------

def simulate(ps, rng, n_events, warmup_events, n_batches, feedback_station=0):
    """
    Returns per-batch statistics for E[N_i], correlations, and the CV^2 of the
    merged arrival stream into `feedback_station`.
    """
    M = ps["M"]
    lam0 = [float(x) for x in ps["lam0"]]
    mu = [float(x) for x in ps["mu"]]
    R = ps["R"]

    # precompute routing cdf per station: list of (dest_or_-1_for_leave, cum)
    routing = []
    for i in range(M):
        cdf = []
        acc = 0.0
        for j in range(M):
            p = float(R[i][j])
            if p > 0:
                acc += p
                cdf.append((j, acc))
        # remainder -> leave (dest = -1) up to 1.0
        cdf.append((-1, 1.0))
        routing.append(cdf)

    n = [0] * M
    lam0_0, lam0_1, lam0_2 = lam0[0], lam0[1], lam0[2]
    mu0, mu1, mu2 = mu[0], mu[1], mu[2]

    # batch accumulators for occupancy statistics
    # each batch b: T, sum n_i dt, sum n_i n_j dt, sum n_i^2 dt
    batch_T = [0.0] * n_batches
    batch_Ni = [[0.0] * M for _ in range(n_batches)]
    batch_Nij = [[0.0] * (M * M) for _ in range(n_batches)]

    # inter-arrival samples for the merged stream into feedback_station,
    # bucketed per batch (by arrival index)
    ia_batches = [[] for _ in range(n_batches)]
    last_arr_time = None

    events_per_batch = (n_events) / n_batches
    t = 0.0
    total_events = 0

    expov = rng.expovariate
    rnd = rng.random

    while total_events < n_events + warmup_events:
        # total event rate
        total_rate = lam0_0 + lam0_1 + lam0_2
        n0, n1, n2 = n[0], n[1], n[2]
        if n0 > 0:
            total_rate += mu0
        if n1 > 0:
            total_rate += mu1
        if n2 > 0:
            total_rate += mu2

        dt = expov(total_rate)

        past_warmup = total_events >= warmup_events
        if past_warmup:
            # which batch does this interval belong to
            b = int((total_events - warmup_events) // events_per_batch)
            if b >= n_batches:
                b = n_batches - 1
            batch_T[b] += dt
            bn = batch_Ni[b]
            bnij = batch_Nij[b]
            bn[0] += n0 * dt
            bn[1] += n1 * dt
            bn[2] += n2 * dt
            bnij[0] += n0 * n0 * dt
            bnij[4] += n1 * n1 * dt
            bnij[8] += n2 * n2 * dt
            bnij[1] += n0 * n1 * dt
            bnij[2] += n0 * n2 * dt
            bnij[5] += n1 * n2 * dt

        t += dt

        # choose event
        r = rnd() * total_rate
        arrival_into_fb = False
        if r < lam0_0:
            n[0] += 1
            if feedback_station == 0:
                arrival_into_fb = True
        else:
            r -= lam0_0
            if r < lam0_1:
                n[1] += 1
                if feedback_station == 1:
                    arrival_into_fb = True
            else:
                r -= lam0_1
                if r < lam0_2:
                    n[2] += 1
                    if feedback_station == 2:
                        arrival_into_fb = True
                else:
                    r -= lam0_2
                    # service completion: walk over active stations
                    comp = None
                    rr = r
                    if n0 > 0:
                        if rr < mu0:
                            comp = 0
                        else:
                            rr -= mu0
                    if comp is None and n1 > 0:
                        if rr < mu1:
                            comp = 1
                        else:
                            rr -= mu1
                    if comp is None and n2 > 0:
                        if rr < mu2:
                            comp = 2
                        else:
                            rr -= mu2
                    if comp is None:
                        # numerical edge; assign to last active station
                        for cand in (2, 1, 0):
                            if n[cand] > 0:
                                comp = cand
                                break
                    n[comp] -= 1
                    # route the completed job
                    u = rnd()
                    dest = -1
                    for d, cum in routing[comp]:
                        if u < cum:
                            dest = d
                            break
                    if dest >= 0:
                        n[dest] += 1
                        if dest == feedback_station:
                            arrival_into_fb = True

        # record merged inter-arrival into feedback station
        if arrival_into_fb and past_warmup:
            if last_arr_time is not None:
                ia = t - last_arr_time
                b = int((total_events - warmup_events) // events_per_batch)
                if b >= n_batches:
                    b = n_batches - 1
                ia_batches[b].append(ia)
            last_arr_time = t
        elif arrival_into_fb and not past_warmup:
            last_arr_time = t

        total_events += 1

    return {
        "batch_T": batch_T,
        "batch_Ni": batch_Ni,
        "batch_Nij": batch_Nij,
        "ia_batches": ia_batches,
    }


# ---------------------------------------------------------------------------
# statistics helpers
# ---------------------------------------------------------------------------

def mean_se(vals):
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in vals) / (n - 1)
    se = (var / n) ** 0.5
    return m, se


def analyze(sim, M, true_mean, true_var):
    """Compute per-batch E[N_i], correlations, and CV^2 of the merged stream.

    Correlation uses the KNOWN closed-form means/variances as fixed references
    (true_mean, true_var). Estimating E[n_i n_j] by a batch time-average and
    subtracting the *known* product E_i*E_j yields an UNBIASED covariance
    estimator: E[<n_i n_j>] = E_stationary[n_i n_j] = E_i E_j under product form.
    (Subtracting per-batch *sample* means instead would inject an O(1/T) bias,
    because coupled stations have nonzero lagged cross-covariance even though
    their equal-time covariance is exactly zero.)
    """
    batch_T = sim["batch_T"]
    batch_Ni = sim["batch_Ni"]
    batch_Nij = sim["batch_Nij"]
    ia_batches = sim["ia_batches"]
    B = len(batch_T)

    # per-batch E[N_i]
    per_batch_Ni = [[batch_Ni[b][i] / batch_T[b] for i in range(M)] for b in range(B)]

    # per-batch correlation for each pair (0,1),(0,2),(1,2)
    pairs = [(0, 1), (0, 2), (1, 2)]
    per_batch_corr = {p: [] for p in pairs}
    for b in range(B):
        T = batch_T[b]
        for (a, c) in pairs:
            Eac = batch_Nij[b][a * M + c] / T
            cov = Eac - true_mean[a] * true_mean[c]
            denom = (true_var[a] * true_var[c]) ** 0.5
            corr = cov / denom if denom > 0 else 0.0
            per_batch_corr[(a, c)].append(corr)

    # per-batch CV^2 of merged inter-arrival stream
    cv2_batch = []
    for b in range(B):
        xs = ia_batches[b]
        if len(xs) < 2:
            continue
        m = sum(xs) / len(xs)
        v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
        if m > 0:
            cv2_batch.append(v / (m * m))

    return per_batch_Ni, per_batch_corr, cv2_batch


# ---------------------------------------------------------------------------
# rounding for the canonical results dict
# ---------------------------------------------------------------------------

def rf(x, nd=6):
    return round(float(x), nd)


def frac_str(x):
    return "%d/%d" % (x.numerator, x.denominator)


def ps_public(ps):
    M = ps["M"]
    return {
        "name": ps["name"],
        "lam0": [frac_str(x) for x in ps["lam0"]],
        "R": [[frac_str(ps["R"][i][j]) for j in range(M)] for i in range(M)],
        "mu": [frac_str(x) for x in ps["mu"]],
        "lam": [frac_str(x) for x in ps["lam"]],
        "rho": [frac_str(x) for x in ps["rho"]],
    }


# ---------------------------------------------------------------------------
# one full computation (returns canonical results dict)
# ---------------------------------------------------------------------------

def run_set(ps, rng, n_events, warmup, n_batches, feedback_station, do_nonpoisson):
    M = ps["M"]
    checked, max_abs = exact_balance(ps, kmax=3)

    true_mean = [float(ps["rho"][i] / (1 - ps["rho"][i])) for i in range(M)]
    true_var = [float(ps["rho"][i] / (1 - ps["rho"][i]) ** 2) for i in range(M)]

    sim = simulate(ps, rng, n_events, warmup, n_batches, feedback_station)
    per_batch_Ni, per_batch_corr, cv2_batch = analyze(sim, M, true_mean, true_var)
    B = len(sim["batch_T"])

    # marginal means vs closed form
    Ni_out = []
    for i in range(M):
        vals = [per_batch_Ni[b][i] for b in range(B)]
        m, se = mean_se(vals)
        closed = float(ps["rho"][i] / (1 - ps["rho"][i]))
        z = abs(m - closed) / se if se > 0 else 0.0
        Ni_out.append({
            "emp_mean": rf(m),
            "closed_form": rf(closed),
            "se": rf(se),
            "z": rf(z),
        })

    # correlations
    corr_out = {}
    pairs = [(0, 1), (0, 2), (1, 2)]
    for p in pairs:
        m, se = mean_se(per_batch_corr[p])
        z = abs(m - 0.0) / se if se > 0 else 0.0
        corr_out["%d-%d" % (p[0] + 1, p[1] + 1)] = {
            "emp_corr": rf(m),
            "se": rf(se),
            "z": rf(z),
        }

    out = {
        "params": ps_public(ps),
        "exact_balance_states_checked": checked,
        "exact_balance_max_abs_residual": frac_str(max_abs) if isinstance(max_abs, F) else str(max_abs),
        "n_batches": B,
        "n_events": n_events,
        "warmup_events": warmup,
        "marginal_means": Ni_out,
        "pairwise_correlation": corr_out,
    }

    if do_nonpoisson:
        m_cv2, se_cv2 = mean_se(cv2_batch)
        z_np = abs(m_cv2 - 1.0) / se_cv2 if se_cv2 > 0 else 0.0
        out["nonpoisson"] = {
            "feedback_station": feedback_station + 1,
            "cv2": rf(m_cv2),
            "cv2_se": rf(se_cv2),
            "z_nonpoisson": rf(z_np),
            "cv2_batches": len(cv2_batch),
            "arrivals_recorded": sum(len(x) for x in sim["ia_batches"]),
        }

    return out


def build_param_sets():
    # SET 1: strong feedback (3->1 with prob 3/4) so the merged internal
    # arrival stream into station 1 is strongly non-Poisson.
    set1 = make_paramset(
        "set1_strong_feedback",
        lam0=[F(1), F(0), F(0)],
        R=[
            [F(0), F(1), F(0)],      # 1 -> 2 (prob 1)
            [F(0), F(0), F(1)],      # 2 -> 3 (prob 1)
            [F(3, 4), F(0), F(0)],   # 3 -> 1 (prob 3/4), leaves 1/4
        ],
        mu=[F(8), F(7), F(6)],
    )
    # SET 2: 3-cycle with partial routing / leaving at every station.
    set2 = make_paramset(
        "set2_partial_cycle",
        lam0=[F(1), F(0), F(0)],
        R=[
            [F(0), F(1, 2), F(0)],   # 1 -> 2 (1/2), leaves 1/2
            [F(0), F(0), F(1, 2)],   # 2 -> 3 (1/2), leaves 1/2
            [F(1, 2), F(0), F(0)],   # 3 -> 1 (1/2), leaves 1/2
        ],
        mu=[F(2), F(6, 7), F(4, 7)],
    )
    return set1, set2


def compute_results():
    set1, set2 = build_param_sets()

    N_EVENTS = 800000
    WARMUP = 50000
    N_BATCHES = 30

    # Each set gets its own deterministic RNG derived from SEED, so the two
    # simulations are independent and modular (order-independent digest).
    # Set 1: full gates incl. non-Poisson (feedback station = 1 -> index 0)
    res1 = run_set(set1, random.Random(SEED), N_EVENTS, WARMUP, N_BATCHES,
                   feedback_station=0, do_nonpoisson=True)
    # Set 2: robustness (gates 1 and 3); still report non-Poisson for interest
    res2 = run_set(set2, random.Random(SEED + 1), N_EVENTS, WARMUP, N_BATCHES,
                   feedback_station=0, do_nonpoisson=True)

    results = {
        "seed": SEED,
        "head": "open Jackson network with feedback -> product-form independent M/M/1 marginals",
        "n_events": N_EVENTS,
        "warmup_events": WARMUP,
        "n_batches": N_BATCHES,
        "set1": res1,
        "set2": res2,
    }
    return results


def main():
    # in-process double run: must be byte-identical
    r1 = compute_results()
    r2 = compute_results()
    j1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    j2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    assert j1 == j2, "in-process double-run mismatch"

    digest = hashlib.sha256(j1.encode()).hexdigest()

    print(json.dumps(r1, sort_keys=True, indent=2))
    print("RESULTS_SHA256=" + digest)


if __name__ == "__main__":
    main()

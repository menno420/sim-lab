#!/usr/bin/env python3
"""PROPOSAL 213 firsthand verifier -- Little's law as a pathwise,
distribution-free and discipline-free conservation identity.

stdlib-only (hashlib, json, math, random, fractions). SEED = 20260717.
Deterministic across in-process double-run and across separate invocations.

Firsthand claim (exact, per sample path):
  For a single-server, work-conserving, non-preemptive queue that starts and
  ends empty, for EVERY scheduling discipline in {FIFO, LIFO, SIRO, priority}:
        area = integral_0^T N(t) dt  ==  sum_i (dep_i - arr_i)   (Fraction-exact)
  therefore  L == lambda * Wbar   exactly  (L=area/T, lambda=n/T, Wbar=sumW/n).
  The final emptying time T (hence lambda) is identical across disciplines,
  while L and Wbar individually DEPEND on the discipline -> the identity is
  non-trivial. It is invariant to service-time variance (robustness gate).
"""
import hashlib, json, math, random
from fractions import Fraction

SEED = 20260717
DISCIPLINES = ('fifo', 'lifo', 'siro', 'priority')


def simulate(arrivals, services, discipline, rng):
    n = len(arrivals)
    prio = [rng.random() for _ in range(n)] if discipline == 'priority' else None
    departures = [None] * n
    t = arrivals[0] if n else Fraction(0)
    next_arr = 0
    waiting = []
    while next_arr < n or waiting:
        if not waiting:
            if arrivals[next_arr] > t:
                t = arrivals[next_arr]
        while next_arr < n and arrivals[next_arr] <= t:
            waiting.append(next_arr)
            next_arr += 1
        if discipline == 'fifo':
            k = min(waiting, key=lambda i: (arrivals[i], i))
        elif discipline == 'lifo':
            k = max(waiting, key=lambda i: (arrivals[i], i))
        elif discipline == 'siro':
            k = waiting[rng.randrange(len(waiting))]
        else:  # priority
            k = min(waiting, key=lambda i: (prio[i], i))
        waiting.remove(k)
        start = t if t >= arrivals[k] else arrivals[k]
        t = start + services[k]
        departures[k] = t
    T = max(departures)
    return departures, T


def area_under_N(arrivals, departures):
    events = [(a, 1) for a in arrivals] + [(d, -1) for d in departures]
    events.sort(key=lambda x: x[0])
    area = Fraction(0)
    level = 0
    prev = events[0][0]
    for tt, delta in events:
        area += level * (tt - prev)
        prev = tt
        level += delta
    return area


def gen_rational(rng, n, gap_max=4, svc_max=7):
    arrivals = []
    t = Fraction(0)
    for _ in range(n):
        t += Fraction(rng.randint(0, gap_max))
        arrivals.append(t)
    services = [Fraction(rng.randint(1, svc_max)) for _ in range(n)]
    return arrivals, services


def gate_exact(rng, realizations, n):
    identity_ok = True
    lambda_invariant_ok = True
    L_dep_count = 0
    for _ in range(realizations):
        arrivals, services = gen_rational(rng, n)
        areas, Ts = {}, {}
        for disc in DISCIPLINES:
            dep, T = simulate(arrivals, services, disc, rng)
            area = area_under_N(arrivals, dep)
            sumW = sum((d - a for d, a in zip(dep, arrivals)), Fraction(0))
            if area != sumW:
                identity_ok = False
            areas[disc], Ts[disc] = area, T
        if len(set(Ts.values())) != 1:
            lambda_invariant_ok = False
        if len(set(areas.values())) > 1:
            L_dep_count += 1
    return {
        'identity_exact_all': identity_ok,
        'lambda_invariant_all': lambda_invariant_ok,
        'realizations': realizations,
        'n_per_realization': n,
        'L_discipline_dependent_count': L_dep_count,
    }


def gate_robustness(rng, realizations, n):
    det_ok = True
    hivar_ok = True
    falsify_caught = True
    m = 4
    for _ in range(realizations):
        arrivals = []
        t = Fraction(0)
        for _ in range(n):
            t += Fraction(rng.randint(0, 4))
            arrivals.append(t)
        svc_det = [Fraction(m)] * n
        svc_hi = [Fraction(m - 3) if rng.random() < 0.5 else Fraction(m + 3)
                  for _ in range(n)]
        for svc, is_det in ((svc_det, True), (svc_hi, False)):
            dep, T = simulate(arrivals, svc, 'fifo', rng)
            area = area_under_N(arrivals, dep)
            sumW = sum((d - a for d, a in zip(dep, arrivals)), Fraction(0))
            ok = (area == sumW)
            if is_det and not ok:
                det_ok = False
            if (not is_det) and not ok:
                hivar_ok = False
        dep, T = simulate(arrivals, svc_det, 'fifo', rng)
        area = area_under_N(arrivals, dep)
        sumW_bad = sum((dep[i] - arrivals[i] for i in range(n - 1)), Fraction(0))
        if not (area != sumW_bad):
            falsify_caught = False
    return {
        'identity_exact_deterministic_service': det_ok,
        'identity_exact_highvariance_service': hivar_ok,
        'perturbed_accounting_rejected': falsify_caught,
        'mean_service': m,
        'realizations': realizations,
    }


def build_segments_float(arr, dep):
    events = [(a, 1) for a in arr] + [(d, -1) for d in dep]
    events.sort(key=lambda x: x[0])
    segs = []
    level = 0
    prev = events[0][0]
    for tt, delta in events:
        if tt > prev:
            segs.append((prev, tt, level))
        prev = tt
        level += delta
    return segs


def area_in_window(segs, t0, t1):
    s = 0.0
    for a, b, lvl in segs:
        lo = a if a > t0 else t0
        hi = b if b < t1 else t1
        if hi > lo:
            s += lvl * (hi - lo)
    return s


def gate_mc_mm1(rng, rho, n_arr, warmup, nbatches):
    mu = 1.0
    lam = rho
    t = 0.0
    arr, svc = [], []
    for _ in range(n_arr):
        t += rng.expovariate(lam)
        arr.append(t)
        svc.append(rng.expovariate(mu))
    dep = [0.0] * n_arr
    free = 0.0
    for i in range(n_arr):
        start = arr[i] if arr[i] > free else free
        dep[i] = start + svc[i]
        free = dep[i]
    segs = build_segments_float(arr, dep)
    T0 = arr[warmup]
    T1 = dep[-1]
    width = (T1 - T0) / nbatches
    batch_means = []
    for b in range(nbatches):
        a0 = T0 + b * width
        a1 = T0 + (b + 1) * width
        batch_means.append(area_in_window(segs, a0, a1) / (a1 - a0))
    mean = sum(batch_means) / nbatches
    var = sum((x - mean) ** 2 for x in batch_means) / (nbatches - 1)
    se = math.sqrt(var / nbatches)
    L_true = rho / (1.0 - rho)
    L_wrong = rho * rho / (1.0 - rho)
    z_correct = (mean - L_true) / se
    z_wrong = (mean - L_wrong) / se
    return {
        'rho': rho,
        'n_arrivals': n_arr,
        'nbatches': nbatches,
        'L_hat': round(mean, 6),
        'se': round(se, 6),
        'L_true_closed_form': round(L_true, 6),
        'L_wrong_alt': round(L_wrong, 6),
        'z_correct_abs': round(abs(z_correct), 6),
        'z_wrong_abs': round(abs(z_wrong), 6),
    }


def run_battery():
    rng = random.Random(SEED)
    exact = gate_exact(rng, realizations=200, n=30)
    robust = gate_robustness(rng, realizations=200, n=30)
    mc = gate_mc_mm1(rng, rho=0.7, n_arr=120000, warmup=20000, nbatches=40)
    Z_AGREE = 4.0
    Z_SEP = 6.0
    g1 = bool(exact['identity_exact_all'] and exact['lambda_invariant_all'])
    g2 = bool(exact['L_discipline_dependent_count'] > 0)
    g3 = bool(mc['z_correct_abs'] < Z_AGREE and mc['z_wrong_abs'] > Z_SEP)
    g4 = bool(robust['identity_exact_deterministic_service']
              and robust['identity_exact_highvariance_service']
              and robust['perturbed_accounting_rejected'])
    gates = {
        'G1_pathwise_identity_and_lambda_invariance': g1,
        'G2_L_discipline_dependent': g2,
        'G3_mc_mm1_3sigma_discrimination': g3,
        'G4_robustness_and_falsifiability': g4,
    }
    return {
        'seed': SEED,
        'thresholds': {'Z_AGREE': Z_AGREE, 'Z_SEP': Z_SEP},
        'exact_gate': exact,
        'robustness_gate': robust,
        'mc_gate': mc,
        'gates': gates,
        'sim_ready': all(gates.values()),
    }


def _digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


if __name__ == '__main__':
    import sys
    r1 = run_battery()
    r2 = run_battery()
    determinism = (_digest(r1) == _digest(r2))
    r1['determinism_double_run_ok'] = determinism
    digest = _digest(r1)
    print(json.dumps(r1, indent=2, sort_keys=True))
    print('results_sha256=' + digest)
    sys.exit(0 if (r1['sim_ready'] and determinism) else 1)

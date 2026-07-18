#!/usr/bin/env python3
"""service-variance wait tax -- round-32 FLEET-slot verifier (PROPOSAL 137).

Phenomenon: for an M/G/1 FIFO queue the Pollaczek-Khinchine mean-value law gives
mean queue wait W_q = (rho / (1 - rho)) * E[S] * (1 + C^2) / 2, where
C^2 = Var(S) / E[S]^2 is the squared coefficient of variation of SERVICE time.
At FIXED utilization rho and FIXED mean service E[S], the wait depends ONLY on
service-time variance. Pinned world rho=0.8, E[S]=1.0 gives, exactly:
  Deterministic (M/D/1, C^2=0):   W_q = 2.0
  Exponential  (M/M/1, C^2=1):    W_q = 4.0
  Hyperexp     (M/H2/1, C^2=4):   W_q = 10.0
a 1 : 2 : 5 spread from variance alone -- invisible to any utilization dashboard.

Method: the exact single-server FIFO Lindley recursion W_{i+1}=max(0, W_i+S_i-T_i)
with T_i ~ Exp(lambda) interarrivals (lambda = rho / E[S] = 0.8) and S_i drawn from
the service distribution under test. Because Lindley waits are autocorrelated,
naive std/sqrt(n) is invalid; we use the METHOD OF INDEPENDENT REPLICATIONS: each
replication runs n_jobs jobs with a warm-up discard and contributes ONE sample
(its post-warmup mean W_q); replications get independent sub-seeds drawn from a
master random.Random(SEED) via getrandbits, so no stream is shared across reps.
z = (grand_mean - W_q_theory) / (std_across_reps / sqrt(R)); PASS iff |z| < 3.

Stdlib only. Deterministic under the pinned SEED; a double run is byte-identical.
"""
import hashlib
import json
import math
import random

SEED = 20260717
RHO = 0.8
MEAN_SERVICE = 1.0
LAMBDA = RHO / MEAN_SERVICE  # = 0.8
CV2_H2 = 4.0
N_JOBS = 600000
WARMUP = 150000
REPLICATIONS = 30
SUBSEED_BITS = 64
Z_GATE = 3.0


def wq_theory(cv2):
    """Pollaczek-Khinchine mean queue wait for M/G/1 at the pinned rho, E[S]."""
    return (RHO / (1.0 - RHO)) * MEAN_SERVICE * (1.0 + cv2) / 2.0


def h2_params(mean, cv2):
    """Balanced-means two-phase hyperexponential: return (p1, b1, b2).

    p1 = 0.5*(1 + sqrt((cv2-1)/(cv2+1))); branch means b1 = mean/(2*p1),
    b2 = mean/(2*p2). This yields overall mean == `mean` and C^2 == cv2 exactly.
    """
    p1 = 0.5 * (1.0 + math.sqrt((cv2 - 1.0) / (cv2 + 1.0)))
    p2 = 1.0 - p1
    b1 = mean / (2.0 * p1)
    b2 = mean / (2.0 * p2)
    return p1, b1, b2


_P1, _B1, _B2 = h2_params(MEAN_SERVICE, CV2_H2)


def service_D(rng):
    return MEAN_SERVICE


def service_M(rng):
    return rng.expovariate(1.0 / MEAN_SERVICE)


def service_H2(rng):
    if rng.random() < _P1:
        return rng.expovariate(1.0 / _B1)
    return rng.expovariate(1.0 / _B2)


def simulate_rep(rng, service_sampler, n_jobs, warmup):
    """One replication: exact Lindley recursion, return post-warmup mean W_q."""
    w = 0.0
    total = 0.0
    count = 0
    for i in range(n_jobs):
        if i >= warmup:
            total += w
            count += 1
        s = service_sampler(rng)
        t = rng.expovariate(LAMBDA)
        w = w + s - t
        if w < 0.0:
            w = 0.0
    return total / count


def run_dist(master, service_sampler, cv2):
    theory = wq_theory(cv2)
    samples = []
    for _ in range(REPLICATIONS):
        sub_seed = master.getrandbits(SUBSEED_BITS)
        rng = random.Random(sub_seed)
        samples.append(simulate_rep(rng, service_sampler, N_JOBS, WARMUP))
    grand_mean = sum(samples) / len(samples)
    var = sum((x - grand_mean) ** 2 for x in samples) / (len(samples) - 1)
    std = math.sqrt(var)
    se = std / math.sqrt(len(samples))
    z = (grand_mean - theory) / se if se > 0 else 0.0
    return {
        "cv2": cv2,
        "wq_theory": theory,
        "grand_mean": grand_mean,
        "std_across_reps": std,
        "se": se,
        "z": z,
        "pass": abs(z) < Z_GATE,
    }


def run():
    master = random.Random(SEED)
    # Order fixed D -> M -> H2 so sub-seed draws are deterministic.
    d = run_dist(master, service_D, 0.0)
    m = run_dist(master, service_M, 1.0)
    h2 = run_dist(master, service_H2, CV2_H2)

    per_dist = {"D": d, "M": m, "H2": h2}

    gates = {
        "G1_deterministic_MD1": {
            "dist": "D", "cv2": 0.0, "wq_theory": d["wq_theory"],
            "z": d["z"], "pass": d["pass"],
        },
        "G2_exponential_MM1": {
            "dist": "M", "cv2": 1.0, "wq_theory": m["wq_theory"],
            "z": m["z"], "pass": m["pass"],
        },
        "G3_hyperexponential_MH2_1": {
            "dist": "H2", "cv2": CV2_H2, "wq_theory": h2["wq_theory"],
            "z": h2["z"], "pass": h2["pass"],
        },
    }
    all_pass = d["pass"] and m["pass"] and h2["pass"]

    return {
        "mechanism": "service-variance-wait-tax",
        "config": {
            "seed": SEED,
            "rho": RHO,
            "mean_service": MEAN_SERVICE,
            "lambda": LAMBDA,
            "cv2_h2": CV2_H2,
            "n_jobs": N_JOBS,
            "warmup": WARMUP,
            "replications": REPLICATIONS,
            "subseed_bits": SUBSEED_BITS,
            "z_gate": Z_GATE,
        },
        "h2_params": {"p1": _P1, "branch_mean_1": _B1, "branch_mean_2": _B2},
        "theory": {"D": wq_theory(0.0), "M": wq_theory(1.0), "H2": wq_theory(CV2_H2)},
        "per_dist": per_dist,
        "gates": gates,
        "all_pass": all_pass,
    }


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

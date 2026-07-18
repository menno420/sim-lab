"""Cache stampede / request coalescing: caching a HOT key does not reduce its
worst-case origin recompute load -- it CONCENTRATES it into a herd, and the
herd grows LINEARLY with request rate.

Folk belief: a cache with a near-100% hit ratio protects the origin, and a
hotter key (higher request rate) is SAFER because it is almost always served
from cache -- so to tame origin load you raise the hit ratio / lengthen the TTL.

Reality (cache stampede / dogpile / thundering herd): when a hot key's cached
value expires it is stale for the length of one recompute T, and under a plain
TTL cache WITHOUT coordination EVERY request that arrives during that window
independently recomputes the same value at the origin. Model one expiry event
as a window [0, T): requests arrive as a Poisson process of rate lambda, so the
number that pile onto the origin is exactly Poisson(lambda*T) -- expected herd
E = lambda*T. (This is the Wikipedia cache-stampede example verbatim: 10 req/s
with a 3 s render => 30 processes recomputing the same page at once.) The herd
therefore SCALES with the request rate: doubling traffic doubles the per-expiry
origin burst even as the cache hit ratio climbs toward 100%. Request coalescing
(single-flight / dogpile lock) lets the FIRST request in the window recompute
and makes every other request wait on that in-flight result, collapsing the herd
to exactly 1 recompute per expiry (E = 1 - e^{-lambda*T}, ~1 for a hot key) --
INDEPENDENT of lambda. So the cure for a stampede is coalescing, not a longer
TTL (a longer TTL leaves the per-expiry herd size lambda*T untouched).

Pinned world: SEED = 20260717, one random.Random(SEED) drawn sequentially in
the fixed config order. T_RECOMPUTE = 1.0. SIGMA_GATE = 3.0.

Estimator: per replication (one expiry event) draw a Poisson process on [0, T)
by summing interarrival ~ Exp(lambda) until the clock passes T; the naive herd
is the count of arrivals in the window (exactly Poisson(lambda*T)); the coalesced
recompute count is 1 if the herd is >= 1 else 0. R independent replications; for
a config the reported statistic is the mean over replications, se =
sample-std / sqrt(R) -- an honest independent-replication standard error. z =
(mean - anchor) / se.

Gates (PASS iff ALL, in order CFG_LOW -> CFG_HIGH -> CFG_HEAD):
  1. CFG_LOW  verifier-correctness: naive herd matches exact Poisson mean
     lambda*T = 5 within |z| < 3.
  2. CFG_HIGH verifier-correctness: naive herd matches exact Poisson mean
     lambda*T = 30 within |z| < 3 -- the herd is Poisson(lambda*T) and SCALES
     with rate (6x the CFG_LOW herd for 6x the rate; the mechanism control that
     the folk "more caching -> less origin load" guess misses: a hotter key
     stampedes harder).
  3. CFG_HEAD counterintuitive headline (z >= 3): with request coalescing the
     paired amplification (naive_herd - coalesced_recomputes) per expiry sits
     z >= 3 ABOVE zero, i.e. coalescing removes ~lambda*T - 1 redundant origin
     recomputes per expiry (a ~30x -> 1x collapse) that a plain TTL cache never
     touches.

Stdlib only (random, json, hashlib, math). WHOLE-DICT / NO-SELF-FIELD /
STDOUT-ONLY: the results dict carries no results_sha256 key, the digest is the
sha256 of the compact canonical json.dumps(sort_keys=True,separators=(",",":"))
of the whole dict, every float rounded to 6 dp; the stdout DUMP is pretty
indent=2 (the P127+ twist) while the hashed payload is compact; no on-disk JSON.
"""

import hashlib
import json
import math
import random

SEED = 20260717
SIGMA_GATE = 3.0
T_RECOMPUTE = 1.0

# (name, request rate lambda, recompute time T, replications R, coalesced?)
CONFIGS = [
    ("CFG_LOW", 5.0, T_RECOMPUTE, 4000, False),
    ("CFG_HIGH", 30.0, T_RECOMPUTE, 4000, False),
    ("CFG_HEAD", 30.0, T_RECOMPUTE, 4000, True),
]


def simulate_replication(rng, lam, T):
    """One expiry event: draw a Poisson(lam) arrival process on [0, T) by summing
    interarrival ~ Exp(lam) until the clock passes T. Returns (naive_herd,
    coalesced_recomputes): naive = count of arrivals in the window (every request
    recomputes); coalesced = 1 if any arrival else 0 (single-flight collapses the
    herd to one recompute)."""
    t = 0.0
    herd = 0
    while True:
        t += rng.expovariate(lam)
        if t >= T:
            break
        herd += 1
    coalesced = 1 if herd >= 1 else 0
    return herd, coalesced


def mean_std(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, var ** 0.5


def run():
    rng = random.Random(SEED)
    configs_out = {}
    gates = []
    for name, lam, T, R, coalesce in CONFIGS:
        naive = []
        coalesced = []
        for _ in range(R):
            h, c = simulate_replication(rng, lam, T)
            naive.append(h)
            coalesced.append(c)
        poisson_mean = lam * T
        coalesced_mean_exact = 1.0 - math.exp(-lam * T)
        if coalesce:
            # head: paired amplification naive - coalesced per expiry, vs zero
            amp = [naive[i] - coalesced[i] for i in range(R)]
            m, sd = mean_std(amp)
            se = sd / (R ** 0.5)
            anchor = 0.0
            anchor_kind = "zero_amplification"
            z = (m - anchor) / se if se > 0 else 0.0
            passed = z >= SIGMA_GATE
            naive_m, _ = mean_std(naive)
            coal_m, _ = mean_std(coalesced)
            stat = m
            stat_kind = "mean_amplification(naive-coalesced)"
        else:
            m, sd = mean_std(naive)
            se = sd / (R ** 0.5)
            anchor = poisson_mean
            anchor_kind = "exact_poisson_mean_lambda*T"
            z = (m - anchor) / se if se > 0 else 0.0
            passed = abs(z) < SIGMA_GATE
            naive_m = m
            coal_m, _ = mean_std(coalesced)
            stat = m
            stat_kind = "mean_naive_herd"
        gates.append(passed)
        configs_out[name] = {
            "lambda": lam,
            "T_recompute": T,
            "replications": R,
            "coalesce": coalesce,
            "mean_naive_herd": round(naive_m, 6),
            "mean_coalesced_recomputes": round(coal_m, 6),
            "poisson_mean_lambda_T": round(poisson_mean, 6),
            "coalesced_mean_exact": round(coalesced_mean_exact, 6),
            "amplification_factor": round(naive_m / coal_m, 6) if coal_m > 0 else 0.0,
            "statistic": round(stat, 6),
            "statistic_kind": stat_kind,
            "anchor": round(anchor, 6),
            "anchor_kind": anchor_kind,
            "se": round(se, 6),
            "z": round(z, 6),
            "pass": passed,
        }
    first_fail = None
    for i, (name, _, _, _, _) in enumerate(CONFIGS):
        if not gates[i]:
            first_fail = name
            break
    return {
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "t_recompute": T_RECOMPUTE,
        "configs": configs_out,
        "all_gates_pass": all(gates),
        "first_failing_gate": first_fail,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    # in-process double-run determinism assertion
    results2 = run()
    payload2 = json.dumps(results2, sort_keys=True, separators=(",", ":"))
    digest2 = hashlib.sha256(payload2.encode()).hexdigest()
    assert digest == digest2, "non-deterministic: %s != %s" % (digest, digest2)

    for name, _, _, _, _ in CONFIGS:
        cfg = results["configs"][name]
        print("%-9s lam=%-4g herd=%.4f coalesced=%.4f anchor=%.4f (%s) z=%+.4f %s" % (
            name, cfg["lambda"], cfg["mean_naive_herd"], cfg["mean_coalesced_recomputes"],
            cfg["anchor"], cfg["anchor_kind"], cfg["z"],
            "PASS" if cfg["pass"] else "FAIL"))
    print("all_gates_pass =", results["all_gates_pass"])
    print("first_failing_gate =", results["first_failing_gate"])
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()

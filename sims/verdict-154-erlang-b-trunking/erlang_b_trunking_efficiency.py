"""Erlang-B trunking efficiency: fragmenting a loss-system fabric into small
independent pools at the SAME offered-load-per-server MULTIPLIES blocking.

Folk belief: blocking is a function of utilization, so two pools each at 80%
offered load block the same fraction as one big pool at 80% -- capacity is
additive, so splitting a fabric into per-tenant / per-shard pools at the same
utilization is free.

Reality: model each pool as an M/M/c/c loss system (Poisson arrivals rate
lambda, exponential service rate mu, c servers, NO queue, blocked-calls-cleared).
Offered load a = lambda/mu Erlangs. By PASTA the probability an arriving call is
blocked is the exact Erlang-B loss formula

    B(c, a) = (a^c / c!) / sum_{k=0..c} a^k / k!

computed by the stable recursion B(0,a)=1, B(k,a) = a*B(k-1,a) / (k + a*B(k-1,a)).

At a FIXED offered-load-per-server rho = a/c, B(c, c*rho) FALLS steeply as c
grows (trunking efficiency / economy of scale). At rho = 0.8:
B(2,1.6) ~= 0.330, B(10,8) ~= 0.122, B(100,80) ~= 0.004 -- same utilization,
~90x less blocking from 2 to 100 servers. So fragmenting one pooled 100-server
fabric into 50 independent 2-server pools at the same rho lifts the drop rate
from ~0.4% to ~33%.

Pinned world: SEED = 20260717, one random.Random(SEED) drawn sequentially in
the fixed config order. mu = 1.0. SIGMA_GATE = 3.0. rho = 0.8 for every config.

Estimator: event-driven M/M/c/c per replication (interarrival ~ Exp(lambda) then
service ~ Exp(mu), two draws/arrival in fixed order; a call is accepted if any
server's free-at time <= the clock, else blocked/cleared). R independent
replications; mc = mean of the per-replication blocking fractions; se =
sample-std / sqrt(R) -- an honest independent-replication standard error, so
within-replication autocorrelation is folded into the between-replication spread.
z = (mc - anchor) / se.

Gates (PASS iff ALL, in order CFG_SMALL -> CFG_MED -> CFG_HEAD):
  1. CFG_SMALL verifier-correctness: |z| < 3 vs exact B(2,1.6).
  2. CFG_MED  verifier-correctness: |z| < 3 vs exact B(10,8) (already far below
     CFG_SMALL at the identical rho -- the trunking gradient is real).
  3. CFG_HEAD counterintuitive headline: z = (mc - L)/se >= 3, i.e. a 2-server
     fragment blocks dozens of sigma ABOVE the pooled anchor L = exact B(100,80)
     (the folk "same-utilization -> same-blocking" guess understates loss ~90x).

Stdlib only (random, json, hashlib). WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.
"""

import hashlib
import json
import random

SEED = 20260717
SIGMA_GATE = 3.0
MU = 1.0

# pooled anchor: one big pool at the same offered-load-per-server (rho = 0.8)
POOL_C = 100
POOL_A = 80.0

# (name, servers c, offered load a Erlangs, replications R, arrivals/rep A, warmup W)
CONFIGS = [
    ("CFG_SMALL", 2, 1.6, 400, 8000, 1500),
    ("CFG_MED", 10, 8.0, 400, 8000, 1500),
    ("CFG_HEAD", 2, 1.6, 400, 8000, 1500),
]


def erlang_b(c, a):
    """Exact Erlang-B blocking probability via the stable recursion."""
    b = 1.0
    for k in range(1, c + 1):
        b = (a * b) / (k + a * b)
    return b


def simulate_replication(rng, c, a, arrivals, warmup):
    """Event-driven M/M/c/c loss system, one replication starting empty.
    Draws exactly two exponentials per arrival (interarrival, service) in fixed
    order for determinism. Returns the blocking fraction over post-warmup arrivals."""
    lam = a * MU
    free_at = [0.0] * c
    t = 0.0
    blocked = 0
    counted = 0
    for i in range(arrivals):
        t += rng.expovariate(lam)
        service = rng.expovariate(MU)
        idx = -1
        for j in range(c):
            if free_at[j] <= t:
                idx = j
                break
        accepted = idx != -1
        if accepted:
            free_at[idx] = t + service
        if i >= warmup:
            counted += 1
            if not accepted:
                blocked += 1
    return blocked / counted


def mean_std(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, var ** 0.5


def run():
    rng = random.Random(SEED)
    pooled_anchor = erlang_b(POOL_C, POOL_A)
    configs_out = {}
    gates = []
    for name, c, a, R, A, W in CONFIGS:
        fracs = [simulate_replication(rng, c, a, A, W) for _ in range(R)]
        m, sd = mean_std(fracs)
        se = sd / (R ** 0.5)
        if name == "CFG_HEAD":
            anchor = pooled_anchor
            anchor_kind = "pooled_exact_B(100,80)"
            z = (m - anchor) / se if se > 0 else 0.0
            passed = z >= SIGMA_GATE
        else:
            anchor = erlang_b(c, a)
            anchor_kind = "exact_B(%d,%s)" % (c, ("%g" % a))
            z = (m - anchor) / se if se > 0 else 0.0
            passed = abs(z) < SIGMA_GATE
        gates.append(passed)
        configs_out[name] = {
            "servers": c,
            "offered_load": a,
            "replications": R,
            "arrivals_per_rep": A,
            "warmup": W,
            "mc_blocking": round(m, 9),
            "anchor": round(anchor, 9),
            "anchor_kind": anchor_kind,
            "se": round(se, 9),
            "z": round(z, 6),
            "pass": passed,
        }
    return {
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "mu": MU,
        "offered_load_per_server": round(POOL_A / POOL_C, 9),
        "pooled_anchor_B_100_80": round(pooled_anchor, 9),
        "exact_B_2_1p6": round(erlang_b(2, 1.6), 9),
        "exact_B_10_8": round(erlang_b(10, 8.0), 9),
        "configs": configs_out,
        "all_gates_pass": all(gates),
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

    for name, _, _, _, _, _ in CONFIGS:
        cfg = results["configs"][name]
        print("%-10s c=%-3d a=%-4g mc=%.6f anchor=%.6f (%s) z=%+.3f %s" % (
            name, cfg["servers"], cfg["offered_load"], cfg["mc_blocking"],
            cfg["anchor"], cfg["anchor_kind"], cfg["z"],
            "PASS" if cfg["pass"] else "FAIL"))
    print("all_gates_pass =", results["all_gates_pass"])
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PROPOSAL 249 — PageRank / random-surfer stationary distribution on a fixed 4-node graph.

HEAD: On a FIXED directed graph of N=4 nodes with out-links

    0 -> {1, 2}     1 -> {2, 3}     2 -> {0}     3 -> {}  (DANGLING)

the PageRank random-surfer process with damping d = 1/2 and uniform teleport
1/N has an EXACT rational stationary distribution

    pi = (52/179, 40/179, 50/179, 37/179).

Fleet framing: a random-surfer token routing across a fleet of agents, where the
damping d is the "follow a link" probability and (1-d) is the restart/teleport
probability; the exact stationary attention/reputation share of each agent is the
closed-form left-eigenvector of the Google matrix.

GOOGLE MATRIX (row-stochastic). With A the adjacency, outdeg(i) the out-degree,
d = 1/2 and teleport term (1-d)/N = 1/8:
  * non-dangling row i: G[i][j] = d * (A[i][j] / outdeg(i)) + (1-d)/N
  * dangling row (outdeg 0): the link part is uniform, so G[i][j] = d*(1/N) +
    (1-d)/N = 1/N.
Every row sums to 1. The stationary vector pi is the exact rational left-
eigenvector: pi G = pi, sum(pi) = 1.

RANDOM-SURFER MARKOV CHAIN. Each step: with probability (1-d) TELEPORT to a
uniform-random node; else (probability d) FOLLOW a uniform-random out-link of the
current node; if the current node is DANGLING, follow degenerates to a uniform
teleport. This transition law reproduces G exactly.

Gate battery (SEED=20260717; each gate reads in its OWN direction):
  G1 EXACT (fractions.Fraction, zero tolerance): build G exactly; solve the linear
     system for pi exactly by Gaussian elimination over Fraction on (G^T - I) with
     the sum(pi)=1 constraint replacing one row; assert pi G = pi with ZERO
     residual on every entry and sum(pi) = 1 exactly (max residual = 0).
     Independently cross-check pi via the exact ADJUGATE / cofactor null-vector of
     (G^T - I) (a genuinely distinct route from Gaussian elimination, no reuse of
     the solve) and assert it equals the solved pi EXACTLY (0 mismatches). Exact
     power iteration from the uniform vector is run as a convergence corroboration
     (it approaches pi geometrically at rate |lambda_2| and matches pi to within a
     tiny rational epsilon; because lambda_2 != 0 an exact stochastic matrix never
     reaches its stationary vector in finitely many exact steps, so the two EXACT
     routes are the Gaussian solve and the adjugate null-vector).
  G2 MONTE-CARLO AGREEMENT (|z| < 3, batch means): run ONE long random-surfer
     chain, discard burn-in, then BATCH-MEANS — partition the post-burn-in
     occupancy into B batches, per-node batch means, se = stdev(batch means)/
     sqrt(B), z_node = (mean - pi_node)/se; assert max|z| < 3. Random-walk
     occupancy along a sample path is AUTOCORRELATED, so the iid binomial SE is
     dishonest (structurally too small) and batch means / thinning is required;
     the batch SE is honest because batches of size batch_size >> mixing time are
     ~decorrelated.
  G3 INVARIANCE / EQUIVARIANCE (own direction): apply a fixed non-trivial
     permutation sigma to the node labels, rebuild G and re-solve pi on the
     permuted graph EXACTLY, and assert it equals sigma(pi_original) exactly (0
     mismatches). A verifier that hard-codes node indices breaks this.
  G4 FALSIFIABILITY (own direction, SAME MC sample): the plausible-but-wrong naive
     hypothesis pi_naive proportional to IN-DEGREE. On the SAME batch-means sample,
     z against pi_naive must be LARGE (REJECT, max|z| > 6) while G2 shows the true
     pi is ACCEPTED (small |z|). In-degree share ignores that a link's weight is
     itself set by the linking node's PageRank and the damping/teleport structure.

Determinism posture: build_results() is a pure function of SEED and the fixed
module constants. A single random.Random(SEED) is seeded once and consumed in a
fixed order across the whole chain; the exact-Fraction kernel is deterministic
rational arithmetic. Every rational serializes via str(Fraction) as "num/den",
integer visit counts serialize as ints, and every z-value via a fixed f"{z:.4f}"
string, so no wall-clock / PID / unordered-set iteration enters the hashed
payload. main() builds the results twice in one process and asserts the canonical
JSON forms are byte-identical (in-process double-run guard), supports --selfcheck
(prints "SELFCHECK: byte-identical"), prints a human summary and
`results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717

# Fixed directed graph (N=4). Out-links; node 3 is dangling (no out-links).
N = 4
ADJ = {0: [1, 2], 1: [2, 3], 2: [0], 3: []}
D = Fraction(1, 2)          # damping = follow-a-link probability
D_FLOAT = 0.5               # same value for the Monte-Carlo chain

Z_ACCEPT = 3.0              # G2 agreement band
Z_REJECT = 6.0             # G4 rejection threshold for the naive alternative

# Monte-Carlo batch-means configuration.
BURN_IN = 50_000
N_BATCHES = 200
BATCH_SIZE = 20_000
POWER_ITERS_CAP = 400
EPS = Fraction(1, 10 ** 18)  # rational convergence tolerance for power iteration


def zfmt(z):
    """Fixed z-score format so the serialization is invocation-stable."""
    return f"{float(z):.4f}"


def build_google_matrix(adj, n, d):
    """Exact row-stochastic Google matrix over fractions.Fraction."""
    teleport = (Fraction(1) - d) / n
    G = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        outs = adj[i]
        if not outs:                       # dangling row -> uniform
            for j in range(n):
                G[i][j] = Fraction(1, n)
        else:
            k = len(outs)
            for j in range(n):
                link = Fraction(1, k) if j in outs else Fraction(0)
                G[i][j] = d * link + teleport
    return G


def solve_stationary(G, n):
    """Exact left-eigenvector pi with pi G = pi, sum(pi)=1 (Gaussian elimination).

    Build M = (G^T - I) (so M x = 0 has x = pi^T in its null space), replace the
    last row with the all-ones normalization row and the rhs with 1, and solve the
    n x n system exactly over Fraction."""
    M = [[G[j][i] - (Fraction(1) if i == j else Fraction(0)) for j in range(n)]
         for i in range(n)]
    b = [Fraction(0)] * n
    M[n - 1] = [Fraction(1)] * n
    b[n - 1] = Fraction(1)
    for col in range(n):
        pivot = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[pivot] = M[pivot], M[col]
        b[col], b[pivot] = b[pivot], b[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        b[col] = b[col] / pv
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * c for a, c in zip(M[r], M[col])]
                b[r] = b[r] - f * b[col]
    return b


def _det(m):
    """Exact determinant by cofactor expansion (small matrices)."""
    k = len(m)
    if k == 1:
        return m[0][0]
    if k == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    total = Fraction(0)
    for c in range(k):
        minor = [[m[r][cc] for cc in range(k) if cc != c] for r in range(1, k)]
        total += ((-1) ** c) * m[0][c] * _det(minor)
    return total


def stationary_via_adjugate(G, n):
    """Exact pi via the adjugate null-vector of M0 = (G^T - I), a route independent
    of Gaussian elimination. Since M0 has rank n-1, any nonzero column of adj(M0)
    lies in the null space; normalize it to sum 1."""
    M0 = [[G[j][i] - (Fraction(1) if i == j else Fraction(0)) for j in range(n)]
          for i in range(n)]

    def cofactor(i, j):
        minor = [[M0[r][c] for c in range(n) if c != j]
                 for r in range(n) if r != i]
        return ((-1) ** (i + j)) * _det(minor)

    # column 0 of adj(M0): adj[i][0] = cofactor(0, i)
    col = [cofactor(0, i) for i in range(n)]
    s = sum(col)
    return [c / s for c in col]


def power_iteration(G, n, pi, cap, eps):
    """Corroboration: iterate v <- v G in exact Fraction from the uniform vector
    until consecutive iterates differ by < eps on every entry (or cap). Return the
    iteration count, whether it converged, and whether the limit matches pi within
    eps on every entry."""
    v = [Fraction(1, n)] * n
    iters = 0
    converged = False
    for t in range(1, cap + 1):
        nv = [sum(v[i] * G[i][j] for i in range(n)) for j in range(n)]
        delta = max(abs(nv[k] - v[k]) for k in range(n))
        v = nv
        iters = t
        if delta < eps:
            converged = True
            break
    matches = all(abs(v[k] - pi[k]) < eps for k in range(n))
    return iters, converged, matches


def surf_step(node, rng):
    """One random-surfer transition. With prob (1-d) teleport uniformly, else
    follow a uniform out-link; a dangling node follows to a uniform teleport."""
    if rng.random() < (1.0 - D_FLOAT):
        return rng.randrange(N)
    outs = ADJ[node]
    if not outs:
        return rng.randrange(N)
    return outs[rng.randrange(len(outs))]


def run_chain(rng):
    """One long random-surfer chain. Discard BURN_IN steps, then record occupancy
    over N_BATCHES batches of BATCH_SIZE steps each. Return (batch_means, counts):
    batch_means[b][k] is the fraction of batch b spent at node k; counts[k] is the
    total post-burn-in visits to node k (an integer, byte-stable)."""
    node = 0
    for _ in range(BURN_IN):
        node = surf_step(node, rng)
    batch_means = [[0.0] * N for _ in range(N_BATCHES)]
    counts = [0] * N
    for b in range(N_BATCHES):
        c = [0] * N
        for _ in range(BATCH_SIZE):
            node = surf_step(node, rng)
            c[node] += 1
        for k in range(N):
            batch_means[b][k] = c[k] / BATCH_SIZE
            counts[k] += c[k]
    return batch_means, counts


def batch_z(batch_means, target):
    """Per-node batch-means z against a target vector: se = stdev(batch means)/
    sqrt(B); z = (grand mean - target)/se. Returns list of (mean, z)."""
    B = len(batch_means)
    out = []
    for k in range(N):
        bm = [batch_means[b][k] for b in range(B)]
        m = sum(bm) / B
        var = sum((x - m) ** 2 for x in bm) / (B - 1)
        se = math.sqrt(var / B)
        out.append((m, (m - float(target[k])) / se))
    return out


def in_degrees(adj, n):
    deg = [0] * n
    for i in range(n):
        for j in adj[i]:
            deg[j] += 1
    return deg


def build_results():
    rng = random.Random(SEED)  # seeded once; consumed in a fixed order below

    results = {
        "proposal": 249,
        "claim": (
            "PageRank random-surfer stationary distribution on the fixed 4-node "
            "directed graph 0->{1,2}, 1->{2,3}, 2->{0}, 3->{} (dangling) with "
            "damping d=1/2 and uniform teleport 1/N is exactly "
            "pi=(52/179,40/179,50/179,37/179)."
        ),
        "seed": SEED,
        "n_nodes": N,
        "damping": f"{D.numerator}/{D.denominator}",
        "adjacency": {str(i): ADJ[i] for i in range(N)},
        "z_accept": zfmt(Z_ACCEPT),
        "z_reject": zfmt(Z_REJECT),
        "burn_in": BURN_IN,
        "n_batches": N_BATCHES,
        "batch_size": BATCH_SIZE,
    }

    # --- G1 EXACT: build G, solve pi, zero residual, adjugate cross-check -------
    G = build_google_matrix(ADJ, N, D)
    row_sums_ok = all(sum(G[i]) == Fraction(1) for i in range(N))
    pi = solve_stationary(G, N)

    # residual pi G - pi on every entry (must be exactly 0), and sum(pi)=1
    residual_entries = []
    max_residual_zero = True
    for j in range(N):
        col_dot = sum(pi[i] * G[i][j] for i in range(N))
        r = col_dot - pi[j]
        residual_entries.append(r)
        if r != 0:
            max_residual_zero = False
    sum_one = (sum(pi) == Fraction(1))

    # independent exact cross-check via the adjugate null-vector
    pi_adj = stationary_via_adjugate(G, N)
    adj_mismatches = sum(1 for k in range(N) if pi_adj[k] != pi[k])

    # power-iteration convergence corroboration (not an exact route)
    pi_iters, pi_converged, pi_matches = power_iteration(
        G, N, pi, POWER_ITERS_CAP, EPS)

    g1_pass = (row_sums_ok and max_residual_zero and sum_one
               and adj_mismatches == 0 and pi_converged and pi_matches)
    results["G1_exact"] = {
        "google_matrix": [[f"{G[i][j].numerator}/{G[i][j].denominator}"
                           for j in range(N)] for i in range(N)],
        "row_sums_ok": row_sums_ok,
        "pi": [f"{p.numerator}/{p.denominator}" for p in pi],
        "pi_float": [f"{float(p):.10f}" for p in pi],
        "max_residual": "0" if max_residual_zero else "nonzero",
        "sum_is_one": sum_one,
        "z": None,
        "z_note": "exact",
        "adjugate_pi": [f"{p.numerator}/{p.denominator}" for p in pi_adj],
        "adjugate_mismatches": adj_mismatches,
        "power_iteration": {
            "iters": pi_iters,
            "eps": "1e-18",
            "converged": pi_converged,
            "matches_pi_within_eps": pi_matches,
            "note": "corroboration; exact stochastic matrix never reaches pi in "
                    "finitely many exact steps (lambda_2 != 0)",
        },
        "pass": g1_pass,
    }

    # --- G2 MONTE-CARLO batch-means agreement (|z| < 3) -------------------------
    batch_means, counts = run_chain(rng)
    pi_float = [float(p) for p in pi]
    z_true = batch_z(batch_means, pi_float)
    max_abs_z_true = max(abs(z_true[k][1]) for k in range(N))
    g2_pass = max_abs_z_true < Z_ACCEPT
    results["G2_mc_agreement"] = {
        "visit_counts": counts,
        "total_steps": N_BATCHES * BATCH_SIZE,
        "method": "batch_means",
        "per_node": [
            {"node": k, "mean_hat": f"{z_true[k][0]:.6f}",
             "pi": f"{pi_float[k]:.6f}", "z": zfmt(z_true[k][1])}
            for k in range(N)
        ],
        "max_abs_z": zfmt(max_abs_z_true),
        "autocorrelated_needs_batch_means": True,
        "pass": g2_pass,
    }

    # --- G3 INVARIANCE / EQUIVARIANCE under a node relabel ----------------------
    # fixed non-trivial permutation sigma: old node i -> new label PERM[i]
    PERM = [2, 0, 3, 1]
    adj_perm = {PERM[i]: [PERM[j] for j in ADJ[i]] for i in range(N)}
    G_perm = build_google_matrix(adj_perm, N, D)
    pi_perm = solve_stationary(G_perm, N)
    # equivariance: pi_perm[PERM[i]] must equal pi[i] exactly
    sigma_pi = [None] * N
    for i in range(N):
        sigma_pi[PERM[i]] = pi[i]
    relabel_mismatches = sum(1 for k in range(N) if pi_perm[k] != sigma_pi[k])
    g3_pass = (relabel_mismatches == 0)
    results["G3_equivariance"] = {
        "permutation": PERM,
        "pi_permuted": [f"{p.numerator}/{p.denominator}" for p in pi_perm],
        "sigma_of_pi": [f"{p.numerator}/{p.denominator}" for p in sigma_pi],
        "relabel_mismatches": relabel_mismatches,
        "pass": g3_pass,
    }

    # --- G4 FALSIFIABILITY: reject naive in-degree hypothesis on SAME sample ----
    indeg = in_degrees(ADJ, N)
    tot = sum(indeg)
    pi_naive = [Fraction(indeg[k], tot) for k in range(N)]
    pi_naive_float = [float(p) for p in pi_naive]
    z_naive = batch_z(batch_means, pi_naive_float)
    max_abs_z_naive = max(abs(z_naive[k][1]) for k in range(N))
    g4_pass = max_abs_z_naive > Z_REJECT
    results["G4_falsifiability"] = {
        "naive_claim": "pi proportional to in-degree",
        "in_degrees": indeg,
        "pi_naive": [f"{p.numerator}/{p.denominator}" for p in pi_naive],
        "per_node_z_naive": [
            {"node": k, "pi_naive": f"{pi_naive_float[k]:.6f}",
             "z": zfmt(z_naive[k][1])} for k in range(N)
        ],
        "max_abs_z_naive": zfmt(max_abs_z_naive),
        "rejected": g4_pass,
        "same_sample_agrees_true_pi": g2_pass,
        "pass": g4_pass,
    }

    gates = {
        "G1": results["G1_exact"]["pass"],
        "G2": results["G2_mc_agreement"]["pass"],
        "G3": results["G3_equivariance"]["pass"],
        "G4": results["G4_falsifiability"]["pass"],
    }
    order = ["G1", "G2", "G3", "G4"]
    results["gates"] = gates
    results["first_failing_gate"] = next((k for k in order if not gates[k]), None)
    results["all_pass"] = all(gates[k] for k in order)
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def compute_digest():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    identical = (c1 == c2)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    return r1, c1, identical, digest


def main():
    selfcheck = "--selfcheck" in sys.argv[1:]
    r1, c1, identical, digest = compute_digest()
    if not identical:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)

    if selfcheck:
        print("SELFCHECK: byte-identical")
        print(f"results_sha256={digest}")
        sys.exit(0 if r1["all_pass"] else 1)

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for key in ["G1", "G2", "G3", "G4"]:
        print(f"{key}: {'PASS' if r1['gates'][key] else 'FAIL'}")
    print()
    print(f"in_process_double_run: {'IDENTICAL' if identical else 'DIVERGED'}")
    print(f"all_pass: {r1['all_pass']}")
    print(f"first_failing_gate: {r1['first_failing_gate']}")
    print(f"results_sha256={digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()

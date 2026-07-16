#!/usr/bin/env python3
"""VERDICT-099 - Series read-through concentrate-vs-spread saturation crossover.

Source proposal (header cited verbatim):
  ## PROPOSAL 086 * 2026-07-16T17:48:11Z * status: sim-ready
  idea-engine ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md
PROPOSAL<->VERDICT offset = +13 (PROPOSAL 086 -> VERDICT 099), confirmed at
sim-lab docs/current-state.md, Verdict-numbering map.

Pinned world (reproduced exactly from P086):
  Series: N=4 books -> 3 read-through transitions r_1,r_2,r_3. Book 1 is always
    bought by every entry-cohort reader.
  Entry cohort C=2000 readers per seed. Seeds S=[1,2,3,4,5] (in-file reporting
    constants; SEEDLESS - no seed-ledger draw).
  Royalty 1 unit/book; Revenue(seed,B,mode) = total books bought across the cohort.
  Base read-through r_base=0.30; ceiling (STABILITY BOUND) r_max=0.85 (strictly <1;
    realized read-through clamps here); slope=0.05.
  Quality->read-through map (linear up to the cap): r_k = min(r_max, r_base+slope*b_k).
    A single step saturates at b = (r_max-r_base)/slope = (0.85-0.30)/0.05 = 11 units.
  Allocations at budget B: CONCENTRATE bs=(B,0,0); SPREAD bs=(B/3,B/3,B/3).
  Budget grid B in {6,11,16,22,33}.
  COMMON RANDOM NUMBERS (critical - else NULL): per seed, draw each reader's three
    uniforms (u1,u2,u3) ONCE via rng=random.Random(seed) then
    [(rng.random(),rng.random(),rng.random()) for _ in range(C)]. REUSE that same
    uniform matrix for BOTH allocations AND across ALL B. A reader advances transition
    k iff u_k < r_k(mode,B); books are cumulative (book2 iff adv1; book3 iff adv1 AND
    adv2; book4 iff adv1 AND adv2 AND adv3 - stop at first failure).

Pre-registered gates (ACCEPT iff ALL hold; rule fires R1->R2->R3->R4; else REJECT at
first failing gate):
  R1 reach regime:       at B=6, per-seed rev_CONC > rev_SPREAD for ALL 5 seeds, AND
                         paired margin_sigma (diffs = CONC-SPREAD) >= 3.
  R2 saturation reversal: at B=33, per-seed rev_SPREAD > rev_CONC for ALL 5 seeds, AND
                         paired margin_sigma (diffs = SPREAD-CONC) >= 3.
  R3 well-posedness:     every realized r_k across all modes/B in [0.30, 0.85], AND
                         mean_rev monotone non-decreasing in B for BOTH allocations.
  R4 crossover at ceiling: B* = smallest grid B with mean_rev[SPREAD][B] >=
                         mean_rev[CONC][B]; require B* in (11, 22], AND CONCENTRATE
                         mean_rev FLAT (all equal) across B in {11,16,22,33}.
  paired margin_sigma = mean(d) / (sample_std(d, ddof=1)/sqrt(5)) (the paired
    t-statistic; std==0 guarded).
Determinism: byte-identical results.json across a double run; seed-1 B=6 first-50-reader
  (u1,u2,u3) draws + books under BOTH allocations committed as the fixture and
  re-verified each run.
"""
import json
import hashlib
import math
import os
import random

N_BOOKS = 4
N_TRANS = 3
C = 2000
SEEDS = [1, 2, 3, 4, 5]
R_BASE = 0.30
R_MAX = 0.85
SLOPE = 0.05
BUDGETS = [6, 11, 16, 22, 33]
MODES = ["CONCENTRATE", "SPREAD"]
HERE = os.path.dirname(os.path.abspath(__file__))


def alloc(mode, B):
    """Per-transition budget vector b = (b_1, b_2, b_3) for an allocation at budget B."""
    if mode == "CONCENTRATE":
        return (float(B), 0.0, 0.0)
    if mode == "SPREAD":
        return (B / 3.0, B / 3.0, B / 3.0)
    raise SystemExit("unknown mode: %s" % mode)


def rates(mode, B):
    """Realized read-through vector r = (r_1, r_2, r_3), each clamped at r_max."""
    b1, b2, b3 = alloc(mode, B)
    return (
        min(R_MAX, R_BASE + SLOPE * b1),
        min(R_MAX, R_BASE + SLOPE * b2),
        min(R_MAX, R_BASE + SLOPE * b3),
    )


def books(rs, u):
    """Cumulative books bought by one reader with rates rs on draws u (stop at first fail)."""
    r1, r2, r3 = rs
    u1, u2, u3 = u
    b = 1
    if u1 < r1:
        b += 1
        if u2 < r2:
            b += 1
            if u3 < r3:
                b += 1
    return b


def draw_matrix(seed):
    """The per-seed common-random-numbers uniform matrix (drawn ONCE per seed)."""
    rng = random.Random(seed)
    return [(rng.random(), rng.random(), rng.random()) for _ in range(C)]


def matrix_fp(mat):
    """Deterministic fingerprint of a uniform matrix (NULL-guard identity check)."""
    h = hashlib.sha256()
    for u1, u2, u3 in mat:
        h.update(repr((u1, u2, u3)).encode())
    return h.hexdigest()


def revenue(mat, mode, B):
    """Cohort-total books for one allocation on the shared matrix; returns (total, fp).

    fp is the fingerprint of the matrix this evaluation actually iterated - compared
    across allocations to prove CONCENTRATE and SPREAD saw the identical draws.
    """
    rs = rates(mode, B)
    total = 0
    h = hashlib.sha256()
    for u in mat:
        total += books(rs, u)
        h.update(repr(u).encode())
    return total, h.hexdigest()


def sample_std(xs):
    """Sample standard deviation, ddof=1."""
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) * (x - m) for x in xs) / (n - 1)
    return math.sqrt(var)


def margin_sigma(diffs):
    """Paired t-statistic: mean(d) / (sample_std(d, ddof=1)/sqrt(n)). std==0 guarded."""
    n = len(diffs)
    m = sum(diffs) / n
    sd = sample_std(diffs)
    sem = sd / math.sqrt(n)
    if sem == 0.0:
        return (float("inf") if m > 0 else 0.0), sd, sem
    return m / sem, sd, sem


def mean(xs):
    return sum(xs) / len(xs)


def simulate():
    """Run the full seed x budget x allocation grid under common random numbers.

    Returns (table, per_seed_rev, seed_fps) where:
      table[mode][B]      = mean revenue over seeds
      per_seed_rev[mode][B] = list of per-seed cohort-total revenues (seed order = SEEDS)
      seed_fps            = per-seed matrix fingerprint (for the NULL guard report)
    """
    per_seed_rev = {m: {B: [] for B in BUDGETS} for m in MODES}
    seed_fps = {}
    null_guard_ok = True
    for seed in SEEDS:
        mat = draw_matrix(seed)
        seed_fp = matrix_fp(mat)
        seed_fps[seed] = seed_fp
        for B in BUDGETS:
            rev_conc, fp_conc = revenue(mat, "CONCENTRATE", B)
            rev_spread, fp_spread = revenue(mat, "SPREAD", B)
            # NULL guard: both allocations MUST have iterated the identical matrix.
            if not (fp_conc == fp_spread == seed_fp):
                null_guard_ok = False
            per_seed_rev["CONCENTRATE"][B].append(rev_conc)
            per_seed_rev["SPREAD"][B].append(rev_spread)
    if not null_guard_ok:
        raise SystemExit("NULL: allocations saw different draws")
    table = {m: {B: mean(per_seed_rev[m][B]) for B in BUDGETS} for m in MODES}
    return table, per_seed_rev, seed_fps


def compute_gates(table, per_seed_rev):
    # ---- R1: reach regime at B=6 (CONC > SPREAD) ----
    c6 = per_seed_rev["CONCENTRATE"][6]
    s6 = per_seed_rev["SPREAD"][6]
    d1 = [c - s for c, s in zip(c6, s6)]
    r1_all_pos = all(d > 0 for d in d1)
    m1, sd1, sem1 = margin_sigma(d1)
    r1 = r1_all_pos and m1 >= 3.0

    # ---- R2: saturation reversal at B=33 (SPREAD > CONC) ----
    c33 = per_seed_rev["CONCENTRATE"][33]
    s33 = per_seed_rev["SPREAD"][33]
    d2 = [s - c for s, c in zip(s33, c33)]
    r2_all_pos = all(d > 0 for d in d2)
    m2, sd2, sem2 = margin_sigma(d2)
    r2 = r2_all_pos and m2 >= 3.0

    # ---- R3: well-posedness (rate range + monotone non-decreasing mean_rev) ----
    all_rates_in_range = True
    for m in MODES:
        for B in BUDGETS:
            for rk in rates(m, B):
                if not (R_BASE - 1e-12 <= rk <= R_MAX + 1e-12):
                    all_rates_in_range = False
    mono = {}
    for m in MODES:
        seq = [table[m][B] for B in BUDGETS]
        mono[m] = all(seq[i + 1] >= seq[i] for i in range(len(seq) - 1))
    r3 = all_rates_in_range and mono["CONCENTRATE"] and mono["SPREAD"]

    # ---- R4: crossover located at the entry-step ceiling ----
    b_star = None
    for B in BUDGETS:
        if table["SPREAD"][B] >= table["CONCENTRATE"][B]:
            b_star = B
            break
    b_star_in_window = (b_star is not None) and (11 < b_star <= 22)
    conc_flat_region = [11, 16, 22, 33]
    conc_flat_vals = [table["CONCENTRATE"][B] for B in conc_flat_region]
    conc_flat = all(v == conc_flat_vals[0] for v in conc_flat_vals)
    r4 = b_star_in_window and conc_flat

    gates = {
        "R1": r1, "R2": r2, "R3": r3, "R4": r4,
        "R1_all_seeds_positive": r1_all_pos, "R1_margin_sigma": m1,
        "R1_diffs": d1, "R1_std": sd1, "R1_sem": sem1,
        "R2_all_seeds_positive": r2_all_pos, "R2_margin_sigma": m2,
        "R2_diffs": d2, "R2_std": sd2, "R2_sem": sem2,
        "R3_rates_in_range": all_rates_in_range,
        "R3_monotone_concentrate": mono["CONCENTRATE"],
        "R3_monotone_spread": mono["SPREAD"],
        "R4_b_star": b_star, "R4_b_star_in_window": b_star_in_window,
        "R4_concentrate_flat": conc_flat,
        "R4_concentrate_flat_values": conc_flat_vals,
    }
    return gates


def decide_ifchain(gr):
    """Evaluator A: ordered short-circuit if-chain; first failing gate is the reason."""
    if not gr["R1"]:
        return "REJECT", "R1"
    if not gr["R2"]:
        return "REJECT", "R2"
    if not gr["R3"]:
        return "REJECT", "R3"
    if not gr["R4"]:
        return "REJECT", "R4"
    return "ACCEPT", None


def decide_table(gr):
    """Evaluator B: independent transcription over the ordered gate list."""
    order = [("R1", gr["R1"]), ("R2", gr["R2"]), ("R3", gr["R3"]), ("R4", gr["R4"])]
    reason = None
    verdict = "ACCEPT"
    for name, ok in order:
        if not ok and reason is None:
            reason = name
            verdict = "REJECT"
    return verdict, reason


def canon(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def realized_rate_table():
    return {m: {str(B): list(rates(m, B)) for B in BUDGETS} for m in MODES}


def main():
    L = []

    def out(s=""):
        L.append(s)

    table, per_seed_rev, seed_fps = simulate()
    gr = compute_gates(table, per_seed_rev)
    vA, rA = decide_ifchain(gr)
    vB, rB = decide_table(gr)

    # ---- fixture (seed-1, B=6, first-50-reader draws + books under both allocations) ----
    fx_path = os.path.join(HERE, "fixtures.json")
    mat1 = draw_matrix(1)
    rs_conc6 = rates("CONCENTRATE", 6)
    rs_spread6 = rates("SPREAD", 6)
    first50 = []
    for u in mat1[:50]:
        first50.append({
            "u": [u[0], u[1], u[2]],
            "books_concentrate": books(rs_conc6, u),
            "books_spread": books(rs_spread6, u),
        })
    fixture = {
        "source": "sim-lab/sims/verdict-099-series-readthrough-saturation-crossover",
        "proposal": "## PROPOSAL 086 * 2026-07-16T17:48:11Z * status: sim-ready "
                    "(idea-engine ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md); "
                    "offset +13 -> VERDICT 099",
        "pinned_world": {
            "N_books": N_BOOKS, "N_transitions": N_TRANS, "C": C, "seeds": SEEDS,
            "r_base": R_BASE, "r_max": R_MAX, "slope": SLOPE, "budgets": BUDGETS,
            "allocations": {
                "CONCENTRATE": "bs=(B,0,0)",
                "SPREAD": "bs=(B/3,B/3,B/3)",
            },
            "rate_map": "r_k = min(r_max, r_base + slope*b_k); step saturates at b=(r_max-r_base)/slope=11",
            "common_random_numbers": "per seed draw (u1,u2,u3) once per reader via random.Random(seed); "
                                     "REUSE that matrix for BOTH allocations AND all B; a reader advances "
                                     "transition k iff u_k < r_k; books cumulative, stop at first failure",
        },
        "preregistered_gates": {
            "R1": "B=6: rev_CONC > rev_SPREAD all 5 seeds AND paired margin_sigma(CONC-SPREAD) >= 3",
            "R2": "B=33: rev_SPREAD > rev_CONC all 5 seeds AND paired margin_sigma(SPREAD-CONC) >= 3",
            "R3": "every realized r_k in [0.30,0.85] AND mean_rev monotone non-decreasing in B for BOTH allocations",
            "R4": "B* (smallest grid B with mean_rev[SPREAD]>=mean_rev[CONC]) in (11,22] AND CONCENTRATE mean_rev flat over B in {11,16,22,33}",
            "margin_sigma": "mean(d) / (sample_std(d, ddof=1)/sqrt(5)) (paired t-statistic; std==0 guarded)",
            "decision_rule": "ACCEPT iff R1 and R2 and R3 and R4; else REJECT at first failing gate; rule fires R1->R2->R3->R4",
        },
        "seed1_B6_first50_rates": {"CONCENTRATE": list(rs_conc6), "SPREAD": list(rs_spread6)},
        "seed1_B6_first50_readers": first50,
    }
    if os.path.exists(fx_path):
        with open(fx_path) as f:
            committed = json.load(f)
        fixture_ok = (
            committed.get("seed1_B6_first50_readers") == fixture["seed1_B6_first50_readers"]
            and committed.get("seed1_B6_first50_rates") == fixture["seed1_B6_first50_rates"]
        )
    else:
        with open(fx_path, "w") as f:
            f.write(canon(fixture) + "\n")
        fixture_ok = True

    # ---- self-checks ----
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    chk("fixture_matches_committed", fixture_ok)
    chk("twin_evaluators_agree_verdict", vA == vB)
    chk("twin_evaluators_agree_reason", rA == rB)
    chk("common_random_numbers_shared_per_seed", len(set(seed_fps.values())) == len(SEEDS) and all(seed_fps.values()))
    chk("realized_rates_within_stability_bound", gr["R3_rates_in_range"])
    chk("cohort_size_is_C", all(len(draw_matrix(s)) == C for s in [1]))
    chk("budget_grid_straddles_saturation", (min(BUDGETS) < 11) and (max(BUDGETS) > 11))

    # ---- human-readable log ----
    out("VERDICT-099 - Series read-through concentrate-vs-spread saturation crossover (P086)")
    out("=" * 82)
    out("")
    out("Pinned world: N=%d books -> %d transitions; C=%d readers/seed; seeds S=%s" % (
        N_BOOKS, N_TRANS, C, SEEDS))
    out("  r_base=%.2f  r_max=%.2f (stability bound)  slope=%.2f  =>  step saturates at b=%d" % (
        R_BASE, R_MAX, SLOPE, int((R_MAX - R_BASE) / SLOPE)))
    out("  CONCENTRATE bs=(B,0,0)   SPREAD bs=(B/3,B/3,B/3)   grid B in %s" % BUDGETS)
    out("  Common random numbers: one per-reader uniform matrix per seed, shared by BOTH allocations and ALL B.")
    out("")
    out("Mean revenue over seeds S=%s (total books bought across the C=%d cohort):" % (SEEDS, C))
    out("")
    hdr = "%-6s | %-12s %-12s | %-12s" % ("B", "CONCENTRATE", "SPREAD", "SPREAD-CONC")
    out(hdr)
    out("-" * len(hdr))
    for B in BUDGETS:
        cc = table["CONCENTRATE"][B]
        ss = table["SPREAD"][B]
        out("%-6d | %-12.2f %-12.2f | %-+12.2f" % (B, cc, ss, ss - cc))
    out("")
    out("Per-seed revenues (seed order S=%s):" % SEEDS)
    for B in BUDGETS:
        out("  B=%-3d CONC   %s" % (B, per_seed_rev["CONCENTRATE"][B]))
        out("  B=%-3d SPREAD %s" % (B, per_seed_rev["SPREAD"][B]))
    out("")
    out("Realized read-through r_k = min(r_max, r_base+slope*b_k):")
    for m in MODES:
        for B in BUDGETS:
            rs = rates(m, B)
            out("  %-11s B=%-3d  r=(%.4f, %.4f, %.4f)" % (m, B, rs[0], rs[1], rs[2]))
    out("")
    out("Gate outcomes (pre-registered, fire in order R1->R2->R3->R4):")
    out("  R1 reach regime @B=6      : %s   (all-5-seeds CONC>SPREAD %s, margin %.2f sigma, need >=3)" % (
        "PASS" if gr["R1"] else "FAIL", gr["R1_all_seeds_positive"], gr["R1_margin_sigma"]))
    out("      diffs CONC-SPREAD = %s" % gr["R1_diffs"])
    out("  R2 saturation reversal@B=33: %s   (all-5-seeds SPREAD>CONC %s, margin %.2f sigma, need >=3)" % (
        "PASS" if gr["R2"] else "FAIL", gr["R2_all_seeds_positive"], gr["R2_margin_sigma"]))
    out("      diffs SPREAD-CONC = %s" % gr["R2_diffs"])
    out("  R3 well-posedness         : %s   (rates_in_range %s, mono CONC %s, mono SPREAD %s)" % (
        "PASS" if gr["R3"] else "FAIL", gr["R3_rates_in_range"],
        gr["R3_monotone_concentrate"], gr["R3_monotone_spread"]))
    out("  R4 crossover @ ceiling    : %s   (B*=%s in (11,22] %s, CONC flat over {11,16,22,33} %s)" % (
        "PASS" if gr["R4"] else "FAIL", gr["R4_b_star"], gr["R4_b_star_in_window"],
        gr["R4_concentrate_flat"]))
    out("      CONCENTRATE flat values {11,16,22,33} = %s" % gr["R4_concentrate_flat_values"])
    out("")
    out("Twin evaluators: A(if-chain)=%s/%s  B(table)=%s/%s" % (vA, rA, vB, rB))
    out("")
    n_pass = sum(1 for _, c in checks if c)
    for name, c in checks:
        out("  [%s] %s" % ("ok" if c else "XX", name))
    out("Self-checks: %d/%d passed" % (n_pass, len(checks)))
    out("")
    out("VERDICT: %s%s" % (vA, ("" if rA is None else " (first failing gate: %s)" % rA)))

    results = {
        "verdict": vA,
        "first_failing_gate": rA,
        "gates": gr,
        "mean_revenue": {m: {str(B): table[m][B] for B in BUDGETS} for m in MODES},
        "per_seed_revenue": {m: {str(B): per_seed_rev[m][B] for B in BUDGETS} for m in MODES},
        "realized_rates": realized_rate_table(),
        "b_star": gr["R4_b_star"],
        "twin": {"if_chain": [vA, rA], "table": [vB, rB], "agree": vA == vB and rA == rB},
        "self_checks": {name: c for name, c in checks},
        "seed_matrix_fingerprints": seed_fps,
        "params": {
            "N_books": N_BOOKS, "N_transitions": N_TRANS, "C": C, "seeds": SEEDS,
            "r_base": R_BASE, "r_max": R_MAX, "slope": SLOPE, "budgets": BUDGETS,
        },
    }
    res_path = os.path.join(HERE, "results.json")
    canonical = canon(results)
    with open(res_path, "w") as f:
        f.write(canonical + "\n")
    stdout_text = "\n".join(L) + "\n"
    with open(os.path.join(HERE, "run-stdout.txt"), "w") as f:
        f.write(stdout_text)
    res_sha = hashlib.sha256((canonical + "\n").encode()).hexdigest()
    std_sha = hashlib.sha256(stdout_text.encode()).hexdigest()
    print(stdout_text, end="")
    print("results.json sha256 : " + res_sha)
    print("run-stdout.txt sha256: " + std_sha)
    if n_pass != len(checks):
        raise SystemExit("SELF-CHECK FAILURE: %d/%d" % (n_pass, len(checks)))


if __name__ == "__main__":
    main()

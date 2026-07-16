#!/usr/bin/env python3
"""VERDICT-100 - Hits-to-kill breakpoint variance comb (TIGHT vs WILD).

Source proposal (header cited verbatim):
  ## PROPOSAL 087 * 2026-07-16T18:59:26Z * status: sim-ready
  idea-engine PROPOSAL 087 (bundle-pwyw-floor-lattice numbering slot;
  registered spec: htk-breakpoint-variance-comb)
PROPOSAL<->VERDICT offset = +13 (PROPOSAL 087 -> VERDICT 100), confirmed at
sim-lab docs/current-state.md, Verdict-numbering map.

Pinned world (reproduced exactly from the registered P087 spec):
  Single target with HP H; dies when cumulative realized damage >= H. HTK =
    number of hits to reach H (floor HTK >= 1).
  Two equal-cost builds, differ ONLY in per-hit damage distribution:
    TIGHT ~ Uniform[100, 110]  (mean 105, min 100)
    WILD  ~ Uniform[ 75, 165]  (mean 120, min 75, max 165)
  Cohort C=4000 trials per seed. Seeds S=[1,2,3,4,5] (fresh trials per seed).
  HP grid H in {80, 100, 140, 300, 500}.
  Metric: mean HTK (lower = better). Paired diff per seed
    d_s(H) = meanHTK_WILD - meanHTK_TIGHT (positive => TIGHT wins).
    mean_d(H) = mean over 5 seeds; sigma(H) = stdev(d_s, ddof=1)/sqrt(5);
    margin(H) = |mean_d| / sigma.
  COMMON RANDOM NUMBERS (critical - else NULL): for each trial draw a single
    stream of MAX_HITS>=25 base uniforms u_i in [0,1) from ONE random.Random(seed).
    BOTH builds consume the SAME u_i sequence, each mapping u_i to its own [lo,hi]:
    damage = lo + u_i*(hi-lo). Identical per-(trial,hit) uniforms across builds
    (the paired/CRN construction). Draw trials in order; the same seed's stream is
    reused across the H grid - re-seed random.Random(seed) fresh at the start of
    each (seed) cohort so the SAME trials are evaluated at every H (CRN across H too).

Pre-registered gates (ACCEPT iff R1 AND R2 AND R3 AND R4, evaluated in order
R1->R2->R3->R4; REJECT at the first failing gate):
  R1 (H=100): mean HTK TIGHT < WILD for ALL 5 seeds, AND margin(100) >= 3sigma.
  R2 (H=500): mean HTK WILD < TIGHT for ALL 5 seeds, AND margin(500) >= 3sigma.
  R3: every realized HTK >= 1, AND mean HTK monotone non-decreasing in H for BOTH
      builds across the H grid.
  R4a: sign of mean_d(H) over H in [80,100,140,300,500] equals [+, +, -, +, -].
  R4b: deterministic control HTK = ceil(H/mean) with TIGHT mean=105, WILD mean=120
       has WILD <= TIGHT at every H (removes variance; shows the stochastic TIGHT
       wins are variance-driven, not mean-driven).
  (R4 PASS iff R4a AND R4b.)
Determinism: fully hermetic (no network/repo reads, no wall-clock). results.json
  and run-stdout.txt are byte-identical across a double run; the seed-1 H=100
  first-20-trial HTK under BOTH builds on identical draws is committed as the
  fixture and re-verified each run.
"""
import json
import hashlib
import math
import os
import random

# ---- pinned-world constants (top-of-file, per the registration) ----
C = 4000
SEEDS = [1, 2, 3, 4, 5]
H_GRID = [80, 100, 140, 300, 500]
TIGHT_LO, TIGHT_HI = 100.0, 110.0
WILD_LO, WILD_HI = 75.0, 165.0
MEAN_TIGHT = 105.0
MEAN_WILD = 120.0
MAX_HITS = 25
BUILDS = ["TIGHT", "WILD"]
BOUNDS = {"TIGHT": (TIGHT_LO, TIGHT_HI), "WILD": (WILD_LO, WILD_HI)}
EXPECTED_COMB_SIGNS = ["+", "+", "-", "+", "-"]
HERE = os.path.dirname(os.path.abspath(__file__))


def htk(us, lo, hi, H):
    """Hits-to-kill for one trial: smallest n with cumulative damage >= H.

    Each hit deals damage = lo + u_i*(hi-lo) on the shared uniform stream us.
    Floor HTK >= 1 (the first hit always deals positive damage, so a target with
    H>0 always takes at least one hit). Raises if MAX_HITS cannot reach H.
    """
    cum = 0.0
    for i, u in enumerate(us):
        cum += lo + u * (hi - lo)
        if cum >= H:
            return i + 1
    raise SystemExit("MAX_HITS=%d too small to reach H=%d" % (MAX_HITS, H))


def draw_matrix(seed):
    """Per-seed common-random-numbers uniform matrix (drawn ONCE per seed).

    C trials, each a stream of MAX_HITS uniforms from ONE random.Random(seed).
    Re-seeding fresh per seed makes the SAME C trials evaluable at every H (CRN
    across the H grid) and shareable by BOTH builds (CRN across builds).
    """
    rng = random.Random(seed)
    return [[rng.random() for _ in range(MAX_HITS)] for _ in range(C)]


def matrix_fp(mat):
    """Deterministic fingerprint of a uniform matrix (NULL-guard identity check)."""
    h = hashlib.sha256()
    for us in mat:
        h.update(repr(tuple(us)).encode())
    return h.hexdigest()


def cohort_htk(mat, build, H):
    """Per-trial HTK for one build on the shared matrix; returns (htks, fp).

    fp fingerprints the FULL matrix this evaluation iterated (every trial's full
    uniform row), compared across builds to prove TIGHT and WILD saw the identical
    draws - the CRN NULL guard. HTK itself early-stops at the kill, but the
    fingerprint hashes the whole row so a divergent matrix would be caught.
    """
    lo, hi = BOUNDS[build]
    htks = []
    h = hashlib.sha256()
    for us in mat:
        h.update(repr(tuple(us)).encode())
        htks.append(htk(us, lo, hi, H))
    return htks, h.hexdigest()


def mean(xs):
    return sum(xs) / len(xs)


def sample_std(xs):
    """Sample standard deviation, ddof=1."""
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) * (x - m) for x in xs) / (n - 1)
    return math.sqrt(var)


def margin_stats(d):
    """Return (mean_d, sigma, margin) with sigma = sample_std(d,ddof=1)/sqrt(n).

    margin = |mean_d| / sigma (sigma==0 guarded: inf if mean_d!=0 else 0).
    """
    n = len(d)
    md = sum(d) / n
    sd = sample_std(d)
    sigma = sd / math.sqrt(n)
    if sigma == 0.0:
        return md, sigma, (float("inf") if md != 0 else 0.0)
    return md, sigma, abs(md) / sigma


def sign_of(x):
    return "+" if x > 0 else ("-" if x < 0 else "0")


def simulate():
    """Run the full seed x H x build grid under common random numbers.

    Returns (per_seed, seed_fps, min_htk, crn_ok) where:
      per_seed[build][H] = list of per-seed mean HTK (seed order = SEEDS)
      seed_fps           = per-seed matrix fingerprint (for the NULL guard report)
      min_htk            = smallest realized HTK across every evaluation (R3 floor)
      crn_ok             = both builds fingerprinted the identical per-seed matrix
    """
    per_seed = {b: {H: [] for H in H_GRID} for b in BUILDS}
    seed_fps = {}
    min_htk = None
    crn_ok = True
    for seed in SEEDS:
        mat = draw_matrix(seed)
        seed_fp = matrix_fp(mat)
        seed_fps[seed] = seed_fp
        for H in H_GRID:
            for b in BUILDS:
                htks, fp = cohort_htk(mat, b, H)
                # NULL guard: this build MUST have iterated the identical matrix.
                if fp != seed_fp:
                    crn_ok = False
                lo_htk = min(htks)
                min_htk = lo_htk if min_htk is None else min(min_htk, lo_htk)
                per_seed[b][H].append(mean(htks))
    if not crn_ok:
        raise SystemExit("NULL: builds saw different draws")
    return per_seed, seed_fps, min_htk, crn_ok


def control_htk(H, m):
    """Deterministic (variance-free) control HTK = ceil(H/mean)."""
    return int(math.ceil(H / m))


def compute_gates(per_seed, min_htk):
    build_mean = {b: {H: mean(per_seed[b][H]) for H in H_GRID} for b in BUILDS}

    # per-H paired-diff statistics: d_s = meanHTK_WILD - meanHTK_TIGHT
    per_H = {}
    for H in H_GRID:
        t = per_seed["TIGHT"][H]
        w = per_seed["WILD"][H]
        d = [ww - tt for ww, tt in zip(w, t)]
        md, sigma, marg = margin_stats(d)
        per_H[H] = {
            "d": d, "mean_d": md, "sigma": sigma, "margin": marg,
            "sign": sign_of(md),
            "tight_lt_wild_all": all(tt < ww for tt, ww in zip(t, w)),
            "wild_lt_tight_all": all(ww < tt for ww, tt in zip(w, t)),
        }

    # ---- R1: reach regime @H=100 (TIGHT < WILD all seeds; margin >= 3) ----
    r1_all = per_H[100]["tight_lt_wild_all"]
    r1_margin = per_H[100]["margin"]
    r1 = r1_all and r1_margin >= 3.0

    # ---- R2: saturation reversal @H=500 (WILD < TIGHT all seeds; margin >= 3) ----
    r2_all = per_H[500]["wild_lt_tight_all"]
    r2_margin = per_H[500]["margin"]
    r2 = r2_all and r2_margin >= 3.0

    # ---- R3: floor + monotone non-decreasing mean HTK in H for BOTH builds ----
    htk_floor_ok = (min_htk is not None) and (min_htk >= 1)
    mono = {}
    for b in BUILDS:
        seq = [build_mean[b][H] for H in H_GRID]
        mono[b] = all(seq[i + 1] >= seq[i] - 1e-12 for i in range(len(seq) - 1))
    r3 = htk_floor_ok and mono["TIGHT"] and mono["WILD"]

    # ---- R4a: comb sign vector matches the registered [+,+,-,+,-] ----
    comb_signs = [per_H[H]["sign"] for H in H_GRID]
    r4a = comb_signs == EXPECTED_COMB_SIGNS

    # ---- R4b: deterministic control WILD <= TIGHT at every H ----
    control = {}
    r4b = True
    for H in H_GRID:
        t_ctrl = control_htk(H, MEAN_TIGHT)
        w_ctrl = control_htk(H, MEAN_WILD)
        control[H] = {"tight": t_ctrl, "wild": w_ctrl, "wild_le_tight": w_ctrl <= t_ctrl}
        if not (w_ctrl <= t_ctrl):
            r4b = False
    r4 = r4a and r4b

    gates = {
        "R1": r1, "R2": r2, "R3": r3, "R4": r4,
        "R1_tight_lt_wild_all_seeds": r1_all, "R1_margin": r1_margin,
        "R1_diffs": per_H[100]["d"], "R1_mean_d": per_H[100]["mean_d"],
        "R1_sigma": per_H[100]["sigma"],
        "R2_wild_lt_tight_all_seeds": r2_all, "R2_margin": r2_margin,
        "R2_diffs": per_H[500]["d"], "R2_mean_d": per_H[500]["mean_d"],
        "R2_sigma": per_H[500]["sigma"],
        "R3_htk_floor_ok": htk_floor_ok, "R3_min_htk": min_htk,
        "R3_monotone_tight": mono["TIGHT"], "R3_monotone_wild": mono["WILD"],
        "R4a_comb_signs": comb_signs, "R4a_expected": EXPECTED_COMB_SIGNS,
        "R4a_signs_match": r4a,
        "R4b_control": {str(H): control[H] for H in H_GRID}, "R4b_ok": r4b,
    }
    return gates, build_mean, per_H, control


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


def build_fixture():
    """Seed-1, H=100, first-20-trial HTK under BOTH builds on identical draws."""
    mat1 = draw_matrix(1)
    first20 = mat1[:20]
    htk_tight = [htk(us, TIGHT_LO, TIGHT_HI, 100) for us in first20]
    htk_wild = [htk(us, WILD_LO, WILD_HI, 100) for us in first20]
    return {
        "source": "sim-lab/sims/verdict-100-htk-breakpoint-variance-comb",
        "proposal": "## PROPOSAL 087 * 2026-07-16T18:59:26Z * status: sim-ready "
                    "(idea-engine PROPOSAL 087, registered spec htk-breakpoint-variance-comb); "
                    "offset +13 -> VERDICT 100",
        "pinned_world": {
            "C": C, "seeds": SEEDS, "H_grid": H_GRID,
            "TIGHT": {"lo": TIGHT_LO, "hi": TIGHT_HI, "mean": MEAN_TIGHT, "min": TIGHT_LO},
            "WILD": {"lo": WILD_LO, "hi": WILD_HI, "mean": MEAN_WILD,
                     "min": WILD_LO, "max": WILD_HI},
            "MAX_HITS": MAX_HITS,
            "metric": "mean HTK (lower = better); HTK = smallest n with cumulative "
                      "damage >= H, floor >= 1",
            "damage_map": "damage = lo + u_i*(hi-lo); BOTH builds map the SAME u_i to "
                          "their own [lo,hi]",
            "common_random_numbers": "per trial draw MAX_HITS>=25 uniforms once via "
                                     "random.Random(seed); BOTH builds consume the SAME "
                                     "u_i stream; re-seed fresh per seed so the SAME "
                                     "trials are evaluated at every H (CRN across H and builds)",
            "paired_diff": "d_s(H) = meanHTK_WILD - meanHTK_TIGHT (positive => TIGHT wins); "
                           "mean_d = mean over 5 seeds; sigma = stdev(d_s,ddof=1)/sqrt(5); "
                           "margin = |mean_d|/sigma",
        },
        "preregistered_gates": {
            "R1": "H=100: mean HTK TIGHT < WILD all 5 seeds AND margin(100) >= 3sigma",
            "R2": "H=500: mean HTK WILD < TIGHT all 5 seeds AND margin(500) >= 3sigma",
            "R3": "every realized HTK >= 1 AND mean HTK monotone non-decreasing in H for BOTH builds",
            "R4a": "sign of mean_d(H) over H in [80,100,140,300,500] equals [+,+,-,+,-]",
            "R4b": "deterministic control HTK = ceil(H/mean) (TIGHT mean=105, WILD mean=120) "
                   "has WILD <= TIGHT at every H",
            "decision_rule": "ACCEPT iff R1 and R2 and R3 and R4 (R4 = R4a and R4b); "
                             "else REJECT at first failing gate; rule fires R1->R2->R3->R4",
        },
        "seed1_H100_first20_uniforms": first20,
        "seed1_H100_first20_htk_tight": htk_tight,
        "seed1_H100_first20_htk_wild": htk_wild,
    }


def main():
    L = []

    def out(s=""):
        L.append(s)

    per_seed, seed_fps, min_htk, crn_ok = simulate()
    gr, build_mean, per_H, control = compute_gates(per_seed, min_htk)
    vA, rA = decide_ifchain(gr)
    vB, rB = decide_table(gr)

    # ---- fixture (write on first run, else verify committed) ----
    fx_path = os.path.join(HERE, "fixtures.json")
    fixture = build_fixture()
    if os.path.exists(fx_path):
        with open(fx_path) as f:
            committed = json.load(f)
        fixture_ok = (
            committed.get("seed1_H100_first20_htk_tight") == fixture["seed1_H100_first20_htk_tight"]
            and committed.get("seed1_H100_first20_htk_wild") == fixture["seed1_H100_first20_htk_wild"]
            and committed.get("seed1_H100_first20_uniforms") == fixture["seed1_H100_first20_uniforms"]
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
    chk("common_random_numbers_shared_per_build_and_H", crn_ok)
    chk("per_seed_matrices_distinct", len(set(seed_fps.values())) == len(SEEDS) and all(seed_fps.values()))
    chk("every_realized_htk_ge_1", gr["R3_htk_floor_ok"])
    chk("cohort_size_is_C", all(len(draw_matrix(s)) == C for s in [1]))
    chk("hp_grid_spans_reversal", min(H_GRID) <= 100 and max(H_GRID) >= 500)

    # ---- human-readable log ----
    out("VERDICT-100 - Hits-to-kill breakpoint variance comb: TIGHT vs WILD (P087)")
    out("=" * 82)
    out("")
    out("Pinned world: single target HP H; HTK = hits to reach cumulative damage >= H (floor 1).")
    out("  TIGHT ~ Uniform[%g,%g] (mean %g)   WILD ~ Uniform[%g,%g] (mean %g)" % (
        TIGHT_LO, TIGHT_HI, MEAN_TIGHT, WILD_LO, WILD_HI, MEAN_WILD))
    out("  C=%d trials/seed; seeds S=%s; H grid=%s; MAX_HITS=%d" % (C, SEEDS, H_GRID, MAX_HITS))
    out("  Common random numbers: one per-trial uniform stream per seed, shared by BOTH builds and ALL H.")
    out("  Metric: mean HTK (lower = better). d_s(H)=meanHTK_WILD-meanHTK_TIGHT (positive => TIGHT wins).")
    out("")
    out("Mean HTK over seeds S=%s (lower is better):" % SEEDS)
    out("")
    hdr = "%-6s | %-12s %-12s | %-12s %-8s %-10s" % (
        "H", "TIGHT", "WILD", "mean_d(W-T)", "sign", "margin")
    out(hdr)
    out("-" * len(hdr))
    for H in H_GRID:
        tt = build_mean["TIGHT"][H]
        ww = build_mean["WILD"][H]
        p = per_H[H]
        out("%-6d | %-12.4f %-12.4f | %-+12.4f %-8s %-10.2f" % (
            H, tt, ww, p["mean_d"], p["sign"], p["margin"]))
    out("")
    out("Per-seed mean HTK (seed order S=%s):" % SEEDS)
    for H in H_GRID:
        out("  H=%-3d TIGHT  %s" % (H, ["%.4f" % x for x in per_seed["TIGHT"][H]]))
        out("  H=%-3d WILD   %s" % (H, ["%.4f" % x for x in per_seed["WILD"][H]]))
    out("")
    out("Deterministic control HTK = ceil(H/mean) (variance removed):")
    out("  %-6s | %-8s %-8s %-12s" % ("H", "TIGHT", "WILD", "WILD<=TIGHT"))
    for H in H_GRID:
        c = control[H]
        out("  %-6d | %-8d %-8d %-12s" % (H, c["tight"], c["wild"], c["wild_le_tight"]))
    out("")
    out("Gate outcomes (pre-registered, fire in order R1->R2->R3->R4):")
    out("  R1 reach regime @H=100    : %s   (TIGHT<WILD all 5 seeds %s, margin %.2f sigma, need >=3)" % (
        "PASS" if gr["R1"] else "FAIL", gr["R1_tight_lt_wild_all_seeds"], gr["R1_margin"]))
    out("      diffs WILD-TIGHT = %s" % ["%+.4f" % d for d in gr["R1_diffs"]])
    out("  R2 saturation reversal@H=500: %s   (WILD<TIGHT all 5 seeds %s, margin %.2f sigma, need >=3)" % (
        "PASS" if gr["R2"] else "FAIL", gr["R2_wild_lt_tight_all_seeds"], gr["R2_margin"]))
    out("      diffs WILD-TIGHT = %s" % ["%+.4f" % d for d in gr["R2_diffs"]])
    out("  R3 well-posedness         : %s   (min HTK=%s>=1 %s, mono TIGHT %s, mono WILD %s)" % (
        "PASS" if gr["R3"] else "FAIL", gr["R3_min_htk"], gr["R3_htk_floor_ok"],
        gr["R3_monotone_tight"], gr["R3_monotone_wild"]))
    out("  R4 comb + control         : %s   (R4a signs %s == %s %s, R4b control WILD<=TIGHT all H %s)" % (
        "PASS" if gr["R4"] else "FAIL", gr["R4a_comb_signs"], gr["R4a_expected"],
        gr["R4a_signs_match"], gr["R4b_ok"]))
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
        "mean_htk": {b: {str(H): build_mean[b][H] for H in H_GRID} for b in BUILDS},
        "per_seed_mean_htk": {b: {str(H): per_seed[b][H] for H in H_GRID} for b in BUILDS},
        "paired_diff": {
            str(H): {
                "d": per_H[H]["d"], "mean_d": per_H[H]["mean_d"],
                "sigma": per_H[H]["sigma"], "margin": per_H[H]["margin"],
                "sign": per_H[H]["sign"],
            } for H in H_GRID
        },
        "comb_signs": gr["R4a_comb_signs"],
        "deterministic_control": {str(H): control[H] for H in H_GRID},
        "twin": {"if_chain": [vA, rA], "table": [vB, rB], "agree": vA == vB and rA == rB},
        "self_checks": {name: c for name, c in checks},
        "seed_matrix_fingerprints": seed_fps,
        "params": {
            "C": C, "seeds": SEEDS, "H_grid": H_GRID,
            "TIGHT_lo": TIGHT_LO, "TIGHT_hi": TIGHT_HI, "MEAN_TIGHT": MEAN_TIGHT,
            "WILD_lo": WILD_LO, "WILD_hi": WILD_HI, "MEAN_WILD": MEAN_WILD,
            "MAX_HITS": MAX_HITS,
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
    # exit 0: twin evaluators agree AND the pre-registered rule was applied honestly.
    if not (vA == vB and rA == rB):
        raise SystemExit("TWIN DISAGREEMENT: %s/%s vs %s/%s" % (vA, rA, vB, rB))


if __name__ == "__main__":
    main()

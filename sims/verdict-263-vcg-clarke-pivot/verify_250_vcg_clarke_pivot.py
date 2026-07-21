#!/usr/bin/env python3
"""PROPOSAL 250 — Vickrey-Clarke-Groves (Clarke-pivot) mechanism, multi-unit single-demand.

HEAD: k identical units are auctioned to n bidders who each want AT MOST ONE
unit, with valuations v_1 >= v_2 >= ... >= v_n. Then

  1. the efficient allocation gives the k units to the k highest-value bidders;
  2. the VCG / Clarke-pivot payment of each winner = the EXTERNALITY it imposes
     on the others = W_{-i}(efficient allocation WITHOUT agent i) minus
     W_{-i}(efficient allocation WITH agent i), and this equals, for EVERY
     winner, the SAME uniform price = the (k+1)-th highest valuation = the
     highest LOSING bid;
  3. truthful reporting is a dominant strategy (a winner's payment is
     independent of its own report as long as it stays a winner);
  4. the expected revenue is k * E[V_{(k+1):n}] (k times the expected
     (k+1)-th highest order statistic).

FIXED HEADLINE INSTANCE (n=5, k=2, v=(10,8,6,4,2)): the efficient allocation
gives units to the bidders valued 10 and 8; the uniform Clarke price is the
3rd-highest valuation = 6; revenue = k*price = 12. The pivot for the 10-bidder
is 14-8=6 (others' best without it, {8,6,4,2} top-2 = 14, minus others' welfare
with it, 8); for the 8-bidder it is 16-10=6 (others without it {10,6,4,2} top-2
= 16, minus others' welfare with it, 10). Both winners pay the SAME price 6.

DISTINCTNESS: this is the MULTI-UNIT generalization of the single-item Vickrey
second-price auction. The pivot price is the (k+1)-th highest order statistic
(not the 2nd), and the content is the externality-payment identity. At k=1 it
recovers single-item second-price exactly (price = 2nd highest).

Gate battery (SEED=20260717; each gate reads in its OWN direction):
  G1 EXACT (fractions.Fraction, zero tolerance): on the fixed instance (and a
     tie instance, k=1, and k=3) compute the efficient allocation and each
     winner's Clarke-pivot payment EXACTLY as the externality
     W_{-i}(without i) - W_{-i}(with i). Assert (a) each winner's payment equals
     that externality exactly, and (b) all winners pay the SAME price equal to
     the (k+1)-th highest valuation. Record 0 mismatches. The externality route
     and the closed-form (k+1)-th-order-statistic route are independent; their
     exact agreement is the teeth.
  G2 MONTE-CARLO AGREEMENT (|z| < 3): draw N iid profiles of n=5 values iid
     Discrete-Uniform{1..6}, k=2, revenue per profile = 2*(3rd highest). The
     exact target E[revenue] = k*E[V_{(k+1):n}] is computed EXACTLY by full
     enumeration of all 6^5 profiles with Fraction (bulletproof; no order-
     statistic formula). z = (sample_mean - exact_mean)/(sample_std/sqrt(N));
     require |z| < 3. iid profiles are NOT autocorrelated, so the plain iid SE
     is honest here -- do NOT batch-mean/thin (that is only for autocorrelated
     sample-path estimators like queues / Markov chains). The whole sample sum
     and sum-of-squares are accumulated in EXACT integer arithmetic (revenue is
     an integer), so sample_mean and sample_var are exact rationals and only the
     final sqrt/division touch float, keeping the hashed payload byte-stable.
  G3 INVARIANCE (exact, 0 mismatches): (a) a winner's payment is INVARIANT to
     its own reported value across the whole winning range -- vary a winner's
     bid over every value that keeps it a winner and assert the payment is
     unchanged (the DSIC / strategyproofness core); (b) relabelling: apply a
     permutation to the agents and assert the allocation and payment vector
     permute accordingly (outcome equivariance). Both exact via Fraction.
  G4 FALSIFIABILITY (reject at large |z|, Z_REJECT=6.0): the pre-registered
     naive foil "the uniform price is the lowest WINNING bid" (the k-th highest
     = 2nd-highest for k=2), i.e. predicted E[revenue] = k*E[V_{(k):n}] (exact
     enumerated). On the SAME G2 sample of TRUE revenue,
     z_foil = (sample_mean_true - exact_mean_foil)/(sample_std/sqrt(N)) must
     satisfy |z_foil| > 6 (it lands in the hundreds). This is the classic
     multi-unit-auction confusion: charge the highest LOSING bid (correct) vs
     the lowest WINNING bid (wrong).

Determinism posture: build_results() is a pure function of SEED and the fixed
module constants. A single random.Random(SEED) is seeded once and consumed in a
fixed order for the MC gate; the exact-Fraction kernel is deterministic rational
arithmetic. Every rational serializes via str(Fraction) as "num/den", integer
counts serialize as ints, and every z-value via a fixed f"{z:.4f}" string, so no
wall-clock / PID / unordered-set iteration enters the hashed payload. main()
builds the results twice in one process and asserts the canonical JSON forms are
byte-identical (in-process double-run guard), supports --selfcheck (prints
"SELFCHECK: byte-identical"), prints a human summary and
`results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717

Z_ACCEPT = 3.0              # G2 agreement band
Z_REJECT = 6.0             # G4 rejection threshold for the naive foil

# Fixed headline instance.
K = 2
VALUATIONS = (10, 8, 6, 4, 2)

# Monte-Carlo configuration (iid profiles; NOT autocorrelated -> no batching).
MC_N = 200_000
FACE = 6                    # Discrete-Uniform{1..6}
MC_N_BIDDERS = 5
MC_K = 2


def zfmt(z):
    """Fixed z-score format so the serialization is invocation-stable."""
    return f"{float(z):.4f}"


def frac(p):
    """Serialize a Fraction (or int) as 'num/den'."""
    p = Fraction(p)
    return f"{p.numerator}/{p.denominator}"


# --------------------------------------------------------------------------- #
# Core mechanism (exact; agents are (agent_id, value) pairs).                  #
# --------------------------------------------------------------------------- #

def sort_desc(agents):
    """Deterministic descending order by (-value, agent_id) -- ties broken by
    the LOWER agent_id winning."""
    return sorted(agents, key=lambda a: (-a[1], a[0]))


def welfare_topk(values, k):
    """Exact efficient welfare: sum of the top-k values (all, if fewer than k)."""
    s = sorted(values, reverse=True)
    return sum(s[:k], Fraction(0))


def efficient_winners(agents, k):
    """Winner agent_ids: the k highest-value bidders (deterministic tie-break)."""
    return [a[0] for a in sort_desc(agents)[:k]]


def clarke_payments(agents, k):
    """Exact Clarke-pivot payment for each winner, computed as the externality
    W_{-i}(without i) - W_{-i}(with i). Returns (winners, payments, detail) where
    payments maps winner agent_id -> Fraction, and detail maps agent_id ->
    (W_without, W_with_others)."""
    all_values = [a[1] for a in agents]
    W = welfare_topk(all_values, k)                      # total efficient welfare
    winners = set(efficient_winners(agents, k))
    payments = {}
    detail = {}
    for (aid, val) in agents:
        if aid in winners:
            others = [a[1] for a in agents if a[0] != aid]
            w_without = welfare_topk(others, k)          # others' best WITHOUT i
            w_with_others = W - val                      # others' welfare WITH i
            payments[aid] = w_without - w_with_others    # the externality
            detail[aid] = (w_without, w_with_others)
    return winners, payments, detail


def kth_highest(values, j):
    """The j-th highest value (1-indexed): sorted-descending[j-1]."""
    return sorted(values, reverse=True)[j - 1]


# --------------------------------------------------------------------------- #
# G1 -- exact identity on fixed instances.                                     #
# --------------------------------------------------------------------------- #

def run_instance(values, k):
    """Run the mechanism on a tuple of integer valuations (agent_id = position)
    and return a fully-serialized record plus a mismatch count. mismatches counts
    winners whose externality payment differs from the (k+1)-th highest value."""
    agents = [(i, Fraction(v)) for i, v in enumerate(values)]
    winners, payments, detail = clarke_payments(agents, k)
    n = len(values)
    # closed-form uniform price = (k+1)-th highest valuation (highest losing bid);
    # if there is no (k+1)-th bidder the price is 0 (no losing bid to charge).
    price = kth_highest(list(values), k + 1) if n >= k + 1 else 0
    price = Fraction(price)

    winner_ids = sorted(winners)
    mismatches = 0
    per_winner = []
    for aid in winner_ids:
        pay = payments[aid]
        w_without, w_with_others = detail[aid]
        agrees = (pay == price)
        if not agrees:
            mismatches += 1
        per_winner.append({
            "agent_id": aid,
            "value": frac(agents[aid][1]),
            "W_without_i": frac(w_without),
            "W_with_i_others": frac(w_with_others),
            "externality_payment": frac(pay),
            "equals_uniform_price": agrees,
        })
    revenue = sum((payments[a] for a in winner_ids), Fraction(0))
    all_same_price = all(payments[a] == price for a in winner_ids)
    return {
        "valuations": list(values),
        "k": k,
        "winner_ids": winner_ids,
        "winner_values": [int(values[a]) for a in winner_ids],
        "uniform_price": frac(price),
        "uniform_price_is_kplus1_highest": True if n >= k + 1 else False,
        "revenue": frac(revenue),
        "per_winner": per_winner,
        "all_winners_same_price": all_same_price,
        "mismatches": mismatches,
    }


# --------------------------------------------------------------------------- #
# G2 / G4 -- Monte-Carlo agreement and the falsifiability foil.                #
# --------------------------------------------------------------------------- #

def enumerate_exact_means(face, n_bidders, k):
    """Full enumeration of all face^n_bidders iid profiles. Returns
    (exact_mean_true, exact_mean_foil) as Fractions, where
      true revenue  = k * (k+1)-th highest value  (highest LOSING bid),
      foil revenue  = k * (k)-th   highest value  (lowest  WINNING bid)."""
    total_true = 0
    total_foil = 0
    count = 0

    def rec(prefix):
        nonlocal total_true, total_foil, count
        if len(prefix) == n_bidders:
            s = sorted(prefix, reverse=True)
            total_true += k * s[k]        # (k+1)-th highest, 0-indexed s[k]
            total_foil += k * s[k - 1]    # k-th highest, 0-indexed s[k-1]
            count += 1
            return
        for v in range(1, face + 1):
            prefix.append(v)
            rec(prefix)
            prefix.pop()

    rec([])
    return Fraction(total_true, count), Fraction(total_foil, count), count


def run_mc(rng, n, face, n_bidders, k):
    """Draw n iid profiles; accumulate the TRUE revenue sum and sum-of-squares in
    EXACT integer arithmetic (revenue is an integer), so the sample mean and
    variance are exact rationals. Returns (sample_mean, sample_var) as Fractions."""
    total = 0
    total_sq = 0
    for _ in range(n):
        profile = [rng.randint(1, face) for _ in range(n_bidders)]
        third = sorted(profile, reverse=True)[k]   # (k+1)-th highest
        rev = k * third
        total += rev
        total_sq += rev * rev
    sample_mean = Fraction(total, n)
    # unbiased sample variance with (n-1): (sum_sq - n*mean^2)/(n-1)
    sample_var = (Fraction(total_sq) - n * sample_mean * sample_mean) / (n - 1)
    return sample_mean, sample_var


def zscore(sample_mean, sample_var, target_mean, n):
    """z = (sample_mean - target_mean)/(sample_std/sqrt(n)); float only at the end."""
    se = math.sqrt(float(sample_var)) / math.sqrt(n)
    return (float(sample_mean) - float(target_mean)) / se


# --------------------------------------------------------------------------- #
# G3 -- invariance (own-report DSIC) and equivariance (relabelling).           #
# --------------------------------------------------------------------------- #

def own_report_invariance(base_values, k, winner_pos, lo, hi):
    """Vary the reported value of the winner at index winner_pos over every
    integer in [lo, hi]; for each report that keeps it a winner, record its
    Clarke payment. Returns (payments_seen, winning_reports, mismatches). All
    winning reports must yield the SAME payment (the highest losing bid)."""
    others = [(i, Fraction(v)) for i, v in enumerate(base_values) if i != winner_pos]
    other_values = [v for (_, v) in others]
    # highest losing bid the winner faces = k-th highest of the OTHERS
    highest_losing = sorted(other_values, reverse=True)[k - 1]
    payments_seen = []
    winning_reports = []
    for b in range(lo, hi + 1):
        agents = others + [(winner_pos, Fraction(b))]
        winners, payments, _ = clarke_payments(agents, k)
        if winner_pos in winners:
            winning_reports.append(b)
            payments_seen.append(payments[winner_pos])
    distinct = sorted(set(frac(p) for p in payments_seen))
    mismatches = sum(1 for p in payments_seen if p != highest_losing)
    return {
        "winner_pos": winner_pos,
        "highest_losing_bid": frac(highest_losing),
        "winning_reports": winning_reports,
        "distinct_payments": distinct,
        "invariant": len(distinct) == 1 and mismatches == 0,
        "mismatches": mismatches,
    }


def relabel_equivariance(base_values, k, perm):
    """Relabel agent i -> perm[i]. Assert the winner set and payment vector
    permute accordingly. Returns a record with a mismatch count."""
    base_agents = [(i, Fraction(v)) for i, v in enumerate(base_values)]
    w0, p0, _ = clarke_payments(base_agents, k)
    perm_agents = [(perm[i], Fraction(v)) for i, v in enumerate(base_values)]
    w1, p1, _ = clarke_payments(perm_agents, k)
    expected_winners = set(perm[i] for i in w0)
    winners_ok = (w1 == expected_winners)
    pay_mismatches = 0
    for i in w0:
        if p1.get(perm[i]) != p0.get(i):
            pay_mismatches += 1
    mismatches = (0 if winners_ok else 1) + pay_mismatches
    return {
        "permutation": list(perm),
        "winners_original": sorted(w0),
        "winners_relabelled": sorted(w1),
        "winners_equivariant": winners_ok,
        "payment_mismatches": pay_mismatches,
        "mismatches": mismatches,
    }


# --------------------------------------------------------------------------- #

def build_results():
    rng = random.Random(SEED)  # seeded once; consumed only by the MC gate below

    results = {
        "proposal": 250,
        "claim": (
            "Multi-unit single-demand VCG (Clarke pivot): k units to n unit-demand "
            "bidders. Efficient allocation = the k highest-value bidders; each "
            "winner's Clarke-pivot payment = its externality on others = "
            "W_{-i}(without i) - W_{-i}(with i) = the SAME uniform price = the "
            "(k+1)-th highest valuation (highest losing bid); truthful reporting "
            "is a dominant strategy; expected revenue = k*E[V_{(k+1):n}]. On "
            "n=5,k=2,v=(10,8,6,4,2): winners {10,8}, uniform price 6, revenue 12. "
            "At k=1 it recovers single-item second-price (price = 2nd highest)."
        ),
        "seed": SEED,
        "z_accept": zfmt(Z_ACCEPT),
        "z_reject": zfmt(Z_REJECT),
        "fixed_instance": {"valuations": list(VALUATIONS), "k": K},
        "mc_n": MC_N,
        "mc_face": FACE,
        "mc_n_bidders": MC_N_BIDDERS,
        "mc_k": MC_K,
    }

    # --- G1 EXACT: externality payment == uniform (k+1)-th-highest price -------
    primary = run_instance(VALUATIONS, K)
    tie = run_instance((10, 8, 8, 4, 2), 2)      # exercises tie-breaking
    single = run_instance(VALUATIONS, 1)         # recovers single-item 2nd price
    triple = run_instance(VALUATIONS, 3)
    instances = [primary, tie, single, triple]
    total_mismatches = sum(inst["mismatches"] for inst in instances)

    # explicit hand-worked check of the headline instance
    headline_ok = (
        primary["winner_values"] == [10, 8]
        and primary["uniform_price"] == frac(6)
        and primary["revenue"] == frac(12)
        and all(w["externality_payment"] == frac(6) for w in primary["per_winner"])
    )
    # k=1 recovers single-item second-price (price = 2nd highest = 8)
    single_recovers_second_price = (single["uniform_price"] == frac(8))
    # k=3 uniform price = 4th highest = 4, revenue = 12
    triple_ok = (triple["uniform_price"] == frac(4) and triple["revenue"] == frac(12))

    g1_pass = (
        total_mismatches == 0
        and all(inst["all_winners_same_price"] for inst in instances)
        and headline_ok and single_recovers_second_price and triple_ok
    )
    results["G1_exact"] = {
        "instances": instances,
        "total_mismatches": total_mismatches,
        "headline_ok": headline_ok,
        "single_item_recovers_second_price": single_recovers_second_price,
        "triple_ok": triple_ok,
        "z": None,
        "z_note": "exact",
        "pass": g1_pass,
    }

    # --- G2 MONTE-CARLO agreement (|z| < 3) ------------------------------------
    exact_true, exact_foil, enum_count = enumerate_exact_means(
        FACE, MC_N_BIDDERS, MC_K)
    sample_mean, sample_var = run_mc(rng, MC_N, FACE, MC_N_BIDDERS, MC_K)
    z_true = zscore(sample_mean, sample_var, exact_true, MC_N)
    g2_pass = abs(z_true) < Z_ACCEPT
    results["G2_mc_agreement"] = {
        "n_profiles": MC_N,
        "enum_profiles": enum_count,
        "exact_mean_true": frac(exact_true),
        "exact_mean_true_float": f"{float(exact_true):.6f}",
        "sample_mean": frac(sample_mean),
        "sample_mean_float": f"{float(sample_mean):.6f}",
        "sample_std_float": f"{math.sqrt(float(sample_var)):.6f}",
        "z": zfmt(z_true),
        "autocorrelated_needs_batch_means": False,
        "iid_se_is_honest": True,
        "pass": g2_pass,
    }

    # --- G3 INVARIANCE: own-report DSIC + relabel equivariance -----------------
    # (a) vary the winner at index 1 (value 8) over its whole winning range.
    dsic = own_report_invariance(VALUATIONS, K, winner_pos=1, lo=7, hi=30)
    # (b) relabel the agents by a fixed non-trivial permutation.
    PERM = [2, 0, 3, 1, 4]
    equiv = relabel_equivariance(VALUATIONS, K, PERM)
    g3_mismatches = dsic["mismatches"] + equiv["mismatches"]
    g3_pass = (g3_mismatches == 0 and dsic["invariant"]
               and equiv["winners_equivariant"])
    results["G3_invariance"] = {
        "own_report_dsic": dsic,
        "relabel_equivariance": equiv,
        "total_mismatches": g3_mismatches,
        "z": None,
        "z_note": "exact",
        "pass": g3_pass,
    }

    # --- G4 FALSIFIABILITY: reject the lowest-winning-bid foil (SAME sample) ----
    z_foil = zscore(sample_mean, sample_var, exact_foil, MC_N)
    g4_pass = abs(z_foil) > Z_REJECT
    results["G4_falsifiability"] = {
        "foil": "uniform price = lowest WINNING bid (k-th highest = 2nd highest)",
        "exact_mean_foil": frac(exact_foil),
        "exact_mean_foil_float": f"{float(exact_foil):.6f}",
        "z_foil": zfmt(z_foil),
        "rejected": g4_pass,
        "same_sample_agrees_true": g2_pass,
        "pass": g4_pass,
    }

    gates = {
        "G1": results["G1_exact"]["pass"],
        "G2": results["G2_mc_agreement"]["pass"],
        "G3": results["G3_invariance"]["pass"],
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

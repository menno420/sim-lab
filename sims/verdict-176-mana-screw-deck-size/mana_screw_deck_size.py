#!/usr/bin/env python3
"""PROPOSAL 163 - mana screw is governed by DECK SIZE, not land FRACTION.

PHENOMENON (one line)
    Opening-hand "mana screw/flood" consistency is a VARIANCE property, and at a
    MATCHED land fraction the variance of lands drawn in a 7-card opening hand is
    strictly LOWER for a smaller deck. The land count in an opening hand is
    hypergeometric with variance n*p*(1-p)*(N-n)/(N-1); the finite-population
    correction (N-n)/(N-1) SHRINKS as the deck size N shrinks, so a 40-card deck at
    40% lands is more consistent (fewer off-curve hands) than a 60-card deck at 40%
    lands - even though the EXPECTED lands per card (n*p = 2.8) is identical.

FOLK BELIEF
    "Consistency is set by the land RATIO - 40% lands is 40% lands, so a 40-card
    deck and a 60-card deck at the same fraction screw you equally." That is the
    ratio-only null, and it predicts EQUAL off-curve rates. It is false: the mean
    lands-per-card is indeed identical, but the SPREAD is not - the smaller deck's
    hypergeometric FPC (33/39) is below the larger deck's (53/59), so its opening
    hand clusters tighter around the mean and lands in the [2,4] keep window more
    often. Deck SIZE, not fraction, is the consistency lever.

GAME-DESIGN THESIS (reasoned to fuller form - Q-0254 duty)
    Model an opening hand as n=7 cards drawn WITHOUT replacement from a deck of N
    cards containing K = round(p*N) lands. The land count X in the opening hand is
    Hypergeometric(N, K, n), with
        E[X]   = n * (K/N) = n*p                     (identical across matched p)
        Var[X] = n*p*(1-p) * (N-n)/(N-1)             (FPC shrinks with N)
    Define an "off-curve" opening hand = land count OUTSIDE the keep window [2,4]
    (i.e. <=1 lands = screwed, or >=5 lands = flooded). Because both decks share
    the same mean 2.8 but the 40-card deck has strictly smaller variance, its land
    count sits inside [2,4] more often, so its off-curve proportion is strictly
    LOWER. The ratio-only null (equal off-curve) is REJECTED at many sigma; the
    measured variance ratio matches the closed-form FPC ratio to Monte-Carlo error,
    pinning the mechanism to the finite-population correction and nothing else.

FORMAL MODEL (committed constants)
    Deck A = N=40 with K=16 lands (p=0.40); Deck B = N=60 with K=24 lands (p=0.40).
    Opening hand n=7 drawn without replacement via the urn recurrence (land drawn
    with prob lands_left/cards_left each pick). Keep window [2,4]; off-curve = land
    count <=1 or >=5. G3 is a DISTRIBUTION SHIFT to a different matched fraction
    p=0.30 (Deck A' = N=40/12 lands, Deck B' = N=60/18 lands, same n=7) with the
    keep window RECENTERED to [1,3] (mean 2.1); off-curve = <=0 or >=4.

PRE-REGISTERED GATES (APPROVE iff ALL hold, in order G1 -> G2 -> G3; z_gate=3.0)
    G1 head (>=3 sigma separation): measured off-curve proportion for Deck B (60)
        is strictly GREATER than for Deck A (40) at matched 40% fraction. Two-
        proportion z = (pB - pA)/sqrt(pA(1-pA)/T + pB(1-pB)/T) must be >= 3. This
        rejects the ratio-only null (which predicts pA == pB).
    G2 mechanism (closed-form match): measured variance ratio VarB/VarA agrees with
        the closed-form FPC ratio [(53/59)/(33/39)] within Monte-Carlo error. Report
        the agreement z (delta method on the ratio of two sample variances); PASS
        when |z| < 3 - validation that the effect IS the finite-population
        correction, not something else.
    G3 robustness (shifted distribution, >=3 sigma): re-run the G1 head at the
        SHIFTED matched fraction p=0.30 with the recentered window; Deck B' off-
        curve > Deck A' at two-proportion z >= 3. Confirms the deck-size law is not
        an artifact of the 40% choice.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (mirrors the sibling
    speedrun_record_drought.py). The results dict carries NO digest field; main()
    rounds every float to 6 dp, hashes the compact-canonical (sorted-keys,
    comma/colon-separated) JSON, and prints an indent=2 pretty dump then a
    `Results-JSON sha256:` line. In-process double-run must produce identical dicts
    (determinism assert). No JSON is written to disk. Grounding: hypergeometric
    variance + finite-population correction, en.wikipedia.org/wiki/Hypergeometric_distribution.
"""
import math
import json
import hashlib
import random

SEED = 20260717
TRIALS = 400000
Z_GATE = 3.0
HAND = 7

# Matched-fraction decks at p=0.40 (G1/G2), keep window [2,4].
N_A, K_A = 40, 16
N_B, K_B = 60, 24
KEEP_LO, KEEP_HI = 2, 4

# Shifted matched-fraction decks at p=0.30 (G3), recentered window [1,3].
N_A2, K_A2 = 40, 12
N_B2, K_B2 = 60, 18
KEEP_LO2, KEEP_HI2 = 1, 3


def theory_var(N, K, n):
    """Exact hypergeometric variance n*p*(1-p)*(N-n)/(N-1)."""
    p = K / N
    return n * p * (1.0 - p) * (N - n) / (N - 1)


def theory_offcurve(N, K, n, lo, hi):
    """Exact P(land count outside [lo, hi]) under Hypergeometric(N, K, n)."""
    denom = math.comb(N, n)
    inside = 0
    for x in range(lo, hi + 1):
        if 0 <= x <= K and 0 <= n - x <= N - K:
            inside += math.comb(K, x) * math.comb(N - K, n - x)
    return 1.0 - inside / denom


def draw_hand_lands(rng, N, K, n):
    """Land count in an n-card opening hand drawn WITHOUT replacement (urn)."""
    lands = K
    total = N
    count = 0
    for _ in range(n):
        if rng.random() * total < lands:
            count += 1
            lands -= 1
        total -= 1
    return count


def sample_pass(rng, N, K, n, lo, hi):
    """One Monte-Carlo pass: return (off-curve count, raw power sums S1..S4)."""
    off = 0
    s1 = s2 = s3 = s4 = 0.0
    for _ in range(TRIALS):
        x = draw_hand_lands(rng, N, K, n)
        if x < lo or x > hi:
            off += 1
        s1 += x
        s2 += x * x
        s3 += x * x * x
        s4 += x * x * x * x
    return off, s1, s2, s3, s4


def central_moments(s1, s2, s3, s4, T):
    """Population central moments (mu2..mu4) from raw power sums."""
    m = s1 / T
    mu2 = s2 / T - m * m
    mu3 = s3 / T - 3 * m * (s2 / T) + 2 * m ** 3
    mu4 = s4 / T - 4 * m * (s3 / T) + 6 * m * m * (s2 / T) - 3 * m ** 4
    return m, mu2, mu3, mu4


def two_prop_z(off_a, off_b, T):
    """z for (pB - pA) under independent-sample two-proportion SE."""
    pa = off_a / T
    pb = off_b / T
    se = math.sqrt(pa * (1 - pa) / T + pb * (1 - pb) / T)
    return pa, pb, (pb - pa) / se, se


def run():
    rng = random.Random(SEED)
    res = {}
    res["params"] = {
        "seed": SEED,
        "trials": TRIALS,
        "z_gate": Z_GATE,
        "hand_size": HAND,
        "deck_a": {"N": N_A, "lands": K_A, "p": K_A / N_A},
        "deck_b": {"N": N_B, "lands": K_B, "p": K_B / N_B},
        "keep_window": [KEEP_LO, KEEP_HI],
        "deck_a_shift": {"N": N_A2, "lands": K_A2, "p": K_A2 / N_A2},
        "deck_b_shift": {"N": N_B2, "lands": K_B2, "p": K_B2 / N_B2},
        "keep_window_shift": [KEEP_LO2, KEEP_HI2],
        "off_curve_def": "land count outside the keep window (<lo screwed, >hi flooded)",
        "g3_shift": "matched fraction shifted 0.40->0.30, keep window recentered [2,4]->[1,3]",
    }

    # Closed-form anchors (theory).
    var_a_th = theory_var(N_A, K_A, HAND)
    var_b_th = theory_var(N_B, K_B, HAND)
    fpc_a = (N_A - HAND) / (N_A - 1)          # 33/39
    fpc_b = (N_B - HAND) / (N_B - 1)          # 53/59
    fpc_ratio = fpc_b / fpc_a                 # (53/59)/(33/39)
    res["theory"] = {
        "mean_lands": HAND * (K_A / N_A),
        "var_a_hypergeom": var_a_th,
        "var_b_hypergeom": var_b_th,
        "fpc_a_33_39": fpc_a,
        "fpc_b_53_59": fpc_b,
        "fpc_ratio_b_over_a": fpc_ratio,
        "var_ratio_theory_b_over_a": var_b_th / var_a_th,
        "offcurve_a_theory": theory_offcurve(N_A, K_A, HAND, KEEP_LO, KEEP_HI),
        "offcurve_b_theory": theory_offcurve(N_B, K_B, HAND, KEEP_LO, KEEP_HI),
        "offcurve_a_shift_theory": theory_offcurve(N_A2, K_A2, HAND, KEEP_LO2, KEEP_HI2),
        "offcurve_b_shift_theory": theory_offcurve(N_B2, K_B2, HAND, KEEP_LO2, KEEP_HI2),
    }

    # --- p=0.40 passes (feed G1 head + G2 mechanism) ---
    off_a, a1, a2, a3, a4 = sample_pass(rng, N_A, K_A, HAND, KEEP_LO, KEEP_HI)
    off_b, b1, b2, b3, b4 = sample_pass(rng, N_B, K_B, HAND, KEEP_LO, KEEP_HI)

    # G1 head: off-curve(B) strictly > off-curve(A), two-proportion z >= 3.
    pa, pb, z_g1, se_g1 = two_prop_z(off_a, off_b, TRIALS)
    g1 = (pb > pa) and (z_g1 >= Z_GATE)
    res["g1_head_deck_size"] = {
        "offcurve_a_40card": pa,
        "offcurve_b_60card": pb,
        "diff_b_minus_a": pb - pa,
        "se": se_g1,
        "z": z_g1,
        "ratio_only_null": "equal off-curve (pB == pA)",
        "pass": g1,
    }

    # G2 mechanism: sample variance ratio matches the FPC ratio, |z| < 3.
    mean_a, mu2_a, _, mu4_a = central_moments(a1, a2, a3, a4, TRIALS)
    mean_b, mu2_b, _, mu4_b = central_moments(b1, b2, b3, b4, TRIALS)
    s2_a = mu2_a * TRIALS / (TRIALS - 1)      # unbiased sample variance
    s2_b = mu2_b * TRIALS / (TRIALS - 1)
    var_s2_a = (mu4_a - mu2_a ** 2) / TRIALS  # Var of the sample variance
    var_s2_b = (mu4_b - mu2_b ** 2) / TRIALS
    ratio_obs = s2_b / s2_a
    # delta method on F = s2_b/s2_a with independent A,B samples
    var_ratio = ratio_obs ** 2 * (var_s2_b / s2_b ** 2 + var_s2_a / s2_a ** 2)
    se_ratio = math.sqrt(var_ratio)
    z_g2 = (ratio_obs - fpc_ratio) / se_ratio
    g2 = abs(z_g2) < Z_GATE
    res["g2_mechanism_fpc"] = {
        "var_a_measured": s2_a,
        "var_b_measured": s2_b,
        "var_ratio_measured_b_over_a": ratio_obs,
        "fpc_ratio_closed_form": fpc_ratio,
        "se_ratio": se_ratio,
        "z": z_g2,
        "mean_a_check": mean_a,
        "mean_b_check": mean_b,
        "pass": g2,
    }

    # --- p=0.30 shifted pass (feeds G3 robustness) ---
    off_a2, _, _, _, _ = sample_pass(rng, N_A2, K_A2, HAND, KEEP_LO2, KEEP_HI2)
    off_b2, _, _, _, _ = sample_pass(rng, N_B2, K_B2, HAND, KEEP_LO2, KEEP_HI2)
    pa2, pb2, z_g3, se_g3 = two_prop_z(off_a2, off_b2, TRIALS)
    g3 = (pb2 > pa2) and (z_g3 >= Z_GATE)
    res["g3_robustness_shift"] = {
        "offcurve_a_40card": pa2,
        "offcurve_b_60card": pb2,
        "diff_b_minus_a": pb2 - pa2,
        "se": se_g3,
        "z": z_g3,
        "shift": "p=0.30, keep window [1,3]",
        "pass": g3,
    }

    gates = [
        {"id": "G1", "name": "head_deck_size", "pass": g1, "z": z_g1},
        {"id": "G2", "name": "mechanism_fpc", "pass": g2, "z": z_g2},
        {"id": "G3", "name": "robustness_shift", "pass": g3, "z": z_g3},
    ]
    res["gates"] = gates
    res["all_pass"] = all(x["pass"] for x in gates)
    res["first_failing_gate"] = next((x["id"] for x in gates if not x["pass"]), None)
    return res


def round_floats(o, ndigits=6):
    if isinstance(o, float):
        return round(o, ndigits)
    if isinstance(o, dict):
        return {k: round_floats(v, ndigits) for k, v in o.items()}
    if isinstance(o, list):
        return [round_floats(v, ndigits) for v in o]
    return o


def canonical_sha256(res):
    blob = json.dumps(round_floats(res, 6), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    res1 = run()
    res2 = run()
    h1 = canonical_sha256(res1)
    h2 = canonical_sha256(res2)
    assert h1 == h2, "non-deterministic: in-process double-run digests differ"
    print(json.dumps(round_floats(res1, 6), indent=2, sort_keys=True))
    print("Results-JSON sha256: " + h1)
    raise SystemExit(0 if res1["all_pass"] else 1)


if __name__ == "__main__":
    main()

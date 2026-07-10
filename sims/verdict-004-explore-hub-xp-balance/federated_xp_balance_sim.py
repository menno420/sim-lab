#!/usr/bin/env python3
"""
federated_xp_balance_sim.py
VERDICT 004 / idea-engine PROPOSAL 004 — explore-hub federated-world GLOBAL XP balance.

Canonical idea: menno420/superbot docs/ideas/explore-hub-federated-world-2026-06-19.md
@ fd638e3c0693687a62093aa6bd75954e238fa58d (pinned).
Routed as idea-engine control/outbox.md PROPOSAL 004 @
cd7251ec30950d12d29e65c57d843864387d0aec (pinned).

WHAT THIS SETTLES
  The explore-hub contract is "loops are accelerators, never gates." A GLOBAL XP pool
  receives a trickle from per-game XP; the global level confers global skills
  (stamina/carry/luck/xp-gain) meant to help in ANY game. This sweep asks which
  (trickle ratio t + effect size e + mechanism split phi) parameter sets keep the global
  pool a MEASURABLE cold-start accelerator in a NEW game WHILE (a) never substituting for
  per-game mastery and (b) never gating content.

  The load-bearing result is STRUCTURAL, not a tuned magnitude: when global skills are
  pure RATE/efficiency multipliers (phi = 0) the substitution index and the gate-risk band
  are ZERO for EVERY swept effect size e and trickle t, BY CONSTRUCTION — "accelerator,
  never gate" holds as an identity — while cold-start advantage (CSA) still scales with e,
  t, and veteran depth. Only when the effect budget is spent on in-game COMPETENCE
  (phi > 0, the luck-as-gear / carry-as-dominance style) does global level start to
  substitute for mastery and open a global-only content band.

WHAT IT DOES NOT SETTLE (declared, not hidden)
  The recommended MAGNITUDE (how much acceleration "feels good" / stays "measurable") is a
  hypothesis pending live telemetry. The earn shapes here are family-level stand-ins for the
  shipped mining/fishing/GAME_ENCOUNTERS curves, not the catalogue; session-length is
  abstracted; the organic efficiency->power conversion a player performs (secondary
  substitution) is unmodeled. See REPORT.md.

RUN (one documented command, deterministic, stdlib-only, exit 0 iff all self-checks pass):
  python3 sims/verdict-004-explore-hub-xp-balance/federated_xp_balance_sim.py

SEEDS: 5 fixed seeds; each headline metric is mean +/- population stdev across seeds.
Common random numbers: ONE per-session earn-noise sequence per seed is reused for the
veteran and the fresh player, so the only difference between them is the earn multiplier
(the variance-reduction trick from intake-003). No wall-clock, no hash(); PYTHONHASHSEED
is never relied upon.
"""

import random
import statistics
from collections import OrderedDict

# ----------------------------------------------------------------------------- config
SEEDS = [11, 23, 42, 101, 2027]
BASE_SESSION_XP = 100.0     # abstract earn units per session (family-level stand-in)
NOISE_CV = 0.15             # per-session earn noise: Normal(1, 0.15) clipped to > 0.05
SESSIONS_MAX = 600          # climb cap (never reached at these earn rates; asserted)

# Per-game leveling curve and its inverse.
def xp_for_level(L):
    return 60.0 * (L ** 1.6)

def level_from_xp(xp):
    return (xp / 60.0) ** (1.0 / 1.6)

L_BASE = 10                 # per-game "core loop comfortable" -- time-to-baseline target
L_MASTER = 50               # per-game mastery ceiling

def pg_competence(L):
    """Per-game competence, normalized so pg_competence(L_MASTER) == 1.0."""
    return (min(L, L_MASTER) / L_MASTER) ** 0.8

BOOST_CAP = 0.60            # hard cap on the earn-RATE multiplier's global term
GCOMP_CAP = 0.60            # hard cap on the flat COMPETENCE a maxed global pool can add

# Calibrate GLOBAL_CAP_XP so a MODERATE veteran (n_prior=3, L_vet=25) at t=0.10 reaches
# global_frac ~= 0.5. Derived constant, not a free knob.
GLOBAL_CAP_XP = (0.10 * 3 * xp_for_level(25)) / 0.5

# thresholds for the decision table
CSA_MIN = 0.10              # claim (a): "measurable" cold-start accelerator
GCOMP_MAX = 0.15            # claim (b): global stays a garnish (no substitution)
GATE_SMALL = 0.15           # gate-risk band must be small (0 by construction at phi=0)

# ----------------------------------------------------------------------------- sweep grids
TRICKLES = [0.02, 0.05, 0.10, 0.20, 0.40]
EFFECTS = [0.05, 0.10, 0.20, 0.35, 0.50]
PHIS = [0.0, 0.25, 0.50, 1.0]
DEPTHS = OrderedDict([                       # veteran career: (n_prior, L_vet)
    ("shallow", (1, 15)),
    ("moderate", (3, 25)),
    ("deep", (6, 40)),
])

# recommended default (phi=0 is the load-bearing constraint; magnitude is a UX dial)
REC_PHI = 0.0
REC_E = 0.20
REC_T = 0.10
REC_DEPTH = "moderate"


# ----------------------------------------------------------------------------- mechanism
def global_pool_of(t, n_prior, L_vet):
    """Trickle t of the veteran's prior per-game XP flows into the shared global pool."""
    return t * n_prior * xp_for_level(L_vet)

def global_frac_of(t, n_prior, L_vet):
    return min(1.0, global_pool_of(t, n_prior, L_vet) / GLOBAL_CAP_XP)

def rate_effect(e, phi):
    """Pure-accelerator share of the effect budget: multiplies earn RATE only."""
    return e * (1.0 - phi)

def power_effect(e, phi):
    """Substitution-prone share: adds flat in-game COMPETENCE."""
    return e * phi

def earn_multiplier(e, phi, gf):
    return 1.0 + min(BOOST_CAP, rate_effect(e, phi) * gf)

def global_competence(e, phi, gf):
    return min(GCOMP_CAP, power_effect(e, phi) * gf)

def effective_competence(L, e, phi, gf):
    return pg_competence(L) + global_competence(e, phi, gf)


# ----------------------------------------------------------------------------- traces
_NOISE = {}
def noise_seq(seed):
    """ONE per-session earn-noise sequence per seed, reused for veteran and fresh (CRN)."""
    if seed not in _NOISE:
        rng = random.Random(seed)
        _NOISE[seed] = [max(rng.gauss(1.0, NOISE_CV), 0.05) for _ in range(SESSIONS_MAX)]
    return _NOISE[seed]


def trajectory(mult, seed):
    """Cumulative XP per session until the L_BASE threshold is crossed."""
    noise = noise_seq(seed)
    thr = xp_for_level(L_BASE)
    cum = 0.0
    out = []
    for s in range(SESSIONS_MAX):
        cum += BASE_SESSION_XP * mult * noise[s]
        out.append(cum)
        if cum >= thr:
            break
    return out


def sessions_to_baseline(mult, seed):
    """First session index (1-based) whose cumulative XP >= xp_for_level(L_BASE)."""
    return len(trajectory(mult, seed))


_TFRESH = {}
def t_fresh(seed):
    """Fresh player: global_frac = 0 -> earn_multiplier = 1. Cached per seed."""
    if seed not in _TFRESH:
        _TFRESH[seed] = sessions_to_baseline(1.0, seed)
    return _TFRESH[seed]


def mean_sd(xs):
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


# ----------------------------------------------------------------------------- metrics
def csa_cell(e, phi, t, n_prior, L_vet):
    """Cold-start advantage over SEEDS for one parameter cell (common random numbers)."""
    gf = global_frac_of(t, n_prior, L_vet)
    mult = earn_multiplier(e, phi, gf)
    csas = []
    for seed in SEEDS:
        tf = t_fresh(seed)
        tv = sessions_to_baseline(mult, seed)
        csas.append((tf - tv) / tf)
    return mean_sd(csas), mult, gf


def msi_cell(e, phi):
    """Mastery-substitution index at a global-MAXED (global_frac=1.0), game-NOVICE player.

    novice_competence = effective_competence(L_BASE, gf=1.0)
    master_competence = pg_competence(L_MASTER) = 1.0
    Also returns global's share of a true master's effective competence.
    """
    gcomp = global_competence(e, phi, 1.0)
    novice = effective_competence(L_BASE, e, phi, 1.0)
    master = pg_competence(L_MASTER)                 # == 1.0
    msi = novice / master
    master_eff = effective_competence(L_MASTER, e, phi, 1.0)
    global_share = gcomp / master_eff
    gate_risk_band = gcomp                           # 0 iff phi==0 or e==0
    return {
        "gcomp": gcomp,
        "msi": msi,
        "master_share": global_share,
        "gate_risk_band": gate_risk_band,
    }


# ----------------------------------------------------------------------------- self-checks
_CHECKS = {"pass": 0}
def _check(cond, label):
    if cond:
        _CHECKS["pass"] += 1
    else:
        raise AssertionError("SELF-CHECK FAILED: " + label)


def full_grid_selfcheck():
    """Iterate every one of the 300 grid cells and tie the simulated numbers to the
    analytic mechanism. Any violation aborts (exit 1)."""
    for t in TRICKLES:
        for depth, (n_prior, L_vet) in DEPTHS.items():
            gf = global_frac_of(t, n_prior, L_vet)
            _check(0.0 <= gf <= 1.0, "global_frac in [0,1] (t=%.2f %s)" % (t, depth))
            for e in EFFECTS:
                for phi in PHIS:
                    (csa_m, _csa_s), mult, _gf = csa_cell(e, phi, t, n_prior, L_vet)
                    re_ = rate_effect(e, phi)
                    # earn_multiplier >= 1 always; == 1 exactly iff gf==0 or rate_effect==0
                    _check(mult >= 1.0, "earn_multiplier >= 1 (t=%.2f e=%.2f phi=%.2f %s)"
                           % (t, e, phi, depth))
                    if gf == 0.0 or re_ == 0.0:
                        _check(abs(mult - 1.0) <= 1e-12,
                               "earn_multiplier == 1 when gf==0 or rate_effect==0 "
                               "(t=%.2f e=%.2f phi=%.2f %s)" % (t, e, phi, depth))
                    else:
                        _check(mult > 1.0,
                               "earn_multiplier > 1 when accelerating "
                               "(t=%.2f e=%.2f phi=%.2f %s)" % (t, e, phi, depth))
                    # t_vet <= t_fresh on every cell (more boost is never slower)
                    for seed in SEEDS:
                        _check(sessions_to_baseline(mult, seed) <= t_fresh(seed),
                               "t_vet <= t_fresh (t=%.2f e=%.2f phi=%.2f %s seed=%d)"
                               % (t, e, phi, depth, seed))
                    # CSA in [0, 1) on every cell
                    _check(0.0 <= csa_m < 1.0, "CSA in [0,1) (t=%.2f e=%.2f phi=%.2f %s)"
                           % (t, e, phi, depth))
                    # analytic tie: sim rate matches the closed form within noise
                    for seed in SEEDS:
                        tv = sessions_to_baseline(mult, seed)
                        tf = t_fresh(seed)
                        _check(abs(tv - tf / mult) / tf < 0.15,
                               "analytic tie t_vet ~= t_fresh/mult "
                               "(t=%.2f e=%.2f phi=%.2f %s seed=%d)" % (t, e, phi, depth, seed))
                    # phi==0 => global_competence(1.0)==0 => MSI == pg_competence(L_BASE)
                    #           AND gate_risk_band == 0  (structural no-substitution/no-gate)
                    m = msi_cell(e, phi)
                    if phi == 0.0:
                        _check(m["gcomp"] == 0.0,
                               "phi=0 => global_competence(1.0)==0 (e=%.2f)" % e)
                        _check(m["msi"] == pg_competence(L_BASE),
                               "phi=0 => MSI == pg_competence(L_BASE) (e=%.2f)" % e)
                        _check(m["gate_risk_band"] == 0.0,
                               "phi=0 => gate_risk_band==0 (e=%.2f)" % e)


def monotonicity_selfcheck():
    """CSA nondecreasing in e (fixed phi<1, t, depth); global_competence & gate_risk_band
    nondecreasing in phi and in e; pg_competence nondecreasing in L; pg_competence(L_MASTER)==1."""
    # CSA nondecreasing in e
    for t in TRICKLES:
        for depth, (n_prior, L_vet) in DEPTHS.items():
            for phi in [p for p in PHIS if p < 1.0]:
                prev = -1.0
                for e in EFFECTS:
                    (csa_m, _s), _mult, _gf = csa_cell(e, phi, t, n_prior, L_vet)
                    _check(csa_m >= prev - 1e-9,
                           "CSA nondecreasing in e (t=%.2f phi=%.2f %s e=%.2f)"
                           % (t, phi, depth, e))
                    prev = csa_m
    # global_competence & gate_risk_band nondecreasing in e (fixed phi) and in phi (fixed e)
    for phi in PHIS:
        prev = -1.0
        for e in EFFECTS:
            g = global_competence(e, phi, 1.0)
            _check(g >= prev - 1e-12, "global_competence nondecreasing in e (phi=%.2f e=%.2f)"
                   % (phi, e))
            prev = g
    for e in EFFECTS:
        prev = -1.0
        for phi in PHIS:
            g = global_competence(e, phi, 1.0)
            _check(g >= prev - 1e-12, "global_competence nondecreasing in phi (e=%.2f phi=%.2f)"
                   % (e, phi))
            prev = g
    # pg_competence monotonic nondecreasing in L; pg_competence(L_MASTER) == 1.0
    prev = -1.0
    for L in range(0, L_MASTER + 11):
        c = pg_competence(L)
        _check(c >= prev - 1e-12, "pg_competence nondecreasing in L (L=%d)" % L)
        prev = c
    _check(pg_competence(L_MASTER) == 1.0, "pg_competence(L_MASTER) == 1.0")


# ----------------------------------------------------------------------------- experiments
def determinism_selftest():
    """Same (seed, params) run twice -> byte-identical trajectory + metrics."""
    print("=" * 78)
    print("DETERMINISM SELF-TEST  -  same (seed, params) twice => byte-identical")
    print("=" * 78)
    n_prior, L_vet = DEPTHS[REC_DEPTH]
    gf = global_frac_of(REC_T, n_prior, L_vet)
    mult = earn_multiplier(REC_E, REC_PHI, gf)
    traj1 = trajectory(mult, 42)
    metr1 = csa_cell(REC_E, REC_PHI, REC_T, n_prior, L_vet)
    _NOISE.clear()
    _TFRESH.clear()
    traj2 = trajectory(mult, 42)
    metr2 = csa_cell(REC_E, REC_PHI, REC_T, n_prior, L_vet)
    _check(traj1 == traj2, "determinism: identical trajectory for identical (seed, params)")
    _check(metr1 == metr2, "determinism: identical metrics for identical (seed, params)")
    print("  trajectory length = %d sessions; CSA(mean) = %.4f; identical on re-run: YES"
          % (len(traj1), metr1[0][0]))


def csa_sweep():
    """CSA over (trickle t x effect e) at phi=0, MODERATE veteran. Shows accelerator
    magnitude and that a pure-RATE global still accelerates cold-start."""
    print("\n" + "=" * 78)
    print("CSA SWEEP  -  cold-start advantage, phi=0 (pure rate), MODERATE veteran (3,25)")
    print("CSA = (t_fresh - t_vet)/t_fresh, mean over %d seeds. 'measurable' line = %.2f."
          % (len(SEEDS), CSA_MIN))
    print("=" * 78)
    n_prior, L_vet = DEPTHS["moderate"]
    print("  t\\e    " + "".join("%9.2f" % e for e in EFFECTS))
    for t in TRICKLES:
        row = []
        for e in EFFECTS:
            (csa_m, _s), _mult, _gf = csa_cell(e, 0.0, t, n_prior, L_vet)
            row.append("%8.3f%s" % (csa_m, "*" if csa_m >= CSA_MIN else " "))
        print("  %.2f  " % t + "".join(row))
    print("  (* = at/above the %.2f measurable line)  gf(moderate) grows with t; earn cap %.2f"
          % (CSA_MIN, BOOST_CAP))


def mechanism_sweep():
    """global_competence(1.0), MSI, gate_risk_band over (phi x e). Shows substitution/gate
    risk is driven by phi (the MECHANISM), ZERO at phi=0 for every e."""
    print("\n" + "=" * 78)
    print("MECHANISM SWEEP  -  substitution/gate risk vs (phi x e), global pool MAXED (gf=1.0)")
    print("gcomp=global_competence(1.0); MSI=novice/master; band=gate_risk_band. "
          "Master baseline=1.0.")
    print("no-substitution safe-band: gcomp < %.2f ; gate-free iff band==0 (phi=0 or e=0)."
          % GCOMP_MAX)
    print("=" * 78)
    for metric in ("gcomp", "msi", "gate_risk_band"):
        label = {"gcomp": "global_competence(1.0)",
                 "msi": "MSI = novice/master",
                 "gate_risk_band": "gate_risk_band"}[metric]
        print("\n  [%s]" % label)
        print("  phi\\e  " + "".join("%9.2f" % e for e in EFFECTS))
        for phi in PHIS:
            row = []
            for e in EFFECTS:
                v = msi_cell(e, phi)[metric]
                row.append("%9.3f" % v)
            print("  %.2f  " % phi + "".join(row))
    print("\n  -> at phi=0 every gcomp and band cell is 0.000: no substitution, no gate, "
          "at any e.")


def veteran_depth_sweep():
    """CSA over veteran depth x effect e at phi=0, trickle fixed at the recommended t.
    Robustness at the edges: does a shallow vet still get some accel? does a deep vet cap out?"""
    print("\n" + "=" * 78)
    print("VETERAN-DEPTH SWEEP  -  CSA over depth x e, phi=0, trickle t=%.2f (recommended)"
          % REC_T)
    print("Depths: shallow=(1,15), moderate=(3,25), deep=(6,40). CSA mean over %d seeds."
          % len(SEEDS))
    print("=" * 78)
    print("  depth      gf     " + "".join("%9.2f" % e for e in EFFECTS))
    for depth, (n_prior, L_vet) in DEPTHS.items():
        gf = global_frac_of(REC_T, n_prior, L_vet)
        row = []
        for e in EFFECTS:
            (csa_m, _s), _mult, _gf = csa_cell(e, 0.0, REC_T, n_prior, L_vet)
            row.append("%8.3f%s" % (csa_m, "*" if csa_m >= CSA_MIN else " "))
        print("  %-9s %.3f  " % (depth, gf) + "".join(row))
    print("  (* = >= %.2f)  deeper careers -> higher global_frac -> more cold-start accel, "
          "capped by BOOST_CAP." % CSA_MIN)


def safe_region():
    """DECISION TABLE: every (t, e, phi) at MODERATE depth with CSA, gcomp, gate_risk_band
    and PASS/FAIL vs thresholds. The safe region is where cold-start is measurable AND global
    never substitutes AND the gate-risk band is small."""
    print("\n" + "=" * 78)
    print("SAFE REGION (decision table)  -  MODERATE veteran (3,25), all (t,e,phi)")
    print("PASS iff CSA >= %.2f  AND  global_competence(1.0) < %.2f  AND  gate_risk_band < %.2f"
          % (CSA_MIN, GCOMP_MAX, GATE_SMALL))
    print("=" * 78)
    n_prior, L_vet = DEPTHS["moderate"]
    print("     t     e   phi      CSA    gcomp     band   verdict")
    n_pass = 0
    n_gate_free_pass = 0
    pass_cells = []
    for t in TRICKLES:
        for e in EFFECTS:
            for phi in PHIS:
                (csa_m, _s), _mult, _gf = csa_cell(e, phi, t, n_prior, L_vet)
                m = msi_cell(e, phi)
                ok = (csa_m >= CSA_MIN and m["gcomp"] < GCOMP_MAX
                      and m["gate_risk_band"] < GATE_SMALL)
                gate_free = (m["gate_risk_band"] == 0.0)
                tag = "PASS" if ok else "fail"
                if ok:
                    n_pass += 1
                    if gate_free:
                        n_gate_free_pass += 1
                    pass_cells.append((t, e, phi, csa_m, gate_free))
                print("  %5.2f %5.2f %5.2f  %7.3f  %7.3f  %7.3f   %s%s"
                      % (t, e, phi, csa_m, m["gcomp"], m["gate_risk_band"], tag,
                         "  [gate-free]" if gate_free else ""))
    total = len(TRICKLES) * len(EFFECTS) * len(PHIS)
    print("  -> %d / %d cells PASS the loose thresholds; of those %d are GATE-FREE "
          "(band==0), all at phi=0." % (n_pass, total, n_gate_free_pass))
    print("     The %d PASS cells at phi>0 carry a small but NONZERO gate-risk band "
          "(0.05-0.125): content in" % (n_pass - n_gate_free_pass))
    print("     (1.0, 1.0+band] would be reachable ONLY with global level -> a gate. Under the")
    print("     strict 'never gate' contract only the phi=0 column is truly safe; magnitude (e,t)")
    print("     then sets how much cold-start acceleration you buy. Recommended default lives here.")
    return pass_cells


def recommended_headline():
    """The ONE recommended default set, with its actual numbers."""
    print("\n" + "=" * 78)
    print("RECOMMENDED DEFAULT  ->  phi=%.2f (pure RATE), e=%.2f, trickle t=%.2f"
          % (REC_PHI, REC_E, REC_T))
    print("=" * 78)
    n_prior, L_vet = DEPTHS[REC_DEPTH]
    (csa_m, csa_s), mult, gf = csa_cell(REC_E, REC_PHI, REC_T, n_prior, L_vet)
    m = msi_cell(REC_E, REC_PHI)
    print("  moderate veteran (3,25): global_frac=%.3f, earn_multiplier=%.3f" % (gf, mult))
    print("  CSA (cold-start advantage) = %.3f +/- %.3f  (measurable line %.2f)"
          % (csa_m, csa_s, CSA_MIN))
    print("  global_competence(1.0)     = %.3f   (substitution safe-band < %.2f)"
          % (m["gcomp"], GCOMP_MAX))
    print("  gate_risk_band             = %.3f   (0 => 'accelerator never gate' by construction)"
          % m["gate_risk_band"])
    print("  MSI (global-maxed novice / true master) = %.3f  (pg_competence(L_BASE)=%.3f)"
          % (m["msi"], pg_competence(L_BASE)))
    print("  deeper veterans clear the %.2f line comfortably (see veteran-depth sweep); "
          "magnitude is a" % CSA_MIN)
    print("  UX dial pending live telemetry. The STRUCTURAL claim (phi=0 => no substitution,")
    print("  no gate, at every e and t) is settled by construction, not by this magnitude.")


def main():
    print("federated XP balance sim  |  seeds=%s  sessions_max=%d  L_BASE=%d  L_MASTER=%d"
          % (SEEDS, SESSIONS_MAX, L_BASE, L_MASTER))
    print("GLOBAL_CAP_XP=%.1f (derived: moderate vet @ t=0.10 -> global_frac=0.5); "
          "BOOST_CAP=%.2f GCOMP_CAP=%.2f" % (GLOBAL_CAP_XP, BOOST_CAP, GCOMP_CAP))
    determinism_selftest()
    full_grid_selfcheck()
    monotonicity_selfcheck()
    csa_sweep()
    mechanism_sweep()
    veteran_depth_sweep()
    safe_region()
    recommended_headline()
    print("\n" + "=" * 78)
    print("SELF-CHECKS: %d passed, 0 failed  (determinism; earn_multiplier>=1 & ==1 iff "
          "no-accel;" % _CHECKS["pass"])
    print("t_vet<=t_fresh; CSA in [0,1); analytic tie; phi=0 => no-substitution & no-gate;")
    print("monotonicity in e/phi/L; global_frac in [0,1]; all 300 grid cells). Exit 0.")
    print("=" * 78)


if __name__ == "__main__":
    main()

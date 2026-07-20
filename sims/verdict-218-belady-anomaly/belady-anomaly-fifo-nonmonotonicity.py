#!/usr/bin/env python3
"""Belady's anomaly verifier -- PROPOSAL 205 (round-49 FLEET slot).

Claim: FIFO page replacement is NON-monotone in the number of frames -- giving
the cache MORE memory can make it fault MORE. On the canonical reference string
[1,2,3,4,1,2,5,1,2,3,4,5] FIFO faults 9 times with 3 frames but 10 times with 4.
LRU (a STACK algorithm: the resident set at m frames is always a subset of the
resident set at m+1 frames -- Mattson, Gecsei, Slutz & Traiger 1970) is provably
immune: adding a frame can never increase LRU faults, so LRU is never anomalous.

Deterministic, stdlib-only. SEED = 20260717. Raw counts are stored as integers
(perfectly deterministic); derived rates / z are stored as fixed-precision
STRINGS so the results JSON is byte-stable. An in-process double-run reproduces
the identical results-dict sha256, and a separate cross-invocation reproduces it
too. The sha256 is of the WHOLE dict and is NOT a field of the dict (NO-SELF-FIELD).

Gates:
  G1  EXACTLY-TRUE canonical witness ([1,2,3,4,1,2,5,1,2,3,4,5]): FIFO faults
      == 9 at 3 frames and == 10 at 4 frames, anomaly_delta = +1 (>0); AND LRU
      faults on the SAME string are monotone non-increasing across frames 1..5.
      Direction: exact integer equality; PASS iff FIFO delta>0 AND LRU monotone
      non-increasing.
  G2  EXHAUSTIVE EXACTLY-TRUE (all A=4 length-8 strings, 4^8 = 65536; frames
      1..4): FIFO_anomalous == 0 AND LRU_anomalous == 0 (both exact integers).
      Direction: both exactly 0. Exhaustive enumeration matches the closed-form
      prediction -- LRU is immune by the stack/inclusion property, and FIFO
      cannot be Belady-anomalous with <=4 distinct pages, pinning the anomaly
      threshold above 4 pages (the classic minimal FIFO anomaly needs 5 pages,
      length 12). Not a claim about all lengths: exhaustive over length-8
      strings on 4 pages only.
  G3  >=3 sigma SIGNAL (N=200000 random strings, A=6, L=16, frames 1..6,
      random.Random(SEED)): two-proportion one-sided z-test H0 p_fifo==p_lru vs
      p_fifo>p_lru. Direction: z >= 3. z clears 3 sigma because the comparator
      LRU is provably exactly 0, so even a rare-but-nonzero FIFO rate is hugely
      significant against zero. LRU anomaly count must be 0.
  G4  ROBUSTNESS / regime-shift (N=200000 random strings, A=7, L=20, frames
      1..7, random.Random(20260718)): FIFO anomaly rate stays above floor 0.0003
      AND the shifted-regime two-proportion z (FIFO vs LRU=0) >= 3, while LRU
      stays exactly 0. Direction: the FIFO anomaly persists above the floor
      across the regime shift while LRU is invariantly 0.
"""
import json
import hashlib
import math
import random
from collections import deque

SEED = 20260717


def fifo_faults(ref, frames):
    """FIFO page replacement: evict the oldest-INSERTED page. Count page faults."""
    resident = set()
    order = deque()
    faults = 0
    for p in ref:
        if p not in resident:
            faults += 1
            if len(resident) >= frames:
                old = order.popleft()
                resident.discard(old)
            resident.add(p)
            order.append(p)
    return faults


def lru_faults(ref, frames):
    """LRU page replacement: on a hit move the page to MRU; on a miss evict the
    LRU (front) page. Count page faults."""
    resident = set()
    order = []  # order[0] = LRU, order[-1] = MRU
    faults = 0
    for p in ref:
        if p in resident:
            order.remove(p)
            order.append(p)
        else:
            faults += 1
            if len(resident) >= frames:
                old = order.pop(0)
                resident.discard(old)
            resident.add(p)
            order.append(p)
    return faults


def fifo_anomalous(ref, fmax):
    """True iff exists m in [1..fmax-1] with fifo_faults(ref, m+1) > fifo_faults(ref, m)."""
    prev = fifo_faults(ref, 1)
    for m in range(2, fmax + 1):
        cur = fifo_faults(ref, m)
        if cur > prev:
            return True
        prev = cur
    return False


def lru_anomalous(ref, fmax):
    """True iff exists m in [1..fmax-1] with lru_faults(ref, m+1) > lru_faults(ref, m)."""
    prev = lru_faults(ref, 1)
    for m in range(2, fmax + 1):
        cur = lru_faults(ref, m)
        if cur > prev:
            return True
        prev = cur
    return False


def two_prop_z(a_count, b_count, N):
    """One-sided two-proportion z for H0: p_a == p_b (b is the LRU comparator)."""
    p_a = a_count / N
    p_b = b_count / N
    p_pool = (a_count + b_count) / (2 * N)
    denom = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / N + 1.0 / N))
    return (p_a - p_b) / denom


def gate1():
    canonical = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    f3 = fifo_faults(canonical, 3)
    f4 = fifo_faults(canonical, 4)
    delta = f4 - f3
    lru_curve = [lru_faults(canonical, m) for m in range(1, 6)]
    lru_monotone = all(lru_curve[i + 1] <= lru_curve[i] for i in range(len(lru_curve) - 1))
    ok = (f3 == 9) and (f4 == 10) and (delta > 0) and lru_monotone
    return ok, {
        "canonical": list(canonical),
        "fifo_3": f3,
        "fifo_4": f4,
        "anomaly_delta": delta,
        "lru_curve_frames_1_to_5": lru_curve,
        "lru_monotone_non_increasing": lru_monotone,
        "pass": ok,
    }


def gate2():
    A, L, fmax = 4, 8, 4
    total = A ** L
    fifo_anom = 0
    lru_anom = 0
    ref = [0] * L
    for code in range(total):
        c = code
        for i in range(L):
            ref[i] = c % A
            c //= A
        if fifo_anomalous(ref, fmax):
            fifo_anom += 1
        if lru_anomalous(ref, fmax):
            lru_anom += 1
    ok = (fifo_anom == 0) and (lru_anom == 0)
    return ok, {
        "A": A, "L": L, "total": total, "frames_max": fmax,
        "fifo_anomalous": fifo_anom,
        "lru_anomalous": lru_anom,
        "pass": ok,
    }


def _sample_gate(rng, N, A, L, fmax):
    fifo_anom = 0
    lru_anom = 0
    randrange = rng.randrange
    for _ in range(N):
        ref = [randrange(A) for _ in range(L)]
        if fifo_anomalous(ref, fmax):
            fifo_anom += 1
        if lru_anomalous(ref, fmax):
            lru_anom += 1
    return fifo_anom, lru_anom


def gate3():
    N, A, L, fmax = 200000, 6, 16, 6
    rng = random.Random(SEED)
    fifo_anom, lru_anom = _sample_gate(rng, N, A, L, fmax)
    p_fifo = fifo_anom / N
    z = two_prop_z(fifo_anom, lru_anom, N)
    ok = (z >= 3.0) and (lru_anom == 0)
    return ok, {
        "N": N, "A": A, "L": L, "frames_max": fmax,
        "fifo_anom": fifo_anom,
        "lru_anom": lru_anom,
        "p_fifo": f"{p_fifo:.10f}",
        "z": f"{z:.6f}",
        "pass": ok,
    }


def gate4():
    N, A, L, fmax = 200000, 7, 20, 7
    rng = random.Random(20260718)
    fifo_anom, lru_anom = _sample_gate(rng, N, A, L, fmax)
    rate = fifo_anom / N
    z = two_prop_z(fifo_anom, lru_anom, N)
    floor = 0.0003
    ok = (rate > floor) and (z >= 3.0) and (lru_anom == 0)
    return ok, {
        "N": N, "A": A, "L": L, "frames_max": fmax,
        "fifo_anom": fifo_anom,
        "fifo_rate": f"{rate:.10f}",
        "lru_anom": lru_anom,
        "z": f"{z:.6f}",
        "floor": f"{floor:.10f}",
        "pass": ok,
    }


def compute():
    g1_ok, g1 = gate1()
    g2_ok, g2 = gate2()
    g3_ok, g3 = gate3()
    g4_ok, g4 = gate4()
    return {
        "seed": SEED,
        "G1_canonical_witness": g1,
        "G2_exhaustive": g2,
        "G3_signal": g3,
        "G4_robustness": g4,
        "gates": {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok},
        "decision": "sim-ready" if (g1_ok and g2_ok and g3_ok and g4_ok) else "needs-more-grooming",
    }


def canonical_json(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    c1 = canonical_json(r1)
    c2 = canonical_json(r2)
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + r1["decision"])


if __name__ == "__main__":
    main()

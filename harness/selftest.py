#!/usr/bin/env python3
"""Self-test for harness/simharness.py -- the consumer proof for this slice.

One documented command, exit 0 iff every helper behaves as the five source
sims relied on. This is what substrate-gate checks.

    python3 harness/selftest.py
"""

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import simharness as h  # noqa: E402


def main():
    sc = h.SelfCheck()

    # SEEDS: the frozen standard multi-seed set.
    sc.check(h.SEEDS == [11, 23, 42, 101, 2027], "SEEDS is the standard set")

    # mean_sd: pstdev, 0.0 for a single sample.
    m, s = h.mean_sd([2, 4, 6])
    sc.check(m == 4 and round(s, 9) == round((8 / 3) ** 0.5, 9),
             "mean_sd: mean and population stdev")
    sc.check(h.mean_sd([7]) == (7, 0.0), "mean_sd: single sample -> 0 stdev")

    # CrnCache: builds once per key, reuses, rebuilds after clear.
    calls = []

    def build(k):
        calls.append(k)
        return [k, k + 1]

    crn = h.CrnCache()
    sc.check(crn.get(5, build) == [5, 6], "crn: build")
    sc.check(crn.get(5, build) == [5, 6], "crn: reuse cached")
    sc.check(calls == [5], "crn: built once per key")
    crn.clear()
    crn.get(5, build)
    sc.check(calls == [5, 5], "crn: rebuild after clear")

    # sweep: full cartesian product, every cell present.
    rows = h.sweep({"a": [1, 2], "b": [10, 20]}, run=lambda a, b: a + b)
    sc.check(len(rows) == 4 and sorted(r[1] for r in rows) == [11, 12, 21, 22],
             "sweep: full grid")

    # expect_reject / expect_ok: gate fails closed, happy path stays open.
    def boom():
        raise ValueError("scope_denied")

    sc.expect_reject("gate fails closed (with code)", boom, code="scope_denied")
    sc.expect_ok("happy path stays open", lambda: None)

    # in_set: enum validator.
    sc.in_set("BUILD", {"BUILD", "HOLD", "KILL"}, "rec in VALID_RECS")

    # determinism_check (run twice, cache cleared inside) + canonical JSON.
    crn2 = h.CrnCache()

    def produce():
        crn2.clear()
        return [crn2.get(sd, lambda s: [s * 3, s * 3 + 1]) for sd in h.SEEDS]

    h.determinism_check(sc, produce, "sim re-run byte-identical")
    h.determinism_bytes(sc, {"z": 1, "a": [3, 2, 1]}, "canonical JSON stable")

    # modal / agreement_rate.
    winner, top, _ = h.modal(["BUILD", "BUILD", "HOLD"])
    sc.check(winner == "BUILD" and top == 2, "modal: winner and count")
    rate, w, _ = h.agreement_rate(["A", "A", "A", "B", "A"])
    sc.check(round(rate, 3) == 0.8 and w == "A", "agreement_rate: 4/5")

    # load_frozen_runs: sorted, deterministic load over a tiny fixture.
    with tempfile.TemporaryDirectory() as td:
        runs = os.path.join(td, "runs")
        os.makedirs(runs)
        for val in ["b", "a"]:  # written out of order
            with open(os.path.join(runs, "run_%s.json" % val), "w") as f:
                json.dump({"v": val}, f)
        loaded = h.load_frozen_runs(td)
        sc.check([n for n, _ in loaded] == ["run_a.json", "run_b.json"],
                 "load_frozen_runs: sorted deterministic order")

    return sc.report()


if __name__ == "__main__":
    sys.exit(main())

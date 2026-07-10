"""sim-lab harness -- reusable helpers extracted from the first five verdict sims.

Stdlib-only. Vendor-COPY the pieces you need into sims/<slug>/ -- sims stay
self-contained (the layout contract) and never import this module at runtime.
This file is a copy source, not a dependency.

Provenance (which sims re-invented each piece before extraction):
  SEEDS, mean_sd            intake-003, verdict-004
  CrnCache (CRN caching)    intake-003 (_HONEST_CACHE), verdict-004 (_NOISE)
  SelfCheck battery         all five (intake-001/002/003, verdict-004/005)
  sweep (grid runner)       intake-002, intake-003, verdict-004
  determinism_check/_bytes  intake-003, verdict-004 (run-twice); verdict-005 (json)
  modal, agreement_rate     intake-001, verdict-005 (frozen-run analyzers)
  load_frozen_runs          intake-001 (runs/cells.json), verdict-005 (runs/*.json)

See harness/README.md for the usage note and the self-test command.
"""

import itertools
import json
import os
import statistics


# ---- seeded runs (rung-1 numeric sims) -------------------------------------

# The standard multi-seed set. Every seedable sim so far used exactly this,
# so cross-seed stability is always reported over the same five streams.
SEEDS = [11, 23, 42, 101, 2027]


def mean_sd(xs):
    """(mean, population stdev); stdev is 0.0 for a single sample.

    Byte-identical in intake-003 and verdict-004.
    """
    xs = list(xs)
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


class CrnCache:
    """Common-Random-Numbers cache keyed by seed (variance reduction).

    Draw a seed's noise stream once, reuse it across every sweep cell / arm so
    differences are signal, not RNG jitter. `get(key, build)` builds once per
    key; `clear()` before a determinism re-run so it rebuilds from seed.

    Extracted from intake-003 (honest_trace/_HONEST_CACHE) and verdict-004
    (noise_seq/_NOISE, which already cited intake-003's trick).
    """

    def __init__(self):
        self._d = {}

    def get(self, key, build):
        if key not in self._d:
            self._d[key] = build(key)
        return self._d[key]

    def clear(self):
        self._d.clear()


def sweep(grid, run):
    """Full-grid parameter sweep -- the anti-cherry-pick idiom.

    grid: dict of name -> list of values (dict preserves insertion order).
    run:  callable(**cell) -> result row.
    Returns [(cell_dict, result), ...] over the FULL cartesian product, so the
    report shows the whole table, never just the best point.

    Extracted from intake-002 (RL_CAPACITIES x RL_REFILLS), intake-003
    (THRESHOLDS x DEBOUNCES x COOLDOWNS), verdict-004 (300 cells).
    """
    names = list(grid.keys())
    rows = []
    for combo in itertools.product(*[grid[n] for n in names]):
        cell = dict(zip(names, combo))
        rows.append((cell, run(**cell)))
    return rows


# ---- self-check battery (all five sims) ------------------------------------

class SelfCheck:
    """Assertion battery with a pass counter -- re-invented in all five sims.

    check() raises AssertionError('SELF-CHECK FAILED: ...') on a hole; report()
    prints the uniform 'SELF-CHECKS: n passed, 0 failed' line and returns an
    exit code (0 clean). Provenance: intake-003 _CHECKS/_check, verdict-004
    _CHECKS/_check, verdict-005 _CHECKS/check, intake-002 CHECKS/expect_reject/
    expect_ok, intake-001 inline assert battery.
    """

    def __init__(self):
        self.passed = 0
        self.detail = []

    def check(self, cond, label):
        self.detail.append((bool(cond), label))
        if cond:
            self.passed += 1
        else:
            raise AssertionError("SELF-CHECK FAILED: " + label)
        return bool(cond)

    def expect_reject(self, label, fn, code=None):
        """Assert fn() raises; optionally that the error text carries `code`.

        intake-002 adversarial rig: a gate that fails OPEN is a hole, so the
        ABSENCE of an exception is the failure.
        """
        try:
            fn()
        except Exception as e:  # noqa: BLE001 -- any rejection counts
            if code is not None and code not in str(e):
                raise AssertionError(
                    "SELF-CHECK FAILED: %s (rejected but not with %r: %s)"
                    % (label, code, e))
            self.passed += 1
            self.detail.append((True, label))
            return
        raise AssertionError(
            "SELF-CHECK FAILED: %s (expected rejection, got none)" % label)

    def expect_ok(self, label, fn):
        """Assert fn() does NOT raise -- the happy path stays open."""
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            raise AssertionError(
                "SELF-CHECK FAILED: %s (unexpected reject: %s)" % (label, e))
        self.passed += 1
        self.detail.append((True, label))

    def in_set(self, value, allowed, label):
        """Enum/range validator: intake-001 VALID_RECS, verdict-005
        VALID_RESULTS/VALID_SOURCES, intake-002 REQUIRED_SCOPES."""
        return self.check(
            value in allowed,
            "%s: %r not in %s" % (label, value, sorted(allowed)))

    def report(self):
        """Print the terminal line every sim ends on; return exit code."""
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


# ---- determinism (rung-1 run-twice + frozen-run canonical JSON) ------------

def determinism_check(sc, produce, label="determinism: identical output for identical seed"):
    """Run produce() twice and assert byte-identical results.

    produce: zero-arg callable returning any ==-comparable value. If it uses a
    CrnCache, clear it INSIDE produce so the second run rebuilds from seed.
    intake-003/verdict-004 run the sim twice, clearing the noise cache between.
    """
    return sc.check(produce() == produce(), label)


def determinism_bytes(sc, obj, label="determinism: stable canonical JSON"):
    """Byte-identical canonical serialization check (frozen-run analyzers).

    verdict-005 analyze.py: json.dumps(obj, indent=2, sort_keys=True) twice,
    assert equal -- the analyzer copies frozen stamps and calls no clock.
    """
    s1 = json.dumps(obj, indent=2, sort_keys=True)
    s2 = json.dumps(obj, indent=2, sort_keys=True)
    return sc.check(s1 == s2, label)


# ---- frozen-run analyzers (rung-2 prototypes: live layer -> frozen JSON) ----

def load_frozen_runs(here, subdir="runs", suffix=".json"):
    """Load every frozen run JSON under <here>/<subdir>/, sorted by filename
    (deterministic order). Returns [(name, data), ...].

    intake-001 (runs/cells.json), verdict-005 (runs/probe_*_run{1..5}.json).
    The live layer that produced these is NOT seedable; reproducibility is
    redefined as agreement bounds + a byte-identical analyzer over the freeze.
    """
    root = os.path.join(here, subdir)
    out = []
    for name in sorted(os.listdir(root)):
        if name.endswith(suffix):
            with open(os.path.join(root, name)) as f:
                out.append((name, json.load(f)))
    return out


def modal(values):
    """(winner, top_count, counts) -- most common value, ties broken by sorted
    order for determinism.

    Near-identical modal() in intake-001 (recs -> winner, is_tie) and
    verdict-005 (values -> winner, top_count, counts).
    """
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winner = sorted(k for k, v in counts.items() if v == top)[0]
    return winner, top, counts


def agreement_rate(values):
    """(rate, winner, counts) with rate = modal_count / N -- the frozen-run
    reproducibility metric when the live layer can't be seeded (verdict-005)."""
    values = list(values)
    if not values:
        return 0.0, None, {}
    winner, top, counts = modal(values)
    return top / len(values), winner, counts

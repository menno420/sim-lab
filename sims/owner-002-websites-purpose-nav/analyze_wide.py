#!/usr/bin/env python3
"""owner-002 -- robustness addendum: WIDER-CAP re-crawl analysis (control-plane + botsite).

VERDICT 011 audited four sites; two LIVE sites (control-plane, botsite) hit the
80-page / depth-2 crawl cap, leaving a ROBUST-gate gap and one open @codex
question: "could the 80-page cap hide a broken route that flips a sub-verdict?"

This analyzer closes that gap. It ingests the WIDER snapshots
(runs/{control-plane,botsite}-wide.json, crawled at cap=400 pages / depth=8, 2
passes each) alongside the ORIGINAL narrow snapshots, RE-DERIVES every metric
from the JSON (reusing analyze_nav.py's measured metric functions -- same
source-of-truth discipline), and computes the KEY comparison: does the wider
crawl surface any NEW dead links / broken routes / orphans BEYOND the 80-cap, and
would any of it FLIP a sub-verdict?

Determinism is the same two-layer contract as analyze_nav.py:
  (1) live re-crawl AGREEMENT -- pass1 vs pass2 url->status (asserted == 1.0);
  (2) this ANALYSIS over the committed wide snapshots is BYTE-DETERMINISTIC --
      run twice, asserted byte-identical (determinism_bytes).

The metric functions + SelfCheck harness are REUSED (imported) from the sibling
analyze_nav.py so the two analyzers never drift; analyze_nav.py itself vendor-
copies the harness helpers from harness/simharness.py @ 87ca0df (sims stay
self-contained, never import the harness at runtime).

Run:  python3 sims/owner-002-websites-purpose-nav/analyze_wide.py
Ends on sys.exit(sc.report()); writes results-wide.json next to this file.
"""

import json
import os
import sys

import analyze_nav as base  # sibling in the same sim dir; reuse measured metrics

HERE = os.path.dirname(os.path.abspath(__file__))

# The two LIVE sites that hit the 80-page cap in VERDICT 011. For each we compare
# the ORIGINAL narrow snapshot (runs/<site>.json, 80/depth-2) against the WIDER
# snapshot (runs/<site>-wide.json, 400/depth-8).
WIDE_SITES = ["control-plane", "botsite"]


def _dead_url_set(site_metrics):
    return set(site_metrics["dead_links"]["urls"])


def _crawled_url_set(snap):
    # Normalize a trailing slash the way the crawler's own canon dedup does
    # (canon = url.rstrip("/")), so the home page in its "/base/" vs "/base"
    # string forms compares equal across a narrow and a wider re-crawl.
    return {p["url"].rstrip("/") for p in snap["passes"][0]["pages"]}


def compute_wide():
    """Whole computation, deterministic, no clock / no network / no randomness."""
    per_site = {}
    for name in WIDE_SITES:
        narrow_snap = base.load_snapshot(name)
        wide_snap = base.load_snapshot(name + "-wide")

        narrow = base.compute_site(narrow_snap)
        wide = base.compute_site(wide_snap)

        cap = wide_snap.get("cap", {})
        # Truncation: did the wider crawl hit its own 400-page cap?
        wide_truncated = wide["total_pages"] >= int(cap.get("pages", 400))

        narrow_dead = _dead_url_set(narrow)
        wide_dead = _dead_url_set(wide)
        new_dead = sorted(wide_dead - narrow_dead)      # surfaced only past the 80-cap
        dropped_dead = sorted(narrow_dead - wide_dead)  # in narrow but not wide (want: none)

        narrow_broken = set(narrow["broken_assets"]["urls"])
        wide_broken = set(wide["broken_assets"]["urls"])
        new_broken = sorted(wide_broken - narrow_broken)

        narrow_orphan = set(narrow["orphan_pages"]["urls"])
        wide_orphan = set(wide["orphan_pages"]["urls"])
        new_orphan = sorted(wide_orphan - narrow_orphan)

        # Is the wider dead-link set a SUPERSET-or-equal of the narrow one?
        wide_is_superset = narrow_dead.issubset(wide_dead)
        crawled_superset = _crawled_url_set(narrow_snap).issubset(_crawled_url_set(wide_snap))

        # A sub-verdict flips only if the wider crawl surfaces a NEW hard failure
        # (a dead route / broken asset / orphan) that the 80-cap hid AND that is
        # not an already-known / benign class. New 404s on in-content .md/.sh
        # doc-cross-references are the SAME defect class VERDICT 011 already ruled
        # (control-plane's known 25) -- more instances of a ruled defect do not
        # flip the ruling. We record the raw counts and let the report judge; the
        # deterministic flag here is "did a NEW hard failure appear at all".
        surfaced_new_hard_failures = bool(new_dead or new_broken or new_orphan)

        per_site[name] = {
            "base_url": wide["base_url"],
            "crawl_mode": wide["crawl_mode"],
            "cap": {"pages": int(cap.get("pages", 400)), "depth": int(cap.get("depth", 8))},
            "skipped_prefixes": wide_snap.get("skipped_prefixes", []),
            "wide": {
                "total_pages": wide["total_pages"],
                "max_depth": wide["max_depth"],
                "avg_depth": wide["avg_depth"],
                "dead_links": wide["dead_links"],
                "broken_assets": wide["broken_assets"],
                "orphan_pages": wide["orphan_pages"],
                "dead_end_pages": wide["dead_end_pages"],
                "forms_total": wide["forms_total"],
                "recrawl_agreement": wide["recrawl_agreement"],
                "truncated_at_cap": wide_truncated,
            },
            "narrow": {
                "total_pages": narrow["total_pages"],
                "max_depth": narrow["max_depth"],
                "dead_links_count": narrow["dead_links"]["count"],
                "broken_assets_count": narrow["broken_assets"]["count"],
                "orphan_pages_count": narrow["orphan_pages"]["count"],
                "dead_end_pages_count": narrow["dead_end_pages"]["count"],
            },
            "delta": {
                "pages_gained": wide["total_pages"] - narrow["total_pages"],
                "depth_gained": wide["max_depth"] - narrow["max_depth"],
                "new_dead_links": {"count": len(new_dead), "urls": new_dead},
                "dropped_dead_links": {"count": len(dropped_dead), "urls": dropped_dead},
                "new_broken_assets": {"count": len(new_broken), "urls": new_broken},
                "new_orphan_pages": {"count": len(new_orphan), "urls": new_orphan},
                "wide_dead_is_superset_of_narrow": wide_is_superset,
                "wide_crawl_is_superset_of_narrow": crawled_superset,
                "surfaced_new_hard_failures": surfaced_new_hard_failures,
            },
        }
    return {
        "meta": {
            "analysis": "owner-002-websites-purpose-nav -- wider-cap robustness re-crawl",
            "closes": "VERDICT 011 ROBUST-gate 80-page-cap gap + @codex cap question",
            "wide_snapshot_source": "live re-crawl 2026-07-11 (UNPINNED-recrawl); cap=400 pages / depth=8, 2 passes",
            "sites": WIDE_SITES,
            "reproducibility": "byte-identical analyzer over committed wide snapshots; "
                               "live re-crawl agreement-reproducible (see crawl_site.py --max-pages 400 --max-depth 8)",
        },
        "sites": per_site,
    }


def run_selfchecks(sc, results):
    # Run the whole computation a SECOND time and assert byte-identical.
    results2 = compute_wide()
    base.determinism_bytes(sc, results, label="wide-analyze-determinism (run 1 canonical)")
    base.determinism_bytes(sc, results2, label="wide-analyze-determinism (run 2 canonical)")
    sc.check(
        json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True),
        "wide-analyze-determinism: two full runs byte-identical")

    for name in WIDE_SITES:
        s = results["sites"][name]
        snap = base.load_snapshot(name + "-wide")
        w = s["wide"]

        # wider crawl reached MORE pages than the narrow 80-cap, and at least
        # as deep. The wider ENVELOPE is proven by breadth OR depth: control-plane
        # goes deeper (depth 3); botsite is breadth-bound (400 pages exhausted at
        # depth 2 by its ~365 /commands/* + /features fan-out), so it goes wider,
        # not deeper. Either strictly exceeds the narrow 80/depth-2 envelope.
        sc.check(w["total_pages"] > 80, "%s-wide: pages > narrow 80-cap" % name)
        sc.check(w["max_depth"] >= 2, "%s-wide: depth reached >= narrow depth-2" % name)
        sc.check(w["total_pages"] > 80 or w["max_depth"] > 2,
                 "%s-wide: strictly exceeds narrow 80/depth-2 envelope (breadth or depth)" % name)
        sc.check(s["delta"]["pages_gained"] >= 0, "%s-wide: pages_gained >= 0" % name)

        # every http_status in 100..599 across BOTH passes
        for pnum in (0, 1):
            for p in snap["passes"][pnum]["pages"]:
                sc.check(100 <= int(p["http_status"]) <= 599,
                         "%s-wide: http_status %r in 100..599 (pass %d)"
                         % (name, p["http_status"], pnum + 1))

        # live re-crawl agreement still 100% at the wider cap
        sc.check(w["recrawl_agreement"]["rate"] == 1.0,
                 "%s-wide: recrawl_agreement == 1.0" % name)

        # count/urls integrity
        sc.check(w["dead_links"]["count"] == len(w["dead_links"]["urls"]),
                 "%s-wide: dead_links count == len(urls)" % name)
        sc.check(w["broken_assets"]["count"] == len(w["broken_assets"]["urls"]),
                 "%s-wide: broken_assets count == len(urls)" % name)
        sc.check(w["orphan_pages"]["count"] == len(w["orphan_pages"]["urls"]),
                 "%s-wide: orphan_pages count == len(urls)" % name)
        sc.check(w["dead_end_pages"]["count"] == len(w["dead_end_pages"]["urls"]),
                 "%s-wide: dead_end_pages count == len(urls)" % name)

        # crawl surface is a SUPERSET-or-equal of the narrow one (BFS-order guarantee)
        sc.check(s["delta"]["wide_crawl_is_superset_of_narrow"],
                 "%s-wide: crawled URL set superset-or-equal of narrow" % name)

        # /owner (401-gated) must never appear -- we skip it, GET-only, no probe
        for pfx in s["skipped_prefixes"]:
            for p in snap["passes"][0]["pages"]:
                sc.check(not p["url"].startswith(pfx),
                         "%s-wide: skipped prefix %r absent from pages" % (name, pfx))
        # no 401/403 sneaked in (we do not crawl gated routes)
        for p in snap["passes"][0]["pages"]:
            sc.check(int(p["http_status"]) not in (401, 403),
                     "%s-wide: no gated 401/403 page crawled (%s)" % (name, p["url"]))

    # KEY superset assertion for control-plane (the site WITH known dead links):
    # the wider dead-link set must contain every narrow dead link (none dropped).
    cp = results["sites"]["control-plane"]
    sc.check(cp["delta"]["wide_dead_is_superset_of_narrow"],
             "control-plane-wide: dead-link set superset-or-equal of narrow (no known 404 dropped)")
    sc.check(cp["delta"]["dropped_dead_links"]["count"] == 0,
             "control-plane-wide: zero narrow dead links dropped")
    sc.check(cp["narrow"]["dead_links_count"] == 25,
             "control-plane: narrow dead_links == 25 (VERDICT 011 headline)")
    sc.check(cp["wide"]["dead_links"]["count"] >= 25,
             "control-plane-wide: dead_links >= narrow 25 (monotone)")

    # botsite: narrow had 0 dead links; superset means wide >= 0 (trivially true),
    # but assert the narrow baseline for the record.
    bs = results["sites"]["botsite"]
    sc.check(bs["narrow"]["dead_links_count"] == 0,
             "botsite: narrow dead_links == 0 (VERDICT 011 headline)")
    sc.check(bs["delta"]["dropped_dead_links"]["count"] == 0,
             "botsite-wide: zero narrow dead links dropped")


def print_summary(results):
    print()
    print("owner-002 wider-cap robustness re-crawl -- narrow(80/2) vs wide(400/8)")
    print("=" * 96)
    hdr = ("%-14s %14s %10s %8s %10s %9s %8s %9s" %
           ("site", "pages n->w", "depth n->w", "dead", "newdead", "broken", "orphan", "trunc?"))
    print(hdr)
    print("-" * 96)
    for name in WIDE_SITES:
        s = results["sites"][name]
        w, n, d = s["wide"], s["narrow"], s["delta"]
        print("%-14s %14s %10s %8s %10s %9s %8s %9s" % (
            name,
            "%d->%d" % (n["total_pages"], w["total_pages"]),
            "%d->%d" % (n["max_depth"], w["max_depth"]),
            "%d->%d" % (n["dead_links_count"], w["dead_links"]["count"]),
            "+%d" % d["new_dead_links"]["count"],
            "%d/%d" % (w["broken_assets"]["count"], w["broken_assets"]["total_assets"]),
            "%d" % w["orphan_pages"]["count"],
            "YES" if w["truncated_at_cap"] else "no"))
    print("-" * 96)
    for name in WIDE_SITES:
        s = results["sites"][name]
        d = s["delta"]
        print("%-14s new dead=%d  new broken=%d  new orphan=%d  new-hard-failure=%s  recrawl=%.0f%%" % (
            name, d["new_dead_links"]["count"], d["new_broken_assets"]["count"],
            d["new_orphan_pages"]["count"], d["surfaced_new_hard_failures"],
            s["wide"]["recrawl_agreement"]["rate"] * 100))
        if d["new_dead_links"]["urls"]:
            for u in d["new_dead_links"]["urls"][:12]:
                print("               NEW dead: " + u)
            if d["new_dead_links"]["count"] > 12:
                print("               ... (%d more)" % (d["new_dead_links"]["count"] - 12))
    print("=" * 96)


def main():
    sc = base.SelfCheck()
    results = compute_wide()
    run_selfchecks(sc, results)

    out = os.path.join(HERE, "results-wide.json")
    with open(out, "w") as f:
        f.write(json.dumps(results, indent=2, sort_keys=True) + "\n")

    print_summary(results)
    print("wrote", os.path.relpath(out, HERE), "(canonical, sort_keys)")
    return sys.exit(sc.report())


if __name__ == "__main__":
    main()

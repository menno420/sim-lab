#!/usr/bin/env python3
"""owner-002 -- websites-purpose-nav: deterministic analyzer over 4 committed crawl snapshots.

Reads the four committed crawl snapshots under runs/*.json (three LIVE-crawled
Railway sites + one LOCALLY-built review service) and RE-DERIVES every headline
number from the JSON as the single source of truth: per-site page/depth counts,
dead links, broken assets, orphan pages (inbound-graph), dead-end pages, console
errors, forms, task pass rate, re-crawl agreement (pass1 vs pass2), plus a
cross-site consistency block (shared ds/ design system, nav-home presence).

The live crawls are NOT seed-deterministic (a live site can change between
passes); reproducibility here is redefined two ways and BOTH are checked:
  (1) re-crawl AGREEMENT -- pass1 vs pass2 url->status maps (measured 100%);
  (2) the ANALYSIS over the committed snapshots is BYTE-DETERMINISTIC -- the whole
      computation is run twice and asserted byte-identical (determinism_bytes).

Snapshot provenance: menno420/websites @ 31cfd9f (per-site head_sha in each JSON).
Run:  python3 sims/owner-002-websites-purpose-nav/analyze_nav.py
Ends on sys.exit(sc.report()); writes results.json next to this file.

Harness helpers (SEEDS, mean_sd, sweep, SelfCheck, determinism_bytes) are
VENDOR-COPIED below from harness/simharness.py @ 87ca0df -- sims stay
self-contained and never import the harness at runtime (the layout contract).
"""

import itertools
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

# The four snapshots, in a fixed order (deterministic iteration).
SITES = ["botsite", "control-plane", "dashboard", "review"]

# ---------------------------------------------------------------------------
# Vendored harness helpers (copy of harness/simharness.py @ 87ca0df pieces).
# ---------------------------------------------------------------------------

SEEDS = [11, 23, 42, 101, 2027]


def mean_sd(xs):
    xs = list(xs)
    return (statistics.mean(xs), statistics.pstdev(xs) if len(xs) > 1 else 0.0)


def sweep(grid, run):
    names = list(grid.keys())
    rows = []
    for combo in itertools.product(*[grid[n] for n in names]):
        cell = dict(zip(names, combo))
        rows.append((cell, run(**cell)))
    return rows


class SelfCheck:
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

    def in_set(self, value, allowed, label):
        return self.check(
            value in allowed,
            "%s: %r not in %s" % (label, value, sorted(allowed)))

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def determinism_bytes(sc, obj, label="determinism: stable canonical JSON"):
    s1 = json.dumps(obj, indent=2, sort_keys=True)
    s2 = json.dumps(obj, indent=2, sort_keys=True)
    return sc.check(s1 == s2, label)


# ---------------------------------------------------------------------------
# Snapshot loading + per-site computation (all measured from the JSON).
# ---------------------------------------------------------------------------

def load_snapshot(site):
    with open(os.path.join(RUNS, site + ".json")) as f:
        return json.load(f)


def _home_variants(base):
    return {base, base + "/", base.rstrip("/")}


def compute_site(snap):
    """Re-derive every metric for one site from its committed snapshot."""
    base = snap["base_url"]
    p1 = snap["passes"][0]["pages"]
    p2 = snap["passes"][1]["pages"]
    homes = _home_variants(base)

    # --- depth ---
    depths = [p["depth"] for p in p1]
    avg_depth, _ = mean_sd(depths)

    # --- dead links (http_status >= 400) ---
    dead_urls = sorted(p["url"] for p in p1 if int(p.get("http_status", 0)) >= 400)

    # --- broken assets (asset status not None and >= 400) ---
    total_assets = 0
    broken_asset_urls = []
    for p in p1:
        for a in p.get("assets", []):
            if not isinstance(a, dict):
                continue
            total_assets += 1
            st = a.get("status")
            if st is not None and int(st) >= 400:
                broken_asset_urls.append(a["url"])
    broken_asset_urls = sorted(broken_asset_urls)

    # --- inbound graph -> orphan pages (depth>0, no other page links in) ---
    inbound = {}
    for p in p1:
        for link in p.get("out_links", []):
            inbound.setdefault(link, set()).add(p["url"])
    orphan_urls = []
    for p in p1:
        if p["depth"] == 0 or p["url"] in homes:
            continue  # home / base is never an orphan
        srcs = {s for s in inbound.get(p["url"], set()) if s != p["url"]}
        if not srcs:
            orphan_urls.append(p["url"])
    orphan_urls = sorted(orphan_urls)

    # --- dead-end pages ---
    dead_end_urls = sorted(p["url"] for p in p1 if p.get("is_dead_end"))

    # --- console errors: only real when Playwright captured pages ---
    pw = snap.get("playwright", {}) or {}
    pw_pages = pw.get("pages") if isinstance(pw, dict) else None
    if pw_pages:
        console_errors_total = sum(len(pg.get("console_errors", [])) for pg in pw_pages)
        console_errors = console_errors_total
        console_source = "playwright (local)"
    else:
        console_errors = "not-captured (live/proxy)"
        console_source = "skipped: " + str(pw.get("reason", ""))[:200] if isinstance(pw, dict) else "skipped"

    # --- forms ---
    forms_total = sum(int(p.get("forms", 0)) for p in p1)

    # --- task battery ---
    tb = snap.get("task_battery", [])
    tb_pass = sum(1 for t in tb if t.get("reached"))
    tb_total = len(tb)
    task_pass_rate = (tb_pass / tb_total) if tb_total else 0.0
    per_task = [
        {"task": t.get("task"), "reached": bool(t.get("reached")),
         "clicks": t.get("clicks"), "failure": t.get("failure")}
        for t in tb
    ]

    # --- re-crawl agreement (sorted url->status maps of pass1 vs pass2) ---
    m1 = {p["url"]: p["http_status"] for p in p1}
    m2 = {p["url"]: p["http_status"] for p in p2}
    all_urls = sorted(set(m1) | set(m2))
    agree = sum(1 for u in all_urls if m1.get(u) == m2.get(u))
    recrawl_agreement = (agree / len(all_urls)) if all_urls else 0.0
    status_diffs = [
        {"url": u, "pass1": m1.get(u), "pass2": m2.get(u)}
        for u in all_urls if m1.get(u) != m2.get(u)
    ]

    # --- nav-home presence (over reachable 200-status pages) ---
    status200 = [p for p in p1 if int(p.get("http_status", 0)) == 200]
    with_home = sum(
        1 for p in status200 if any(hv in p.get("out_links", []) for hv in homes)
    )
    nav_home_rate = (with_home / len(status200)) if status200 else 0.0

    # --- shared ds/ design system + external link volume ---
    shares_ds = any(
        "/ds/" in a.get("url", "")
        for p in p1 for a in p.get("assets", []) if isinstance(a, dict)
    )
    external_links_total = sum(int(p.get("external_links", 0)) for p in p1)

    return {
        "site": snap["site"],
        "base_url": base,
        "crawl_mode": snap["crawl_mode"],
        "head_sha": snap["head_sha"],
        "purpose_path": snap.get("purpose_path"),
        "purpose_quote": snap.get("purpose_quote"),
        "total_pages": len(p1),
        "max_depth": max(depths),
        "avg_depth": round(avg_depth, 4),
        "dead_links": {"count": len(dead_urls), "urls": dead_urls},
        "broken_assets": {"count": len(broken_asset_urls),
                          "total_assets": total_assets,
                          "urls": broken_asset_urls},
        "orphan_pages": {"count": len(orphan_urls), "urls": orphan_urls},
        "dead_end_pages": {"count": len(dead_end_urls), "urls": dead_end_urls},
        "console_errors": console_errors,
        "console_source": console_source,
        "forms_total": forms_total,
        "external_links_total": external_links_total,
        "task_battery": {"passed": tb_pass, "total": tb_total,
                         "rate": round(task_pass_rate, 4), "per_task": per_task},
        "recrawl_agreement": {"rate": round(recrawl_agreement, 4),
                              "compared": len(all_urls), "diffs": status_diffs},
        "nav_home": {"rate": round(nav_home_rate, 4),
                     "pages_with_home": with_home,
                     "status200_pages": len(status200)},
        "shares_ds_design_system": shares_ds,
    }


def compute_cross_site(sites):
    """Measured cross-site consistency block."""
    ds = {name: sites[name]["shares_ds_design_system"] for name in SITES}
    navh = {name: sites[name]["nav_home"]["rate"] for name in SITES}
    titles = {}
    for name in SITES:
        snap = load_snapshot(name)
        titles[name] = snap["passes"][0]["pages"][0].get("title", "")
    ds_shared_count = sum(1 for v in ds.values() if v)
    return {
        "ds_design_system": ds,
        "ds_shared_count": ds_shared_count,
        "ds_shared_by_all": ds_shared_count == len(SITES),
        "nav_home_rate": navh,
        "home_title": titles,
    }


def build_results():
    """Whole computation, deterministic, no clock / no network / no randomness."""
    sites = {}
    for name in SITES:
        sites[name] = compute_site(load_snapshot(name))
    return {
        "meta": {
            "analysis": "owner-002-websites-purpose-nav",
            "snapshot_source": "menno420/websites @ 31cfd9f",
            "sites": SITES,
            "seeds_available": SEEDS,  # analysis is snapshot-deterministic; seeds unused
            "reproducibility": "byte-identical analyzer over committed snapshots; "
                               "live re-crawl agreement-reproducible (see crawl_site.py)",
        },
        "sites": sites,
        "cross_site": compute_cross_site(sites),
    }


def run_selfchecks(sc, results):
    sites = results["sites"]

    # Run the whole computation a SECOND time and assert byte-identical.
    results2 = build_results()
    determinism_bytes(sc, results, label="analyze-determinism (run 1 canonical)")
    determinism_bytes(sc, results2, label="analyze-determinism (run 2 canonical)")
    sc.check(
        json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True),
        "analyze-determinism: two full runs byte-identical")

    for name in SITES:
        s = sites[name]
        snap = load_snapshot(name)
        # pages > 0
        sc.check(s["total_pages"] > 0, "%s: pages > 0" % name)
        # every http_status in 100..599
        for p in snap["passes"][0]["pages"]:
            sc.check(100 <= int(p["http_status"]) <= 599,
                     "%s: http_status %r in 100..599" % (name, p["http_status"]))
        # recrawl agreement measured 100%
        sc.check(s["recrawl_agreement"]["rate"] == 1.0,
                 "%s: recrawl_agreement == 1.0" % name)
        # dead_links count matches listed urls length
        sc.check(s["dead_links"]["count"] == len(s["dead_links"]["urls"]),
                 "%s: dead_links count == len(urls)" % name)
        # broken_assets count matches listed urls length
        sc.check(s["broken_assets"]["count"] == len(s["broken_assets"]["urls"]),
                 "%s: broken_assets count == len(urls)" % name)
        # task_pass_rate in [0,1]
        sc.check(0.0 <= s["task_battery"]["rate"] <= 1.0,
                 "%s: task_pass_rate in [0,1]" % name)
        # orphan sanity: home / base never in the orphan list
        for hv in _home_variants(s["base_url"]):
            sc.check(hv not in s["orphan_pages"]["urls"],
                     "%s: home %r not an orphan" % (name, hv))
        # avg_depth never exceeds max_depth
        sc.check(s["avg_depth"] <= s["max_depth"],
                 "%s: avg_depth <= max_depth" % name)

    # Headline guards (the numbers the verdict rests on).
    sc.check(sites["control-plane"]["dead_links"]["count"] == 25,
             "control-plane: dead_links == 25 (headline)")
    sc.check(sites["botsite"]["dead_links"]["count"] == 0,
             "botsite: dead_links == 0")
    sc.check(sites["dashboard"]["dead_links"]["count"] == 0,
             "dashboard: dead_links == 0")
    sc.check(sites["review"]["dead_links"]["count"] == 0,
             "review: dead_links == 0")
    sc.check(sites["dashboard"]["forms_total"] == 0,
             "dashboard: forms_total == 0 (read-only guard)")
    sc.in_set(sites["review"]["crawl_mode"], {"local"},
              "review: crawl_mode == local")
    sc.in_set(sites["control-plane"]["crawl_mode"], {"live"},
              "control-plane: crawl_mode == live")
    sc.in_set(sites["botsite"]["crawl_mode"], {"live"},
              "botsite: crawl_mode == live")
    sc.in_set(sites["dashboard"]["crawl_mode"], {"live"},
              "dashboard: crawl_mode == live")
    # orphans measured 0 everywhere
    for name in SITES:
        sc.check(sites[name]["orphan_pages"]["count"] == 0,
                 "%s: orphan_pages == 0" % name)
    # review console errors captured locally (int, not the live sentinel)
    sc.check(isinstance(sites["review"]["console_errors"], int),
             "review: console_errors captured (int, local playwright)")
    sc.check(sites["control-plane"]["console_errors"] == "not-captured (live/proxy)",
             "control-plane: console_errors not-captured (live/proxy)")
    # cross-site: ds/ design system NOT shared by all (control-plane diverges)
    sc.check(results["cross_site"]["ds_shared_by_all"] is False,
             "cross-site: ds/ design system not shared by all 4 (control-plane diverges)")
    sc.check(results["cross_site"]["ds_design_system"]["control-plane"] is False,
             "cross-site: control-plane does NOT ship the ds/ design system")


def print_summary(results):
    print()
    print("owner-002 websites-purpose-nav -- per-site summary (re-derived from snapshots)")
    print("=" * 92)
    hdr = ("%-14s %5s %4s %5s %5s %6s %7s %6s %6s %8s" %
           ("site", "mode", "pgs", "maxd", "avgd", "dead", "deadend", "forms", "task", "recrawl"))
    print(hdr)
    print("-" * 92)
    for name in SITES:
        s = results["sites"][name]
        print("%-14s %5s %4d %5d %5.2f %6d %7d %6d %5s %8s" % (
            name, s["crawl_mode"][:4], s["total_pages"], s["max_depth"],
            s["avg_depth"], s["dead_links"]["count"], s["dead_end_pages"]["count"],
            s["forms_total"],
            "%d/%d" % (s["task_battery"]["passed"], s["task_battery"]["total"]),
            "%.0f%%" % (s["recrawl_agreement"]["rate"] * 100)))
    print("-" * 92)
    print("broken assets:  " + "  ".join(
        "%s %d/%d" % (n, results["sites"][n]["broken_assets"]["count"],
                     results["sites"][n]["broken_assets"]["total_assets"]) for n in SITES))
    cs = results["cross_site"]
    print("ds/ design sys: " + "  ".join(
        "%s=%s" % (n, cs["ds_design_system"][n]) for n in SITES) +
        "  (shared by all: %s)" % cs["ds_shared_by_all"])
    print("console errors: " + "  ".join(
        "%s=%s" % (n, results["sites"][n]["console_errors"]) for n in SITES))
    print("=" * 92)


def main():
    sc = SelfCheck()
    results = build_results()
    run_selfchecks(sc, results)

    out = os.path.join(HERE, "results.json")
    with open(out, "w") as f:
        f.write(json.dumps(results, indent=2, sort_keys=True) + "\n")

    print_summary(results)
    print("wrote", os.path.relpath(out, HERE), "(canonical, sort_keys)")
    return sys.exit(sc.report())


if __name__ == "__main__":
    main()

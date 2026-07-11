# owner-002 — the four websites: purpose-fit, navigation health, cross-site consistency

Deterministic, self-checked, stdlib-only analysis of the fleet's four websites
(`menno420/websites`) — do they serve their stated purpose, is the navigation
healthy (dead links / orphans / dead-ends / broken assets), and are they
consistent with each other. Owner-direct request, 2026-07-11.

## Run

```
python3 sims/owner-002-websites-purpose-nav/analyze_nav.py
```

Exits 0, prints `SELF-CHECKS: 243 passed, 0 failed`, runs the whole computation
twice and asserts the two results are byte-identical, and writes `results.json`
(canonical, `sort_keys`) next to the script. The analysis over the committed
snapshots is its own byte-deterministic reproducibility check.

## Inputs (committed crawl snapshots — reproducible from data alone)

`runs/*.json` are four crawl snapshots of `menno420/websites` @ `31cfd9f`:

- **control-plane** — LIVE crawl of https://control-plane-production-abb0.up.railway.app
- **botsite** — LIVE crawl of https://botsite-production-cfd7.up.railway.app
- **dashboard** — LIVE crawl of https://dashboard-production-a91b.up.railway.app
- **review** — LOCAL build (not deployed): served with `uvicorn review.app:app`
  and crawled at `127.0.0.1`

Snapshot schema (per site): `{site, base_url, crawl_mode, head_sha,
purpose_quote, purpose_path, passes:[{pass, pages:[{url, depth, http_status,
title, out_links, external_links, forms, buttons, assets:[{url,status}],
is_dead_end, redirected_to, console_errors}]}], playwright, task_battery}`.

## Re-crawl (agreement-reproducible — live sites are NOT seed-deterministic)

```
python3 sims/owner-002-websites-purpose-nav/crawl_site.py <base_url> <site_name>
```

A live re-crawl is not byte-identical to a committed snapshot (a live site can
change); reproducibility for the crawl layer is defined as **re-crawl agreement**
(pass1 ≡ pass2, measured 100% in every snapshot). The byte-deterministic layer is
`analyze_nav.py` over the committed snapshots.

## Pinned source

`menno420/websites` @ `31cfd9f` (each snapshot carries its own `head_sha`;
review's full sha is `31cfd9f69a845515c0a7162fafa3457cc8e38468`).

## What it computes

Per site (re-derived from pass 1): total pages, max/avg depth, dead links
(HTTP ≥400, with the offending URLs), broken assets, orphan pages (inbound-graph:
depth>0 pages no other page links to), dead-end pages, console errors (from
Playwright where captured, else `not-captured (live/proxy)`), forms, task-battery
pass rate, and re-crawl agreement (pass1 vs pass2 url→status). Plus a cross-site
consistency block (shared `ds/` design system, nav-home rate, home titles).

See `REPORT.md` for the filled sections, the five-question validity gate answered
honestly, the limits, and the verdict. The harness helpers used (`SEEDS`,
`mean_sd`, `sweep`, `SelfCheck`, `determinism_bytes`) are vendor-copied into
`analyze_nav.py` — the sim never imports the harness at runtime.

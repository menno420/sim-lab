#!/usr/bin/env python3
"""owner-002 -- reference stdlib BFS crawler (makes the live crawl reproducible-by-recrawl).

Stdlib-only (urllib + html.parser). Same-origin breadth-first crawl with a depth
cap and a page cap, run TWICE, emitting the snapshot schema consumed by
analyze_nav.py. This is the documented re-crawl path for the three LIVE sites
(control-plane / botsite / dashboard) and the locally-served review build.

IMPORTANT -- reproducibility semantics: a live site is NOT seed-deterministic, so
a re-crawl is not byte-identical to a committed snapshot. Reproducibility for the
live layer is defined as RE-CRAWL AGREEMENT: the two in-run passes are compared
url->status and the snapshots measured 100% agreement. The byte-deterministic
layer is analyze_nav.py over the committed snapshots (one command, same result).

Emits per snapshot:
  { site, base_url, crawl_mode, head_sha, purpose_quote, purpose_path,
    passes:[ {pass, pages:[ {url, depth, http_status, title, out_links,
              external_links, forms, buttons, assets:[{url,status}],
              is_dead_end, redirected_to, console_errors} ]} ],
    playwright:{skipped:...}, task_battery:[] }

Console errors and the Playwright browser pass are OUT OF SCOPE for this stdlib
crawler (the snapshots' real-browser layer hit a Chromium/proxy wall on the live
sites -- see REPORT.md COMPARABLE-TO-LIVE); playwright is emitted as skipped.

Re-crawl command:
    python3 crawl_site.py <base_url> <site_name> [--max-pages N] [--max-depth D]

e.g.
    python3 crawl_site.py https://control-plane-production-abb0.up.railway.app control-plane
    python3 crawl_site.py http://127.0.0.1:8099 review --max-pages 200 --max-depth 3
"""

import argparse
import collections
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ASSET_TAGS = {"link": "href", "script": "src", "img": "src"}
DEFAULT_MAX_PAGES = 80
DEFAULT_MAX_DEPTH = 2
TIMEOUT = 20


class PageParser(HTMLParser):
    """Extract anchors, asset refs, form/button counts, and <title> from HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []       # raw href values from <a>
        self.assets = []      # raw src/href values from link/script/img
        self.forms = 0
        self.buttons = 0
        self._in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(d["href"])
        elif tag in ASSET_TAGS:
            ref = d.get(ASSET_TAGS[tag])
            # only stylesheets/scripts/images are assets we resolve
            if ref and (tag != "link" or "stylesheet" in (d.get("rel") or "")):
                self.assets.append(ref)
        elif tag == "form":
            self.forms += 1
        elif tag == "button":
            self.buttons += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()


def same_origin(base, url):
    b, u = urllib.parse.urlparse(base), urllib.parse.urlparse(url)
    return (u.scheme, u.netloc) == (b.scheme, b.netloc)


def fetch(url):
    """GET a url; return (status, final_url, body_text_or_None)."""
    req = urllib.request.Request(url, headers={"User-Agent": "owner-002-crawler/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            final = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            raw = resp.read()
            body = raw.decode("utf-8", "replace") if "text" in ctype or "json" in ctype else None
            return resp.status, final, body
    except urllib.error.HTTPError as e:
        return e.code, url, None
    except Exception:  # noqa: BLE001 -- network/timeout -> mark unreachable
        return 0, url, None


def head_status(url):
    """Cheap status probe for a link/asset (GET, status only)."""
    req = urllib.request.Request(url, headers={"User-Agent": "owner-002-crawler/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return None


def _skipped(url, skip_prefixes):
    """True if url starts with any caller-supplied skip prefix (e.g. a gated route)."""
    return any(url.startswith(pfx) for pfx in (skip_prefixes or ()))


def crawl_pass(base, max_pages, max_depth, status_cache, skip_prefixes=()):
    """One BFS pass. status_cache memoizes link/asset status within a pass.

    skip_prefixes: same-origin URL prefixes never fetched or enqueued (e.g. the
    401-gated /owner route -- GET-only crawler, we do not probe gated routes).
    """
    seen = set()
    pages = []
    q = collections.deque([(base, 0)])
    while q and len(pages) < max_pages:
        url, depth = q.popleft()
        if _skipped(url, skip_prefixes):
            continue
        canon = url.rstrip("/") if url != base else url
        if canon in seen:
            continue
        seen.add(canon)

        status, final, body = fetch(url)
        parser = PageParser()
        out_links, ext_count, assets = [], 0, []
        if body is not None and "<" in body:
            try:
                parser.feed(body)
            except Exception:  # noqa: BLE001 -- tolerate malformed HTML
                pass
            for href in parser.links:
                absu = urllib.parse.urljoin(final, href).split("#")[0]
                if not absu.startswith("http"):
                    continue
                if same_origin(base, absu):
                    out_links.append(absu)
                    if depth + 1 <= max_depth and not _skipped(absu, skip_prefixes):
                        q.append((absu, depth + 1))
                else:
                    ext_count += 1
            for ref in parser.assets:
                absu = urllib.parse.urljoin(final, ref)
                if not absu.startswith("http"):
                    continue
                if same_origin(base, absu):
                    if absu not in status_cache:
                        status_cache[absu] = head_status(absu)
                    assets.append({"url": absu, "status": status_cache[absu]})
                else:
                    assets.append({"url": absu, "status": None})  # external, not fetched

        out_links = sorted(set(out_links))
        is_dead_end = (status < 400) and (len(out_links) == 0)
        pages.append({
            "url": url,
            "depth": depth,
            "http_status": status,
            "title": parser.title,
            "out_links": out_links,
            "external_links": ext_count,
            "forms": parser.forms,
            "buttons": parser.buttons,
            "assets": assets,
            "is_dead_end": is_dead_end,
            "redirected_to": final if final != url else None,
            "console_errors": [],  # stdlib crawler cannot observe the JS console
        })
    return pages


def crawl(base, site, max_pages, max_depth, skip_prefixes=()):
    status_cache = {}
    passes = []
    for n in (1, 2):
        pages = crawl_pass(base, max_pages, max_depth, dict(status_cache), skip_prefixes)
        passes.append({"pass": n, "pages": pages})
    return {
        "site": site,
        "base_url": base,
        "crawl_mode": "local" if urllib.parse.urlparse(base).hostname in ("127.0.0.1", "localhost") else "live",
        "head_sha": "UNPINNED-recrawl",
        "purpose_quote": "",
        "purpose_path": "",
        "cap": {"pages": max_pages, "depth": max_depth},
        "skipped_prefixes": sorted(skip_prefixes),
        "passes": passes,
        "playwright": {"skipped": True,
                       "reason": "stdlib crawler does not run a browser; see REPORT.md"},
        "task_battery": [],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="stdlib BFS crawler -> owner-002 snapshot schema")
    ap.add_argument("base_url")
    ap.add_argument("site_name")
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    ap.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    ap.add_argument("--skip-prefix", action="append", default=[],
                    help="same-origin URL prefix never fetched/enqueued (repeatable; e.g. a gated route)")
    ap.add_argument("--out", default=None, help="output path (default: <site>.json)")
    args = ap.parse_args(argv)

    snap = crawl(args.base_url.rstrip("/"), args.site_name, args.max_pages,
                 args.max_depth, tuple(args.skip_prefix))
    out = args.out or (args.site_name + ".json")
    with open(out, "w") as f:
        f.write(json.dumps(snap, indent=2, sort_keys=True) + "\n")
    p1 = snap["passes"][0]["pages"]
    dead = sum(1 for p in p1 if p["http_status"] >= 400)
    print("crawled %s: %d pages (pass1), %d dead links -> %s"
          % (args.site_name, len(p1), dead, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

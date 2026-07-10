#!/usr/bin/env python3
"""VERDICT 005 - capability self-awareness probe: the LIVE / non-deterministic layer.

Method: measured prototype (ladder rung 2). This script is the NON-reproducible half:
it hits the real subprocess-plane environment (git, network, env) with a READ-ONLY
battery and freezes ONE json transcript per (seat, run-id) into runs/. Environment
probes are NOT seed-deterministic - a network status can flake, an env var can change -
so re-running yields a similar-but-not-identical transcript. Reproducibility for this
sim is defined as (a) agreement-rate bounds over N frozen runs and (b) byte-identical
output of analyze.py over the frozen runs; only analyze.py is bit-reproducible.

The AGENT-plane items (subagent-spawn, bash, github-mcp, triggers, ...) are TOOL-
AVAILABILITY facts of the RUNNING SEAT, not subprocess-testable, so probe.py emits them
as result=not-probeable/source=ledger; their real present/absent values are captured by
the per-seat inventory files (runs/agent_inventory_<seat>.json), written by the seat
itself, and diffed in analyze.py.

CLI: python3 probe.py --seat <coordinator|worker> --run-id <int> --out <path.json>
Stdlib only. Read-only. Never prints or records any secret VALUE (env token NAMES only).
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

TIMEOUT = 10

# ---- agent-plane item ids (availability enumerated by the seat, NOT by this subprocess) ----
AGENT_PLANE_ITEMS = [
    "ap:subagent-spawn",
    "ap:bash-shell",
    "ap:file-io",
    "ap:grep-glob",
    "ap:github-mcp",
    "ap:webagent-reply",
    "ap:send_later-selfbind",
    "ap:create_trigger-crosssession",
    "ap:workflow",
]


def _http_get(url, seat_hdr=None):
    """Read-only HTTP GET honoring HTTPS_PROXY. Returns (status_or_None, body_first_bytes, err)."""
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        opener = urllib.request.build_opener(handler)
    else:
        opener = urllib.request.build_opener()
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "verdict005-capability-probe"})
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            body = resp.read(240)
            return resp.status, body.decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read(240).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body, None
    except Exception as e:  # noqa: BLE001 - verbatim exception text is the evidence
        return None, "", "%s: %s" % (type(e).__name__, e)


def probe_git():
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=TIMEOUT)
        if r.returncode == 0:
            return {"result": "present", "detail": r.stdout.strip()}
        return {"result": "absent", "detail": "exit %d: %s" % (r.returncode, (r.stderr or "").strip())}
    except Exception as e:  # noqa: BLE001
        return {"result": "error", "detail": "%s: %s" % (type(e).__name__, e)}


def probe_raw_cross_repo():
    url = "https://raw.githubusercontent.com/menno420/idea-engine/main/control/outbox.md"
    status, body, err = _http_get(url)
    if err is not None:
        return {"result": "error", "detail": err}
    if status == 200:
        return {"result": "present", "detail": "200 (%d bytes head read)" % len(body)}
    return {"result": "wall", "detail": "%s" % status}


def probe_api_repo_object():
    url = "https://api.github.com/repos/menno420/sim-lab"
    status, body, err = _http_get(url)
    if err is not None:
        return {"result": "error", "detail": err}
    if status == 403:
        return {"result": "wall", "detail": "403 %s" % body[:120].replace("\n", " ")}
    if status == 200:
        return {"result": "present", "detail": "200"}
    return {"result": "absent", "detail": "%s" % status}


def probe_api_branch_protection():
    url = "https://api.github.com/repos/menno420/sim-lab/branches/main/protection"
    status, body, err = _http_get(url)
    if err is not None:
        return {"result": "error", "detail": err}
    if status == 403:
        return {"result": "wall", "detail": "403 %s (OA-001: REST branch-protection read walled)" % body[:120].replace("\n", " ")}
    return {"result": "wall" if status in (401, 404) else "absent",
            "detail": "%s (OA-001 note)" % status}


def probe_proxy_status():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    if not proxy:
        return {"result": "absent", "detail": "no HTTPS_PROXY in env"}
    url = "%s/__agentproxy/status" % proxy
    status, body, err = _http_get(url)
    if err is not None:
        return {"result": "error", "detail": "proxy set; status probe error: %s" % err}
    return {"result": "present", "detail": "%s reachable" % status}


def probe_env_token_names():
    pat = re.compile(r"(TOKEN|KEY|SECRET|PASSWORD|CRED)", re.IGNORECASE)
    names = sorted(k for k in os.environ.keys() if pat.search(k))
    if names:
        # NAMES ONLY - never any value.
        return {"result": "present", "detail": "%d matching env NAME(s) (values withheld): %s"
                % (len(names), ", ".join(names))}
    return {"result": "absent", "detail": "0 env names match (TOKEN|KEY|SECRET|PASSWORD|CRED)"}


SUBPROCESS_BATTERY = [
    ("sp:tool-git", probe_git),
    ("sp:net-raw-cross-repo", probe_raw_cross_repo),
    ("sp:net-api-repo-object", probe_api_repo_object),
    ("sp:net-api-branch-protection", probe_api_branch_protection),
    ("sp:net-proxy-status", probe_proxy_status),
    ("sp:env-token-names", probe_env_token_names),
]


def build_items(seat):
    items = []
    # --- subprocess plane (seat-invariant, read-only, source=probed) ---
    for iid, fn in SUBPROCESS_BATTERY:
        base = fn()
        items.append({
            "id": iid,
            "plane": "subprocess",
            "seat_variant": False,
            "result": base["result"],
            "detail": base["detail"],
            "source": "probed",
        })
    # sp:push-main - not read-only probeable (would be a side-effect); wall from the ledger.
    items.append({
        "id": "sp:push-main",
        "plane": "subprocess",
        "seat_variant": False,
        "result": "not-probeable",
        "detail": "not-probeable read-only: direct push to protected main would be a side-effect; "
                  "wall recorded by forward-only/PR-required convention (CONVENTIONS.md) + OA-001",
        "source": "ledger",
    })
    # --- agent plane (seat-variant tool-availability; not subprocess-testable) ---
    for iid in AGENT_PLANE_ITEMS:
        items.append({
            "id": iid,
            "plane": "agent",
            "seat_variant": True,
            "result": "not-probeable",
            "detail": "agent-plane: availability enumerated by the running seat, not by this "
                      "subprocess; see runs/agent_inventory_%s.json" % seat,
            "source": "ledger",
        })
    return items


def main():
    ap = argparse.ArgumentParser(description="VERDICT 005 capability self-probe (live layer).")
    ap.add_argument("--seat", required=True, choices=["coordinator", "worker"])
    ap.add_argument("--run-id", required=True, type=int)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    record = {
        "seat": args.seat,
        "run_id": args.run_id,
        "stamp": datetime.datetime.utcnow().isoformat() + "Z",
        "items": build_items(args.seat),
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")

    # stdout summary (subprocess plane only - the probed half)
    print("probe: seat=%s run=%d stamp=%s -> %s" % (args.seat, args.run_id, record["stamp"], args.out))
    for it in record["items"]:
        if it["plane"] == "subprocess":
            print("  %-28s %-13s %s" % (it["id"], it["result"], it["detail"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

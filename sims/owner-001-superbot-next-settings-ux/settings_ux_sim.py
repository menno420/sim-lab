#!/usr/bin/env python3
"""owner-001 -- superbot-next (NEW) vs superbot (OLD) settings/command/UX surface.

Deterministic, self-checked, stdlib-only analysis over committed inventories
(data/{next,old}/{settings,commands,panels}.json). Reads CODE STRUCTURE, not
users: every number here is measured from the static inventory or derived from
an explicitly-declared model. No network, no clock, no randomness except the
seeded combinability sampler (SEEDS below).

Pinned source SHAs (provenance of the inventories):
  superbot-next (NEW): 168ef8080347905766893fd92ae3be1ec2ebbc4c  (main)
  superbot     (OLD):  9f46cb7840cb2216a012002fe27feb342d45f480  (main)

Run:  python3 sims/owner-001-superbot-next-settings-ux/settings_ux_sim.py
Ends on sys.exit(sc.report()); writes results.json next to this file.

Harness helpers (SEEDS, mean_sd, sweep, SelfCheck, determinism_bytes) are
VENDOR-COPIED below -- sims stay self-contained and never import the harness.
"""

import collections
import itertools
import json
import os
import random
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Vendored harness helpers (copy of harness/simharness.py pieces we use).
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

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def determinism_bytes(sc, obj, label="determinism: stable canonical JSON"):
    s1 = json.dumps(obj, indent=2, sort_keys=True)
    s2 = json.dumps(obj, indent=2, sort_keys=True)
    return sc.check(s1 == s2, label)


# ---------------------------------------------------------------------------
# Inventory loading + shared parsers.
# ---------------------------------------------------------------------------

VERSIONS = ["next", "old"]  # next == NEW (superbot-next), old == OLD (superbot)
SHA = {
    "next": "168ef8080347905766893fd92ae3be1ec2ebbc4c",
    "old": "9f46cb7840cb2216a012002fe27feb342d45f480",
}

# read-site token: a .py path with an optional :line. Handles both the clean
# NEW "sb/domain/x.py:92" and the descriptive OLD "disbot/cogs/x.py (note)".
READSITE = re.compile(r"[A-Za-z0-9_./-]+\.py(?::\d+)?")
DOTPANEL = re.compile(r"panel:([A-Za-z0-9_.]+)")           # NEW dotted panel ref
CMDTOK = re.compile(r"command:([/!]?[A-Za-z0-9_?.\-]+)")  # opened_by command ref
PARENTPANEL = re.compile(r"parent-panel:([A-Za-z0-9_]+)")  # OLD parent ref


def load(version, kind):
    with open(os.path.join(HERE, "data", version, kind + ".json")) as f:
        return json.load(f)


def norm_cmd(name):
    """Canonical command id: drop leading /,! and case (NEW '/ai' == OLD 'ai')."""
    return name.lstrip("/!").strip().lower()


def read_sites(setting):
    """Normalized SET of read-site tokens for a setting (order-independent)."""
    out = set()
    for entry in setting.get("read_where") or []:
        out.update(READSITE.findall(entry))
    return frozenset(out)


def set_where_panels(setting):
    """Panel references named in a setting's set_where provenance string.

    NEW: 'command:/settings -> panel:ai settings (op)'  -> ['ai settings']
    OLD: 'panel:AIPanelView>Settings / panel:SubsystemSettingsView'
         -> ['AIPanelView', 'SubsystemSettingsView']
    Captures free-text panel names (may contain spaces); trims at ( ; / > .
    """
    sw = setting.get("set_where") or ""
    refs = []
    for m in re.finditer(r"panel:", sw):
        tail = sw[m.end():]
        # cut at the first delimiter that ends a panel name
        cut = len(tail)
        for d in ["(", ";", ">", " / ", "\n"]:
            i = tail.find(d)
            if i != -1:
                cut = min(cut, i)
        name = tail[:cut].strip()
        if name:
            refs.append(name)
    return refs


def is_master_toggle(setting):
    n = setting["name"].lower()
    return setting.get("type") == "bool" and (
        n.endswith("_enabled") or n.endswith("_enable") or n.endswith("enabled"))


def rename_key(name, subsystem):
    """Collapse subsystem prefix + separators so 'counters.bots_channel' and
    'counters_bots_channel' hash equal -- used only to FLAG rename candidates."""
    s = name.lower()
    for pre in (subsystem.lower() + ".", subsystem.lower() + "_"):
        if s.startswith(pre):
            s = s[len(pre):]
            break
    return re.sub(r"[^a-z0-9]", "", s)


# ---------------------------------------------------------------------------
# SECTION 1 -- inventory diff.
# ---------------------------------------------------------------------------

def inventory_diff(sc, settings, commands):
    res = {}

    # settings: match by exact name
    sn = {v: {s["name"]: s for s in settings[v]} for v in VERSIONS}
    new_names, old_names = set(sn["next"]), set(sn["old"])
    kept = sorted(new_names & old_names)
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    moved = sorted(
        [n for n in kept if sn["next"][n]["subsystem"] != sn["old"][n]["subsystem"]])
    moved_detail = {n: {"old_subsystem": sn["old"][n]["subsystem"],
                        "new_subsystem": sn["next"][n]["subsystem"]} for n in moved}

    # rename CANDIDATES (never asserted): added vs removed, same subsystem and
    # equal collapsed name key. The type LABEL frequently changed in the
    # refactor (e.g. 'str' -> 'binding:channel'), so type is recorded, not
    # required -- these are flags for human confirmation, not assertions.
    rc = []
    for a in added:
        sa = sn["next"][a]
        for r in removed:
            sr = sn["old"][r]
            if (sa["subsystem"] == sr["subsystem"]
                    and rename_key(a, sa["subsystem"]) == rename_key(r, sr["subsystem"])):
                rc.append({"new": a, "old": r, "subsystem": sa["subsystem"],
                           "new_type": sa["type"], "old_type": sr["type"],
                           "type_changed": sa["type"] != sr["type"],
                           "basis": "CANDIDATE ONLY: same subsystem, name equal "
                           "after separator/prefix normalization; not confirmed"})
    rc.sort(key=lambda d: (d["new"], d["old"]))

    res["settings"] = {
        "count_new": len(new_names), "count_old": len(old_names),
        "kept_count": len(kept), "added_count": len(added),
        "removed_count": len(removed),
        "kept": kept, "added": added, "removed": removed,
        "moved": moved, "moved_detail": moved_detail,
        "rename_candidates": rc,
    }
    sc.check(len(kept) + len(added) == len(new_names),
             "settings partition: kept+added == len(new)")
    sc.check(len(kept) + len(removed) == len(old_names),
             "settings partition: kept+removed == len(old)")

    # commands: raw totals + distinct-normalized partition + per-subsystem
    raw_new, raw_old = len(commands["next"]), len(commands["old"])
    cn = {v: set(norm_cmd(c["name"]) for c in commands[v]) for v in VERSIONS}
    ckept = sorted(cn["next"] & cn["old"])
    cadded = sorted(cn["next"] - cn["old"])
    cremoved = sorted(cn["old"] - cn["next"])
    sub_new = collections.Counter(c["subsystem"] for c in commands["next"])
    sub_old = collections.Counter(c["subsystem"] for c in commands["old"])
    subs = sorted(set(sub_new) | set(sub_old))
    per_sub = {s: {"new": sub_new.get(s, 0), "old": sub_old.get(s, 0),
                   "delta": sub_new.get(s, 0) - sub_old.get(s, 0)} for s in subs}
    res["commands"] = {
        "raw_total_new": raw_new, "raw_total_old": raw_old,
        "raw_delta": raw_new - raw_old,
        "distinct_new": len(cn["next"]), "distinct_old": len(cn["old"]),
        "distinct_kept": len(ckept), "distinct_added": len(cadded),
        "distinct_removed": len(cremoved),
        "distinct_delta": len(cn["next"]) - len(cn["old"]),
        "per_subsystem": per_sub,
        "added_names": cadded, "removed_names": cremoved,
    }
    sc.check(len(ckept) + len(cadded) == len(cn["next"]),
             "commands partition: kept+added == distinct(new)")
    sc.check(len(ckept) + len(cremoved) == len(cn["old"]),
             "commands partition: kept+removed == distinct(old)")
    return res


# ---------------------------------------------------------------------------
# SECTION 2 -- redundancy (measured from read_where).
# ---------------------------------------------------------------------------

def redundancy(sc, settings):
    out = {}
    for v in VERSIONS:
        st = settings[v]
        dead, display = [], []
        for s in st:
            rw = s.get("read_where") or []
            note = (s.get("notes") or "").upper()
            if not rw or "NO READER" in note:
                dead.append(s["name"])
                continue
            if all("panels.py" in r for r in rw):
                display.append(s["name"])
        dead.sort()
        display.sort()

        # duplicate-effect: identical read-site sets (global within version)
        by_rs = collections.defaultdict(list)
        for s in st:
            rs = read_sites(s)
            if rs:  # dead settings (empty) excluded from duplicate grouping
                by_rs[rs].append(s["name"])
        dup_groups = sorted(
            [sorted(names) for names in by_rs.values() if len(names) > 1],
            key=lambda g: (-len(g), g[0]))

        # subordinate/shadowed pairs (same subsystem, strict subset of a master)
        by_sub = collections.defaultdict(list)
        for s in st:
            by_sub[s["subsystem"]].append(s)
        subordinate = []
        for sub, group in by_sub.items():
            masters = [g for g in group if is_master_toggle(g) and read_sites(g)]
            for a in group:
                ra = read_sites(a)
                if not ra:
                    continue
                for m in masters:
                    if a["name"] == m["name"]:
                        continue
                    rm = read_sites(m)
                    if ra < rm:  # strict subset
                        subordinate.append({"subordinate": a["name"],
                                            "master": m["name"], "subsystem": sub})
        subordinate.sort(key=lambda d: (d["subsystem"], d["master"], d["subordinate"]))

        out[v] = {
            "dead": dead, "dead_count": len(dead),
            "display_only": display, "display_only_count": len(display),
            "duplicate_effect_groups": dup_groups,
            "duplicate_effect_group_count": len(dup_groups),
            "subordinate_pairs": subordinate,
            "subordinate_pair_count": len(subordinate),
        }
        # self-checks
        sc.check(not (set(dead) & set(display)),
                 "%s: dead and display-only are disjoint" % v)
        for name in dead:
            s = next(x for x in st if x["name"] == name)
            rw = s.get("read_where") or []
            note = (s.get("notes") or "").upper()
            sc.check((not rw) or ("NO READER" in note),
                     "%s: dead '%s' has empty read_where or NO READER note" % (v, name))
        for name in display:
            s = next(x for x in st if x["name"] == name)
            sc.check(all("panels.py" in r for r in s["read_where"]),
                     "%s: display-only '%s' reads only in panels.py" % (v, name))
    return out


# ---------------------------------------------------------------------------
# SECTION 3 -- combinability (structural co-read + seeded config-space model).
# ---------------------------------------------------------------------------

def combinability(sc, settings):
    out = {}
    for v in VERSIONS:
        by_sub = collections.defaultdict(list)
        for s in settings[v]:
            by_sub[s["subsystem"]].append(s)

        # 3a STRUCTURAL (robust, measured): per-subsystem co-read collapse.
        collapsed = {}
        for sub, group in sorted(by_sub.items()):
            buckets = collections.defaultdict(list)
            for s in group:
                rs = read_sites(s)
                if rs:
                    buckets[rs].append(s["name"])
            groups = sorted([sorted(names) for names in buckets.values()
                             if len(names) > 1], key=lambda g: (-len(g), g[0]))
            if groups:
                collapsed[sub] = groups

        # 3b SAMPLED demonstration (supporting, seeded). MODEL (declared, not
        # executed): dims = bool/enum settings in the subsystem, each a binary
        # coordinate (at-default=0 / enabled-or-non-default=1). Behavior
        # signature of a config vector = UNION of read-site sets of the
        # settings whose bit is 1. A subsystem where many distinct config
        # vectors collapse to the same signature has combinable dimensions.
        sampled = {}
        K = 256
        for sub, group in sorted(by_sub.items()):
            dims = [s for s in group if s.get("type") in ("bool", "enum")
                    and read_sites(s)]
            d = len(dims)
            if d < 2:
                continue
            rs_list = [read_sites(s) for s in dims]
            config_space = 2 ** d

            def signature(bits):
                sig = set()
                for i, bit in enumerate(bits):
                    if bit:
                        sig |= rs_list[i]
                return frozenset(sig)

            per_seed_ratio = []
            distinct_counts = []
            n_sampled_ref = None
            for seed in SEEDS:
                if config_space <= K:
                    vectors = list(itertools.product((0, 1), repeat=d))  # exhaustive
                else:
                    rng = random.Random(seed)
                    seen = set()
                    while len(seen) < K:
                        seen.add(tuple(rng.randint(0, 1) for _ in range(d)))
                    vectors = sorted(seen)
                n_sampled = len(vectors)
                sigs = {signature(vec) for vec in vectors}
                distinct = len(sigs)
                distinct_counts.append(distinct)
                per_seed_ratio.append(distinct / n_sampled)
                n_sampled_ref = n_sampled
                sc.check(distinct <= config_space,
                         "%s/%s: distinct_behaviors <= config_space" % (v, sub))
                sc.check(distinct <= n_sampled,
                         "%s/%s: distinct_behaviors <= n_sampled" % (v, sub))
            m, sd = mean_sd(per_seed_ratio)
            dm, dsd = mean_sd(distinct_counts)
            sampled[sub] = {
                "dims": d, "config_space": config_space,
                "n_sampled": n_sampled_ref,
                "distinct_behaviors_mean": dm, "distinct_behaviors_sd": dsd,
                "collapse_ratio_mean": m, "collapse_ratio_sd": sd,
                "fully_enumerated": config_space <= K,
            }
        out[v] = {"coread_collapsed_groups": collapsed, "sampled_config_space": sampled}
    return out


# ---------------------------------------------------------------------------
# SECTION 4 -- reachability graph (measured, rung 1).
# ---------------------------------------------------------------------------

SETTINGS_HUB_PANEL = {"next": "settings.hub", "old": "SettingsHubView"}
TOP_SETTINGS_CMD = "settings"  # normalized id present in both versions


def build_graph(sc, version, settings, commands, panels):
    """Directed graph. Nodes: ('cmd',id) ('panel',name) ('set',name).
    Edges (unit weight = one click): command->panel (opens), panel->panel
    (button navigation / parent-panel), panel->setting (set_where terminal),
    settings-hub->subsystem-panel (subsystem-select wiring)."""
    panel_names = set(p["panel"] for p in panels)
    cmd_ids = set(norm_cmd(c["name"]) for c in commands)
    adj = collections.defaultdict(set)
    nodes = set()

    def add_edge(a, b):
        if a == b:
            return  # never count a self-loop as a step
        adj[a].add(b)
        nodes.add(a)
        nodes.add(b)

    def resolve_panel(raw):
        x = raw.strip()
        if x in panel_names:
            return ("panel", x)
        xd = x.replace(" ", ".")
        if xd in panel_names:
            return ("panel", xd)
        return ("panel*", xd)  # synthesized (referenced but not in panels.json)

    for c in commands:
        nodes.add(("cmd", norm_cmd(c["name"])))
    for p in panels:
        nodes.add(("panel", p["panel"]))
    for s in settings:
        nodes.add(("set", s["name"]))

    # 1. command opens_panel (commands.json)
    for c in commands:
        op = c.get("opens_panel")
        if op:
            add_edge(("cmd", norm_cmd(c["name"])), resolve_panel(op))

    # 2. panels: opened_by (command / panel / parent-panel) + buttons
    for p in panels:
        pnode = ("panel", p["panel"])
        ob = p.get("opened_by")
        ob_text = " ; ".join(ob) if isinstance(ob, list) else (ob or "")
        for tok in CMDTOK.findall(ob_text):
            cid = norm_cmd(tok)
            if cid in cmd_ids:
                add_edge(("cmd", cid), pnode)
        for tok in DOTPANEL.findall(ob_text):
            if ("panel", tok) != pnode and tok in panel_names:
                add_edge(("panel", tok), pnode)
        for tok in PARENTPANEL.findall(ob_text):
            if tok in panel_names:
                add_edge(("panel", tok), pnode)
        for b in p.get("buttons") or []:
            if "->" not in b:
                continue
            segs = b.split("->")
            for seg in segs[1:]:
                # NEW dotted panel action
                for tok in DOTPANEL.findall(seg):
                    if tok in panel_names:
                        add_edge(pnode, ("panel", tok))
                # OLD View-name action: strip trailing "( ..." descriptor
                cand = seg.split("(")[0].strip()
                if cand in panel_names:
                    add_edge(pnode, ("panel", cand))

    # 3. panel -> setting from set_where terminal panel refs
    referenced = set()
    for s in settings:
        snode = ("set", s["name"])
        for raw in set_where_panels(s):
            pnode = resolve_panel(raw)
            referenced.add(pnode)
            add_edge(pnode, snode)

    # 4. settings-hub subsystem-select wiring: hub -> each referenced settings
    #    panel (the documented subsystem dropdown). Makes settings discoverable
    #    from the top-level /settings entry.
    hub = ("panel", SETTINGS_HUB_PANEL[version])
    if hub[1] in panel_names:
        for pnode in referenced:
            add_edge(hub, pnode)

    # no self-loops present
    for a in adj:
        sc.check(a not in adj[a], "%s: no self-loop at node %r" % (version, a))
    return nodes, adj


def bfs_dist(sources, adj):
    dist = {s: 0 for s in sources}
    q = collections.deque(sources)
    while q:
        u = q.popleft()
        for w in adj.get(u, ()):  # deterministic order below
            if w not in dist:
                dist[w] = dist[u] + 1
                q.append(w)
    return dist


def reachability(sc, settings, commands, panels):
    out = {}
    per_setting = {}  # version -> name -> steps (int or None)
    for v in VERSIONS:
        nodes, adj = build_graph(sc, v, settings[v], commands[v], panels[v])
        # sort adjacency for deterministic BFS traversal
        sadj = {u: sorted(ws) for u, ws in adj.items()}
        cmd_sources = sorted(n for n in nodes if n[0] == "cmd")
        dist_multi = bfs_dist(cmd_sources, sadj)
        # discoverability from single top-level settings command
        top = ("cmd", TOP_SETTINGS_CMD)
        dist_top = bfs_dist([top], sadj) if top in nodes else {}

        steps = {}
        reachable, unreachable = [], []
        multiplicity = {}
        for s in settings[v]:
            node = ("set", s["name"])
            d = dist_multi.get(node)
            if d is None:
                unreachable.append(s["name"])
                steps[s["name"]] = None
            else:
                reachable.append(s["name"])
                steps[s["name"]] = d
                sc.check(d >= 1, "%s: reachable '%s' steps>=1" % (v, s["name"]))
                # path multiplicity: how many distinct entry commands reach it
                cnt = 0
                for c in cmd_sources:
                    dc = bfs_dist([c], sadj).get(node)
                    if dc is not None:
                        cnt += 1
                multiplicity[s["name"]] = cnt
        per_setting[v] = steps
        reachable.sort()
        unreachable.sort()
        sc.check(not (set(reachable) & set(unreachable)),
                 "%s: reachable and unreachable disjoint" % v)

        vals = [steps[n] for n in reachable]
        dist_hist = dict(collections.Counter(vals))
        worst = sorted(reachable, key=lambda n: (-steps[n], n))[:10]
        worst_detail = [{"name": n, "steps": steps[n],
                         "subsystem": next(x["subsystem"] for x in settings[v]
                                           if x["name"] == n)} for n in worst]
        # discoverability
        disc = [s["name"] for s in settings[v]
                if ("set", s["name"]) in dist_top]
        # same-subsystem depth variance
        by_sub = collections.defaultdict(list)
        for n in reachable:
            sub = next(x["subsystem"] for x in settings[v] if x["name"] == n)
            by_sub[sub].append(steps[n])
        sub_var = {sub: (statistics.pvariance(ds) if len(ds) > 1 else 0.0)
                   for sub, ds in sorted(by_sub.items())}
        multi_gt1 = sorted(n for n, c in multiplicity.items() if c > 1)

        out[v] = {
            "total_settings": len(settings[v]),
            "reachable_count": len(reachable),
            "unreachable_count": len(unreachable),
            "unreachable": unreachable,
            "steps": steps,
            "avg_steps": round(statistics.mean(vals), 4) if vals else None,
            "median_steps": statistics.median(vals) if vals else None,
            "max_steps": max(vals) if vals else None,
            "distribution": {str(k): dist_hist[k] for k in sorted(dist_hist)},
            "worst10": worst_detail,
            "discoverability_from_top_count": len(disc),
            "discoverability_from_top_fraction": round(
                len(disc) / len(settings[v]), 4) if settings[v] else None,
            "path_multiplicity_gt1": multi_gt1,
            "path_multiplicity_gt1_count": len(multi_gt1),
            "subsystem_depth_variance": sub_var,
        }

    # CONSISTENCY across matched settings
    sn = {v: {s["name"] for s in settings[v]} for v in VERSIONS}
    matched = sorted(sn["next"] & sn["old"])
    shallower, deeper, same, incomparable = [], [], [], []
    per_matched = {}
    for n in matched:
        a = per_setting["next"][n]  # NEW
        b = per_setting["old"][n]   # OLD
        per_matched[n] = {"new": a, "old": b}
        if a is None or b is None:
            incomparable.append(n)
        elif a < b:
            shallower.append(n)
        elif a > b:
            deeper.append(n)
        else:
            same.append(n)
    out["consistency"] = {
        "matched_count": len(matched),
        "shallower_in_new": sorted(shallower),
        "deeper_in_new": sorted(deeper),
        "same": sorted(same),
        "incomparable": sorted(incomparable),
        "shallower_count": len(shallower),
        "deeper_count": len(deeper),
        "same_count": len(same),
        "incomparable_count": len(incomparable),
        "per_matched_steps": per_matched,
    }
    sc.check(len(shallower) + len(deeper) + len(same) + len(incomparable)
             == len(matched), "consistency partitions matched settings")

    # TASK BATTERY: first-alphabetical matched setting per subsystem present in
    # both, deterministic pick. Report cold-start clicks (nearest-entry steps).
    sub_new = {v: collections.defaultdict(list) for v in VERSIONS}
    subs_both = {}
    for s in settings["next"]:
        if s["name"] in matched:
            subs_both.setdefault(s["subsystem"], []).append(s["name"])
    tasks = []
    for sub in sorted(subs_both):
        pick = sorted(subs_both[sub])[0]
        a = per_setting["next"][pick]
        b = per_setting["old"][pick]
        tasks.append({"subsystem": sub, "setting": pick,
                      "clicks_new": a, "clicks_old": b,
                      "delta": (a - b) if (a is not None and b is not None) else None})
    new_clicks = [t["clicks_new"] for t in tasks if t["clicks_new"] is not None]
    old_clicks = [t["clicks_old"] for t in tasks if t["clicks_old"] is not None]
    out["task_battery"] = {
        "tasks": tasks,
        "mean_clicks_new": round(statistics.mean(new_clicks), 4) if new_clicks else None,
        "mean_clicks_old": round(statistics.mean(old_clicks), 4) if old_clicks else None,
        "mean_delta": (round(statistics.mean(new_clicks) - statistics.mean(old_clicks), 4)
                       if new_clicks and old_clicks else None),
    }
    return out


# ---------------------------------------------------------------------------
# SECTION 5 -- UX delta (measured proxies; signed deltas, regressions named).
# ---------------------------------------------------------------------------

def ux_delta(redun, reach):
    def m(v, key):
        return reach[v][key]

    metrics = {}

    def signed(name, new, old, better="lower"):
        delta = None
        if new is not None and old is not None:
            delta = round(new - old, 4)
        metrics[name] = {"new": new, "old": old, "delta": delta,
                         "better_direction": better}

    signed("total_settings", reach["next"]["total_settings"],
           reach["old"]["total_settings"], "n/a")
    signed("dead_settings", redun["next"]["dead_count"],
           redun["old"]["dead_count"], "lower")
    signed("display_only_settings", redun["next"]["display_only_count"],
           redun["old"]["display_only_count"], "lower")
    signed("mean_steps_to_reach", m("next", "avg_steps"), m("old", "avg_steps"),
           "lower")
    signed("median_steps_to_reach", m("next", "median_steps"),
           m("old", "median_steps"), "lower")
    signed("max_steps_to_reach", m("next", "max_steps"), m("old", "max_steps"),
           "lower")
    signed("discoverability_fraction",
           m("next", "discoverability_from_top_fraction"),
           m("old", "discoverability_from_top_fraction"), "higher")
    signed("unreachable_settings", m("next", "unreachable_count"),
           m("old", "unreachable_count"), "lower")
    signed("mean_task_battery_clicks", reach["task_battery"]["mean_clicks_new"],
           reach["task_battery"]["mean_clicks_old"], "lower")

    # regressions: a metric moved in the WORSE direction
    regressions = []
    for name, d in metrics.items():
        if d["delta"] is None or d["better_direction"] == "n/a":
            continue
        if d["better_direction"] == "lower" and d["delta"] > 0:
            regressions.append({"metric": name, "delta": d["delta"],
                                "new": d["new"], "old": d["old"]})
        if d["better_direction"] == "higher" and d["delta"] < 0:
            regressions.append({"metric": name, "delta": d["delta"],
                                "new": d["new"], "old": d["old"]})
    # per-task regressions (deeper in NEW)
    task_regressions = [t for t in reach["task_battery"]["tasks"]
                        if t["delta"] is not None and t["delta"] > 0]
    return {"metrics": metrics,
            "consistency_counts": {
                "shallower_in_new": reach["consistency"]["shallower_count"],
                "deeper_in_new": reach["consistency"]["deeper_count"],
                "same": reach["consistency"]["same_count"],
                "incomparable": reach["consistency"]["incomparable_count"]},
            "regressions": sorted(regressions, key=lambda d: d["metric"]),
            "task_regressions": task_regressions}


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------

def analyze(sc):
    settings = {v: load(v, "settings") for v in VERSIONS}
    commands = {v: load(v, "commands") for v in VERSIONS}
    panels = {v: load(v, "panels") for v in VERSIONS}

    results = {"meta": {"versions": {"new": "next", "old": "old"}, "sha": SHA,
                        "seeds": SEEDS}}
    results["inventory_diff"] = inventory_diff(sc, settings, commands)
    results["redundancy"] = redundancy(sc, settings)
    results["combinability"] = combinability(sc, settings)
    results["reachability"] = reachability(sc, settings, commands, panels)
    results["ux_delta"] = ux_delta(results["redundancy"], results["reachability"])
    return results


def main():
    sc = SelfCheck()
    results = analyze(sc)

    # determinism: a second independent analysis must be byte-identical.
    sc2 = SelfCheck()
    results2 = analyze(sc2)
    s1 = json.dumps(results, sort_keys=True)
    s2 = json.dumps(results2, sort_keys=True)
    sc.check(s1 == s2, "determinism: analysis byte-identical on re-run")
    determinism_bytes(sc, results)
    print("determinism: %s" % ("byte-identical on re-run"
                                if s1 == s2 else "DIVERGED"))

    out = os.path.join(HERE, "results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    print("results.json written (%d bytes)" % os.path.getsize(out))
    sys.exit(sc.report())


if __name__ == "__main__":
    main()

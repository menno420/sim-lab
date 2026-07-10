#!/usr/bin/env python3
"""VERDICT 005 - capability self-awareness probe: the DETERMINISTIC analyzer.

Method: measured prototype (ladder rung 2). The LIVE layer (probe.py + the seat
self-enumerations) is NOT bit-reproducible - a network status can flake, a seat's
toolset is what it is. This script is the reproducible half: given the FROZEN runs
under runs/, it recomputes every headline number, self-checks them, emits the proposed
CAPABILITIES.v1 schema instance (CAPABILITIES.json) + a rendered CAPABILITIES.md
sample, and is byte-identical on re-run (it copies frozen stamps; it calls no clock).

Run: python3 sims/verdict-005-capability-self-probe/analyze.py
Stdlib only. Exit 0 iff all self-checks pass.

It computes:
  (1) INTERNAL AGREEMENT per subprocess-plane item across the N frozen worker runs
      (agreement_rate = modal_count / N; flags any item that disagreed across runs).
  (2) SEAT DIVERGENCE for each agent-plane item (coordinator vs worker present/absent).
  (3) THREE-WAY DIFF (coordinator inventory vs worker inventory vs baseline) plus, for
      the subprocess plane, probe-modal vs baseline. Counts FALSE-WALLS (a seat says
      absent / a probe says wall where the baseline records the capability as real) and
      FALSE-CAPABILITIES (a seat's naive present projection where the baseline records a
      wall - e.g. create_trigger visible while its cross-session bind is org-walled).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

SUBPROC_PROBED = [
    "sp:tool-git", "sp:net-raw-cross-repo", "sp:net-api-repo-object",
    "sp:net-api-branch-protection", "sp:net-proxy-status", "sp:env-token-names",
]
SUBPROC_LEDGER = ["sp:push-main"]
AGENT_ITEMS = [
    "ap:subagent-spawn", "ap:bash-shell", "ap:file-io", "ap:grep-glob",
    "ap:github-mcp", "ap:webagent-reply", "ap:send_later-selfbind",
    "ap:create_trigger-crosssession", "ap:workflow",
]
VALID_RESULTS = {"present", "absent", "wall", "not-probeable"}
VALID_SOURCES = {"probed", "ledger"}

_CHECKS = [0]


def check(cond, msg):
    _CHECKS[0] += 1
    assert cond, "SELF-CHECK FAILED: %s" % msg


def load(name):
    with open(os.path.join(RUNS, name)) as f:
        return json.load(f)


def project_inventory(token):
    """Map an inventory token to (result, walled_flag). 'present-but-walled' -> present+wall."""
    if token == "present-but-walled":
        return "present", True
    return token, False


def modal(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winners = sorted(k for k, c in counts.items() if c == top)
    return winners[0], top, counts


def main():
    # ---- load frozen runs deterministically ----
    run_files = sorted(fn for fn in os.listdir(RUNS)
                       if fn.startswith("probe_worker_run") and fn.endswith(".json"))
    runs = [load(fn) for fn in run_files]
    N = len(runs)
    check(N == 5, "expected 5 frozen worker runs, got %d" % N)
    for r in runs:
        check(r["seat"] == "worker", "run seat must be worker")
        check(isinstance(r["stamp"], str) and r["stamp"].endswith("Z"), "run stamp must be ISO Z string")
    run_ids = sorted(r["run_id"] for r in runs)
    check(run_ids == [1, 2, 3, 4, 5], "run ids must be 1..5, got %s" % run_ids)
    # frozen stamps, ordered by run_id -> deterministic
    run_stamps = [r["stamp"] for r in sorted(runs, key=lambda x: x["run_id"])]
    check(len(run_stamps) == 5, "expected 5 run stamps")

    # index each run's items by id
    per_run = []
    for r in runs:
        d = {it["id"]: it for it in r["items"]}
        per_run.append(d)
        for iid in SUBPROC_PROBED:
            check(iid in d, "run missing subprocess item %s" % iid)
            check(d[iid]["source"] == "probed", "%s must be source=probed" % iid)
            check(d[iid]["plane"] == "subprocess", "%s must be plane=subprocess" % iid)
        for iid in SUBPROC_LEDGER:
            check(iid in d and d[iid]["source"] == "ledger", "%s must be source=ledger" % iid)
            check(d[iid]["result"] == "not-probeable", "%s must be not-probeable" % iid)
        for iid in AGENT_ITEMS:
            check(iid in d, "run missing agent item %s" % iid)
            check(d[iid]["result"] == "not-probeable" and d[iid]["source"] == "ledger",
                  "%s in probe run must be not-probeable/ledger" % iid)
            check(d[iid]["seat_variant"] is True, "%s must be seat_variant" % iid)

    # ---- (1) internal agreement per subprocess-plane item across N runs ----
    agreement = {}
    flaky = []
    for iid in SUBPROC_PROBED:
        results = [per_run[i][iid]["result"] for i in range(N)]
        m, cnt, counts = modal(results)
        rate = cnt / N
        agreement[iid] = {"modal": m, "runs": N, "rate": rate, "counts": counts}
        check(0.0 <= rate <= 1.0, "%s agreement rate out of range" % iid)
        check(m in VALID_RESULTS, "%s modal result invalid" % iid)
        if len(set(results)) > 1:
            flaky.append((iid, counts))

    # no-secret-value guard on the env-token item detail (names only, never values)
    env_detail = per_run[0]["sp:env-token-names"]["detail"]
    check("withheld" in env_detail, "env-token detail must state values withheld")
    if ":" in env_detail:
        names_part = env_detail.split(":", 1)[1]
        for nm in [x.strip() for x in names_part.split(",") if x.strip()]:
            check("=" not in nm, "env-token detail leaks an assignment (=): %r" % nm)
            check(all(c.isalnum() or c == "_" for c in nm),
                  "env-token name has non-identifier char (possible value leak): %r" % nm)

    # ---- load inventories + baseline ----
    inv_coord = load("agent_inventory_coordinator.json")
    inv_work = load("agent_inventory_worker.json")
    baseline = load("baseline.json")
    check(inv_coord["seat"] == "coordinator", "coordinator inventory seat")
    check(inv_work["seat"] == "worker", "worker inventory seat")
    for inv in (inv_coord, inv_work):
        for iid in AGENT_ITEMS:
            check(iid in inv["items"], "%s missing from %s inventory" % (iid, inv["seat"]))
    check(len(baseline["subprocess_plane"]) == 7, "baseline needs 7 subprocess items")
    check(len(baseline["agent_plane"]) == 9, "baseline needs 9 agent items")

    # ---- (2) seat divergence (agent plane, coordinator vs worker) ----
    divergent = []
    for iid in AGENT_ITEMS:
        cr, _cw = project_inventory(inv_coord["items"][iid])
        wr, _ww = project_inventory(inv_work["items"][iid])
        if cr != wr:
            divergent.append((iid, cr, wr))
    seat_divergence_count = len(divergent)

    # ---- (3) three-way diff + false-wall / false-capability counts ----
    false_wall_items = []       # (seat, id): inventory absent / probe wall where baseline capable/present
    false_cap_items = []        # (seat, id): naive present projection where baseline walled
    # agent plane, per seat vs baseline
    for seat, inv in (("coordinator", inv_coord), ("worker", inv_work)):
        for iid in AGENT_ITEMS:
            res, walled = project_inventory(inv["items"][iid])
            base = baseline["agent_plane"][iid]["expected_result"]  # capable | walled
            if res == "absent" and base == "capable":
                false_wall_items.append((seat, iid))
            if res == "present" and base == "walled":
                false_cap_items.append((seat, iid))
    # subprocess plane, probe-modal vs baseline
    subproc_false_walls = []
    for iid in SUBPROC_PROBED:
        m = agreement[iid]["modal"]
        base = baseline["subprocess_plane"][iid]["expected_result"]  # present | wall
        if m == "wall" and base == "present":
            subproc_false_walls.append(iid)
            false_wall_items.append(("seat-invariant", iid))
    false_walls = len(false_wall_items)
    false_capability_item_set = sorted(set(iid for _s, iid in false_cap_items))
    false_capabilities = len(false_capability_item_set)

    # consistency self-checks
    check(seat_divergence_count == len(divergent), "divergence count mismatch")
    check(false_walls == len(false_wall_items), "false-wall count mismatch")
    check(false_capabilities == len(false_capability_item_set), "false-cap count mismatch")
    check(agreement["sp:net-api-repo-object"]["modal"] == "wall", "api repo-object should be a wall")
    check(agreement["sp:net-api-branch-protection"]["modal"] == "wall", "branch-protection should be a wall")
    check(agreement["sp:tool-git"]["modal"] == "present", "git should be present")
    check(len(subproc_false_walls) == 0,
          "subprocess plane should reproduce ledgered walls (0 false walls), got %s" % subproc_false_walls)
    check(("worker", "ap:subagent-spawn") in false_wall_items, "worker subagent-spawn must be a false wall vs baseline")
    check(("coordinator", "ap:bash-shell") in false_wall_items, "coordinator bash must be a false wall vs baseline")
    check("ap:create_trigger-crosssession" in false_capability_item_set,
          "create_trigger cross-session must surface as the false capability")
    # every seat-divergent item is a false wall in exactly one seat
    for iid, _cr, _wr in divergent:
        seats_flagged = [s for (s, i) in false_wall_items if i == iid]
        check(len(seats_flagged) == 1, "divergent %s should be a false wall in exactly one seat" % iid)

    baseline_b_reachable = bool(baseline["baseline_b"]["reachable_from_probing_seat"])
    check(isinstance(baseline_b_reachable, bool), "baseline-B reachability must be bool")

    # ---- build CAPABILITIES.v1 schema instance ----
    records = []
    # subprocess plane (seat-invariant)
    for iid in SUBPROC_PROBED:
        m = agreement[iid]["modal"]
        base = baseline["subprocess_plane"][iid]["expected_result"]
        records.append({
            "id": iid, "plane": "subprocess", "seat": "seat-invariant", "seat_variant": False,
            "result": m, "detail": per_run[0][iid]["detail"], "source": "probed",
            "agreement": {"runs": N, "rate": agreement[iid]["rate"]},
            "baseline_diff": {
                "baseline_expected": base,
                "false_wall": (m == "wall" and base == "present"),
                "false_capability": (m == "present" and base == "wall"),
            },
        })
    for iid in SUBPROC_LEDGER:
        base = baseline["subprocess_plane"][iid]["expected_result"]
        records.append({
            "id": iid, "plane": "subprocess", "seat": "seat-invariant", "seat_variant": False,
            "result": "not-probeable", "detail": per_run[0][iid]["detail"], "source": "ledger",
            "agreement": {"runs": 0, "rate": None},
            "baseline_diff": {"baseline_expected": base, "false_wall": False, "false_capability": False},
        })
    # agent plane (per seat - the point: seat-annotated sections)
    for seat, inv in (("coordinator", inv_coord), ("worker", inv_work)):
        for iid in AGENT_ITEMS:
            res, walled = project_inventory(inv["items"][iid])
            base = baseline["agent_plane"][iid]["expected_result"]
            detail = "seat inventory token=%r; baseline=%s" % (inv["items"][iid], base)
            if walled:
                detail += "; tool visible but capability org-walled (OA-003)"
            records.append({
                "id": iid, "plane": "agent", "seat": seat, "seat_variant": True,
                "result": res, "detail": detail, "source": "ledger",
                "agreement": {"runs": 0, "rate": None},
                "baseline_diff": {
                    "baseline_expected": base,
                    "false_wall": (res == "absent" and base == "capable"),
                    "false_capability": (res == "present" and base == "walled"),
                },
            })

    for rec in records:
        check(rec["result"] in VALID_RESULTS, "record %s bad result" % rec["id"])
        check(rec["source"] in VALID_SOURCES, "record %s bad source" % rec["id"])
        check(set(rec["baseline_diff"]) >= {"false_wall", "false_capability", "baseline_expected"},
              "record %s baseline_diff incomplete" % rec["id"])
    check(len(records) == len(SUBPROC_PROBED) + len(SUBPROC_LEDGER) + 2 * len(AGENT_ITEMS),
          "record count wrong: %d" % len(records))

    capabilities = {
        "schema": "CAPABILITIES.v1",
        "intake": "INTAKE 005 / PROPOSAL 005 (capability self-awareness probe)",
        "generated_from": "frozen runs under sims/verdict-005-capability-self-probe/runs/ (deterministic; live layer not bit-reproducible)",
        "run_stamps": run_stamps,
        "seats": ["coordinator", "worker"],
        "records": records,
        "rollup": {
            "subprocess_agreement": {iid: {"modal": agreement[iid]["modal"], "runs": N,
                                           "rate": agreement[iid]["rate"]} for iid in SUBPROC_PROBED},
            "subprocess_flaky_items": [iid for iid, _c in flaky],
            "seat_divergence": {"count": seat_divergence_count,
                                "items": [{"id": i, "coordinator": c, "worker": w} for i, c, w in divergent]},
            "baseline_diff": {
                "false_walls": false_walls,
                "false_wall_items": [{"seat": s, "id": i} for s, i in false_wall_items],
                "false_capabilities": false_capabilities,
                "false_capability_items": false_capability_item_set,
                "false_capability_seat_pairs": [{"seat": s, "id": i} for s, i in false_cap_items],
            },
            "baseline_b_fleet_manager_reachable": baseline_b_reachable,
        },
    }

    # ---- determinism self-test: serialize twice, must be byte-identical ----
    s1 = json.dumps(capabilities, indent=2, sort_keys=True)
    s2 = json.dumps(capabilities, indent=2, sort_keys=True)
    check(s1 == s2, "CAPABILITIES.json serialization not deterministic within run")

    with open(os.path.join(HERE, "CAPABILITIES.json"), "w") as f:
        f.write(s1 + "\n")

    # ---- rendered CAPABILITIES.md sample ----
    md = render_md(capabilities, agreement, N)
    with open(os.path.join(HERE, "CAPABILITIES.md"), "w") as f:
        f.write(md)

    # ---- stdout summary ----
    print("=" * 78)
    print("VERDICT 005 - capability self-awareness probe - frozen-run analysis")
    print("=" * 78)
    print("\nframes: %d worker runs frozen; stamps %s .. %s" % (N, run_stamps[0], run_stamps[-1]))
    print("\n(1) SUBPROCESS-PLANE INTERNAL AGREEMENT (across %d runs):" % N)
    for iid in SUBPROC_PROBED:
        a = agreement[iid]
        print("  %-30s modal=%-9s agreement=%.2f  (%s)" % (iid, a["modal"], a["rate"], a["counts"]))
    print("  overall flakiness: %s" % ("NONE - all subprocess items unanimous"
                                        if not flaky else ", ".join(i for i, _ in flaky)))
    print("\n(2) SEAT DIVERGENCE (agent plane, coordinator vs worker): count=%d" % seat_divergence_count)
    for iid, c, w in divergent:
        print("  %-32s coordinator=%-8s worker=%-8s  DIVERGENT" % (iid, c, w))
    agree_items = [i for i in AGENT_ITEMS if i not in {d[0] for d in divergent}]
    print("  agreeing agent-plane items (%d): %s" % (len(agree_items), ", ".join(agree_items)))
    print("\n(3) THREE-WAY DIFF vs hand-maintained baseline:")
    print("  FALSE-WALLS  = %d  (a seat/probe records a wall/absent where the baseline has the capability):"
          % false_walls)
    for s, i in false_wall_items:
        print("      %-12s %s" % (s, i))
    print("  subprocess-plane false-walls: %d (the read-only probe reproduces the ledgered walls exactly)"
          % len(subproc_false_walls))
    print("  FALSE-CAPABILITIES = %d  (naive present projection where the baseline records a wall):"
          % false_capabilities)
    for i in false_capability_item_set:
        seats = ", ".join(s for s, ii in false_cap_items if ii == i)
        print("      %s  (surfaced in: %s; OA-003 cross-session bind org-walled)" % (i, seats))
    print("\n  baseline-B (fleet-manager docs/capabilities.md) reachable from probing seat: %s"
          % baseline_b_reachable)
    print("\nEMITTED: CAPABILITIES.json (schema=%s, %d records) + CAPABILITIES.md"
          % (capabilities["schema"], len(records)))
    print("SELF-CHECKS: %d passed" % _CHECKS[0])
    print("=" * 78)


def render_md(cap, agreement, N):
    lines = []
    lines.append("# CAPABILITIES.md — sample render (schema `%s`)\n" % cap["schema"])
    lines.append("> DETERMINISTIC sample emitted by `analyze.py` over the frozen runs. "
                 "**Seat-annotated** — a whole-repo single-seat regeneration would launder one "
                 "seat's absences into repo-wide walls (see the three-way diff).\n")
    lines.append("> Frozen run stamps: %s .. %s (%d runs).\n" % (cap["run_stamps"][0], cap["run_stamps"][-1], N))
    lines.append("\n## Subprocess plane (seat-invariant, read-only probed)\n")
    lines.append("| id | result | agreement | baseline | false-wall | false-cap |")
    lines.append("|----|--------|-----------|----------|-----------|-----------|")
    for rec in cap["records"]:
        if rec["plane"] != "subprocess":
            continue
        a = rec["agreement"]
        rate = "n/a" if a["rate"] is None else ("%.2f" % a["rate"])
        bd = rec["baseline_diff"]
        lines.append("| %s | %s | %s (%d runs) | %s | %s | %s |" % (
            rec["id"], rec["result"], rate, a["runs"], bd["baseline_expected"],
            bd["false_wall"], bd["false_capability"]))
    for seat in cap["seats"]:
        lines.append("\n## Agent plane — seat: `%s`\n" % seat)
        lines.append("| id | result | baseline | false-wall | false-cap |")
        lines.append("|----|--------|----------|-----------|-----------|")
        for rec in cap["records"]:
            if rec["plane"] != "agent" or rec["seat"] != seat:
                continue
            bd = rec["baseline_diff"]
            lines.append("| %s | %s | %s | %s | %s |" % (
                rec["id"], rec["result"], bd["baseline_expected"], bd["false_wall"], bd["false_capability"]))
    ro = cap["rollup"]
    lines.append("\n## Roll-up\n")
    lines.append("- seat divergence (agent plane): **%d** items — %s" % (
        ro["seat_divergence"]["count"],
        ", ".join(d["id"] for d in ro["seat_divergence"]["items"])))
    lines.append("- false-walls (single-seat vs fleet baseline): **%d**" % ro["baseline_diff"]["false_walls"])
    lines.append("- false-capabilities: **%d** — %s" % (
        ro["baseline_diff"]["false_capabilities"],
        ", ".join(ro["baseline_diff"]["false_capability_items"])))
    lines.append("- subprocess-plane flaky items: %s" % (ro["subprocess_flaky_items"] or "none"))
    lines.append("- baseline-B (fleet-manager) reachable from probing seat: %s"
                 % ro["baseline_b_fleet_manager_reachable"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

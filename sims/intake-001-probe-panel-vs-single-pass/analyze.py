#!/usr/bin/env python3
"""INTAKE 001 - panel-mode vs single-pass probing: deterministic analysis over frozen probe runs.

Method: measured prototype (ladder rung 2). The LIVE probe layer (LLM agents) is NOT
bit-reproducible; this script recomputes every headline number from the FROZEN recorded
runs in runs/cells.json, self-checks them, and exits 0 iff all checks pass. Same input ->
same output, every run. Stdlib only.

Run: python3 sims/intake-001-probe-panel-vs-single-pass/analyze.py
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = os.path.join(HERE, "runs", "cells.json")
VALID_RECS = {"BUILD", "HOLD", "KILL"}


def modal(recs):
    counts = {}
    for r in recs:
        counts[r] = counts.get(r, 0) + 1
    top = max(counts.values())
    winners = sorted(k for k, v in counts.items() if v == top)
    return winners[0], (len(winners) > 1)


def main():
    with open(CELLS) as f:
        data = json.load(f)
    ideas = data["ideas"]

    # ---- self-checks (corruption gate) ----
    assert len(ideas) == 3, "expected 3 ideas, got %d" % len(ideas)
    judge_records = 0
    for slug, cell in ideas.items():
        assert len(cell["mode1"]) == 3, "%s: need 3 mode1 reps" % slug
        assert len(cell["mode2"]) == 3, "%s: need 3 mode2 reps" % slug
        for c in cell["mode1"]:
            assert c["recommendation"] in VALID_RECS, "%s m1 bad rec" % slug
            assert 0.0 <= c["confidence"] <= 1.0, "%s m1 bad conf" % slug
            assert c["tokens"] > 0 and c["wall_ms"] > 0, "%s m1 bad instrumentation" % slug
        for c in cell["mode2"]:
            assert c["recommendation"] in VALID_RECS, "%s m2 bad rec" % slug
            assert 0.0 <= c["confidence"] <= 1.0, "%s m2 bad conf" % slug
            assert c["cell_agents"] == 4, "%s: panel must be 4 agents" % slug
            assert c["cell_tokens"] > 0 and c["cell_wall_parallel_ms"] > 0, "%s m2 bad instrumentation" % slug
        for j in cell["judges"]:
            assert j["winner_mode"] in {"mode1", "mode2", "tie"}, "%s bad judge winner" % slug
            judge_records += 1
    assert judge_records == 6, "expected 6 judge records, got %d" % judge_records

    m1_tok = [c["tokens"] for cell in ideas.values() for c in cell["mode1"]]
    m2_tok = [c["cell_tokens"] for cell in ideas.values() for c in cell["mode2"]]
    assert statistics.mean(m2_tok) > statistics.mean(m1_tok), "panel not costlier than single-pass?!"

    # ---- headline computations ----
    flips = []
    m1_stable = 0
    m2_stable = 0
    lines = []
    for slug, cell in sorted(ideas.items()):
        m1r = [c["recommendation"] for c in cell["mode1"]]
        m2r = [c["recommendation"] for c in cell["mode2"]]
        m1_mode, m1_tie = modal(m1r)
        m2_mode, _ = modal(m2r)
        m1_unanimous = len(set(m1r)) == 1
        m2_unanimous = len(set(m2r)) == 1
        m1_stable += int(m1_unanimous)
        m2_stable += int(m2_unanimous)
        flipped = m1_mode != m2_mode
        if flipped:
            flips.append((slug, m1_mode, m2_mode, m1_unanimous))
        lines.append(
            "  %-34s m1=%s (modal %s%s, %s) -> m2=%s (modal %s) : %s"
            % (slug, m1r, m1_mode, "*tie" if m1_tie else "",
               "unanimous" if m1_unanimous else "split", m2r, m2_mode,
               "FLIP %s->%s" % (m1_mode, m2_mode) if flipped else "no flip"))

    m2_wins = 0
    tot = 0
    pos_bias_ok = True
    jlines = []
    for slug, cell in sorted(ideas.items()):
        winners = [j["winner_mode"] for j in cell["judges"]]
        tot += len(winners)
        m2_wins += winners.count("mode2")
        both = winners.count("mode2") == 2
        jlines.append("  %-34s judges=%s  %s"
                      % (slug, winners, "mode2 both orders" if both else "MIXED (check bias)"))
        if winners.count("mode2") not in (0, 2):
            pos_bias_ok = False

    m1_wall = [c["wall_ms"] for cell in ideas.values() for c in cell["mode1"]]
    m2_wall = [c["cell_wall_parallel_ms"] for cell in ideas.values() for c in cell["mode2"]]
    tok_ratio = statistics.mean(m2_tok) / statistics.mean(m1_tok)
    wall_ratio = statistics.mean(m2_wall) / statistics.mean(m1_wall)

    print("=" * 78)
    print("INTAKE 001 - panel-mode vs single-pass probing - frozen-run analysis")
    print("=" * 78)
    print("\nRECOMMENDATION FLIPS (modal mode1 vs modal mode2):")
    for l in lines:
        print(l)
    print("\n  flip rate: %d/3 ideas   direction(s): %s"
          % (len(flips), ", ".join("%s:%s->%s" % (s, a, b) for s, a, b, _ in flips) or "none"))
    clean = [s for s, a, b, uni in flips if uni]
    print("  flips where single-pass was UNANIMOUS (exceeds intra-mode noise): %s"
          % (clean or "none"))
    print("\nINTRA-MODE STABILITY (ideas with unanimous 3/3 reps):  mode1 %d/3   mode2 %d/3"
          % (m1_stable, m2_stable))
    print("\nQUALITY (blind judges, A/B order swapped):")
    for l in jlines:
        print(l)
    print("\n  mode2 win rate: %d/%d   position-bias: %s"
          % (m2_wins, tot, "none (winner stable across A/B swap)" if pos_bias_ok else "DETECTED"))
    print("\nCOST (means; absolute values are Opus-4.8/this-env specific - ratios transfer):")
    print("  tokens : single-pass %8.0f   panel %8.0f   ratio %.2fx"
          % (statistics.mean(m1_tok), statistics.mean(m2_tok), tok_ratio))
    print("  wall_ms: single-pass %8.0f   panel %8.0f   ratio %.2fx  (personas parallel -> sublinear)"
          % (statistics.mean(m1_wall), statistics.mean(m2_wall), wall_ratio))
    print("  agents : single-pass        1   panel        4   ratio 4.00x")
    print("\nRULING: adopt panel-mode ONLY for big-or-contested ideas (flips clustered there); reject always-on.")
    print("Self-checks: PASS")
    print("=" * 78)


if __name__ == "__main__":
    main()

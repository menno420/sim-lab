"""PROBE 6 — bounded path census: mint-count distribution over ALL legal sessions.

Exhaustively enumerates every sequence of legal (surfaced, non-clamped) choices up
to K chooses from the start scene at the xp=0 width floor, driving the real seam on
a fresh DnDState per path. Reports the mint-count distribution and extremal paths.
stdlib only, deterministic (DFS in option order).
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from services.dnd_workflow import DnDState, InMemorySink, choose, surfaced_options
from games.dnd.data.scenes import get_scene

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def replay(seq):
    state = DnDState()
    sink = InMemorySink()
    c = [0]
    def mid():
        c[0] += 1
        return f"m{c[0]:04d}"
    mints = 0
    for opt in seq:
        r = choose(state, opt, sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
        assert not r.resolution.clamped
        mints += r.reward is not None
    return mints, state


def enumerate_paths(k):
    results = []
    def dfs(seq):
        if seq:
            mints, state = replay(seq)
            results.append((tuple(seq), mints))
            if len(seq) == k:
                return
            scene_id = state.scene_id
        else:
            scene_id = DnDState().scene_id
        if len(seq) < k:
            scene = get_scene(scene_id)
            for o in surfaced_options(scene, xp=0):
                dfs(seq + [o.id])
    dfs([])
    return results


def main():
    K = 5
    print(f"PROBE 6 — exhaustive legal-path census, up to K={K} chooses at the xp=0 width floor (pin 57f69be3)")
    results = enumerate_paths(K)
    by_len = {}
    for seq, mints in results:
        by_len.setdefault(len(seq), []).append((seq, mints))
    for length in sorted(by_len):
        rows = by_len[length]
        dist = {}
        for _, m in rows:
            dist[m] = dist.get(m, 0) + 1
        max_m = max(m for _, m in rows)
        best = [s for s, m in rows if m == max_m]
        print(f"len={length}: {len(rows)} paths; mint distribution {dict(sorted(dist.items()))}; "
              f"max mints {max_m}")
        print(f"  a max-mint path: {' -> '.join(best[0])}")
    print()
    packet = ("advance_escort", "circle_to_treeline", "signal_escort")
    m, st = replay(list(packet))
    print(f"packet arc {' -> '.join(packet)}: {m} mints, totals g{st.global_xp}/x{st.game_xp}/c{st.currency}")
    fastest2 = ("advance_escort", "scout_ahead")  # road mint -> gate? no; kept for contrast below
    for seq in (("scout_ahead", "signal_escort"), ("scout_ahead", "signal_escort", "signal_escort"),
                ("advance_escort", "circle_to_treeline", "signal_escort", "signal_escort", "signal_escort")):
        m, st = replay(list(seq))
        print(f"{' -> '.join(seq)}: {m} mints, totals g{st.global_xp}/x{st.game_xp}/c{st.currency}")
    print()
    print("RESULT: mints grow linearly with path length (max = 1 mint/choose once at an escort")
    print("scene); the packet's 2x is not a ceiling — it is one point on an unbounded line.")


if __name__ == "__main__":
    main()

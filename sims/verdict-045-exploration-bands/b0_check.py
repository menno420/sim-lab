#!/usr/bin/env python3
"""B0 validity gate — VERDICT 045 (exploration reward bands, ORDER 006 item 7).

Re-derives every constant the order and the recon packet QUOTE from the
byte-copied pinned modules under ``engine/`` and FAILS LOUDLY (exit 1, named
check) on any mismatch. No ruling may be read before this gate exits 0.

Checks:
  B0.0  sha256 of every byte-copied file matches engine/MANIFEST.json
  B0.1  TIER_CAPS exactly tier I (5,25,10) · II (10,60,25) · III (20,120,50),
        every bundle capability=None (rewards carry no capability grant field
        value; capability unlocks are play-only per the catalog docstring)
  B0.2  GLOBAL_MAX exactly (20,120,50)
  B0.3  catalog docstring carries the D-0005/D-0008 placeholder note and the
        play-only capability line verbatim
  B0.4  survival TUNABLES exactly Easy (60,10,1) · Medium (50,15,1) ·
        Hard (40,20,1) and the Easy ≡ mining-bar identity holds BY IMPORT
        (Easy fields are energy.MAX_ENERGY / REGEN_SECONDS / DIG_COST)
  B0.5  mining bar exactly MAX_ENERGY=60, REGEN_SECONDS=10, DIG_COST=1
  B0.6  RewardBundle field semantics: (global_xp, game_xp, currency,
        capability=None) — the three TIER_CAPS numbers are global-XP /
        game-XP / currency in that order
  B0.7  RewardTier semantics: I="casual", II="standard", III="prestige"
        (models.py inline comments — read from source text)

stdlib-only, hermetic (reads only ./engine). Run:
    python3 sims/verdict-045-exploration-bands/b0_check.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engine"

_FAILED: list[str] = []
_PASSED = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _PASSED
    if ok:
        _PASSED += 1
        print(f"  PASS {name}")
    else:
        _FAILED.append(name)
        print(f"  FAIL {name} {detail}")


def main() -> int:
    # --- B0.0 manifest re-verification (before any import) ---
    manifest = json.loads((ENGINE / "MANIFEST.json").read_text())
    for rel, want in manifest["files"].items():
        got = hashlib.sha256((ENGINE / rel).read_bytes()).hexdigest()
        check(f"B0.0 sha256 {rel}", got == want, f"got={got} want={want}")

    sys.path.insert(0, str(ENGINE))
    from games.exploration.quest import catalog  # noqa: E402
    from games.exploration.quest.models import RewardBundle, RewardTier  # noqa: E402
    from games.exploration.survival.difficulty import (  # noqa: E402
        TUNABLES,
        Difficulty,
    )
    from games.mining.core import energy  # noqa: E402

    # --- B0.1 TIER_CAPS exact ---
    want_caps = {
        RewardTier.I: (5, 25, 10),
        RewardTier.II: (10, 60, 25),
        RewardTier.III: (20, 120, 50),
    }
    for tier, (g, x, c) in want_caps.items():
        b = catalog.TIER_CAPS[tier]
        check(
            f"B0.1 TIER_CAPS[{tier.value}] == ({g},{x},{c},capability=None)",
            (b.global_xp, b.game_xp, b.currency, b.capability) == (g, x, c, None),
            f"got=({b.global_xp},{b.game_xp},{b.currency},{b.capability})",
        )
    check("B0.1 exactly three tiers", set(catalog.TIER_CAPS) == set(RewardTier))

    # --- B0.2 GLOBAL_MAX exact ---
    gm = catalog.GLOBAL_MAX
    check(
        "B0.2 GLOBAL_MAX == (20,120,50)",
        (gm.global_xp, gm.game_xp, gm.currency) == (20, 120, 50),
        f"got=({gm.global_xp},{gm.game_xp},{gm.currency})",
    )

    # --- B0.3 catalog docstring notes verbatim ---
    doc = catalog.__doc__ or ""
    check(
        "B0.3 D-0005/D-0008 placeholder note verbatim",
        "the exact superbot Q-0087 dual-track band constants were not\n"
        "sourced into this repo. The tier ceilings below are deliberately "
        "conservative,\nin-band values chosen to be reconciled against the "
        "real Q-0087 bands later" in doc,
    )
    check(
        "B0.3 play-only capability line verbatim",
        "Capability\nunlocks are play-only (tier III completion), never bought "
        "with currency" in doc,
    )

    # --- B0.4 survival TUNABLES exact + Easy identity by import ---
    want_tun = {
        Difficulty.EASY: (60, 10, 1),
        Difficulty.MEDIUM: (50, 15, 1),
        Difficulty.HARD: (40, 20, 1),
    }
    for diff, (m, r, c) in want_tun.items():
        t = TUNABLES[diff]
        check(
            f"B0.4 TUNABLES[{diff.value}] == ({m},{r},{c})",
            (t.max_energy, t.regen_seconds, t.cost) == (m, r, c),
            f"got=({t.max_energy},{t.regen_seconds},{t.cost})",
        )
    easy = TUNABLES[Difficulty.EASY]
    check(
        "B0.4 Easy ≡ mining bar BY IMPORT (D-0004)",
        easy.max_energy == energy.MAX_ENERGY
        and easy.regen_seconds == energy.REGEN_SECONDS
        and easy.cost == energy.DIG_COST,
    )
    src = (ENGINE / "games/exploration/survival/difficulty.py").read_text()
    check(
        "B0.4 Easy identity is by-import in SOURCE (max_energy=energy.MAX_ENERGY)",
        "max_energy=energy.MAX_ENERGY" in src
        and "regen_seconds=energy.REGEN_SECONDS" in src
        and "cost=energy.DIG_COST" in src,
    )

    # --- B0.5 mining bar exact ---
    check(
        "B0.5 mining bar == (MAX_ENERGY 60, REGEN_SECONDS 10, DIG_COST 1)",
        (energy.MAX_ENERGY, energy.REGEN_SECONDS, energy.DIG_COST) == (60, 10, 1),
        f"got=({energy.MAX_ENERGY},{energy.REGEN_SECONDS},{energy.DIG_COST})",
    )

    # --- B0.6 RewardBundle field semantics ---
    fields = tuple(RewardBundle.__dataclass_fields__)
    check(
        "B0.6 RewardBundle fields == (global_xp, game_xp, currency, capability)",
        fields == ("global_xp", "game_xp", "currency", "capability"),
        f"got={fields}",
    )

    # --- B0.7 tier semantics from models.py source comments ---
    msrc = (ENGINE / "games/exploration/quest/models.py").read_text()
    check(
        "B0.7 tier comments: I casual · II standard · III prestige",
        'I = "I"  # casual' in msrc
        and 'II = "II"  # standard' in msrc
        and 'III = "III"  # prestige' in msrc,
    )

    print()
    if _FAILED:
        print(f"B0 GATE: FAILED ({len(_FAILED)} failed, {_PASSED} passed): {_FAILED}")
        return 1
    print(f"B0 GATE: VALID — {_PASSED} checks passed, 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

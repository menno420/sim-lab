"""idle_engine — deterministic, pure-domain idle-game core (VENDORED for SIM-001).

RECONSTRUCTED __init__.py — the ONLY file in this package that is NOT a byte
copy of the pinned superbot-idle source. The five sibling modules
(``state``, ``engine``, ``upgrades``, ``prestige``, ``economy``) are byte-for-byte
copies of ``idle_engine/`` @ ``f11c71a52d4d2adf88b2bf11f5d1134bad495be2``
(``menno420/superbot-idle``). The upstream package ``__init__`` also re-exported
``idle_engine.theme`` and ``idle_engine.render``; those two modules are NOT part of
the SIM-001 economy surface (Q-0264 / economy-v1.md § Inputs names only the
mechanics functions) and were not vendored, so this reconstruction re-exports ONLY
the five vendored modules. Nothing in the economy/mechanics logic was edited — this
file merely wires the package's public names. Any deviation from the upstream
economy logic would be a bug; this init changes none of it.
"""

from idle_engine.state import GameState, GeneratorSpec
from idle_engine.engine import (
    apply_offline_progress,
    offline_progress,
    production_per_second,
    tick,
)
from idle_engine.upgrades import (
    UpgradeSpec,
    purchase_upgrade,
    upgrade_cost,
    upgrade_percent,
)
from idle_engine.prestige import (
    PrestigeSpec,
    apply_prestige,
    prestige_award,
    prestige_eligible,
    prestige_percent,
)
from idle_engine.economy import (
    UPGRADE_BASE_COST_SECONDS,
    UPGRADE_COST_GROWTH_NUM,
    UPGRADE_COST_GROWTH_DEN,
    UPGRADE_EFFECT_PERCENT,
    PRESTIGE_THRESHOLD,
    PRESTIGE_AWARD_DIVISOR,
    PRESTIGE_BONUS_PERCENT,
    build_prestige_spec,
    build_upgrade_spec,
)

__all__ = [
    "GameState",
    "GeneratorSpec",
    "PrestigeSpec",
    "UpgradeSpec",
    "UPGRADE_BASE_COST_SECONDS",
    "UPGRADE_COST_GROWTH_NUM",
    "UPGRADE_COST_GROWTH_DEN",
    "UPGRADE_EFFECT_PERCENT",
    "PRESTIGE_THRESHOLD",
    "PRESTIGE_AWARD_DIVISOR",
    "PRESTIGE_BONUS_PERCENT",
    "apply_offline_progress",
    "apply_prestige",
    "build_prestige_spec",
    "build_upgrade_spec",
    "offline_progress",
    "prestige_award",
    "prestige_eligible",
    "prestige_percent",
    "production_per_second",
    "purchase_upgrade",
    "tick",
    "upgrade_cost",
    "upgrade_percent",
]

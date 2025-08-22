# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, TechEffectResult
from saiyanquest.locale import T

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.technique.technique import Technique


@dataclass
class ScopeEffect(CoreEffect):
    """
    Scope: scan monster stats.

    """

    name = "scope"

    def apply_tech_target(
        self, session: Session, tech: Technique, user: Monster, target: Monster
    ) -> TechEffectResult:
        params = {
            "AR": target.armour,
            "DE": target.dodge,
            "ME": target.melee,
            "RD": target.ranged,
            "SD": target.speed,
        }
        extra = [T.format("combat_scope", params)]
        return TechEffectResult(name=tech.name, success=True, extras=extra)

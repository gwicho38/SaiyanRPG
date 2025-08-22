# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, TechEffectResult

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.technique.technique import Technique


@dataclass
class EmptyEffect(CoreEffect):
    """
    "This effect lets the technique show the animation, but it also prevents
    the technique from failing. Without it, the technique would automatically
    fail, because the effect list is empty [] and success is False by default.
    """

    name = "empty"

    def apply_tech_target(
        self, session: Session, tech: Technique, user: Monster, target: Monster
    ) -> TechEffectResult:
        hit = session.client.combat_session.get_tech_hit(user)
        tech.hit = tech.accuracy >= hit
        return TechEffectResult(name=tech.name, success=tech.hit)

# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, StatusEffectResult
from saiyanquest.db import EffectPhase
from saiyanquest.technique.technique import Technique

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.status.status import Status


@dataclass
class CharmedEffect(CoreEffect):
    """
    Charmed: 50% chance of failing if they target an opponent.

    Parameters:
        chance: The chance.
    """

    name = "charmed"
    chance: float

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        if (
            status.has_phase(EffectPhase.PRE_CHECKING)
            and random.random() > self.chance
        ):
            user = status.get_host()
            action = session.client.combat_session.get_variable("action_tech")
            technique = Technique.create(str(action) or "skip")
            if any(
                technique.target.get(target_type, True)
                for target_type in [
                    "enemy_monster",
                    "enemy_team",
                    "enemy_trainer",
                ]
            ):
                session.client.combat_session.set_tech_hit(user, 1.0)
        return StatusEffectResult(name=status.name, success=True)

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
class FlinchingEffect(CoreEffect):
    """
    Flinching: 50% chance to miss your next turn.
    If you do miss your next turn, this status ends.

    Parameters:
        chance: The chance.
    """

    name = "flinching"
    chance: float

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        tech: list[Technique] = []
        if (
            status.has_phase(EffectPhase.PRE_CHECKING)
            and random.random() > self.chance
        ):
            empty = status.on_tech_use
            assert empty
            skip = Technique.create(empty)
            tech = [skip]
            target.status.clear_status(session)
        return StatusEffectResult(
            name=status.name, success=True, techniques=tech
        )

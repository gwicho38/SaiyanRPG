# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, StatusEffectResult
from saiyanquest.db import EffectPhase
from saiyanquest.formula import simple_lifeleech

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.status.status import Status


@dataclass
class LifeGiftEffect(CoreEffect):
    """
    This effect has a chance to apply the lifegift status effect.

    Parameters:
        user: The monster losing HPs.
        target: The monster getting HPs.
        divisor: The number by which target HP is to be divided.

    """

    name = "lifegift"
    divisor: int

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        lifegift: bool = False
        user = status.get_host()
        if (
            status.has_phase(EffectPhase.PERFORM_STATUS)
            and not user.is_fainted
        ):
            damage = simple_lifeleech(user, target, self.divisor)
            user.current_hp = max(0, user.current_hp - damage)
            target.current_hp = min(target.hp, target.current_hp + damage)
            lifegift = True
        if user.is_fainted:
            target.status.clear_status(session)

        return StatusEffectResult(name=status.name, success=lifegift)

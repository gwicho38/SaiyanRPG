# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, StatusEffectResult
from saiyanquest.db import EffectPhase
from saiyanquest.locale import T
from saiyanquest.modifiers import parse_modifier_mode

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.status.status import Status


@dataclass
class BurntEffect(CoreEffect):
    """
    This effect has a chance to apply the burnt status based on a calculated
    damage multiplier.

    Parameters:
        divisor: Determines how much HP is lost (damage is calculated as
            target.hp / divisor).
        mode: Specifies the strategy used to evaluate modifiers against
            the target. Must be one of: "first", "weakest", "strongest",
            "average", "cumulative".

    The effect checks whether a damage multiplier applies to the target using
    the given mode. If the calculated damage is greater than zero, the target
    is burned and loses HP. Otherwise, the status fails to apply and is cleared.
    """

    name = "burnt"
    divisor: int
    mode: str

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        burnt: bool = False
        params = {"target": target.name, "method": status.name}
        if status.has_phase(EffectPhase.PERFORM_STATUS):
            damage = target.hp / self.divisor
            mode_enum = parse_modifier_mode(self.mode)
            mult = status.modifiers.get_multiplier(target, mode=mode_enum)
            damage *= mult
            if damage > 0:
                burnt = True
                target.current_hp = max(0, target.current_hp - int(damage))
            else:
                status.use_failure = T.format("combat_state_immune", params)
                target.status.clear_status(session)

        return StatusEffectResult(name=status.name, success=burnt)

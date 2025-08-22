# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, StatusEffectResult
from saiyanquest.db import EffectPhase
from saiyanquest.locale import T

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.status.status import Status


@dataclass
class DieHardEffect(CoreEffect):
    """
    DieHard: When HP would fall below 1, set it to 1, remove this status and
    print "X fights through the pain."

    A monster that is already on exactly 1 HP cannot gain the Diehard status.

    Parameters:
        hp: The amount of HP to set.
    """

    name = "diehard"
    hp: int

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        extra: list[str] = []
        if status.has_phase(EffectPhase.CHECK_PARTY_HP):
            params = {"target": target.name.upper()}
            if target.is_fainted:
                target.current_hp = self.hp
                target.status.clear_status(session)
                extra = [T.format("combat_state_diehard_tech", params)]
            if target.current_hp == self.hp:
                target.status.clear_status(session)
                extra = [T.format("combat_state_diehard_end", params)]

        return StatusEffectResult(name=status.name, success=True, extras=extra)

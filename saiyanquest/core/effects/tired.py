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
class TiredEffect(CoreEffect):
    """
    Tired status

    """

    name = "tired"

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        extra: list[str] = []
        if status.has_phase(EffectPhase.PERFORM_TECH):
            params = {"target": target.name.upper()}
            extra = [T.format("combat_state_tired_end", params)]
            target.status.clear_status(session)
        return StatusEffectResult(name=status.name, success=True, extras=extra)

# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, StatusEffectResult

if TYPE_CHECKING:
    from saiyanquest.monster import Monster
    from saiyanquest.session import Session
    from saiyanquest.status.status import Status


@dataclass
class FesteringEffect(CoreEffect):
    """
    This effect has a chance to apply the festering status effect.
    """

    name = "festering"

    def apply_status_target(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        return StatusEffectResult(name=status.name, success=True)

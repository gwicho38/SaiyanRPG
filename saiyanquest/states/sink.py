# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from typing import ClassVar, Optional

from saiyanquest.platform_interface.events import PlayerInput
from saiyanquest.state.state import State


class SinkState(State):
    """State blocking input to lower states in the stack."""

    name: ClassVar[str] = "SinkState"
    transparent = True

    def process_event(self, event: PlayerInput) -> Optional[PlayerInput]:
        return None

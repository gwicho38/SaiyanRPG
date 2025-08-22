# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import final

from saiyanquest.event.eventaction import EventAction
from saiyanquest.session import Session
from saiyanquest.states.sink import SinkState


@final
@dataclass
class UnlockControlsAction(
    EventAction,
):
    """
    Unlock player controls

    Script usage:
        .. code-block::

            unlock_controls

    """

    name = "unlock_controls"

    def start(self, session: Session) -> None:
        sink_state = session.client.get_state_by_name(SinkState)

        if sink_state:
            session.client.pop_state(sink_state)

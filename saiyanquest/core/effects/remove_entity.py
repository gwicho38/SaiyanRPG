# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saiyanquest.core.core_effect import CoreEffect, ItemEffectResult
from saiyanquest.event import get_npc_pos
from saiyanquest.map import get_coords, get_direction

if TYPE_CHECKING:
    from saiyanquest.item.item import Item
    from saiyanquest.session import Session


@dataclass
class RemoveEntityEffect(CoreEffect):
    """
    Removes the NPC and creates a variable.
    """

    name = "remove_entity"

    def apply_item(self, session: Session, item: Item) -> ItemEffectResult:
        remove: bool = False
        client = session.client
        player = session.player
        tiles = get_coords(player.tile_pos, client.map_manager.map_size)

        for coords in tiles:
            npc = get_npc_pos(session, coords)
            if npc:
                facing = get_direction(player.tile_pos, npc.tile_pos)
                if player.facing == facing:
                    client.event_engine.execute_action(
                        "remove_npc", [npc.slug], True
                    )
                    player.game_variables[npc.slug] = self.name
                    remove = True

        return ItemEffectResult(name=item.name, success=remove)

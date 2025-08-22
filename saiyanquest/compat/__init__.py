# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from saiyanquest.compat.rect import ReadOnlyRect

Rect: type[ReadOnlyRect]

try:
    from pygame.rect import Rect
except ImportError:
    from saiyanquest.compat.rect import Rect

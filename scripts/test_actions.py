"""
Script to validate map actions
"""

from unittest.mock import MagicMock

from saiyanquest.constants import paths
from saiyanquest.db import db
from saiyanquest.event.eventaction import ActionManager
from saiyanquest.event.eventcondition import ConditionManager
from saiyanquest.event.eventengine import EventEngine
from saiyanquest.map_loader import TMXMapLoader
from saiyanquest.prepare import CONFIG
from saiyanquest.session import Session

db.load("monster")
action = ActionManager()
condition = ConditionManager()
engine = EventEngine(Session(), action, condition)
loader = TMXMapLoader()
loader.image_loader = MagicMock()

for mod_name in CONFIG.mods:
    for path in (paths.mods_folder / mod_name / "maps").glob("*.tmx"):
        txmn_map = loader.load(str(path))
        for event in txmn_map.events:
            for act in event.acts:
                if not engine.action_manager.get_action(act.type, act.parameters):
                    print(f"{path} failed")

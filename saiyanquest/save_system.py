#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Save/Load System for SaiyanQuest

import json
import os
import time
import shutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from .character_system import Character
from .gta_world import GTAWorld, District
from .vehicle_system import Vehicle, VehicleManager
from .mission_system import MissionManager, Mission
from .crime_system import CrimeSystem

@dataclass
class SaveInfo:
    slot: int
    character_name: str
    level: int
    money: int
    location: str
    playtime: float
    save_date: str
    mission_progress: str
    completion_percentage: float

class GameSaveData:
    """Container for all saveable game data"""
    
    def __init__(self):
        # Core game data
        self.character_data: Dict = {}
        self.world_data: Dict = {}
        self.mission_data: Dict = {}
        self.vehicle_data: Dict = {}
        self.crime_data: Dict = {}
        
        # Game state
        self.game_time: float = 0.0
        self.weather: str = "clear"
        self.player_position: tuple = (0, 0)
        self.player_rotation: float = 0.0
        
        # Meta information
        self.save_version: str = "1.0"
        self.save_timestamp: float = 0.0
        self.playtime: float = 0.0
        self.completion_percentage: float = 0.0

class SaveManager:
    """Manages game saves and loads"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.max_save_slots = 8
        self.auto_save_interval = 300.0  # 5 minutes
        self.last_auto_save = 0.0
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Create auto-save directory
        self.auto_save_dir = os.path.join(self.save_directory, "autosave")
        os.makedirs(self.auto_save_dir, exist_ok=True)
        
        # Quick save slot (F5/F9 functionality)
        self.quick_save_slot = 99
        
    def save_game(self, slot: int, character: Character, world: GTAWorld, 
                  vehicle_manager: VehicleManager, mission_manager: MissionManager,
                  crime_system: CrimeSystem, player_x: float, player_y: float,
                  game_time: float) -> bool:
        """Save the complete game state"""
        try:
            save_data = GameSaveData()
            
            # Character data
            save_data.character_data = character.save_to_dict()
            
            # World data
            save_data.world_data = self._save_world_data(world)
            
            # Mission data
            save_data.mission_data = self._save_mission_data(mission_manager)
            
            # Vehicle data
            save_data.vehicle_data = self._save_vehicle_data(vehicle_manager)
            
            # Crime data
            save_data.crime_data = self._save_crime_data(crime_system)
            
            # Game state
            save_data.game_time = game_time
            save_data.weather = world.weather
            save_data.player_position = (player_x, player_y)
            save_data.playtime = character.time_played
            
            # Meta data
            save_data.save_timestamp = time.time()
            save_data.completion_percentage = self._calculate_completion_percentage(
                character, mission_manager
            )
            
            # Write to file
            save_file = os.path.join(self.save_directory, f"save_{slot:02d}.json")
            with open(save_file, 'w') as f:
                json.dump(self._serialize_save_data(save_data), f, indent=2)
            
            # Create save info file for quick loading
            self._create_save_info(slot, save_data)
            
            print(f"Game saved to slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, slot: int) -> Optional[GameSaveData]:
        """Load game state from save slot"""
        try:
            save_file = os.path.join(self.save_directory, f"save_{slot:02d}.json")
            
            if not os.path.exists(save_file):
                print(f"Save file not found for slot {slot}")
                return None
            
            with open(save_file, 'r') as f:
                data = json.load(f)
            
            save_data = self._deserialize_save_data(data)
            print(f"Game loaded from slot {slot}")
            return save_data
            
        except Exception as e:
            print(f"Failed to load game from slot {slot}: {e}")
            return None
    
    def quick_save(self, character: Character, world: GTAWorld, 
                   vehicle_manager: VehicleManager, mission_manager: MissionManager,
                   crime_system: CrimeSystem, player_x: float, player_y: float,
                   game_time: float) -> bool:
        """Quick save to dedicated slot"""
        return self.save_game(self.quick_save_slot, character, world, vehicle_manager,
                            mission_manager, crime_system, player_x, player_y, game_time)
    
    def quick_load(self) -> Optional[GameSaveData]:
        """Quick load from dedicated slot"""
        return self.load_game(self.quick_save_slot)
    
    def auto_save(self, dt: float, character: Character, world: GTAWorld,
                  vehicle_manager: VehicleManager, mission_manager: MissionManager,
                  crime_system: CrimeSystem, player_x: float, player_y: float,
                  game_time: float) -> bool:
        """Automatically save game at intervals"""
        self.last_auto_save += dt
        
        if self.last_auto_save >= self.auto_save_interval:
            self.last_auto_save = 0.0
            
            # Save to auto-save slot
            auto_save_file = os.path.join(self.auto_save_dir, "autosave.json")
            
            try:
                save_data = GameSaveData()
                save_data.character_data = character.save_to_dict()
                save_data.world_data = self._save_world_data(world)
                save_data.mission_data = self._save_mission_data(mission_manager)
                save_data.vehicle_data = self._save_vehicle_data(vehicle_manager)
                save_data.crime_data = self._save_crime_data(crime_system)
                save_data.game_time = game_time
                save_data.weather = world.weather
                save_data.player_position = (player_x, player_y)
                save_data.playtime = character.time_played
                save_data.save_timestamp = time.time()
                
                with open(auto_save_file, 'w') as f:
                    json.dump(self._serialize_save_data(save_data), f, indent=2)
                
                print("Auto-save completed")
                return True
                
            except Exception as e:
                print(f"Auto-save failed: {e}")
                return False
        
        return False
    
    def get_save_list(self) -> List[SaveInfo]:
        """Get list of all available saves"""
        saves = []
        
        for slot in range(1, self.max_save_slots + 1):
            info_file = os.path.join(self.save_directory, f"save_{slot:02d}_info.json")
            
            if os.path.exists(info_file):
                try:
                    with open(info_file, 'r') as f:
                        info_data = json.load(f)
                    
                    save_info = SaveInfo(
                        slot=info_data['slot'],
                        character_name=info_data['character_name'],
                        level=info_data['level'],
                        money=info_data['money'],
                        location=info_data['location'],
                        playtime=info_data['playtime'],
                        save_date=info_data['save_date'],
                        mission_progress=info_data['mission_progress'],
                        completion_percentage=info_data['completion_percentage']
                    )
                    saves.append(save_info)
                    
                except Exception as e:
                    print(f"Error reading save info for slot {slot}: {e}")
        
        # Sort by slot number
        saves.sort(key=lambda x: x.slot)
        return saves
    
    def delete_save(self, slot: int) -> bool:
        """Delete a save file"""
        try:
            save_file = os.path.join(self.save_directory, f"save_{slot:02d}.json")
            info_file = os.path.join(self.save_directory, f"save_{slot:02d}_info.json")
            
            if os.path.exists(save_file):
                os.remove(save_file)
            if os.path.exists(info_file):
                os.remove(info_file)
            
            print(f"Save slot {slot} deleted")
            return True
            
        except Exception as e:
            print(f"Failed to delete save slot {slot}: {e}")
            return False
    
    def copy_save(self, from_slot: int, to_slot: int) -> bool:
        """Copy save from one slot to another"""
        try:
            from_file = os.path.join(self.save_directory, f"save_{from_slot:02d}.json")
            to_file = os.path.join(self.save_directory, f"save_{to_slot:02d}.json")
            
            from_info = os.path.join(self.save_directory, f"save_{from_slot:02d}_info.json")
            to_info = os.path.join(self.save_directory, f"save_{to_slot:02d}_info.json")
            
            if os.path.exists(from_file):
                shutil.copy2(from_file, to_file)
                
                if os.path.exists(from_info):
                    shutil.copy2(from_info, to_info)
                    
                    # Update slot number in copied info
                    with open(to_info, 'r') as f:
                        info_data = json.load(f)
                    info_data['slot'] = to_slot
                    with open(to_info, 'w') as f:
                        json.dump(info_data, f, indent=2)
                
                print(f"Save copied from slot {from_slot} to slot {to_slot}")
                return True
            else:
                print(f"No save found in slot {from_slot}")
                return False
                
        except Exception as e:
            print(f"Failed to copy save: {e}")
            return False
    
    def _save_world_data(self, world: GTAWorld) -> Dict:
        """Save world state data"""
        return {
            'time_of_day': world.time_of_day,
            'weather': world.weather,
            'wanted_level': world.wanted_level.value,
            'chaos_level': world.chaos_level,
            'safe_houses': [
                {
                    'name': house.name,
                    'position': house.position,
                    'owned': house.owned,
                    'price': house.price,
                    'garage_capacity': house.garage_capacity,
                    'amenities': house.amenities
                } for house in world.safe_houses
            ]
        }
    
    def _save_mission_data(self, mission_manager: MissionManager) -> Dict:
        """Save mission progress data"""
        return {
            'completed_missions': mission_manager.completed_missions,
            'failed_missions': mission_manager.failed_missions,
            'player_level': mission_manager.player_level,
            'player_respect': mission_manager.player_respect,
            'active_missions': [
                {
                    'mission_id': mission.mission_id,
                    'title': mission.title,
                    'current_objective_index': mission.current_objective_index,
                    'start_time': mission.start_time,
                    'mission_data': mission.mission_data
                } for mission in mission_manager.active_missions
            ]
        }
    
    def _save_vehicle_data(self, vehicle_manager: VehicleManager) -> Dict:
        """Save vehicle data"""
        return {
            'player_vehicles': [
                {
                    'vehicle_type': vehicle.vehicle_type.value,
                    'x': vehicle.x,
                    'y': vehicle.y,
                    'angle': vehicle.angle,
                    'health': vehicle.health,
                    'fuel': vehicle.fuel,
                    'modifications': getattr(vehicle, 'modifications', [])
                } for vehicle in vehicle_manager.vehicles
            ],
            'parked_vehicles': [
                {
                    'vehicle_type': vehicle.vehicle_type.value,
                    'x': vehicle.x,
                    'y': vehicle.y,
                    'angle': vehicle.angle,
                    'health': vehicle.health,
                    'fuel': vehicle.fuel
                } for vehicle in vehicle_manager.parked_vehicles
            ]
        }
    
    def _save_crime_data(self, crime_system: CrimeSystem) -> Dict:
        """Save crime system data"""
        return {
            'wanted_level': crime_system.get_wanted_level().value,
            'heat_percentage': crime_system.get_heat_percentage(),
            'total_crimes': crime_system.total_crimes_committed,
            'crimes_by_type': {k.value: v for k, v in crime_system.crimes_by_type.items()},
            'time_spent_wanted': crime_system.time_spent_wanted,
            'max_wanted_level': crime_system.max_wanted_level_reached.value
        }
    
    def _create_save_info(self, slot: int, save_data: GameSaveData) -> None:
        """Create save info file for quick display"""
        character_data = save_data.character_data
        
        info = {
            'slot': slot,
            'character_name': character_data.get('name', 'Unknown'),
            'level': character_data.get('level', 1),
            'money': character_data.get('money', 0),
            'location': self._get_location_name(save_data.player_position),
            'playtime': save_data.playtime,
            'save_date': datetime.fromtimestamp(save_data.save_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'mission_progress': f"{character_data.get('missions_completed', 0)} missions completed",
            'completion_percentage': save_data.completion_percentage
        }
        
        info_file = os.path.join(self.save_directory, f"save_{slot:02d}_info.json")
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2)
    
    def _get_location_name(self, position: tuple) -> str:
        """Get readable location name from coordinates"""
        x, y = position
        
        # These would match the actual district coordinates from GTAWorld
        if 3500 <= x <= 4500 and 2000 <= y <= 3500:
            return "Downtown"
        elif 1000 <= x <= 3000 and 3000 <= y <= 4500:
            return "Grove Street"
        elif 4500 <= x <= 6500 and 4000 <= y <= 5500:
            return "Industrial"
        elif 500 <= x <= 3000 and 500 <= y <= 1500:
            return "Beach"
        elif 2000 <= x <= 3500 and 500 <= y <= 2000:
            return "Hills"
        elif 6000 <= x <= 7500 and 1000 <= y <= 3000:
            return "Airport"
        elif 5500 <= x <= 7500 and 4500 <= y <= 5500:
            return "Docks"
        else:
            return "Los Santos"
    
    def _calculate_completion_percentage(self, character: Character, 
                                       mission_manager: MissionManager) -> float:
        """Calculate game completion percentage"""
        # This would be more complex in a real implementation
        total_missions = 100  # Placeholder
        story_missions_completed = len([m for m in mission_manager.completed_missions 
                                      if m.startswith('story_')])
        
        mission_percentage = (character.missions_completed / total_missions) * 60
        stats_percentage = (sum(character.stats.__dict__.values()) / (1000 * 8)) * 20
        territory_percentage = (len(character.territory_controlled) / 20) * 10
        property_percentage = (len(character.owned_properties) / 10) * 10
        
        return min(100.0, mission_percentage + stats_percentage + 
                  territory_percentage + property_percentage)
    
    def _serialize_save_data(self, save_data: GameSaveData) -> Dict:
        """Serialize save data to JSON-compatible format"""
        return {
            'save_version': save_data.save_version,
            'save_timestamp': save_data.save_timestamp,
            'playtime': save_data.playtime,
            'completion_percentage': save_data.completion_percentage,
            'game_time': save_data.game_time,
            'weather': save_data.weather,
            'player_position': save_data.player_position,
            'player_rotation': save_data.player_rotation,
            'character_data': save_data.character_data,
            'world_data': save_data.world_data,
            'mission_data': save_data.mission_data,
            'vehicle_data': save_data.vehicle_data,
            'crime_data': save_data.crime_data
        }
    
    def _deserialize_save_data(self, data: Dict) -> GameSaveData:
        """Deserialize save data from JSON format"""
        save_data = GameSaveData()
        
        save_data.save_version = data.get('save_version', '1.0')
        save_data.save_timestamp = data.get('save_timestamp', 0.0)
        save_data.playtime = data.get('playtime', 0.0)
        save_data.completion_percentage = data.get('completion_percentage', 0.0)
        save_data.game_time = data.get('game_time', 0.0)
        save_data.weather = data.get('weather', 'clear')
        save_data.player_position = tuple(data.get('player_position', (0, 0)))
        save_data.player_rotation = data.get('player_rotation', 0.0)
        save_data.character_data = data.get('character_data', {})
        save_data.world_data = data.get('world_data', {})
        save_data.mission_data = data.get('mission_data', {})
        save_data.vehicle_data = data.get('vehicle_data', {})
        save_data.crime_data = data.get('crime_data', {})
        
        return save_data
    
    def backup_saves(self) -> bool:
        """Create backup of all save files"""
        try:
            backup_dir = os.path.join(self.save_directory, "backup")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy all save files
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json') and filename.startswith('save_'):
                    src = os.path.join(self.save_directory, filename)
                    dst = os.path.join(backup_path, filename)
                    shutil.copy2(src, dst)
            
            print(f"Save backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Failed to create save backup: {e}")
            return False
    
    def restore_from_backup(self, backup_name: str) -> bool:
        """Restore saves from backup"""
        try:
            backup_dir = os.path.join(self.save_directory, "backup")
            backup_path = os.path.join(backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                print(f"Backup not found: {backup_name}")
                return False
            
            # Copy backup files to save directory
            for filename in os.listdir(backup_path):
                if filename.endswith('.json'):
                    src = os.path.join(backup_path, filename)
                    dst = os.path.join(self.save_directory, filename)
                    shutil.copy2(src, dst)
            
            print(f"Saves restored from backup: {backup_name}")
            return True
            
        except Exception as e:
            print(f"Failed to restore from backup: {e}")
            return False


class GameStateManager:
    """Manages the overall game state and coordinates saving/loading"""
    
    def __init__(self):
        self.save_manager = SaveManager()
        self.is_loading = False
        self.last_save_time = 0.0
        
    def apply_save_data(self, save_data: GameSaveData, character: Character, 
                       world: GTAWorld, vehicle_manager: VehicleManager,
                       mission_manager: MissionManager, crime_system: CrimeSystem) -> Tuple[float, float, float]:
        """Apply loaded save data to game objects"""
        
        # Load character
        character.load_from_dict(save_data.character_data)
        
        # Load world state
        world_data = save_data.world_data
        world.time_of_day = world_data.get('time_of_day', 12.0)
        world.weather = world_data.get('weather', 'clear')
        world.wanted_level = world.WantedLevel(world_data.get('wanted_level', 0))
        world.chaos_level = world_data.get('chaos_level', 0.0)
        
        # Update safe house ownership
        safe_house_data = world_data.get('safe_houses', [])
        for i, house_data in enumerate(safe_house_data):
            if i < len(world.safe_houses):
                world.safe_houses[i].owned = house_data.get('owned', False)
        
        # Load mission progress
        mission_data = save_data.mission_data
        mission_manager.completed_missions = mission_data.get('completed_missions', [])
        mission_manager.failed_missions = mission_data.get('failed_missions', [])
        mission_manager.player_level = mission_data.get('player_level', 1)
        mission_manager.player_respect = mission_data.get('player_respect', 0)
        
        # Load vehicles
        vehicle_data = save_data.vehicle_data
        vehicle_manager.vehicles.clear()
        
        # Load crime system state
        crime_data = save_data.crime_data
        crime_system.total_crimes_committed = crime_data.get('total_crimes', 0)
        crime_system.time_spent_wanted = crime_data.get('time_spent_wanted', 0.0)
        
        # Return player position and game time
        player_x, player_y = save_data.player_position
        return player_x, player_y, save_data.game_time
    
    def create_new_game(self, character: Character) -> None:
        """Initialize a new game state"""
        character.name = "Player"
        character.money = 350
        character.respect = 0
        character.current_gang = character.GangAffiliation.GROVE_STREET
        
        # Starting location (Grove Street)
        character.stats.health = character.stats.max_health
        
        print("New game created")
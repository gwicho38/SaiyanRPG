#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Enhanced Mission System with Advanced Objectives and Rewards

import time
import random
import json
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager
from .vehicle_physics import VehiclePhysicsSystem
from .character_ai import CharacterAIManager
from .world_3d_system import World3DSystem


class MissionType(Enum):
    """Types of missions"""
    STORY = "story"
    SIDE_QUEST = "side_quest"
    RANDOM_EVENT = "random_event"
    DAILY_CHALLENGE = "daily_challenge"
    ACHIEVEMENT = "achievement"
    TUTORIAL = "tutorial"


class MissionStatus(Enum):
    """Mission status"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"


class ObjectiveType(Enum):
    """Types of objectives"""
    REACH_LOCATION = "reach_location"
    ELIMINATE_TARGET = "eliminate_target"
    COLLECT_ITEM = "collect_item"
    DELIVER_ITEM = "deliver_item"
    SURVIVE_TIME = "survive_time"
    ESCAPE_AREA = "escape_area"
    PROTECT_TARGET = "protect_target"
    STEAL_VEHICLE = "steal_vehicle"
    RACE_COMPETITION = "race_competition"
    CUSTOM_SCRIPT = "custom_script"


class RewardType(Enum):
    """Types of rewards"""
    MONEY = "money"
    EXPERIENCE = "experience"
    WEAPON = "weapon"
    VEHICLE = "vehicle"
    ITEM = "item"
    UNLOCK = "unlock"
    REPUTATION = "reputation"


@dataclass
class Objective:
    """Mission objective"""
    objective_id: int
    objective_type: ObjectiveType
    description: str
    target_data: Dict[str, Any]  # Type-specific data
    is_completed: bool = False
    is_optional: bool = False
    completion_time: float = 0.0


@dataclass
class Reward:
    """Mission reward"""
    reward_type: RewardType
    amount: int
    item_id: Optional[str] = None
    description: str = ""


@dataclass
class Mission:
    """Enhanced mission with objectives and rewards"""
    mission_id: int
    name: str
    description: str
    mission_type: MissionType
    status: MissionStatus
    objectives: List[Objective]
    rewards: List[Reward]
    prerequisites: List[int]  # Mission IDs that must be completed first
    difficulty: int  # 1-10
    estimated_time: float  # minutes
    start_time: float = 0.0
    completion_time: float = 0.0
    failure_conditions: List[str] = None
    success_conditions: List[str] = None


class MissionScript:
    """Mission scripting system"""
    
    def __init__(self):
        self.scripts: Dict[str, Callable] = {}
        self._register_default_scripts()
    
    def _register_default_scripts(self):
        """Register default mission scripts"""
        self.scripts["reach_location"] = self._script_reach_location
        self.scripts["eliminate_target"] = self._script_eliminate_target
        self.scripts["collect_item"] = self._script_collect_item
        self.scripts["deliver_item"] = self._script_deliver_item
        self.scripts["survive_time"] = self._script_survive_time
        self.scripts["escape_area"] = self._script_escape_area
        self.scripts["protect_target"] = self._script_protect_target
        self.scripts["steal_vehicle"] = self._script_steal_vehicle
        self.scripts["race_competition"] = self._script_race_competition
    
    def _script_reach_location(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for reaching a location"""
        target_x = objective.target_data.get('x', 0)
        target_y = objective.target_data.get('y', 0)
        radius = objective.target_data.get('radius', 10.0)
        
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0)
        
        distance = ((player_x - target_x)**2 + (player_y - target_y)**2)**0.5
        return distance <= radius
    
    def _script_eliminate_target(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for eliminating a target"""
        target_id = objective.target_data.get('target_id')
        required_kills = objective.target_data.get('kills', 1)
        
        # Check if target has been eliminated
        # This would integrate with the combat system
        return False  # Placeholder
    
    def _script_collect_item(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for collecting an item"""
        item_id = objective.target_data.get('item_id')
        required_amount = objective.target_data.get('amount', 1)
        
        # Check if player has collected the required items
        # This would integrate with the inventory system
        return False  # Placeholder
    
    def _script_deliver_item(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for delivering an item"""
        item_id = objective.target_data.get('item_id')
        delivery_x = objective.target_data.get('delivery_x', 0)
        delivery_y = objective.target_data.get('delivery_y', 0)
        radius = objective.target_data.get('radius', 10.0)
        
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0)
        
        # Check if player is at delivery location and has the item
        distance = ((player_x - delivery_x)**2 + (player_y - delivery_y)**2)**0.5
        return distance <= radius  # Placeholder - would also check inventory
    
    def _script_survive_time(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for surviving for a certain time"""
        required_time = objective.target_data.get('time', 60.0)  # seconds
        start_time = objective.target_data.get('start_time', 0.0)
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        return elapsed_time >= required_time
    
    def _script_escape_area(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for escaping an area"""
        escape_x = objective.target_data.get('escape_x', 0)
        escape_y = objective.target_data.get('escape_y', 0)
        radius = objective.target_data.get('radius', 100.0)
        
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0)
        
        distance = ((player_x - escape_x)**2 + (player_y - escape_y)**2)**0.5
        return distance > radius
    
    def _script_protect_target(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for protecting a target"""
        target_id = objective.target_data.get('target_id')
        protection_time = objective.target_data.get('time', 60.0)
        
        # Check if target is still alive and protected
        # This would integrate with the character system
        return False  # Placeholder
    
    def _script_steal_vehicle(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for stealing a vehicle"""
        vehicle_type = objective.target_data.get('vehicle_type')
        delivery_x = objective.target_data.get('delivery_x', 0)
        delivery_y = objective.target_data.get('delivery_y', 0)
        
        # Check if player has stolen the required vehicle and delivered it
        # This would integrate with the vehicle system
        return False  # Placeholder
    
    def _script_race_competition(self, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Script for race competition"""
        race_time = objective.target_data.get('race_time', 120.0)
        required_position = objective.target_data.get('position', 1)
        
        # Check if player completed the race in the required position
        # This would integrate with the racing system
        return False  # Placeholder
    
    def register_script(self, script_name: str, script_function: Callable):
        """Register a custom mission script"""
        self.scripts[script_name] = script_function
        print(f"📜 Registered mission script: {script_name}")
    
    def execute_script(self, script_name: str, objective: Objective, game_state: Dict[str, Any]) -> bool:
        """Execute a mission script"""
        if script_name in self.scripts:
            return self.scripts[script_name](objective, game_state)
        else:
            print(f"❌ Unknown mission script: {script_name}")
            return False


class MissionManager:
    """Enhanced mission management system"""
    
    def __init__(self, physics_manager: PhysicsManager,
                 vehicle_physics: VehiclePhysicsSystem,
                 character_ai: CharacterAIManager,
                 world_3d: World3DSystem):
        self.physics_manager = physics_manager
        self.vehicle_physics = vehicle_physics
        self.character_ai = character_ai
        self.world_3d = world_3d
        
        # Mission data
        self.missions: Dict[int, Mission] = {}
        self.active_missions: List[int] = []
        self.completed_missions: Set[int] = set()
        self.next_mission_id = 1
        
        # Mission scripting
        self.mission_script = MissionScript()
        
        # Statistics
        self.total_missions_completed = 0
        self.total_rewards_earned = 0
        self.total_play_time = 0.0
        
        # Initialize default missions
        self._initialize_default_missions()
        
        print("📜 MissionManager initialized")
    
    def _initialize_default_missions(self):
        """Initialize default missions"""
        # Tutorial mission
        tutorial_mission = Mission(
            mission_id=self.next_mission_id,
            name="Tutorial: First Steps",
            description="Learn the basics of the game",
            mission_type=MissionType.TUTORIAL,
            status=MissionStatus.AVAILABLE,
            objectives=[
                Objective(
                    objective_id=1,
                    objective_type=ObjectiveType.REACH_LOCATION,
                    description="Go to the starting area",
                    target_data={'x': 500, 'y': 500, 'radius': 20.0}
                ),
                Objective(
                    objective_id=2,
                    objective_type=ObjectiveType.STEAL_VEHICLE,
                    description="Steal a vehicle",
                    target_data={'vehicle_type': 'sedan', 'delivery_x': 600, 'delivery_y': 600}
                )
            ],
            rewards=[
                Reward(RewardType.MONEY, 1000, description="Starting money"),
                Reward(RewardType.EXPERIENCE, 100, description="Tutorial experience")
            ],
            prerequisites=[],
            difficulty=1,
            estimated_time=5.0
        )
        self.missions[self.next_mission_id] = tutorial_mission
        self.next_mission_id += 1
        
        # Story mission
        story_mission = Mission(
            mission_id=self.next_mission_id,
            name="The Heist",
            description="Rob the bank and escape",
            mission_type=MissionType.STORY,
            status=MissionStatus.LOCKED,
            objectives=[
                Objective(
                    objective_id=1,
                    objective_type=ObjectiveType.REACH_LOCATION,
                    description="Go to the bank",
                    target_data={'x': 300, 'y': 300, 'radius': 15.0}
                ),
                Objective(
                    objective_id=2,
                    objective_type=ObjectiveType.COLLECT_ITEM,
                    description="Collect the money",
                    target_data={'item_id': 'money_bag', 'amount': 1}
                ),
                Objective(
                    objective_id=3,
                    objective_type=ObjectiveType.ESCAPE_AREA,
                    description="Escape the police",
                    target_data={'escape_x': 800, 'escape_y': 800, 'radius': 200.0}
                )
            ],
            rewards=[
                Reward(RewardType.MONEY, 50000, description="Heist money"),
                Reward(RewardType.EXPERIENCE, 500, description="Heist experience"),
                Reward(RewardType.REPUTATION, -100, description="Criminal reputation")
            ],
            prerequisites=[1],  # Requires tutorial mission
            difficulty=5,
            estimated_time=15.0
        )
        self.missions[self.next_mission_id] = story_mission
        self.next_mission_id += 1
        
        # Side quest
        side_quest = Mission(
            mission_id=self.next_mission_id,
            name="Taxi Driver",
            description="Pick up passengers and drive them to their destinations",
            mission_type=MissionType.SIDE_QUEST,
            status=MissionStatus.AVAILABLE,
            objectives=[
                Objective(
                    objective_id=1,
                    objective_type=ObjectiveType.DELIVER_ITEM,
                    description="Pick up passenger at location A",
                    target_data={'item_id': 'passenger', 'delivery_x': 200, 'delivery_y': 200, 'radius': 10.0}
                ),
                Objective(
                    objective_id=2,
                    objective_type=ObjectiveType.DELIVER_ITEM,
                    description="Drop off passenger at location B",
                    target_data={'item_id': 'passenger', 'delivery_x': 700, 'delivery_y': 700, 'radius': 10.0}
                )
            ],
            rewards=[
                Reward(RewardType.MONEY, 500, description="Taxi fare"),
                Reward(RewardType.EXPERIENCE, 50, description="Driving experience")
            ],
            prerequisites=[],
            difficulty=2,
            estimated_time=8.0
        )
        self.missions[self.next_mission_id] = side_quest
        self.next_mission_id += 1
        
        print(f"📜 Initialized {len(self.missions)} default missions")
    
    def start_mission(self, mission_id: int) -> bool:
        """Start a mission"""
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        
        # Check prerequisites
        for prereq_id in mission.prerequisites:
            if prereq_id not in self.completed_missions:
                print(f"❌ Cannot start mission {mission_id}: prerequisite {prereq_id} not completed")
                return False
        
        # Check if mission is available
        if mission.status != MissionStatus.AVAILABLE:
            print(f"❌ Cannot start mission {mission_id}: not available")
            return False
        
        # Start mission
        mission.status = MissionStatus.ACTIVE
        mission.start_time = time.time()
        self.active_missions.append(mission_id)
        
        print(f"📜 Started mission: {mission.name}")
        return True
    
    def update_missions(self, dt: float, game_state: Dict[str, Any]) -> List[int]:
        """Update all active missions"""
        completed_missions = []
        
        for mission_id in self.active_missions.copy():
            mission = self.missions[mission_id]
            
            # Update mission objectives
            all_objectives_completed = True
            for objective in mission.objectives:
                if not objective.is_completed:
                    # Execute objective script
                    script_name = objective.objective_type.value
                    if self.mission_script.execute_script(script_name, objective, game_state):
                        objective.is_completed = True
                        objective.completion_time = time.time()
                        print(f"📜 Completed objective: {objective.description}")
                    else:
                        all_objectives_completed = False
            
            # Check if mission is completed
            if all_objectives_completed:
                self._complete_mission(mission_id)
                completed_missions.append(mission_id)
        
        return completed_missions
    
    def _complete_mission(self, mission_id: int):
        """Complete a mission"""
        mission = self.missions[mission_id]
        mission.status = MissionStatus.COMPLETED
        mission.completion_time = time.time()
        
        # Remove from active missions
        if mission_id in self.active_missions:
            self.active_missions.remove(mission_id)
        
        # Add to completed missions
        self.completed_missions.add(mission_id)
        
        # Award rewards
        self._award_rewards(mission)
        
        # Unlock dependent missions
        self._unlock_dependent_missions(mission_id)
        
        self.total_missions_completed += 1
        
        print(f"📜 Completed mission: {mission.name}")
    
    def _award_rewards(self, mission: Mission):
        """Award mission rewards"""
        for reward in mission.rewards:
            self.total_rewards_earned += reward.amount
            print(f"🎁 Reward: {reward.description} (+{reward.amount})")
    
    def _unlock_dependent_missions(self, completed_mission_id: int):
        """Unlock missions that depend on the completed mission"""
        for mission in self.missions.values():
            if completed_mission_id in mission.prerequisites:
                # Check if all prerequisites are met
                all_prereqs_met = all(prereq_id in self.completed_missions 
                                    for prereq_id in mission.prerequisites)
                
                if all_prereqs_met and mission.status == MissionStatus.LOCKED:
                    mission.status = MissionStatus.AVAILABLE
                    print(f"📜 Unlocked mission: {mission.name}")
    
    def get_available_missions(self) -> List[Mission]:
        """Get list of available missions"""
        return [mission for mission in self.missions.values() 
                if mission.status == MissionStatus.AVAILABLE]
    
    def get_active_missions(self) -> List[Mission]:
        """Get list of active missions"""
        return [self.missions[mission_id] for mission_id in self.active_missions]
    
    def get_mission_statistics(self) -> Dict[str, Any]:
        """Get mission system statistics"""
        mission_counts = {}
        for mission in self.missions.values():
            mission_type = mission.mission_type.value
            mission_counts[mission_type] = mission_counts.get(mission_type, 0) + 1
        
        return {
            'total_missions': len(self.missions),
            'active_missions': len(self.active_missions),
            'completed_missions': len(self.completed_missions),
            'mission_types': mission_counts,
            'total_completed': self.total_missions_completed,
            'total_rewards_earned': self.total_rewards_earned
        }
    
    def save_missions(self, filename: str):
        """Save missions to file"""
        mission_data = {}
        for mission_id, mission in self.missions.items():
            mission_data[mission_id] = {
                'name': mission.name,
                'description': mission.description,
                'mission_type': mission.mission_type.value,
                'status': mission.status.value,
                'objectives': [
                    {
                        'objective_type': obj.objective_type.value,
                        'description': obj.description,
                        'target_data': obj.target_data,
                        'is_completed': obj.is_completed,
                        'is_optional': obj.is_optional
                    }
                    for obj in mission.objectives
                ],
                'rewards': [
                    {
                        'reward_type': reward.reward_type.value,
                        'amount': reward.amount,
                        'description': reward.description
                    }
                    for reward in mission.rewards
                ],
                'prerequisites': mission.prerequisites,
                'difficulty': mission.difficulty,
                'estimated_time': mission.estimated_time
            }
        
        with open(filename, 'w') as f:
            json.dump(mission_data, f, indent=2)
        
        print(f"📜 Saved missions to {filename}")
    
    def load_missions(self, filename: str):
        """Load missions from file"""
        try:
            with open(filename, 'r') as f:
                mission_data = json.load(f)
            
            self.missions.clear()
            
            for mission_id_str, data in mission_data.items():
                mission_id = int(mission_id_str)
                
                objectives = []
                for obj_data in data['objectives']:
                    objective = Objective(
                        objective_id=len(objectives) + 1,
                        objective_type=ObjectiveType(obj_data['objective_type']),
                        description=obj_data['description'],
                        target_data=obj_data['target_data'],
                        is_completed=obj_data['is_completed'],
                        is_optional=obj_data['is_optional']
                    )
                    objectives.append(objective)
                
                rewards = []
                for reward_data in data['rewards']:
                    reward = Reward(
                        reward_type=RewardType(reward_data['reward_type']),
                        amount=reward_data['amount'],
                        description=reward_data['description']
                    )
                    rewards.append(reward)
                
                mission = Mission(
                    mission_id=mission_id,
                    name=data['name'],
                    description=data['description'],
                    mission_type=MissionType(data['mission_type']),
                    status=MissionStatus(data['status']),
                    objectives=objectives,
                    rewards=rewards,
                    prerequisites=data['prerequisites'],
                    difficulty=data['difficulty'],
                    estimated_time=data['estimated_time']
                )
                
                self.missions[mission_id] = mission
            
            print(f"📜 Loaded missions from {filename}")
            
        except Exception as e:
            print(f"❌ Failed to load missions: {e}")


# Test the mission system
if __name__ == "__main__":
    print("🧪 Testing Mission System...")
    
    # Create dependencies
    from saiyanquest.physics_manager import PhysicsManager
    from saiyanquest.vehicle_physics import VehiclePhysicsSystem
    from saiyanquest.character_ai import CharacterAIManager
    from saiyanquest.world_3d_system import World3DSystem
    
    physics_manager = PhysicsManager(gravity=(0, 0))
    vehicle_physics = VehiclePhysicsSystem(physics_manager)
    character_ai = CharacterAIManager(physics_manager)
    world_3d = World3DSystem(1000, 1000, 2)
    
    # Create mission manager
    mission_manager = MissionManager(physics_manager, vehicle_physics, character_ai, world_3d)
    
    # Test mission system
    print("Testing mission system...")
    
    # Start tutorial mission
    tutorial_id = 1
    mission_manager.start_mission(tutorial_id)
    
    # Simulate game state
    game_state = {
        'player_x': 500,
        'player_y': 500,
        'player_speed': 0.0,
        'player_vehicle': None,
        'player_hidden': False
    }
    
    # Run simulation
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update missions
        completed = mission_manager.update_missions(dt, game_state)
        
        if completed:
            print(f"Completed missions: {completed}")
        
        if frame % 60 == 0:  # Print every second
            stats = mission_manager.get_mission_statistics()
            print(f"  Frame {frame}: Active = {stats['active_missions']}, "
                  f"Completed = {stats['completed_missions']}")
    
    print("✅ Mission System test completed")
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Mission and Quest System for SaiyanQuest

import pygame
import random
import json
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

class MissionType(Enum):
    STORY = "story"
    SIDE_QUEST = "side_quest"
    RANDOM_EVENT = "random_event"
    GANG_MISSION = "gang_mission"
    HEIST = "heist"
    RACING = "racing"
    DELIVERY = "delivery"
    ASSASSINATION = "assassination"
    ESCORT = "escort"
    COLLECTION = "collection"

class MissionStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"

class ObjectiveType(Enum):
    GO_TO = "go_to"
    KILL_TARGET = "kill_target"
    DESTROY_VEHICLE = "destroy_vehicle"
    COLLECT_ITEM = "collect_item"
    DELIVER_ITEM = "deliver_item"
    ESCORT_NPC = "escort_npc"
    STEAL_VEHICLE = "steal_vehicle"
    SURVIVE_TIME = "survive_time"
    LOSE_COPS = "lose_cops"
    REACH_SPEED = "reach_speed"
    DRIVE_DISTANCE = "drive_distance"

@dataclass
class Objective:
    objective_type: ObjectiveType
    description: str
    target_x: float = 0.0
    target_y: float = 0.0
    target_id: str = ""
    target_count: int = 1
    current_count: int = 0
    completed: bool = False
    optional: bool = False
    
    # Objective-specific data
    data: Dict[str, Any] = field(default_factory=dict)
    
    def check_completion(self, game_state: Dict[str, Any]) -> bool:
        """Check if objective is completed"""
        if self.completed:
            return True
            
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0)
        
        if self.objective_type == ObjectiveType.GO_TO:
            distance = ((player_x - self.target_x)**2 + (player_y - self.target_y)**2)**0.5
            self.completed = distance < self.data.get('radius', 50)
            
        elif self.objective_type == ObjectiveType.KILL_TARGET:
            killed_targets = game_state.get('killed_targets', [])
            self.current_count = sum(1 for target in killed_targets if target == self.target_id)
            self.completed = self.current_count >= self.target_count
            
        elif self.objective_type == ObjectiveType.COLLECT_ITEM:
            collected_items = game_state.get('collected_items', {})
            self.current_count = collected_items.get(self.target_id, 0)
            self.completed = self.current_count >= self.target_count
            
        elif self.objective_type == ObjectiveType.DESTROY_VEHICLE:
            destroyed_vehicles = game_state.get('destroyed_vehicles', [])
            self.current_count = sum(1 for vehicle in destroyed_vehicles if vehicle == self.target_id)
            self.completed = self.current_count >= self.target_count
            
        elif self.objective_type == ObjectiveType.LOSE_COPS:
            wanted_level = game_state.get('wanted_level', 0)
            self.completed = wanted_level == 0
            
        elif self.objective_type == ObjectiveType.SURVIVE_TIME:
            mission_time = game_state.get('mission_time', 0)
            target_time = self.data.get('time', 60)
            self.completed = mission_time >= target_time
            
        elif self.objective_type == ObjectiveType.REACH_SPEED:
            current_speed = game_state.get('player_speed', 0)
            target_speed = self.data.get('speed', 100)
            self.completed = current_speed >= target_speed
            
        return self.completed

@dataclass 
class MissionReward:
    money: int = 0
    respect: int = 0
    items: List[str] = field(default_factory=list)
    vehicles: List[str] = field(default_factory=list)
    safe_houses: List[str] = field(default_factory=list)
    weapons: List[str] = field(default_factory=list)

class Mission:
    def __init__(self, mission_id: str, title: str, description: str, 
                 mission_type: MissionType = MissionType.SIDE_QUEST):
        self.mission_id = mission_id
        self.title = title
        self.description = description
        self.mission_type = mission_type
        self.status = MissionStatus.AVAILABLE
        
        # Mission flow
        self.objectives: List[Objective] = []
        self.current_objective_index = 0
        self.start_time = 0.0
        self.time_limit = 0.0  # 0 = no limit
        
        # Requirements
        self.required_level = 1
        self.required_missions: List[str] = []
        self.required_respect = 0
        
        # Location and NPCs
        self.start_x = 0.0
        self.start_y = 0.0
        self.contact_npc = ""
        
        # Rewards
        self.rewards = MissionReward()
        
        # Mission state
        self.mission_data: Dict[str, Any] = {}
        self.cutscene_played = False
        
        # Callbacks
        self.on_start: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_fail: Optional[Callable] = None

    def can_start(self, player_level: int, completed_missions: List[str], 
                  player_respect: int) -> bool:
        """Check if mission can be started"""
        if self.status != MissionStatus.AVAILABLE:
            return False
            
        if player_level < self.required_level:
            return False
            
        if player_respect < self.required_respect:
            return False
            
        for required_mission in self.required_missions:
            if required_mission not in completed_missions:
                return False
                
        return True

    def start(self, game_state: Dict[str, Any]) -> None:
        """Start the mission"""
        self.status = MissionStatus.ACTIVE
        self.start_time = game_state.get('game_time', 0)
        self.current_objective_index = 0
        
        if self.on_start:
            self.on_start(self, game_state)

    def update(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update mission progress"""
        if self.status != MissionStatus.ACTIVE:
            return
            
        # Check time limit
        if self.time_limit > 0:
            elapsed_time = game_state.get('game_time', 0) - self.start_time
            if elapsed_time > self.time_limit:
                self.fail()
                return
        
        # Update current objective
        if self.current_objective_index < len(self.objectives):
            current_obj = self.objectives[self.current_objective_index]
            
            if current_obj.check_completion(game_state):
                self.current_objective_index += 1
                
                # Check if all objectives completed
                if self.current_objective_index >= len(self.objectives):
                    self.complete()

    def complete(self) -> None:
        """Complete the mission"""
        self.status = MissionStatus.COMPLETED
        
        if self.on_complete:
            self.on_complete(self, {})

    def fail(self) -> None:
        """Fail the mission"""
        self.status = MissionStatus.FAILED
        
        if self.on_fail:
            self.on_fail(self, {})

    def get_current_objective(self) -> Optional[Objective]:
        """Get the current active objective"""
        if 0 <= self.current_objective_index < len(self.objectives):
            return self.objectives[self.current_objective_index]
        return None

    def add_objective(self, objective: Objective) -> None:
        """Add an objective to the mission"""
        self.objectives.append(objective)

class MissionFactory:
    """Factory class for creating different types of missions"""
    
    @staticmethod
    def create_story_mission(mission_id: str, title: str, description: str) -> Mission:
        """Create a story mission"""
        mission = Mission(mission_id, title, description, MissionType.STORY)
        return mission
    
    @staticmethod
    def create_gang_mission(gang_name: str, difficulty: int = 1) -> Mission:
        """Create a random gang mission"""
        mission_types = [
            "Take out rival gang members",
            "Steal a shipment",
            "Defend territory",
            "Drive-by shooting"
        ]
        
        mission_type = random.choice(mission_types)
        mission_id = f"gang_{gang_name}_{random.randint(1000, 9999)}"
        title = f"{gang_name}: {mission_type}"
        
        mission = Mission(mission_id, title, f"Help {gang_name} with {mission_type.lower()}",
                         MissionType.GANG_MISSION)
        
        # Add rewards based on difficulty
        mission.rewards.money = difficulty * 500
        mission.rewards.respect = difficulty * 10
        
        return mission
    
    @staticmethod 
    def create_heist_mission(target_location: str, payout: int) -> Mission:
        """Create a heist mission"""
        mission_id = f"heist_{target_location.lower().replace(' ', '_')}"
        title = f"Heist: {target_location}"
        description = f"Plan and execute a heist on {target_location}. Big risk, big reward."
        
        mission = Mission(mission_id, title, description, MissionType.HEIST)
        
        # Multi-stage heist
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Scout the target location",
            data={'radius': 100}
        ))
        mission.add_objective(Objective(
            ObjectiveType.COLLECT_ITEM, "Gather equipment", 
            target_id="heist_equipment", target_count=3
        ))
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Execute the heist",
            data={'radius': 50}
        ))
        mission.add_objective(Objective(
            ObjectiveType.LOSE_COPS, "Escape the police"
        ))
        
        mission.rewards.money = payout
        mission.rewards.respect = 50
        mission.time_limit = 600  # 10 minutes
        
        return mission
    
    @staticmethod
    def create_racing_mission(track_name: str, laps: int = 3) -> Mission:
        """Create a racing mission"""
        mission_id = f"race_{track_name.lower().replace(' ', '_')}"
        title = f"Race: {track_name}"
        description = f"Win the race at {track_name} ({laps} laps)"
        
        mission = Mission(mission_id, title, description, MissionType.RACING)
        
        # Racing objectives would need more complex checkpoint system
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Get to the starting line",
            data={'radius': 20}
        ))
        
        mission.rewards.money = 1000
        mission.rewards.respect = 25
        
        return mission
    
    @staticmethod
    def create_delivery_mission(pickup_x: float, pickup_y: float, 
                               delivery_x: float, delivery_y: float) -> Mission:
        """Create a delivery mission"""
        mission_id = f"delivery_{random.randint(1000, 9999)}"
        title = "Package Delivery"
        description = "Pick up and deliver a package. Don't ask what's in it."
        
        mission = Mission(mission_id, title, description, MissionType.DELIVERY)
        
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Pick up the package",
            target_x=pickup_x, target_y=pickup_y,
            data={'radius': 30}
        ))
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Deliver the package", 
            target_x=delivery_x, target_y=delivery_y,
            data={'radius': 30}
        ))
        
        # Calculate payment based on distance
        distance = ((delivery_x - pickup_x)**2 + (delivery_y - pickup_y)**2)**0.5
        mission.rewards.money = int(distance * 0.5) + 200
        
        return mission

class RandomEventGenerator:
    """Generates random events during gameplay"""
    
    def __init__(self):
        self.event_cooldown = 0.0
        self.min_event_interval = 60.0  # seconds
        self.max_event_interval = 180.0
        self.next_event_time = random.uniform(self.min_event_interval, self.max_event_interval)
        
    def update(self, dt: float, game_time: float, player_x: float, player_y: float) -> Optional[Mission]:
        """Check if a random event should occur"""
        if game_time < self.next_event_time:
            return None
            
        # Generate random event
        event = self._generate_random_event(player_x, player_y)
        
        # Set next event time
        self.next_event_time = game_time + random.uniform(
            self.min_event_interval, self.max_event_interval
        )
        
        return event
    
    def _generate_random_event(self, player_x: float, player_y: float) -> Mission:
        """Generate a random event mission"""
        events = [
            self._create_car_chase_event,
            self._create_robbery_event,
            self._create_accident_event,
            self._create_gang_fight_event
        ]
        
        event_creator = random.choice(events)
        return event_creator(player_x, player_y)
    
    def _create_car_chase_event(self, player_x: float, player_y: float) -> Mission:
        """Create a car chase random event"""
        mission = Mission(
            f"chase_{random.randint(1000, 9999)}",
            "High Speed Chase",
            "Help the police catch a criminal, or help the criminal escape!",
            MissionType.RANDOM_EVENT
        )
        
        # Event occurs nearby
        event_x = player_x + random.uniform(-200, 200)
        event_y = player_y + random.uniform(-200, 200)
        
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Investigate the chase",
            target_x=event_x, target_y=event_y,
            data={'radius': 100}
        ))
        
        mission.rewards.money = 500
        mission.rewards.respect = 10
        
        return mission
    
    def _create_robbery_event(self, player_x: float, player_y: float) -> Mission:
        """Create a robbery random event"""
        mission = Mission(
            f"robbery_{random.randint(1000, 9999)}",
            "Store Robbery",
            "A store is being robbed nearby. Stop the robbers or join them!",
            MissionType.RANDOM_EVENT
        )
        
        event_x = player_x + random.uniform(-150, 150)
        event_y = player_y + random.uniform(-150, 150)
        
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Go to the robbery",
            target_x=event_x, target_y=event_y,
            data={'radius': 50}
        ))
        
        mission.rewards.money = 300
        mission.time_limit = 120  # 2 minutes to respond
        
        return mission
    
    def _create_accident_event(self, player_x: float, player_y: float) -> Mission:
        """Create a traffic accident event"""
        mission = Mission(
            f"accident_{random.randint(1000, 9999)}",
            "Traffic Accident",
            "There's been an accident. Help out or cause more chaos!",
            MissionType.RANDOM_EVENT
        )
        
        event_x = player_x + random.uniform(-100, 100)
        event_y = player_y + random.uniform(-100, 100)
        
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Check the accident",
            target_x=event_x, target_y=event_y,
            data={'radius': 75}
        ))
        
        mission.rewards.money = 100
        mission.rewards.respect = 5
        
        return mission
    
    def _create_gang_fight_event(self, player_x: float, player_y: float) -> Mission:
        """Create a gang fight random event"""
        mission = Mission(
            f"gang_fight_{random.randint(1000, 9999)}",
            "Gang War",
            "Two gangs are fighting in the streets. Pick a side or stay neutral!",
            MissionType.RANDOM_EVENT
        )
        
        event_x = player_x + random.uniform(-250, 250)
        event_y = player_y + random.uniform(-250, 250)
        
        mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Find the gang fight",
            target_x=event_x, target_y=event_y,
            data={'radius': 100}
        ))
        
        mission.rewards.money = 750
        mission.rewards.respect = 20
        mission.time_limit = 300  # 5 minutes
        
        return mission

class MissionManager:
    """Manages all missions and quests in the game"""
    
    def __init__(self):
        self.available_missions: List[Mission] = []
        self.active_missions: List[Mission] = []
        self.completed_missions: List[str] = []
        self.failed_missions: List[str] = []
        
        self.random_event_generator = RandomEventGenerator()
        
        # Mission givers (NPCs that give missions)
        self.mission_givers: Dict[str, List[str]] = {}
        
        # Player stats for mission requirements
        self.player_level = 1
        self.player_respect = 0
        
    def load_missions_from_file(self, filename: str) -> None:
        """Load missions from a JSON file"""
        try:
            with open(filename, 'r') as f:
                mission_data = json.load(f)
                
            for mission_json in mission_data.get('missions', []):
                mission = self._create_mission_from_json(mission_json)
                self.available_missions.append(mission)
                
        except FileNotFoundError:
            print(f"Mission file {filename} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON in mission file {filename}")
    
    def _create_mission_from_json(self, mission_json: Dict) -> Mission:
        """Create a mission from JSON data"""
        mission = Mission(
            mission_json['id'],
            mission_json['title'], 
            mission_json['description'],
            MissionType(mission_json.get('type', 'side_quest'))
        )
        
        # Set properties
        mission.required_level = mission_json.get('required_level', 1)
        mission.required_respect = mission_json.get('required_respect', 0)
        mission.required_missions = mission_json.get('required_missions', [])
        mission.time_limit = mission_json.get('time_limit', 0)
        mission.start_x = mission_json.get('start_x', 0)
        mission.start_y = mission_json.get('start_y', 0)
        
        # Create objectives
        for obj_data in mission_json.get('objectives', []):
            objective = Objective(
                ObjectiveType(obj_data['type']),
                obj_data['description'],
                obj_data.get('target_x', 0),
                obj_data.get('target_y', 0),
                obj_data.get('target_id', ''),
                obj_data.get('target_count', 1),
                data=obj_data.get('data', {})
            )
            mission.add_objective(objective)
        
        # Set rewards
        rewards_data = mission_json.get('rewards', {})
        mission.rewards = MissionReward(
            money=rewards_data.get('money', 0),
            respect=rewards_data.get('respect', 0),
            items=rewards_data.get('items', []),
            vehicles=rewards_data.get('vehicles', []),
            weapons=rewards_data.get('weapons', [])
        )
        
        return mission
    
    def update(self, dt: float, game_state: Dict[str, Any]) -> None:
        """Update all active missions and check for random events"""
        game_time = game_state.get('game_time', 0)
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0)
        
        # Update active missions
        for mission in self.active_missions[:]:  # Copy to avoid modification during iteration
            mission.update(dt, game_state)
            
            if mission.status == MissionStatus.COMPLETED:
                self._complete_mission(mission)
                self.active_missions.remove(mission)
                self.completed_missions.append(mission.mission_id)
                
            elif mission.status == MissionStatus.FAILED:
                self._fail_mission(mission)
                self.active_missions.remove(mission)
                self.failed_missions.append(mission.mission_id)
        
        # Check for random events
        random_event = self.random_event_generator.update(dt, game_time, player_x, player_y)
        if random_event:
            self.available_missions.append(random_event)
    
    def start_mission(self, mission_id: str, game_state: Dict[str, Any]) -> bool:
        """Start a mission by ID"""
        for mission in self.available_missions:
            if mission.mission_id == mission_id:
                if mission.can_start(self.player_level, self.completed_missions, self.player_respect):
                    mission.start(game_state)
                    self.active_missions.append(mission)
                    self.available_missions.remove(mission)
                    return True
                break
        return False
    
    def abandon_mission(self, mission_id: str) -> bool:
        """Abandon an active mission"""
        for mission in self.active_missions:
            if mission.mission_id == mission_id:
                mission.status = MissionStatus.AVAILABLE
                self.active_missions.remove(mission)
                self.available_missions.append(mission)
                return True
        return False
    
    def get_available_missions_for_npc(self, npc_id: str) -> List[Mission]:
        """Get available missions for a specific NPC"""
        npc_missions = self.mission_givers.get(npc_id, [])
        return [m for m in self.available_missions if m.mission_id in npc_missions]
    
    def _complete_mission(self, mission: Mission) -> None:
        """Handle mission completion"""
        # Award rewards
        # This would integrate with the player's inventory/stats system
        print(f"Mission completed: {mission.title}")
        print(f"Rewards: ${mission.rewards.money}, Respect +{mission.rewards.respect}")
        
        self.player_respect += mission.rewards.respect
    
    def _fail_mission(self, mission: Mission) -> None:
        """Handle mission failure"""
        print(f"Mission failed: {mission.title}")
    
    def get_mission_by_id(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by its ID"""
        all_missions = self.available_missions + self.active_missions
        for mission in all_missions:
            if mission.mission_id == mission_id:
                return mission
        return None
    
    def add_mission_giver(self, npc_id: str, mission_ids: List[str]) -> None:
        """Add an NPC as a mission giver"""
        self.mission_givers[npc_id] = mission_ids
        
    def create_sample_missions(self) -> None:
        """Create some sample missions for testing"""
        # Story mission
        story_mission = MissionFactory.create_story_mission(
            "intro_001", "Welcome to Los Santos", 
            "Learn the basics of surviving in the city"
        )
        story_mission.add_objective(Objective(
            ObjectiveType.GO_TO, "Go to Grove Street",
            target_x=2337, target_y=3109, data={'radius': 100}
        ))
        self.available_missions.append(story_mission)
        
        # Gang mission
        gang_mission = MissionFactory.create_gang_mission("Grove Street Families", 2)
        gang_mission.start_x = 2300
        gang_mission.start_y = 3100
        self.available_missions.append(gang_mission)
        
        # Heist
        heist = MissionFactory.create_heist_mission("Los Santos Bank", 50000)
        heist.start_x = 4000
        heist.start_y = 2200
        self.available_missions.append(heist)
        
        # Delivery
        delivery = MissionFactory.create_delivery_mission(1000, 1000, 3000, 3000)
        self.available_missions.append(delivery)
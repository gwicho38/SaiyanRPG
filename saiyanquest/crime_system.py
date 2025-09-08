#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Crime and Wanted System for SaiyanQuest

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from .gta_world import WantedLevel

class CrimeType(Enum):
    JAYWALKING = "jaywalking"
    SPEEDING = "speeding"
    RECKLESS_DRIVING = "reckless_driving"
    HIT_AND_RUN = "hit_and_run"
    VEHICLE_THEFT = "vehicle_theft"
    ASSAULT = "assault"
    MURDER = "murder"
    PROPERTY_DAMAGE = "property_damage"
    ARMED_ROBBERY = "armed_robbery"
    BANK_ROBBERY = "bank_robbery"
    DRUG_DEALING = "drug_dealing"
    GANG_VIOLENCE = "gang_violence"
    POLICE_ASSAULT = "police_assault"
    MILITARY_ASSAULT = "military_assault"
    MASS_DESTRUCTION = "mass_destruction"

@dataclass
class Crime:
    crime_type: CrimeType
    severity: float  # 0.1 to 5.0
    location: Tuple[float, float]
    timestamp: float
    witnessed: bool = True
    reported: bool = False
    
    def get_wanted_increase(self) -> int:
        """Get how much this crime increases wanted level"""
        severity_map = {
            CrimeType.JAYWALKING: 0,
            CrimeType.SPEEDING: 0,
            CrimeType.RECKLESS_DRIVING: 1,
            CrimeType.HIT_AND_RUN: 1,
            CrimeType.VEHICLE_THEFT: 1,
            CrimeType.ASSAULT: 1,
            CrimeType.MURDER: 2,
            CrimeType.PROPERTY_DAMAGE: 1,
            CrimeType.ARMED_ROBBERY: 2,
            CrimeType.BANK_ROBBERY: 3,
            CrimeType.DRUG_DEALING: 1,
            CrimeType.GANG_VIOLENCE: 2,
            CrimeType.POLICE_ASSAULT: 3,
            CrimeType.MILITARY_ASSAULT: 4,
            CrimeType.MASS_DESTRUCTION: 5
        }
        
        base_increase = severity_map.get(self.crime_type, 1)
        return min(5, int(base_increase * self.severity))

class WantedLevelSystem:
    def __init__(self):
        self.current_level = WantedLevel.NONE
        self.heat_points = 0.0  # Internal heat system
        self.max_heat = 1000.0
        self.decay_rate = 1.0  # Heat points lost per second when hiding
        self.last_crime_time = 0.0
        self.last_seen_time = 0.0
        
        # Areas where player can hide
        self.safe_zones = []  # List of pygame.Rect safe areas
        self.in_safe_zone = False
        
        # Police response
        self.response_escalation = {
            WantedLevel.ONE_STAR: {"units": 2, "vehicles": ["police"], "aggressiveness": 0.3},
            WantedLevel.TWO_STAR: {"units": 4, "vehicles": ["police"], "aggressiveness": 0.5},
            WantedLevel.THREE_STAR: {"units": 6, "vehicles": ["police", "swat_van"], "aggressiveness": 0.7},
            WantedLevel.FOUR_STAR: {"units": 8, "vehicles": ["police", "swat_van", "helicopter"], "aggressiveness": 0.8},
            WantedLevel.FIVE_STAR: {"units": 12, "vehicles": ["police", "swat_van", "helicopter", "tank"], "aggressiveness": 1.0}
        }
        
    def add_crime(self, crime: Crime, player_visible: bool = True) -> None:
        """Add a crime and update wanted level"""
        if not crime.witnessed:
            return
            
        # Add heat points based on crime severity
        heat_increase = crime.severity * 100
        if not player_visible:
            heat_increase *= 0.5  # Reduce if player not clearly seen
            
        self.heat_points = min(self.max_heat, self.heat_points + heat_increase)
        self.last_crime_time = time.time()
        
        if player_visible:
            self.last_seen_time = time.time()
            
        self._update_wanted_level()
        
    def update(self, dt: float, player_x: float, player_y: float, 
               is_player_hidden: bool = False) -> None:
        """Update the wanted system"""
        current_time = time.time()
        
        # Check if player is in safe zone
        self._check_safe_zones(player_x, player_y)
        
        # Decay heat over time when not committing crimes
        if current_time - self.last_crime_time > 5.0:  # 5 seconds since last crime
            decay_multiplier = 1.0
            
            if is_player_hidden or self.in_safe_zone:
                decay_multiplier = 3.0  # Faster decay when hidden
            elif current_time - self.last_seen_time > 30.0:  # Not seen for 30 seconds
                decay_multiplier = 2.0
                
            self.heat_points = max(0, self.heat_points - (self.decay_rate * decay_multiplier * dt))
            self._update_wanted_level()
    
    def _update_wanted_level(self) -> None:
        """Update wanted level based on heat points"""
        old_level = self.current_level
        
        if self.heat_points >= 800:
            self.current_level = WantedLevel.FIVE_STAR
        elif self.heat_points >= 600:
            self.current_level = WantedLevel.FOUR_STAR  
        elif self.heat_points >= 400:
            self.current_level = WantedLevel.THREE_STAR
        elif self.heat_points >= 200:
            self.current_level = WantedLevel.TWO_STAR
        elif self.heat_points >= 100:
            self.current_level = WantedLevel.ONE_STAR
        else:
            self.current_level = WantedLevel.NONE
            
        # Trigger events when wanted level changes
        if old_level != self.current_level:
            self._on_wanted_level_changed(old_level, self.current_level)
    
    def _on_wanted_level_changed(self, old_level: WantedLevel, new_level: WantedLevel) -> None:
        """Handle wanted level changes"""
        if new_level.value > old_level.value:
            print(f"Wanted level increased to {new_level.value} stars!")
        elif new_level.value < old_level.value:
            print(f"Wanted level decreased to {new_level.value} stars")
            
    def _check_safe_zones(self, player_x: float, player_y: float) -> None:
        """Check if player is in a safe zone"""
        self.in_safe_zone = False
        for safe_zone in self.safe_zones:
            if safe_zone.collidepoint(player_x, player_y):
                self.in_safe_zone = True
                break
                
    def add_safe_zone(self, rect: pygame.Rect) -> None:
        """Add a safe zone where wanted level decreases faster"""
        self.safe_zones.append(rect)
        
    def clear_wanted_level(self) -> None:
        """Instantly clear wanted level (cheat/debug)"""
        self.heat_points = 0.0
        self.current_level = WantedLevel.NONE
        
    def get_police_response(self) -> Dict:
        """Get the current police response configuration"""
        return self.response_escalation.get(self.current_level, {"units": 0, "vehicles": [], "aggressiveness": 0})

class CrimeDetector:
    """Detects crimes based on player actions and world state"""
    
    def __init__(self):
        self.last_speed_check = 0.0
        self.speed_check_interval = 1.0  # Check speed every second
        self.last_position = (0.0, 0.0)
        self.collision_cooldown = 0.0
        
    def check_traffic_crimes(self, dt: float, player_x: float, player_y: float, 
                           player_speed: float, player_vehicle: Optional[object] = None) -> List[Crime]:
        """Check for traffic-related crimes"""
        crimes = []
        current_time = time.time()
        
        # Speed check
        if current_time - self.last_speed_check >= self.speed_check_interval:
            if player_vehicle and player_speed > 80:  # Speed limit is ~80 km/h
                severity = min(3.0, (player_speed - 80) / 40)  # Scale severity with speed
                crimes.append(Crime(
                    CrimeType.SPEEDING, 
                    severity,
                    (player_x, player_y),
                    current_time
                ))
            self.last_speed_check = current_time
            
        # Reckless driving (rapid direction changes, high speed in populated areas)
        if player_vehicle and player_speed > 60:
            position_change = math.sqrt((player_x - self.last_position[0])**2 + 
                                      (player_y - self.last_position[1])**2)
            if position_change > 200:  # Rapid movement/direction changes
                crimes.append(Crime(
                    CrimeType.RECKLESS_DRIVING,
                    2.0,
                    (player_x, player_y),
                    current_time
                ))
        
        self.last_position = (player_x, player_y)
        return crimes
    
    def check_vehicle_collision(self, player_vehicle: object, hit_vehicle: object, 
                              damage_dealt: float) -> Optional[Crime]:
        """Check for hit and run or reckless driving from collisions"""
        if self.collision_cooldown > 0:
            return None
            
        self.collision_cooldown = 2.0  # Prevent spam
        
        if damage_dealt > 20:  # Significant damage
            severity = min(3.0, damage_dealt / 30)
            return Crime(
                CrimeType.HIT_AND_RUN,
                severity,
                (player_vehicle.x, player_vehicle.y),
                time.time()
            )
        return None
    
    def check_pedestrian_hit(self, player_x: float, player_y: float, 
                           pedestrian_killed: bool = False) -> Crime:
        """Check for hitting pedestrians"""
        crime_type = CrimeType.MURDER if pedestrian_killed else CrimeType.ASSAULT
        severity = 3.0 if pedestrian_killed else 1.5
        
        return Crime(
            crime_type,
            severity,
            (player_x, player_y),
            time.time()
        )
    
    def check_weapon_crime(self, player_x: float, player_y: float, 
                          target_type: str, target_killed: bool = False) -> Crime:
        """Check for weapon-related crimes"""
        if target_type == "police":
            crime_type = CrimeType.POLICE_ASSAULT
            severity = 4.0 if target_killed else 2.5
        elif target_type == "military":
            crime_type = CrimeType.MILITARY_ASSAULT
            severity = 5.0 if target_killed else 3.0
        else:
            crime_type = CrimeType.MURDER if target_killed else CrimeType.ASSAULT
            severity = 3.0 if target_killed else 1.5
            
        return Crime(
            crime_type,
            severity,
            (player_x, player_y),
            time.time()
        )
    
    def check_theft_crime(self, player_x: float, player_y: float, 
                         stolen_item: str, value: float) -> Crime:
        """Check for theft crimes"""
        if stolen_item == "vehicle":
            return Crime(
                CrimeType.VEHICLE_THEFT,
                min(2.5, value / 20000),  # Scale with vehicle value
                (player_x, player_y),
                time.time()
            )
        else:
            return Crime(
                CrimeType.ARMED_ROBBERY,
                min(3.0, value / 10000),
                (player_x, player_y), 
                time.time()
            )
    
    def check_property_damage(self, player_x: float, player_y: float, 
                            damage_value: float) -> Optional[Crime]:
        """Check for property damage"""
        if damage_value > 500:  # Significant property damage
            severity = min(3.0, damage_value / 5000)
            return Crime(
                CrimeType.PROPERTY_DAMAGE,
                severity,
                (player_x, player_y),
                time.time()
            )
        return None
    
    def update(self, dt: float) -> None:
        """Update crime detector cooldowns"""
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt

class LawEnforcementResponse:
    """Manages law enforcement response to crimes"""
    
    def __init__(self):
        self.active_response = False
        self.response_level = 0
        self.spawn_points = []  # Police spawn locations
        self.roadblocks = []  # Active roadblocks
        self.helicopters = []  # Active helicopters
        
    def update_response(self, wanted_level: WantedLevel, player_x: float, player_y: float) -> None:
        """Update law enforcement response"""
        if wanted_level == WantedLevel.NONE:
            self.active_response = False
            self.response_level = 0
            return
            
        self.active_response = True
        self.response_level = wanted_level.value
        
        # Spawn police based on wanted level
        self._manage_police_units(wanted_level, player_x, player_y)
        
        # Manage special responses
        if wanted_level.value >= 3:
            self._manage_roadblocks(player_x, player_y)
        if wanted_level.value >= 4:
            self._manage_helicopters(player_x, player_y)
            
    def _manage_police_units(self, wanted_level: WantedLevel, player_x: float, player_y: float) -> None:
        """Manage police unit spawning"""
        # This would integrate with the police AI system
        pass
        
    def _manage_roadblocks(self, player_x: float, player_y: float) -> None:
        """Manage roadblock placement"""
        # Place roadblocks on major roads ahead of player
        pass
        
    def _manage_helicopters(self, player_x: float, player_y: float) -> None:
        """Manage police helicopter deployment"""
        # Spawn and manage police helicopters
        pass

class CrimeSystem:
    """Main crime system that coordinates all crime-related functionality"""
    
    def __init__(self):
        self.wanted_system = WantedLevelSystem()
        self.crime_detector = CrimeDetector()
        self.law_enforcement = LawEnforcementResponse()
        
        # Crime statistics
        self.total_crimes_committed = 0
        self.crimes_by_type: Dict[CrimeType, int] = {}
        self.time_spent_wanted = 0.0
        self.max_wanted_level_reached = WantedLevel.NONE
        
        # Witness system
        self.witnesses = []  # NPCs who have seen crimes
        self.witness_cooldown = 0.0
        
    def update(self, dt: float, game_state: Dict) -> None:
        """Update the entire crime system"""
        player_x = game_state.get('player_x', 0)
        player_y = game_state.get('player_y', 0) 
        player_speed = game_state.get('player_speed', 0)
        player_vehicle = game_state.get('player_vehicle')
        is_hidden = game_state.get('player_hidden', False)
        
        # Update wanted level system
        self.wanted_system.update(dt, player_x, player_y, is_hidden)
        
        # Update crime detector
        self.crime_detector.update(dt)
        
        # Check for traffic crimes
        traffic_crimes = self.crime_detector.check_traffic_crimes(
            dt, player_x, player_y, player_speed, player_vehicle
        )
        
        # Process detected crimes
        for crime in traffic_crimes:
            self.commit_crime(crime, game_state)
        
        # Update law enforcement response
        self.law_enforcement.update_response(
            self.wanted_system.current_level, player_x, player_y
        )
        
        # Update statistics
        if self.wanted_system.current_level != WantedLevel.NONE:
            self.time_spent_wanted += dt
            
        if self.wanted_system.current_level.value > self.max_wanted_level_reached.value:
            self.max_wanted_level_reached = self.wanted_system.current_level
    
    def commit_crime(self, crime: Crime, game_state: Dict) -> None:
        """Process a committed crime"""
        # Check if crime was witnessed
        if self._was_crime_witnessed(crime, game_state):
            self.wanted_system.add_crime(crime, True)
            
        # Update statistics
        self.total_crimes_committed += 1
        self.crimes_by_type[crime.crime_type] = self.crimes_by_type.get(crime.crime_type, 0) + 1
        
        print(f"Crime committed: {crime.crime_type.value} (Severity: {crime.severity:.1f})")
    
    def _was_crime_witnessed(self, crime: Crime, game_state: Dict) -> bool:
        """Check if a crime was witnessed by NPCs or police"""
        player_x, player_y = crime.location
        
        # Check for nearby pedestrians (witnesses)
        pedestrians = game_state.get('nearby_pedestrians', [])
        for pedestrian in pedestrians:
            distance = math.sqrt((pedestrian.x - player_x)**2 + (pedestrian.y - player_y)**2)
            if distance < 100:  # Pedestrian saw the crime
                return True
                
        # Check for police visibility
        police_units = game_state.get('nearby_police', [])
        for unit in police_units:
            distance = math.sqrt((unit.x - player_x)**2 + (unit.y - player_y)**2)
            if distance < 200:  # Police saw the crime
                return True
                
        # Random chance of being seen by off-screen witnesses
        return random.random() < 0.3  # 30% chance
    
    def player_hit_pedestrian(self, player_x: float, player_y: float, killed: bool = False) -> None:
        """Report that player hit a pedestrian"""
        crime = self.crime_detector.check_pedestrian_hit(player_x, player_y, killed)
        game_state = {'player_x': player_x, 'player_y': player_y}
        self.commit_crime(crime, game_state)
    
    def player_used_weapon(self, player_x: float, player_y: float, target_type: str, killed: bool = False) -> None:
        """Report weapon use"""
        crime = self.crime_detector.check_weapon_crime(player_x, player_y, target_type, killed)
        game_state = {'player_x': player_x, 'player_y': player_y}
        self.commit_crime(crime, game_state)
    
    def player_stole_item(self, player_x: float, player_y: float, item: str, value: float) -> None:
        """Report theft"""
        crime = self.crime_detector.check_theft_crime(player_x, player_y, item, value)
        game_state = {'player_x': player_x, 'player_y': player_y}
        self.commit_crime(crime, game_state)
    
    def player_damaged_property(self, player_x: float, player_y: float, damage: float) -> None:
        """Report property damage"""
        crime = self.crime_detector.check_property_damage(player_x, player_y, damage)
        if crime:
            game_state = {'player_x': player_x, 'player_y': player_y}
            self.commit_crime(crime, game_state)
    
    def get_wanted_level(self) -> WantedLevel:
        """Get current wanted level"""
        return self.wanted_system.current_level
    
    def get_heat_percentage(self) -> float:
        """Get heat level as percentage (0.0 to 1.0)"""
        return self.wanted_system.heat_points / self.wanted_system.max_heat
    
    def is_in_safe_zone(self) -> bool:
        """Check if player is in a safe zone"""
        return self.wanted_system.in_safe_zone
    
    def add_safe_zone(self, rect: pygame.Rect) -> None:
        """Add a safe zone"""
        self.wanted_system.add_safe_zone(rect)
    
    def cheat_clear_wanted_level(self) -> None:
        """Cheat to clear wanted level"""
        self.wanted_system.clear_wanted_level()
    
    def get_crime_stats(self) -> Dict:
        """Get crime statistics for the player"""
        return {
            'total_crimes': self.total_crimes_committed,
            'crimes_by_type': dict(self.crimes_by_type),
            'time_spent_wanted': self.time_spent_wanted,
            'max_wanted_level': self.max_wanted_level_reached.value,
            'current_wanted_level': self.wanted_system.current_level.value,
            'heat_percentage': self.get_heat_percentage()
        }
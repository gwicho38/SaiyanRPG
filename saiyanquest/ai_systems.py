#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style AI Systems for SaiyanQuest (Pedestrians, Traffic, Police)

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from .vehicle_system import Vehicle, VehicleType, VehicleManager
from .gta_world import GTAWorld, WantedLevel

class PedestrianType(Enum):
    CIVILIAN = "civilian"
    GANG_MEMBER = "gang_member"
    POLICE = "police"
    SECURITY = "security"
    BUSINESSMAN = "businessman"
    TOURIST = "tourist"
    HOMELESS = "homeless"

class PedestrianState(Enum):
    WALKING = "walking"
    STANDING = "standing"
    RUNNING = "running"
    FLEEING = "fleeing"
    FIGHTING = "fighting"
    DEAD = "dead"

class AIState(Enum):
    PATROL = "patrol"
    CHASE = "chase"
    SEARCH = "search"
    BACKUP = "backup"
    INVESTIGATE = "investigate"
    RETREAT = "retreat"

@dataclass
class Pedestrian:
    x: float
    y: float
    pedestrian_type: PedestrianType
    state: PedestrianState = PedestrianState.WALKING
    health: float = 100.0
    fear_level: float = 0.0  # 0.0 to 1.0
    aggression: float = 0.1  # 0.0 to 1.0
    speed: float = 50.0  # pixels per second
    
    # AI behavior
    target_x: float = 0.0
    target_y: float = 0.0
    last_direction_change: float = 0.0
    direction_change_interval: float = 5.0  # seconds
    
    # Visual
    angle: float = 0.0
    color: Tuple[int, int, int] = (100, 100, 100)
    
    def __post_init__(self):
        self.target_x = self.x
        self.target_y = self.y
        self._set_type_properties()
    
    def _set_type_properties(self):
        """Set properties based on pedestrian type"""
        if self.pedestrian_type == PedestrianType.GANG_MEMBER:
            self.aggression = 0.8
            self.speed = 60.0
            self.color = (200, 50, 50)
        elif self.pedestrian_type == PedestrianType.POLICE:
            self.health = 150.0
            self.aggression = 0.6
            self.speed = 70.0
            self.color = (50, 50, 200)
        elif self.pedestrian_type == PedestrianType.BUSINESSMAN:
            self.fear_level = 0.3
            self.speed = 45.0
            self.color = (50, 50, 50)
        elif self.pedestrian_type == PedestrianType.TOURIST:
            self.fear_level = 0.4
            self.speed = 40.0
            self.color = (100, 150, 100)
        elif self.pedestrian_type == PedestrianType.HOMELESS:
            self.health = 80.0
            self.speed = 35.0
            self.color = (120, 80, 60)
        else:  # CIVILIAN
            self.color = (150, 150, 150)

class PoliceAI:
    def __init__(self):
        self.active_units: List[Vehicle] = []
        self.spawn_cooldown = 0.0
        self.last_player_position = (0, 0)
        self.search_radius = 500
        
    def update(self, dt: float, player_x: float, player_y: float, wanted_level: WantedLevel, 
               world: GTAWorld, vehicle_manager: VehicleManager) -> None:
        """Update police AI behavior"""
        self.last_player_position = (player_x, player_y)
        
        # Remove destroyed units
        self.active_units = [unit for unit in self.active_units if not unit.is_destroyed]
        
        # Spawn new units based on wanted level
        if wanted_level != WantedLevel.NONE:
            self._spawn_police_units(dt, wanted_level, world, vehicle_manager)
        
        # Update existing units
        for unit in self.active_units:
            self._update_police_unit(unit, dt, player_x, player_y, wanted_level)
    
    def _spawn_police_units(self, dt: float, wanted_level: WantedLevel, 
                           world: GTAWorld, vehicle_manager: VehicleManager) -> None:
        """Spawn police units based on wanted level"""
        self.spawn_cooldown -= dt
        if self.spawn_cooldown > 0:
            return
            
        max_units = wanted_level.value * 2
        if len(self.active_units) >= max_units:
            return
        
        # Set spawn cooldown
        self.spawn_cooldown = max(5.0 - wanted_level.value, 1.0)
        
        # Spawn location - off screen but near player
        player_x, player_y = self.last_player_position
        spawn_distance = world.get_police_spawn_distance()
        
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player_x + math.cos(angle) * spawn_distance
        spawn_y = player_y + math.sin(angle) * spawn_distance
        
        # Choose vehicle type based on wanted level
        if wanted_level.value >= 4:
            vehicle_type = VehicleType.HELICOPTER if random.random() < 0.3 else VehicleType.POLICE
        else:
            vehicle_type = VehicleType.POLICE
            
        # Spawn police vehicle
        police_vehicle = vehicle_manager.spawn_vehicle(vehicle_type, spawn_x, spawn_y)
        police_vehicle.start_engine()
        police_vehicle.sirens_on = True
        police_vehicle.lights_on = True
        
        # Add AI state
        police_vehicle.ai_state = AIState.CHASE
        police_vehicle.ai_target_x = player_x
        police_vehicle.ai_target_y = player_y
        police_vehicle.ai_aggressive = wanted_level.value >= 3
        
        self.active_units.append(police_vehicle)
    
    def _update_police_unit(self, unit: Vehicle, dt: float, player_x: float, 
                           player_y: float, wanted_level: WantedLevel) -> None:
        """Update individual police unit behavior"""
        # Calculate distance to player
        distance = math.sqrt((unit.x - player_x)**2 + (unit.y - player_y)**2)
        
        if unit.ai_state == AIState.CHASE:
            self._chase_behavior(unit, player_x, player_y, distance)
        elif unit.ai_state == AIState.SEARCH:
            self._search_behavior(unit, dt)
        elif unit.ai_state == AIState.PATROL:
            self._patrol_behavior(unit, dt)
        
        # Switch states based on distance and wanted level
        if distance > 1500 and wanted_level == WantedLevel.NONE:
            unit.ai_state = AIState.RETREAT
        elif distance < 200 and unit.ai_state != AIState.CHASE:
            unit.ai_state = AIState.CHASE
    
    def _chase_behavior(self, unit: Vehicle, player_x: float, player_y: float, distance: float) -> None:
        """Police chase behavior"""
        # Calculate angle to player
        angle_to_player = math.atan2(player_y - unit.y, player_x - unit.x)
        target_angle = math.degrees(angle_to_player) + 90  # +90 for vehicle orientation
        
        # Steering toward player
        angle_diff = (target_angle - unit.angle + 180) % 360 - 180
        unit.steering = max(-1.0, min(1.0, angle_diff / 45.0))
        
        # Throttle based on distance
        if distance > 100:
            unit.throttle = 0.8
        elif distance < 50:
            unit.throttle = -0.2  # Brake when too close
        else:
            unit.throttle = 0.4
        
        # Ramming behavior for high wanted levels
        if distance < 100 and unit.ai_aggressive:
            unit.throttle = 1.0
    
    def _search_behavior(self, unit: Vehicle, dt: float) -> None:
        """Police search behavior when player is hidden"""
        # Simple search pattern - drive in expanding circles
        unit.throttle = 0.3
        unit.steering = 0.2  # Gentle turn
    
    def _patrol_behavior(self, unit: Vehicle, dt: float) -> None:
        """Police patrol behavior"""
        unit.throttle = 0.4
        # Random steering changes
        if random.random() < 0.01:
            unit.steering = random.uniform(-0.5, 0.5)

class TrafficAI:
    def __init__(self):
        self.traffic_lights: Dict[Tuple[int, int], float] = {}  # Position -> timer
        self.intersections: List[Tuple[int, int]] = []
        
    def update_traffic_vehicle(self, vehicle: Vehicle, dt: float, other_vehicles: List[Vehicle],
                              player_x: float, player_y: float) -> None:
        """Update individual traffic vehicle AI"""
        # Simple traffic AI
        
        # Check for obstacles ahead
        obstacle_ahead = self._check_obstacles_ahead(vehicle, other_vehicles)
        
        if obstacle_ahead:
            # Brake and try to change lanes
            vehicle.brake = 0.8
            vehicle.throttle = 0.0
            vehicle.steering = random.choice([-0.3, 0.3])  # Try to change lanes
        else:
            # Normal driving
            vehicle.brake = 0.0
            
            # Maintain speed around 30-60 km/h
            speed = vehicle.get_speed_kmh()
            if speed < 30:
                vehicle.throttle = 0.6
            elif speed > 60:
                vehicle.throttle = 0.2
            else:
                vehicle.throttle = 0.4
        
        # Panic behavior if player is causing chaos nearby
        player_distance = math.sqrt((vehicle.x - player_x)**2 + (vehicle.y - player_y)**2)
        if player_distance < 150:  # Player is close
            # Check if player is in a vehicle and moving fast
            # This would require player state, for now just assume chaos if very close
            if player_distance < 75:
                vehicle.throttle = 1.0  # Speed up to escape
                vehicle.steering = random.uniform(-1.0, 1.0)  # Erratic steering
    
    def _check_obstacles_ahead(self, vehicle: Vehicle, other_vehicles: List[Vehicle]) -> bool:
        """Check if there are obstacles ahead of the vehicle"""
        # Simple forward ray cast
        look_ahead_distance = 100
        angle_rad = math.radians(vehicle.angle - 90)  # -90 for forward direction
        
        end_x = vehicle.x + math.cos(angle_rad) * look_ahead_distance
        end_y = vehicle.y + math.sin(angle_rad) * look_ahead_distance
        
        # Check collision with other vehicles
        for other in other_vehicles:
            if other == vehicle:
                continue
                
            # Simple distance check (could be improved with proper ray casting)
            distance = math.sqrt((other.x - vehicle.x)**2 + (other.y - vehicle.y)**2)
            if distance < 80:  # Too close
                return True
        
        return False

class PedestrianManager:
    def __init__(self):
        self.pedestrians: List[Pedestrian] = []
        self.spawn_timer = 0.0
        self.max_pedestrians = 100
        
    def spawn_pedestrian(self, x: float, y: float, pedestrian_type: PedestrianType = None) -> Pedestrian:
        """Spawn a new pedestrian"""
        if pedestrian_type is None:
            # Random civilian type with gang member chance in certain areas
            if random.random() < 0.1:  # 10% chance
                pedestrian_type = random.choice([
                    PedestrianType.GANG_MEMBER,
                    PedestrianType.BUSINESSMAN,
                    PedestrianType.TOURIST,
                    PedestrianType.HOMELESS
                ])
            else:
                pedestrian_type = PedestrianType.CIVILIAN
        
        pedestrian = Pedestrian(x, y, pedestrian_type)
        self.pedestrians.append(pedestrian)
        return pedestrian
    
    def spawn_random_pedestrians(self, spawn_area: pygame.Rect, density: float) -> None:
        """Spawn random pedestrians in an area"""
        if len(self.pedestrians) >= self.max_pedestrians:
            return
            
        spawn_count = int(density * 5)  # Base spawn count
        
        for _ in range(spawn_count):
            if len(self.pedestrians) >= self.max_pedestrians:
                break
                
            x = random.randint(spawn_area.x, spawn_area.x + spawn_area.width)
            y = random.randint(spawn_area.y, spawn_area.y + spawn_area.height)
            
            self.spawn_pedestrian(x, y)
    
    def update_pedestrians(self, dt: float, player_x: float, player_y: float, 
                          chaos_level: float, world: GTAWorld) -> None:
        """Update all pedestrians"""
        despawn_distance = 800
        
        for pedestrian in self.pedestrians[:]:  # Copy list to avoid modification during iteration
            # Remove pedestrians too far from player
            distance = math.sqrt((pedestrian.x - player_x)**2 + (pedestrian.y - player_y)**2)
            if distance > despawn_distance:
                self.pedestrians.remove(pedestrian)
                continue
            
            # Update individual pedestrian
            self._update_pedestrian(pedestrian, dt, player_x, player_y, chaos_level)
    
    def _update_pedestrian(self, pedestrian: Pedestrian, dt: float, 
                          player_x: float, player_y: float, chaos_level: float) -> None:
        """Update individual pedestrian behavior"""
        distance_to_player = math.sqrt(
            (pedestrian.x - player_x)**2 + (pedestrian.y - player_y)**2
        )
        
        # React to player proximity and chaos
        if distance_to_player < 100 and chaos_level > 0.3:
            # Start fleeing
            if pedestrian.state != PedestrianState.FLEEING:
                pedestrian.state = PedestrianState.FLEEING
                # Set flee direction (away from player)
                flee_angle = math.atan2(pedestrian.y - player_y, pedestrian.x - player_x)
                pedestrian.target_x = pedestrian.x + math.cos(flee_angle) * 200
                pedestrian.target_y = pedestrian.y + math.sin(flee_angle) * 200
                pedestrian.speed = 120  # Run fast
        
        elif pedestrian.state == PedestrianState.FLEEING and distance_to_player > 200:
            # Stop fleeing
            pedestrian.state = PedestrianState.WALKING
            pedestrian.speed = 50
        
        # Movement
        if pedestrian.state in [PedestrianState.WALKING, PedestrianState.FLEEING]:
            # Move toward target
            dx = pedestrian.target_x - pedestrian.x
            dy = pedestrian.target_y - pedestrian.y
            distance_to_target = math.sqrt(dx**2 + dy**2)
            
            if distance_to_target < 20:  # Reached target
                self._set_new_target(pedestrian)
            else:
                # Move toward target
                pedestrian.x += (dx / distance_to_target) * pedestrian.speed * dt
                pedestrian.y += (dy / distance_to_target) * pedestrian.speed * dt
                pedestrian.angle = math.degrees(math.atan2(dy, dx))
        
        # Update behavior timers
        pedestrian.last_direction_change += dt
        if (pedestrian.last_direction_change > pedestrian.direction_change_interval and 
            pedestrian.state == PedestrianState.WALKING):
            self._set_new_target(pedestrian)
            pedestrian.last_direction_change = 0
            pedestrian.direction_change_interval = random.uniform(3, 8)
    
    def _set_new_target(self, pedestrian: Pedestrian) -> None:
        """Set a new random target for the pedestrian"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, 150)
        
        pedestrian.target_x = pedestrian.x + math.cos(angle) * distance
        pedestrian.target_y = pedestrian.y + math.sin(angle) * distance
    
    def get_pedestrians_in_area(self, x: float, y: float, radius: float) -> List[Pedestrian]:
        """Get all pedestrians in a circular area"""
        result = []
        for pedestrian in self.pedestrians:
            distance = math.sqrt((pedestrian.x - x)**2 + (pedestrian.y - y)**2)
            if distance <= radius:
                result.append(pedestrian)
        return result
    
    def kill_pedestrian(self, pedestrian: Pedestrian) -> None:
        """Kill a pedestrian (for crime system)"""
        pedestrian.state = PedestrianState.DEAD
        pedestrian.health = 0


class AIManager:
    """Main manager for all AI systems"""
    
    def __init__(self):
        self.police_ai = PoliceAI()
        self.traffic_ai = TrafficAI()
        self.pedestrian_manager = PedestrianManager()
        
        # Crime system integration
        self.last_crime_position = (0, 0)
        self.crime_cooldown = 0.0
    
    def update(self, dt: float, player_x: float, player_y: float, 
               world: GTAWorld, vehicle_manager: VehicleManager) -> None:
        """Update all AI systems"""
        
        # Update police AI
        self.police_ai.update(dt, player_x, player_y, world.wanted_level, 
                             world, vehicle_manager)
        
        # Update traffic AI
        for vehicle in vehicle_manager.traffic_vehicles:
            self.traffic_ai.update_traffic_vehicle(
                vehicle, dt, vehicle_manager.traffic_vehicles + vehicle_manager.vehicles,
                player_x, player_y
            )
        
        # Update pedestrians
        self.pedestrian_manager.update_pedestrians(dt, player_x, player_y, 
                                                  world.chaos_level, world)
        
        # Spawn pedestrians based on current district
        current_district = world.get_current_district(player_x, player_y)
        if current_district:
            spawn_area = pygame.Rect(
                player_x - 400, player_y - 400, 800, 800
            )
            self.pedestrian_manager.spawn_random_pedestrians(
                spawn_area, current_district.pedestrian_density
            )
    
    def report_crime(self, x: float, y: float, severity: float) -> None:
        """Report a crime to increase wanted level"""
        self.last_crime_position = (x, y)
        
        # Increase chaos level
        # This would be handled by the world system
        
        # Crime cooldown to prevent spam
        self.crime_cooldown = 5.0
    
    def get_nearby_pedestrians(self, x: float, y: float, radius: float = 100) -> List[Pedestrian]:
        """Get pedestrians near a position"""
        return self.pedestrian_manager.get_pedestrians_in_area(x, y, radius)
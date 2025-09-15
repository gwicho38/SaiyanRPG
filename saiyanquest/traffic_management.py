#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Traffic Management System with AI-Controlled Vehicles

import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from .vehicle_physics import VehiclePhysicsSystem, VehicleState
from .world_3d_system import World3DSystem, DistrictType
from .physics_manager import PhysicsManager


class TrafficDensity(Enum):
    """Traffic density levels"""
    EMPTY = 0.0
    LIGHT = 0.3
    MODERATE = 0.6
    HEAVY = 0.8
    EXTREME = 1.0


class TrafficBehavior(Enum):
    """Traffic behavior patterns"""
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    EMERGENCY = "emergency"
    DRUNK = "drunk"


class TrafficLane(Enum):
    """Traffic lane types"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    EMERGENCY = "emergency"


@dataclass
class TrafficSpawnPoint:
    """Traffic spawn point configuration"""
    position: Tuple[float, float]
    direction: Tuple[float, float]  # Normalized direction vector
    lane_type: TrafficLane
    district_id: int
    spawn_probability: float
    vehicle_types: List[str]
    speed_limit: float
    is_active: bool = True


@dataclass
class TrafficRoute:
    """Traffic route definition"""
    route_id: int
    waypoints: List[Tuple[float, float]]
    district_sequence: List[int]
    preferred_speed: float
    lane_preference: TrafficLane
    route_type: str  # "commuter", "delivery", "emergency", "leisure"


@dataclass
class TrafficVehicle:
    """AI-controlled traffic vehicle"""
    vehicle_id: int
    route: Optional[TrafficRoute]
    current_waypoint_index: int
    behavior: TrafficBehavior
    target_speed: float
    lane_position: float  # -1.0 to 1.0 (left to right)
    following_distance: float
    last_lane_change: float
    patience_level: float  # 0.0 to 1.0
    aggression_level: float  # 0.0 to 1.0
    reaction_time: float
    is_emergency_vehicle: bool = False


class TrafficAI:
    """AI controller for traffic vehicles"""
    
    def __init__(self, vehicle_id: int, behavior: TrafficBehavior = TrafficBehavior.NORMAL):
        self.vehicle_id = vehicle_id
        self.behavior = behavior
        
        # AI parameters based on behavior
        self._set_behavior_parameters()
        
        # State tracking
        self.current_target: Optional[Tuple[float, float]] = None
        self.avoidance_target: Optional[Tuple[float, float]] = None
        self.lane_change_timer = 0.0
        self.obstacle_detection_timer = 0.0
        
        # Decision making
        self.decision_timer = 0.0
        self.last_decision = "continue"
        
    def _set_behavior_parameters(self):
        """Set AI parameters based on behavior type"""
        if self.behavior == TrafficBehavior.NORMAL:
            self.aggression = 0.5
            self.patience = 0.7
            self.reaction_time = 1.0
            self.following_distance = 2.0
            self.speed_variance = 0.1
        elif self.behavior == TrafficBehavior.AGGRESSIVE:
            self.aggression = 0.8
            self.patience = 0.3
            self.reaction_time = 0.5
            self.following_distance = 1.0
            self.speed_variance = 0.2
        elif self.behavior == TrafficBehavior.CAUTIOUS:
            self.aggression = 0.2
            self.patience = 0.9
            self.reaction_time = 2.0
            self.following_distance = 3.0
            self.speed_variance = 0.05
        elif self.behavior == TrafficBehavior.EMERGENCY:
            self.aggression = 0.9
            self.patience = 0.1
            self.reaction_time = 0.3
            self.following_distance = 0.5
            self.speed_variance = 0.0
        else:  # DRUNK
            self.aggression = 0.6
            self.patience = 0.4
            self.reaction_time = 3.0
            self.following_distance = 1.5
            self.speed_variance = 0.3
    
    def update(self, dt: float, vehicle_physics: VehiclePhysicsSystem, 
               world_3d: World3DSystem, traffic_manager) -> Tuple[float, float, float, bool]:
        """Update AI and return control inputs"""
        self.decision_timer += dt
        self.lane_change_timer += dt
        self.obstacle_detection_timer += dt
        
        # Get current vehicle state
        position = vehicle_physics.get_vehicle_position(self.vehicle_id)
        speed = vehicle_physics.get_vehicle_speed(self.vehicle_id)
        angle = vehicle_physics.get_vehicle_angle(self.vehicle_id)
        
        # Make decisions periodically
        if self.decision_timer >= self.reaction_time:
            self._make_decision(vehicle_physics, world_3d, traffic_manager)
            self.decision_timer = 0.0
        
        # Calculate inputs based on current decision
        throttle, brake, steering, handbrake = self._calculate_inputs(
            position, speed, angle, vehicle_physics, world_3d, traffic_manager
        )
        
        return throttle, brake, steering, handbrake
    
    def _make_decision(self, vehicle_physics: VehiclePhysicsSystem, 
                      world_3d: World3DSystem, traffic_manager):
        """Make high-level driving decisions"""
        position = vehicle_physics.get_vehicle_position(self.vehicle_id)
        speed = vehicle_physics.get_vehicle_speed(self.vehicle_id)
        
        # Check for obstacles ahead
        obstacle_ahead = self._check_obstacles_ahead(position, vehicle_physics, traffic_manager)
        
        # Check for lane change opportunities
        lane_change_opportunity = self._check_lane_change_opportunity(position, traffic_manager)
        
        # Make decision based on situation
        if obstacle_ahead and lane_change_opportunity and self.lane_change_timer > 2.0:
            self.last_decision = "lane_change"
            self.lane_change_timer = 0.0
        elif obstacle_ahead:
            self.last_decision = "brake"
        elif speed < self._get_target_speed() * 0.8:
            self.last_decision = "accelerate"
        else:
            self.last_decision = "continue"
    
    def _check_obstacles_ahead(self, position: Tuple[float, float], 
                              vehicle_physics: VehiclePhysicsSystem, 
                              traffic_manager) -> bool:
        """Check for obstacles ahead of the vehicle"""
        # Get vehicle angle
        angle = vehicle_physics.get_vehicle_angle(self.vehicle_id)
        
        # Calculate look-ahead distance
        look_ahead_distance = 50.0 + vehicle_physics.get_vehicle_speed(self.vehicle_id) * 2.0
        
        # Calculate look-ahead position
        look_ahead_x = position[0] + math.cos(angle) * look_ahead_distance
        look_ahead_y = position[1] + math.sin(angle) * look_ahead_distance
        
        # Check for other vehicles in the path
        for other_vehicle_id in traffic_manager.traffic_vehicles.keys():
            if other_vehicle_id == self.vehicle_id:
                continue
            
            other_position = vehicle_physics.get_vehicle_position(other_vehicle_id)
            distance = math.sqrt(
                (other_position[0] - look_ahead_x)**2 + 
                (other_position[1] - look_ahead_y)**2
            )
            
            if distance < 30.0:  # Within 30 units
                return True
        
        return False
    
    def _check_lane_change_opportunity(self, position: Tuple[float, float], 
                                     traffic_manager) -> bool:
        """Check if lane change is safe and beneficial"""
        # Simple implementation - check if adjacent lanes are clear
        # In a real implementation, this would be more sophisticated
        
        # Check left lane
        left_clear = self._check_lane_clear(position, -1.0, traffic_manager)
        # Check right lane  
        right_clear = self._check_lane_clear(position, 1.0, traffic_manager)
        
        return left_clear or right_clear
    
    def _check_lane_clear(self, position: Tuple[float, float], 
                         lane_offset: float, traffic_manager) -> bool:
        """Check if a specific lane is clear"""
        # Calculate lane position
        lane_x = position[0] + lane_offset * 20.0  # 20 units lane width
        
        # Check for vehicles in this lane
        for other_vehicle_id in traffic_manager.traffic_vehicles.keys():
            if other_vehicle_id == self.vehicle_id:
                continue
            
            other_position = traffic_manager.vehicle_physics.get_vehicle_position(other_vehicle_id)
            distance = abs(other_position[0] - lane_x)
            
            if distance < 15.0:  # Too close
                return False
        
        return True
    
    def _get_target_speed(self) -> float:
        """Get target speed based on behavior and conditions"""
        base_speed = 15.0  # m/s base speed
        
        # Adjust based on behavior
        if self.behavior == TrafficBehavior.AGGRESSIVE:
            base_speed *= 1.3
        elif self.behavior == TrafficBehavior.CAUTIOUS:
            base_speed *= 0.8
        elif self.behavior == TrafficBehavior.EMERGENCY:
            base_speed *= 1.5
        elif self.behavior == TrafficBehavior.DRUNK:
            base_speed *= 0.9
        
        # Add some randomness
        variance = random.uniform(-self.speed_variance, self.speed_variance)
        return base_speed * (1.0 + variance)
    
    def _calculate_inputs(self, position: Tuple[float, float], speed: float, 
                          angle: float, vehicle_physics: VehiclePhysicsSystem,
                          world_3d: World3DSystem, traffic_manager) -> Tuple[float, float, float, bool]:
        """Calculate vehicle control inputs"""
        target_speed = self._get_target_speed()
        
        # Calculate throttle and brake
        speed_error = target_speed - speed
        
        if speed_error > 1.0:
            throttle = min(0.8, speed_error / target_speed)
            brake = 0.0
        elif speed_error < -2.0:
            throttle = 0.0
            brake = min(0.8, abs(speed_error) / target_speed)
        else:
            throttle = 0.3  # Maintain speed
            brake = 0.0
        
        # Calculate steering
        steering = 0.0
        
        if self.last_decision == "lane_change":
            # Simple lane change steering
            steering = random.uniform(-0.3, 0.3)
        else:
            # Follow road or avoid obstacles
            steering = self._calculate_steering(position, angle, world_3d, traffic_manager)
        
        return throttle, brake, steering, False
    
    def _calculate_steering(self, position: Tuple[float, float], angle: float,
                           world_3d: World3DSystem, traffic_manager) -> float:
        """Calculate steering angle to follow road or avoid obstacles"""
        # Simple implementation - random steering with slight bias toward road
        base_steering = random.uniform(-0.1, 0.1)
        
        # Add some road-following behavior
        # In a real implementation, this would use the navigation system
        district = world_3d.get_district_at_position(position[0], position[1])
        if district:
            # Slight bias toward district center
            center_x, center_y = district.center
            dx = center_x - position[0]
            dy = center_y - position[1]
            
            if abs(dx) > 10.0:  # Far from center
                road_steering = 0.1 if dx > 0 else -0.1
                base_steering += road_steering * 0.3
        
        return max(-0.5, min(0.5, base_steering))


class TrafficManager:
    """Main traffic management system"""
    
    def __init__(self, vehicle_physics: VehiclePhysicsSystem, world_3d: World3DSystem):
        self.vehicle_physics = vehicle_physics
        self.world_3d = world_3d
        
        # Traffic configuration
        self.traffic_density = TrafficDensity.MODERATE
        self.max_vehicles = 100
        self.spawn_interval = 2.0  # seconds
        self.despawn_distance = 500.0  # units
        
        # Traffic data
        self.traffic_vehicles: Dict[int, TrafficVehicle] = {}
        self.traffic_ai: Dict[int, TrafficAI] = {}
        self.spawn_points: List[TrafficSpawnPoint] = []
        self.traffic_routes: List[TrafficRoute] = []
        
        # Statistics
        self.total_vehicles_spawned = 0
        self.total_vehicles_despawned = 0
        self.average_speed = 0.0
        self.traffic_flow_rate = 0.0
        
        # Timing
        self.last_spawn_time = 0.0
        self.update_timer = 0.0
        
        # Initialize traffic system
        self._initialize_traffic_system()
        
        print("🚦 TrafficManager initialized")
    
    def _initialize_traffic_system(self):
        """Initialize traffic spawn points and routes"""
        # Create spawn points around the world
        self._create_spawn_points()
        
        # Create traffic routes
        self._create_traffic_routes()
        
        print(f"🚦 Created {len(self.spawn_points)} spawn points and {len(self.traffic_routes)} routes")
    
    def _create_spawn_points(self):
        """Create traffic spawn points around the world"""
        # Edge spawn points
        edge_positions = [
            # North edge
            (500, 0), (400, 0), (600, 0), (300, 0), (700, 0),
            # South edge  
            (500, 1000), (400, 1000), (600, 1000), (300, 1000), (700, 1000),
            # West edge
            (0, 500), (0, 400), (0, 600), (0, 300), (0, 700),
            # East edge
            (1000, 500), (1000, 400), (1000, 600), (1000, 300), (1000, 700)
        ]
        
        for i, (x, y) in enumerate(edge_positions):
            # Determine direction based on position
            if y == 0:  # North edge
                direction = (0, 1)
                lane_type = TrafficLane.CENTER
            elif y == 1000:  # South edge
                direction = (0, -1)
                lane_type = TrafficLane.CENTER
            elif x == 0:  # West edge
                direction = (1, 0)
                lane_type = TrafficLane.CENTER
            else:  # East edge
                direction = (-1, 0)
                lane_type = TrafficLane.CENTER
            
            # Get district
            district_id = 1  # Default to downtown
            district = self.world_3d.get_district_at_position(x, y)
            if district:
                district_id = district.district_id
            
            spawn_point = TrafficSpawnPoint(
                position=(x, y),
                direction=direction,
                lane_type=lane_type,
                district_id=district_id,
                spawn_probability=0.7,
                vehicle_types=['sedan', 'sports_car', 'truck', 'motorcycle'],
                speed_limit=15.0
            )
            
            self.spawn_points.append(spawn_point)
    
    def _create_traffic_routes(self):
        """Create traffic routes between districts"""
        # Simple routes between district centers
        districts = list(self.world_3d.districts.values())
        
        for i, district_a in enumerate(districts):
            for j, district_b in enumerate(districts):
                if i != j:
                    route = TrafficRoute(
                        route_id=len(self.traffic_routes) + 1,
                        waypoints=[district_a.center, district_b.center],
                        district_sequence=[district_a.district_id, district_b.district_id],
                        preferred_speed=15.0,
                        lane_preference=TrafficLane.CENTER,
                        route_type="commuter"
                    )
                    self.traffic_routes.append(route)
    
    def update(self, dt: float, player_position: Tuple[float, float]) -> None:
        """Update traffic management system"""
        self.update_timer += dt
        
        # Update traffic density based on player location
        self._update_traffic_density(player_position)
        
        # Spawn new vehicles
        self._spawn_vehicles(dt)
        
        # Update existing traffic vehicles
        self._update_traffic_vehicles(dt)
        
        # Despawn distant vehicles
        self._despawn_distant_vehicles(player_position)
        
        # Update statistics
        self._update_statistics(dt)
    
    def _update_traffic_density(self, player_position: Tuple[float, float]):
        """Update traffic density based on player location"""
        district = self.world_3d.get_district_at_position(player_position[0], player_position[1])
        
        if district:
            if district.district_type == DistrictType.DOWNTOWN:
                self.traffic_density = TrafficDensity.HEAVY
            elif district.district_type == DistrictType.COMMERCIAL:
                self.traffic_density = TrafficDensity.MODERATE
            elif district.district_type == DistrictType.RESIDENTIAL:
                self.traffic_density = TrafficDensity.LIGHT
            else:  # INDUSTRIAL
                self.traffic_density = TrafficDensity.LIGHT
    
    def _spawn_vehicles(self, dt: float):
        """Spawn new traffic vehicles"""
        current_time = time.time()
        
        if current_time - self.last_spawn_time < self.spawn_interval:
            return
        
        # Check if we can spawn more vehicles
        if len(self.traffic_vehicles) >= self.max_vehicles:
            return
        
        # Calculate spawn probability based on density
        spawn_probability = self.traffic_density.value * 0.1  # 0-10% chance per interval
        
        if random.random() < spawn_probability:
            self._spawn_traffic_vehicle()
            self.last_spawn_time = current_time
    
    def _spawn_traffic_vehicle(self):
        """Spawn a single traffic vehicle"""
        # Select spawn point
        active_spawn_points = [sp for sp in self.spawn_points if sp.is_active]
        if not active_spawn_points:
            return
        
        spawn_point = random.choice(active_spawn_points)
        
        # Select vehicle type
        vehicle_type = random.choice(spawn_point.vehicle_types)
        
        # Spawn vehicle
        vehicle_id = self.vehicle_physics.create_vehicle(
            vehicle_type, spawn_point.position
        )
        
        # Select behavior
        behavior_weights = {
            TrafficBehavior.NORMAL: 0.7,
            TrafficBehavior.AGGRESSIVE: 0.15,
            TrafficBehavior.CAUTIOUS: 0.1,
            TrafficBehavior.DRUNK: 0.05
        }
        
        behavior = random.choices(
            list(behavior_weights.keys()),
            weights=list(behavior_weights.values())
        )[0]
        
        # Create traffic vehicle data
        traffic_vehicle = TrafficVehicle(
            vehicle_id=vehicle_id,
            route=None,  # Will be assigned later
            current_waypoint_index=0,
            behavior=behavior,
            target_speed=spawn_point.speed_limit,
            lane_position=0.0,
            following_distance=2.0,
            last_lane_change=0.0,
            patience_level=0.7,
            aggression_level=0.5,
            reaction_time=1.0
        )
        
        # Create AI controller
        traffic_ai = TrafficAI(vehicle_id, behavior)
        
        # Store references
        self.traffic_vehicles[vehicle_id] = traffic_vehicle
        self.traffic_ai[vehicle_id] = traffic_ai
        
        self.total_vehicles_spawned += 1
        
        print(f"🚦 Spawned traffic vehicle {vehicle_id} ({vehicle_type}, {behavior.value})")
    
    def _update_traffic_vehicles(self, dt: float):
        """Update all traffic vehicles"""
        for vehicle_id, traffic_vehicle in list(self.traffic_vehicles.items()):
            # Get AI inputs
            traffic_ai = self.traffic_ai.get(vehicle_id)
            if not traffic_ai:
                continue
            
            throttle, brake, steering, handbrake = traffic_ai.update(
                dt, self.vehicle_physics, self.world_3d, self
            )
            
            # Apply inputs to vehicle
            self.vehicle_physics.update_vehicle(
                vehicle_id, dt, throttle, brake, steering, handbrake
            )
            
            # Update traffic vehicle data
            traffic_vehicle.last_lane_change += dt
    
    def _despawn_distant_vehicles(self, player_position: Tuple[float, float]):
        """Despawn vehicles that are too far from player"""
        vehicles_to_despawn = []
        
        for vehicle_id, traffic_vehicle in self.traffic_vehicles.items():
            vehicle_position = self.vehicle_physics.get_vehicle_position(vehicle_id)
            distance = math.sqrt(
                (vehicle_position[0] - player_position[0])**2 +
                (vehicle_position[1] - player_position[1])**2
            )
            
            if distance > self.despawn_distance:
                vehicles_to_despawn.append(vehicle_id)
        
        # Despawn vehicles
        for vehicle_id in vehicles_to_despawn:
            self._despawn_traffic_vehicle(vehicle_id)
    
    def _despawn_traffic_vehicle(self, vehicle_id: int):
        """Despawn a traffic vehicle"""
        if vehicle_id in self.traffic_vehicles:
            # Remove from vehicle physics
            self.vehicle_physics.remove_vehicle(vehicle_id)
            
            # Remove from traffic data
            del self.traffic_vehicles[vehicle_id]
            if vehicle_id in self.traffic_ai:
                del self.traffic_ai[vehicle_id]
            
            self.total_vehicles_despawned += 1
    
    def _update_statistics(self, dt: float):
        """Update traffic statistics"""
        if not self.traffic_vehicles:
            self.average_speed = 0.0
            return
        
        # Calculate average speed
        total_speed = 0.0
        for vehicle_id in self.traffic_vehicles.keys():
            speed = self.vehicle_physics.get_vehicle_speed(vehicle_id)
            total_speed += speed
        
        self.average_speed = total_speed / len(self.traffic_vehicles)
        
        # Calculate traffic flow rate
        self.traffic_flow_rate = len(self.traffic_vehicles) / self.max_vehicles
    
    def set_traffic_density(self, density: TrafficDensity):
        """Set traffic density level"""
        self.traffic_density = density
        print(f"🚦 Traffic density set to {density.name}")
    
    def get_traffic_statistics(self) -> Dict[str, Any]:
        """Get traffic system statistics"""
        behavior_counts = {}
        for traffic_vehicle in self.traffic_vehicles.values():
            behavior = traffic_vehicle.behavior.value
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        
        return {
            'total_vehicles': len(self.traffic_vehicles),
            'max_vehicles': self.max_vehicles,
            'traffic_density': self.traffic_density.name,
            'average_speed': self.average_speed,
            'traffic_flow_rate': self.traffic_flow_rate,
            'total_spawned': self.total_vehicles_spawned,
            'total_despawned': self.total_vehicles_despawned,
            'behavior_distribution': behavior_counts,
            'spawn_points': len(self.spawn_points),
            'traffic_routes': len(self.traffic_routes)
        }


# Test the traffic management system
if __name__ == "__main__":
    print("🧪 Testing Traffic Management System...")
    
    # Create dependencies
    from saiyanquest.physics_manager import PhysicsManager
    from saiyanquest.vehicle_physics import VehiclePhysicsSystem
    from saiyanquest.world_3d_system import World3DSystem
    
    physics_manager = PhysicsManager(gravity=(0, 0))
    vehicle_physics = VehiclePhysicsSystem(physics_manager)
    world_3d = World3DSystem(1000, 1000, 2)
    
    # Create districts
    world_3d.create_district("Downtown", DistrictType.DOWNTOWN, (0, 0, 499, 499))
    world_3d.create_district("Residential", DistrictType.RESIDENTIAL, (500, 0, 999, 499))
    world_3d.create_district("Commercial", DistrictType.COMMERCIAL, (0, 500, 499, 999))
    world_3d.create_district("Industrial", DistrictType.INDUSTRIAL, (500, 500, 999, 999))
    
    # Create traffic manager
    traffic_manager = TrafficManager(vehicle_physics, world_3d)
    
    # Test traffic simulation
    player_position = (500, 500)  # Center of world
    
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update traffic
        traffic_manager.update(dt, player_position)
        
        # Update physics
        physics_manager.update(dt)
        
        if frame % 60 == 0:  # Print every second
            stats = traffic_manager.get_traffic_statistics()
            print(f"  Frame {frame}: Vehicles = {stats['total_vehicles']}, "
                  f"Avg Speed = {stats['average_speed']:.1f} m/s, "
                  f"Density = {stats['traffic_density']}")
    
    print("✅ Traffic Management System test completed")
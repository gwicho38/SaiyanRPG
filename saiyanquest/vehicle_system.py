#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# GTA-style Vehicle System for SaiyanQuest with Physics Integration

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Import our new physics system
from .physics_manager import (
    PhysicsManager, PhysicsBody, PhysicsBodyType,
    CollisionCategory, CollisionInfo
)
from .tire_physics import VehicleTireSystem, TireType
from .vehicle_electrical import VehicleElectricalSystem, ElectricalComponent
from .vehicle_mechanical import VehicleMechanicalSystem, MechanicalFailureType
from .vehicle_effects import VehicleEffectsSystem

class VehicleType(Enum):
    SEDAN = "sedan"
    SPORTS_CAR = "sports_car"
    MUSCLE_CAR = "muscle_car"
    SUV = "suv"
    TRUCK = "truck"
    VAN = "van"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    BUS = "bus"
    TAXI = "taxi"
    POLICE = "police"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    HELICOPTER = "helicopter"
    BOAT = "boat"
    TANK = "tank"  # Special military vehicle

@dataclass
class VehicleStats:
    max_speed: float
    acceleration: float
    handling: float
    durability: float
    weight: float
    fuel_capacity: float = 100.0
    seats: int = 4
    has_radio: bool = True
    has_weapons: bool = False

class Vehicle:
    def __init__(self, vehicle_type: VehicleType, x: float, y: float, angle: float = 0):
        self.vehicle_type = vehicle_type
        
        # Create physics body
        self.physics_manager = PhysicsManager(gravity=(0, 0))
        
        # Get vehicle stats for physics configuration
        self.stats = self._get_vehicle_stats()
        
        # Create physics body (convert pixels to meters)
        physics_x = x / 16.0  # 16 pixels per meter
        physics_y = y / 16.0
        physics_angle = math.radians(angle)
        
        # Determine vehicle dimensions based on type
        width, height = self._get_vehicle_dimensions(vehicle_type)
        
        self.physics_body = self.physics_manager.create_body(
            PhysicsBodyType.DYNAMIC,
            position=(physics_x, physics_y),
            shape_data={'type': 'box', 'width': width, 'height': height, 'mass': self.stats.weight},
            collision_category=CollisionCategory.VEHICLE,
            user_data=self
        )
        
        # Set initial angle
        self.physics_body.angle = physics_angle
        
        # Initialize advanced tire physics system
        tire_type = self._get_tire_type_for_vehicle(vehicle_type)
        wheelbase = self._get_wheelbase(vehicle_type)
        self.tire_system = VehicleTireSystem(tire_type, wheelbase)
        
        # Initialize electrical system
        self.electrical_system = VehicleElectricalSystem(vehicle_type.value)
        
        # Initialize mechanical system  
        self.mechanical_system = VehicleMechanicalSystem(vehicle_type.value)
        
        # Initialize visual effects system
        self.effects_system = VehicleEffectsSystem()
        
        # Vehicle state (Carnage3D-inspired)
        self.engine_on = False
        self.fuel = 100.0
        self.damage_level = 0.0  # 0.0 = perfect, 1.0 = wrecked
        self.is_burning = False
        self.is_wrecked = False
        self.is_in_water = False
        self.emergency_lights = False
        
        # Passenger system
        self.passengers = {}  # seat_id -> character
        self.max_passengers = self.stats.seats
        
        # Door system
        self.doors = {
            'driver': {'open': False, 'animation_time': 0.0},
            'passenger': {'open': False, 'animation_time': 0.0},
            'rear_left': {'open': False, 'animation_time': 0.0},
            'rear_right': {'open': False, 'animation_time': 0.0}
        }
        
        # Physics-based driving controls
        self.throttle = 0.0  # -1.0 to 1.0
        self.steering = 0.0  # -1.0 to 1.0
        self.brake = 0.0     # 0.0 to 1.0
        
        print(f"🚗 Created {vehicle_type.value} vehicle with physics at ({x}, {y})")
    
    @property
    def x(self) -> float:
        """Get vehicle X position in pixels"""
        return self.physics_body.position[0] * 16.0
    
    @property
    def y(self) -> float:
        """Get vehicle Y position in pixels"""
        return self.physics_body.position[1] * 16.0
    
    @property
    def angle(self) -> float:
        """Get vehicle angle in degrees"""
        return math.degrees(self.physics_body.angle)
    
    @property
    def velocity_x(self) -> float:
        """Get velocity X component in pixels/second"""
        return self.physics_body.velocity[0] * 16.0
    
    @property
    def velocity_y(self) -> float:
        """Get velocity Y component in pixels/second"""
        return self.physics_body.velocity[1] * 16.0
    
    @property
    def speed(self) -> float:
        """Get current speed in pixels/second"""
        vx, vy = self.physics_body.velocity
        return math.sqrt(vx*vx + vy*vy) * 16.0
    
    def _get_vehicle_dimensions(self, vehicle_type: VehicleType) -> Tuple[float, float]:
        """Get vehicle dimensions in meters for physics"""
        if vehicle_type in [VehicleType.TRUCK, VehicleType.BUS]:
            return (2.5, 5.0)  # Large vehicles
        elif vehicle_type == VehicleType.MOTORCYCLE:
            return (1.0, 2.0)  # Small vehicles
        else:
            return (2.0, 4.0)  # Standard cars
    
    def _get_tire_type_for_vehicle(self, vehicle_type: VehicleType) -> TireType:
        """Get appropriate tire type for vehicle"""
        tire_map = {
            VehicleType.SPORTS_CAR: TireType.SPORT,
            VehicleType.MUSCLE_CAR: TireType.SPORT,
            VehicleType.TRUCK: TireType.OFFROAD,
            VehicleType.SUV: TireType.OFFROAD,
            VehicleType.POLICE: TireType.SPORT,
            VehicleType.FIRE_TRUCK: TireType.OFFROAD,
            VehicleType.AMBULANCE: TireType.STANDARD,
            VehicleType.TAXI: TireType.STANDARD,
            VehicleType.BICYCLE: TireType.STANDARD,
            VehicleType.BUS: TireType.STANDARD,
            VehicleType.VAN: TireType.STANDARD,
            VehicleType.MOTORCYCLE: TireType.SPORT,
            VehicleType.HELICOPTER: TireType.STANDARD,  # Landing gear
            VehicleType.BOAT: TireType.STANDARD,       # Not used
            VehicleType.TANK: TireType.OFFROAD,
        }
        return tire_map.get(vehicle_type, TireType.STANDARD)
    
    def _get_wheelbase(self, vehicle_type: VehicleType) -> float:
        """Get wheelbase for vehicle type (in meters)"""
        wheelbase_map = {
            VehicleType.SEDAN: 2.7,
            VehicleType.SPORTS_CAR: 2.5,
            VehicleType.MUSCLE_CAR: 2.8,
            VehicleType.SUV: 3.0,
            VehicleType.TRUCK: 3.5,
            VehicleType.VAN: 3.2,
            VehicleType.MOTORCYCLE: 1.5,
            VehicleType.BICYCLE: 1.1,
            VehicleType.BUS: 6.0,
            VehicleType.TAXI: 2.7,
            VehicleType.POLICE: 2.8,
            VehicleType.AMBULANCE: 3.2,
            VehicleType.FIRE_TRUCK: 5.5,
            VehicleType.HELICOPTER: 4.0,
            VehicleType.BOAT: 4.0,
            VehicleType.TANK: 4.5,
        }
        return wheelbase_map.get(vehicle_type, 2.7)

    def _get_vehicle_stats(self) -> VehicleStats:
        """Get stats based on vehicle type"""
        stats_map = {
            VehicleType.SEDAN: VehicleStats(
                max_speed=120, acceleration=0.5, handling=0.7, durability=0.6, weight=1500
            ),
            VehicleType.SPORTS_CAR: VehicleStats(
                max_speed=200, acceleration=0.9, handling=0.9, durability=0.4, weight=1200
            ),
            VehicleType.MUSCLE_CAR: VehicleStats(
                max_speed=160, acceleration=0.8, handling=0.6, durability=0.7, weight=1800
            ),
            VehicleType.SUV: VehicleStats(
                max_speed=110, acceleration=0.4, handling=0.5, durability=0.8, weight=2500, seats=7
            ),
            VehicleType.TRUCK: VehicleStats(
                max_speed=90, acceleration=0.3, handling=0.4, durability=0.9, weight=3500, seats=2
            ),
            VehicleType.VAN: VehicleStats(
                max_speed=100, acceleration=0.4, handling=0.5, durability=0.7, weight=2000, seats=8
            ),
            VehicleType.MOTORCYCLE: VehicleStats(
                max_speed=180, acceleration=0.8, handling=1.0, durability=0.2, weight=300, seats=2
            ),
            VehicleType.BICYCLE: VehicleStats(
                max_speed=30, acceleration=0.6, handling=1.0, durability=0.1, weight=15, 
                fuel_capacity=0, seats=1, has_radio=False
            ),
            VehicleType.BUS: VehicleStats(
                max_speed=80, acceleration=0.2, handling=0.3, durability=0.9, weight=8000, seats=40
            ),
            VehicleType.TAXI: VehicleStats(
                max_speed=130, acceleration=0.5, handling=0.7, durability=0.6, weight=1500
            ),
            VehicleType.POLICE: VehicleStats(
                max_speed=150, acceleration=0.7, handling=0.8, durability=0.7, weight=1600
            ),
            VehicleType.AMBULANCE: VehicleStats(
                max_speed=140, acceleration=0.6, handling=0.6, durability=0.8, weight=2500, seats=6
            ),
            VehicleType.FIRE_TRUCK: VehicleStats(
                max_speed=100, acceleration=0.3, handling=0.4, durability=1.0, weight=12000, seats=6
            ),
            VehicleType.HELICOPTER: VehicleStats(
                max_speed=200, acceleration=0.5, handling=0.9, durability=0.5, weight=2000, seats=4
            ),
            VehicleType.BOAT: VehicleStats(
                max_speed=80, acceleration=0.4, handling=0.6, durability=0.7, weight=1000, seats=6
            ),
            VehicleType.TANK: VehicleStats(
                max_speed=60, acceleration=0.2, handling=0.2, durability=2.0, weight=50000, 
                seats=4, has_weapons=True
            ),
        }
        return stats_map.get(self.vehicle_type, VehicleStats(100, 0.5, 0.5, 0.5, 1500))

    def update(self, dt: float) -> None:
        """Update vehicle physics and state using Box2D physics"""
        # Update electrical system
        self.electrical_system.update(dt, self.engine_on)
        
        # Update mechanical system
        vehicle_speed_kmh = self.get_speed_kmh()
        self.mechanical_system.update(dt, self.throttle, self.brake, vehicle_speed_kmh)
        
        # Sync engine state with mechanical system
        if self.mechanical_system.engine_running != self.engine_on:
            if self.mechanical_system.engine_running and not self.engine_on:
                self.engine_on = True
            elif not self.mechanical_system.engine_running and self.engine_on:
                self.engine_on = False
        
        # Update fuel consumption (now controlled by mechanical system)
        if self.engine_on and self.stats.fuel_capacity > 0:
            # Base fuel consumption from mechanical system efficiency
            base_consumption = 0.01 * dt  # Base idle consumption
            load_consumption = abs(self.throttle) * 0.1 * dt  # Load-based consumption
            
            # Apply mechanical system efficiency
            fuel_consumption = (base_consumption + load_consumption) / self.mechanical_system.efficiency_multiplier
            
            self.fuel = max(0, self.fuel - fuel_consumption)
            
            if self.fuel <= 0:
                self.engine_on = False
                self.mechanical_system.stop_engine()
        
        # Apply driving forces if engine is on
        if self.engine_on or self.vehicle_type == VehicleType.BICYCLE:
            self._apply_driving_forces(dt)
        
        # Update damage effects
        self._update_damage_effects(dt)
        
        # Update door animations
        self._update_door_animations(dt)
        
        # Update electrical components based on vehicle state
        self._update_electrical_components()
        
        # Update visual effects system
        self.effects_system.update(dt, self)
    
    def _apply_driving_forces(self, dt: float) -> None:
        """Apply advanced tire-based driving forces"""
        if self.is_wrecked:
            return
        
        # Get current vehicle state
        vehicle_velocity = self.physics_body.velocity
        vehicle_angular_velocity = self.physics_body.angular_velocity
        vehicle_angle = self.physics_body.angle
        
        # Get mechanical system power output
        engine_power = self.mechanical_system.get_engine_power()
        power_factor = engine_power / self.mechanical_system.engine_stats.max_power if engine_power > 0 else 0.0
        
        # Apply brake effectiveness from mechanical system
        effective_brake = self.brake * self.mechanical_system.get_brake_effectiveness()
        
        # Use advanced tire physics to calculate forces
        tire_force_x, tire_force_y, tire_torque = self.tire_system.calculate_vehicle_forces(
            vehicle_velocity, vehicle_angular_velocity, vehicle_angle,
            self.throttle, self.steering, effective_brake
        )
        
        # Apply power and mechanical condition factors
        tire_force_x *= power_factor
        tire_force_y *= power_factor
        
        # Reduce forces if damaged
        damage_factor = 1.0 - (self.damage_level * 0.5)
        tire_force_x *= damage_factor
        tire_force_y *= damage_factor
        tire_torque *= damage_factor
        
        # Apply calculated forces to physics body
        if abs(tire_force_x) > 0.1 or abs(tire_force_y) > 0.1:
            self.physics_body.apply_force((tire_force_x, tire_force_y))
        
        # Apply torque for turning
        if abs(tire_torque) > 0.1:
            self.physics_body.body.ApplyTorque(tire_torque, True)
    
    # Carnage3D-inspired collision handling
    def on_collision_begin(self, collision_info: CollisionInfo) -> None:
        """Handle collision start (called by physics system)"""
        other = collision_info.body_b if collision_info.body_a == self.physics_body else collision_info.body_a
        
        if hasattr(other.game_object, 'vehicle_type'):  # Vehicle-vehicle collision
            self._handle_vehicle_collision(other.game_object, collision_info)
        elif hasattr(other.game_object, 'character_type'):  # Vehicle-pedestrian collision
            self._handle_pedestrian_collision(other.game_object, collision_info)
        else:  # Vehicle-world collision
            self._handle_world_collision(collision_info)
    
    def on_collision_impact(self, other_body: 'PhysicsBody', impact_force: float) -> None:
        """Handle significant collision impact"""
        # Calculate damage based on impact force and vehicle durability
        damage_amount = max(0, (impact_force - 1000) / 10000) / self.stats.durability
        self.take_damage(damage_amount)
        
        print(f"🚗 Vehicle collision! Impact: {impact_force:.1f}, Damage: {damage_amount:.3f}")
    
    def _handle_vehicle_collision(self, other_vehicle: 'Vehicle', collision_info: CollisionInfo) -> None:
        """Handle collision with another vehicle"""
        # Calculate relative speed
        my_velocity = self.physics_body.velocity
        other_velocity = other_vehicle.physics_body.velocity
        relative_speed = math.sqrt(
            (my_velocity[0] - other_velocity[0])**2 + 
            (my_velocity[1] - other_velocity[1])**2
        )
        
        # Apply damage based on relative speed and mass difference
        mass_ratio = other_vehicle.stats.weight / self.stats.weight
        damage = (relative_speed * mass_ratio) / 1000 / self.stats.durability
        self.take_damage(damage)
    
    def _handle_pedestrian_collision(self, pedestrian, collision_info: CollisionInfo) -> None:
        """Handle collision with pedestrian"""
        # Pedestrian takes most of the damage, vehicle takes minimal damage
        if hasattr(pedestrian, 'take_damage'):
            pedestrian.take_damage(self.speed / 10)  # Speed-based damage
        
        # Small damage to vehicle
        self.take_damage(0.001)
    
    def _handle_world_collision(self, collision_info: CollisionInfo) -> None:
        """Handle collision with world/buildings"""
        # Take damage based on current speed
        damage = (self.speed / 100) / self.stats.durability
        self.take_damage(damage)
    
    def take_damage(self, amount: float) -> None:
        """Apply damage to vehicle"""
        self.damage_level = min(1.0, self.damage_level + amount)
        
        # Check if vehicle becomes wrecked
        if self.damage_level >= 0.8 and not self.is_wrecked:
            self.is_wrecked = True
            self.engine_on = False
            print(f"🔥 Vehicle wrecked! ({self.vehicle_type.value})")
        
        # Check if vehicle catches fire
        if self.damage_level >= 0.9 and not self.is_burning:
            self.is_burning = True
            print(f"🔥 Vehicle on fire! ({self.vehicle_type.value})")
    
    def repair(self, amount: float = 1.0) -> None:
        """Repair vehicle damage"""
        self.damage_level = max(0.0, self.damage_level - amount)
        
        if self.damage_level < 0.8:
            self.is_wrecked = False
        
        if self.damage_level < 0.9:
            self.is_burning = False
    
    # Passenger management (Carnage3D-inspired)
    def add_passenger(self, character, seat_id: str = "driver") -> bool:
        """Add passenger to specific seat"""
        if seat_id in self.passengers or len(self.passengers) >= self.max_passengers:
            return False
        
        self.passengers[seat_id] = character
        
        # Open appropriate door
        if seat_id in self.doors:
            self.open_door(seat_id)
        
        print(f"👤 {character} entered {self.vehicle_type.value} as {seat_id}")
        return True
    
    def remove_passenger(self, seat_id: str) -> bool:
        """Remove passenger from seat"""
        if seat_id not in self.passengers:
            return False
        
        character = self.passengers[seat_id]
        del self.passengers[seat_id]
        
        # Open appropriate door
        if seat_id in self.doors:
            self.open_door(seat_id)
        
        print(f"👤 {character} exited {self.vehicle_type.value} from {seat_id}")
        return True
    
    def open_door(self, door_id: str) -> None:
        """Open specific door"""
        if door_id in self.doors:
            self.doors[door_id]['open'] = True
            self.doors[door_id]['animation_time'] = 0.0
    
    def close_door(self, door_id: str) -> None:
        """Close specific door"""
        if door_id in self.doors:
            self.doors[door_id]['open'] = False
            self.doors[door_id]['animation_time'] = 0.0
    
    def toggle_emergency_lights(self) -> None:
        """Toggle emergency lights (for police, ambulance, etc.)"""
        if self.vehicle_type in [VehicleType.POLICE, VehicleType.AMBULANCE, VehicleType.FIRE_TRUCK]:
            self.emergency_lights = not self.emergency_lights
            print(f"🚨 Emergency lights {'ON' if self.emergency_lights else 'OFF'}")
    
    # Advanced tire system methods
    def get_tire_stats(self) -> dict:
        """Get detailed tire statistics"""
        return self.tire_system.get_tire_stats()
    
    def get_skidding_wheels(self) -> List[str]:
        """Get list of wheels currently skidding"""
        return self.tire_system.get_skidding_wheels()
    
    def is_skidding(self) -> bool:
        """Check if any wheels are skidding"""
        return len(self.get_skidding_wheels()) > 0
    
    def get_tire_smoke_amount(self) -> float:
        """Get tire smoke intensity for visual effects"""
        return self.tire_system.get_total_smoke_amount()
    
    def get_tire_sound_level(self) -> float:
        """Get tire noise level for audio system"""
        return self.tire_system.get_tire_sound_level()
    
    def set_tire_pressure(self, wheel: str, pressure: float) -> None:
        """Set tire pressure for specific wheel"""
        self.tire_system.set_tire_pressure(wheel, pressure)
        print(f"🛞 {self.vehicle_type.value} {wheel} tire pressure set to {pressure:.1f} PSI")
    
    def puncture_tire(self, wheel: str) -> None:
        """Puncture a specific tire"""
        self.tire_system.puncture_tire(wheel)
        print(f"💨 {self.vehicle_type.value} {wheel} tire punctured!")
        
        # Add some damage for punctured tire
        self.take_damage(0.05)
    
    def check_tire_condition(self) -> dict:
        """Check overall tire condition"""
        tire_stats = self.get_tire_stats()
        condition = {}
        
        for wheel, stats in tire_stats.items():
            if stats['pressure'] < 15:
                condition[wheel] = "FLAT"
            elif stats['wear_level'] > 0.8:
                condition[wheel] = "WORN"
            elif stats['temperature'] > 80:
                condition[wheel] = "OVERHEATED"
            elif stats['pressure'] < 25:
                condition[wheel] = "LOW_PRESSURE"
            else:
                condition[wheel] = "GOOD"
        
        return condition

    def _update_damage_effects(self, dt: float) -> None:
        """Update damage-related visual effects"""
        # Effects are now handled by the VehicleEffectsSystem
        # This method is kept for compatibility but effects are generated in effects_system.update()
        pass
    
    def _update_door_animations(self, dt: float) -> None:
        """Update door opening/closing animations"""
        for door_id, door_state in self.doors.items():
            if door_state['animation_time'] < 1.0:
                door_state['animation_time'] += dt * 2.0  # 0.5 second animation
                door_state['animation_time'] = min(1.0, door_state['animation_time'])
    
    def get_seat_position(self, seat_id: str) -> Tuple[float, float]:
        """Get world position for a specific seat"""
        # Base offsets for different seats (relative to vehicle center)
        seat_offsets = {
            'driver': (-0.7, 0.5),
            'passenger': (0.7, 0.5),
            'rear_left': (-0.7, -0.5),
            'rear_right': (0.7, -0.5)
        }
        
        if seat_id not in seat_offsets:
            return (self.x, self.y)
        
        # Rotate offset by vehicle angle
        angle_rad = math.radians(self.angle)
        offset_x, offset_y = seat_offsets[seat_id]
        
        rotated_x = offset_x * math.cos(angle_rad) - offset_y * math.sin(angle_rad)
        rotated_y = offset_x * math.sin(angle_rad) + offset_y * math.cos(angle_rad)
        
        return (self.x + rotated_x * 16, self.y + rotated_y * 16)  # Convert to pixels
    
    def destroy(self) -> None:
        """Destroy the vehicle and clean up physics body"""
        if self.physics_body:
            self.physics_manager.remove_body(self.physics_body.body_id)
            self.physics_body = None
        print(f"💥 Vehicle destroyed: {self.vehicle_type.value}")

    def start_engine(self) -> bool:
        """Start the vehicle engine using electrical and mechanical systems"""
        if self.vehicle_type == VehicleType.BICYCLE:
            self.engine_on = True
            return True
        
        # Check basic prerequisites
        if self.fuel <= 0:
            print(f"🔧 Cannot start {self.vehicle_type.value}: no fuel")
            return False
        
        if self.is_wrecked:
            print(f"🔧 Cannot start {self.vehicle_type.value}: vehicle is wrecked")
            return False
        
        # Try to start using electrical system
        if not self.electrical_system.try_start_engine():
            return False
        
        # Try to start using mechanical system
        if not self.mechanical_system.start_engine():
            return False
        
        self.engine_on = True
        print(f"🔧 Engine started: {self.vehicle_type.value}")
        return True

    def stop_engine(self) -> None:
        """Stop the vehicle engine"""
        self.engine_on = False
        self.mechanical_system.stop_engine()
        self.throttle = 0
        self.steering = 0
        print(f"🔧 Engine stopped: {self.vehicle_type.value}")

    # Compatibility methods (delegate to new physics-based passenger system)
    def enter_vehicle(self, character, seat: str = "driver") -> bool:
        """Legacy method - use add_passenger instead"""
        return self.add_passenger(character, seat)

    def exit_vehicle(self, character) -> bool:
        """Legacy method - use remove_passenger instead"""
        # Find which seat the character is in
        for seat_id, passenger in self.passengers.items():
            if passenger == character:
                return self.remove_passenger(seat_id)
        return False

    def refuel(self, amount: float = 100.0) -> None:
        """Refuel the vehicle"""
        if self.stats.fuel_capacity > 0:
            self.fuel = min(self.stats.fuel_capacity, self.fuel + amount)
            print(f"⛽ Refueled {self.vehicle_type.value}: {self.fuel:.1f}/{self.stats.fuel_capacity}")

    def get_speed_kmh(self) -> float:
        """Get current speed in km/h"""
        return self.speed * 3.6 / 16.0  # Convert pixels/s to km/h

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle for the vehicle (for legacy compatibility)"""
        width, height = self._get_vehicle_dimensions(self.vehicle_type)
        width_pixels = int(width * 16)  # Convert meters to pixels
        height_pixels = int(height * 16)
        
        return pygame.Rect(
            int(self.x - width_pixels // 2),
            int(self.y - height_pixels // 2),
            width_pixels,
            height_pixels
        )

    def is_near_position(self, x: float, y: float, distance: float = 50.0) -> bool:
        """Check if vehicle is near a position"""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2) < distance
    
    def _update_electrical_components(self) -> None:
        """Update electrical components based on vehicle state"""
        # Turn on headlights automatically at night or when requested
        # (This would be called by game logic)
        
        # Activate brake lights when braking
        self.electrical_system.activate_brake_lights(self.brake > 0.1)
        
        # Activate reverse lights when in reverse
        if hasattr(self.mechanical_system, 'current_gear'):
            is_reversing = self.mechanical_system.current_gear == -1
            self.electrical_system.activate_reverse_lights(is_reversing)
    
    # Electrical system interface methods
    def toggle_headlights(self) -> bool:
        """Toggle headlights on/off"""
        return self.electrical_system.toggle_headlights()
    
    def toggle_emergency_lights(self) -> bool:
        """Toggle emergency lights (for emergency vehicles)"""
        return self.electrical_system.toggle_emergency_lights()
    
    def set_turn_signal(self, direction: str) -> None:
        """Set turn signals (left, right, or off)"""
        self.electrical_system.set_turn_signal(direction)
    
    def honk_horn(self) -> bool:
        """Honk the horn"""
        return self.electrical_system.turn_on_component(ElectricalComponent.HORN)
    
    def get_electrical_status(self) -> Dict:
        """Get electrical system status"""
        return self.electrical_system.get_electrical_status()
    
    def get_mechanical_status(self) -> Dict:
        """Get mechanical system status"""
        return self.mechanical_system.get_mechanical_status()
    
    def get_system_warnings(self) -> List[str]:
        """Get all system warning indicators"""
        electrical_failures = self.electrical_system.get_failure_summary()
        mechanical_warnings = self.mechanical_system.get_warning_indicators()
        
        all_warnings = []
        all_warnings.extend([f"ELECTRICAL: {f}" for f in electrical_failures])
        all_warnings.extend([f"MECHANICAL: {w}" for w in mechanical_warnings])
        
        return all_warnings
    
    def repair_electrical_component(self, component: ElectricalComponent) -> bool:
        """Repair a failed electrical component"""
        return self.electrical_system.repair_component(component)
    
    def repair_mechanical_component(self, failure_type: MechanicalFailureType) -> bool:
        """Repair a failed mechanical component"""
        return self.mechanical_system.repair_component(failure_type)
    
    def emergency_shutdown(self) -> None:
        """Emergency shutdown of all systems"""
        self.electrical_system.emergency_shutdown()
        self.stop_engine()
        print(f"⚠️ Emergency shutdown: {self.vehicle_type.value}")
    
    def render_effects(self, screen, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render vehicle visual effects"""
        self.effects_system.render(screen, self, camera_offset)
    
    def get_engine_rpm(self) -> float:
        """Get current engine RPM"""
        return self.mechanical_system.engine_rpm if hasattr(self.mechanical_system, 'engine_rpm') else 0.0
    
    def get_engine_temperature(self) -> float:
        """Get engine temperature in Celsius"""
        return self.mechanical_system.engine_temperature if hasattr(self.mechanical_system, 'engine_temperature') else 20.0
    
    def shift_gear(self, gear: int) -> bool:
        """Shift to specified gear (for manual transmissions)"""
        return self.mechanical_system.shift_gear(gear)
    
    def engage_clutch(self, engaged: bool) -> None:
        """Engage/disengage clutch (for manual transmissions)"""
        self.mechanical_system.engage_clutch(engaged)
    
    def render_effects(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render all vehicle visual effects"""
        self.effects_system.render(screen, self, camera_offset)
    
    def get_effects_info(self) -> Dict:
        """Get information about active visual effects"""
        return self.effects_system.get_effects_info()
    
    def clear_effects(self) -> None:
        """Clear all visual effects"""
        self.effects_system.clear_effects()


class VehicleManager:
    def __init__(self):
        self.vehicles: List[Vehicle] = []
        self.parked_vehicles: List[Vehicle] = []
        self.traffic_vehicles: List[Vehicle] = []
        self.spawn_timer = 0.0
        self.max_traffic = 50

    def spawn_vehicle(self, vehicle_type: VehicleType, x: float, y: float, angle: float = 0, 
                     is_traffic: bool = False) -> Vehicle:
        """Spawn a new vehicle"""
        vehicle = Vehicle(vehicle_type, x, y, angle)
        
        if is_traffic:
            self.traffic_vehicles.append(vehicle)
            vehicle.start_engine()
        else:
            self.vehicles.append(vehicle)
            
        return vehicle

    def spawn_random_traffic(self, spawn_points: List[Tuple[float, float]], 
                           vehicle_types: List[VehicleType]) -> None:
        """Spawn random traffic vehicles"""
        if len(self.traffic_vehicles) >= self.max_traffic:
            return
            
        for _ in range(min(3, self.max_traffic - len(self.traffic_vehicles))):
            if spawn_points and vehicle_types:
                spawn_point = random.choice(spawn_points)
                vehicle_type = random.choice(vehicle_types)
                angle = random.uniform(0, 360)
                
                vehicle = self.spawn_vehicle(vehicle_type, spawn_point[0], spawn_point[1], 
                                           angle, is_traffic=True)
                
                # Set random traffic behavior
                vehicle.throttle = random.uniform(0.3, 0.7)

    def update_traffic(self, dt: float, player_x: float, player_y: float) -> None:
        """Update AI-controlled traffic vehicles"""
        despawn_distance = 1000
        
        for vehicle in self.traffic_vehicles[:]:  # Use slice copy to avoid modification during iteration
            # Remove vehicles too far from player
            distance = math.sqrt((vehicle.x - player_x)**2 + (vehicle.y - player_y)**2)
            if distance > despawn_distance:
                self.traffic_vehicles.remove(vehicle)
                continue
            
            # Simple AI: drive forward with occasional direction changes
            if random.random() < 0.01:  # 1% chance per frame to change direction
                vehicle.steering = random.uniform(-0.5, 0.5)
            
            # Avoid going too fast
            speed = vehicle.get_speed_kmh()
            if speed < 30:
                vehicle.throttle = random.uniform(0.3, 0.8)
            elif speed > 60:
                vehicle.throttle = random.uniform(-0.2, 0.3)
                
            vehicle.update(dt)

    def update_all_vehicles(self, dt: float) -> None:
        """Update all vehicles"""
        for vehicle in self.vehicles:
            vehicle.update(dt)
    
    def render_all_effects(self, screen: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """Render visual effects for all vehicles"""
        for vehicle in self.vehicles + self.traffic_vehicles + self.parked_vehicles:
            vehicle.render_effects(screen, camera_offset)

    def get_nearest_vehicle(self, x: float, y: float, max_distance: float = 100.0) -> Optional[Vehicle]:
        """Get the nearest vehicle to a position"""
        nearest = None
        min_distance = float('inf')
        
        for vehicle in self.vehicles + self.traffic_vehicles:
            distance = math.sqrt((vehicle.x - x)**2 + (vehicle.y - y)**2)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest = vehicle
                
        return nearest

    def remove_vehicle(self, vehicle: Vehicle) -> None:
        """Remove a vehicle from the game"""
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)
        if vehicle in self.traffic_vehicles:
            self.traffic_vehicles.remove(vehicle)
        if vehicle in self.parked_vehicles:
            self.parked_vehicles.remove(vehicle)

    def get_vehicle_by_type(self, vehicle_type: VehicleType) -> List[Vehicle]:
        """Get all vehicles of a specific type"""
        return [v for v in self.vehicles + self.traffic_vehicles if v.vehicle_type == vehicle_type]
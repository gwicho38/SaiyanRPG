#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Advanced Vehicle Physics System

import math
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .physics_manager import PhysicsManager, PhysicsBody, CollisionCategory, PhysicsBodyType


class VehicleState(Enum):
    """Vehicle states"""
    NORMAL = "normal"
    DAMAGED = "damaged"
    WRECKED = "wrecked"
    BURNING = "burning"
    IN_WATER = "in_water"
    EMERGENCY_LIGHTS = "emergency_lights"


class TirePosition(Enum):
    """Tire positions"""
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"
    REAR_LEFT = "rear_left"
    REAR_RIGHT = "rear_right"


@dataclass
class TirePhysics:
    """Individual tire physics"""
    position: TirePosition
    world_position: Tuple[float, float]
    velocity: Tuple[float, float]
    angular_velocity: float
    steering_angle: float
    brake_force: float
    drive_force: float
    friction: float
    radius: float
    width: float
    is_grounded: bool = False
    ground_friction: float = 0.8
    slip_ratio: float = 0.0
    slip_angle: float = 0.0


@dataclass
class VehiclePhysicsData:
    """Complete vehicle physics data"""
    # Basic properties
    mass: float
    length: float
    width: float
    height: float
    center_of_mass: Tuple[float, float]
    
    # Engine properties
    engine_power: float
    max_speed: float
    max_reverse_speed: float
    engine_torque: float
    engine_rpm: float
    gear_ratio: List[float]
    current_gear: int
    
    # Handling properties
    steering_angle: float
    max_steering_angle: float
    steering_speed: float
    wheelbase: float
    track_width: float
    
    # Braking properties
    brake_force: float
    handbrake_force: float
    brake_balance: float  # Front/rear brake distribution
    
    # Aerodynamics
    drag_coefficient: float
    downforce: float
    
    # Damage
    damage_level: float  # 0.0 to 1.0
    is_on_fire: bool
    is_wrecked: bool
    
    # Tires
    tires: Dict[TirePosition, TirePhysics]
    
    # Physics body reference
    physics_body_id: Optional[int] = None


class VehiclePhysicsSystem:
    """Advanced vehicle physics system with tire simulation"""
    
    def __init__(self, physics_manager: PhysicsManager):
        self.physics_manager = physics_manager
        self.vehicles: Dict[int, VehiclePhysicsData] = {}
        self.next_vehicle_id = 1
        
        # Physics constants
        self.gravity = 9.81
        self.air_density = 1.225  # kg/m³
        
        # Tire physics constants
        self.tire_stiffness = 1000.0
        self.tire_damping = 10.0
        self.max_tire_force = 10000.0
        
        print("🚗 VehiclePhysicsSystem initialized")
    
    def create_vehicle(self, vehicle_type: str, position: Tuple[float, float], 
                      angle: float = 0.0) -> int:
        """Create a new vehicle with physics"""
        vehicle_id = self.next_vehicle_id
        self.next_vehicle_id += 1
        
        # Get vehicle specifications
        specs = self._get_vehicle_specs(vehicle_type)
        
        # Create physics body
        physics_body = self.physics_manager.create_body(
            PhysicsBodyType.DYNAMIC,
            position,
            {
                'type': 'box',
                'width': specs['width'],
                'height': specs['length'],
                'mass': specs['mass'],
                'friction': 0.7,
                'restitution': 0.1
            },
            CollisionCategory.VEHICLE,
            user_data={'vehicle_id': vehicle_id, 'type': 'vehicle'}
        )
        
        # Create tire physics
        tires = self._create_tires(specs, position, angle)
        
        # Create vehicle physics data
        vehicle_data = VehiclePhysicsData(
            mass=specs['mass'],
            length=specs['length'],
            width=specs['width'],
            height=specs['height'],
            center_of_mass=(0, 0),
            engine_power=specs['engine_power'],
            max_speed=specs['max_speed'],
            max_reverse_speed=specs['max_reverse_speed'],
            engine_torque=specs['engine_torque'],
            engine_rpm=800.0,
            gear_ratio=specs['gear_ratio'],
            current_gear=1,
            steering_angle=0.0,
            max_steering_angle=specs['max_steering_angle'],
            steering_speed=specs['steering_speed'],
            wheelbase=specs['wheelbase'],
            track_width=specs['track_width'],
            brake_force=specs['brake_force'],
            handbrake_force=specs['handbrake_force'],
            brake_balance=0.6,  # 60% front, 40% rear
            drag_coefficient=specs['drag_coefficient'],
            downforce=specs['downforce'],
            damage_level=0.0,
            is_on_fire=False,
            is_wrecked=False,
            tires=tires,
            physics_body_id=physics_body.body_id
        )
        
        self.vehicles[vehicle_id] = vehicle_data
        print(f"🚗 Created vehicle {vehicle_id} ({vehicle_type}) at {position}")
        return vehicle_id
    
    def _get_vehicle_specs(self, vehicle_type: str) -> Dict[str, Any]:
        """Get vehicle specifications by type"""
        specs = {
            'sedan': {
                'mass': 1500.0,
                'length': 4.5,
                'width': 1.8,
                'height': 1.5,
                'engine_power': 150.0,  # kW
                'max_speed': 200.0,  # km/h
                'max_reverse_speed': 50.0,
                'engine_torque': 300.0,  # Nm
                'gear_ratio': [3.5, 2.1, 1.4, 1.0, 0.8],
                'max_steering_angle': 0.6,  # radians
                'steering_speed': 3.0,  # rad/s
                'wheelbase': 2.7,
                'track_width': 1.6,
                'brake_force': 8000.0,
                'handbrake_force': 4000.0,
                'drag_coefficient': 0.3,
                'downforce': 0.0
            },
            'sports_car': {
                'mass': 1200.0,
                'length': 4.2,
                'width': 1.9,
                'height': 1.3,
                'engine_power': 300.0,
                'max_speed': 300.0,
                'max_reverse_speed': 60.0,
                'engine_torque': 500.0,
                'gear_ratio': [3.2, 1.9, 1.3, 1.0, 0.7],
                'max_steering_angle': 0.5,
                'steering_speed': 4.0,
                'wheelbase': 2.5,
                'track_width': 1.7,
                'brake_force': 12000.0,
                'handbrake_force': 6000.0,
                'drag_coefficient': 0.25,
                'downforce': 1000.0
            },
            'truck': {
                'mass': 8000.0,
                'length': 12.0,
                'width': 2.5,
                'height': 3.5,
                'engine_power': 400.0,
                'max_speed': 120.0,
                'max_reverse_speed': 30.0,
                'engine_torque': 2000.0,
                'gear_ratio': [5.0, 3.5, 2.5, 1.8, 1.2, 1.0],
                'max_steering_angle': 0.4,
                'steering_speed': 2.0,
                'wheelbase': 6.0,
                'track_width': 2.2,
                'brake_force': 20000.0,
                'handbrake_force': 10000.0,
                'drag_coefficient': 0.6,
                'downforce': 0.0
            },
            'motorcycle': {
                'mass': 200.0,
                'length': 2.1,
                'width': 0.7,
                'height': 1.2,
                'engine_power': 100.0,
                'max_speed': 250.0,
                'max_reverse_speed': 40.0,
                'engine_torque': 120.0,
                'gear_ratio': [2.5, 1.8, 1.3, 1.0, 0.8],
                'max_steering_angle': 0.8,
                'steering_speed': 5.0,
                'wheelbase': 1.4,
                'track_width': 0.0,  # Single track
                'brake_force': 3000.0,
                'handbrake_force': 1500.0,
                'drag_coefficient': 0.4,
                'downforce': 0.0
            }
        }
        
        return specs.get(vehicle_type, specs['sedan'])
    
    def _create_tires(self, specs: Dict[str, Any], position: Tuple[float, float], 
                     angle: float) -> Dict[TirePosition, TirePhysics]:
        """Create tire physics for a vehicle"""
        tires = {}
        
        # Calculate tire positions relative to vehicle center
        wheelbase = specs['wheelbase']
        track_width = specs['track_width']
        
        tire_positions = {
            TirePosition.FRONT_LEFT: (-wheelbase/2, -track_width/2),
            TirePosition.FRONT_RIGHT: (-wheelbase/2, track_width/2),
            TirePosition.REAR_LEFT: (wheelbase/2, -track_width/2),
            TirePosition.REAR_RIGHT: (wheelbase/2, track_width/2)
        }
        
        for tire_pos, rel_pos in tire_positions.items():
            # Rotate tire position by vehicle angle
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            world_x = position[0] + rel_pos[0] * cos_a - rel_pos[1] * sin_a
            world_y = position[1] + rel_pos[0] * sin_a + rel_pos[1] * cos_a
            
            tires[tire_pos] = TirePhysics(
                position=tire_pos,
                world_position=(world_x, world_y),
                velocity=(0.0, 0.0),
                angular_velocity=0.0,
                steering_angle=0.0,
                brake_force=0.0,
                drive_force=0.0,
                friction=0.8,
                radius=0.3,
                width=0.2
            )
        
        return tires
    
    def update_vehicle(self, vehicle_id: int, dt: float, 
                      throttle: float = 0.0, brake: float = 0.0,
                      steering: float = 0.0, handbrake: bool = False) -> None:
        """Update vehicle physics"""
        if vehicle_id not in self.vehicles:
            return
        
        vehicle = self.vehicles[vehicle_id]
        physics_body = self.physics_manager.get_body(vehicle.physics_body_id)
        
        if not physics_body:
            return
        
        # Update steering
        target_steering = steering * vehicle.max_steering_angle
        steering_diff = target_steering - vehicle.steering_angle
        max_steering_change = vehicle.steering_speed * dt
        
        if abs(steering_diff) > max_steering_change:
            vehicle.steering_angle += max_steering_change if steering_diff > 0 else -max_steering_change
        else:
            vehicle.steering_angle = target_steering
        
        # Update engine
        self._update_engine(vehicle, dt, throttle)
        
        # Update tires
        self._update_tires(vehicle, physics_body, dt)
        
        # Calculate forces
        forces = self._calculate_forces(vehicle, physics_body, throttle, brake, handbrake)
        
        # Apply forces to physics body
        for force, point in forces:
            self.physics_manager.apply_force(vehicle.physics_body_id, force, point)
        
        # Update damage
        self._update_damage(vehicle, physics_body, dt)
        
        # Update vehicle state
        self._update_vehicle_state(vehicle, physics_body)
    
    def _update_engine(self, vehicle: VehiclePhysicsData, dt: float, throttle: float) -> None:
        """Update engine physics"""
        # Calculate engine RPM based on wheel speed
        avg_wheel_speed = sum(abs(tire.angular_velocity) for tire in vehicle.tires.values()) / 4.0
        vehicle.engine_rpm = avg_wheel_speed * 60.0 / (2 * math.pi) * vehicle.gear_ratio[vehicle.current_gear]
        
        # Clamp RPM
        vehicle.engine_rpm = max(800, min(6000, vehicle.engine_rpm))
        
        # Calculate engine power based on RPM and throttle
        power_factor = self._get_power_factor(vehicle.engine_rpm)
        current_power = vehicle.engine_power * throttle * power_factor
        
        # Apply damage reduction
        current_power *= (1.0 - vehicle.damage_level * 0.5)
        
        # Calculate torque
        vehicle.engine_torque = current_power * 1000.0 / (vehicle.engine_rpm * math.pi / 30.0)
    
    def _get_power_factor(self, rpm: float) -> float:
        """Get power factor based on RPM (power curve)"""
        # Simplified power curve - peak power around 5000 RPM
        if rpm < 1000:
            return rpm / 1000.0
        elif rpm < 5000:
            return 0.5 + 0.5 * (rpm - 1000) / 4000.0
        else:
            return max(0.3, 1.0 - (rpm - 5000) / 1000.0 * 0.7)
    
    def _update_tires(self, vehicle: VehiclePhysicsData, physics_body: PhysicsBody, dt: float) -> None:
        """Update tire physics"""
        vehicle_angle = physics_body.angle
        vehicle_velocity = physics_body.velocity
        
        for tire_pos, tire in vehicle.tires.items():
            # Update tire world position
            wheelbase = vehicle.wheelbase
            track_width = vehicle.track_width
            
            # Calculate relative position
            if tire_pos == TirePosition.FRONT_LEFT:
                rel_x, rel_y = -wheelbase/2, -track_width/2
            elif tire_pos == TirePosition.FRONT_RIGHT:
                rel_x, rel_y = -wheelbase/2, track_width/2
            elif tire_pos == TirePosition.REAR_LEFT:
                rel_x, rel_y = wheelbase/2, -track_width/2
            else:  # REAR_RIGHT
                rel_x, rel_y = wheelbase/2, track_width/2
            
            # Rotate by vehicle angle
            cos_a = math.cos(vehicle_angle)
            sin_a = math.sin(vehicle_angle)
            
            tire.world_position = (
                physics_body.position[0] + rel_x * cos_a - rel_y * sin_a,
                physics_body.position[1] + rel_x * sin_a + rel_y * cos_a
            )
            
            # Calculate tire velocity
            tire.velocity = (
                vehicle_velocity[0] + tire.angular_velocity * tire.radius * math.cos(vehicle_angle + tire.steering_angle),
                vehicle_velocity[1] + tire.angular_velocity * tire.radius * math.sin(vehicle_angle + tire.steering_angle)
            )
            
            # Calculate slip ratio and angle
            tire_speed = math.sqrt(tire.velocity[0]**2 + tire.velocity[1]**2)
            vehicle_speed = math.sqrt(vehicle_velocity[0]**2 + vehicle_velocity[1]**2)
            
            if vehicle_speed > 0.1:
                tire.slip_ratio = (tire_speed - vehicle_speed) / vehicle_speed
            else:
                tire.slip_ratio = 0.0
            
            # Calculate slip angle (simplified)
            if tire_speed > 0.1:
                tire.slip_angle = math.atan2(tire.velocity[1], tire.velocity[0]) - vehicle_angle
            else:
                tire.slip_angle = 0.0
    
    def _calculate_forces(self, vehicle: VehiclePhysicsData, physics_body: PhysicsBody,
                         throttle: float, brake: float, handbrake: bool) -> List[Tuple[Tuple[float, float], Optional[Tuple[float, float]]]]:
        """Calculate all forces acting on the vehicle"""
        forces = []
        
        # Drive forces (rear wheels)
        drive_force = vehicle.engine_torque * vehicle.gear_ratio[vehicle.current_gear] / vehicle.tires[TirePosition.REAR_LEFT].radius
        
        for tire_pos in [TirePosition.REAR_LEFT, TirePosition.REAR_RIGHT]:
            tire = vehicle.tires[tire_pos]
            tire.drive_force = drive_force * throttle / 2.0  # Split between rear wheels
            
            # Apply drive force
            force_magnitude = tire.drive_force
            force_angle = physics_body.angle
            
            force = (
                force_magnitude * math.cos(force_angle),
                force_magnitude * math.sin(force_angle)
            )
            
            forces.append((force, tire.world_position))
        
        # Brake forces
        brake_force = vehicle.brake_force * brake
        handbrake_force = vehicle.handbrake_force if handbrake else 0.0
        
        for tire_pos, tire in vehicle.tires.items():
            if tire_pos in [TirePosition.FRONT_LEFT, TirePosition.FRONT_RIGHT]:
                tire.brake_force = brake_force * vehicle.brake_balance / 2.0
            else:
                tire.brake_force = brake_force * (1.0 - vehicle.brake_balance) / 2.0 + handbrake_force / 2.0
            
            # Apply brake force (opposite to velocity)
            if tire.brake_force > 0:
                velocity_magnitude = math.sqrt(physics_body.velocity[0]**2 + physics_body.velocity[1]**2)
                if velocity_magnitude > 0.1:
                    brake_direction = (
                        -physics_body.velocity[0] / velocity_magnitude,
                        -physics_body.velocity[1] / velocity_magnitude
                    )
                    
                    brake_force_vector = (
                        brake_direction[0] * tire.brake_force,
                        brake_direction[1] * tire.brake_force
                    )
                    
                    forces.append((brake_force_vector, tire.world_position))
        
        # Aerodynamic forces
        velocity_magnitude = math.sqrt(physics_body.velocity[0]**2 + physics_body.velocity[1]**2)
        if velocity_magnitude > 0.1:
            # Drag force
            drag_force = 0.5 * self.air_density * velocity_magnitude**2 * vehicle.drag_coefficient * vehicle.width * vehicle.height
            
            drag_direction = (
                -physics_body.velocity[0] / velocity_magnitude,
                -physics_body.velocity[1] / velocity_magnitude
            )
            
            drag_force_vector = (
                drag_direction[0] * drag_force,
                drag_direction[1] * drag_force
            )
            
            forces.append((drag_force_vector, None))  # Applied at center of mass
        
        return forces
    
    def _update_damage(self, vehicle: VehiclePhysicsData, physics_body: PhysicsBody, dt: float) -> None:
        """Update vehicle damage"""
        # Check for high-speed collisions
        velocity_magnitude = math.sqrt(physics_body.velocity[0]**2 + physics_body.velocity[1]**2)
        
        # Damage from high speed
        if velocity_magnitude > 50.0:  # 50 m/s = 180 km/h
            damage_rate = (velocity_magnitude - 50.0) * 0.01 * dt
            vehicle.damage_level = min(1.0, vehicle.damage_level + damage_rate)
        
        # Fire damage
        if vehicle.is_on_fire:
            vehicle.damage_level = min(1.0, vehicle.damage_level + 0.1 * dt)
        
        # Update wrecked state
        if vehicle.damage_level > 0.8:
            vehicle.is_wrecked = True
            vehicle.is_on_fire = True
    
    def _update_vehicle_state(self, vehicle: VehiclePhysicsData, physics_body: PhysicsBody) -> None:
        """Update vehicle state based on physics"""
        # Check if vehicle is in water (simplified)
        # This would need water detection from the world system
        vehicle_state = VehicleState.NORMAL
        
        if vehicle.is_wrecked:
            vehicle_state = VehicleState.WRECKED
        elif vehicle.is_on_fire:
            vehicle_state = VehicleState.BURNING
        elif vehicle.damage_level > 0.3:
            vehicle_state = VehicleState.DAMAGED
        
        # Update emergency lights based on damage
        if vehicle.damage_level > 0.5:
            vehicle_state = VehicleState.EMERGENCY_LIGHTS
    
    def get_vehicle_speed(self, vehicle_id: int) -> float:
        """Get vehicle speed in m/s"""
        if vehicle_id not in self.vehicles:
            return 0.0
        
        vehicle = self.vehicles[vehicle_id]
        physics_body = self.physics_manager.get_body(vehicle.physics_body_id)
        
        if not physics_body:
            return 0.0
        
        return math.sqrt(physics_body.velocity[0]**2 + physics_body.velocity[1]**2)
    
    def get_vehicle_position(self, vehicle_id: int) -> Tuple[float, float]:
        """Get vehicle position"""
        if vehicle_id not in self.vehicles:
            return (0.0, 0.0)
        
        vehicle = self.vehicles[vehicle_id]
        physics_body = self.physics_manager.get_body(vehicle.physics_body_id)
        
        if not physics_body:
            return (0.0, 0.0)
        
        return physics_body.position
    
    def get_vehicle_angle(self, vehicle_id: int) -> float:
        """Get vehicle angle"""
        if vehicle_id not in self.vehicles:
            return 0.0
        
        vehicle = self.vehicles[vehicle_id]
        physics_body = self.physics_manager.get_body(vehicle.physics_body_id)
        
        if not physics_body:
            return 0.0
        
        return physics_body.angle
    
    def remove_vehicle(self, vehicle_id: int) -> None:
        """Remove a vehicle"""
        if vehicle_id not in self.vehicles:
            return
        
        vehicle = self.vehicles[vehicle_id]
        
        # Remove physics body
        if vehicle.physics_body_id:
            self.physics_manager.remove_body(vehicle.physics_body_id)
        
        del self.vehicles[vehicle_id]
        print(f"🚗 Removed vehicle {vehicle_id}")
    
    def get_vehicle_statistics(self) -> Dict[str, Any]:
        """Get vehicle system statistics"""
        return {
            'total_vehicles': len(self.vehicles),
            'damaged_vehicles': len([v for v in self.vehicles.values() if v.damage_level > 0.1]),
            'wrecked_vehicles': len([v for v in self.vehicles.values() if v.is_wrecked]),
            'burning_vehicles': len([v for v in self.vehicles.values() if v.is_on_fire])
        }


# Test the vehicle physics system
if __name__ == "__main__":
    print("🧪 Testing VehiclePhysicsSystem...")
    
    # Create physics manager
    physics_manager = PhysicsManager(gravity=(0, 0))
    
    # Create vehicle physics system
    vehicle_physics = VehiclePhysicsSystem(physics_manager)
    
    # Create a test vehicle
    vehicle_id = vehicle_physics.create_vehicle('sports_car', (100, 100))
    
    # Test update loop
    import time
    start_time = time.time()
    
    while time.time() - start_time < 5.0:  # Run for 5 seconds
        dt = 1.0 / 60.0  # 60 FPS
        
        # Apply some input
        vehicle_physics.update_vehicle(vehicle_id, dt, throttle=0.5, steering=0.3)
        
        # Update physics
        physics_manager.update(dt)
        
        # Get vehicle info
        speed = vehicle_physics.get_vehicle_speed(vehicle_id)
        position = vehicle_physics.get_vehicle_position(vehicle_id)
        
        print(f"Speed: {speed:.1f} m/s, Position: ({position[0]:.1f}, {position[1]:.1f})")
        
        time.sleep(dt)
    
    print("✅ VehiclePhysicsSystem test completed")
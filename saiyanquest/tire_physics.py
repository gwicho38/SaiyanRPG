#!/usr/bin/env python3
"""
Advanced Tire Physics System - Based on Carnage3D's tire simulation
Provides realistic tire behavior, skidding, and traction simulation.
"""

import math
from typing import Tuple, List
from dataclasses import dataclass
from enum import Enum

class TireType(Enum):
    """Different tire types with different characteristics"""
    STANDARD = "standard"
    SPORT = "sport" 
    OFFROAD = "offroad"
    RACING = "racing"
    WINTER = "winter"
    WORN = "worn"

@dataclass
class TireProperties:
    """Properties for different tire types"""
    max_traction: float  # Maximum traction coefficient
    lateral_grip: float  # Sideways grip for cornering
    wear_rate: float     # How fast tires wear out
    noise_level: float   # Tire noise (for sound effects)
    optimal_pressure: float = 32.0  # Optimal tire pressure in PSI

class TirePhysics:
    """
    Advanced tire physics simulation based on Carnage3D.
    Handles tire forces, slip angles, and realistic vehicle dynamics.
    """
    
    def __init__(self, tire_type: TireType = TireType.STANDARD):
        self.tire_type = tire_type
        self.properties = self._get_tire_properties(tire_type)
        
        # Tire state
        self.pressure = self.properties.optimal_pressure
        self.wear_level = 0.0  # 0.0 = new, 1.0 = completely worn
        self.temperature = 20.0  # Celsius
        
        # Physics state
        self.slip_angle = 0.0  # Angle between tire direction and velocity
        self.slip_ratio = 0.0  # Ratio of wheel speed to ground speed
        self.contact_patch_size = 0.15  # Size of tire contact patch
        
        # Forces
        self.longitudinal_force = 0.0  # Forward/backward force
        self.lateral_force = 0.0       # Sideways force
        self.normal_force = 1000.0     # Downward force from vehicle weight
        
        # Skid marks and effects
        self.is_skidding = False
        self.skid_intensity = 0.0  # 0.0 to 1.0
        self.smoke_amount = 0.0    # Tire smoke generation
        
        print(f"🛞 Tire physics initialized: {tire_type.value}")
    
    def _get_tire_properties(self, tire_type: TireType) -> TireProperties:
        """Get properties for the specified tire type"""
        properties_map = {
            TireType.STANDARD: TireProperties(
                max_traction=0.8, lateral_grip=0.7, wear_rate=0.1, noise_level=0.3
            ),
            TireType.SPORT: TireProperties(
                max_traction=0.9, lateral_grip=0.9, wear_rate=0.15, noise_level=0.5
            ),
            TireType.OFFROAD: TireProperties(
                max_traction=0.7, lateral_grip=0.5, wear_rate=0.05, noise_level=0.4
            ),
            TireType.RACING: TireProperties(
                max_traction=1.0, lateral_grip=1.0, wear_rate=0.3, noise_level=0.7
            ),
            TireType.WINTER: TireProperties(
                max_traction=0.6, lateral_grip=0.6, wear_rate=0.08, noise_level=0.2
            ),
            TireType.WORN: TireProperties(
                max_traction=0.4, lateral_grip=0.3, wear_rate=0.01, noise_level=0.6
            ),
        }
        return properties_map.get(tire_type, properties_map[TireType.STANDARD])
    
    def calculate_tire_forces(self, wheel_velocity: Tuple[float, float], 
                            wheel_angular_velocity: float, wheel_radius: float,
                            vehicle_velocity: Tuple[float, float], 
                            vehicle_angle: float, surface_friction: float = 1.0) -> Tuple[float, float]:
        """
        Calculate tire forces based on wheel and vehicle state.
        Returns (longitudinal_force, lateral_force)
        """
        
        # Calculate slip angle (angle between tire direction and velocity direction)
        self._calculate_slip_angle(vehicle_velocity, vehicle_angle)
        
        # Calculate slip ratio (difference between wheel speed and ground speed)
        self._calculate_slip_ratio(wheel_velocity, wheel_angular_velocity, wheel_radius)
        
        # Calculate available traction based on tire condition and surface
        available_traction = self._get_available_traction(surface_friction)
        
        # Calculate longitudinal force (acceleration/braking)
        self.longitudinal_force = self._calculate_longitudinal_force(available_traction)
        
        # Calculate lateral force (cornering)
        self.lateral_force = self._calculate_lateral_force(available_traction)
        
        # Update tire temperature and wear
        self._update_tire_condition()
        
        # Check for skidding
        self._update_skidding_state()
        
        return (self.longitudinal_force, self.lateral_force)
    
    def _calculate_slip_angle(self, vehicle_velocity: Tuple[float, float], vehicle_angle: float):
        """Calculate the slip angle of the tire"""
        if vehicle_velocity[0] == 0 and vehicle_velocity[1] == 0:
            self.slip_angle = 0.0
            return
        
        # Vehicle direction vector
        vehicle_dir_x = math.cos(vehicle_angle)
        vehicle_dir_y = math.sin(vehicle_angle)
        
        # Velocity direction vector
        velocity_magnitude = math.sqrt(vehicle_velocity[0]**2 + vehicle_velocity[1]**2)
        velocity_dir_x = vehicle_velocity[0] / velocity_magnitude
        velocity_dir_y = vehicle_velocity[1] / velocity_magnitude
        
        # Calculate angle between vehicle direction and velocity direction
        dot_product = vehicle_dir_x * velocity_dir_x + vehicle_dir_y * velocity_dir_y
        cross_product = vehicle_dir_x * velocity_dir_y - vehicle_dir_y * velocity_dir_x
        
        self.slip_angle = math.atan2(cross_product, dot_product)
    
    def _calculate_slip_ratio(self, wheel_velocity: Tuple[float, float], 
                            wheel_angular_velocity: float, wheel_radius: float):
        """Calculate the slip ratio of the tire"""
        # Wheel speed at contact patch
        wheel_speed = abs(wheel_angular_velocity * wheel_radius)
        
        # Ground speed
        ground_speed = math.sqrt(wheel_velocity[0]**2 + wheel_velocity[1]**2)
        
        if ground_speed > 0.1:  # Avoid division by zero
            self.slip_ratio = (wheel_speed - ground_speed) / ground_speed
        else:
            self.slip_ratio = 0.0
        
        # Clamp slip ratio to reasonable bounds
        self.slip_ratio = max(-1.0, min(1.0, self.slip_ratio))
    
    def _get_available_traction(self, surface_friction: float) -> float:
        """Calculate available traction based on tire condition and surface"""
        # Base traction from tire properties
        base_traction = self.properties.max_traction
        
        # Reduce traction based on wear
        wear_factor = 1.0 - (self.wear_level * 0.6)  # Up to 60% reduction when worn
        
        # Reduce traction based on pressure
        pressure_factor = 1.0
        if self.pressure < self.properties.optimal_pressure * 0.8:
            # Under-inflated tires lose traction
            pressure_factor = 0.7
        elif self.pressure > self.properties.optimal_pressure * 1.2:
            # Over-inflated tires lose traction
            pressure_factor = 0.8
        
        # Temperature effects
        temp_factor = 1.0
        if self.temperature > 80:  # Overheated tires lose grip
            temp_factor = 0.8
        elif self.temperature > 60:  # Warm tires have optimal grip
            temp_factor = 1.1
        
        return base_traction * wear_factor * pressure_factor * temp_factor * surface_friction
    
    def _calculate_longitudinal_force(self, available_traction: float) -> float:
        """Calculate forward/backward tire force"""
        # Use magic formula tire model (simplified)
        slip_ratio_abs = abs(self.slip_ratio)
        
        if slip_ratio_abs < 0.1:
            # Linear region - good traction
            force_coefficient = slip_ratio_abs * 10.0
        else:
            # Non-linear region - sliding
            peak_force = 0.9
            force_coefficient = peak_force * (1.0 - (slip_ratio_abs - 0.1) * 0.5)
            force_coefficient = max(0.3, force_coefficient)  # Minimum sliding friction
        
        force_coefficient *= available_traction
        
        # Apply normal force to get actual force
        force = force_coefficient * self.normal_force
        
        # Maintain sign of slip ratio
        return force * (1 if self.slip_ratio >= 0 else -1)
    
    def _calculate_lateral_force(self, available_traction: float) -> float:
        """Calculate sideways tire force for cornering"""
        slip_angle_abs = abs(self.slip_angle)
        
        if slip_angle_abs < 0.1:  # 5.7 degrees
            # Linear region
            force_coefficient = slip_angle_abs * 8.0
        else:
            # Non-linear region
            peak_force = 0.8 * self.properties.lateral_grip
            force_coefficient = peak_force * (1.0 - (slip_angle_abs - 0.1) * 0.6)
            force_coefficient = max(0.2, force_coefficient)
        
        force_coefficient *= available_traction
        
        # Apply normal force
        force = force_coefficient * self.normal_force
        
        # Maintain sign of slip angle
        return force * (1 if self.slip_angle >= 0 else -1)
    
    def _update_tire_condition(self):
        """Update tire temperature and wear based on forces"""
        # Heat generation from forces
        force_magnitude = math.sqrt(self.longitudinal_force**2 + self.lateral_force**2)
        heat_generation = force_magnitude / 1000.0  # Simplified heat model
        
        # Temperature increase
        self.temperature += heat_generation * 0.1
        
        # Cooling (simplified)
        ambient_temp = 20.0
        self.temperature = self.temperature * 0.99 + ambient_temp * 0.01
        
        # Wear calculation
        slip_energy = abs(self.slip_ratio) + abs(self.slip_angle)
        wear_increment = slip_energy * self.properties.wear_rate * 0.0001
        self.wear_level = min(1.0, self.wear_level + wear_increment)
    
    def _update_skidding_state(self):
        """Update tire skidding effects"""
        # Determine if tire is skidding
        slip_threshold = 0.2
        self.is_skidding = (abs(self.slip_ratio) > slip_threshold or 
                          abs(self.slip_angle) > slip_threshold)
        
        if self.is_skidding:
            # Calculate skid intensity
            self.skid_intensity = min(1.0, (abs(self.slip_ratio) + abs(self.slip_angle)) / 0.5)
            
            # Generate smoke based on skid intensity and surface
            self.smoke_amount = self.skid_intensity * 0.8
        else:
            self.skid_intensity *= 0.9  # Fade out
            self.smoke_amount *= 0.8
    
    def set_pressure(self, pressure: float):
        """Set tire pressure"""
        self.pressure = max(10, min(60, pressure))  # Reasonable pressure bounds
    
    def puncture_tire(self):
        """Simulate tire puncture"""
        self.pressure = 5.0  # Very low pressure
        print(f"💨 Tire punctured! Pressure dropped to {self.pressure} PSI")
    
    def get_tire_sound_level(self) -> float:
        """Get tire noise level for audio system"""
        base_noise = self.properties.noise_level
        
        # Increase noise when skidding
        skid_noise = self.skid_intensity * 0.5
        
        # Increase noise when worn
        wear_noise = self.wear_level * 0.3
        
        return min(1.0, base_noise + skid_noise + wear_noise)
    
    def get_stats(self) -> dict:
        """Get tire statistics for debugging"""
        return {
            'type': self.tire_type.value,
            'pressure': self.pressure,
            'wear_level': self.wear_level,
            'temperature': self.temperature,
            'slip_angle': math.degrees(self.slip_angle),
            'slip_ratio': self.slip_ratio,
            'longitudinal_force': self.longitudinal_force,
            'lateral_force': self.lateral_force,
            'is_skidding': self.is_skidding,
            'skid_intensity': self.skid_intensity,
            'smoke_amount': self.smoke_amount
        }

class VehicleTireSystem:
    """
    Manages all four tires of a vehicle with individual tire physics.
    Based on Carnage3D's tire corner tracking system.
    """
    
    def __init__(self, tire_type: TireType = TireType.STANDARD, wheelbase: float = 2.5):
        self.wheelbase = wheelbase  # Distance between front and rear axles
        self.track_width = 1.5      # Distance between left and right wheels
        
        # Create individual tire physics for each wheel
        self.tires = {
            'front_left': TirePhysics(tire_type),
            'front_right': TirePhysics(tire_type),
            'rear_left': TirePhysics(tire_type),
            'rear_right': TirePhysics(tire_type)
        }
        
        # Tire positions relative to vehicle center
        self.tire_positions = {
            'front_left': (-self.track_width/2, self.wheelbase/2),
            'front_right': (self.track_width/2, self.wheelbase/2),
            'rear_left': (-self.track_width/2, -self.wheelbase/2),
            'rear_right': (self.track_width/2, -self.wheelbase/2)
        }
        
        # Steering angles (front wheels only)
        self.steering_angles = {
            'front_left': 0.0,
            'front_right': 0.0,
            'rear_left': 0.0,
            'rear_right': 0.0
        }
        
        print(f"🚗 Vehicle tire system initialized with {tire_type.value} tires")
    
    def calculate_vehicle_forces(self, vehicle_velocity: Tuple[float, float], 
                               vehicle_angular_velocity: float, vehicle_angle: float,
                               throttle: float, steering: float, brake: float) -> Tuple[float, float, float]:
        """
        Calculate total forces and torque on vehicle from all tires.
        Returns (total_force_x, total_force_y, total_torque)
        """
        
        total_force_x = 0.0
        total_force_y = 0.0
        total_torque = 0.0
        
        # Update steering angles for front wheels
        max_steering_angle = math.radians(30)  # 30 degrees max steering
        self.steering_angles['front_left'] = steering * max_steering_angle
        self.steering_angles['front_right'] = steering * max_steering_angle
        
        # Process each tire
        for tire_name, tire_physics in self.tires.items():
            # Get tire position relative to vehicle center
            tire_pos = self.tire_positions[tire_name]
            
            # Calculate tire velocity considering vehicle rotation
            tire_vel_x = (vehicle_velocity[0] + 
                         vehicle_angular_velocity * (-tire_pos[1]))
            tire_vel_y = (vehicle_velocity[1] + 
                         vehicle_angular_velocity * tire_pos[0])
            
            # Calculate wheel angular velocity (simplified)
            wheel_radius = 0.3  # 30cm radius
            if tire_name.startswith('front'):
                # Front wheels get throttle and brake
                wheel_angular_vel = throttle * 100 - brake * 50
            else:
                # Rear wheels (assuming FWD for now)
                wheel_angular_vel = 0
            
            # Calculate tire angle (vehicle angle + steering angle)
            tire_angle = vehicle_angle + self.steering_angles[tire_name]
            
            # Calculate tire forces
            long_force, lat_force = tire_physics.calculate_tire_forces(
                (tire_vel_x, tire_vel_y), wheel_angular_vel, wheel_radius,
                vehicle_velocity, tire_angle
            )
            
            # Transform forces from tire coordinate system to vehicle coordinates
            cos_tire_angle = math.cos(tire_angle)
            sin_tire_angle = math.sin(tire_angle)
            
            force_x = long_force * cos_tire_angle - lat_force * sin_tire_angle
            force_y = long_force * sin_tire_angle + lat_force * cos_tire_angle
            
            # Add to total forces
            total_force_x += force_x
            total_force_y += force_y
            
            # Calculate torque contribution
            torque = tire_pos[0] * force_y - tire_pos[1] * force_x
            total_torque += torque
        
        return (total_force_x, total_force_y, total_torque)
    
    def get_skidding_wheels(self) -> List[str]:
        """Get list of wheels that are currently skidding"""
        skidding_wheels = []
        for tire_name, tire_physics in self.tires.items():
            if tire_physics.is_skidding:
                skidding_wheels.append(tire_name)
        return skidding_wheels
    
    def get_total_smoke_amount(self) -> float:
        """Get total smoke generation from all tires"""
        return sum(tire.smoke_amount for tire in self.tires.values()) / 4.0
    
    def get_tire_sound_level(self) -> float:
        """Get combined tire noise level"""
        return max(tire.get_tire_sound_level() for tire in self.tires.values())
    
    def set_tire_pressure(self, wheel: str, pressure: float):
        """Set pressure for specific wheel"""
        if wheel in self.tires:
            self.tires[wheel].set_pressure(pressure)
    
    def puncture_tire(self, wheel: str):
        """Puncture specific tire"""
        if wheel in self.tires:
            self.tires[wheel].puncture_tire()
    
    def get_tire_stats(self) -> dict:
        """Get statistics for all tires"""
        stats = {}
        for tire_name, tire_physics in self.tires.items():
            stats[tire_name] = tire_physics.get_stats()
        return stats
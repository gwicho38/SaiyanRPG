#!/usr/bin/env python3
"""
Advanced Vehicle Mechanical System
Implements realistic mechanical systems including engine, transmission, brakes, and mechanical failures.
Based on Carnage3D vehicle mechanical mechanics.
"""

import random
import time
import math
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class EngineType(Enum):
    """Types of engines"""
    INLINE_4 = "inline_4"
    V6 = "v6"
    V8 = "v8"
    TURBO_4 = "turbo_4"
    DIESEL = "diesel"
    ELECTRIC = "electric"


class TransmissionType(Enum):
    """Types of transmissions"""
    MANUAL_3_SPEED = "manual_3"
    MANUAL_4_SPEED = "manual_4"
    MANUAL_5_SPEED = "manual_5"
    AUTOMATIC_3_SPEED = "auto_3"
    AUTOMATIC_4_SPEED = "auto_4"
    CVT = "cvt"


class MechanicalFailureType(Enum):
    """Types of mechanical failures"""
    ENGINE_OVERHEATING = "engine_overheating"
    ENGINE_KNOCK = "engine_knock"
    TRANSMISSION_SLIPPING = "transmission_slipping"
    BRAKE_FAILURE = "brake_failure"
    SUSPENSION_DAMAGE = "suspension_damage"
    EXHAUST_DAMAGE = "exhaust_damage"
    COOLING_SYSTEM_LEAK = "cooling_system_leak"
    OIL_LEAK = "oil_leak"
    BELT_FAILURE = "belt_failure"
    SPARK_PLUG_FAILURE = "spark_plug_failure"


@dataclass
class EngineStats:
    """Engine specifications and current state"""
    engine_type: EngineType
    displacement: float  # Liters
    max_power: float    # Horsepower
    max_torque: float   # Nm
    max_rpm: float      # RPM
    idle_rpm: float     # RPM
    redline_rpm: float  # RPM
    fuel_efficiency: float  # L/100km at optimal conditions


class VehicleMechanicalSystem:
    """Advanced mechanical system for vehicles"""
    
    def __init__(self, vehicle_type: str):
        self.vehicle_type = vehicle_type
        
        # Engine system
        self.engine_stats = self._get_engine_stats(vehicle_type)
        self.engine_temperature = 20.0  # Celsius
        self.engine_rpm = 0.0
        self.engine_running = False
        self.engine_load = 0.0  # 0.0 to 1.0
        self.throttle_position = 0.0  # 0.0 to 1.0
        
        # Transmission system  
        self.transmission_type = self._get_transmission_type(vehicle_type)
        self.current_gear = 0  # 0=Park/Neutral, 1=1st, etc., -1=Reverse
        self.gear_ratios = self._get_gear_ratios(self.transmission_type)
        self.clutch_engaged = True
        self.transmission_temperature = 50.0
        
        # Brake system
        self.brake_temperature = 20.0  # Celsius
        self.brake_wear_front = 0.0  # 0.0 to 1.0 (1.0 = completely worn)
        self.brake_wear_rear = 0.0
        self.brake_fluid_level = 1.0  # 0.0 to 1.0
        self.brake_pressure = 0.0  # 0.0 to 1.0
        
        # Cooling system
        self.coolant_level = 1.0  # 0.0 to 1.0
        self.coolant_temperature = 20.0  # Celsius
        self.radiator_efficiency = 1.0  # 0.0 to 1.0
        
        # Lubrication system
        self.oil_level = 1.0  # 0.0 to 1.0
        self.oil_temperature = 20.0  # Celsius
        self.oil_pressure = 0.0  # PSI
        self.oil_viscosity = 1.0  # Degradation factor
        
        # Suspension system
        self.suspension_wear = 0.0  # 0.0 to 1.0
        self.shock_absorber_efficiency = 1.0
        
        # Exhaust system
        self.exhaust_efficiency = 1.0  # 0.0 to 1.0
        self.catalytic_converter_efficiency = 1.0
        
        # Mechanical failures
        self.active_failures: List[MechanicalFailureType] = []
        self.failure_timestamps: Dict[MechanicalFailureType, float] = {}
        self.mean_time_between_failures = 7200.0  # 2 hours
        self.last_failure_check = time.time()
        
        # Performance modifiers
        self.power_multiplier = 1.0
        self.efficiency_multiplier = 1.0
        
        print(f"🔧 Mechanical system initialized for {vehicle_type}")
        print(f"   Engine: {self.engine_stats.engine_type.value} ({self.engine_stats.max_power:.0f}HP)")
        print(f"   Transmission: {self.transmission_type.value}")
    
    def _get_engine_stats(self, vehicle_type: str) -> EngineStats:
        """Get engine specifications based on vehicle type"""
        engine_configs = {
            "sports_car": EngineStats(
                EngineType.V8, 5.0, 450, 600, 8000, 800, 7500, 12.0
            ),
            "sedan": EngineStats(
                EngineType.INLINE_4, 2.0, 150, 200, 6500, 700, 6000, 7.5
            ),
            "truck": EngineStats(
                EngineType.V6, 3.5, 280, 400, 6000, 600, 5500, 11.0
            ),
            "suv": EngineStats(
                EngineType.V6, 3.0, 250, 350, 6200, 650, 5800, 9.5
            ),
            "police": EngineStats(
                EngineType.V8, 4.6, 350, 500, 7000, 700, 6500, 13.0
            ),
            "taxi": EngineStats(
                EngineType.INLINE_4, 2.4, 180, 240, 6000, 650, 5800, 8.0
            ),
            "ambulance": EngineStats(
                EngineType.V6, 3.7, 300, 420, 5800, 600, 5500, 12.0
            ),
            "fire_truck": EngineStats(
                EngineType.DIESEL, 7.2, 400, 1200, 4500, 600, 4200, 15.0
            )
        }
        
        return engine_configs.get(vehicle_type, engine_configs["sedan"])
    
    def _get_transmission_type(self, vehicle_type: str) -> TransmissionType:
        """Get transmission type based on vehicle type"""
        transmission_configs = {
            "sports_car": TransmissionType.MANUAL_5_SPEED,
            "sedan": TransmissionType.AUTOMATIC_4_SPEED,
            "truck": TransmissionType.MANUAL_4_SPEED,
            "suv": TransmissionType.AUTOMATIC_4_SPEED,
            "police": TransmissionType.AUTOMATIC_4_SPEED,
            "taxi": TransmissionType.AUTOMATIC_3_SPEED,
            "ambulance": TransmissionType.AUTOMATIC_4_SPEED,
            "fire_truck": TransmissionType.MANUAL_4_SPEED
        }
        
        return transmission_configs.get(vehicle_type, TransmissionType.AUTOMATIC_4_SPEED)
    
    def _get_gear_ratios(self, transmission: TransmissionType) -> List[float]:
        """Get gear ratios for transmission type"""
        gear_ratio_configs = {
            TransmissionType.MANUAL_3_SPEED: [2.8, 1.6, 1.0],
            TransmissionType.MANUAL_4_SPEED: [3.2, 2.1, 1.4, 1.0],
            TransmissionType.MANUAL_5_SPEED: [3.5, 2.2, 1.5, 1.1, 0.85],
            TransmissionType.AUTOMATIC_3_SPEED: [2.5, 1.5, 1.0],
            TransmissionType.AUTOMATIC_4_SPEED: [2.8, 1.8, 1.2, 1.0],
            TransmissionType.CVT: [3.0, 1.0]  # Simplified for CVT
        }
        
        return gear_ratio_configs.get(transmission, [2.8, 1.8, 1.2, 1.0])
    
    def update(self, dt: float, throttle: float, brake: float, vehicle_speed_kmh: float) -> None:
        """Update mechanical system state"""
        self.throttle_position = max(0.0, min(1.0, throttle))
        brake_input = max(0.0, min(1.0, brake))
        
        # Update engine
        self._update_engine(dt, vehicle_speed_kmh)
        
        # Update transmission
        self._update_transmission(dt, vehicle_speed_kmh)
        
        # Update brakes
        self._update_brakes(dt, brake_input)
        
        # Update cooling system
        self._update_cooling_system(dt)
        
        # Update lubrication system
        self._update_lubrication_system(dt)
        
        # Check for mechanical failures
        self._check_for_failures(dt)
        
        # Update performance based on failures and wear
        self._update_performance_modifiers()
    
    def _update_engine(self, dt: float, vehicle_speed_kmh: float) -> None:
        """Update engine state"""
        if not self.engine_running:
            # Engine cooling down when off
            self.engine_temperature = max(20.0, self.engine_temperature - 50.0 * dt)
            self.engine_rpm = max(0.0, self.engine_rpm - 1000.0 * dt)
            return
        
        # Calculate target RPM based on throttle and speed
        if self.current_gear > 0:
            gear_ratio = self.gear_ratios[self.current_gear - 1]
            wheel_rpm = (vehicle_speed_kmh * 1000.0 / 60.0) / (math.pi * 0.35)  # Assume 0.35m wheel radius
            base_rpm = wheel_rpm * gear_ratio
        else:
            base_rpm = self.engine_stats.idle_rpm
        
        # Target RPM based on throttle
        target_rpm = self.engine_stats.idle_rpm + (
            (self.engine_stats.max_rpm - self.engine_stats.idle_rpm) * self.throttle_position
        )
        target_rpm = max(base_rpm, target_rpm)
        
        # Smooth RPM changes
        rpm_change_rate = 3000.0  # RPM per second
        if target_rpm > self.engine_rpm:
            self.engine_rpm = min(target_rpm, self.engine_rpm + rpm_change_rate * dt)
        else:
            self.engine_rpm = max(target_rpm, self.engine_rpm - rpm_change_rate * dt)
        
        # Calculate engine load
        self.engine_load = min(1.0, self.engine_rpm / self.engine_stats.max_rpm + self.throttle_position * 0.5)
        
        # Engine temperature increases with load
        target_temp = 90.0 + self.engine_load * 30.0  # 90-120°C normal range
        if MechanicalFailureType.ENGINE_OVERHEATING in self.active_failures:
            target_temp += 40.0
        
        temp_change_rate = 20.0  # °C per second
        if target_temp > self.engine_temperature:
            self.engine_temperature = min(target_temp, self.engine_temperature + temp_change_rate * dt)
        else:
            self.engine_temperature = max(target_temp, self.engine_temperature - temp_change_rate * dt)
    
    def _update_transmission(self, dt: float, vehicle_speed_kmh: float) -> None:
        """Update transmission state"""
        # Automatic gear shifting for automatic transmissions
        if "auto" in self.transmission_type.value or self.transmission_type == TransmissionType.CVT:
            self._auto_shift_gears(vehicle_speed_kmh)
        
        # Transmission temperature
        self.transmission_temperature = 50.0 + self.engine_load * 30.0
        if MechanicalFailureType.TRANSMISSION_SLIPPING in self.active_failures:
            self.transmission_temperature += 20.0
    
    def _auto_shift_gears(self, vehicle_speed_kmh: float) -> None:
        """Automatic transmission gear shifting logic"""
        if not self.engine_running or vehicle_speed_kmh < 0.1:
            return
        
        # Shift points based on speed (simplified)
        if self.transmission_type == TransmissionType.AUTOMATIC_3_SPEED:
            shift_points = [15, 40]  # km/h
        elif self.transmission_type == TransmissionType.AUTOMATIC_4_SPEED:
            shift_points = [15, 35, 65]  # km/h
        else:  # CVT
            # CVT continuously adjusts, simulate with 2 virtual gears
            shift_points = [30]
        
        # Determine target gear
        target_gear = 1
        for i, shift_point in enumerate(shift_points):
            if vehicle_speed_kmh > shift_point:
                target_gear = i + 2
        
        # Hysteresis for downshifting (shift down at lower speeds)
        if self.current_gear > target_gear:
            downshift_points = [s * 0.8 for s in shift_points]
            for i, shift_point in enumerate(downshift_points):
                if vehicle_speed_kmh > shift_point:
                    target_gear = max(target_gear, i + 2)
        
        # Apply gear change if needed
        if target_gear != self.current_gear and target_gear <= len(self.gear_ratios):
            self.shift_gear(target_gear)
    
    def _update_brakes(self, dt: float, brake_input: float) -> None:
        """Update brake system state"""
        self.brake_pressure = brake_input
        
        # Brake temperature increases with use
        if brake_input > 0.1:
            heat_generation = brake_input * 100.0  # °C per second
            self.brake_temperature += heat_generation * dt
        else:
            # Cooling when not braking
            cooling_rate = 50.0  # °C per second
            self.brake_temperature = max(20.0, self.brake_temperature - cooling_rate * dt)
        
        # Brake wear increases with use
        wear_rate = brake_input * 0.001 * dt  # 0.1% per second of full braking
        self.brake_wear_front += wear_rate
        self.brake_wear_rear += wear_rate * 0.7  # Rear brakes wear less
        
        # Brake fluid temperature
        brake_fluid_temp = self.brake_temperature * 0.8
        if brake_fluid_temp > 200.0:  # Brake fluid boiling
            self.brake_pressure *= 0.5  # Reduced braking effectiveness
    
    def _update_cooling_system(self, dt: float) -> None:
        """Update cooling system state"""
        if MechanicalFailureType.COOLING_SYSTEM_LEAK in self.active_failures:
            self.coolant_level = max(0.0, self.coolant_level - 0.01 * dt)  # 1% per second leak
        
        # Coolant temperature follows engine temperature
        target_coolant_temp = self.engine_temperature - 10.0
        temp_change_rate = 15.0
        
        if target_coolant_temp > self.coolant_temperature:
            self.coolant_temperature = min(target_coolant_temp, 
                                         self.coolant_temperature + temp_change_rate * dt)
        else:
            self.coolant_temperature = max(target_coolant_temp,
                                         self.coolant_temperature - temp_change_rate * dt)
        
        # Radiator efficiency affects cooling
        if self.coolant_level < 0.3:
            self.radiator_efficiency = 0.3  # Poor cooling with low coolant
        elif MechanicalFailureType.COOLING_SYSTEM_LEAK in self.active_failures:
            self.radiator_efficiency = 0.6
        else:
            self.radiator_efficiency = 1.0
    
    def _update_lubrication_system(self, dt: float) -> None:
        """Update oil/lubrication system state"""
        if self.engine_running:
            # Oil pressure when engine is running
            base_pressure = 30.0  # PSI
            rpm_factor = self.engine_rpm / self.engine_stats.max_rpm
            self.oil_pressure = base_pressure * (0.5 + 0.5 * rpm_factor) * self.oil_level
        else:
            self.oil_pressure = 0.0
        
        # Oil temperature follows engine temperature
        target_oil_temp = self.engine_temperature + 20.0
        temp_change_rate = 10.0
        
        if target_oil_temp > self.oil_temperature:
            self.oil_temperature = min(target_oil_temp, self.oil_temperature + temp_change_rate * dt)
        else:
            self.oil_temperature = max(target_oil_temp, self.oil_temperature - temp_change_rate * dt)
        
        # Oil degradation over time
        if self.engine_running:
            degradation_rate = 0.00001 * (1.0 + self.engine_load) * dt
            self.oil_viscosity = max(0.3, self.oil_viscosity - degradation_rate)
        
        # Oil leaks
        if MechanicalFailureType.OIL_LEAK in self.active_failures:
            self.oil_level = max(0.0, self.oil_level - 0.005 * dt)  # 0.5% per second leak
    
    def _check_for_failures(self, dt: float) -> None:
        """Check for mechanical failures based on wear and conditions"""
        current_time = time.time()
        
        if current_time - self.last_failure_check > 15.0:  # Check every 15 seconds
            self.last_failure_check = current_time
            
            # Calculate failure probabilities based on conditions
            failure_checks = [
                (MechanicalFailureType.ENGINE_OVERHEATING, 
                 0.001 if self.engine_temperature > 120.0 else 0.0001),
                (MechanicalFailureType.TRANSMISSION_SLIPPING,
                 0.0005 if self.transmission_temperature > 100.0 else 0.0001),
                (MechanicalFailureType.BRAKE_FAILURE,
                 0.001 if self.brake_wear_front > 0.8 else 0.0001),
                (MechanicalFailureType.COOLING_SYSTEM_LEAK,
                 0.0008 if self.engine_temperature > 110.0 else 0.0002),
                (MechanicalFailureType.OIL_LEAK,
                 0.0005 if self.oil_pressure < 15.0 else 0.0001),
                (MechanicalFailureType.EXHAUST_DAMAGE,
                 0.0003),
                (MechanicalFailureType.SUSPENSION_DAMAGE,
                 0.0002)
            ]
            
            for failure_type, probability in failure_checks:
                if failure_type not in self.active_failures and random.random() < probability:
                    self._cause_mechanical_failure(failure_type)
    
    def _cause_mechanical_failure(self, failure_type: MechanicalFailureType) -> None:
        """Cause a specific mechanical failure"""
        self.active_failures.append(failure_type)
        self.failure_timestamps[failure_type] = time.time()
        
        print(f"🔧 Mechanical failure: {failure_type.value}")
        
        # Immediate effects of failures
        if failure_type == MechanicalFailureType.ENGINE_OVERHEATING:
            self.engine_temperature += 30.0
        elif failure_type == MechanicalFailureType.BRAKE_FAILURE:
            self.brake_fluid_level = 0.2
        elif failure_type == MechanicalFailureType.COOLING_SYSTEM_LEAK:
            self.coolant_level = 0.4
        elif failure_type == MechanicalFailureType.OIL_LEAK:
            self.oil_level = 0.6
    
    def _update_performance_modifiers(self) -> None:
        """Update performance modifiers based on mechanical condition"""
        self.power_multiplier = 1.0
        self.efficiency_multiplier = 1.0
        
        # Engine condition effects
        if self.engine_temperature > 120.0:
            self.power_multiplier *= 0.8  # Overheating reduces power
        
        if self.oil_level < 0.3:
            self.power_multiplier *= 0.9  # Low oil affects performance
        
        if self.oil_viscosity < 0.5:
            self.efficiency_multiplier *= 0.9  # Old oil reduces efficiency
        
        # Transmission effects
        if MechanicalFailureType.TRANSMISSION_SLIPPING in self.active_failures:
            self.power_multiplier *= 0.7  # Power loss due to slipping
        
        # Exhaust effects
        if MechanicalFailureType.EXHAUST_DAMAGE in self.active_failures:
            self.power_multiplier *= 0.95
            self.efficiency_multiplier *= 0.9
        
        # Ensure values stay in reasonable bounds
        self.power_multiplier = max(0.1, min(1.2, self.power_multiplier))
        self.efficiency_multiplier = max(0.3, min(1.1, self.efficiency_multiplier))
    
    def start_engine(self) -> bool:
        """Attempt to start the engine"""
        # Check prerequisites for starting
        if self.oil_level < 0.1:
            print("🔧 Cannot start engine: insufficient oil")
            return False
        
        if self.coolant_level < 0.2:
            print("🔧 Cannot start engine: insufficient coolant")
            return False
        
        if MechanicalFailureType.ENGINE_OVERHEATING in self.active_failures:
            print("🔧 Cannot start engine: overheated")
            return False
        
        self.engine_running = True
        self.engine_rpm = self.engine_stats.idle_rpm
        self.current_gear = 1 if "manual" in self.transmission_type.value else 0
        
        print(f"🚗 Engine started: {self.engine_stats.engine_type.value}")
        return True
    
    def stop_engine(self) -> None:
        """Stop the engine"""
        self.engine_running = False
        self.current_gear = 0
        print("🔧 Engine stopped")
    
    def shift_gear(self, gear: int) -> bool:
        """Shift to specified gear"""
        if not self.engine_running:
            return False
        
        # Check gear bounds
        if gear < -1 or gear > len(self.gear_ratios):
            return False
        
        # Manual transmission requires clutch
        if "manual" in self.transmission_type.value and not self.clutch_engaged:
            print("🔧 Cannot shift: clutch not engaged")
            return False
        
        self.current_gear = gear
        gear_name = "Reverse" if gear == -1 else f"Gear {gear}" if gear > 0 else "Neutral"
        print(f"⚙️ Shifted to {gear_name}")
        return True
    
    def engage_clutch(self, engaged: bool) -> None:
        """Engage/disengage clutch (manual transmissions)"""
        if "manual" in self.transmission_type.value:
            self.clutch_engaged = engaged
            clutch_state = "engaged" if engaged else "disengaged"
            print(f"🔧 Clutch {clutch_state}")
    
    def get_engine_power(self) -> float:
        """Get current engine power output in horsepower"""
        if not self.engine_running:
            return 0.0
        
        # Power curve based on RPM
        rpm_ratio = self.engine_rpm / self.engine_stats.max_rpm
        
        if rpm_ratio < 0.2:  # Below peak torque RPM
            power_ratio = rpm_ratio * 2.5  # Linear increase
        elif rpm_ratio < 0.6:  # Peak power band
            power_ratio = 0.8 + (rpm_ratio - 0.2) * 0.5  # Peak efficiency
        else:  # Above peak power
            power_ratio = 1.0 - (rpm_ratio - 0.6) * 0.7  # Power drops off
        
        base_power = self.engine_stats.max_power * power_ratio * self.throttle_position
        return base_power * self.power_multiplier
    
    def get_brake_effectiveness(self) -> float:
        """Get current brake effectiveness (0.0 to 1.0)"""
        # Brake effectiveness decreases with wear and overheating
        wear_factor = 1.0 - (self.brake_wear_front * 0.8 + self.brake_wear_rear * 0.2)
        
        # Temperature affects braking (brake fade)
        temp_factor = 1.0
        if self.brake_temperature > 300.0:
            temp_factor = 0.5  # Severe brake fade
        elif self.brake_temperature > 200.0:
            temp_factor = 0.8  # Moderate brake fade
        
        # Brake fluid level affects pressure
        fluid_factor = min(1.0, self.brake_fluid_level * 2.0)
        
        effectiveness = wear_factor * temp_factor * fluid_factor
        
        # Brake failure
        if MechanicalFailureType.BRAKE_FAILURE in self.active_failures:
            effectiveness *= 0.3
        
        return max(0.0, min(1.0, effectiveness))
    
    def repair_component(self, failure_type: MechanicalFailureType) -> bool:
        """Repair a specific mechanical failure"""
        if failure_type not in self.active_failures:
            return True  # Already functional
        
        # Simulate repair success based on failure type
        repair_difficulty = {
            MechanicalFailureType.ENGINE_OVERHEATING: 0.8,
            MechanicalFailureType.TRANSMISSION_SLIPPING: 0.6,
            MechanicalFailureType.BRAKE_FAILURE: 0.9,
            MechanicalFailureType.COOLING_SYSTEM_LEAK: 0.7,
            MechanicalFailureType.OIL_LEAK: 0.8,
            MechanicalFailureType.EXHAUST_DAMAGE: 0.9,
            MechanicalFailureType.SUSPENSION_DAMAGE: 0.7
        }
        
        success_rate = repair_difficulty.get(failure_type, 0.8)
        
        if random.random() < success_rate:
            self.active_failures.remove(failure_type)
            del self.failure_timestamps[failure_type]
            
            # Restore some component condition
            if failure_type == MechanicalFailureType.COOLING_SYSTEM_LEAK:
                self.coolant_level = 1.0
            elif failure_type == MechanicalFailureType.OIL_LEAK:
                self.oil_level = 1.0
            elif failure_type == MechanicalFailureType.BRAKE_FAILURE:
                self.brake_fluid_level = 1.0
                self.brake_wear_front *= 0.8
                self.brake_wear_rear *= 0.8
            
            print(f"🔧 Repaired {failure_type.value}")
            return True
        else:
            print(f"❌ Failed to repair {failure_type.value}")
            return False
    
    def get_mechanical_status(self) -> Dict:
        """Get comprehensive mechanical system status"""
        return {
            "engine_running": self.engine_running,
            "engine_rpm": round(self.engine_rpm, 0),
            "engine_temperature": round(self.engine_temperature, 1),
            "engine_power": round(self.get_engine_power(), 1),
            "current_gear": self.current_gear,
            "transmission_temp": round(self.transmission_temperature, 1),
            "brake_effectiveness": round(self.get_brake_effectiveness() * 100, 1),
            "brake_temperature": round(self.brake_temperature, 1),
            "oil_level": round(self.oil_level * 100, 1),
            "oil_pressure": round(self.oil_pressure, 1),
            "coolant_level": round(self.coolant_level * 100, 1),
            "active_failures": [f.value for f in self.active_failures],
            "power_multiplier": round(self.power_multiplier, 2),
            "efficiency_multiplier": round(self.efficiency_multiplier, 2)
        }
    
    def get_warning_indicators(self) -> List[str]:
        """Get list of warning indicators that should be displayed"""
        warnings = []
        
        # Engine warnings
        if self.engine_temperature > 110.0:
            warnings.append("ENGINE_OVERHEATING")
        if self.oil_pressure < 15.0 and self.engine_running:
            warnings.append("LOW_OIL_PRESSURE")
        if self.oil_level < 0.3:
            warnings.append("LOW_OIL_LEVEL")
        
        # Cooling system warnings
        if self.coolant_level < 0.3:
            warnings.append("LOW_COOLANT")
        if self.coolant_temperature > 105.0:
            warnings.append("HIGH_COOLANT_TEMP")
        
        # Brake system warnings
        if self.brake_fluid_level < 0.3:
            warnings.append("LOW_BRAKE_FLUID")
        if self.brake_temperature > 250.0:
            warnings.append("BRAKE_OVERHEAT")
        if self.brake_wear_front > 0.8 or self.brake_wear_rear > 0.8:
            warnings.append("BRAKE_WEAR")
        
        # Transmission warnings
        if self.transmission_temperature > 120.0:
            warnings.append("TRANSMISSION_OVERHEAT")
        
        return warnings
#!/usr/bin/env python3
"""
Advanced Vehicle Electrical System
Implements realistic electrical systems including battery, alternator, lights, and electrical failures.
Based on Carnage3D vehicle electrical mechanics.
"""

import random
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class ElectricalComponent(Enum):
    """Types of electrical components in a vehicle"""
    BATTERY = "battery"
    ALTERNATOR = "alternator" 
    HEADLIGHTS = "headlights"
    TAILLIGHTS = "taillights"
    TURN_SIGNALS = "turn_signals"
    BRAKE_LIGHTS = "brake_lights"
    REVERSE_LIGHTS = "reverse_lights"
    EMERGENCY_LIGHTS = "emergency_lights"
    INTERIOR_LIGHTS = "interior_lights"
    DASHBOARD = "dashboard"
    RADIO = "radio"
    AIR_CONDITIONING = "air_conditioning"
    WINDSHIELD_WIPERS = "windshield_wipers"
    HORN = "horn"
    STARTER = "starter"
    IGNITION = "ignition"


class ElectricalFailureType(Enum):
    """Types of electrical failures"""
    BLOWN_FUSE = "blown_fuse"
    DEAD_BATTERY = "dead_battery"
    FAULTY_ALTERNATOR = "faulty_alternator"
    BURNT_BULB = "burnt_bulb"
    LOOSE_CONNECTION = "loose_connection"
    SHORT_CIRCUIT = "short_circuit"
    CORRODED_TERMINALS = "corroded_terminals"


@dataclass
class ElectricalComponentState:
    """State of an individual electrical component"""
    component: ElectricalComponent
    is_on: bool = False
    is_functional: bool = True
    power_draw: float = 0.0  # Watts
    failure_type: Optional[ElectricalFailureType] = None
    failure_time: float = 0.0
    brightness: float = 1.0  # For lights (0.0 to 1.0)
    flashing: bool = False
    flash_rate: float = 1.0  # Hz


class VehicleElectricalSystem:
    """Advanced electrical system for vehicles"""
    
    def __init__(self, vehicle_type: str):
        self.vehicle_type = vehicle_type
        
        # Battery system
        self.battery_voltage = 12.6  # Fully charged battery
        self.battery_capacity = 60.0  # Amp-hours
        self.battery_charge = 1.0  # 0.0 to 1.0
        self.alternator_output = 14.4  # Volts when engine running
        self.alternator_functional = True
        
        # Initialize electrical components
        self.components: Dict[ElectricalComponent, ElectricalComponentState] = {}
        self._initialize_components()
        
        # Electrical load tracking
        self.total_power_draw = 0.0
        self.engine_running = False
        
        # Failure simulation
        self.mean_time_between_failures = 3600.0  # 1 hour average
        self.last_failure_check = time.time()
        
        # Light patterns for emergency vehicles
        self.emergency_light_patterns = {
            "police": [(True, False), (False, True)] * 4,
            "ambulance": [(True, True), (False, False)] * 3,
            "fire_truck": [(True, False, False), (False, True, False), (False, False, True)] * 2
        }
        
        print(f"🔌 Electrical system initialized for {vehicle_type}")
    
    def _initialize_components(self) -> None:
        """Initialize all electrical components with default states"""
        # Base components for all vehicles
        base_components = {
            ElectricalComponent.BATTERY: 0.5,
            ElectricalComponent.ALTERNATOR: 0.0,
            ElectricalComponent.HEADLIGHTS: 110.0,
            ElectricalComponent.TAILLIGHTS: 40.0,
            ElectricalComponent.TURN_SIGNALS: 42.0,
            ElectricalComponent.BRAKE_LIGHTS: 42.0,
            ElectricalComponent.REVERSE_LIGHTS: 42.0,
            ElectricalComponent.INTERIOR_LIGHTS: 20.0,
            ElectricalComponent.DASHBOARD: 15.0,
            ElectricalComponent.RADIO: 25.0,
            ElectricalComponent.HORN: 80.0,
            ElectricalComponent.STARTER: 400.0,
            ElectricalComponent.IGNITION: 5.0
        }
        
        # Additional components based on vehicle type
        if self.vehicle_type in ["police", "ambulance", "fire_truck"]:
            base_components[ElectricalComponent.EMERGENCY_LIGHTS] = 200.0
        
        if self.vehicle_type in ["sedan", "sports_car", "suv"]:
            base_components[ElectricalComponent.AIR_CONDITIONING] = 300.0
            base_components[ElectricalComponent.WINDSHIELD_WIPERS] = 60.0
        
        # Create component states
        for component, power_draw in base_components.items():
            self.components[component] = ElectricalComponentState(
                component=component,
                power_draw=power_draw
            )
    
    def update(self, dt: float, engine_running: bool) -> None:
        """Update electrical system state"""
        self.engine_running = engine_running
        
        # Update battery charge/discharge
        self._update_battery(dt)
        
        # Update component states
        self._update_components(dt)
        
        # Check for electrical failures
        self._check_for_failures(dt)
        
        # Update emergency light patterns
        self._update_emergency_lights(dt)
        
        # Calculate total power draw
        self._calculate_power_draw()
    
    def _update_battery(self, dt: float) -> None:
        """Update battery charge based on electrical load and alternator output"""
        # Calculate net power flow
        charging_power = 0.0
        if self.engine_running and self.alternator_functional:
            # Alternator provides power when engine is running
            max_alternator_power = 1000.0  # Watts
            charging_power = min(max_alternator_power, self.total_power_draw + 200.0)
        
        # Net power (positive = charging, negative = discharging)
        net_power = charging_power - self.total_power_draw
        
        # Update battery charge (rough approximation)
        battery_wh_capacity = self.battery_capacity * self.battery_voltage
        charge_rate = (net_power * dt) / (battery_wh_capacity * 3600.0)  # Convert to hours
        
        self.battery_charge = max(0.0, min(1.0, self.battery_charge + charge_rate))
        
        # Update battery voltage based on charge
        if self.battery_charge > 0.8:
            self.battery_voltage = 12.6 + (self.battery_charge - 0.8) * 0.8  # 12.6V to 13.0V
        elif self.battery_charge > 0.2:
            self.battery_voltage = 11.8 + (self.battery_charge - 0.2) * 1.33  # 11.8V to 12.6V
        else:
            self.battery_voltage = 10.5 + self.battery_charge * 6.5  # 10.5V to 11.8V
    
    def _update_components(self, dt: float) -> None:
        """Update individual component states"""
        for component_state in self.components.values():
            # Components fail gradually when battery is low
            if self.battery_voltage < 11.5:
                if component_state.component not in [ElectricalComponent.BATTERY, ElectricalComponent.ALTERNATOR]:
                    component_state.brightness *= 0.99  # Dim gradually
                    if component_state.brightness < 0.1:
                        component_state.is_functional = False
            
            # Handle flashing components
            if component_state.flashing and component_state.is_functional:
                flash_cycle = time.time() * component_state.flash_rate
                component_state.is_on = (flash_cycle % 1.0) < 0.5
    
    def _check_for_failures(self, dt: float) -> None:
        """Simulate random electrical failures"""
        current_time = time.time()
        
        if current_time - self.last_failure_check > 10.0:  # Check every 10 seconds
            self.last_failure_check = current_time
            
            # Calculate failure probability based on vehicle condition and age
            base_failure_rate = 1.0 / self.mean_time_between_failures
            
            # Check each component for failures
            for component_state in self.components.values():
                if component_state.is_functional and random.random() < base_failure_rate * 10.0:
                    self._cause_component_failure(component_state)
    
    def _cause_component_failure(self, component_state: ElectricalComponentState) -> None:
        """Cause a specific component to fail"""
        # Choose random failure type
        failure_types = list(ElectricalFailureType)
        component_state.failure_type = random.choice(failure_types)
        component_state.is_functional = False
        component_state.failure_time = time.time()
        
        print(f"⚡ Electrical failure: {component_state.component.value} - {component_state.failure_type.value}")
        
        # Special handling for critical failures
        if component_state.failure_type == ElectricalFailureType.DEAD_BATTERY:
            self.battery_charge = 0.0
            self.battery_voltage = 10.5
        elif component_state.failure_type == ElectricalFailureType.FAULTY_ALTERNATOR:
            self.alternator_functional = False
    
    def _update_emergency_lights(self, dt: float) -> None:
        """Update emergency light patterns"""
        if ElectricalComponent.EMERGENCY_LIGHTS not in self.components:
            return
        
        emergency_component = self.components[ElectricalComponent.EMERGENCY_LIGHTS]
        if not emergency_component.is_on or not emergency_component.is_functional:
            return
        
        # Implement flashing pattern based on vehicle type
        if self.vehicle_type in self.emergency_light_patterns:
            pattern = self.emergency_light_patterns[self.vehicle_type]
            pattern_time = time.time() * 2.0  # 2Hz base frequency
            pattern_index = int(pattern_time) % len(pattern)
            
            # Set brightness based on pattern
            if len(pattern[pattern_index]) > 1:
                emergency_component.brightness = 1.0 if any(pattern[pattern_index]) else 0.0
            else:
                emergency_component.brightness = 1.0 if pattern[pattern_index][0] else 0.0
    
    def _calculate_power_draw(self) -> None:
        """Calculate total electrical power consumption"""
        self.total_power_draw = 0.0
        
        for component_state in self.components.values():
            if component_state.is_on and component_state.is_functional:
                # Adjust power draw based on component condition
                actual_draw = component_state.power_draw
                if component_state.brightness < 1.0:
                    actual_draw *= component_state.brightness
                
                self.total_power_draw += actual_draw
    
    def turn_on_component(self, component: ElectricalComponent) -> bool:
        """Turn on a specific electrical component"""
        if component not in self.components:
            return False
        
        component_state = self.components[component]
        
        # Check if battery has enough power
        if self.battery_voltage < 10.0:
            print(f"🔋 Battery too low to turn on {component.value}")
            return False
        
        if not component_state.is_functional:
            print(f"⚡ Cannot turn on {component.value} - component failed")
            return False
        
        component_state.is_on = True
        print(f"💡 Turned on {component.value}")
        return True
    
    def turn_off_component(self, component: ElectricalComponent) -> None:
        """Turn off a specific electrical component"""
        if component in self.components:
            self.components[component].is_on = False
            print(f"🔌 Turned off {component.value}")
    
    def toggle_component(self, component: ElectricalComponent) -> bool:
        """Toggle a component on/off"""
        if component in self.components:
            if self.components[component].is_on:
                self.turn_off_component(component)
                return False
            else:
                return self.turn_on_component(component)
        return False
    
    def toggle_headlights(self) -> bool:
        """Toggle headlights"""
        return self.toggle_component(ElectricalComponent.HEADLIGHTS)
    
    def toggle_emergency_lights(self) -> bool:
        """Toggle emergency lights (for emergency vehicles)"""
        if ElectricalComponent.EMERGENCY_LIGHTS in self.components:
            return self.toggle_component(ElectricalComponent.EMERGENCY_LIGHTS)
        return False
    
    def set_turn_signal(self, direction: str) -> None:
        """Set turn signals (left, right, or off)"""
        turn_signal_component = self.components.get(ElectricalComponent.TURN_SIGNALS)
        if not turn_signal_component:
            return
        
        if direction == "off":
            turn_signal_component.is_on = False
            turn_signal_component.flashing = False
        elif direction in ["left", "right"]:
            if self.turn_on_component(ElectricalComponent.TURN_SIGNALS):
                turn_signal_component.flashing = True
                turn_signal_component.flash_rate = 1.5  # 1.5Hz
                print(f"🔄 Turn signal: {direction}")
    
    def activate_brake_lights(self, braking: bool) -> None:
        """Activate/deactivate brake lights"""
        if braking:
            self.turn_on_component(ElectricalComponent.BRAKE_LIGHTS)
        else:
            self.turn_off_component(ElectricalComponent.BRAKE_LIGHTS)
    
    def activate_reverse_lights(self, reversing: bool) -> None:
        """Activate/deactivate reverse lights"""
        if reversing:
            self.turn_on_component(ElectricalComponent.REVERSE_LIGHTS)
        else:
            self.turn_off_component(ElectricalComponent.REVERSE_LIGHTS)
    
    def try_start_engine(self) -> bool:
        """Attempt to start the engine using the starter"""
        if self.battery_voltage < 11.0:
            print("🔋 Battery too weak to start engine")
            return False
        
        starter = self.components.get(ElectricalComponent.STARTER)
        if not starter or not starter.is_functional:
            print("🔧 Starter motor failed")
            return False
        
        ignition = self.components.get(ElectricalComponent.IGNITION)
        if not ignition or not ignition.is_functional:
            print("🔧 Ignition system failed")
            return False
        
        # Briefly turn on starter (high power draw)
        starter.is_on = True
        # Reduce battery charge from starting effort
        self.battery_charge -= 0.02
        starter.is_on = False
        
        print("🚗 Engine started successfully")
        return True
    
    def repair_component(self, component: ElectricalComponent) -> bool:
        """Repair a failed electrical component"""
        if component not in self.components:
            return False
        
        component_state = self.components[component]
        if component_state.is_functional:
            return True  # Already functional
        
        # Simulate repair time and success
        repair_success = random.random() > 0.2  # 80% success rate
        
        if repair_success:
            component_state.is_functional = True
            component_state.failure_type = None
            component_state.brightness = 1.0
            
            if component == ElectricalComponent.ALTERNATOR:
                self.alternator_functional = True
            elif component == ElectricalComponent.BATTERY:
                self.battery_charge = 0.8  # Partially charged after repair
            
            print(f"🔧 Repaired {component.value}")
            return True
        else:
            print(f"❌ Failed to repair {component.value}")
            return False
    
    def get_electrical_status(self) -> Dict:
        """Get comprehensive electrical system status"""
        working_components = sum(1 for c in self.components.values() if c.is_functional)
        total_components = len(self.components)
        
        failed_components = [
            c.component.value for c in self.components.values() 
            if not c.is_functional
        ]
        
        active_components = [
            c.component.value for c in self.components.values() 
            if c.is_on and c.is_functional
        ]
        
        return {
            "battery_voltage": round(self.battery_voltage, 1),
            "battery_charge": round(self.battery_charge * 100, 1),
            "alternator_functional": self.alternator_functional,
            "total_power_draw": round(self.total_power_draw, 1),
            "component_health": f"{working_components}/{total_components}",
            "failed_components": failed_components,
            "active_components": active_components,
            "can_start_engine": self.battery_voltage >= 11.0
        }
    
    def get_light_status(self) -> Dict:
        """Get status of all lights"""
        light_components = [
            ElectricalComponent.HEADLIGHTS,
            ElectricalComponent.TAILLIGHTS,
            ElectricalComponent.TURN_SIGNALS,
            ElectricalComponent.BRAKE_LIGHTS,
            ElectricalComponent.REVERSE_LIGHTS,
            ElectricalComponent.EMERGENCY_LIGHTS
        ]
        
        light_status = {}
        for light in light_components:
            if light in self.components:
                component = self.components[light]
                light_status[light.value] = {
                    "on": component.is_on,
                    "functional": component.is_functional,
                    "brightness": component.brightness,
                    "flashing": component.flashing
                }
        
        return light_status
    
    def emergency_shutdown(self) -> None:
        """Emergency electrical shutdown (e.g., after severe damage)"""
        print("⚠️ EMERGENCY ELECTRICAL SHUTDOWN")
        
        # Turn off all non-essential components
        essential_components = [
            ElectricalComponent.BATTERY,
            ElectricalComponent.EMERGENCY_LIGHTS,
            ElectricalComponent.BRAKE_LIGHTS
        ]
        
        for component_state in self.components.values():
            if component_state.component not in essential_components:
                component_state.is_on = False
        
        # Reduce battery charge
        self.battery_charge *= 0.8
    
    def get_failure_summary(self) -> List[str]:
        """Get summary of all current electrical failures"""
        failures = []
        
        for component_state in self.components.values():
            if not component_state.is_functional and component_state.failure_type:
                failures.append(
                    f"{component_state.component.value}: {component_state.failure_type.value}"
                )
        
        if not self.alternator_functional:
            failures.append("alternator: not charging battery")
        
        if self.battery_charge < 0.2:
            failures.append("battery: critically low charge")
        
        return failures
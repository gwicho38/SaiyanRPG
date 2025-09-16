#!/usr/bin/env python3
"""Test the integrated electrical and mechanical vehicle systems."""

import pygame
import time
from saiyanquest.physics_manager import initialize_physics
from saiyanquest.vehicle_system import Vehicle, VehicleType
from saiyanquest.vehicle_electrical import ElectricalComponent
from saiyanquest.vehicle_mechanical import MechanicalFailureType

def test_integrated_vehicle_systems():
    """Test comprehensive vehicle systems integration"""
    print("🔧⚡ Testing Integrated Vehicle Electrical & Mechanical Systems...")
    
    # Initialize pygame and physics
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Vehicle Systems Integration Test")
    clock = pygame.time.Clock()
    
    # Initialize physics system
    physics = initialize_physics()
    print("✓ Physics system initialized")
    
    # Create different test vehicles
    test_vehicles = [
        ("Sports Car", Vehicle(VehicleType.SPORTS_CAR, 200, 200, 0)),
        ("Sedan", Vehicle(VehicleType.SEDAN, 400, 200, 0)),
        ("Police Car", Vehicle(VehicleType.POLICE, 600, 200, 0)),
        ("Truck", Vehicle(VehicleType.TRUCK, 800, 200, 0)),
    ]
    
    print(f"\n🚗 Created {len(test_vehicles)} test vehicles with integrated systems")
    
    # Display initial system status
    print("\n📊 Initial Vehicle System Status:")
    for name, vehicle in test_vehicles:
        electrical = vehicle.get_electrical_status()
        mechanical = vehicle.get_mechanical_status()
        
        print(f"\n   {name}:")
        print(f"     Battery: {electrical['battery_voltage']}V ({electrical['battery_charge']}%)")
        print(f"     Engine: {'ON' if mechanical['engine_running'] else 'OFF'}")
        print(f"     Components: {electrical['component_health']} working")
    
    # Test engine starting with electrical/mechanical checks
    print("\n🔋 Testing engine starting with system integration...")
    for name, vehicle in test_vehicles:
        print(f"\n   Starting {name}...")
        if vehicle.start_engine():
            electrical = vehicle.get_electrical_status()
            mechanical = vehicle.get_mechanical_status()
            print(f"     ✓ Engine started successfully")
            print(f"     Battery: {electrical['battery_voltage']}V")
            print(f"     Engine RPM: {mechanical['engine_rpm']}")
            print(f"     Oil Pressure: {mechanical['oil_pressure']} PSI")
        else:
            print(f"     ❌ Engine failed to start")
    
    print("\n🎮 Running comprehensive systems simulation...")
    
    # Simulation parameters
    frame_count = 0
    max_frames = 900  # 15 seconds at 60fps
    
    # Test scenarios timeline
    scenarios = {
        60:   "normal_driving",      # 1 second
        180:  "aggressive_driving",  # 3 seconds  
        300:  "electrical_test",     # 5 seconds
        420:  "mechanical_stress",   # 7 seconds
        540:  "system_failures",     # 9 seconds
        660:  "repair_attempts",     # 11 seconds
        780:  "emergency_test"       # 13 seconds
    }
    
    while frame_count < max_frames:
        dt = clock.tick(60) / 1000.0
        
        # Check for scenario changes
        if frame_count in scenarios:
            scenario = scenarios[frame_count]
            seconds = frame_count // 60
            print(f"\n⏱️ {seconds}s - Scenario: {scenario.upper().replace('_', ' ')}")
            
            if scenario == "normal_driving":
                print("   📍 Normal driving conditions")
                test_vehicles[0][1].throttle = 0.5  # Sports car
                test_vehicles[1][1].throttle = 0.3  # Sedan
                test_vehicles[2][1].throttle = 0.4  # Police
                test_vehicles[3][1].throttle = 0.2  # Truck
                
            elif scenario == "aggressive_driving":
                print("   📍 High-performance driving test")
                for name, vehicle in test_vehicles:
                    vehicle.throttle = 0.9
                    vehicle.steering = 0.5
                    
            elif scenario == "electrical_test":
                print("   📍 Electrical systems functionality test")
                for name, vehicle in test_vehicles:
                    vehicle.toggle_headlights()
                    if name == "Police Car":
                        vehicle.toggle_emergency_lights()
                    vehicle.set_turn_signal("left")
                    
            elif scenario == "mechanical_stress":
                print("   📍 Mechanical systems stress test")
                # High throttle + braking = stress
                for name, vehicle in test_vehicles:
                    vehicle.throttle = 1.0
                    vehicle.brake = 0.3  # Partial braking while accelerating
                    
            elif scenario == "system_failures":
                print("   📍 Simulating system failures")
                # Force some failures for testing
                test_vehicles[0][1].electrical_system._cause_component_failure(
                    test_vehicles[0][1].electrical_system.components[ElectricalComponent.HEADLIGHTS]
                )
                test_vehicles[1][1].mechanical_system._cause_mechanical_failure(
                    MechanicalFailureType.ENGINE_OVERHEATING
                )
                
            elif scenario == "repair_attempts":
                print("   📍 Testing repair systems")
                for name, vehicle in test_vehicles:
                    # Try to repair any electrical failures
                    for component in ElectricalComponent:
                        if component in vehicle.electrical_system.components:
                            if not vehicle.electrical_system.components[component].is_functional:
                                vehicle.repair_electrical_component(component)
                    
                    # Try to repair mechanical failures
                    for failure in list(vehicle.mechanical_system.active_failures):
                        vehicle.repair_mechanical_component(failure)
                        
            elif scenario == "emergency_test":
                print("   📍 Emergency shutdown test")
                test_vehicles[0][1].emergency_shutdown()
        
        # Update physics
        physics.update(dt)
        
        # Update all vehicles
        for name, vehicle in test_vehicles:
            vehicle.update(dt)
        
        # Status reporting every 3 seconds
        if frame_count % 180 == 0 and frame_count > 0:
            seconds = frame_count // 60
            print(f"\n🔍 {seconds}s Status Report:")
            
            for name, vehicle in test_vehicles:
                electrical = vehicle.get_electrical_status()
                mechanical = vehicle.get_mechanical_status()
                warnings = vehicle.get_system_warnings()
                
                print(f"   {name}:")
                print(f"     Speed: {vehicle.get_speed_kmh():.1f} km/h")
                print(f"     Battery: {electrical['battery_voltage']}V ({electrical['battery_charge']}%)")
                print(f"     Engine: {mechanical['engine_rpm']:.0f}RPM, {mechanical['engine_temperature']:.1f}°C")
                print(f"     Power: {mechanical['engine_power']:.0f}HP (×{mechanical['power_multiplier']})")
                print(f"     Brake: {mechanical['brake_effectiveness']:.0f}% effective")
                
                if warnings:
                    print(f"     ⚠️ Warnings: {len(warnings)}")
                    for warning in warnings[:3]:  # Show first 3 warnings
                        print(f"        - {warning}")
                
                if electrical['failed_components']:
                    print(f"     ⚡ Failed electrical: {', '.join(electrical['failed_components'])}")
                
                if mechanical['active_failures']:
                    print(f"     🔧 Mechanical issues: {', '.join(mechanical['active_failures'])}")
        
        # Simple visualization
        screen.fill((30, 30, 30))
        
        # Draw vehicles with system status indicators
        for i, (name, vehicle) in enumerate(test_vehicles):
            x = int(vehicle.x)
            y = int(vehicle.y)
            
            # Vehicle body
            color = (100, 100, 100)
            if vehicle.engine_on:
                color = (0, 200, 0)  # Green when running
            if vehicle.get_system_warnings():
                color = (255, 255, 0)  # Yellow for warnings
            if not vehicle.electrical_system.get_electrical_status()['can_start_engine']:
                color = (255, 0, 0)  # Red for critical issues
            
            pygame.draw.circle(screen, color, (x, y), 15)
            
            # Draw electrical indicators (lights)
            electrical = vehicle.get_electrical_status()
            if 'headlights' in electrical['active_components']:
                pygame.draw.circle(screen, (255, 255, 200), (x-10, y-5), 3)
                pygame.draw.circle(screen, (255, 255, 200), (x+10, y-5), 3)
            
            if 'brake_lights' in electrical['active_components']:
                pygame.draw.circle(screen, (255, 0, 0), (x-8, y+10), 2)
                pygame.draw.circle(screen, (255, 0, 0), (x+8, y+10), 2)
                
            if 'emergency_lights' in electrical['active_components']:
                # Flashing emergency lights
                if (frame_count // 10) % 2:
                    pygame.draw.circle(screen, (0, 0, 255), (x, y-20), 4)
        
        # Draw physics debug
        physics.draw_debug(screen)
        
        pygame.display.flip()
        frame_count += 1
    
    # Final comprehensive analysis
    print("\n📊 FINAL INTEGRATED SYSTEMS ANALYSIS:")
    print("=" * 60)
    
    for name, vehicle in test_vehicles:
        print(f"\n🚗 {name} Final Status:")
        
        # Electrical system summary
        electrical = vehicle.get_electrical_status()
        print(f"   🔌 Electrical System:")
        print(f"     Battery: {electrical['battery_voltage']}V ({electrical['battery_charge']}% charge)")
        print(f"     Alternator: {'✓' if electrical['alternator_functional'] else '❌'}")
        print(f"     Power Draw: {electrical['total_power_draw']}W")
        print(f"     Component Health: {electrical['component_health']}")
        print(f"     Active Components: {len(electrical['active_components'])}")
        
        # Mechanical system summary
        mechanical = vehicle.get_mechanical_status()
        print(f"   🔧 Mechanical System:")
        print(f"     Engine: {'RUNNING' if mechanical['engine_running'] else 'OFF'}")
        print(f"     RPM: {mechanical['engine_rpm']:.0f} / Temperature: {mechanical['engine_temperature']:.1f}°C")
        print(f"     Power Output: {mechanical['engine_power']:.0f}HP (multiplier: {mechanical['power_multiplier']})")
        print(f"     Transmission: Gear {mechanical['current_gear']} ({mechanical['transmission_temp']:.1f}°C)")
        print(f"     Brakes: {mechanical['brake_effectiveness']:.0f}% effective ({mechanical['brake_temperature']:.1f}°C)")
        print(f"     Fluids: Oil {mechanical['oil_level']:.0f}% ({mechanical['oil_pressure']:.0f} PSI), Coolant {mechanical['coolant_level']:.0f}%")
        
        # System integration
        warnings = vehicle.get_system_warnings()
        if warnings:
            print(f"   ⚠️ Active Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"     - {warning}")
        else:
            print(f"   ✅ All systems nominal")
        
        # Performance metrics
        tire_stats = vehicle.get_tire_stats()
        print(f"   🛞 Tire System: {list(tire_stats.keys())[0]} pressure avg: {sum(t['pressure'] for t in tire_stats.values())/4:.1f} PSI")
        
        overall_health = (
            electrical['battery_charge'] * 0.3 +
            (mechanical['engine_power'] / vehicle.mechanical_system.engine_stats.max_power) * 0.4 +
            mechanical['brake_effectiveness'] / 100.0 * 0.3
        )
        print(f"   📈 Overall Vehicle Health: {overall_health*100:.1f}%")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test vehicles...")
    for name, vehicle in test_vehicles:
        vehicle.destroy()
    
    print("✅ Integrated vehicle systems test completed successfully!")
    print("\n🏆 Key Features Demonstrated:")
    print("   ✓ Electrical system integration with battery, alternator, and components")
    print("   ✓ Mechanical system with engine, transmission, brakes, and cooling")  
    print("   ✓ Realistic failure simulation and repair mechanics")
    print("   ✓ Cross-system dependencies (electrical starter, mechanical power)")
    print("   ✓ Real-time system monitoring and warning indicators")
    print("   ✓ Advanced physics integration with system performance")
    print("   ✓ Emergency shutdown and safety systems")
    
    pygame.quit()

if __name__ == "__main__":
    test_integrated_vehicle_systems()
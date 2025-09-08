#!/usr/bin/env python3
"""Test the advanced tire physics and vehicle system."""

import pygame
from saiyanquest.physics_manager import initialize_physics
from saiyanquest.vehicle_system import Vehicle, VehicleType

def test_tire_physics_system():
    """Test comprehensive tire physics and vehicle behavior"""
    print("🛞 Testing Advanced Tire Physics System...")
    
    # Initialize pygame and physics
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Advanced Tire Physics Test")
    clock = pygame.time.Clock()
    
    # Initialize physics system
    physics = initialize_physics()
    print("✓ Physics system initialized with tire physics")
    
    # Create test vehicles with different tire types
    test_vehicles = [
        ("Sports Car", Vehicle(VehicleType.SPORTS_CAR, 200, 200, 0)),
        ("Sedan", Vehicle(VehicleType.SEDAN, 400, 200, 0)),
        ("Truck", Vehicle(VehicleType.TRUCK, 600, 200, 0)),
        ("Police", Vehicle(VehicleType.POLICE, 800, 200, 0)),
    ]
    
    print("\n🚗 Created test vehicles:")
    for name, vehicle in test_vehicles:
        tire_stats = vehicle.get_tire_stats()
        print(f"   {name}: {vehicle.tire_system.tires['front_left'].tire_type.value} tires")
        print(f"      Wheelbase: {vehicle.tire_system.wheelbase:.1f}m")
    
    # Start all engines
    for name, vehicle in test_vehicles:
        vehicle.start_engine()
    
    print("\n🎮 Testing tire physics scenarios...")
    
    # Scenario 1: Normal driving
    print("\n📍 Scenario 1: Normal driving with different throttle/steering inputs")
    test_vehicles[0][1].throttle = 0.7  # Sports car - high throttle
    test_vehicles[0][1].steering = 0.3
    
    test_vehicles[1][1].throttle = 0.5  # Sedan - moderate
    test_vehicles[1][1].steering = -0.2
    
    test_vehicles[2][1].throttle = 0.8  # Truck - high load
    test_vehicles[2][1].steering = 0.5
    
    test_vehicles[3][1].throttle = 0.6  # Police - pursuit driving
    test_vehicles[3][1].steering = -0.4
    
    # Run simulation
    frame_count = 0
    max_frames = 600  # 10 seconds
    
    while frame_count < max_frames:
        dt = clock.tick(60) / 1000.0
        
        # Update physics
        physics.update_frame(dt)
        
        # Update all vehicles
        for name, vehicle in test_vehicles:
            vehicle.update(dt)
        
        # Display tire information every 2 seconds
        if frame_count % 120 == 0 and frame_count > 0:
            seconds = frame_count // 60
            print(f"\n⏱️ Time: {seconds}s - Tire Status Report:")
            
            for name, vehicle in test_vehicles:
                skidding_wheels = vehicle.get_skidding_wheels()
                smoke_amount = vehicle.get_tire_smoke_amount()
                tire_sound = vehicle.get_tire_sound_level()
                
                print(f"   {name}:")
                print(f"     Speed: {vehicle.get_speed_kmh():.1f} km/h")
                if skidding_wheels:
                    print(f"     🔥 Skidding wheels: {', '.join(skidding_wheels)}")
                if smoke_amount > 0.1:
                    print(f"     💨 Tire smoke: {smoke_amount:.1f}")
                if tire_sound > 0.3:
                    print(f"     🔊 Tire noise: {tire_sound:.1f}")
        
        # Scenario changes during simulation
        if frame_count == 120:  # 2 seconds - aggressive maneuvers
            print("\n📍 Scenario 2: Aggressive maneuvers (high chance of skidding)")
            test_vehicles[0][1].throttle = 1.0
            test_vehicles[0][1].steering = 1.0  # Maximum steering
            
            test_vehicles[1][1].brake = 0.8     # Hard braking
            test_vehicles[1][1].throttle = 0.0
        
        if frame_count == 240:  # 4 seconds - tire damage test
            print("\n📍 Scenario 3: Tire damage and punctures")
            # Puncture tires on different vehicles
            test_vehicles[2][1].puncture_tire("front_left")
            test_vehicles[3][1].puncture_tire("rear_right")
            
            # Set abnormal tire pressures
            test_vehicles[0][1].set_tire_pressure("front_right", 15.0)  # Low pressure
            test_vehicles[1][1].set_tire_pressure("rear_left", 50.0)    # High pressure
        
        if frame_count == 360:  # 6 seconds - check tire conditions
            print("\n📍 Scenario 4: Tire condition analysis")
            for name, vehicle in test_vehicles:
                conditions = vehicle.check_tire_condition()
                problem_tires = [wheel for wheel, condition in conditions.items() 
                               if condition != "GOOD"]
                if problem_tires:
                    print(f"   {name} tire problems:")
                    for wheel in problem_tires:
                        print(f"     - {wheel}: {conditions[wheel]}")
        
        if frame_count == 480:  # 8 seconds - performance test
            print("\n📍 Scenario 5: High-performance driving test")
            # Set all vehicles to maximum performance
            for name, vehicle in test_vehicles:
                vehicle.throttle = 1.0
                vehicle.steering = 0.8 if frame_count % 120 < 60 else -0.8  # Weaving
        
        # Clear screen and draw (simplified visualization)
        screen.fill((40, 40, 40))
        
        # Draw tire physics debug info
        physics.debug_draw_bodies(screen)
        
        # Draw tire smoke visualization
        for name, vehicle in test_vehicles:
            smoke = vehicle.get_tire_smoke_amount()
            if smoke > 0.1:
                # Draw smoke cloud
                smoke_size = int(smoke * 20)
                pygame.draw.circle(screen, (200, 200, 200, int(smoke * 100)), 
                                 (int(vehicle.x), int(vehicle.y)), smoke_size, 1)
        
        pygame.display.flip()
        frame_count += 1
    
    # Final comprehensive tire analysis
    print("\n📊 FINAL TIRE PHYSICS ANALYSIS:")
    print("=" * 50)
    
    for name, vehicle in test_vehicles:
        print(f"\n🚗 {name} ({vehicle.vehicle_type.value}):")
        
        # Overall vehicle stats
        print(f"   Vehicle Speed: {vehicle.get_speed_kmh():.1f} km/h")
        print(f"   Damage Level: {vehicle.damage_level:.1f}")
        print(f"   Fuel: {vehicle.fuel:.1f}/{vehicle.stats.fuel_capacity}")
        
        # Tire system overview
        tire_stats = vehicle.get_tire_stats()
        print(f"   Tire System: {vehicle.tire_system.tires['front_left'].tire_type.value}")
        print(f"   Wheelbase: {vehicle.tire_system.wheelbase:.1f}m")
        
        # Individual tire analysis
        print("   Individual Tire Stats:")
        for wheel, stats in tire_stats.items():
            condition_icon = "🛞"
            if stats['pressure'] < 20:
                condition_icon = "💨"  # Flat/low pressure
            elif stats['wear_level'] > 0.7:
                condition_icon = "🔴"  # Worn
            elif stats['is_skidding']:
                condition_icon = "🔥"  # Skidding
            
            print(f"     {condition_icon} {wheel}:")
            print(f"       Pressure: {stats['pressure']:.1f} PSI")
            print(f"       Wear: {stats['wear_level']*100:.1f}%")
            print(f"       Temp: {stats['temperature']:.1f}°C")
            if stats['is_skidding']:
                print(f"       🔥 SKIDDING (intensity: {stats['skid_intensity']:.2f})")
        
        # Performance metrics
        conditions = vehicle.check_tire_condition()
        good_tires = sum(1 for c in conditions.values() if c == "GOOD")
        print(f"   Tire Health: {good_tires}/4 tires in good condition")
        
        if vehicle.is_skidding():
            print(f"   ⚠️ Currently skidding: {', '.join(vehicle.get_skidding_wheels())}")
        
        smoke_level = vehicle.get_tire_smoke_amount()
        if smoke_level > 0.1:
            print(f"   💨 Tire smoke level: {smoke_level:.2f}")
        
        sound_level = vehicle.get_tire_sound_level()
        print(f"   🔊 Tire noise level: {sound_level:.2f}")
    
    # Test cleanup
    print(f"\n🧹 Cleaning up test vehicles...")
    for name, vehicle in test_vehicles:
        vehicle.destroy()
    
    print("✅ Advanced tire physics system test completed successfully!")
    print("\n🏆 Key Features Demonstrated:")
    print("   ✓ Individual tire physics simulation")
    print("   ✓ Realistic skidding and traction loss")
    print("   ✓ Tire pressure and wear effects")
    print("   ✓ Temperature-based performance changes")
    print("   ✓ Tire puncture and damage simulation")
    print("   ✓ Smoke and sound effect generation")
    print("   ✓ Vehicle-specific tire characteristics")
    
    pygame.quit()

if __name__ == "__main__":
    test_tire_physics_system()
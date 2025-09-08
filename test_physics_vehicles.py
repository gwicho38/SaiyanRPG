#!/usr/bin/env python3
"""Test the physics-integrated vehicle system."""

import pygame
from saiyanquest.physics_manager import initialize_physics
from saiyanquest.vehicle_system import Vehicle, VehicleType

def test_physics_vehicle_integration():
    """Test vehicle system with physics integration"""
    print("🚗 Testing Physics-Integrated Vehicle System...")
    
    # Initialize pygame and physics
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Physics Vehicle Test")
    clock = pygame.time.Clock()
    
    # Initialize physics system
    physics = initialize_physics()
    print("✓ Physics system initialized")
    
    # Create test vehicles
    sedan = Vehicle(VehicleType.SEDAN, 400, 300, 0)
    sports_car = Vehicle(VehicleType.SPORTS_CAR, 200, 200, 45)
    truck = Vehicle(VehicleType.TRUCK, 600, 400, 90)
    
    print("✓ Created test vehicles:")
    print(f"   Sedan at ({sedan.x:.1f}, {sedan.y:.1f})")
    print(f"   Sports car at ({sports_car.x:.1f}, {sports_car.y:.1f})")
    print(f"   Truck at ({truck.x:.1f}, {truck.y:.1f})")
    
    # Test vehicle properties
    print(f"\n📊 Vehicle Properties:")
    print(f"   Sedan speed: {sedan.speed:.1f} px/s, angle: {sedan.angle:.1f}°")
    print(f"   Sports car damage: {sports_car.damage_level:.1f}, wrecked: {sports_car.is_wrecked}")
    print(f"   Truck passengers: {len(truck.passengers)}/{truck.max_passengers}")
    
    # Start engines
    sedan.start_engine()
    sports_car.start_engine()
    truck.start_engine()
    print("✓ All engines started")
    
    # Test driving controls
    sedan.throttle = 0.5
    sedan.steering = 0.3
    
    sports_car.throttle = 0.8
    sports_car.steering = -0.5
    
    truck.throttle = 0.3
    truck.brake = 0.2
    
    print("✓ Applied driving controls")
    
    # Simulate for a few seconds
    print("\n🎮 Running vehicle simulation...")
    
    running = True
    frame_count = 0
    max_frames = 300  # 5 seconds at 60fps
    
    while running and frame_count < max_frames:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update physics
        physics.update_frame(dt)
        
        # Update vehicles
        sedan.update(dt)
        sports_car.update(dt)
        truck.update(dt)
        
        # Clear screen
        screen.fill((30, 30, 30))
        
        # Debug draw physics bodies
        physics.debug_draw_bodies(screen, camera_offset=(0, 0))
        
        # Display vehicle info
        if frame_count % 60 == 0:  # Every second
            print(f"   Frame {frame_count//60}s:")
            print(f"     Sedan: pos=({sedan.x:.0f}, {sedan.y:.0f}), speed={sedan.get_speed_kmh():.1f} km/h")
            print(f"     Sports: pos=({sports_car.x:.0f}, {sports_car.y:.0f}), speed={sports_car.get_speed_kmh():.1f} km/h")
            print(f"     Truck: pos=({truck.x:.0f}, {truck.y:.0f}), speed={truck.get_speed_kmh():.1f} km/h")
        
        # Test collision at 2 seconds
        if frame_count == 120:
            print("💥 Testing collision...")
            # Move sports car toward sedan
            sports_car.physics_body.set_position(sedan.x/16 - 5, sedan.y/16)
            sports_car.physics_body.set_velocity((10, 0))  # High speed collision
        
        # Test damage at 3 seconds
        if frame_count == 180:
            print("🔧 Testing damage system...")
            sedan.take_damage(0.5)  # 50% damage
            truck.take_damage(0.9)  # 90% damage (should catch fire)
        
        # Test passenger system at 4 seconds
        if frame_count == 240:
            print("👤 Testing passenger system...")
            sedan.add_passenger("Test Driver", "driver")
            sports_car.add_passenger("Test Passenger", "passenger")
            truck.add_passenger("Truck Driver", "driver")
            truck.add_passenger("Passenger 1", "rear_left")
        
        pygame.display.flip()
        frame_count += 1
    
    # Final stats
    print(f"\n📊 Final Vehicle Stats:")
    
    vehicles = [("Sedan", sedan), ("Sports Car", sports_car), ("Truck", truck)]
    for name, vehicle in vehicles:
        print(f"   {name}:")
        print(f"     Position: ({vehicle.x:.1f}, {vehicle.y:.1f})")
        print(f"     Speed: {vehicle.get_speed_kmh():.1f} km/h")
        print(f"     Damage: {vehicle.damage_level:.1f}")
        print(f"     Fuel: {vehicle.fuel:.1f}/{vehicle.stats.fuel_capacity}")
        print(f"     Engine: {'ON' if vehicle.engine_on else 'OFF'}")
        print(f"     Status: {'WRECKED' if vehicle.is_wrecked else 'BURNING' if vehicle.is_burning else 'OK'}")
        print(f"     Passengers: {len(vehicle.passengers)}")
        
        # Test emergency lights
        if vehicle.vehicle_type in [VehicleType.POLICE, VehicleType.AMBULANCE, VehicleType.FIRE_TRUCK]:
            vehicle.toggle_emergency_lights()
    
    # Test cleanup
    print("\n🧹 Testing cleanup...")
    sedan.destroy()
    sports_car.destroy()
    truck.destroy()
    
    print("✅ Physics-integrated vehicle system test completed successfully!")
    pygame.quit()

if __name__ == "__main__":
    test_physics_vehicle_integration()
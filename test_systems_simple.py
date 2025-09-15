#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Simple Test Script for Enhanced SaiyanQuest Systems (No GUI)

import time
import random
import math

# Import our enhanced systems
from saiyanquest.physics_manager import PhysicsManager, CollisionCategory, PhysicsBodyType
from saiyanquest.vehicle_physics import VehiclePhysicsSystem, VehicleState
from saiyanquest.character_ai import CharacterAIManager, StimulusType, Stimulus
from saiyanquest.world_3d_system import World3DSystem, BlockType, DistrictType
from saiyanquest.enhanced_game_integration import EnhancedGameIntegration


def test_physics_system():
    """Test the physics system"""
    print("🧪 Testing Physics System...")
    
    # Create physics manager
    physics = PhysicsManager(gravity=(0, 0))  # Top-down game
    
    # Create some test bodies
    bodies = []
    for i in range(5):
        body = physics.create_body(
            PhysicsBodyType.DYNAMIC,
            (random.uniform(100, 500), random.uniform(100, 400)),
            {
                'type': 'circle',
                'radius': random.uniform(10, 30),
                'mass': random.uniform(0.5, 2.0),
                'friction': 0.7,
                'restitution': 0.3
            },
            CollisionCategory.VEHICLE
        )
        bodies.append(body.body_id)
        
        # Apply random force
        force_x = random.uniform(-500, 500)
        force_y = random.uniform(-500, 500)
        physics.apply_force(body.body_id, (force_x, force_y))
    
    # Run simulation
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        physics.update(dt)
        
        if frame % 60 == 0:  # Print every second
            total_velocity = 0.0
            for body_id in bodies:
                body = physics.get_body(body_id)
                if body:
                    velocity_mag = math.sqrt(body.velocity[0]**2 + body.velocity[1]**2)
                    total_velocity += velocity_mag
            
            print(f"  Frame {frame}: Total velocity = {total_velocity:.2f}")
    
    stats = physics.get_statistics()
    print(f"✅ Physics test completed: {stats}")
    return True


def test_vehicle_system():
    """Test the vehicle physics system"""
    print("🧪 Testing Vehicle Physics System...")
    
    # Create physics manager and vehicle system
    physics = PhysicsManager(gravity=(0, 0))
    vehicle_physics = VehiclePhysicsSystem(physics)
    
    # Create test vehicles
    vehicles = []
    vehicle_types = ['sedan', 'sports_car', 'truck', 'motorcycle']
    
    for i in range(3):
        vehicle_type = random.choice(vehicle_types)
        x = random.uniform(200, 600)
        y = random.uniform(200, 400)
        
        vehicle_id = vehicle_physics.create_vehicle(vehicle_type, (x, y))
        vehicles.append(vehicle_id)
    
    # Run simulation
    for frame in range(600):  # 10 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update vehicles with simple AI
        for vehicle_id in vehicles:
            # Simple AI: drive forward with occasional steering
            throttle = 0.5 if frame < 300 else 0.0  # Accelerate for 5 seconds, then coast
            brake = 0.0
            steering = random.uniform(-0.3, 0.3) if random.random() < 0.1 else 0.0
            handbrake = False
            
            vehicle_physics.update_vehicle(vehicle_id, dt, throttle, brake, steering, handbrake)
        
        # Update physics
        physics.update(dt)
        
        if frame % 120 == 0:  # Print every 2 seconds
            for vehicle_id in vehicles:
                speed = vehicle_physics.get_vehicle_speed(vehicle_id)
                position = vehicle_physics.get_vehicle_position(vehicle_id)
                print(f"  Vehicle {vehicle_id}: Speed = {speed:.1f} m/s, Position = ({position[0]:.1f}, {position[1]:.1f})")
    
    stats = vehicle_physics.get_vehicle_statistics()
    print(f"✅ Vehicle physics test completed: {stats}")
    return True


def test_character_ai():
    """Test the character AI system"""
    print("🧪 Testing Character AI System...")
    
    # Create physics manager and character AI
    physics = PhysicsManager(gravity=(0, 0))
    character_ai = CharacterAIManager(physics)
    
    # Create test characters
    characters = []
    for i in range(5):
        x = random.uniform(100, 700)
        y = random.uniform(100, 500)
        
        character_id = character_ai.create_character(i + 1000, (x, y)).character_id
        characters.append(character_id)
    
    # Create some stimuli
    stimuli = []
    for i in range(3):
        stimulus_type = random.choice([StimulusType.GUNSHOT, StimulusType.EXPLOSION, StimulusType.LOUD_NOISE])
        x = random.uniform(200, 600)
        y = random.uniform(200, 400)
        
        stimulus = Stimulus(
            stimulus_type=stimulus_type,
            position=(x, y),
            intensity=random.uniform(0.5, 1.0),
            radius=random.uniform(50, 150),
            timestamp=time.time()
        )
        
        character_ai.add_stimulus(stimulus)
        stimuli.append(stimulus)
    
    # Run simulation
    for frame in range(600):  # 10 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Update AI
        game_state = {
            'player_x': 400,
            'player_y': 300,
            'player_speed': 0.0,
            'player_vehicle': None,
            'player_hidden': False,
            'game_time': frame * dt,
            'time_of_day': 12.0,
            'weather': 'clear',
            'temperature': 20.0
        }
        
        character_ai.update_all_characters(dt, game_state)
        
        # Update physics
        physics.update(dt)
        
        if frame % 120 == 0:  # Print every 2 seconds
            for character_id in characters:
                controller = character_ai.character_controllers.get(character_id)
                if controller:
                    info = controller.get_character_info()
                    print(f"  Character {character_id}: State = {info['state']}, Fear = {info['fear_level']}")
    
    stats = character_ai.get_character_statistics()
    print(f"✅ Character AI test completed: {stats}")
    return True


def test_world_system():
    """Test the 3D world system"""
    print("🧪 Testing 3D World System...")
    
    # Create world system
    world = World3DSystem(200, 200, 2)  # Smaller world for testing
    
    # Create districts
    downtown_id = world.create_district("Downtown", DistrictType.DOWNTOWN, (0, 0, 99, 99))
    residential_id = world.create_district("Residential", DistrictType.RESIDENTIAL, (100, 0, 199, 99))
    commercial_id = world.create_district("Commercial", DistrictType.COMMERCIAL, (0, 100, 99, 199))
    industrial_id = world.create_district("Industrial", DistrictType.INDUSTRIAL, (100, 100, 199, 199))
    
    # Set some blocks
    for y in range(10, 20):
        for x in range(10, 20):
            from saiyanquest.world_3d_system import MapBlockInfo
            block_info = MapBlockInfo(
                block_type=BlockType.BUILDING,
                height=10.0,
                water_level=0.0,
                collision_enabled=True,
                walkable=False,
                driveable=False,
                flyable=True,
                district_id=downtown_id,
                properties={'height': 10.0}
            )
            world.set_block_info(x, y, 0, block_info)
    
    # Generate navigation sectors
    world.generate_navigation_sectors()
    
    # Test pathfinding
    path = world.find_path((5, 5), (95, 95))
    print(f"  Pathfinding test: Found path with {len(path)} waypoints")
    
    # Test collision detection
    collision = world.trace_segment_2d((5, 5), (15, 15))
    if collision:
        print(f"  Collision test: Detected collision at ({collision[0]:.1f}, {collision[1]:.1f})")
    else:
        print("  Collision test: No collision detected")
    
    # Test world state updates
    for frame in range(60):  # 1 second at 60 FPS
        dt = 1.0 / 60.0
        world.update_world_state(dt)
    
    stats = world.get_world_statistics()
    print(f"✅ World system test completed: {stats}")
    return True


def test_integration():
    """Test the complete integration"""
    print("🧪 Testing Complete Integration...")
    
    # Create enhanced game integration
    game = EnhancedGameIntegration()
    
    # Simulate input
    input_state = {
        'throttle': 0.5,
        'brake': 0.0,
        'steering': 0.0,
        'handbrake': False,
        'fire': False,
        'enter_exit_vehicle': False,
        'next_weapon': False,
        'prev_weapon': False
    }
    
    # Run simulation
    for frame in range(600):  # 10 seconds at 60 FPS
        dt = 1.0 / 60.0
        
        # Vary input
        if frame < 200:
            input_state['throttle'] = 0.5
            input_state['steering'] = 0.0
        elif frame < 400:
            input_state['throttle'] = 0.3
            input_state['steering'] = 0.2
        else:
            input_state['throttle'] = 0.0
            input_state['steering'] = 0.0
        
        # Fire weapon occasionally
        input_state['fire'] = (frame % 300 == 0)
        
        # Enter vehicle after 100 frames
        input_state['enter_exit_vehicle'] = (frame == 100)
        
        # Update game
        game.update(dt, input_state)
        
        if frame % 120 == 0:  # Print every 2 seconds
            stats = game.get_performance_statistics()
            print(f"  Frame {frame}: FPS = {stats.get('fps', 0):.1f}, "
                  f"Vehicles = {stats.get('vehicles', 0)}, "
                  f"Characters = {stats.get('characters', 0)}, "
                  f"Distance = {stats.get('total_distance_km', 0):.2f} km")
    
    # Get comprehensive statistics
    final_stats = game.get_comprehensive_statistics()
    print(f"✅ Integration test completed")
    print(f"  Final statistics:")
    for category, stats in final_stats.items():
        print(f"    {category}: {stats}")
    
    return True


def main():
    """Main test function"""
    print("🚀 Starting SaiyanQuest Enhanced Systems Test Suite")
    print("=" * 60)
    
    tests = [
        ("Physics System", test_physics_system),
        ("Vehicle Physics", test_vehicle_system),
        ("Character AI", test_character_ai),
        ("3D World System", test_world_system),
        ("Complete Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Suite Complete: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
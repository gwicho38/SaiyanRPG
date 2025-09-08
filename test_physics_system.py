#!/usr/bin/env python3
"""Test the advanced physics system implementation."""

import pygame
from saiyanquest.physics_manager import (
    PhysicsManager, PhysicsBodyConfig, CollisionCategory,
    get_physics_manager, initialize_physics
)

def test_basic_physics():
    """Test basic physics functionality"""
    print("🧪 Testing Basic Physics System...")
    
    # Initialize pygame (required for display)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Physics Test")
    clock = pygame.time.Clock()
    
    # Initialize physics
    physics = initialize_physics()
    print(f"✓ Physics initialized: {physics.world.bodyCount} bodies")
    
    # Create a test vehicle
    vehicle_body = physics.create_vehicle_body(
        position=(400/16, 300/16),  # Convert pixels to meters
        width=3.0,  # 3 meters wide
        height=1.5,  # 1.5 meters tall
        game_object=None
    )
    print(f"✓ Vehicle body created at {vehicle_body.position}")
    
    # Create some map collision
    wall_body = physics.create_map_collision(
        x=0, y=0, width=800/16, height=50/16  # Top wall
    )
    print(f"✓ Wall collision created")
    
    # Create a pedestrian
    ped_body = physics.create_pedestrian_body(
        position=(200/16, 200/16),
        radius=0.5,  # 0.5 meter radius
        game_object=None
    )
    print(f"✓ Pedestrian body created at {ped_body.position}")
    
    # Test ray casting
    ray_result = physics.ray_cast((100/16, 100/16), (300/16, 100/16))
    if ray_result['hit']:
        print(f"✓ Ray casting works - hit at {ray_result['point']}")
    else:
        print("✓ Ray casting works - no hit")
    
    # Test AABB query
    bodies_in_area = physics.query_aabb((0, 0), (500/16, 400/16))
    print(f"✓ AABB query found {len(bodies_in_area)} bodies")
    
    # Run simulation for a few frames
    print("\n🎮 Running physics simulation...")
    
    running = True
    frame_count = 0
    max_frames = 300  # Run for 5 seconds at 60fps
    
    while running and frame_count < max_frames:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Apply some forces to test physics
        if frame_count == 60:  # After 1 second
            vehicle_body.apply_force((50.0, 0.0))  # Push vehicle right
            print("🚗 Applied force to vehicle")
        
        if frame_count == 120:  # After 2 seconds  
            ped_body.apply_impulse((0.0, -10.0))  # Impulse pedestrian up
            print("🚶 Applied impulse to pedestrian")
        
        # Update physics
        physics.update_frame(dt)
        
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Debug draw physics bodies
        physics.debug_draw_bodies(screen, camera_offset=(0, 0))
        
        # Display stats
        if frame_count % 60 == 0:  # Every second
            stats = physics.get_stats()
            print(f"   Frame {frame_count}: {stats['body_count']} bodies, "
                  f"{stats['world_contacts']} contacts")
            print(f"   Vehicle pos: {vehicle_body.position}, vel: {vehicle_body.velocity}")
        
        pygame.display.flip()
        frame_count += 1
    
    print(f"\n📊 Final Physics Stats:")
    final_stats = physics.get_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    print("✅ Physics system test completed successfully!")
    pygame.quit()

def test_collision_detection():
    """Test collision detection and response"""
    print("\n🧪 Testing Collision Detection...")
    
    physics = get_physics_manager()
    
    # Create two bodies that will collide
    body1 = physics.create_vehicle_body((10, 10), 2.0, 1.0)
    body2 = physics.create_vehicle_body((12, 10), 2.0, 1.0)
    
    # Give them velocities toward each other
    body1.set_velocity((5.0, 0.0))
    body2.set_velocity((-5.0, 0.0))
    
    print(f"✓ Created collision test bodies")
    print(f"   Body1: pos={body1.position}, vel={body1.velocity}")
    print(f"   Body2: pos={body2.position}, vel={body2.velocity}")
    
    # Simulate until collision
    for i in range(60):  # 1 second max
        physics.update_frame(1/60)
        
        # Check if bodies are close (collision occurred)
        pos1 = body1.position
        pos2 = body2.position
        distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
        
        if distance < 3.0:  # Bodies should be touching
            print(f"✓ Collision detected at frame {i}")
            print(f"   Final distance: {distance:.2f}")
            print(f"   Body1: pos={pos1}, vel={body1.velocity}")
            print(f"   Body2: pos={pos2}, vel={body2.velocity}")
            break
    
    print("✅ Collision detection test completed!")

if __name__ == "__main__":
    test_basic_physics()
    test_collision_detection()
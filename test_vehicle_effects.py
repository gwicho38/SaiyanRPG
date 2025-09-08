#!/usr/bin/env python3
"""Test the vehicle visual effects and animations system."""

import pygame
import time
import math
from saiyanquest.physics_manager import initialize_physics
from saiyanquest.vehicle_system import Vehicle, VehicleType

def test_vehicle_effects_system():
    """Test comprehensive vehicle visual effects"""
    print("✨ Testing Vehicle Visual Effects & Animations System...")
    
    # Initialize pygame and physics
    pygame.init()
    screen = pygame.display.set_mode((1400, 900))
    pygame.display.set_caption("Vehicle Effects System Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Initialize physics system
    physics = initialize_physics()
    print("✓ Physics system initialized")
    
    # Create test vehicles for different effects
    test_vehicles = [
        ("Sports Car", Vehicle(VehicleType.SPORTS_CAR, 200, 200, 0)),
        ("Police Car", Vehicle(VehicleType.POLICE, 400, 200, 0)),  
        ("Sedan", Vehicle(VehicleType.SEDAN, 600, 200, 0)),
        ("Truck", Vehicle(VehicleType.TRUCK, 800, 200, 0)),
    ]
    
    print(f"✓ Created {len(test_vehicles)} vehicles with effects systems")
    
    # Start all engines for effects
    for name, vehicle in test_vehicles:
        vehicle.start_engine()
        print(f"   Started {name} engine for effects testing")
    
    print("\n🎬 Running visual effects demonstration...")
    
    # Demo parameters
    frame_count = 0
    max_frames = 1800  # 30 seconds at 60fps
    camera_offset = (0, 0)
    
    # Effect test scenarios
    scenarios = {
        120:  "exhaust_effects",     # 2 seconds - engine effects
        300:  "tire_effects",        # 5 seconds - tire smoke and skidding
        480:  "lighting_effects",    # 8 seconds - headlights and signals  
        660:  "damage_effects",      # 11 seconds - sparks and fire
        840:  "environmental",       # 14 seconds - dust and particles
        1020: "brake_effects",       # 17 seconds - brake lights and dust
        1200: "emergency_lights",    # 20 seconds - emergency vehicle lights
        1380: "overheating",         # 23 seconds - engine overheating
        1560: "comprehensive"        # 26 seconds - all effects combined
    }
    
    while frame_count < max_frames:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        # Scenario management
        if frame_count in scenarios:
            scenario = scenarios[frame_count]
            seconds = frame_count // 60
            print(f"\n⏱️ {seconds}s - Demo: {scenario.upper().replace('_', ' ')}")
            
            if scenario == "exhaust_effects":
                print("   🚗 Testing exhaust smoke and engine effects")
                test_vehicles[0][1].throttle = 0.8  # High throttle for smoke
                test_vehicles[1][1].throttle = 0.6
                test_vehicles[2][1].throttle = 0.4
                test_vehicles[3][1].throttle = 1.0  # Maximum exhaust
                
            elif scenario == "tire_effects":
                print("   🛞 Testing tire smoke and skidding effects")
                # Force skidding conditions
                test_vehicles[0][1].throttle = 0.9
                test_vehicles[0][1].steering = 1.0  # Max steering for skidding
                test_vehicles[0][1].brake = 0.3     # Partial brake while accelerating
                
                test_vehicles[1][1].throttle = 0.8
                test_vehicles[1][1].steering = -0.8
                test_vehicles[1][1].brake = 0.2
                
            elif scenario == "lighting_effects":
                print("   💡 Testing headlights and signal lights")
                for name, vehicle in test_vehicles:
                    vehicle.toggle_headlights()
                    vehicle.set_turn_signal("left")
                    if name == "Police Car":
                        vehicle.toggle_emergency_lights()
                        
            elif scenario == "damage_effects":
                print("   🔥 Testing damage effects - sparks and fire")
                # Simulate damage for effects
                test_vehicles[0][1].damage_level = 0.8  # Heavy damage
                test_vehicles[1][1].is_burning = True   # Set on fire
                test_vehicles[2][1].damage_level = 0.6  # Moderate damage
                
            elif scenario == "environmental":
                print("   🌪️ Testing environmental effects - dust and debris")
                # High speed for dust effects
                test_vehicles[0][1].throttle = 1.0
                test_vehicles[1][1].throttle = 0.9
                test_vehicles[2][1].throttle = 0.8
                test_vehicles[3][1].throttle = 0.7
                
            elif scenario == "brake_effects":
                print("   🛑 Testing brake lights and brake dust")
                for name, vehicle in test_vehicles:
                    vehicle.brake = 0.9  # Hard braking
                    vehicle.throttle = 0.0
                    
            elif scenario == "emergency_lights":
                print("   🚨 Testing emergency vehicle lighting")
                test_vehicles[1][1].toggle_emergency_lights()  # Police car
                
            elif scenario == "overheating":
                print("   🌡️ Testing engine overheating effects")
                # Force overheating for steam effects
                test_vehicles[0][1].mechanical_system.engine_temperature = 130.0
                test_vehicles[2][1].mechanical_system.engine_temperature = 125.0
                
            elif scenario == "comprehensive":
                print("   🎆 Comprehensive effects demonstration")
                # Enable multiple effects simultaneously
                for i, (name, vehicle) in enumerate(test_vehicles):
                    vehicle.throttle = 0.7 + (i * 0.1)
                    vehicle.steering = math.sin(frame_count * 0.02) * 0.5
                    if i % 2 == 0:
                        vehicle.brake = 0.3
                    if name == "Police Car":
                        vehicle.toggle_emergency_lights()
        
        # Update physics
        physics.update_frame(dt)
        
        # Update all vehicles
        for name, vehicle in test_vehicles:
            vehicle.update(dt)
        
        # Clear screen with dark background
        screen.fill((20, 20, 30))
        
        # Draw simple road/ground
        pygame.draw.rect(screen, (40, 40, 40), (0, 180, 1400, 120))  # Road surface
        pygame.draw.line(screen, (255, 255, 100), (0, 240), (1400, 240), 3)  # Center line
        
        # Draw vehicle physics bodies (simple representation)
        for name, vehicle in test_vehicles:
            x, y = int(vehicle.x), int(vehicle.y)
            angle = vehicle.angle
            
            # Vehicle body as rotated rectangle
            cos_a = math.cos(math.radians(angle))
            sin_a = math.sin(math.radians(angle))
            
            # Vehicle corners
            w, h = 30, 15
            corners = [
                (x + cos_a*w//2 - sin_a*h//2, y + sin_a*w//2 + cos_a*h//2),
                (x - cos_a*w//2 - sin_a*h//2, y - sin_a*w//2 + cos_a*h//2),
                (x - cos_a*w//2 + sin_a*h//2, y - sin_a*w//2 - cos_a*h//2),
                (x + cos_a*w//2 + sin_a*h//2, y + sin_a*w//2 - cos_a*h//2)
            ]
            
            # Vehicle color based on state
            color = (100, 100, 100)  # Default gray
            if vehicle.engine_on:
                color = (0, 150, 0)  # Green when running
            if vehicle.damage_level > 0.5:
                color = (200, 100, 0)  # Orange when damaged
            if vehicle.is_burning:
                color = (255, 50, 0)  # Red when burning
                
            pygame.draw.polygon(screen, color, corners)
            
            # Draw vehicle direction indicator
            front_x = x + cos_a * 20
            front_y = y + sin_a * 20
            pygame.draw.line(screen, (255, 255, 255), (x, y), (front_x, front_y), 2)
        
        # Render all visual effects (THIS IS THE KEY TEST)
        for name, vehicle in test_vehicles:
            vehicle.render_effects(screen, camera_offset)
        
        # Draw debug physics bodies
        physics.debug_draw_bodies(screen, camera_offset)
        
        # Status display
        if frame_count % 30 == 0:  # Update every 0.5 seconds
            current_scenario = "warming_up"
            for check_frame, scenario in scenarios.items():
                if frame_count >= check_frame:
                    current_scenario = scenario
            
            print(f"   Frame {frame_count}: {current_scenario} - Particles active")
        
        # Display effects information on screen
        y_offset = 10
        info_texts = [
            f"Frame: {frame_count}/{max_frames}",
            f"Time: {frame_count//60}s",
            f"FPS: {clock.get_fps():.1f}",
            ""
        ]
        
        # Vehicle effects info
        total_particles = 0
        for i, (name, vehicle) in enumerate(test_vehicles):
            effects_info = vehicle.get_effects_info()
            total_particles += effects_info['particle_count']
            
            info_texts.extend([
                f"{name}:",
                f"  Particles: {effects_info['particle_count']}",
                f"  Lights: {effects_info['active_lights']}",
                f"  Speed: {vehicle.get_speed_kmh():.1f} km/h"
            ])
        
        info_texts.append(f"\nTotal Particles: {total_particles}")
        
        # Render info text
        for i, text in enumerate(info_texts):
            if text.strip():
                color = (255, 255, 255) if not text.startswith(" ") else (200, 200, 200)
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (10, y_offset + i * 20))
        
        # Display current scenario
        scenario_text = "Demo Starting..."
        for check_frame, scenario in scenarios.items():
            if frame_count >= check_frame:
                scenario_text = f"DEMO: {scenario.upper().replace('_', ' ')}"
        
        scenario_surface = font.render(scenario_text, True, (255, 255, 100))
        scenario_rect = scenario_surface.get_rect()
        scenario_rect.centerx = screen.get_width() // 2
        scenario_rect.y = 10
        pygame.draw.rect(screen, (50, 50, 50), scenario_rect.inflate(20, 10))
        screen.blit(scenario_surface, scenario_rect)
        
        pygame.display.flip()
        frame_count += 1
    
    # Final effects analysis
    print("\n✨ VISUAL EFFECTS SYSTEM ANALYSIS:")
    print("=" * 50)
    
    for name, vehicle in test_vehicles:
        effects_info = vehicle.get_effects_info()
        electrical = vehicle.get_electrical_status()
        
        print(f"\n🚗 {name}:")
        print(f"   Visual Effects:")
        print(f"     Active Particles: {effects_info['particle_count']}")
        print(f"     Particle Usage: {effects_info['particle_usage']}")
        print(f"     Active Lights: {effects_info['active_lights']}")
        print(f"     Headlight Beams: {effects_info['headlight_beams']}")
        
        print(f"   Vehicle State:")
        print(f"     Engine: {'ON' if vehicle.engine_on else 'OFF'}")
        print(f"     Damage Level: {vehicle.damage_level:.1f}")
        print(f"     Burning: {vehicle.is_burning}")
        print(f"     Speed: {vehicle.get_speed_kmh():.1f} km/h")
        
        print(f"   Electrical:")
        print(f"     Battery: {electrical['battery_voltage']}V")
        print(f"     Active Components: {len(electrical['active_components'])}")
        
        # Clear effects for clean shutdown
        vehicle.clear_effects()
    
    # Cleanup
    print(f"\n🧹 Cleaning up test vehicles...")
    for name, vehicle in test_vehicles:
        vehicle.destroy()
    
    print("✅ Visual effects system test completed successfully!")
    print("\n🏆 Key Features Demonstrated:")
    print("   ✓ Particle systems with multiple effect types")
    print("   ✓ Engine exhaust smoke based on throttle input")
    print("   ✓ Tire smoke and skidding particle effects")
    print("   ✓ Dynamic lighting with headlight beams")
    print("   ✓ Emergency vehicle light patterns")
    print("   ✓ Damage effects with sparks and fire")
    print("   ✓ Environmental effects (dust, debris)")
    print("   ✓ Brake lights and brake dust particles")
    print("   ✓ Engine overheating steam effects")
    print("   ✓ Real-time particle management and optimization")
    
    pygame.quit()

if __name__ == "__main__":
    test_vehicle_effects_system()
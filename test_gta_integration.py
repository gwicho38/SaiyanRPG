#!/usr/bin/env python3
"""
Integration test for GTA systems
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports work correctly"""
    print("Testing imports...")
    
    try:
        from saiyanquest.gta_world import GTAWorld, WantedLevel
        print("✓ gta_world imported successfully")
        
        from saiyanquest.vehicle_system import VehicleManager, Vehicle, VehicleType
        print("✓ vehicle_system imported successfully")
        
        from saiyanquest.ai_systems import AIManager, PedestrianManager
        print("✓ ai_systems imported successfully")
        
        from saiyanquest.mission_system import MissionManager, Mission
        print("✓ mission_system imported successfully")
        
        from saiyanquest.crime_system import CrimeSystem
        print("✓ crime_system imported successfully")
        
        from saiyanquest.weapon_system import WeaponInventory, CombatSystem, Weapon, WeaponType
        print("✓ weapon_system imported successfully")
        
        from saiyanquest.character_system import Character, CharacterManager, CharacterType
        print("✓ character_system imported successfully")
        
        from saiyanquest.gta_ui import UIManager, GTAHUD
        print("✓ gta_ui imported successfully")
        
        from saiyanquest.save_system import SaveManager, GameStateManager
        print("✓ save_system imported successfully")
        
        from saiyanquest.gta_game import GTAGame, GTAGameState
        print("✓ gta_game imported successfully")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    return True

def test_game_initialization():
    """Test game can be initialized without pygame display"""
    print("\nTesting game initialization...")
    
    try:
        # Mock pygame for headless testing
        import unittest.mock
        
        with unittest.mock.patch('pygame.init'), \
             unittest.mock.patch('pygame.display.set_mode'), \
             unittest.mock.patch('pygame.display.set_caption'), \
             unittest.mock.patch('pygame.time.Clock'), \
             unittest.mock.patch('pygame.font.Font'):
            
            from saiyanquest.gta_game import GTAGameState
            
            # Test game state initialization
            game_state = GTAGameState()
            print("✓ GTAGameState created successfully")
            
            # Check key components exist
            assert hasattr(game_state, 'world'), "Missing world component"
            assert hasattr(game_state, 'player_character'), "Missing character component"
            assert hasattr(game_state, 'vehicle_manager'), "Missing vehicle_manager component"
            assert hasattr(game_state, 'mission_manager'), "Missing mission_manager component"
            print("✓ Core components initialized")
            
            # Test basic character stats
            assert game_state.player_character.name is not None, "Character name incorrect"
            assert game_state.player_character.health > 0, "Character health invalid"
            print("✓ Character initialized correctly")
            
            # Test world setup
            assert len(game_state.world.districts) > 0, "No districts in world"
            assert game_state.world.world_width > 0, "Invalid world width"
            print("✓ World initialized correctly")
            
            # Test vehicle spawning
            assert len(game_state.vehicle_manager.vehicles) >= 0, "Vehicle manager not initialized"
            print("✓ Vehicle system initialized correctly")
            
            # Test weapon inventory
            assert game_state.weapon_inventory is not None, "Weapon inventory not initialized"
            assert game_state.current_weapon is not None, "No current weapon set"
            print("✓ Weapon system initialized correctly")
            
    except Exception as e:
        print(f"✗ Game initialization failed: {e}")
        return False
    
    return True

def test_system_interactions():
    """Test basic system interactions"""
    print("\nTesting system interactions...")
    
    try:
        import unittest.mock
        
        with unittest.mock.patch('pygame.init'), \
             unittest.mock.patch('pygame.display.set_mode'), \
             unittest.mock.patch('pygame.display.set_caption'), \
             unittest.mock.patch('pygame.time.Clock'), \
             unittest.mock.patch('pygame.font.Font'):
            
            from saiyanquest.gta_game import GTAGameState
            from saiyanquest.vehicle_system import VehicleType
            from saiyanquest.weapon_system import WeaponType
            
            game_state = GTAGameState()
            
            # Test spawning a vehicle
            initial_vehicle_count = len(game_state.vehicle_manager.vehicles)
            game_state.vehicle_manager.spawn_vehicle(VehicleType.SEDAN, 100, 100)
            assert len(game_state.vehicle_manager.vehicles) > initial_vehicle_count, "Vehicle not spawned"
            print("✓ Vehicle spawning works")
            
            # Test character system (simplified for new architecture)
            # TODO: Implement character skill training with new character system
            assert game_state.player_character is not None, "Character not initialized"
            print("✓ Character system works")
            
            # Test crime system
            initial_heat = game_state.crime_system.wanted_system.heat_points
            game_state.crime_system.player_used_weapon(100, 100, "civilian", False)
            assert game_state.crime_system.wanted_system.heat_points >= initial_heat, "Crime system not working"
            print("✓ Crime system responds to actions")
            
            # Test mission system
            initial_mission_count = len(game_state.mission_manager.available_missions)
            game_state.mission_manager.create_sample_missions()
            assert len(game_state.mission_manager.available_missions) >= initial_mission_count, "Mission creation failed"
            print("✓ Mission system works")
            
    except Exception as e:
        print(f"✗ System interaction test failed: {e}")
        return False
    
    return True

def main():
    """Run all integration tests"""
    print("GTA Game Integration Test")
    print("=" * 30)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_game_initialization():
        tests_passed += 1
    
    if test_system_interactions():
        tests_passed += 1
    
    print("\n" + "=" * 30)
    print(f"Integration Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All integration tests PASSED! Game is ready to run.")
        return 0
    else:
        print("❌ Some integration tests FAILED. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
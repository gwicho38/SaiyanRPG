#!/usr/bin/env python3
"""
Basic GTA systems test without pygame
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without pygame dependency"""
    print("Testing basic imports...")
    
    try:
        # Test data classes and enums that don't require pygame
        from saiyanquest.character_system import Character, CharacterManager, CharacterType
        print("✓ character_system core classes imported")
        
        from saiyanquest.vehicle_system import VehicleType, VehicleStats
        print("✓ vehicle_system core classes imported")
        
        from saiyanquest.weapon_system import WeaponType, WeaponCategory
        print("✓ weapon_system core classes imported")
        
        from saiyanquest.mission_system import MissionType, ObjectiveType
        print("✓ mission_system core classes imported")
        
        from saiyanquest.crime_system import Crime, CrimeType
        print("✓ crime_system core classes imported")
        
        from saiyanquest.gta_world import WantedLevel, DistrictType
        print("✓ gta_world core classes imported")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without pygame"""
    print("\nTesting basic functionality...")
    
    try:
        # Test Character creation and stats
        from saiyanquest.character_system import Character, SkillType
        
        character = Character("TestPlayer")
        assert character.name == "TestPlayer"
        assert character.money >= 0
        assert hasattr(character, 'stats')
        assert hasattr(character, 'skills')
        print("✓ Character creation works")
        
        # Test skill training
        initial_pistol = character.skills.pistol
        character.train_skill(SkillType.PISTOL, 1.0)
        assert character.skills.pistol > initial_pistol
        print("✓ Skill training works")
        
        # Test vehicle types and stats
        from saiyanquest.vehicle_system import VehicleType, VehicleStats
        
        sedan_stats = VehicleStats.get_stats(VehicleType.SEDAN)
        assert sedan_stats.max_speed > 0
        assert sedan_stats.acceleration > 0
        print("✓ Vehicle stats system works")
        
        # Test weapon types
        from saiyanquest.weapon_system import WeaponType, WeaponStats
        
        pistol_stats = WeaponStats.get_stats(WeaponType.PISTOL)
        assert pistol_stats.damage > 0
        assert pistol_stats.range > 0
        print("✓ Weapon stats system works")
        
        # Test crime types
        from saiyanquest.crime_system import CrimeType, Crime
        
        crime = Crime(CrimeType.ASSAULT, 100.0, 100.0, 1.0, True)
        assert crime.crime_type == CrimeType.ASSAULT
        assert crime.severity > 0
        print("✓ Crime system works")
        
        # Test mission types
        from saiyanquest.mission_system import MissionType, ObjectiveType
        
        assert len(list(MissionType)) > 0
        assert len(list(ObjectiveType)) > 0
        print("✓ Mission system types work")
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_system_integration():
    """Test basic system integration without pygame"""
    print("\nTesting system integration...")
    
    try:
        from saiyanquest.character_system import Character
        from saiyanquest.weapon_system import WeaponInventory, WeaponType
        from saiyanquest.vehicle_system import VehicleStats, VehicleType
        
        # Create character
        character = Character("IntegrationTest")
        
        # Test weapon inventory
        inventory = WeaponInventory()
        assert inventory.current_weapon is not None
        print("✓ Weapon inventory initialization works")
        
        # Test vehicle stats lookup
        for vehicle_type in [VehicleType.SEDAN, VehicleType.SPORTS_CAR, VehicleType.TRUCK]:
            stats = VehicleStats.get_stats(vehicle_type)
            assert stats.max_speed > 0
        print("✓ Vehicle stats lookup works")
        
        # Test character progression
        initial_level = character.level
        character.add_experience(1000)
        assert character.experience > 0
        print("✓ Character progression works")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run basic tests"""
    print("GTA Game Basic Integration Test")
    print("=" * 35)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_basic_imports():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_system_integration():
        tests_passed += 1
    
    print("\n" + "=" * 35)
    print(f"Basic Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All basic tests PASSED! Core systems are functional.")
        return 0
    else:
        print("❌ Some basic tests FAILED. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
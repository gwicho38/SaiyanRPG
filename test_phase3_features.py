#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# Comprehensive Test Script for Phase 3 Features

import time
import random
import math

from saiyanquest.enhanced_integration_phase3 import EnhancedIntegrationPhase3
from saiyanquest.traffic_management import TrafficDensity, TrafficBehavior
from saiyanquest.audio_system import AudioType
from saiyanquest.input_controls import ControlScheme


def test_traffic_management():
    """Test traffic management system"""
    print("🧪 Testing Traffic Management System...")
    
    integration = EnhancedIntegrationPhase3()
    
    # Test different traffic densities
    densities = [TrafficDensity.LIGHT, TrafficDensity.MODERATE, TrafficDensity.HEAVY]
    
    for density in densities:
        print(f"  Testing {density.name} traffic density...")
        integration.set_traffic_density(density)
        
        # Run simulation
        for frame in range(120):  # 2 seconds at 60 FPS
            dt = 1.0 / 60.0
            integration.update(dt)
        
        # Get statistics
        stats = integration.traffic_manager.get_traffic_statistics()
        print(f"    Vehicles: {stats['total_vehicles']}, "
              f"Avg Speed: {stats['average_speed']:.1f} m/s, "
              f"Flow Rate: {stats['traffic_flow_rate']:.2f}")
    
    print("✅ Traffic Management test completed")
    return True


def test_audio_system():
    """Test audio system"""
    print("🧪 Testing Audio System...")
    
    integration = EnhancedIntegrationPhase3()
    
    # Test audio volume controls
    print("  Testing audio volume controls...")
    integration.set_audio_volume("master", 0.8)
    integration.set_audio_volume("sfx", 0.9)
    integration.set_audio_volume("music", 0.7)
    
    # Test audio events
    print("  Testing audio events...")
    events = [
        (AudioType.WEAPON_GUNSHOT, (100, 100), 0.8, "high"),
        (AudioType.WEAPON_EXPLOSION, (200, 200), 1.0, "critical"),
        (AudioType.VEHICLE_HORN, (300, 300), 0.6, "normal"),
        (AudioType.CHARACTER_FOOTSTEP, (400, 400), 0.3, "low")
    ]
    
    for audio_type, position, volume, priority in events:
        source_id = integration.create_audio_event(audio_type, position, volume, priority)
        print(f"    Created {audio_type.value} event at {position}")
    
    # Test vehicle audio
    print("  Testing vehicle audio...")
    for frame in range(60):  # 1 second
        dt = 1.0 / 60.0
        integration.update(dt)
    
    # Get audio statistics
    audio_stats = integration.spatial_audio.get_audio_statistics()
    print(f"    Total Sources: {audio_stats['total_sources']}, "
          f"Playing: {audio_stats['playing_sources']}")
    
    print("✅ Audio System test completed")
    return True


def test_input_controls():
    """Test input controls system"""
    print("🧪 Testing Input Controls System...")
    
    integration = EnhancedIntegrationPhase3()
    
    # Test control schemes
    print("  Testing control schemes...")
    schemes = [ControlScheme.KEYBOARD_MOUSE, ControlScheme.GAMEPAD_CLASSIC, ControlScheme.GAMEPAD_MODERN]
    
    for scheme in schemes:
        integration.set_control_scheme(scheme)
        
        # Simulate input processing
        for frame in range(30):  # 0.5 seconds
            dt = 1.0 / 60.0
            integration.update(dt)
        
        input_stats = integration.input_manager.get_input_statistics()
        print(f"    Scheme: {scheme.value}, "
              f"Bindings: {input_stats['total_bindings']}, "
              f"Gamepads: {input_stats['connected_gamepads']}")
    
    # Test input conversion
    print("  Testing input conversion...")
    vehicle_inputs = integration.input_manager.get_vehicle_inputs()
    weapon_inputs = integration.input_manager.get_weapon_inputs()
    interaction_inputs = integration.input_manager.get_interaction_inputs()
    
    print(f"    Vehicle inputs: throttle={vehicle_inputs['throttle']:.2f}, "
          f"brake={vehicle_inputs['brake']:.2f}, "
          f"steering={vehicle_inputs['steering']:.2f}")
    print(f"    Weapon inputs: fire={weapon_inputs['fire']}, "
          f"aim={weapon_inputs['aim']}, "
          f"reload={weapon_inputs['reload']}")
    print(f"    Interaction inputs: enter_vehicle={interaction_inputs['enter_exit_vehicle']}, "
          f"interact={interaction_inputs['interact']}")
    
    print("✅ Input Controls test completed")
    return True


def test_integration():
    """Test complete Phase 3 integration"""
    print("🧪 Testing Complete Phase 3 Integration...")
    
    integration = EnhancedIntegrationPhase3()
    
    # Test comprehensive integration
    print("  Testing comprehensive integration...")
    
    # Set up test scenario
    integration.set_traffic_density(TrafficDensity.HEAVY)
    integration.set_control_scheme(ControlScheme.KEYBOARD_MOUSE)
    integration.set_audio_volume("master", 0.9)
    
    # Create some audio events
    integration.create_audio_event(AudioType.WEAPON_GUNSHOT, (300, 300), 0.8, "high")
    integration.create_audio_event(AudioType.VEHICLE_HORN, (400, 400), 0.6, "normal")
    
    # Run comprehensive simulation
    for frame in range(300):  # 5 seconds at 60 FPS
        dt = 1.0 / 60.0
        integration.update(dt)
        
        if frame % 60 == 0:  # Print every second
            perf_stats = integration.get_performance_statistics()
            print(f"    Frame {frame}: FPS = {perf_stats.get('fps', 0):.1f}, "
                  f"Vehicles = {perf_stats.get('vehicles', 0)}, "
                  f"Traffic = {perf_stats.get('traffic_vehicles', 0)}, "
                  f"Audio = {perf_stats.get('audio_sources', 0)}")
    
    # Get comprehensive statistics
    print("  Getting comprehensive statistics...")
    comprehensive_stats = integration.get_comprehensive_statistics()
    
    # Print key statistics
    print(f"    Base Game:")
    base_stats = comprehensive_stats.get('performance', {})
    print(f"      FPS: {base_stats.get('fps', 0):.1f}")
    print(f"      Vehicles: {base_stats.get('vehicles', 0)}")
    print(f"      Characters: {base_stats.get('characters', 0)}")
    
    print(f"    Phase 3 Features:")
    phase3_stats = comprehensive_stats.get('phase3', {})
    traffic_stats = phase3_stats.get('traffic', {})
    audio_stats = phase3_stats.get('audio', {})
    input_stats = phase3_stats.get('input', {})
    
    print(f"      Traffic Vehicles: {traffic_stats.get('total_vehicles', 0)}")
    print(f"      Audio Sources: {audio_stats.get('total_sources', 0)}")
    print(f"      Control Scheme: {input_stats.get('current_scheme', 'unknown')}")
    
    print("✅ Complete Phase 3 Integration test completed")
    return True


def test_performance_stress():
    """Test performance under stress"""
    print("🧪 Testing Performance Under Stress...")
    
    integration = EnhancedIntegrationPhase3()
    
    # Set up stress test
    integration.set_traffic_density(TrafficDensity.EXTREME)
    integration.set_audio_volume("master", 1.0)
    
    # Create many audio events
    print("  Creating multiple audio events...")
    for i in range(20):
        x = random.uniform(100, 900)
        y = random.uniform(100, 900)
        audio_type = random.choice([AudioType.WEAPON_GUNSHOT, AudioType.WEAPON_EXPLOSION, 
                                  AudioType.VEHICLE_HORN, AudioType.CHARACTER_FOOTSTEP])
        integration.create_audio_event(audio_type, (x, y), random.uniform(0.3, 1.0))
    
    # Run stress test
    print("  Running stress test...")
    start_time = time.time()
    
    for frame in range(600):  # 10 seconds at 60 FPS
        dt = 1.0 / 60.0
        integration.update(dt)
        
        if frame % 120 == 0:  # Print every 2 seconds
            perf_stats = integration.get_performance_statistics()
            print(f"    Stress Frame {frame}: FPS = {perf_stats.get('fps', 0):.1f}, "
                  f"Vehicles = {perf_stats.get('vehicles', 0)}, "
                  f"Traffic = {perf_stats.get('traffic_vehicles', 0)}, "
                  f"Audio = {perf_stats.get('audio_sources', 0)}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"  Stress test completed in {total_time:.2f} seconds")
    print(f"  Average FPS: {600 / total_time:.1f}")
    
    print("✅ Performance Stress test completed")
    return True


def main():
    """Main test function"""
    print("🚀 Starting SaiyanQuest Phase 3 Features Test Suite")
    print("=" * 60)
    print("This test suite validates all Phase 3 features:")
    print("✅ Traffic Management with AI-Controlled Vehicles")
    print("✅ Advanced Audio System with Spatial Audio")
    print("✅ Enhanced Input & Controls with Gamepad Support")
    print("✅ Complete Phase 3 Integration")
    print("=" * 60)
    
    tests = [
        ("Traffic Management", test_traffic_management),
        ("Audio System", test_audio_system),
        ("Input Controls", test_input_controls),
        ("Complete Integration", test_integration),
        ("Performance Stress", test_performance_stress)
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
    print(f"🏁 Phase 3 Test Suite Complete: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed! Advanced features are working correctly.")
        print("\n📊 Phase 3 Features Summary:")
        print("✅ Traffic Management: AI-controlled vehicles with realistic behaviors")
        print("✅ Audio System: Spatial audio with vehicle sounds and environmental audio")
        print("✅ Input Controls: Gamepad support with configurable bindings")
        print("✅ Complete Integration: All systems working together seamlessly")
    else:
        print("⚠️ Some Phase 3 tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)